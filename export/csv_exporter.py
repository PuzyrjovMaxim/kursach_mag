import csv
from pathlib import Path


class CsvExporter:

    HEADER = [

        "dataset",

        "algorithm",

        "total_distance",

        "total_penalty",

        "total_cost",

        "execution_time",

        "route_count",

        "used_vehicles",

        "served_clients",

        "unserved_clients",

        "coverage_ratio",

        "average_route_distance",

        "feasible"
    ]

    @staticmethod
    def export(
        results,
        output_file
    ):

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=CsvExporter.HEADER
            )

            writer.writeheader()

            for result in results:

                writer.writerow(
                    result.to_dict()
                )

    @staticmethod
    def export_algorithm(
        results,
        algorithm_name,
        output_file
    ):

        filtered_results = [

            result

            for result in results

            if (
                result.algorithm
                ==
                algorithm_name
            )

        ]

        CsvExporter.export(
            filtered_results,
            output_file
        )

    @staticmethod
    def export_feasible_only(
        results,
        output_file
    ):

        filtered_results = [

            result

            for result in results

            if result.feasible

        ]

        CsvExporter.export(
            filtered_results,
            output_file
        )

    @staticmethod
    def export_infeasible_only(
        results,
        output_file
    ):

        filtered_results = [

            result

            for result in results

            if not result.feasible

        ]

        CsvExporter.export(
            filtered_results,
            output_file
        )