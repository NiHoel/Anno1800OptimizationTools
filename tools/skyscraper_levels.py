TAG = "v2.1"

import numpy as np

from collections import deque
from io import BytesIO

import codecs
from datetime import datetime
import pandas as pd
import re
import copy
import json
import math
import pathlib
from queue import PriorityQueue
import requests
import threading
import ipywidgets as widgets
import IPython.display
import zipfile

one = np.array([1,1])

from pulp import *
available_solvers = listSolvers(onlyAvailable=True)

if "GUROBI_CMD" in available_solvers :
    from gurobipy import GRB
    SOLVER = "GUROBI"
elif "CPLEX_PY" in available_solvers :
    import cplex
    SOLVER = "CPLEX"
else :
    from tools.fscip_api import FSCIP_CMD
    from subprocess import Popen, PIPE, STDOUT
    SOLVER = "FSCIP" 

i18n = {
    "Open Anno Designer file":{
        "german": "Anno-Designer-Datei öffnen"
    },
    "Optimize": {
          "german": "Optimiere"
    },

    "Needs": {
            "chinese": "需求",
            "english": "Needs",
            "french": "Besoins",
            "german": "Bedürfnisse",
            "italian": "Bisogni",
            "japanese": "需要",
            "korean": "요구",
            "polish": "Potrzeby",
            "russian": "Потребности",
            "spanish": "Necesidades",
            "taiwanese": "需求"
        },
    "Items":{
            "chinese": "物品",
            "english": "Items",
            "french": "Objets",
            "german": "Items",
            #"guid": 23363,
            "italian": "Oggetti",
            "japanese": "アイテム",
            "korean": "아이템",
            "polish": "Przedmioty",
            "russian": "Объекты",
            "spanish": "Objetos",
            "taiwanese": "物品"
        },
    "General":{
            "chinese": "一般",
            "english": "General",
            "french": "Général",
            "german": "Allgemein",
            #"guid": 10368,
            "italian": "Generale",
            "japanese": "全般",
            "korean": "일반",
            "polish": "Ogólne",
            "russian": "Общие",
            "spanish": "General",
            "taiwanese": "一般"
        },
    "Residents": {
        "chinese": "居民",
        "english": "Residents",
        "french": "Résidents",
        "german": "Einwohner",
        # "guid": 22379,
        "italian": "Residenti",
        "japanese": "住民",
        "korean": "주민",
        "polish": "Mieszkańcy",
        "russian": "Жители",
        "spanish": "Residentes",
        "taiwanese": "居民"
    },
    "Residences": {
            "chinese": "住所",
            "english": "Residences",
            "french": "Résidences",
            "german": "Wohngebäude",
            #"guid": 22976,
            "italian": "Residenze",
            "japanese": "住居",
            "korean": "주거지",
            "polish": "Domy mieszkalne",
            "russian": "Жилые здания",
            "spanish": "Residencias",
            "taiwanese": "住所"
        },
    "Per House": {
            "chinese": "每栋房屋",
            "english": "Per house",
            "french": "Par maison",
            "german": "Pro Wohnhaus",
            #"guid": 17435,
            "italian": "Per dimora",
            "japanese": "1件当たり",
            "korean": "세대 당",
            "polish": "na dom",
            "russian": "За дом",
            "spanish": "Por cada casa",
            "taiwanese": "每棟房屋"
        },
    "Max. Residents": {
            "chinese": "最大居民数量",
            "english": "Max. Residents",
            "french": "Habitants max.",
            "german": "Einwohner (max.)",
            #"guid": 2322,
            "italian": "Max. residenti",
            "japanese": "最大住民数",
            "korean": "최대 주민 수",
            "polish": "Maks. liczba mieszkańców",
            "russian": "Макс. кол-во жителей",
            "spanish": "Residentes máx.",
            "taiwanese": "最大居民數量"
        },
    "Department Store": {
            "chinese": "百货公司",
            "english": "Department Store",
            "french": "Grand magasin",
            "german": "Kaufhaus",
            #"guid": 135100,
            "italian": "Grande magazzino",
            "japanese": "デパート",
            "korean": "백화점",
            "polish": "Dom handlowy",
            "russian": "Универмаг",
            "spanish": "Gran almacén",
            "taiwanese": "百貨公司"
        },
    "Furniture Store": {
            "chinese": "家具店",
            "english": "Furniture Store",
            "french": "Magasin de meubles",
            "german": "Einrichtungshaus",
            #"guid": 135099,
            "italian": "Negozio di mobili",
            "japanese": "家具店",
            "korean": "가구점",
            "polish": "Sklep meblowy",
            "russian": "Мебельный магазин",
            "spanish": "Tienda de muebles",
            "taiwanese": "傢俱店"
        },
    "Drug Store": {
            "chinese": "药局",
            "english": "Drug Store",
            "french": "Droguerie",
            "german": "Drogerie",
            #"guid": 135109,
            "italian": "Farmacia",
            "japanese": "ドラッグストア",
            "korean": "약국",
            "polish": "Apteka",
            "russian": "Аптека",
            "spanish": "Droguería",
            "taiwanese": "藥局"
        },
    "Total": {
            "chinese": "总计",
            "english": "Total",
            "french": "Total",
            "german": "Gesamt",
            #"guid": 132281,
            "italian": "Totale",
            "japanese": "合計",
            "korean": "합계",
            "polish": "Razem",
            "russian": "Всего",
            "spanish": "Total",
            "taiwanese": "總計"
        },
    "Residences in TH": {
      "english": "Residences in townhall range",
        "german": "Wohngebäude im Rathausbereich",
    },
    "Max. Residents in TH": {
      "english": "Max. residents in townhall range",
      "german": "Einwohner (max.) im Rathausbereich"  
    },
    "Residences in TH and Department Store": {
      "german": "Wohngebäude im Rathaus und Kaufhaus"  
    },
    "Store Coverage": {
      "german": "Abdeckung durch Einkaufspassagen"  
    },
    "Optimize": {
      "german": "Optimieren"  
    },
    "Terminate": {
      "german": "Beenden"  
    },
    "Use item list stored in townhall label":{
      "german": "Verwende die in der Beschriftung des Rathauses gespeicherte Item-Liste"  
    },
    "High contrast colors for skyscraper levels":{
      "german": "Level der Wolkenkratzer durch Farben mit hohem Kontrast darstellen"  
    },
    "Enforce full store supply":{
      "german": "Erzwinge vollständige Erfüllung der Bedürfnisse nach Einkaufspassagen"  
    },
    "Skip local optimization by swapping engineers and investors (gives occasionally better result)": {
        "german": "Überspringe lokale Optimierung, die zwischen Ingenieuren und Investoren wechselt (führt gelegentlich zu besserem Ergebnis)"
    },
    "Time limit": {
      "german": "Zeitlimit"  
    },
    "MODE_3-3-5": {
        "english": "Mode: Run local optimization for level 3 engineers and investors. Afterward, place few investor level 5 residences to maximize population.",
        "german": "Modus: Führt eine lokale Optimierung für Ingenieure und Investoren der Stufe 3 durch. Platziert anschließend einige Investoren der Stufe 5, um die Bevölkerung zu maximieren."
    },
    "MODE_4-5": {
        "english": "Mode: Searches for the optimal arrangement of level 4 and 5 investors.",
        "german": "Modus: Sucht nach der optimalen Anordnung von Stufe 4 und 5 Investoren."
    },
    "Run": {
      "german": "Durchlauf"  
    },
    "Elapsed Time":{
            "chinese": "匹配耗时",
            "english": "Elapsed Time",
            "french": "Délai écoulé",
            "german": "Vergangene Zeit",
            #"guid": 21388,
            "italian": "Tempo scaduto",
            "japanese": "経過時間",
            "korean": "경과 시간",
            "polish": "Czas rozgrywki",
            "russian": "Время в игре",
            "spanish": "Tiempo transcurrido",
            "taiwanese": "配對耗時"
        },
    "Best found": {
      "german": "Beste gefundene Lösung"  
    },
    "Upper bound": {
      "german": "Obere Schranke"  
    },
    "Gain in last 10 min":{
      "german": "Zugewinn in den letzten 10 min"  
    },
    "Optimizing ...":{
      "german": "Optimiere ..."  
    },
    "Next run": {
      "german": "Nächster Durchlauf"  
    },
    "No solution found": {
      "german": "Keine Lösung gefunden"  
    },
    "Solution found": {
      "german": "Lösung gefunden"  
    },
    "Result written to": {
      "german": "Datei mit Ergebnis erstellt"  
    },
       "Status": {
        "chinese": "状态",
        "english": "State",
        "french": "État",
        "german": "Status",
        # "guid": 23143,
        "italian": "Stato",
        "japanese": "状態",
        "korean": "상태",
        "polish": "Stan",
        "russian": "Состояние",
        "spanish": "Estado",
        "taiwanese": "狀態"
    },
        "Ready": {
        "chinese": "准备就绪",
        "english": "Ready",
        "french": "Prêt",
        "german": "Bereit",
        # "guid": 11625,
        "italian": "Pronto",
        "japanese": "準備完了",
        "korean": "준비",
        "polish": "Gotowy",
        "russian": "Готов(а)",
        "spanish": "Preparado",
        "taiwanese": "準備就緒"
    },
    "Opening": {
        "chinese": "开启",
        "english": "Open",
        "french": "Ouvrir",
        "german": "Öffnen",
        # "guid": 145017,
        "italian": "Apri",
        "japanese": "開く",
        "korean": "열기",
        "polish": "Otwarte",
        "russian": "Открыть",
        "spanish": "Abrir",
        "taiwanese": "開啟"
    },
    "Store Coverage": {
      "german": "Abdeckung durch Geschäfte"  
    },
    "Failed to read file: ": {
        "german": "Datei konnte nicht gelesen werden: "
    },
    "Failed to save ": {
        "german": "Datei konnte nicht gespeichert werden: "
    },
    "A new version is available":{
        "german": "Eine neue Version ist verfügbar"
    },
    "Update": {
        "german": "Aktualisieren"
    },
    "Ignore": {
        "german": "Ignorieren"
    },
    "Close and re-open the application!": {
        "german": "Schlißen und öffnen Sie die Anwendung erneut!"
    }
}

def _(msg):
    if msg in i18n and LANG in i18n[msg]:
        return i18n[msg][LANG]

    return msg



class Level :
    def __init__(self, index, level, template, radius, color) :
        self.index = index
        self.level = level
        self.template = template
        self.radius = radius
        self.color = color

r_th = 20

A7PARAMS = {
        "languages": ["chinese", "english", "french", "german", "italian", "japanese", "korean", "polish", "russian",
                  "spanish", "taiwanese"],
    "panorama": {
        120016: 5,
        1010259: 5,
        1010258: 5,
        1010225: 5,
        1010354: 5,
    },
    "needs": [
        #engineers
        [
    {
        "guid": 1010217,
        "residents": 12,
        "level": 0,
        "locaText": {
            "brazilian": "Canned Food",
            "chinese": "罐头食物",
            "english": "Canned Food",
            "french": "Conserves",
            "german": "Fleischkonserven",
            "italian": "Cibo in scatola",
            "japanese": "缶詰",
            "korean": "통조림",
            "polish": "Konserwy",
            "portuguese": "Canned Food",
            "russian": "Консервы",
            "spanish": "Comida en conserva",
            "taiwanese": "罐頭食物"
        }
    },
    {
        "guid": 1010206,
        "residents": 6,
        "level": 0,
        "locaText": {
            "brazilian": "Sewing Machines",
            "chinese": "缝纫机",
            "english": "Sewing Machines",
            "french": "Machines à coudre",
            "german": "Nähmaschinen",
            "italian": "Macchine da cucire",
            "japanese": "ミシン",
            "korean": "재봉틀",
            "polish": "Maszyny do szycia",
            "portuguese": "Sewing Machines",
            "russian": "Швейные машины",
            "spanish": "Máquinas de coser",
            "taiwanese": "縫紉機"
        }
    },
    {
        "guid": 1010247,
        "residents": 6,
        "level": 0,
        "locaText": {
            "brazilian": "Fur Coats",
            "chinese": "皮草大衣",
            "english": "Fur Coats",
            "french": "Manteaux de fourrure",
            "german": "Pelzmäntel",
            "italian": "Abiti di pelliccia",
            "japanese": "毛皮のコート",
            "korean": "모피 코트",
            "polish": "Płaszcze futrzane",
            "portuguese": "Fur Coats",
            "russian": "Шубы",
            "spanish": "Abrigos de piel",
            "taiwanese": "皮草大衣"
        }
    },
    {
        "guid": 120030,
        "residents": 4,
        "level": 0,
        "locaText": {
            "brazilian": "Glasses",
            "chinese": "眼镜",
            "english": "Spectacles",
            "french": "Lunettes",
            "german": "Brillen",
            "italian": "Occhiali",
            "japanese": "眼鏡",
            "korean": "안경",
            "polish": "Okulary",
            "portuguese": "Glasses",
            "russian": "Очки",
            "spanish": "Gafas",
            "taiwanese": "眼鏡"
        }
    },
    {
        "guid": 120032,
        "residents": 2,
        "level": 0,
        "locaText": {
            "brazilian": "Coffee",
            "chinese": "咖啡",
            "english": "Coffee",
            "french": "Café",
            "german": "Kaffee",
            "italian": "Caffè",
            "japanese": "コーヒー",
            "korean": "커피",
            "polish": "Kawa",
            "portuguese": "Coffee",
            "russian": "Кофе",
            "spanish": "Café",
            "taiwanese": "咖啡"
        }
    },
    {
        "guid": 1010208,
        "residents": 2,
        "level": 0,
        "locaText": {
            "brazilian": "Light Bulbs",
            "chinese": "灯泡",
            "english": "Light Bulbs",
            "french": "Ampoules",
            "german": "Glühbirnen",
            "italian": "Lampadine",
            "japanese": "電球",
            "korean": "전구",
            "polish": "Żarówki",
            "portuguese": "Light Bulbs",
            "russian": "Электролампы",
            "spanish": "Bombillas",
            "taiwanese": "燈泡"
        }
    },
    {
        "guid": 135186,
        "residents": 10,
        "level": 2,
        "locaText": {
            "chinese": "口香糖",
            "english": "Chewing Gum",
            "french": "Chewing-gum",
            "german": "Kaugummis",
            "italian": "Gomma da masticare",
            "japanese": "チューインガム",
            "korean": "껌",
            "polish": "Guma do żucia",
            "russian": "Жевательная резинка",
            "spanish": "Chicle",
            "taiwanese": "口香糖"
        }
    },
    {
        "guid": 135230,
        "residents": 10,
        "level": 3,
        "locaText": {
            "chinese": "打字机",
            "english": "Typewriter",
            "french": "Machines à écrire",
            "german": "Schreibmaschinen",
            "italian": "Macchine da scrivere",
            "japanese": "タイプライター",
            "korean": "타자기",
            "polish": "Maszyny do pisania",
            "russian": "Печатные машинки",
            "spanish": "Máquinas de escribir",
            "taiwanese": "打字機"
        }
    },
    {
        "guid": 135233,
        "residents": 5,
        "level": 3,
        "locaText": {
            "chinese": "小提琴",
            "english": "Violins",
            "french": "Violons",
            "german": "Violinen",
            "italian": "Violini",
            "japanese": "バイオリン",
            "korean": "바이올린",
            "polish": "Skrzypce",
            "russian": "Скрипки",
            "spanish": "Violines",
            "taiwanese": "小提琴"
        }
    },
    {
        "guid": 1010203,
        "residents": [
            2,
            3,
            4,
            5
        ],
        "level": 0,
        "locaText": {
            "brazilian": "Soap",
            "chinese": "肥皂",
            "english": "Soap",
            "french": "Savon",
            "german": "Seife",
            "italian": "Sapone",
            "japanese": "石鹸",
            "korean": "비누",
            "polish": "Mydło",
            "portuguese": "Soap",
            "russian": "Мыло",
            "spanish": "Jabón",
            "taiwanese": "肥皂"
        }
    },
    {
        "guid": 1010258,
        "residents": [
            2,
            3,
            4,
            5
        ],
        "level": 0,
        "locaText": {
            "brazilian": "Chocolate",
            "chinese": "巧克力",
            "english": "Chocolate",
            "french": "Chocolat",
            "german": "Schokolade",
            "italian": "Cioccolato",
            "japanese": "チョコレート",
            "korean": "초콜릿",
            "polish": "Czekolada",
            "portuguese": "Chocolate",
            "russian": "Шоколад",
            "spanish": "Chocolate",
            "taiwanese": "巧克力"
        }
    },
    {
        "guid": 133181,
        "residents": [
            5,
            7,
            8,
            9
        ],
        "level": 0,
        "locaText": {
            "chinese": "洗发水",
            "english": "Shampoo",
            "french": "Shampoing",
            "german": "Shampoo",
            "italian": "Shampoo",
            "japanese": "シャンプー",
            "korean": "샴푸",
            "polish": "Szampon",
            "russian": "Шампунь",
            "spanish": "Champú",
            "taiwanese": "洗髮精"
        }
    },
    {
        "guid": 535,
        "residents": [
            3,
            4,
            6,
            9
        ],
        "level": 0,
        "locaText": {
            "chinese": "当地信件",
            "english": "Local Mail",
            "french": "Courrier local",
            "german": "Lokale Post",
            "italian": "Posta locale",
            "japanese": "普通郵便",
            "korean": "현지 우편",
            "polish": "Poczta miejscowa",
            "russian": "Местная почта",
            "spanish": "Correo local",
            "taiwanese": "當地信件"
        }
    },
    {
        "guid": 536,
        "residents": [
            7,
            10,
            12,
            11
        ],
        "level": 0,
        "locaText": {
            "chinese": "区域信件",
            "english": "Regional Mail",
            "french": "Courrier régional",
            "german": "Regionale Post",
            "italian": "Posta regionale",
            "japanese": "地域郵便",
            "korean": "지역 우편",
            "polish": "Poczta regionalna",
            "russian": "Региональная почта",
            "spanish": "Correo regional",
            "taiwanese": "區域信件"
        }
    },
    {
        "guid": 2524,
        "residents": [
            15,
            20,
            25,
            23
        ],
        "level": 0,
        "locaText": {
            "brazilian": "Hannah is happy to see that more workers are arriving at the town.",
            "chinese": "越洋信件",
            "english": "Overseas Mail",
            "french": "Courrier international",
            "german": "Überregionale Post",
            "italian": "Posta estera",
            "japanese": "海外郵便",
            "korean": "지역 외 우편",
            "polish": "Poczta zamorska",
            "portuguese": "Hannah is happy to see that more workers are arriving at the town.",
            "russian": "Зарубежная почта",
            "spanish": "Correo internacional",
            "taiwanese": "越洋信件"
        }
    },
    {
        "guid": 6600,
        "residents": [
            3,
            5,
            5,
            6
        ],
        "level": 0,
        "locaText": {
            "chinese": "龙舌兰",
            "english": "Mezcal",
            "french": "Mezcal",
            "german": "Mezcal",
            "italian": "Mescal",
            "japanese": "メスカル",
            "korean": "메즈칼",
            "polish": "Mezcal",
            "russian": "Мескаль",
            "spanish": "Mezcal",
            "taiwanese": "龍舌蘭"
        }
    },
    {
        "guid": 5382,
        "residents": [
            6,
            9,
            11,
            12
        ],
        "level": 0,
        "locaText": {
            "chinese": "冰激凌",
            "english": "Ice Cream",
            "french": "Crème glacée",
            "german": "Eiscreme",
            "italian": "Gelato",
            "japanese": "アイスクリーム",
            "korean": "아이스크림",
            "polish": "Lody",
            "russian": "Мороженое",
            "spanish": "Helado",
            "taiwanese": "冰淇淋"
        }
    },
    {
        "guid": 5397,
        "residents": [
            7,
            10,
            11,
            11
        ],
        "level": 0,
        "locaText": {
            "chinese": "药物",
            "english": "Medicine",
            "french": "Médicaments",
            "german": "Medizin",
            "italian": "Medicina",
            "japanese": "薬",
            "korean": "의약품",
            "polish": "Medycyna",
            "russian": "Медикаменты",
            "spanish": "Medicina",
            "taiwanese": "藥物"
        }
    },
    {
        "guid": 1010353,
        "residents": 6,
        "level": 0,
        "locaText": {
            "brazilian": "Graduation",
            "chinese": "大学",
            "english": "University",
            "french": "Universités",
            "german": "Universität",
            "italian": "Università",
            "japanese": "大学",
            "korean": "대학",
            "polish": "Uniwersytet",
            "portuguese": "Graduation",
            "russian": "Университет",
            "spanish": "Universidad",
            "taiwanese": "大學"
        }
    },
    {
        "guid": 1010354,
        "residents": 2,
        "level": 0,
        "hidden": True,
        "locaText": {
            "brazilian": "Electricity",
            "chinese": "电力",
            "english": "Electricity",
            "french": "Électricité",
            "german": "Elektrizität",
            "italian": "Elettricità",
            "japanese": "電気",
            "korean": "전기",
            "polish": "Elektryczność",
            "portuguese": "Electricity",
            "russian": "Электричество",
            "spanish": "Electricidad",
            "taiwanese": "電力"
        }
    },
    {
        "guid": 135108,
        "residents": 20,
        "level": 1,
        "hidden": True,
        "locaText": {
            "chinese": "百货公司",
            "english": "Department Store",
            "french": "Grand magasin",
            "german": "Kaufhaus",
            "italian": "Grande magazzino",
            "japanese": "デパート",
            "korean": "백화점",
            "polish": "Dom handlowy",
            "russian": "Универмаг",
            "spanish": "Gran almacén",
            "taiwanese": "百貨公司"
        }
    },
    {
        "guid": 135107,
        "residents": 10,
        "level": 2,
        "hidden": True,
        "locaText": {
            "chinese": "家具店",
            "english": "Furniture Store",
            "french": "Magasin de meubles",
            "german": "Einrichtungshaus",
            "italian": "Negozio di mobili",
            "japanese": "家具店",
            "korean": "가구점",
            "polish": "Sklep meblowy",
            "russian": "Мебельный магазин",
            "spanish": "Tienda de muebles",
            "taiwanese": "傢俱店"
        }
    },
    {
        "guid": 135109,
        "residents": 5,
        "level": 3,
        "hidden": True,
        "locaText": {
            "chinese": "药局",
            "english": "Drug Store",
            "french": "Droguerie",
            "german": "Drogerie",
            "italian": "Farmacia",
            "japanese": "ドラッグストア",
            "korean": "약국",
            "polish": "Apteka",
            "russian": "Аптека",
            "spanish": "Droguería",
            "taiwanese": "藥局"
        }
    }
],
        
        [#investors
      {
        "guid": 120030,
        "residents": 16,
        "level": 0,
        "locaText": {
            "brazilian": "Glasses",
            "chinese": "眼镜",
            "english": "Spectacles",
            "french": "Lunettes",
            "german": "Brillen",
            "italian": "Occhiali",
            "japanese": "眼鏡",
            "korean": "안경",
            "polish": "Okulary",
            "portuguese": "Glasses",
            "russian": "Очки",
            "spanish": "Gafas",
            "taiwanese": "眼鏡"
        }
    },
    {
        "guid": 120032,
        "residents": 8,
        "level": 0,
        "locaText": {
            "brazilian": "Coffee",
            "chinese": "咖啡",
            "english": "Coffee",
            "french": "Café",
            "german": "Kaffee",
            "italian": "Caffè",
            "japanese": "コーヒー",
            "korean": "커피",
            "polish": "Kawa",
            "portuguese": "Coffee",
            "russian": "Кофе",
            "spanish": "Café",
            "taiwanese": "咖啡"
        }
    },
    {
        "guid": 1010208,
        "residents": 8,
        "level": 0,
        "locaText": {
            "brazilian": "Light Bulbs",
            "chinese": "灯泡",
            "english": "Light Bulbs",
            "french": "Ampoules",
            "german": "Glühbirnen",
            "italian": "Lampadine",
            "japanese": "電球",
            "korean": "전구",
            "polish": "Żarówki",
            "portuguese": "Light Bulbs",
            "russian": "Электролампы",
            "spanish": "Bombillas",
            "taiwanese": "燈泡"
        }
    },
    {
        "guid": 120016,
        "residents": 2,
        "level": 0,
        "locaText": {
            "brazilian": "Champagne",
            "chinese": "香槟",
            "english": "Champagne",
            "french": "Champagne",
            "german": "Sekt",
            "italian": "Champagne",
            "japanese": "シャンパン",
            "korean": "샴페인",
            "polish": "Szampan",
            "portuguese": "Champagne",
            "russian": "Игристое вино",
            "spanish": "Champán",
            "taiwanese": "香檳"
        }
    },
    {
        "guid": 1010259,
        "residents": 2,
        "level": 0,
        "locaText": {
            "brazilian": "Cigars",
            "chinese": "雪茄",
            "english": "Cigars",
            "french": "Cigares",
            "german": "Zigarren",
            "italian": "Sigari",
            "japanese": "葉巻",
            "korean": "시가",
            "polish": "Cygara",
            "portuguese": "Cigars",
            "russian": "Сигары",
            "spanish": "Puros",
            "taiwanese": "雪茄"
        }
    },
    {
        "guid": 1010258,
        "residents": 2,
        "level": 0,
        "locaText": {
            "brazilian": "Chocolate",
            "chinese": "巧克力",
            "english": "Chocolate",
            "french": "Chocolat",
            "german": "Schokolade",
            "italian": "Cioccolato",
            "japanese": "チョコレート",
            "korean": "초콜릿",
            "polish": "Czekolada",
            "portuguese": "Chocolate",
            "russian": "Шоколад",
            "spanish": "Chocolate",
            "taiwanese": "巧克力"
        }
    },
    {
        "guid": 1010225,
        "residents": 4,
        "level": 0,
        "locaText": {
            "brazilian": "Steam Carriages",
            "chinese": "蒸汽车",
            "english": "Steam Carriages",
            "french": "Automobiles à vapeur",
            "german": "Dampfwagen",
            "italian": "Carrozze a vapore",
            "japanese": "蒸気自動車",
            "korean": "증기차",
            "polish": "Pojazdy parowe",
            "portuguese": "Steam Carriages",
            "russian": "Паровой транспорт",
            "spanish": "Carruajes de vapor",
            "taiwanese": "蒸汽車"
        }
    },
    {
        "guid": 135186,
        "residents": 10,
        "level": 2,
        "locaText": {
            "chinese": "口香糖",
            "english": "Chewing Gum",
            "french": "Chewing-gum",
            "german": "Kaugummis",
            "italian": "Gomma da masticare",
            "japanese": "チューインガム",
            "korean": "껌",
            "polish": "Guma do żucia",
            "russian": "Жевательная резинка",
            "spanish": "Chicle",
            "taiwanese": "口香糖"
        }
    },
    {
        "guid": 135229,
        "residents": 15,
        "level": 2,
        "locaText": {
            "chinese": "饼干",
            "english": "Biscuits",
            "french": "Biscuits",
            "german": "Kekse",
            "italian": "Biscotti",
            "japanese": "ビスケット",
            "korean": "비스킷",
            "polish": "Ciastka",
            "russian": "Печенье",
            "spanish": "Galletas",
            "taiwanese": "餅乾"
        }
    },
    {
        "guid": 135234,
        "residents": 15,
        "level": 3,
        "locaText": {
            "chinese": "干邑白兰地",
            "english": "Cognac",
            "french": "Cognac",
            "german": "Cognac",
            "italian": "Cognac",
            "japanese": "コニャック",
            "korean": "코냑",
            "polish": "Koniak",
            "russian": "Коньяк",
            "spanish": "Coñac",
            "taiwanese": "干邑白蘭地"
        }
    },
    {
        "guid": 135230,
        "residents": 10,
        "level": 4,
        "locaText": {
            "chinese": "打字机",
            "english": "Typewriter",
            "french": "Machines à écrire",
            "german": "Schreibmaschinen",
            "italian": "Macchine da scrivere",
            "japanese": "タイプライター",
            "korean": "타자기",
            "polish": "Maszyny do pisania",
            "russian": "Печатные машинки",
            "spanish": "Máquinas de escribir",
            "taiwanese": "打字機"
        }
    },
    {
        "guid": 135232,
        "residents": 15,
        "level": 4,
        "locaText": {
            "chinese": "撞球桌",
            "english": "Billiard Tables",
            "french": "Billards",
            "german": "Billardtische",
            "italian": "Tavoli da biliardo",
            "japanese": "ビリヤード台",
            "korean": "당구대",
            "polish": "Stoły bilardowe",
            "russian": "Бильярдные столы",
            "spanish": "Mesas de billar",
            "taiwanese": "撞球桌"
        }
    },
    {
        "guid": 135233,
        "residents": 5,
        "level": 5,
        "locaText": {
            "chinese": "小提琴",
            "english": "Violins",
            "french": "Violons",
            "german": "Violinen",
            "italian": "Violini",
            "japanese": "バイオリン",
            "korean": "바이올린",
            "polish": "Skrzypce",
            "russian": "Скрипки",
            "spanish": "Violines",
            "taiwanese": "小提琴"
        }
    },
    {
        "guid": 135231,
        "residents": 15,
        "level": 5,
        "locaText": {
            "chinese": "玩具",
            "english": "Toys",
            "french": "Jouets",
            "german": "Spielwaren",
            "italian": "Giocattoli",
            "japanese": "おもちゃ",
            "korean": "장난감",
            "polish": "Zabawki",
            "russian": "Игрушки",
            "spanish": "Juguetes",
            "taiwanese": "玩具"
        }
    },
    {
        "guid": 1010209,
        "residents": [
            3,
            5,
            7,
            8,
            9,
            10
        ],
        "level": 0,
        "locaText": {
            "brazilian": "Furs",
            "chinese": "毛皮",
            "english": "Furs",
            "french": "Fourrures",
            "german": "Felle",
            "italian": "Pellicce",
            "japanese": "毛皮",
            "korean": "모피",
            "polish": "Futra",
            "portuguese": "Furs",
            "russian": "Меха",
            "spanish": "Pieles",
            "taiwanese": "毛皮"
        }
    },
    {
        "guid": 112695,
        "residents": [
            6,
            10,
            11,
            12,
            13,
            14
        ],
        "level": 0,
        "locaText": {
            "chinese": "熊毛皮",
            "english": "Bear Fur",
            "french": "Peau d'ours",
            "german": "Bärenfell",
            "italian": "Pelle d'orso",
            "japanese": "熊の毛皮",
            "korean": "곰의 모피",
            "polish": "Futro niedźwiedzia",
            "russian": "Медвежий мех",
            "spanish": "Pelaje de oso",
            "taiwanese": "熊毛皮"
        }
    },
    {
        "guid": 114404,
        "residents": [
            4,
            7,
            8,
            9,
            11,
            12
        ],
        "level": 0,
        "locaText": {
            "chinese": "壁毯",
            "english": "Tapestries",
            "french": "Tapisseries",
            "german": "Wandteppiche",
            "italian": "Arazzi",
            "japanese": "タペストリー",
            "korean": "태피스트리",
            "polish": "Gobeliny",
            "russian": "Гобелены",
            "spanish": "Tapices",
            "taiwanese": "壁毯"
        }
    },
    {
        "guid": 535,
        "residents": [
            8,
            11,
            13,
            16,
            18,
            24
        ],
        "level": 0,
        "locaText": {
            "chinese": "当地信件",
            "english": "Local Mail",
            "french": "Courrier local",
            "german": "Lokale Post",
            "italian": "Posta locale",
            "japanese": "普通郵便",
            "korean": "현지 우편",
            "polish": "Poczta miejscowa",
            "russian": "Местная почта",
            "spanish": "Correo local",
            "taiwanese": "當地信件"
        }
    },
    {
        "guid": 536,
        "residents": [
            12,
            16,
            20,
            22,
            27,
            31
        ],
        "level": 0,
        "locaText": {
            "chinese": "区域信件",
            "english": "Regional Mail",
            "french": "Courrier régional",
            "german": "Regionale Post",
            "italian": "Posta regionale",
            "japanese": "地域郵便",
            "korean": "지역 우편",
            "polish": "Poczta regionalna",
            "russian": "Региональная почта",
            "spanish": "Correo regional",
            "taiwanese": "區域信件"
        }
    },
    {
        "guid": 2524,
        "residents": [
            25,
            33,
            41,
            49,
            57,
            65
        ],
        "level": 0,
        "locaText": {
            "brazilian": "Hannah is happy to see that more workers are arriving at the town.",
            "chinese": "越洋信件",
            "english": "Overseas Mail",
            "french": "Courrier international",
            "german": "Überregionale Post",
            "italian": "Posta estera",
            "japanese": "海外郵便",
            "korean": "지역 외 우편",
            "polish": "Poczta zamorska",
            "portuguese": "Hannah is happy to see that more workers are arriving at the town.",
            "russian": "Зарубежная почта",
            "spanish": "Correo internacional",
            "taiwanese": "越洋信件"
        }
    },
    {
        "guid": 5388,
        "residents": [
            7,
            11,
            12,
            13,
            15,
            16
        ],
        "level": 0,
        "locaText": {
            "chinese": "香水",
            "english": "Perfumes",
            "french": "Parfums",
            "german": "Parfüms",
            "italian": "Profumi",
            "japanese": "香水",
            "korean": "향수",
            "polish": "Perfumy",
            "russian": "Духи",
            "spanish": "Perfumes",
            "taiwanese": "香水"
        }
    },
    {
        "guid": 5395,
        "residents": [
            10,
            16,
            17,
            18,
            19,
            21
        ],
        "level": 0,
        "locaText": {
            "chinese": "电扇",
            "english": "Fans",
            "french": "Ventilateurs",
            "german": "Ventilatoren",
            "italian": "Ventilatori",
            "japanese": "換気扇",
            "korean": "선풍기",
            "polish": "Wentylatory",
            "russian": "Вентиляторы",
            "spanish": "Ventiladores",
            "taiwanese": "電扇"
        }
    },
    {
        "guid": 5392,
        "residents": [
            5,
            8,
            10,
            11,
            12,
            13
        ],
        "level": 0,
        "locaText": {
            "chinese": "底片卷",
            "english": "Film Reel",
            "french": "Bobine de film",
            "german": "Filmrolle",
            "italian": "Bobina di pellicola",
            "japanese": "フィルムリール",
            "korean": "필름 릴",
            "polish": "Rolka z filmem",
            "russian": "Кинопленка",
            "spanish": "Rollo de película",
            "taiwanese": "底片捲"
        }
    },

    {
        "guid": 1010354,
        "residents": 8,
        "level": 0,
        "hidden": True,
        "locaText": {
            "brazilian": "Electricity",
            "chinese": "电力",
            "english": "Electricity",
            "french": "Électricité",
            "german": "Elektrizität",
            "italian": "Elettricità",
            "japanese": "電気",
            "korean": "전기",
            "polish": "Elektryczność",
            "portuguese": "Electricity",
            "russian": "Электричество",
            "spanish": "Electricidad",
            "taiwanese": "電力"
        }
    },
    {
        "guid": 135108,
        "residents": 25,
        "level": 1,
        "hidden": True,
        "locaText": {
            "chinese": "百货公司",
            "english": "Department Store",
            "french": "Grand magasin",
            "german": "Kaufhaus",
            "italian": "Grande magazzino",
            "japanese": "デパート",
            "korean": "백화점",
            "polish": "Dom handlowy",
            "russian": "Универмаг",
            "spanish": "Gran almacén",
            "taiwanese": "百貨公司"
        }
    },
    {
        "guid": 135107,
        "residents": 10,
        "level": 3,
        "hidden": True,
        "locaText": {
            "chinese": "家具店",
            "english": "Furniture Store",
            "french": "Magasin de meubles",
            "german": "Einrichtungshaus",
            "italian": "Negozio di mobili",
            "japanese": "家具店",
            "korean": "가구점",
            "polish": "Sklep meblowy",
            "russian": "Мебельный магазин",
            "spanish": "Tienda de muebles",
            "taiwanese": "傢俱店"
        }
    },
    {
        "guid": 135109,
        "residents": 5,
        "level": 5,
        "hidden": True,
        "locaText": {
            "chinese": "药局",
            "english": "Drug Store",
            "french": "Droguerie",
            "german": "Drogerie",
            "italian": "Farmacia",
            "japanese": "ドラッグストア",
            "korean": "약국",
            "polish": "Apteka",
            "russian": "Аптека",
            "spanish": "Droguería",
            "taiwanese": "藥局"
        }
    }
]
],
    #extract from calculator:
    #residences = [l.residence].concat(l.skyscraperLevels)
    #for(var n of l.needs){
    # residents = JSON.stringify([...residences.map(r => r.residentsPerNeed.get(n.guid,0))])
    # console.log(`{"guid": ${n.guid}, "residents": ${residents}, "level": 0, \n"locaText": ${JSON.stringify(n.product.locaText)}},`)
    #} 

    "items": {
        137797: {
            "guid": 137797,
            "bonus_supply": {
                135108: 135186,
                135107: 135232,
                135109: 135233
            },
            "locaText": {
                "chinese": "蓝天快递服务",
                "english": "Blue Skies Delivery Service",
                "french": "Service de livraison Blue Skies",
                "german": "Lieferdienst „Blauer Himmel“",
                "italian": "Servizio di consegna Cieli Azzurri",
                "japanese": "ブルースカイデリバリーサービス",
                "korean": "파란 하늘 배송 서비스",
                "polish": "Firma dostawcza Błękitne Niebo",
                "russian": "Служба доставки \"Blue Skies\"",
                "spanish": "Servicio de entrega Cielos azules",
                "taiwanese": "藍天快遞服務"
            }
        },
        137798: {
            "guid": 137798,
            "bonus_residents": {
                135229: 5,
                135230: 5,
                135234: 5,
                135233: 5,
                135232: 5,
                135231: 5,
                135108: 5,
                135107: 5,
                135109: 5,
            },
            "locaText": {
                "chinese": "蓝天女佣",
                "english": "Blue Skies Maid",
                "french": "Femme de chambre Blue Skies",
                "german": "Zofe „Blauer Himmel“",
                "italian": "Cameriera Cieli Azzurri",
                "japanese": "ブルースカイのメイド",
                "korean": "파란 하늘 가정부",
                "polish": "Pokojówka w Błękitnym Niebie",
                "russian": "Горничная \"Blue Skies\"",
                "spanish": "Asistenta de Cielos azules",
                "taiwanese": "藍天女傭"
            }
        },
        191817: {
            "guid": 191817,
            "bonus_residents": {
                1010200: 3,
                1010213: 3,
                1010217: 3,
                1010353: 3,
                120032: 3,
                1010208: 3,
                120016: 3,
                1010225: 3,
                1010258: 3,
                120033: 3,
                6600: 3
            },
            "locaText": {
                "chinese": "教宗诏书－生育延续",
                "english": "Papal Paper of Prenatal Preservation",
                "french": "Bulle sur la préservation prénatale",
                "german": "Päpstliches Papier zur pränatalen Präservation",
                "italian": "Documento papale di tutela prenatale",
                "japanese": "教皇の胎児保護論文",
                "korean": "태아 보호에 관한 교황 서한",
                "polish": "Dokument papieski o ochronie płodowej",
                "russian": "Булла о запрете контрацепции",
                "spanish": "Proposición papal de preservación prenatal",
                "taiwanese": "教宗詔書－生育延續"
            }
        },

        191816: {
            "guid": 191816,
            "bonus_residents": {
                1010200: 2,
                1010213: 2,
                1010217: 2,
                1010353: 2,
                120032: 2,
                1010208: 2,
                120016: 2,
                1010225: 2,
                1010258: 2,
                120033: 2,
                6600: 2
            },
            "locaText": {
                "chinese": "节育规范",
                "english": "Contraception Regulation",
                "french": "Législation sur la contraception",
                "german": "Vorschriften zur Empfängnisverhütung",
                "italian": "Regolamentazione sulla contraccezione",
                "japanese": "避妊規制",
                "korean": "피임 규정",
                "polish": "Przepisy dotyczące antykoncepcji",
                "russian": "Положение о контрацепции",
                "spanish": "Regulación de métodos anticonceptivos",
                "taiwanese": "節育規範"
            }
        },

        191815: {
            "guid": 191815,
            "bonus_residents": {
                1010200: 1,
                1010213: 1,
                1010217: 1,
                1010353: 1,
                120032: 1,
                1010208: 1,
                120016: 1,
                1010225: 1,
                1010258: 1,
                120033: 1
            },
            "locaText": {
                "chinese": "避孕修正案",
                "english": "The Withdrawal Amendment",
                "french": "Loi sur le droit de retrait",
                "german": "Interruptus-Gesetzeszusatz",
                "italian": "Emendamento contraccettivo",
                "japanese": "払い戻し修正案",
                "korean": "금단 개정",
                "polish": "Poprawka o wycofaniu",
                "russian": "Поправка о средствах контрацепции",
                "spanish": "Enmienda de castidad",
                "taiwanese": "避孕修正案"
            }
        },

        190193: {
            "guid": 190193,
            "bonus_residents": {
                1010200: 2,
                1010213: 2,
                1010217: 2,
                1010353: 2,
                120032: 2,
                1010208: 2,
                120016: 2,
                1010225: 2,
                1010258: 2,
                120033: 2
            },
            "locaText": {
                "chinese": "“谷地之眼”圣阿尔铎",
                "english": "Saint D'Artois, Vision of the Valley",
                "french": "Sainte d'Artois - Vue de la vallée",
                "german": "Saint D'Artois, Aura der Erkenntnis",
                "italian": "Santa D'Artois, Visione della Valle",
                "japanese": "サン・ダルトワ - 渓谷の光景",
                "korean": "계곡의 선각자 생 다르투아",
                "polish": "Saint D'Artois - Wizja doliny",
                "russian": "Сейнт д'Артуа - Откровение Долины",
                "spanish": "Santa d'Artois, Visión del Valle",
                "taiwanese": "「谷地之眼」聖阿爾鐸"
            }
        },

        190658: {
            "guid": 190658,
            "bonus_residents": {
                120020: 1,
                1010213: 1,
                1010206: 1,
                1010353: 1,
                120030: 1,
                1010208: 1,
                120016: 1,
                1010225: 1,
                1010258: 1
            },
            "locaText": {
                "chinese": "“灭火英雄”乔治·道提老大",
                "english": "Chief George Doughty, Smouldering Hero",
                "french": "Chef George Doughty, « Capitaine Flammes »",
                "german": "Feuerwehrchef George „Drachenfeuer“ Doughty",
                "italian": "Capo George Doughty, l'eroe serpeggiante",
                "japanese": "ジョージ・ドーティー署長、炎の英雄",
                "korean": "소방 영웅, 조지 도티 소방서장",
                "polish": "Naczelnik George Doughty, bohater płomieni",
                "russian": "Начальник Джордж Доути, \"Опаленный\"",
                "spanish": "Jefe George Doughty, héroe del fuego",
                "taiwanese": "「打火英雄」喬治．道提老大"
            }
        },

        191579: {
            "guid": 191579,
            "bonus_residents": {
                120020: 1,
                1010213: 1,
                1010206: 1,
                1010353: 1,
                120030: 1,
                1010208: 1,
                120016: 1,
                1010225: 1,
                1010258: 1,
                5395: 1
            },
            "locaText": {
                "chinese": "“慈善银行家”雅各·索柯",
                "english": "Jakob Sokow, The Charitable Banker",
                "french": "Jakob Sokow, le banquier philanthrope",
                "german": "Jakob Sokow, Bankier mit Herz",
                "italian": "Jakob Sokow, il banchiere caritatevole",
                "japanese": "ジェイコブ・ソコウ、慈善銀行家",
                "korean": "관대한 은행가, 제이콥 소코우",
                "polish": "Jakob Sokow, bankier filantrop",
                "russian": "Джейкоб Соков, банкир-филантроп",
                "spanish": "Jakob Sokow, banquero caritativo",
                "taiwanese": "「慈善銀行家」雅各．索柯"
            }
        },

        190724: {
            "guid": 190724,
            "bonus_residents": {
                120020: 1,
                1010213: 1,
                1010206: 1,
                1010353: 1,
                120030: 1,
                1010208: 1,
                120016: 1,
                1010225: 1,
                1010258: 1,
                5395: 1
            },
            "locaText": {
                "chinese": "“手臂注射先驱”路易斯·P·赫卡特",
                "english": "Louis P. Hecate, Arm-Puncturing Pioneer",
                "french": "Louis P. Hecate, pionnier de l'acupuncture",
                "german": "Louis P. Hecate, der Pionier",
                "guid": 190724,
                "italian": "Louis P. Hecate, pioniere dei pungi-braccia",
                "japanese": "ルイス・P・ヘカテ、注射の先駆者",
                "korean": "예방접종의 선구자, 루이스 P. 헤카테",
                "polish": "Louis P. Hecate - pionier kłucia w ramię",
                "russian": "Луис П. Гекейт - изобретатель вакцины",
                "spanish": "Louis P. Hecate, pinchabrazos pionero",
                "taiwanese": "「手臂注射先驅」路易斯．P．赫卡特"
            }
        },

        111180: {
            "guid": 111180,
            "bonus_residents": {
                120020: 1,
                1010213: 1,
                1010206: 1,
                1010353: 1,
                120030: 1,
                1010208: 1,
                120016: 1,
                1010225: 1,
                1010258: 1
            },
            "locaText": {
                "chinese": "彼得罗·约拿·普劳德，公共财哲学家",
                "english": "Pietro Jonah Proud, The Philosopher of the Public Good",
                "french": "Pietro Jonah Proud, le philosophe du salut public",
                "german": "Pietro Jonah Proud, Philosoph des öffentlichen Wohls",
                "italian": "Pietro Jonah Proud, il filosofo del bene pubblico",
                "japanese": "ピエトロ・ヨナ・プロウド、公益の哲学者",
                "korean": "공공의 이익을 위한 철학자 피에트로 요나 프라우드",
                "polish": "Pietro Jonah Proud, filozof dobra publicznego",
                "russian": "Пьетро Джона Прауд, философ общественных благ",
                "spanish": "Pietro Jonah Proud, el filósofo del bien público",
                "taiwanese": "彼得羅．約拿．普勞德，公共財哲學家"
            }
        },
    },
    "levels": [[
        Level(index = 0, level = 1, template="A7_residence_SkyScraper_4lvl1", radius = 4, color = {"A": 255, "R": 97, "G": 118, "B": 136}),
        Level(index = 1, level = 2, template="A7_residence_SkyScraper_4lvl2", radius = 4.25, color = {"A": 255, "R": 144, "G": 165, "B": 183}),
        Level(index = 2, level = 3, template="A7_residence_SkyScraper_4lvl3", radius = 5, color = {"A": 255, "R": 169, "G": 195, "B": 237})
    ],[
        Level(index = 0, level = 1, template="A7_residence_SkyScraper_5lvl1", radius = 4, color = {"A": 255, "R": 3, "G": 94, "B": 94}),
        Level(index = 1, level = 2, template="A7_residence_SkyScraper_5lvl2", radius = 4.25, color = {"A": 255, "R": 0, "G": 128, "B": 128}),
        Level(index = 2, level = 3, template="A7_residence_SkyScraper_5lvl3", radius = 5, color = {"A": 255, "R": 68, "G": 166, "B": 166}),
        Level(index = 3, level = 4, template="A7_residence_SkyScraper_5lvl4", radius = 6, color = {"A": 255, "R": 105, "G": 196, "B": 196}), 
        Level(index = 4, level = 5, template="A7_residence_SkyScraper_5lvl5", radius = 6.75, color = {"A": 255, "R": 161, "G": 234, "B": 234}),
    ]
],
    "panorama_effects": [
        #engineers
        [
            #none
            {},
       #weak
         {
                120030: 5,
                120032: 5,
                1010354: 5,
                1010208: 5,
                535: 2,
                536: 4,
                2524: 7,
                1010203: 2,
                1010258: 2,
                133181: 3,
                5382: 4,
                5397: 4,
                6600: 2
         },
        #moderate
         {
                120030: 10,
                120032: 10,
                1010354: 10,
                1010208: 10,
                535: 4,
                536: 8,
                2524: 14,
                1010203: 3,
                1010258: 3,
                133181: 4,
                5382: 5,
                5397: 5,
                6600: 3
         },
        #decent
         {
                120030: 15,
                120032: 15,
                1010354: 15,
                1010208: 15,
                535: 6,
                536: 12,
                2524: 22,
                1010203: 4,
                1010258: 4,
                133181: 5,
                5382: 6,
                5397: 6,
                6600: 4
         },
        #strong
         {
                120030: 20,
                120032: 20,
                1010354: 20,
                1010208: 20,
                535: 8,
                536: 15,
                2524: 29,
                1010203: 5,
                1010258: 5,
                133181: 6,
                5382: 8,
                5397: 7,
                6600: 5
         },
            #intense
           {
                120030: 25,
                120032: 25,
                1010354: 25,
                1010208: 25,
                535: 10,
                536: 19,
                2524: 36,
                1010203: 6,
                1010258: 6,
                133181: 8,
                5382: 10,
                5397: 8,
                6600: 6
           }
    ],
    #investors
    [
        #none
        {},
        #weak
        {
                120016: 5,
                1010259: 5,
                1010258: 5,
                1010225: 5,
                1010354: 5,
                535: 4,
                536: 6,
                2524: 12,
                1010209: 4,
                112695: 5,
                114404: 4,
                5388: 7,
                5395: 8,
                5392: 5
        },
        #moderate
        {
                120016: 10,
                1010259: 10,
                1010258: 10,
                1010225: 10,
                1010354: 10,
                535: 8,
                536: 12,
                2524: 24,
                1010209: 5,
                112695: 7,
                114404: 7,
                5388: 8,
                5395: 11,
                5392: 7
        },
        #decent
        {
                120016: 15,
                1010259: 15,
                1010258: 15,
                1010225: 15,
                1010354: 15,
                535: 12,
                536: 15,
                2524: 36,
                1010209: 8,
                112695: 9,
                114404: 8,
                5388: 10,
                5395: 12,
                5392: 8
        },
        #strong
        {
                120016: 20,
                1010259: 20,
                1010258: 20,
                1010225: 20,
                1010354: 20,
                535: 15,
                536: 23,
                2524: 48,
                1010209: 10,
                112695: 11,
                114404: 10,
                5388: 12,
                5395: 14,
                5392: 10
        },
        #intense
        {
                120016: 25,
                1010259: 25,
                1010258: 25,
                1010225: 25,
                1010354: 25,
                535: 24,
                536: 29,
                2524: 60,
                1010209: 12,
                112695: 13,
                114404: 13,
                5388: 14,
                5395: 16,
                5392: 13
        }
    ]]
}

def pos(obj) :
    return np.array([int(c) for c in obj['Position'].split(',')]) 

def size(obj) :
    return np.array([int(c) for c in obj['Size'].split(',')])

#simple image scaling to (nR x nC) size
def scale(im, nR, nC):
    nR0 = len(im)     # source number of self.rows 
    nC0 = len(im[0])  # source number of columns 
    return [[ im[int(nR0 * r / nR)][int(nC0 * c / nC)]  
             for c in range(nC)] for r in range(nR)]

class Need:
    def __init__(self, guid, residence, residents, level, supply):
        self.guid = guid
        self.residence = residence
        self.residents = residents
        self.min_level = level
        self.supply = supply
        self.bonus_residents = 0

        
    def get_max_residents(self, level, panorama_effect):
        if self.min_level is not None and self.min_level > level.level:
            return 0
        
        effects = A7PARAMS["panorama_effects"][self.residence][panorama_effect]
        
        pop = self.residents
        if type(pop) == list:
            pop = pop[level.level]
            
        pop += self.bonus_residents
        
        if self.guid in effects:
            return effects[self.guid] + pop
        
        return pop

    def get_residents(self, level, panorama_effect):
        return round(self.get_max_residents(level, panorama_effect) * self.supply)
      
    def add_bonus_residents(self, count):
        self.bonus_residents += count

class Townhall:
    def __init__(self, obj, tl = None) :
        self.obj = obj

        self.tl = tl
        if self.tl is None :
            self.tl = pos(obj)
        self.size = np.array([4,4])
        self.center = self.tl + 1.5*one
        
        self.items = []
        if obj.get("Label") is not None :
            match = re.match(r"\[((\d+,? ?)*)\]", obj.get("Label"))
            if match is not None:
                for guid in match[1].split(", "):
                    try:
                        self.items.append(int(guid))
                    except:
                        pass
        
class House :
    def __init__(self, obj, ID, tl = None) :
        self.obj = obj
        self.ID = ID
        self.needs = [dict(), dict()]
        self.var_levels = None
        self.is_fixed = False
        
        self.tl = tl
        if self.tl is None :
            self.tl = pos(obj)
        self.size = np.array([3,3])
        self.center = self.tl + one
        self.neighbors = []
        
        
        self.stores = [0, 0, 0]
        self.electricity = False
        self.th = False
        
        self.level = 3
        self.panorama_effect = 0
        self.residence = 1
        
        self.queue_index = None
        self.prio = 0
        
        if obj.get("Identifier") == "Residence_tier04":
            self.level = 3
            self.residence = 0
            
        if obj.get("Identifier") == "Residence_tier05":
            self.level = 3
            self.residence = 1
        
        for r in [0,1]:
            for l in A7PARAMS["levels"][r] :
                if l.template == obj.get("Identifier") :
                    self.level = l.level
                    self.residence = r
                   
                    break
                    
       
    def __lt__(self,other):
        return self.center[1] < other.center[1] if self.center[0] == other.center[0] else self.center[0] < other.center[0]
    
    def init_levels(self):
        self.var_levels = [[LpVariable("HL_{}_{}_{}".format(self.ID, r, l.level), cat='Binary') for l in A7PARAMS["levels"][r]] for r in [0,1]]
        self.is_fixed = False
    
    def dist(self, h) :
        return np.linalg.norm(self.center - h.center)
    
    def is_gap(self) :
        return "Label" in self.obj and self.obj["Label"] == "-"
    
    def calculate_unbound_panorama(self, level = None, residence = None) :
        if residence is None:
            residence = self.residence
        if level is None :
            level = self.level
        
        support = level
            
        for n in self.neighbors :
            if A7PARAMS["levels"][residence][level-1].radius < self.dist(n) :
                continue
                
            if n.level < level or n.level == level and not residence == n.residence:
                support += 1
            else :
                support -= 1
                
        return support   
    
    def calculate_panorama(self, level = None, residence = None) :
        return max(0,min(5,self.calculate_unbound_panorama(level, residence)))      
           
    
    def get_max_residents(self, level = None, panorama_effect = None, residence = None) :
        if residence is None:
            residence = self.residence
        if level is None:
            level = self.level
        if not isinstance(level, Level):
            level = A7PARAMS["levels"][residence][level - 1]
        if panorama_effect is None :
            panorama_effect = self.panorama_effect
          
        pop = 0
        for n in self.needs[residence].values():
            pop += n.get_max_residents(level, panorama_effect)
               
        return pop
    
    # 0 = engineers, 1 = investors
    def get_residents(self, level = None, panorama_effect = None, residence = None) :   
        if residence is None:
            residence = self.residence
        if level is None:
            level = self.level
        if not isinstance(level, Level):
            level = A7PARAMS["levels"][residence][level - 1]
        if panorama_effect is None :
            panorama_effect = self.panorama_effect
          
        pop = 0
        for n in self.needs[residence].values():
            pop += n.get_residents(level, panorama_effect)
               
        return pop

    def get_residents_delta_when_changed(self, other, residence, level, punish=False):
        if A7PARAMS["levels"][self.residence][self.level-1].radius < self.dist(other) :
            return 0
        
        def is_support(r,l):
            return l < self.level or l == self.level and not r == self.residence
        
        support = 1 if is_support(other.residence, other.level) else -1
        new_support = 1 if is_support(residence, level) else -1
        
        
        if support == new_support:
            return 0
        
        support_delta = new_support - support
        panorama = self.calculate_unbound_panorama()
        if panorama >= 7:
            return -1 if punish and support_delta < 0 else 0
        
        return self.get_residents(self.level, max(0, min(5, panorama + support_delta)), self.residence) - self.get_residents()
    
    def get_profit(self, residence, level, punish = True) :
      
        panorama = self.calculate_panorama(level, residence)
        profit = self.get_residents(level, panorama, residence) - self.get_residents()
        
        for n in self.neighbors :
            profit += n.get_residents_delta_when_changed(self, residence, level, punish)
                
        return profit
    
    def fix_level(self, level, residence) :
        if self.is_fixed:
            return
    
        self.level = level
        self.residence = residence
        for r in [0,1]:
            for l in range(len( A7PARAMS["levels"][r])):
                if l == level - 1 and r == residence:
                    self.var_levels[r][l].setInitialValue(1)
                    self.var_levels[r][l].fixValue()
                else:
                    self.var_levels[r][l].setInitialValue(0)
                    self.var_levels[r][l].fixValue()
                    
        self.is_fixed = True
        
    def gen_object(self, colors=None) : 
        l = A7PARAMS["levels"][self.residence][self.level - 1]
        obj = copy.deepcopy(self.obj)
        
        obj["Identifier"] = l.template
        obj["Label"] = str(self.get_residents())
        obj["Icon"] = "A7_panorama_buff_0" + str(self.panorama_effect)
        obj["Template"] ="SkyScraper_Residence"
        obj["Color"] = l.color if self.residence == 0 or colors is None else colors[self.level - 1]
        obj["Radius"] =l.radius
   
        return obj

    def set_options(self, options):
        self.needs = [dict(), dict()]

        for r in [0,1]:
            needs = self.needs[r]
            for need in A7PARAMS["needs"][r]:
                guid = need["guid"]
                needs[guid] = Need(guid, r, need["residents"],need["level"],(1 if guid in options["needs"][r] else 0))

            needs[1010354].supply = 1 if self.electricity else 0     

            needs[135108].supply = self.stores[0]       
            needs[135107].supply = self.stores[1]      
            needs[135109].supply = self.stores[2]

            if self.th:
                item_list = options["items"]
                if "th_items" in options["general"] and len(self.th.items) > 0:
                    item_list = self.th.items

                for guid in item_list:
                    if guid not in A7PARAMS["items"]:
                        continue

                    item = A7PARAMS["items"][guid]
                    if "bonus_supply" in item:
                        for if_need, then_need in item["bonus_supply"].items():
                            if if_need in needs and then_need in needs:                      
                                needs[then_need].supply = max(needs[then_need].supply, needs[if_need].supply)

                    if "bonus_residents" in item:
                        for need, count in item["bonus_residents"].items():
                            if need in needs:
                                needs[need].add_bonus_residents(count)
                                
                                
class Layout :
    def __init__(self, ad_json) :
        r_max = math.ceil(A7PARAMS["levels"][1][-1].radius)
        
        self.json = ad_json
        
        self.tl = np.array([99999999, 999999999])
        self.br = np.array([-99999999, -999999999])
        one = np.array([1,1])
        for obj in ad_json['Objects'] :
            self.tl = np.minimum.reduce([self.tl, pos(obj)])
            self.br = np.maximum.reduce([self.br, pos(obj) + size(obj)])
         
       
        self.tl = self.tl - r_th * one
        self.br = self.br + r_th * one
        
        dim = self.br - self.tl
        self.rows = dim[1]
        self.cols = dim[0]
        self.area = np.empty(shape=dim, dtype=object)
        self.streets = np.zeros(shape=dim, dtype=int)
        
        self.clusters = []
        self.cluster_gaps = set()
        self.engineer_mode = False
        
        count_residences = [0,0]
        self.houses = []
        for obj in ad_json['Objects'] :
            p = pos(obj) - self.tl
            if self.is_street(obj) :
                self.streets[p[0],p[1]] = 1
                
                if not obj.get("Size") == "1,1":
                    sz = size(obj)
                    for x in range(p[0], p[0] + sz[0]):
                        for y in range(p[1], p[1] + sz[1]):
                            self.streets[x,y] = 1
            
            
            if not self.is_house(obj) :
                continue
                
            self.houses.append(House(obj, len(self.houses) + 1, p))
            h = self.houses[-1]  
            self.area[h.center[0], h.center[1]] = h
            
            count_residences[h.residence] += 1
            
        if count_residences[0] / len(self.houses) > 0.2:
            self.engineer_mode = True
        else:   
            for h in self.houses :
                h.residence = 1
        
        # compute neighbouring houses that may affect panorama
        for h in self.houses :    
            for x in range(h.center[0] - r_max, h.center[0] + r_max) :
                for y in range(h.center[1] - r_max, h.center[1] + r_max) :
                    h_ = self.area[x,y]
                    if h_ is None or h == h_:
                        continue
                        
                    if(h.dist(h_) <= r_max) :
                        h.neighbors.append(h_)
        
        
        for h in self.houses :
            h.panorama_effect = h.calculate_panorama()
            
            for x in range(h.tl[0], h.tl[0] + h.size[0]) :
                for y in range(h.tl[1], h.tl[1] + h.size[1]) :
                    self.area[x][y] = h
                    
        # compute clusters           
        for h in self.houses : 
            if h.is_gap() :
                self.cluster_gaps.add(h)
                continue
            
            in_cluster = False
            for c in self.clusters:
                if h in c :
                    in_cluster = True
                    break
            
            if in_cluster :
                continue
            
            if len(h.neighbors) == 0:
                h.residence = 1
                h.level = 5
                continue

            self.clusters.append(set())
            c = self.clusters[-1]
            q = deque([h])

            while len(q) :
                n = q.pop()

                for m in n.neighbors :
                    if m in c :
                        continue

                    if not m.is_gap() :
                        q.append(m)
                        c.add(m)        
        
        # compute coverage of stores, townhalls and electricity
        self.townhalls = []
        for obj in ad_json['Objects'] :            
            
            if self.is_powerplant(obj) :
                self.mark_in_range(obj, obj["InfluenceRange"], 0)
            
            s = self.get_store_index(obj)
            if s > 0 :
                self.mark_in_range(obj, 63.667, s)
            
            if self.is_th(obj):
                self.townhalls.append(Townhall(obj))
                
                th = self.townhalls[-1]
                p = pos(obj) - self.tl
                center = p + np.array([1.5, 1.5])
                for x in range(p[0] - r_th, p[0] + r_th+2) :
                    for y in range(p[1] - r_th, p[1] + r_th+2) :
                        h = self.area[x][y]
                        
                        if h is None:
                            continue
                            
                     
                        if np.linalg.norm(center - h.center) <= r_th :
                            h.th = th
        
            
        
    def is_house(self, obj) :
        if obj.get("Identifier") is None or obj.get("Template") is None:
            return False
        
        if obj.get("Identifier") == "Scholar_Residence" :
            return False
        
        return "residence" in obj["Identifier"].lower() or "skyscraper" in obj["Template"].lower() or obj.get("Icon") == "A7_resident" or obj.get("Icon") == "A7_dlc_high_life_256"
    
    def is_street(self, obj):
        return obj.get("Road")
    
    def get_store_index(self, obj):
        if obj.get("Identifier") is None or obj.get("Template") is None:
            return 0
        
        if "DepartmentStore" in obj["Identifier"] or "DepartmentStore" in obj["Template"]:
            return 1
        if "FurnitureStore" in obj["Identifier"] or "FurnitureStore" in obj["Template"]:
            return 2
        if "Pharmacy" in obj["Identifier"] or "Pharmacy" in obj["Template"]:
            return 3
        return 0
    
    def is_powerplant(self, obj):
        return not obj.get("Icon") is None and "A7_electric_works" in obj["Icon"]
    
    def is_th(self, obj):
        return not obj.get("Icon") is None and "A7_townhall" in obj.get("Icon")
    
    
    def mark_in_range(self, obj, r, update_mode) :
        r += 1
        n_tiles = []
        c_tiles = []
        p = pos(obj) - self.tl
        s = size(obj)
        streets = copy.deepcopy(self.streets)
        
        for x in range(p[0], p[0] + s[0]) :
            for y in range(p[1], p[1] + s[1]) :
                if x == p[0] or y == p[1] or x == p[0] + s[0] - 1 or y == p[1] + s[1] - 1 :
                    n_tiles.append(np.array([x,y]))
                    streets[x,y] = 3
        
        
        at = lambda container, pos : container[pos[0]][pos[1]]
        
        while r > 0 :
            c_tiles = n_tiles
            n_tiles = []
           
            r -= 1
           
            for center in c_tiles:
                for direction in [np.array([1,0]),np.array([0,1]),np.array([-1,0]),np.array([0,-1])] :
                    n = center + direction
                    neighbor = at(self.area, n)
                      
                    if not neighbor is None and isinstance(neighbor, House) :
                        if update_mode == 0 :
                            neighbor.electricity = True
                        else :
                            neighbor.stores[update_mode - 1] = max(neighbor.stores[update_mode - 1], 1 if r >= 1 else r)
                    
                    elif at(streets, n) == 1:
                        n_tiles.append(n)
                        
                        if r >= 1:
                            streets[n[0], n[1]] = 2
            
            
    def set_options(self, options):
        for h in self.houses:
            h.set_options(options)
            
    def update_panorama(self):
        for h in self.houses:
            h.panorama_effect = h.calculate_panorama()
            
    def get_residents(self):
        return sum([h.get_residents() for h in self.houses])
    
    def get_summary(self) :  
        def empty_entry(name):
            return {
                _("Level"): name,
                _("Residences"): 0,
                _("Residents"): 0,
                _("Per House"): 0,
                _("Max. Residents"): 0, 
                _("Residences in TH"): 0,
                _("Max. Residents in TH"): 0,
                _("Store Coverage"): [0 for i in range(3)],
                _("Department Store"): 0,
                _("Furniture Store"): 0,
                _("Drug Store"): 0,
                _("Residences in TH and Department Store"): 0,
                _("Panorama"): [0 for p in range(6)],
            }
        
        summary = [[empty_entry("{} Lvl. {}".format(_("Engineers") if r == 0 else _("Investors"), l.level)) for l in A7PARAMS["levels"][r]] for r in [0,1]]
        total_summary = empty_entry(_("Total"))
        
        for h in self.houses:
            r = h.residence
            l = A7PARAMS["levels"][r][h.level - 1]
            max_residents = h.get_max_residents()
            residents = h.get_residents()

            # level summary
            s = summary[r][l.index]

            if h.th :
                s[_("Residences in TH")] += 1
                s[_("Max. Residents in TH")] += max_residents
                
                if h.stores[0]:
                    s[_("Residences in TH and Department Store")] += 1

            s[_("Residences")] += 1
            s[_("Residents")] += residents
            s[_("Max. Residents")] += max_residents
            s[_("Panorama")][h.panorama_effect] += 1
            for st in range(3) :
                s[_("Store Coverage")][st] += 1 if h.stores[st] else 0

            #total summary
            s = total_summary
            if h.th :
                s[_("Residences in TH")] += 1
                s[_("Max. Residents in TH")] += max_residents
                
                if h.stores[0]:
                    s[_("Residences in TH and Department Store")] += 1

            s[_("Residences")] += 1
            s[_("Residents")] += residents
            s[_("Max. Residents")] += max_residents
            s[_("Panorama")][h.panorama_effect] += 1
            for st in range(3) :
                s[_("Store Coverage")][st] += 1 if h.stores[st] else 0
        
        result = []
        for r in [0,1]:
            for s in summary[r]:
                if not s[_("Residences")] == 0:
                    result.append(s)

        result.append(total_summary)
                
        for s in result:
            s[_("Per House")] = "{:.5}".format(s[_("Residents")] / s[_("Residences")])
            s[_("Residences in TH")] = "{:.2%}".format(s[_("Residences in TH")] / s[_("Residences")])
            s[_("Max. Residents in TH")] = "{:.2%}".format(s[_("Max. Residents in TH")] / s[_("Max. Residents")])
           
            s[_("Department Store")] = "{:.2%}".format(s[_("Store Coverage")][0] / s[_("Residences")])
            s[_("Furniture Store")] = "{:.2%}".format(s[_("Store Coverage")][1] / s[_("Residences")])
            s[_("Drug Store")] = "{:.2%}".format(s[_("Store Coverage")][2] / s[_("Residences")])
            s[_("Store Coverage")] = ""
            s[_("Residents")] = "{:,}".format(s[_("Residents")])
            s[_("Max. Residents")] = "{:,}".format(s[_("Max. Residents")])
            
            for index, p in enumerate(s[_("Panorama")]):
                s["{} {}".format(_("Level"), index)] = "{:.2%}".format(p / s[_("Residences")])
            s[_("Panorama")] = ""
            #s[_("Panorama")] = " ".join(["{:.2%} Lvl. {}".format(p / s[_("Residences")], index) for index,p in enumerate(s[_("Panorama")])])
            
        return result
            
        
    def save(self, path, colors=None) :
          
        src_json = self.json
        ad_json = {"Objects":[]}
        
        for k in src_json.keys() :
            if not k == "Objects":
                ad_json[k] = src_json[k]
                
        ad_json["Modified"] = str(datetime.now().isoformat())
                
        for obj in src_json["Objects"] :
            if not self.is_house(obj) and ("Identifier" not in obj or not obj["Identifier"] == "Legend") :
                ad_json["Objects"].append(obj)
                
        for h in self.houses:
            ad_json["Objects"].append(h.gen_object(colors))
            
        summary = self.get_summary()
        
        anchor = np.array([self.cols,1])
        offset = 0
        for r in [0,1]:
            for l in A7PARAMS["levels"][r] :
                p = anchor + offset * np.array([3,0])
                ad_json["Objects"].append({
                    "Identifier":"Legend",
                    "Label":"Level " + str(l.level),
                    "Position":"{},{}".format(p[0],p[1]),
                    "Size":"3,3","Icon":"A7_dlc_high_life_256",
                    "Template":"","Color": l.color if r == 0 or colors is None else colors[l.index],
                    "Borderless":False,
                    "Road":False,
                    "Radius":0.0,
                    "InfluenceRange":0.0,
                    "PavedStreet":True,
                    "BlockedAreaLength":0.0,
                    "BlockedAreaWidth":0.0,
                    "Direction":"Down"
                })
                offset += 1

        anchor[1] += 4
        label = ""
        label_height = 2*len(summary[-1].keys())
        label_width = 30
        for k in summary[-1].keys() :
            label += k + "\n"

        ad_json["Objects"].append({
            "Identifier":"Legend",
            "Label":label,
            "Position":"{},{}".format(anchor[0],anchor[1]),
            "Size":"{},{}".format(label_width,label_height),
            "Icon":None,
            "Template":"",
            "Color":{"A": 255, "R": 255, "G": 255, "B": 255},
            "Borderless":True,
            "Road":False,
            "Radius":0.0,
            "InfluenceRange":0.0,
            "PavedStreet":True,
            "BlockedAreaLength":0.0,
            "BlockedAreaWidth":0.0,
            "Direction":"Down"
        })
        anchor[0] += label_width

        for s in summary :
            label = ""
            label_height = 2*len(s)
            label_width = 14
            for v in s.values() :
                label += str(v) + "\n"

            ad_json["Objects"].append({
                "Identifier":"Legend",
                "Label":label,
                "Position":"{},{}".format(anchor[0],anchor[1]),
                "Size":"{},{}".format(label_width,label_height),
                "Icon":None,
                "Template":"",
                "Color":{"A": 255, "R": 255, "G": 255, "B": 255},
                "Borderless":True,
                "Road":False,
                "Radius":0.0,
                "InfluenceRange":0.0,
                "PavedStreet":True,
                "BlockedAreaLength":0.0,
                "BlockedAreaWidth":0.0,
                "Direction":"Down"
            })
            anchor[0] += label_width
        
        with open(path, "w") as f :
            json.dump(ad_json, f)
            



    def run_heuristic(self, src, target, punish=True, callback = None) :
        print("greedy")
        queues = [PriorityQueue()]

        def matches(house, t):
            return house.residence == t[0] and house.level == t[1]

        def get_upgrade(h: House):
            if matches(h, src):
                return target
            elif matches(h, target):
                return src

            return None

        def get_prio(h):
            to = get_upgrade(h)
            return -h.get_profit(to[0], to[1], punish)

        def update(n):
            #print(n.ID,n.queue_index, get_upgrade(n))
            if n.queue_index is None:
                return

            to = get_upgrade(n)
            if to is None:
                return

            prio = get_prio(n)

            if n.prio == prio:
                return

            if n.queue_index + 1 == len(queues) :
                n.queue_index = len(queues)
                queues.append(PriorityQueue())
                queues[-1].put((prio, n))
            else :
                n.queue_index += 1
                queues[n.queue_index].put((prio, n)) 
            n.prio = prio

        for h in self.houses :
            to = get_upgrade(h)
            if to is not None:
                prio = get_prio(h)
                h.prio = prio
                queues[0].put((prio, h))
                h.queue_index = 0

        iteration = 0

        while True:
            maximum = float('-inf')
            maximizer = 0
            has_elements = False
            for i in range(len(queues)) :
                while not queues[i].empty() and queues[i].queue[0][1].queue_index > i :
                    queues[i].get()

                if queues[i].empty() :
                    continue

                has_elements = True

                if not queues[i].queue[0][0] == get_prio(queues[i].queue[0][1]):
                    h = queues[i].queue[0][1]
                    print("Inconsistency", i, queues[i].queue[0][0], h.ID, h.queue_index, get_prio(h))
                    #return

                if -queues[i].queue[0][0] > maximum :
                    maximum = -queues[i].queue[0][0]
                    maximizer = i


            if not has_elements :
                break

            entry = queues[maximizer].get()
            h = entry[1]

            to = get_upgrade(h)
            if to is None:
                continue

            if h.get_profit(to[0], to[1], False) < 0 :
                break

            residents = self.get_residents()
            h.residence = to[0]        
            h.level = to[1]

            h.panorama_effect = h.calculate_panorama()
            for n in h.neighbors :
                n.panorama_effect = n.calculate_panorama()

            update(h)
            visited = set()
            for n in h.neighbors :
                if not n in visited:
                    update(n)
                    visited.add(n)

                for m in n.neighbors:
                    if m in visited:
                        continue

                    update(m)
                    visited.add(m)

            if abs(residents - entry[0] - self.get_residents()) > 6:
                print("Incorrect prio", residents, entry[0], self.get_residents(), h.ID, to)
                return

            iteration += 1
            if iteration % 10 == 0 and callback is not None:
                if callback(self.get_residents()):
                    break
            if iteration > len(self.houses):
                break

        self.update_panorama()        
      
class Watcher:
    def __init__(self, prob, timeLimit, logPath):
        self.prob = prob
                   
    def terminate(self):
        pass
    
    def optimize(self, log_callback = None):
        return constants.LpSolutionInfeasible

if SOLVER == "GUROBI":
    class GurobiWatcher(Watcher):
        stop = False
        callback_calls = 0

        def __init__(self, prob, timeLimit, logPath):
            self.prob = prob
            self.solver = GUROBI(msg=False, timeLimit = timeLimit, logPath = logPath, warmStart = True, options=[('MIPConcurrent',4)])

        def terminate(self):
            GurobiWatcher.stop = True

        def optimize(self, log_callback = None):
            GurobiWatcher.stop = False
            GurobiWatcher.callback_calls = 0

            def callback(model, where):
                if GurobiWatcher.stop :
                    model.terminate()
                    return

                if where == GRB.Callback.MIP:
                    GurobiWatcher.callback_calls += 1

                    if GurobiWatcher.callback_calls % 1 == 0 and log_callback is not None:
                        runtime = model.cbGet(GRB.Callback.RUNTIME)
                        objbst = model.cbGet(GRB.Callback.MIP_OBJBST)
                        objbnd = model.cbGet(GRB.Callback.MIP_OBJBND)
                        log_callback(runtime, objbst, objbnd)

            self.solver.buildSolverModel(self.prob)
            self.solver.callSolver(self.prob, callback=callback)
            return self.extract_solution(self.prob)

        def extract_solution(self, lp):
            """
            Modified version of https://github.com/coin-or/pulp/blob/master/pulp/apis/gurobi_api.py findSolutionValues(self, lp)
            That correctly reads out feasible integer solutions
            """
            model = lp.solverModel
            solutionStatus = model.Status


            gurobiLpStatus = {
                GRB.OPTIMAL: constants.LpSolutionOptimal,
                GRB.INFEASIBLE: constants.LpSolutionInfeasible,
                GRB.INF_OR_UNBD: constants.LpSolutionUnbounded,
                GRB.UNBOUNDED: constants.LpSolutionUnbounded,
                GRB.ITERATION_LIMIT: constants.LpSolutionIntegerFeasible,
                GRB.NODE_LIMIT: constants.LpSolutionIntegerFeasible,
                GRB.TIME_LIMIT: constants.LpSolutionIntegerFeasible,
                GRB.SOLUTION_LIMIT: constants.LpSolutionIntegerFeasible,
                GRB.INTERRUPTED: constants.LpSolutionIntegerFeasible,
                GRB.NUMERIC: constants.LpSolutionIntegerFeasible,
            }

            lp.resolveOK = True
            for var in lp._variables:
                var.isModified = False
            status = gurobiLpStatus.get(solutionStatus, constants.LpSolutionNoSolutionFound)
            if status != constants.LpSolutionOptimal and status != constants.LpSolutionIntegerFeasible:
                return status

            # populate pulp solution values
            for var, value in zip(
                lp._variables, model.getAttr(GRB.Attr.X, model.getVars())
            ):
                var.varValue = value

            # populate pulp constraints slack
            for constr, value in zip(
                lp.constraints.values(),
                model.getAttr(GRB.Attr.Slack, model.getConstrs()),
            ):
                constr.slack = value

            if not model.getAttr(GRB.Attr.IsMIP):
                for var, value in zip(
                    lp._variables, model.getAttr(GRB.Attr.RC, model.getVars())
                ):
                    var.dj = value

                # put pi and slack variables against the constraints
                for constr, value in zip(
                    lp.constraints.values(),
                    model.getAttr(GRB.Attr.Pi, model.getConstrs()),
                ):
                    constr.pi = value

            return status

if SOLVER == "CPLEX":
    class CplexCallback(cplex.callbacks.MIPInfoCallback):
        terminate = False
        callback_calls = 0
        log_callback = None

        def __call__(self):
            if CplexCallback.terminate:
                self.abort()
                return

            CplexCallback.callback_calls += 1

            if CplexCallback.callback_calls % 2 == 0 and CplexCallback.log_callback is not None:
                runtime = self.get_time() - self.get_start_time()
                objbst = self.get_incumbent_objective_value()
                objbnd = self.get_best_objective_value()
                CplexCallback.log_callback(runtime, objbst, objbnd) 

    class CplexWatcher(Watcher):

        def __init__(self, prob, timeLimit, logPath):
            self.prob = prob
            self.solver = CPLEX_PY(msg=False, timeLimit = timeLimit, logPath = logPath, warmStart=False)
            self.solver.buildSolverModel(self.prob)
            self.solver.solverModel.register_callback(CplexCallback)

        def terminate(self):
            CplexCallback.terminate = True        


        def optimize(self, log_callback = None):
            CplexCallback.log_callback = log_callback
            CplexCallback.terminate = False
            CplexCallback.callback_calls = 0

            lp = self.prob
            
            self.solver.callSolver(lp)
            # get the solution information
            solutionStatus = self.solver.findSolutionValues(lp)
            for var in lp._variables:
                var.modified = False
            for constraint in lp.constraints.values():
                constraint.modified = False
            return solutionStatus
    


if SOLVER == "FSCIP":
    
    class FscipWatcher(Watcher): 
        def __init__(self, prob, timeLimit, logPath):
            self.prob = prob
            self.solver = FSCIP_CMD(msg=False, timeLimit = timeLimit, logPath = logPath, warmStart=False, path=os.getcwd() + "/tools/fscip.exe")

        def terminate(self):
            self.solver.terminate()      

        def optimize(self, log_callback = None):
            def callback(line):
                line = line.decode('utf-8')

                match = re.search(r"^[*\s]+(\d+)([*\s]+\d+){3}[*\s]+([\d.]+)[*\s]+([\d.]+)?", line)
                if match is not None:
                    log_callback(int(match[1]), int(float(match[3])), float(match[4]) if match[4] is not None else None)
            
            return self.solver.actualSolve(self.prob, callback if log_callback else None)


    
class LPLevels : 
   
    
    def __init__(self, layout, houses = None,  full_supply = False) :
        self.layout = layout
        self.houses = self.layout.houses if houses is None else houses
        self.prob = LpProblem("Skyscraperlevels", LpMaximize)
        
        self.weights_profit = {}
        
        weights_profit = self.weights_profit
        prob = self.prob
        e_mode = self.layout.engineer_mode # optimize 3-3-5
        def_inv_l = 3 if e_mode else 4 # default investor level
        
        for h in self.houses :
            h.init_levels() 
            
            # if not e_mode all residences are set to 1 (investor) in the constructor of Layout
            if h.residence == 0:
                h.fix_level(h.level, h.residence)
            elif full_supply and sum(h.stores) < 3:
                if not h.stores[0] == True:
                    h.fix_level(1,1)
                elif not h.stores[1] == True:
                    h.fix_level(2,1)
                elif not h.stores[2] == True:
                    h.fix_level(def_inv_l,1)
                h.panorama_effect = h.calculate_panorama()
                for n in h.neighbors:
                    n.panorama_effect = n.calculate_panorama()
            else :
                for l in range(len( A7PARAMS["levels"][0])) :
                    h.var_levels[0][l].setInitialValue(0)
                    h.var_levels[0][l].fixValue()
                
                for l in range(len( A7PARAMS["levels"][1])) :
                    if (l == def_inv_l - 1 or l == 4):
                        h.var_levels[1][l].setInitialValue(1 if h.level == l - 1 else 0)
                    else:                    
                        h.var_levels[1][l].setInitialValue(0)
                        h.var_levels[1][l].fixValue()
            
      
            h.var_panorama = [[LpVariable("HP_{}_{}_{}".format(h.ID, r, l.level), cat='Integer') for l in A7PARAMS["levels"][r]] for r in [0,1]]
            for r in [0,1]:
                for l in range(len( A7PARAMS["levels"][r])) :
                    if l == h.level - 1 and r == h.residence:
                        h.var_panorama[r][l].setInitialValue(h.panorama_effect)
                    else:
                        h.var_panorama[r][l].setInitialValue(0)

                    
                
        #layout.houses[2].fix_level(4)
       
                
        for h in self.houses :
            prob += 1 == sum(sum([h.var_levels[r][l.index] for l in A7PARAMS["levels"][r]]) for r in [0,1]) 
            neighborhood = []            

            r = h.residence
            for l in A7PARAMS["levels"][r] :                  

                T = []
                S = []
                L = h.var_levels[r][l.index]
                P = h.var_panorama[r][l.index]

                weights_profit[L] = h.get_residents(l,0)

                for h_ in h.neighbors :
                    if(h.dist(h_) > l.radius) :
                        continue

                    for r_ in [0,1]:
                        for l_ in A7PARAMS["levels"][r_] :
                            if l.level > l_.level or (l.level == l_.level and not r == r_):
                                S.append(h_.var_levels[r_][l_.index])
                            else :
                                T.append(h_.var_levels[r_][l_.index])


                T_ = LpVariable("T'_{}_{}_{}".format(h.ID, r, l.level), cat='Integer')
                prob += T_ <= 1 + 0.01 * (sum(t for t in T) - (sum(s for s in S)) - l.level)
                prob += P <= 5 * L
                prob += P <= l.level - sum(t for t in T) + 100 * T_ + sum(s for s in S)
                prob += P <= 5 * (1 - T_)
                prob += P >= 0
                weights_profit[P] = (h.get_residents(l,5) - h.get_residents(l,0)) / 5

                                      
 
        prob.objective = LpAffineExpression(weights_profit)
        self.watcher = None
    
    def terminate(self):
        if self.watcher is not None:
            self.watcher.terminate()

    def choose_solver(self, time_limit, log_path):
        if SOLVER == "GUROBI":
            self.watcher = GurobiWatcher(self.prob, time_limit, log_path)
        elif SOLVER == "CPLEX":
            self.watcher = CplexWatcher(self.prob, time_limit, log_path)
        else:
            self.watcher = FscipWatcher(self.prob, time_limit, log_path)
    
    def optimize(self, time_limit = None, log_path = None, log_callback = None):
        self.choose_solver(time_limit, log_path)
        self.status = self.watcher.optimize(log_callback)        
       
        if self.status != constants.LpSolutionOptimal and self.status != constants.LpSolutionIntegerFeasible:
            return
        
        self.objective = value(self.prob.objective)
        #w.stop()
        
        self.level_count = [[0 for l in A7PARAMS["levels"][r]] for r in [0,1]]
        self.panorama_count = [[0 for p in range(6)] for r in [0,1]]
        for h in self.houses :
            h.panorama_effect = 0
            for r in [0,1]:
                for l in range(len(h.var_levels[r])) :
                    if value(h.var_levels[r][l]) < 0.01 :
                        continue

                    self.level_count[r][l] += 1
                    h.residence = r
                    h.level = A7PARAMS["levels"][r][l].level
                    

                    p = round(value(h.var_panorama[r][l]))
                    self.panorama_count[r][p] += 1
                    h.panorama_effect = p
       

            
class Option:
    def __init__(self, identifier, description, init_set=False):
        self.identifier = identifier
        self.description = description
        self.init_set = init_set
        self.widget = None

    def render(self):
        self.widget = widgets.Checkbox(value=self.init_set, description=self.description,indent=False)
        self.widget.layout.width="30rem"
        return self.widget

    def enabled(self):
        return self.widget.value
    
class Group:
    def __init__(self, identifier, name):
        self.identifier = identifier
        self.name = name
        self.options = []
        self.widget = None

    def add_option(self, option):
        self.options.append(option)

    def render(self):
        self.widget = widgets.GridBox([o.render() for o in self.options],
                                      layout=widgets.Layout(grid_template_columns="repeat(3, 35rem)"))
        return self.widget

    def get_options(self):
        return [o.identifier for o in self.options if o.enabled()]
    
class OptimizerGUI:
    NORMAL_COLORS = [
        {"A": 255, "R": 3, "G": 94, "B": 94},
        {"A": 255, "R": 0, "G": 128, "B": 128},
        {"A": 255, "R": 68, "G": 166, "B": 166},
        {"A": 255, "R": 105, "G": 196, "B": 196}, 
        {"A": 255, "R": 161, "G": 234, "B": 234},
    ]
    HIGH_CONTRAST_COLORS = [
        {"A": 255, "R": 34, "G": 136, "B": 51},
        {"A": 255, "R": 68, "G": 119, "B": 170},
        {"A": 255, "R": 170, "G": 51, "B": 119},
        {"A": 255, "R": 204, "G": 187, "B": 68},
        {"A": 255, "R": 102, "G":204, "B": 238},
    ]
    
    def __init__(self):
        self.input_file = None
        self.layout = None
        self.log_path = None
        self.lp = None
        self.terminate = False

        self.groups = []

        self.txt_status = None
        self.vertical_margins = "0 0 1rem 0"
        self.horizontal_margins = "0 2rem 0 0"

        btn_ok = widgets.Button(description=_("OK"),
                                disabled=False)
        self.model = widgets.VBox([widgets.Dropdown(options=A7PARAMS["languages"], value="english"),
                                   btn_ok])
        


        def hide(elem):
            elem.layout.display = 'none'

        def callback(btn):
            global LANG
            LANG = self.model.children[0].value

            self.model.children = []            
            self.check_version()
            

        btn_ok.on_click(callback)
        
        display(self.model)

    def set_status(self, txt: str):
        if self.txt_status is None:
            print(txt)
        else:
            self.txt_status.value = txt

    def compose_header(self):
        def callback(btn):
            self.select_file()

        def hide(elem):
            elem.layout.display = "none"

        self.btn_file_chooser = widgets.FileUpload(accept='.ad', multiple=False)
        self.btn_file_chooser.observe(callback)
        self.btn_file_chooser.layout.margin = self.horizontal_margins

        self.label_filename = widgets.Label()
        hide(self.label_filename)

        return widgets.HBox([
            self.btn_file_chooser,
            self.label_filename,
        ])

    def compose_body(self):
        def hide(elem):
            elem.layout.display = 'none'


        def callback_optimize(btn):
            self.optimize()
            
        def callback_terminate(btn):
            self.terminate = True
            if self.lp is not None:
                self.lp.terminate()

        self.btn_optimize = widgets.Button(description=_("Optimize"))
        self.btn_optimize.on_click(callback_optimize)
        
        self.btn_terminate = widgets.Button(description=_("Terminate"))
        self.btn_terminate.on_click(callback_terminate)  
        
        hide(self.btn_terminate)

        g = Group("needs_0", _("Needs") + " - " + _("Engineers"))
        for need in A7PARAMS["needs"][0]:
            if not need.get("hidden"):
                g.add_option(Option(need["guid"], need["locaText"][LANG], True))
        self.groups.append(g)
        
        g = Group("needs_1", _("Needs") + " - " + _("Investors"))
        for need in A7PARAMS["needs"][1]:
            if not need.get("hidden"):
                g.add_option(Option(need["guid"], need["locaText"][LANG], True))
        self.groups.append(g)

        g = Group("items", _("Items"))
        for item in A7PARAMS["items"].values():
            g.add_option(Option(item["guid"], item["locaText"][LANG]))
        self.groups.append(g)

        g = Group("general", _("General"))
        g.add_option(Option("th_items", _("Use item list stored in townhall label")))
        g.add_option(Option("high_contrast", _("High contrast colors for skyscraper levels")))
        g.add_option(Option("full_supply", _("Enforce full store supply")))
        g.add_option(Option("skip_heuristic", _("Skip local optimization by swapping engineers and investors (gives occasionally better result)")))
        self.groups.append(g)
        
        self.input_time_limit = widgets.BoundedIntText(value=20, min=2, max=1440,step=1,
                                                       description=_("Time limit") + ":",disabled=False)
        self.input_time_limit.layout.width = "15rem"


        tab = widgets.Tab(children=[g.render() for g in self.groups])
        tab.children[-1].children += (widgets.HBox([self.input_time_limit, widgets.Label(value="min")]),)
        titles = [g.name for g in self.groups]
        for i in range(len(tab.children)):
            tab.set_title(i, titles[i])
        
        self.grid_stats = widgets.GridBox([], layout=widgets.Layout(grid_template_columns="repeat(2, 20rem)"))
        self.result_table = widgets.HTML(value="")

        vbox = widgets.VBox([
            tab,
            self.btn_optimize,
            self.grid_stats,
            self.btn_terminate,
            self.result_table
        ])

        for box in vbox.children:
            box.layout.margin = self.vertical_margins

        return vbox

    def compose_footer(self):
        self.txt_status = widgets.Text(value="", description=_("Status") + ":", disabled=True)
        self.txt_status.layout.width = "100%"
        return widgets.HBox([
            self.txt_status
        ])

    def check_version(self):
        """
        Check GitHub for a new release. If one was found, buttons to install the update or ignore it are displayed.
        """

        def hide(elem):
            elem.layout.display = 'none'

        try:
            response = requests.get("https://api.github.com/repos/NiHoel/Anno1800OptimizationTools/releases/latest")
            release = json.loads(response.content)
            version = release["tag_name"]
            if not version == TAG:
                label_update = widgets.Label(value=_("A new version is available"))
                btn_download = widgets.Button(description=_("Download"))
                btn_ignore = widgets.Button(description=_("Ignore"))

                update_box = widgets.VBox([
                    label_update,
                    widgets.HBox([btn_download, btn_ignore])
                ])

                def callback_ignore(btn):
                    hide(update_box)
                    self.show()

                def callback_download(btn):
                    try:
                        hide(update_box)
                        asset_url = release["assets"][0]["browser_download_url"]

                        img_loading = None
                        with open("imgs/loading-buffering.gif", "rb") as f:
                            img_loading = widgets.Image(
                                value=f.read(),
                                format='gif',
                                width="20px",
                                margin="auto"
                            )

                            self.model.children = tuple([img_loading] + list(self.model.children[1:]))

                        zip_response = requests.get(asset_url)
                        with zipfile.ZipFile(BytesIO(zip_response.content)) as archive:
                            archive.extractall(path=os.getcwd())

                        label_restart = widgets.HTML(value="<b><font color='red' size='20px'>{}</b>".format(
                            _("Close and re-open the application!")))
                        self.model.children = tuple([label_restart] + list(self.model.children[1:]))

                    except Exception as e:
                        self.set_status(str(e))
                        if img_loading is not None:
                            hide(img_loading)
                        self.show()

                btn_download.on_click(callback_download)
                btn_ignore.on_click(callback_ignore)

                # show buttons first
                self.model.children = tuple([update_box] + list(self.model.children))

            else:
                self.show()
        except Exception as e:
            self.set_status(str(e))
            self.show()


    def display(self):
        return self.model

    def show(self):
        def hide(elem):
            elem.layout.display = 'none'

        self.header = self.compose_header()
        self.body = self.compose_body()
        hide(self.body)
        self.footer = self.compose_footer()

        self.model.children += (self.header,)
        self.model.children += (self.body,)
        self.model.children += (self.footer,)

        for m in self.model.children:
            m.layout.margin = self.vertical_margins
        
        self.set_status(_("Ready")  + ". Solver: " + SOLVER)


    def select_file(self):
        files = self.btn_file_chooser.value
        if len(files) == 0:
            print("len(files) == 0")
            return
        
       
        file = None
        if type(files) is dict:
            file = list(files.values())[0]
        else:
            file = files[0]
            
        if self.input_file is not None and self.input_file == file:
            return
        
        self.input_file = file
        print(self.input_file.name)

        self.on_file_choosen()

    def get_file_name(self):
        if self.input_file is None:
            return None
        return self.input_file["metadata"]["name"] if "metadata" in self.input_file else self.input_file["name"]
        
    def on_file_choosen(self):
        def hide(elem):
            elem.layout.display = 'none'

        def show(elem):
            elem.layout.display = None

        try:
            self.set_status(_("Opening") + ": " + str(self.get_file_name()))

            hide(self.body)
            hide(self.label_filename)
            
            ad_json = json.loads(codecs.decode(self.input_file["content"], encoding="utf-8"))
            self.layout = Layout(ad_json)

            self.label_filename.value = self.get_file_name()
            show(self.label_filename)
            
            time_limit = 120
            if self.layout.engineer_mode:
                time_limit = len(self.layout.houses) / 1000
            else:
                time_limit = max(2, math.ceil(len(self.layout.houses) / 3 / 60))
            if SOLVER == "FSCIP":
                time_limit *= 3
            self.input_time_limit.value = time_limit

            show(self.body)
            show(self.btn_optimize)
            hide(self.btn_terminate)
            hide(self.grid_stats)
            hide(self.result_table)
            self.set_status(_("Ready") + ". " + _("MODE_3-3-5" if self.layout.engineer_mode else "MODE_4-5"))

        except Exception as e:
            self.set_status(_("Failed to read file: ") + str(e))
            raise e


    def get_options(self):
        options = dict()
        options["needs"] = [[],[]]
        for g in self.groups:
            if "needs" in g.identifier:
                options["needs"][int(g.identifier[-1])] = g.get_options()
            else:
                options[g.identifier] = g.get_options()

        return options

    def optimize(self):
        def hide(elem):
            elem.layout.display = 'none'

        def show(elem):
            elem.layout.display = None      
        
        try:
            hide(self.btn_optimize)
            show(self.btn_terminate)
            self.btn_file_chooser.disabled = True
            
            options = self.get_options()
            self.layout.set_options(options)
            
            
            layout = self.layout
            total_time = 60 * int(self.input_time_limit.value)
            
            
            lbl_run = widgets.Label("1/1")
            lbl_houses = widgets.Label("-/-")
            lbl_time = widgets.Label("-")
            lbl_elapsed = widgets.Label("-")
            lbl_incumbent = widgets.Label("-")
            lbl_bound = widgets.Label("-")
            lbl_improvement = widgets.Label("-")
            
            children = [
                widgets.Label(_("Run")),            lbl_run,
                widgets.Label(_("Residences")),     lbl_houses,
                widgets.Label(_("Time limit")),     lbl_time] if len(layout.clusters) > 1 else []
            
            self.grid_stats.children = children + [
                widgets.Label(_("Elapsed Time")),        lbl_elapsed,
                widgets.Label(_("Best found")),     lbl_incumbent,
                widgets.Label(_("Upper bound")),    lbl_bound,
                widgets.Label(_("Gain in last 10 min")), lbl_improvement,
            ]
            
            self.logs = []
            
            def callback(time, incumbent, bound):
                incumbent = int(incumbent)
                self.logs.append([time, incumbent, bound])
                
                lbl_elapsed.value = "{}:{:02} min".format(int(time/60), int(time%60))
                if incumbent is not None:
                    lbl_incumbent.value = "{:,.0f}".format(incumbent)
                if bound is not None:
                    lbl_bound.value = "{:,.1f}".format(bound)
                
                prev_incumbent = 0
                prev_time = time
                for log in reversed(self.logs):
                    if log[1] is not None:
                        prev_incumbent = log[1]
                        prev_time = log[0]
                    if log[0] + 600 < time:
                        break
                
                if time - prev_time < 1:
                    return
                
                if incumbent is not None:
                    lbl_improvement.value = "{:,.0f}".format(incumbent - prev_incumbent )
                
            
            def run():
                try:                              
                    
                    show(self.grid_stats)
                    self.set_status(_("Optimizing ..."))
                    options = self.get_options()
                    
                    skipped_cluster = False
                    
                    if layout.engineer_mode and not ("skip_heuristic" in options["general"]):
                        print("run heuristic")
                        def cb(residents):
                            lbl_incumbent.value = "{:,.0f}".format(residents)
                            return self.terminate
                            
                        layout.run_heuristic([0,3], [1,3], True, cb)
                        cb(self.layout.get_residents())
                    
                    count = 1
                    for c in layout.clusters :
                        self.logs = []
                        self.btn_terminate.description = _("Terminate") if count >= len(layout.clusters) else _("Next run")
                        self.terminate = False

                        time_limit = None
                        if total_time is not None:
                            time_limit = max(120, int(total_time * len(c) / len(layout.houses)))
                            lbl_time.value = "{} min".format(math.ceil(time_limit/60))

                        lbl_run.value = "{}/{}".format(count, len(layout.clusters))
                        lbl_houses.value = "{:,.0f}/{:,.0f}".format(len(c), len(layout.houses))

                        lbl_elapsed.value = "-"
                        lbl_incumbent.value = "-"
                        lbl_bound.value = "-"
                        lbl_improvement.value = "-"
                        
                        only_cluster = (len(layout.cluster_gaps) == 0)
                        houses = c if only_cluster else None
                        
                        self.lp = LPLevels(layout, houses = houses,  full_supply = ("full_supply" in options["general"]))
                        
                        if not only_cluster:
                            for h in layout.houses :
                                if not h in c and not h in layout.cluster_gaps :
                                    h.fix_level(h.level, h.residence)
                        
                        try:
                            #in rare occations with few houses, FSCIP finds a solution but generates an empty solution file
                            self.lp.optimize(time_limit = time_limit, log_path = self.log_path, log_callback = callback)
                            
                            if self.lp.status != constants.LpSolutionOptimal and self.lp.status != constants.LpSolutionIntegerFeasible:
                                self.set_status(_("No solution found"))
                        except Exception as e:
                            print(e)
                            skipped_cluster = True                     
                        
                        count += 1
                    
                   
                    if skipped_cluster:                            
                        def cb(residents):
                            lbl_incumbent.value = "{:,.0f}".format(residents)
                            return self.terminate
                        
                        if layout.engineer_mode:
                            layout.run_heuristic([1,3], [1,5], True, cb)
                        else:
                            layout.run_heuristic([1,4], [1,5], True, cb)
                        cb(self.layout.get_residents())  
                    else:
                        if self.lp.status != constants.LpSolutionOptimal and self.lp.status != constants.LpSolutionIntegerFeasible:
                            self.set_status(_("No solution found"))
                            show(self.btn_optimize)
                            return

                        self.set_status(_("Solution found"))

                    hide(self.btn_terminate)
                    hide(self.grid_stats)  
                    self.btn_file_chooser.disabled = False

                    out_path = os.getcwd() + "\\" + pathlib.Path(self.get_file_name()).stem + "_opt.ad"
                    options = self.get_options()
                    self.layout.save(out_path, OptimizerGUI.HIGH_CONTRAST_COLORS if "high_contrast" in options["general"] else OptimizerGUI.NORMAL_COLORS)

                    s=self.layout.get_summary()
                    df = pd.DataFrame(s, index=[col["Level"] for col in s])
 
                    self.result_table.value = (df.style.set_table_styles([{'selector': 'th', 'props': [('padding', '0 6px 0 6px'),('border-bottom', '1px solid black')]}])
                         .set_properties(**{'text-align': 'center'})
                         #.set_properties(subset = pd.IndexSlice[["4"], :], **{'background-color': 'rgb(245, 245, 245)'})
                         .set_properties(subset = pd.IndexSlice[[_("Total")], :], **{'font-weight': '700', 'background-color': 'rgb(245, 245, 245)', 'border-top': '1px solid black'})
                         .set_properties(subset = pd.IndexSlice[:,[_("Level")]], **{'font-weight': '700'})
                         .hide(axis='index').to_html() +
                          "<br><span>{}: {}</span>".format(_("Result written to"), out_path))

                    show(self.result_table)
                    
                    if self.log_path is not None:
                        tab = PrettyTable()
                        for col in df:
                            tab.add_column(col, df[col])
                            
                        with open(self.log_path, "a") as f:
                            f.write("\n")
                            f.write(tab.get_string())
                except Exception as e:
                    self.set_status(str(e))
                    show(self.btn_optimize)
                    hide(self.btn_terminate)
                    hide(self.grid_stats)
                    self.btn_file_chooser.disabled = False
                    raise e
                
      
            thread = threading.Thread(target=run) # required to run in a seperate thread that the terminate button works
            thread.start()
        
        except Exception as e:
            self.set_status(str(e))
            show(self.btn_optimize)
            hide(self.btn_terminate)
            hide(self.grid_stats)
            self.btn_file_chooser.disabled = False
            raise e
