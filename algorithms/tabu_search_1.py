import random
import time
from collections import deque
from itertools import permutations

from algorithms.base_solver import BaseSolver
from algorithms.greedy import GreedySolver

from optimization.encoding import (
    encode,
    decode
)

from optimization.objective import (
    evaluate_solution
)

from models.route import Route
from models.solution import Solution


class TabuSearchSolver(BaseSolver):

    def __init__(
        self,
        max_iterations=1000,
        tabu_tenure=30,
        move_probability=0.4,
        exchange_probability=0.4,
        swap_probability=0.2
    ):

        self.max_iterations = (
            max_iterations
        )

        self.tabu_tenure = (
            tabu_tenure
        )

        self.move_probability = (
            move_probability
        )

        self.exchange_probability = (
            exchange_probability
        )

        self.swap_probability = (
            swap_probability
        )

    @property
    def name(self):

        return "Tabu Search"

    #
    # ------------------------
    # Fitness
    # ------------------------
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

        return distance + penalty

    #
    # ------------------------
    # Move
    # ------------------------
    #

    def move_operator(
        self,
        chromosome
    ):

        if len(chromosome) < 2:
            return chromosome[:], None

        result = chromosome[:]

        i = random.randint(
            0,
            len(result) - 1
        )

        client = result.pop(i)

        j = random.randint(
            0,
            len(result)
        )

        result.insert(
            j,
            client
        )

        move = (
            "move",
            client.id
        )

        return result, move

    #
    # ------------------------
    # Exchange
    # ------------------------
    #

    def exchange_operator(
        self,
        chromosome
    ):

        if len(chromosome) < 2:
            return chromosome[:], None

        result = chromosome[:]

        i, j = random.sample(
            range(len(result)),
            2
        )

        result[i], result[j] = (
            result[j],
            result[i]
        )

        move = (
            "exchange",
            result[i].id,
            result[j].id
        )

        return result, move

    #
    # ------------------------
    # Swap (3 nodes)
    # ------------------------
    #

    def swap_operator(
        self,
        chromosome,
        instance
    ):

        if len(chromosome) < 3:
            return chromosome[:], None

        result = chromosome[:]

        indices = sorted(
            random.sample(
                range(len(result)),
                3
            )
        )

        nodes = [
            result[i]
            for i in indices
        ]

        best = result[:]

        best_cost = (
            self.fitness(
                instance,
                decode(
                    best,
                    instance
                )
            )
        )

        for perm in permutations(
            nodes
        ):

            candidate = result[:]

            for pos, node in zip(
                indices,
                perm
            ):

                candidate[pos] = node

            candidate_cost = (
                self.fitness(
                    instance,
                    decode(
                        candidate,
                        instance
                    )
                )
            )

            if (
                candidate_cost
                <
                best_cost
            ):

                best_cost = (
                    candidate_cost
                )

                best = candidate

        move = (
            "swap",
            tuple(
                node.id
                for node in nodes
            )
        )

        return best, move

    #
    # ------------------------
    # Random operator
    # ------------------------
    #

    def generate_neighbor(
        self,
        chromosome,
        instance
    ):

        r = random.random()

        if r < self.move_probability:

            return self.move_operator(
                chromosome
            )

        if (
            r
            <
            self.move_probability
            +
            self.exchange_probability
        ):

            return self.exchange_operator(
                chromosome
            )

        return self.swap_operator(
            chromosome,
            instance
        )

    #
    # ------------------------
    # Solve
    # ------------------------
    #

    def solve(
        self,
        instance
    ):

        start_time = (
            time.perf_counter()
        )

        #
        # Initial solution
        #

        greedy_solution = (
            GreedySolver().solve(
                instance
            )
        )

        current_routes = [
            route.clients
            for route
            in greedy_solution.routes
        ]

        current_chromosome = (
            encode(
                current_routes
            )
        )

        current_cost = (
            self.fitness(
                instance,
                current_routes
            )
        )

        best_chromosome = (
            current_chromosome[:]
        )

        best_cost = (
            current_cost
        )

        tabu_list = deque(
            maxlen=self.tabu_tenure
        )

        no_improvement = 0

        #
        # Main loop
        #

        for _ in range(
            self.max_iterations
        ):

            best_neighbor = None

            best_neighbor_cost = (
                float("inf")
            )

            best_move = None

            #
            # Neighborhood
            #

            for _ in range(50):

                neighbor, move = (
                    self.generate_neighbor(
                        current_chromosome,
                        instance
                    )
                )

                neighbor_routes = (
                    decode(
                        neighbor,
                        instance
                    )
                )

                neighbor_cost = (
                    self.fitness(
                        instance,
                        neighbor_routes
                    )
                )

                is_tabu = (
                    move in tabu_list
                )

                aspiration = (
                    neighbor_cost
                    <
                    best_cost
                )

                if (
                    is_tabu
                    and
                    not aspiration
                ):
                    continue

                if (
                    neighbor_cost
                    <
                    best_neighbor_cost
                ):

                    best_neighbor = (
                        neighbor
                    )

                    best_neighbor_cost = (
                        neighbor_cost
                    )

                    best_move = move

            if best_neighbor is None:
                continue

            current_chromosome = (
                best_neighbor
            )

            current_cost = (
                best_neighbor_cost
            )

            tabu_list.append(
                best_move
            )

            #
            # Global best
            #

            if (
                current_cost
                <
                best_cost
            ):

                best_cost = (
                    current_cost
                )

                best_chromosome = (
                    current_chromosome[:]
                )

                no_improvement = 0

            else:

                no_improvement += 1

            #
            # Diversification
            #

            if no_improvement > 200:

                random.shuffle(
                    current_chromosome
                )

                no_improvement = 0

        #
        # Decode best
        #

        best_routes_clients = (
            decode(
                best_chromosome,
                instance
            )
        )

        routes = []

        for vehicle_id, clients in enumerate(
            best_routes_clients,
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
                best_routes_clients
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