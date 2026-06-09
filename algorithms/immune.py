import random
import time

from algorithms.base_solver import BaseSolver
from algorithms.greedy import GreedySolver
from algorithms.clarke_wright import ClarkeWrightSolver

from models.route import Route
from models.solution import Solution

from optimization.encoding import (
    encode,
    decode
)

from optimization.objective import (
    evaluate_solution
)

from routing.route_utils import (
    route_distance,
    route_completion_time
)


class ImmuneSolver(BaseSolver):

    def __init__(
        self,
        population_size=100,
        generations=150,
        clone_factor=20
    ):

        self.population_size = population_size
        self.generations = generations
        self.clone_factor = clone_factor

    @property
    def name(self):

        return "Immune"

    #
    # ---------- M1 ----------
    #

    def move_single(self, chromosome):

        if len(chromosome) < 2:
            return chromosome[:]

        result = chromosome[:]

        i = random.randrange(len(result))

        customer = result.pop(i)

        j = random.randrange(
            len(result) + 1
        )

        result.insert(j, customer)

        return result

    #
    # ---------- M2 ----------
    #

    def move_pair(self, chromosome):

        if len(chromosome) < 3:
            return chromosome[:]

        result = chromosome[:]

        start = random.randint(
            0,
            len(result) - 2
        )

        pair = result[start:start + 2]

        del result[start:start + 2]

        pos = random.randint(
            0,
            len(result)
        )

        result[pos:pos] = pair

        return result

    #
    # ---------- M3 ----------
    #

    def move_reversed_pair(self, chromosome):

        if len(chromosome) < 3:
            return chromosome[:]

        result = chromosome[:]

        start = random.randint(
            0,
            len(result) - 2
        )

        pair = result[start:start + 2]

        pair.reverse()

        del result[start:start + 2]

        pos = random.randint(
            0,
            len(result)
        )

        result[pos:pos] = pair

        return result

    #
    # ---------- M4 ----------
    #

    def swap_single(self, chromosome):

        if len(chromosome) < 2:
            return chromosome[:]

        result = chromosome[:]

        i, j = random.sample(
            range(len(result)),
            2
        )

        result[i], result[j] = (
            result[j],
            result[i]
        )

        return result

    #
    # ---------- M5 ----------
    #

    def swap_pair_single(self, chromosome):

        if len(chromosome) < 3:
            return chromosome[:]

        result = chromosome[:]

        pair_start = random.randint(
            0,
            len(result) - 2
        )

        single_idx = random.randrange(
            len(result)
        )

        if (
            single_idx == pair_start
            or
            single_idx == pair_start + 1
        ):
            return result

        pair = result[
            pair_start:
            pair_start + 2
        ]

        single = result[single_idx]

        result[pair_start] = single

        result[pair_start + 1] = pair[1]

        result[single_idx] = pair[0]

        return result

    #
    # ---------- M6 ----------
    #

    def swap_pairs(self, chromosome):

        if len(chromosome) < 4:
            return chromosome[:]

        result = chromosome[:]

        i = random.randint(
            0,
            len(result) - 3
        )

        j = random.randint(
            0,
            len(result) - 3
        )

        attempts = 0

        while abs(i - j) < 2 and attempts < 10:
            j = random.randint(
                0,
                len(result) - 3
            )

            attempts += 1

        if abs(i - j) < 2:
            return result

        pair1 = result[i:i + 2]
        pair2 = result[j:j + 2]

        result[i:i + 2] = pair2
        result[j:j + 2] = pair1

        return result

    #
    # ---------- M7 ----------
    #

    def edge_exchange_same_route(
            self,
            chromosome
    ):

        if len(chromosome) < 4:
            return chromosome[:]

        result = chromosome[:]

        i = random.randint(
            0,
            len(result) - 3
        )

        j = random.randint(
            i + 1,
            len(result) - 2
        )

        u = result[i]
        x = result[i + 1]

        v = result[j]
        y = result[j + 1]

        result[i] = u
        result[i + 1] = v

        result[j] = x
        result[j + 1] = y

        return result

    #
    # ---------- M8 ----------
    #

    def edge_exchange_diff_route(
        self,
        chromosome
    ):

        return self.edge_exchange_same_route(
            chromosome
        )

    #
    # ---------- M9 ----------
    #

    def edge_exchange_cross(
            self,
            chromosome
    ):

        if len(chromosome) < 4:
            return chromosome[:]

        result = chromosome[:]

        i = random.randint(
            0,
            len(result) - 3
        )

        j = random.randint(
            i + 1,
            len(result) - 2
        )

        u = result[i]
        x = result[i + 1]

        v = result[j]
        y = result[j + 1]

        result[i] = u
        result[i + 1] = y

        result[j] = x
        result[j + 1] = v

        return result

    def mutate(self, chromosome):

        operators = [

            self.move_single,
            self.move_pair,
            self.move_reversed_pair,
            self.swap_single,
            self.swap_pair_single,
            self.swap_pairs,
            self.edge_exchange_same_route,
            self.edge_exchange_diff_route,
            self.edge_exchange_cross

        ]

        operator = random.choice(
            operators
        )

        return operator(
            chromosome
        )

    def fitness(
            self,
            chromosome,
            instance
    ):

        routes = decode(
            chromosome,
            instance
        )

        distance, penalty = (
            evaluate_solution(
                instance,
                routes
            )
        )

        return (
            len(routes),
            distance + penalty
        )

    def solve(
        self,
        instance
    ):

        start_time = (
            time.perf_counter()
        )

        #
        # Initial population
        #

        greedy_solution = (
            GreedySolver().solve(
                instance
            )
        )
        cw_solution = (
            ClarkeWrightSolver().solve(instance)
        )

        greedy_chromosome = encode(
            [
                route.clients
                for route
                in greedy_solution.routes
            ]
        )
        cw_chromosome = encode(
            [route.clients for route in cw_solution.routes]
        )

        population = [
            greedy_chromosome,
            cw_chromosome
        ]

        clients = (
            instance.clients[:]
        )

        while (
            len(population)
            <
            self.population_size
        ):

            chromosome = clients[:]

            random.shuffle(
                chromosome
            )

            population.append(
                chromosome
            )

        #
        # Evolution
        #

        for _ in range(
            self.generations
        ):

            scored = []

            for chromosome in population:

                cost = self.fitness(
                    chromosome,
                    instance
                )

                scored.append(
                    (
                        cost,
                        chromosome
                    )
                )

            scored.sort(
                key=lambda x: x[0]
            )

            best_cost = scored[0][0]

            clones = []

            population_size = len(scored)

            for rank, (_, chromosome) in enumerate(
                    scored
            ):

                affinity = (
                                   population_size - rank
                           ) / population_size

                clone_count = max(
                    1,
                    int(
                        affinity *
                        self.clone_factor
                    )
                )

                for _ in range(
                        clone_count
                ):
                    clone = self.mutate(
                        chromosome
                    )

                    clones.append(
                        clone
                    )

            combined = (
                population +
                clones
            )

            scored = []

            for chromosome in combined:

                cost = self.fitness(
                    chromosome,
                    instance
                )

                scored.append(
                    (
                        cost,
                        chromosome
                    )
                )

            scored.sort(
                key=lambda x: x[0]
            )

            population = [

                chromosome

                for _, chromosome

                in scored[
                    :self.population_size
                ]

            ]

        #
        # Best solution
        #

        best = min(
            population,
            key=lambda c:
            self.fitness(
                c,
                instance
            )
        )

        routes_data = decode(
            best,
            instance
        )

        routes = []

        total_distance = 0.0

        depot = instance.depot

        matrix = (
            instance.distance_matrix
        )

        for index, clients in enumerate(
            routes_data
        ):

            route = Route(
                vehicle_id=index + 1
            )

            route.clients = clients

            route.load = sum(
                client.demand
                for client
                in clients
            )

            route.distance = (
                route_distance(
                    depot,
                    clients,
                    matrix
                )
            )

            route.total_time = (
                route_completion_time(
                    depot,
                    clients,
                    matrix
                )
            )

            total_distance += (
                route.distance
            )

            routes.append(
                route
            )

        distance, penalty = (
            evaluate_solution(
                instance,
                routes_data
            )
        )

        execution_time = (
            time.perf_counter()
            - start_time
        )

        served_clients = sum(
            len(route.clients)
            for route in routes
        )

        solution = Solution(

            algorithm=self.name,

            routes=routes,

            total_distance=distance,

            total_penalty=penalty,

            execution_time=execution_time,

            feasible=(penalty == 0),

            served_clients=served_clients,

            unserved_clients=(
                len(instance.clients)
                - served_clients
            )
        )

        return solution