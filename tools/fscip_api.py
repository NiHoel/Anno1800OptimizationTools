from pulp import *
import io
from subprocess import Popen, PIPE, STDOUT

class FSCIP_CMD_INTERACTIVE(FSCIP_CMD):
    """Interactive specialization with callback and termination method of the FSCIP optimization solver"""
    
    name="FSCIP_CMD_INTERACTIVE"
    
    def __init__(
        self,
        path=None,
        mip=True,
        keepFiles=False,
        msg=True,
        options=None,
        timeLimit=None,
        gapRel=None,
        gapAbs=None,
        maxNodes=None,
        threads=None,
        logPath=None,
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
        FSCIP_CMD.__init__(
            self,
            mip=mip,
            msg=msg,
            options=options,
            path=path,
            keepFiles=keepFiles,
            timeLimit=timeLimit,
            gapRel=gapRel,
            gapAbs=gapAbs,
            maxNodes=maxNodes,
            threads=threads,
            logPath=logPath,
        )

        self.process = None

    def terminate(self):
        if self.process is not None:
            self.process.terminate()
        
    def actualSolve(self, lp, outputHandler = None):
        """Solve a well formulated lp problem"""
        if not self.executable(self.path):
            raise PulpSolverError("PuLP: cannot execute " + self.path)

        tmpLp, tmpSol, tmpOptions, tmpParams = self.create_tmp_files(
            lp.name, "lp", "sol", "set", "prm"
        )
        lp.writeLP(tmpLp)

        file_options: List[str] = []
        if "gapRel" in self.optionsDict:
            file_options.append(f"limits/gap={self.optionsDict['gapRel']}")
        if "gapAbs" in self.optionsDict:
            file_options.append(f"limits/absgap={self.optionsDict['gapAbs']}")
        if "maxNodes" in self.optionsDict:
            file_options.append(f"limits/nodes={self.optionsDict['maxNodes']}")
        if not self.mip:
            warnings.warn(f"{self.name} does not allow a problem to be relaxed")

        file_parameters: List[str] = []
        if self.timeLimit is not None:
            file_parameters.append(f"TimeLimit = {self.timeLimit}")
        # disable presolving in the LoadCoordinator to make sure a solution file is always written
        file_parameters.append("NoPreprocessingInLC = TRUE")

        command: List[str] = []
        command.append(self.path)
        command.append(tmpParams)
        command.append(tmpLp)
        command.extend(["-s", tmpOptions])
        command.extend(["-fsol", tmpSol])
        if not self.msg:
            command.append("-q")
        if "logPath" in self.optionsDict:
            command.extend(["-l", self.optionsDict["logPath"]])
        if "threads" in self.optionsDict:
            command.extend(["-sth", f"{self.optionsDict['threads']}"])

        options = iter(self.options)
        for option in options:
            # identify cli options by a leading dash (-) and treat other options as file options
            if option.startswith("-"):
                # assumption: all cli options require an argument which is provided as a separate parameter
                argument = next(options)
                command.extend([option, argument])
            else:
                # assumption: all file options contain a slash (/)
                is_file_options = "/" in option

                # assumption: all file options and parameters require an argument which is provided after the equal sign (=)
                if "=" not in option:
                    argument = next(options)
                    option += f"={argument}"

                if is_file_options:
                    file_options.append(option)
                else:
                    file_parameters.append(option)

        # wipe the solution file since FSCIP does not overwrite it if no solution was found which causes parsing errors
        self.silent_remove(tmpSol)
        with open(tmpOptions, "w") as options_file:
            options_file.write("\n".join(file_options))
        with open(tmpParams, "w") as parameters_file:
            parameters_file.write("\n".join(file_parameters))
        
        if outputHandler is None:
            stdout = self.firstWithFilenoSupport(sys.stdout, sys.__stdout__)
        else:
            stdout = PIPE
            
        stderr = self.firstWithFilenoSupport(sys.stderr, sys.__stderr__)

        self.process = Popen(command, stdout=stdout, stderr=stderr)
        if outputHandler is not None:
            for line in self.process.stdout:
                outputHandler(line)
        exitcode = self.process.wait()

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
        self.delete_tmp_files(tmpLp, tmpSol, tmpOptions, tmpParams)
        return status
    
    @staticmethod
    def firstWithFilenoSupport(*streams):
        for stream in streams:
            try:
                stream.fileno()
                return stream
            except io.UnsupportedOperation:
                pass
        return None