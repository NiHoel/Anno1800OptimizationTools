from pulp import *
import copy
from subprocess import Popen, PIPE, STDOUT

class FSCIP_CMD(LpSolver_CMD):
    """The FSCIP optimization solver"""
    
    name="FSCIP_CMD"
    
    def __init__(
        self,
        path=None,
        keepFiles=False,
        mip=True,
        msg=True,
        options=None,
        timeLimit=None,
        warmStart=False,
        threads=0,
        logPath=None
    ):
        """
        :param bool mip: if False, assume LP even if integer variables
        :param bool msg: if False, no log is shown
        :param list options: list of additional options to pass to solver, see https://ug.zib.de/doc-1.0.0/html/PARAMETERS.php
        :param bool keepFiles: if True, files are saved in the current directory and not deleted after solving
        :param str path: path to the solver binary
        :param float timeLimit: maximum time for solver (in seconds)
        :param bool warmStart: if True, the solver will use the current value of variables as a start
        :param int threads: sets the maximum number of threads
        :param str logPath: path to the log file
        """
        LpSolver_CMD.__init__(
            self,
            mip=mip,
            msg=msg,
            options=options,
            path=path,
            keepFiles=keepFiles,
            timeLimit=timeLimit,
            warmStart=warmStart,
            logPath=logPath
        )
        self.threads = threads
        self.logPath = logPath
        self.warmStart = warmStart
        self.process = None
     
    def defaultPath(self):
        return self.executableExtension("fscip.exe")

    def available(self):
        """True if the solver is available"""
        return self.executable(self.path)
    
    def terminate(self):
        if self.process is not None:
            self.process.terminate()
        
    def actualSolve(self, lp, outputHandler = None):
        """Solve a well formulated lp problem"""
        if not self.executable(self.path):
            raise PulpSolverError("PuLP: cannot execute " + self.path)

        tmpLp, tmpSol, tmpMst, tmpPrm = self.create_tmp_files(lp.name, "lp", "sol", "mst", "prm")
        vs = lp.writeLP(tmpLp, writeSOS=1)

        options = copy.deepcopy(self.options)
        if options is None:
            options = []
        if self.timeLimit is not None:
            options.append(["TimeLimit", str(self.timeLimit)])
        with open(tmpPrm, "w") as f:
            f.write("\n".join(["%s = %s" % (key, value) for key, value in options]))
            f.close()
        
        proc = ["%s" % self.path, tmpPrm, tmpLp]
        proc.extend(["-sth", str(self.threads)])

        if self.logPath is not None:
            proc.extend(["-l", str(self.logPath)])
        proc.extend(["-fsol", str(tmpSol)])
        if self.warmStart == True:
            self.writesol(filename=tmpMst, vs=vs)
            proc.extend(["-isol", str(tmpMst)])     

        if not self.msg:
            proc.append("-q")

        
        if outputHandler is None:
            stdout = self.firstWithFilenoSupport(sys.stdout, sys.__stdout__)
        else:
            stdout = PIPE
            
        stderr = self.firstWithFilenoSupport(sys.stderr, sys.__stderr__)

        self.solution_time = -clock()
        self.process = Popen(proc, stdout=stdout, stderr=stderr)
        if outputHandler is not None:
            for line in self.process.stdout:
                outputHandler(line)
        exitcode = self.process.wait()
        self.solution_time += clock()
        
        self.process = None

        if not os.path.exists(tmpSol):
            raise PulpSolverError("PuLP: Error while executing " + self.path)

        status, values = self.readsol(tmpSol)

        # Make sure to add back in any 0-valued variables SCIP leaves out.
        finalVals = {}
        for v in lp.variables():
            finalVals[v.name] = values.get(v.name, 0.0)

        lp.assignVarsVals(finalVals)
        lp.assignStatus(status)
        self.delete_tmp_files(tmpLp, tmpSol,tmpMst,tmpPrm)
        return status
    
    @staticmethod
    def readsol(filename):
        """Read a SCIP solution file"""
        with open(filename) as f:

            # Ignore first line it is different from scip sol file
            try:
                line = f.readline()
            except Exception:
                raise PulpSolverError("Can't get SCIP solver status")

            status = constants.LpStatusOptimal
            values = {}

            # Look for an objective value. If we can't find one, stop.
            try:
                line = f.readline()
                comps = line.split(": ")
                assert comps[0] == "objective value"
                assert len(comps) == 2
                float(comps[1].strip())
            except Exception:
                raise PulpSolverError("Can't get SCIP solver objective: %r" % line)

            # Parse the variable values.
            for line in f:
                try:
                    comps = line.split()
                    values[comps[0]] = float(comps[1])
                except:
                    raise PulpSolverError("Can't read SCIP solver output: %r" % line)

            return status, values
    
    @staticmethod
    def firstWithFilenoSupport(*streams):
        for stream in streams:
            try:
                stream.fileno()
                return stream
            except io.UnsupportedOperation:
                pass
        return None