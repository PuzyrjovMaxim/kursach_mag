import time

from ortools.constraint_solver import (
    pywrapcp,
    routing_enums_pb2
)

from models.route import Route
from models.solution import Solution

from routing.route_utils import (
    route_distance,
    served_clients
)

from algorithms.base_solver import BaseSolver


class ORToolsSolver(BaseSolver):

    @property
    def name(self):
        return "OR-Tools"

    def solve(self, instance):

        start_time = time.perf_counter()

        manager = pywrapcp.RoutingIndexManager(
            len(instance.nodes),
            instance.vehicle_count,
            0
        )

        routing = pywrapcp.RoutingModel(
            manager
        )

        #
        # Distance callback
        #

        def distance_callback(
            from_index,
            to_index
        ):

            from_node = manager.IndexToNode(
                from_index
            )

            to_node = manager.IndexToNode(
                to_index
            )

            distance = (
                instance.distance_matrix.get(
                    from_node,
                    to_node
                )
            )

            return int(
                round(distance * 100)
            )

        distance_callback_index = (
            routing.RegisterTransitCallback(
                distance_callback
            )
        )

        routing.SetArcCostEvaluatorOfAllVehicles(
            distance_callback_index
        )

        #
        # Vehicle fixed cost
        # помогает минимизировать число машин
        #

        for vehicle_id in range(
            instance.vehicle_count
        ):

            routing.SetFixedCostOfVehicle(
                100000,
                vehicle_id
            )

        #
        # Capacity
        #

        def demand_callback(
            from_index
        ):

            node = manager.IndexToNode(
                from_index
            )

            return (
                instance.nodes[node]
                .demand
            )

        demand_callback_index = (
            routing.RegisterUnaryTransitCallback(
                demand_callback
            )
        )

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            [
                instance.vehicle_capacity
            ] * instance.vehicle_count,
            True,
            "Capacity"
        )

        #
        # Time callback
        #

        def time_callback(
            from_index,
            to_index
        ):

            from_node = manager.IndexToNode(
                from_index
            )

            to_node = manager.IndexToNode(
                to_index
            )

            travel_time = (
                instance.distance_matrix.get(
                    from_node,
                    to_node
                )
            )

            service_time = (
                instance.nodes[
                    from_node
                ].service_time
            )

            return int(
                round(
                    travel_time +
                    service_time
                )
            )

        time_callback_index = (
            routing.RegisterTransitCallback(
                time_callback
            )
        )

        routing.AddDimension(
            time_callback_index,
            100000,
            100000,
            False,
            "Time"
        )

        time_dimension = (
            routing.GetDimensionOrDie(
                "Time"
            )
        )

        #
        # Customer windows
        #

        for node_index, node in enumerate(
            instance.nodes
        ):

            index = manager.NodeToIndex(
                node_index
            )

            time_dimension.CumulVar(
                index
            ).SetRange(
                int(node.ready_time),
                int(node.due_date)
            )

        #
        # Depot return window
        #

        depot = instance.depot

        for vehicle_id in range(
            instance.vehicle_count
        ):

            end_index = routing.End(
                vehicle_id
            )

            time_dimension.CumulVar(
                end_index
            ).SetRange(
                int(depot.ready_time),
                int(depot.due_date)
            )

        #
        # Search parameters
        #

        search_parameters = (
            pywrapcp
            .DefaultRoutingSearchParameters()
        )

        search_parameters.first_solution_strategy = (
            routing_enums_pb2
            .FirstSolutionStrategy
            .PARALLEL_CHEAPEST_INSERTION
        )

        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2
            .LocalSearchMetaheuristic
            .GUIDED_LOCAL_SEARCH
        )

        search_parameters.time_limit.seconds = 30

        solution = routing.SolveWithParameters(
            search_parameters
        )

        if solution is None:

            return Solution(
                algorithm=self.name,
                feasible=False
            )

        routes = []

        for vehicle_id in range(
            instance.vehicle_count
        ):

            index = routing.Start(
                vehicle_id
            )

            route = Route(
                vehicle_id + 1
            )

            while not routing.IsEnd(
                index
            ):

                node_index = (
                    manager.IndexToNode(
                        index
                    )
                )

                if node_index != 0:

                    route.add_client(
                        instance.nodes[
                            node_index
                        ]
                    )

                index = solution.Value(
                    routing.NextVar(
                        index
                    )
                )

            if route.clients:

                route.distance = (
                    route_distance(
                        instance.depot,
                        route.clients,
                        instance.distance_matrix
                    )
                )

                routes.append(
                    route
                )

        total_distance = sum(
            route.distance
            for route in routes
        )

        served = served_clients(
            [
                route.clients
                for route in routes
            ]
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        return Solution(
            algorithm=self.name,
            routes=routes,
            total_distance=total_distance,
            execution_time=execution_time,
            served_clients=served,
            unserved_clients=(
                len(instance.clients)
                - served
            ),
            feasible=(
                served ==
                len(instance.clients)
            )
        )