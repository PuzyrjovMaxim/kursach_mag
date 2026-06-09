from dataclasses import dataclass


@dataclass
class BenchmarkResult:

    dataset: str

    algorithm: str

    total_distance: float

    total_penalty: float

    total_cost: float

    execution_time: float

    route_count: int

    used_vehicles: int

    served_clients: int

    unserved_clients: int

    coverage_ratio: float

    average_route_distance: float

    feasible: bool

    @property
    def status(self) -> str:

        return (
            "Feasible"
            if self.feasible
            else "Infeasible"
        )

    def to_dict(self) -> dict:

        return {

            "dataset":
                self.dataset,

            "algorithm":
                self.algorithm,

            "total_distance":
                self.total_distance,

            "total_penalty":
                self.total_penalty,

            "total_cost":
                self.total_cost,

            "execution_time":
                self.execution_time,

            "route_count":
                self.route_count,

            "used_vehicles":
                self.used_vehicles,

            "served_clients":
                self.served_clients,

            "unserved_clients":
                self.unserved_clients,

            "coverage_ratio":
                self.coverage_ratio,

            "average_route_distance":
                self.average_route_distance,

            "feasible":
                self.feasible
        }

    @classmethod
    def from_solution(
        cls,
        dataset_name: str,
        solution
    ):

        return cls(

            dataset=dataset_name,

            algorithm=solution.algorithm,

            total_distance=
            solution.total_distance,

            total_penalty=
            solution.total_penalty,

            total_cost=
            solution.total_cost,

            execution_time=
            solution.execution_time,

            route_count=
            solution.route_count,

            used_vehicles=
            solution.used_vehicles,

            served_clients=
            solution.served_clients,

            unserved_clients=
            solution.unserved_clients,

            coverage_ratio=
            solution.coverage_ratio,

            average_route_distance=
            solution.average_route_distance,

            feasible=
            solution.feasible
        )

    def __repr__(self):

        return (

            f"BenchmarkResult("
            f"dataset='{self.dataset}', "
            f"algorithm='{self.algorithm}', "
            f"cost={self.total_cost:.2f}, "
            f"time={self.execution_time:.4f}s)"
        )