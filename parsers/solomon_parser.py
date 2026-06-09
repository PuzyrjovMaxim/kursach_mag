from pathlib import Path

from models.client import Client
from models.instance import Instance

from routing.distance_matrix import DistanceMatrix

from parsers.base_parser import BaseParser
from parsers.exceptions import (
    InvalidDataError,
    InvalidFileFormatError
)


class SolomonParser(BaseParser):

    def parse(self, file_path: str) -> Instance:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(file_path)

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        vehicle_count = None
        vehicle_capacity = None

        nodes = []

        customer_section = False

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not stripped:
                continue

            #
            # VEHICLE SECTION
            #
            if stripped.startswith("NUMBER"):

                try:
                    values = lines[index + 1].split()

                    vehicle_count = int(values[0])
                    vehicle_capacity = int(values[1])

                except Exception as exc:
                    raise InvalidFileFormatError(
                        "Failed to parse VEHICLE section"
                    ) from exc

            #
            # CUSTOMER SECTION
            #
            if stripped.startswith("CUST NO."):
                customer_section = True
                continue

            if not customer_section:
                continue

            parts = stripped.split()

            if len(parts) != 7:
                continue

            try:

                node = Client(
                    id=int(parts[0]),
                    x=float(parts[1]),
                    y=float(parts[2]),
                    demand=int(parts[3]),
                    ready_time=float(parts[4]),
                    due_date=float(parts[5]),
                    service_time=float(parts[6])
                )

                nodes.append(node)

            except ValueError as exc:

                raise InvalidDataError(
                    f"Invalid node line: {stripped}"
                ) from exc

        #
        # VALIDATION
        #

        if vehicle_count is None:
            raise InvalidDataError(
                "Vehicle count not found"
            )

        if vehicle_capacity is None:
            raise InvalidDataError(
                "Vehicle capacity not found"
            )

        if not nodes:
            raise InvalidDataError(
                "No nodes found"
            )

        #
        # SORT BY NODE ID
        #

        nodes.sort(key=lambda node: node.id)

        #
        # DEPOT MUST BE NODE 0
        #

        if nodes[0].id != 0:
            raise InvalidDataError(
                "Depot node (id=0) not found"
            )

        #
        # BUILD DISTANCE MATRIX
        #

        distance_matrix = DistanceMatrix(nodes)

        #
        # CREATE INSTANCE
        #

        return Instance(
            name=path.stem,
            vehicle_count=vehicle_count,
            vehicle_capacity=vehicle_capacity,
            nodes=nodes,
            distance_matrix=distance_matrix
        )