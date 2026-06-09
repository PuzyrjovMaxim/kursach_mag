import copy
import random
import time
from collections import deque

from algorithms.base_solver import BaseSolver
from algorithms.greedy import GreedySolver

from optimization.objective import (
    evaluate_solution
)

from models.route import Route
from models.solution import Solution


class TabuSearchSolver(BaseSolver):

    def __init__(
        self,
        max_iterations=1000,
        neighborhood_size=100,
        tabu_tenure=50
    ):

        self.max_iterations = max_iterations
        self.neighborhood_size = neighborhood_size
        self.tabu_tenure = tabu_tenure

    @property
    def name(self):

        return "Tabu Search"

    #
    # --------------------------------------------------
    # FITNESS
    # --------------------------------------------------
    #

    def fitness(
            self,
            instance,
            routes
    ):

        distance, penalty = (
            evaluate_solution(
                instance,
                routes
            )
        )

        return (
            penalty,
            len(routes),
            distance
        )

    #
    # --------------------------------------------------
    # RELOCATE
    # --------------------------------------------------
    #

    def relocate_move(
            self,
            routes
    ):

        routes = [
            route[:]
            for route in routes
        ]

        non_empty = [
            i
            for i, route in enumerate(routes)
            if len(route) > 0
        ]

        if len(non_empty) < 1:
            return routes, None

        from_route_idx = random.choice(
            non_empty
        )

        to_route_idx = random.randint(
            0,
            len(routes) - 1
        )

        while (
                to_route_idx == from_route_idx
                and
                len(routes) > 1
        ):
            to_route_idx = random.randint(
                0,
                len(routes) - 1
            )

        from_route = routes[
            from_route_idx
        ]

        to_route = routes[
            to_route_idx
        ]

        client_pos = random.randint(
            0,
            len(from_route) - 1
        )

        client = from_route.pop(
            client_pos
        )

        insert_pos = random.randint(
            0,
            len(to_route)
        )

        to_route.insert(
            insert_pos,
            client
        )

        routes = [
            route
            for route in routes
            if len(route) > 0
        ]

        move = (
            "relocate",
            client.id,
            from_route_idx,
            to_route_idx
        )

        return routes, move

    #
    # --------------------------------------------------
    # EXCHANGE
    # --------------------------------------------------
    #

    def exchange_move(
            self,
            routes
    ):

        routes = [
            route[:]
            for route in routes
        ]

        candidates = [
            i
            for i, route in enumerate(routes)
            if len(route) > 0
        ]

        if len(candidates) < 2:
            return routes, None

        r1, r2 = random.sample(
            candidates,
            2
        )

        i = random.randint(
            0,
            len(routes[r1]) - 1
        )

        j = random.randint(
            0,
            len(routes[r2]) - 1
        )

        routes[r1][i], routes[r2][j] = (
            routes[r2][j],
            routes[r1][i]
        )

        move = (
            "exchange",
            routes[r1][i].id,
            routes[r2][j].id
        )

        return routes, move

    #
    # --------------------------------------------------
    # 2-OPT
    # --------------------------------------------------
    #

    def two_opt_move(
            self,
            routes
    ):

        routes = [
            route[:]
            for route in routes
        ]

        candidates = [
            route
            for route in routes
            if len(route) >= 4
        ]

        if not candidates:
            return routes, None

        route = random.choice(
            candidates
        )

        i = random.randint(
            0,
            len(route) - 3
        )

        j = random.randint(
            i + 1,
            len(route) - 1
        )

        route[i:j] = reversed(
            route[i:j]
        )

        move = (
            "2opt",
            i,
            j
        )

        return routes, move

    #
    # --------------------------------------------------
    # MERGE
    # --------------------------------------------------
    #

    def merge_routes(
        self,
        routes
    ):

        routes = copy.deepcopy(routes)

        if len(routes) < 2:
            return routes, None

        r1, r2 = random.sample(
            range(len(routes)),
            2
        )

        merged = (
            routes[r1]
            +
            routes[r2]
        )

        new_routes = []

        for idx, route in enumerate(routes):

            if idx in (r1, r2):
                continue

            new_routes.append(route)

        new_routes.append(
            merged
        )

        move = (
            "merge",
            r1,
            r2
        )

        return new_routes, move

    #
    # --------------------------------------------------
    # RANDOM MOVE
    # --------------------------------------------------
    #

    def generate_neighbor(
        self,
        routes
    ):

        r = random.random()

        if r < 0.30:

            return self.relocate(
                routes
            )

        if r < 0.60:

            return self.exchange(
                routes
            )

        if r < 0.50:
            return self.relocate(routes)

        if r < 0.80:
            return self.exchange(routes)

        return self.two_opt(routes)

    #
    # --------------------------------------------------
    # SOLVE
    # --------------------------------------------------
    #

    def solve(
        self,
        instance
    ):

        start_time = (
            time.perf_counter()
        )

        greedy_solution = (
            GreedySolver().solve(
                instance
            )
        )

        current_routes = [
            route.clients[:]
            for route
            in greedy_solution.routes
        ]

        current_cost = (
            self.fitness(
                instance,
                current_routes
            )
        )

        best_routes = (
            copy.deepcopy(
                current_routes
            )
        )

        best_cost = (
            current_cost
        )

        tabu_list = deque(
            maxlen=self.tabu_tenure
        )

        stagnation = 0

        for _ in range(
            self.max_iterations
        ):

            best_neighbor = None
            best_neighbor_cost = None
            best_move = None

            for _ in range(
                self.neighborhood_size
            ):

                operator = random.choice(
                    [
                        self.relocate_move,
                        self.exchange_move,
                        self.two_opt_move
                    ]
                )

                neighbor_routes, move = (
                    operator(
                        current_routes
                    )
                )

                neighbor_cost = (
                    self.fitness(
                        instance,
                        neighbor_routes
                    )
                )

                cost = self.fitness(
                    instance,
                    neighbor_routes
                )

                tabu = (
                    move in tabu_list
                )

                aspiration = (
                    cost < best_cost
                )

                if tabu and not aspiration:
                    continue

                if (
                    best_neighbor_cost
                    is None
                    or
                    cost
                    <
                    best_neighbor_cost
                ):
                    best_neighbor = [
                        route[:]
                        for route in neighbor_routes
                    ]

                    best_neighbor_cost = (
                        cost
                    )

                    best_move = move

            if best_neighbor is None:
                continue

            current_routes = [
                route[:]
                for route
                in best_neighbor
            ]

            current_cost = (
                best_neighbor_cost
            )

            tabu_list.append(
                best_move
            )

            print(
                "best:",
                best_cost,
                "current:",
                current_cost
            )
            if (
                current_cost
                <
                best_cost
            ):

                best_cost = (
                    current_cost
                )

                best_routes = (
                    copy.deepcopy(
                        current_routes
                    )
                )

                stagnation = 0

            else:

                stagnation += 1

            #
            # diversification
            #

            if stagnation > 200:

                random.shuffle(
                    current_routes
                )

                stagnation = 0

        #
        # build solution
        #

        routes = []

        for vehicle_id, clients in enumerate(
            best_routes,
            start=1
        ):

            route = Route(
                vehicle_id
            )

            for client in clients:

                route.add_client(
                    client
                )

            routes.append(
                route
            )

        total_distance, total_penalty = (
            evaluate_solution(
                instance,
                best_routes
            )
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        served = sum(
            len(route.clients)
            for route in routes
        )

        return Solution(
            algorithm=self.name,
            routes=routes,
            total_distance=total_distance,
            total_penalty=total_penalty,
            execution_time=execution_time,
            feasible=(
                total_penalty == 0
            ),
            served_clients=served,
            unserved_clients=(
                len(instance.clients)
                - served
            )
        )