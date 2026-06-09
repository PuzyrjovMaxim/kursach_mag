from pathlib import Path

from parsers.solomon_parser import (
    SolomonParser
)


class DatasetLoader:

    def __init__(
        self,
        parser=None
    ):

        self.parser = (
            parser
            if parser is not None
            else SolomonParser()
        )

    def load_file(
        self,
        file_path
    ):

        return self.parser.parse(
            file_path
        )

    def load_folder(
        self,
        folder_path,
        recursive=False
    ):

        folder = Path(
            folder_path
        )

        if not folder.exists():

            raise FileNotFoundError(
                f"Folder not found: "
                f"{folder_path}"
            )

        pattern = (
            "**/*.txt"
            if recursive
            else "*.txt"
        )

        instances = []

        for file_path in sorted(
            folder.glob(pattern)
        ):

            try:

                instance = (
                    self.load_file(
                        file_path
                    )
                )

                instances.append(
                    instance
                )

            except Exception as error:

                print(
                    f"[ERROR] "
                    f"{file_path}"
                )

                print(error)

        return instances

    def load_by_prefix(
        self,
        folder_path,
        prefix,
        recursive=False
    ):

        instances = self.load_folder(
            folder_path,
            recursive
        )

        return [

            instance

            for instance
            in instances

            if (
                instance.name.startswith(
                    prefix
                )
            )

        ]

    def load_by_customer_count(
        self,
        folder_path,
        customer_count,
        recursive=False
    ):

        instances = self.load_folder(
            folder_path,
            recursive
        )

        return [

            instance

            for instance
            in instances

            if (
                instance.customer_count
                ==
                customer_count
            )

        ]

    def load_by_capacity(
        self,
        folder_path,
        capacity,
        recursive=False
    ):

        instances = self.load_folder(
            folder_path,
            recursive
        )

        return [

            instance

            for instance
            in instances

            if (
                instance.vehicle_capacity
                ==
                capacity
            )

        ]

    def load_by_vehicle_count(
        self,
        folder_path,
        vehicle_count,
        recursive=False
    ):

        instances = self.load_folder(
            folder_path,
            recursive
        )

        return [

            instance

            for instance
            in instances

            if (
                instance.vehicle_count
                ==
                vehicle_count
            )

        ]

    def load_names(
        self,
        folder_path,
        recursive=False
    ):

        instances = self.load_folder(
            folder_path,
            recursive
        )

        return [

            instance.name

            for instance
            in instances

        ]

    def group_by_prefix(
        self,
        folder_path,
        recursive=False
    ):

        instances = self.load_folder(
            folder_path,
            recursive
        )

        groups = {

            "C": [],
            "R": [],
            "RC": []
        }

        for instance in instances:

            name = (
                instance.name.upper()
            )

            if name.startswith(
                "RC"
            ):

                groups["RC"].append(
                    instance
                )

            elif name.startswith(
                "R"
            ):

                groups["R"].append(
                    instance
                )

            elif name.startswith(
                "C"
            ):

                groups["C"].append(
                    instance
                )

        return groups

    def summary(
        self,
        folder_path,
        recursive=False
    ):

        instances = self.load_folder(
            folder_path,
            recursive
        )

        print()

        print(
            "=" * 60
        )

        print(
            "DATASET SUMMARY"
        )

        print(
            "=" * 60
        )

        print(
            f"Instances: "
            f"{len(instances)}"
        )

        if not instances:
            return

        customers = [

            instance.customer_count

            for instance
            in instances

        ]

        capacities = [

            instance.vehicle_capacity

            for instance
            in instances

        ]

        vehicles = [

            instance.vehicle_count

            for instance
            in instances

        ]

        print(
            f"Min customers: "
            f"{min(customers)}"
        )

        print(
            f"Max customers: "
            f"{max(customers)}"
        )

        print(
            f"Min capacity: "
            f"{min(capacities)}"
        )

        print(
            f"Max capacity: "
            f"{max(capacities)}"
        )

        print(
            f"Min vehicles: "
            f"{min(vehicles)}"
        )

        print(
            f"Max vehicles: "
            f"{max(vehicles)}"
        )