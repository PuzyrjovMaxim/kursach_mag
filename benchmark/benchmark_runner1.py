import traceback

from benchmark.benchmark_result import (
    BenchmarkResult
)


class BenchmarkRunner:

    def __init__(
        self,
        solvers
    ):

        self.solvers = solvers

    def run_instance(
        self,
        instance
    ):

        results = []

        for solver in self.solvers:

            try:

                solution = solver.solve(
                    instance
                )

                result = (
                    BenchmarkResult.from_solution(
                        instance.name,
                        solution
                    )
                )

                results.append(
                    result
                )

            except Exception as error:

                print(
                    f"[ERROR] "
                    f"{solver.name} "
                    f"failed on "
                    f"{instance.name}"
                )

                print(error)

                traceback.print_exc()

        return results

    def run_instances(
        self,
        instances
    ):

        all_results = []

        for idx, instance in enumerate(instances, 1):
            print(
                f"\n{'=' * 60}"
            )
            print(
                f"[{idx}/{len(instances)}] "
                f"INSTANCE: {instance.name}"
            )
            print(
                f"  Customers: {instance.customer_count}"
            )
            print(
                f"  Vehicle limit: {instance.vehicle_count}"
            )
            print(
                f"  Capacity: {instance.vehicle_capacity}"
            )
            print(
                f"{'=' * 60}"
            )

            results = self.run_instance(
                instance
            )

            all_results.extend(
                results
            )
        return all_results

    def run_folder(
        self,
        parser,
        file_paths
    ):

        instances = []

        for file_path in file_paths:

            try:

                instance = parser.parse(
                    file_path
                )

                instances.append(
                    instance
                )

            except Exception as error:

                print(
                    f"[ERROR] "
                    f"Cannot load "
                    f"{file_path}"
                )

                print(error)

        return self.run_instances(
            instances
        )

    def filter_by_algorithm(
            self,
            results,
            algorithm_name
    ):

        return [

            result

            for result in results

            if (
                    result.algorithm
                    ==
                    algorithm_name
            )

        ]

    def best_result(
            self,
            results
    ):

        if not results:
            return None

        return min(
            results,
            key=lambda result:
            result.total_cost
        )