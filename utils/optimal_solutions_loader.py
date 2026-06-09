# utils/optimal_solutions_loader.py
"""
Загрузчик оптимальных решений с сайта SINTEF
URL: www.sintef.no/projectweb/top/vrptw/100-customers/
"""

import json
import urllib.request
from pathlib import Path
from typing import Dict, Optional


class OptimalSolutionsLoader:
    """
    Загрузчик оптимальных решений для VRPTW
    Данные с SINTEF (оптимальные значения для Solomon instances)
    """

    # Известные оптимальные решения для C101, C102, и т.д.
    # Источник: www.sintef.no/projectweb/top/vrptw/100-customers/
    OPTIMAL_SOLUTIONS = {
        # C1 тип (сгруппированные клиенты)
        "C101": {"distance": 828.94, "vehicles": 10},
        "C102": {"distance": 828.94, "vehicles": 10},
        "C103": {"distance": 828.06, "vehicles": 10},
        "C104": {"distance": 824.78, "vehicles": 10},
        "C105": {"distance": 828.94, "vehicles": 10},
        "C106": {"distance": 828.94, "vehicles": 10},
        "C107": {"distance": 828.94, "vehicles": 10},
        "C108": {"distance": 828.94, "vehicles": 10},
        "C109": {"distance": 828.94, "vehicles": 10},

        # C2 тип
        "C201": {"distance": 589.86, "vehicles": 3},
        "C202": {"distance": 589.86, "vehicles": 3},
        "C203": {"distance": 591.17, "vehicles": 3},
        "C204": {"distance": 590.60, "vehicles": 3},
        "C205": {"distance": 588.88, "vehicles": 3},
        "C206": {"distance": 588.49, "vehicles": 3},
        "C207": {"distance": 588.29, "vehicles": 3},
        "C208": {"distance": 588.32, "vehicles": 3},

        # R1 тип (случайные клиенты)
        "R101": {"distance": 1645.79, "vehicles": 19},
        "R102": {"distance": 1486.12, "vehicles": 17},
        "R103": {"distance": 1292.68, "vehicles": 14},
        "R104": {"distance": 1007.24, "vehicles": 10},
        "R105": {"distance": 1377.11, "vehicles": 14},
        "R106": {"distance": 1252.03, "vehicles": 13},
        "R107": {"distance": 1111.35, "vehicles": 11},
        "R108": {"distance": 968.66, "vehicles": 10},
        "R109": {"distance": 1194.73, "vehicles": 12},
        "R110": {"distance": 1084.09, "vehicles": 11},
        "R111": {"distance": 1096.72, "vehicles": 11},
        "R112": {"distance": 982.14, "vehicles": 10},

        # R2 тип
        "R201": {"distance": 1252.37, "vehicles": 4},
        "R202": {"distance": 1191.70, "vehicles": 4},
        "R203": {"distance": 942.78, "vehicles": 4},
        "R204": {"distance": 849.78, "vehicles": 3},
        "R205": {"distance": 1034.61, "vehicles": 4},
        "R206": {"distance": 985.00, "vehicles": 4},
        "R207": {"distance": 903.58, "vehicles": 3},
        "R208": {"distance": 734.44, "vehicles": 3},
        "R209": {"distance": 957.19, "vehicles": 4},
        "R210": {"distance": 968.08, "vehicles": 4},
        "R211": {"distance": 895.68, "vehicles": 3},

        # RC1 тип (смешанные)
        "RC101": {"distance": 1696.94, "vehicles": 14},
        "RC102": {"distance": 1554.75, "vehicles": 13},
        "RC103": {"distance": 1261.67, "vehicles": 11},
        "RC104": {"distance": 1135.48, "vehicles": 10},
        "RC105": {"distance": 1629.44, "vehicles": 14},
        "RC106": {"distance": 1426.81, "vehicles": 12},
        "RC107": {"distance": 1230.48, "vehicles": 11},
        "RC108": {"distance": 1139.10, "vehicles": 10},

        # RC2 тип
        "RC201": {"distance": 1406.94, "vehicles": 4},
        "RC202": {"distance": 1365.64, "vehicles": 4},
        "RC203": {"distance": 1050.66, "vehicles": 4},
        "RC204": {"distance": 803.68, "vehicles": 3},
        "RC205": {"distance": 1297.19, "vehicles": 4},
        "RC206": {"distance": 1147.09, "vehicles": 4},
        "RC207": {"distance": 1064.60, "vehicles": 3},
        "RC208": {"distance": 832.65, "vehicles": 3},
    }

    @classmethod
    def get_optimal(cls, instance_name: str) -> Optional[Dict]:
        """Получить оптимальное решение для инстанса"""
        return cls.OPTIMAL_SOLUTIONS.get(instance_name.upper())

    @classmethod
    def calculate_gap(cls, instance_name: str, achieved_distance: float,
                      achieved_vehicles: int) -> Dict:
        """
        Вычисление отклонения от оптимального решения (GAP)
        """
        optimal = cls.get_optimal(instance_name)

        if optimal is None:
            return {"distance_gap": None, "vehicles_gap": None, "has_optimal": False}

        distance_gap = ((achieved_distance - optimal["distance"]) / optimal["distance"]) * 100
        vehicles_gap = achieved_vehicles - optimal["vehicles"]

        return {
            "optimal_distance": optimal["distance"],
            "optimal_vehicles": optimal["vehicles"],
            "distance_gap": distance_gap,
            "vehicles_gap": vehicles_gap,
            "has_optimal": True
        }

    @classmethod
    def get_all_groups(cls) -> Dict:
        """Группировка оптимальных решений по типам"""
        groups = {
            "C1": [], "C2": [], "R1": [], "R2": [], "RC1": [], "RC2": []
        }

        for name, data in cls.OPTIMAL_SOLUTIONS.items():
            if name.startswith("C10"):
                groups["C1"].append((name, data))
            elif name.startswith("C20"):
                groups["C2"].append((name, data))
            elif name.startswith("R10"):
                groups["R1"].append((name, data))
            elif name.startswith("R20"):
                groups["R2"].append((name, data))
            elif name.startswith("RC10"):
                groups["RC1"].append((name, data))
            elif name.startswith("RC20"):
                groups["RC2"].append((name, data))

        return groups