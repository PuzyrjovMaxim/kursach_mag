# algorithms/genetic.py
import random
import time
import copy

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


class GeneticSolver(BaseSolver):

    def __init__(
            self,
            population_size=400,
            generations=100,
            elite_fraction=0.1,
            crossover_rate=0.9,
            mutation_rate=0.3,
            gvns_attempts=20
    ):
        self.population_size = population_size
        self.generations = generations
        self.elite_size = max(1, int(population_size * elite_fraction))
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.gvns_attempts = gvns_attempts

    @property
    def name(self):
        return "Genetic"

    #
    # -------- Все 9 операторов --------
    #

    def m1_move_single(self, chromosome):
        if len(chromosome) < 2:
            return chromosome[:]
        result = chromosome[:]
        i = random.randrange(len(result))
        customer = result.pop(i)
        j = random.randrange(len(result) + 1)
        result.insert(j, customer)
        return result

    def m2_move_pair(self, chromosome):
        if len(chromosome) < 3:
            return chromosome[:]
        result = chromosome[:]
        start = random.randint(0, len(result) - 2)
        pair = result[start:start + 2]
        del result[start:start + 2]
        pos = random.randint(0, len(result))
        result[pos:pos] = pair
        return result

    def m3_move_reversed_pair(self, chromosome):
        if len(chromosome) < 3:
            return chromosome[:]
        result = chromosome[:]
        start = random.randint(0, len(result) - 2)
        pair = result[start:start + 2]
        pair.reverse()
        del result[start:start + 2]
        pos = random.randint(0, len(result))
        result[pos:pos] = pair
        return result

    def m4_swap_single(self, chromosome):
        if len(chromosome) < 2:
            return chromosome[:]
        result = chromosome[:]
        i, j = random.sample(range(len(result)), 2)
        result[i], result[j] = result[j], result[i]
        return result

    def m5_swap_pair_single(self, chromosome):
        if len(chromosome) < 3:
            return chromosome[:]
        result = chromosome[:]
        pair_start = random.randint(0, len(result) - 2)
        single_idx = random.randrange(len(result))
        if single_idx == pair_start or single_idx == pair_start + 1:
            return result
        pair = result[pair_start:pair_start + 2]
        single = result[single_idx]
        result[pair_start] = single
        result[pair_start + 1] = pair[1]
        result[single_idx] = pair[0]
        return result

    def m6_swap_pairs(self, chromosome):
        if len(chromosome) < 4:
            return chromosome[:]
        result = chromosome[:]
        i = random.randint(0, len(result) - 3)
        j = random.randint(0, len(result) - 3)
        attempts = 0
        while abs(i - j) < 2 and attempts < 10:
            j = random.randint(0, len(result) - 3)
            attempts += 1
        if abs(i - j) < 2:
            return result
        pair1 = result[i:i + 2]
        pair2 = result[j:j + 2]
        result[i:i + 2] = pair2
        result[j:j + 2] = pair1
        return result

    def m7_edge_exchange_same_route(self, chromosome):
        if len(chromosome) < 4:
            return chromosome[:]
        result = chromosome[:]
        i = random.randint(0, len(result) - 3)
        j = random.randint(i + 1, len(result) - 2)
        u = result[i]
        x = result[i + 1]
        v = result[j]
        y = result[j + 1]
        result[i] = u
        result[i + 1] = v
        result[j] = x
        result[j + 1] = y
        return result

    def m8_edge_exchange_diff_route(self, chromosome):
        return self.m7_edge_exchange_same_route(chromosome)

    def m9_edge_exchange_cross(self, chromosome):
        if len(chromosome) < 4:
            return chromosome[:]
        result = chromosome[:]
        i = random.randint(0, len(result) - 3)
        j = random.randint(i + 1, len(result) - 2)
        u = result[i]
        x = result[i + 1]
        v = result[j]
        y = result[j + 1]
        result[i] = u
        result[i + 1] = y
        result[j] = x
        result[j + 1] = v
        return result

    def get_all_neighborhoods(self):
        return [
            self.m1_move_single,
            self.m2_move_pair,
            self.m3_move_reversed_pair,
            self.m4_swap_single,
            self.m5_swap_pair_single,
            self.m6_swap_pairs,
            self.m7_edge_exchange_same_route,
            self.m8_edge_exchange_diff_route,
            self.m9_edge_exchange_cross
        ]

    #
    # -------- GVNS --------
    #

    def gvns_improve(self, chromosome, instance):
        """GVNS - применяет все операторы для улучшения хромосомы"""
        if not chromosome:
            return chromosome

        current = chromosome[:]
        neighborhoods = self.get_all_neighborhoods()

        routes = decode(current, instance)
        distance, penalty = evaluate_solution(instance, routes)
        current_fitness = (penalty, len(routes), distance)

        improved = True
        attempts = 0

        while improved and attempts < self.gvns_attempts:
            improved = False
            attempts += 1

            for operator in neighborhoods:
                neighbor = operator(current)
                routes_n = decode(neighbor, instance)
                dist_n, penalty_n = evaluate_solution(instance, routes_n)
                neighbor_fitness = (penalty_n, len(routes_n), dist_n)

                if neighbor_fitness < current_fitness:
                    current = neighbor
                    current_fitness = neighbor_fitness
                    improved = True
                    break

        return current

    #
    # -------- Кроссовер (исправленный) --------
    #

    def crossover(self, parent1, parent2):
        """Order Crossover (OX) с проверкой длины"""
        if random.random() > self.crossover_rate:
            return parent1[:], parent2[:]

        if len(parent1) < 2 or len(parent2) < 2:
            return parent1[:], parent2[:]

        size = min(len(parent1), len(parent2))

        p1 = random.randint(0, size - 2)
        p2 = random.randint(p1 + 1, size - 1)

        child1 = [-1] * size
        child2 = [-1] * size

        # Копируем сегменты
        child1[p1:p2] = parent1[p1:p2]
        child2[p1:p2] = parent2[p1:p2]

        # Заполняем child1 из parent2
        pos = p2
        for i in range(size):
            idx = (p2 + i) % size
            value = parent2[idx]
            if value not in child1:
                child1[pos % size] = value
                pos += 1

        # Заполняем child2 из parent1
        pos = p2
        for i in range(size):
            idx = (p2 + i) % size
            value = parent1[idx]
            if value not in child2:
                child2[pos % size] = value
                pos += 1

        child1 = [c for c in child1 if c != -1]
        child2 = [c for c in child2 if c != -1]

        return child1, child2

    #
    # -------- Fitness --------
    #

    def fitness_tuple(self, chromosome, instance):
        if not chromosome:
            return (float('inf'), 0, float('inf'))
        routes = decode(chromosome, instance)
        distance, penalty = evaluate_solution(instance, routes)
        return (penalty, len(routes), distance)

    def is_better(self, sol1, sol2):
        p1, v1, d1 = sol1
        p2, v2, d2 = sol2
        if p1 != p2:
            return p1 < p2
        if v1 != v2:
            return v1 < v2
        return d1 < d2

    #
    # -------- Selection --------
    #

    def roulette_select(self, population, fitnesses):
        costs = []
        for penalty, vehicles, distance in fitnesses:
            cost = penalty * 1_000_000 + vehicles * 10_000 + distance
            costs.append(cost)

        max_cost = max(costs)
        weights = [max_cost - c + 1e-9 for c in costs]
        total = sum(weights)

        r = random.uniform(0, total)
        cumsum = 0.0

        for chromosome, w in zip(population, weights):
            cumsum += w
            if cumsum >= r:
                return chromosome

        return population[-1]

    #
    # -------- Initialisation --------
    #

    def initialize_population(self, instance):
        population = []

        # Greedy solution
        try:
            greedy_solution = GreedySolver().solve(instance)
            greedy_chromosome = encode([route.clients for route in greedy_solution.routes])
            population.append(greedy_chromosome)
            penalty, vehicles, distance = self.fitness_tuple(greedy_chromosome, instance)
            print(f"  [GA init] Greedy: penalty={penalty}, vehicles={vehicles}, distance={distance:.2f}")
        except Exception as e:
            print(f"  [GA init] Greedy failed: {e}")

        # Clarke-Wright solution
        try:
            cw_solution = ClarkeWrightSolver().solve(instance)
            cw_chromosome = encode([route.clients for route in cw_solution.routes])
            population.append(cw_chromosome)
            penalty, vehicles, distance = self.fitness_tuple(cw_chromosome, instance)
            print(f"  [GA init] Clarke-Wright: penalty={penalty}, vehicles={vehicles}, distance={distance:.2f}")
        except Exception as e:
            print(f"  [GA init] Clarke-Wright failed: {e}")

        # Random chromosomes
        clients_objects = instance.clients[:]

        while len(population) < self.population_size:
            random_chrom = clients_objects[:]
            random.shuffle(random_chrom)
            population.append(random_chrom)

        return population

    #
    # -------- Main loop --------
    #

    def solve(self, instance):
        start_time = time.perf_counter()

        population = self.initialize_population(instance)

        best_chromosome = None
        best_fitness_tuple = None

        print(f"  [GA] Starting evolution: pop={self.population_size}, generations={self.generations}")

        # Initial evaluation
        fitnesses = [self.fitness_tuple(c, instance) for c in population]

        for chrom, fit in zip(population, fitnesses):
            if best_fitness_tuple is None or self.is_better(fit, best_fitness_tuple):
                best_fitness_tuple = fit
                best_chromosome = chrom[:]

        print(
            f"  [GA] Init best: penalty={best_fitness_tuple[0]}, vehicles={best_fitness_tuple[1]}, cost={best_fitness_tuple[2]:.2f}")

        for generation in range(self.generations):
            # Проверка на пустую популяцию
            if not population:
                print(f"  [GA] Gen {generation}: Population empty! Reinitializing...")
                population = self.initialize_population(instance)
                fitnesses = [self.fitness_tuple(c, instance) for c in population]
                continue

            # Сортировка
            scored = sorted(zip(fitnesses, population), key=lambda x: x[0])
            sorted_population = [chrom for _, chrom in scored]
            sorted_fitnesses = [fit for fit, _ in scored]

            # Элитизм
            new_population = [copy.deepcopy(chrom) for chrom in sorted_population[:self.elite_size]]

            # Скрещивание и GVNS
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate and len(sorted_population) >= 2:
                    parent1 = self.roulette_select(sorted_population, sorted_fitnesses)
                    parent2 = self.roulette_select(sorted_population, sorted_fitnesses)
                    child1, child2 = self.crossover(parent1, parent2)
                    children = [child1, child2]
                else:
                    parent = self.roulette_select(sorted_population, sorted_fitnesses)
                    children = [copy.deepcopy(parent)]

                for child in children:
                    if child and len(child) > 0:
                        # Применяем GVNS
                        child = self.gvns_improve(child, instance)
                        new_population.append(child)

            if not new_population:
                print(f"  [GA] Gen {generation}: New population empty! Breaking...")
                break

            population = new_population[:self.population_size]

            # Оценка популяции
            fitnesses = [self.fitness_tuple(c, instance) for c in population]

            # Обновляем лучшее решение
            for chrom, fit in zip(population, fitnesses):
                if self.is_better(fit, best_fitness_tuple):
                    best_fitness_tuple = fit
                    best_chromosome = copy.deepcopy(chrom)
                    print(f"  [GA] Gen {generation}: ★ NEW BEST ★ "
                          f"penalty={best_fitness_tuple[0]}, "
                          f"vehicles={best_fitness_tuple[1]}, "
                          f"cost={best_fitness_tuple[2]:.2f}")

            if generation % 50 == 0 or generation == self.generations - 1:
                print(f"  [GA] Gen {generation:>4d} | "
                      f"penalty={best_fitness_tuple[0]}, "
                      f"vehicles={best_fitness_tuple[1]}, "
                      f"cost={best_fitness_tuple[2]:.2f}")

        # Финальное решение
        if best_chromosome is None or not best_chromosome:
            print("  [GA] No valid solution found! Returning best from population...")
            if population:
                best_chromosome = population[0]
                best_fitness_tuple = fitnesses[0]
            else:
                return Solution(
                    algorithm=self.name,
                    routes=[],
                    total_distance=0,
                    total_penalty=0,
                    execution_time=0,
                    feasible=False,
                    served_clients=0,
                    unserved_clients=0
                )

        # Декодируем финальное решение
        routes_data = decode(best_chromosome, instance)

        routes = []
        depot = instance.depot
        matrix = instance.distance_matrix

        for index, clients in enumerate(routes_data, start=1):
            if not clients:
                continue
            route = Route(vehicle_id=index)
            route.clients = clients
            route.load = sum(c.demand for c in clients)
            route.distance = route_distance(depot, clients, matrix)
            route.total_time = route_completion_time(depot, clients, matrix)
            routes.append(route)

        distance, penalty = evaluate_solution(instance, routes_data)
        execution_time = time.perf_counter() - start_time
        served_clients = sum(len(route.clients) for route in routes)

        print(f"\n  [GA] Final: penalty={penalty}, vehicles={len(routes)}, distance={distance:.2f}")

        return Solution(
            algorithm=self.name,
            routes=routes,
            total_distance=distance,
            total_penalty=penalty,
            execution_time=execution_time,
            feasible=(penalty == 0),
            served_clients=served_clients,
            unserved_clients=len(instance.clients) - served_clients
        )