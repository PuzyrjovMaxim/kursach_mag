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
            population_size=200,
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

    # ========================================================================
    # 6 ОПЕРАТОРОВ ИЗ СТАТЬИ
    # ========================================================================

    def operator_1_relocation(self, chromosome):
        """
        Relocation operator:
        Randomly select a node i from a route and reinsert this node
        into any other position within the same route.
        """
        if len(chromosome) < 2:
            return chromosome[:]

        result = chromosome[:]
        i = random.randrange(len(result))
        node = result.pop(i)
        j = random.randrange(len(result) + 1)
        result.insert(j, node)
        return result

    def operator_2_2opt(self, chromosome):
        """
        2-opt operator:
        Randomly select two nodes i and j from a route and reverse
        the chromosome segment between these two nodes.
        """
        if len(chromosome) < 3:
            return chromosome[:]

        result = chromosome[:]
        i = random.randrange(len(result) - 1)
        j = random.randrange(i + 1, len(result))
        result[i:j + 1] = reversed(result[i:j + 1])
        return result

    def operator_3_3opt(self, chromosome):
        """
        3-opt operator:
        Randomly select three nodes i, j, and k from a route,
        reverse the two chromosome segments formed between these nodes,
        and then swap them to create a new route.
        """
        if len(chromosome) < 6:
            return chromosome[:]

        result = chromosome[:]
        n = len(result)

        # Выбираем три точки
        positions = sorted(random.sample(range(1, n), 3))
        i, j, k = positions

        # Разбиваем на сегменты
        segment1 = result[i:j]
        segment2 = result[j:k]

        # Реверсируем и меняем местами
        result[i:i + len(segment2)] = segment2[::-1]
        result[i + len(segment2):k] = segment1[::-1]

        return result

    def operator_4_or_opt(self, chromosome):
        """
        Or-opt operator:
        Randomly select a node i from a route, extract a chromosome segment
        of length three starting from this node, and reinsert this segment
        into any position within the remaining chromosome sequence.
        """
        if len(chromosome) < 4:
            return chromosome[:]

        result = chromosome[:]

        # Выбираем начальную позицию сегмента длины 3
        start = random.randint(0, len(result) - 3)
        segment = result[start:start + 3]

        # Удаляем сегмент
        del result[start:start + 3]

        # Вставляем в случайную позицию
        if len(result) > 0:
            pos = random.randint(0, len(result))
            result[pos:pos] = segment
        else:
            result.extend(segment)

        return result

    def operator_5_swap(self, chromosome):
        """
        Swap operator:
        Randomly select two nodes i and j from a route and swap these two nodes.
        """
        if len(chromosome) < 2:
            return chromosome[:]

        result = chromosome[:]
        i, j = random.sample(range(len(result)), 2)
        result[i], result[j] = result[j], result[i]
        return result

    def operator_6_cross(self, parent1, parent2):
        """
        Cross operator:
        Randomly select two chromosomes, then choose two breakpoints from each chromosome.
        Exchange the segments following the breakpoints between the two chromosomes.
        """
        if len(parent1) < 2 or len(parent2) < 2:
            return parent1[:], parent2[:]

        # Выбираем точки разрыва на каждой хромосоме
        break1 = random.randint(1, len(parent1) - 1)
        break2 = random.randint(1, len(parent2) - 1)

        # Обмениваем хвосты
        child1 = parent1[:break1] + parent2[break2:]
        child2 = parent2[:break2] + parent1[break1:]

        # Удаляем дубликаты (если есть)
        def remove_duplicates(chrom):
            seen = set()
            result = []
            for gene in chrom:
                if gene.id not in seen:
                    seen.add(gene.id)
                    result.append(gene)
            return result

        return remove_duplicates(child1), remove_duplicates(child2)

    def get_all_operators(self):
        """Возвращает все 5 операторов для локального поиска (1-5)"""
        return [
            self.operator_1_relocation,
            self.operator_2_2opt,
            self.operator_3_3opt,
            self.operator_4_or_opt,
            self.operator_5_swap
        ]

    def mutate(self, chromosome):
        """Мутация - случайный оператор из 1-5"""
        if random.random() > self.mutation_rate:
            return chromosome[:]

        operators = self.get_all_operators()
        operator = random.choice(operators)
        return operator(chromosome)

    # ========================================================================
    # GVNS - применяет все 5 операторов для улучшения
    # ========================================================================

    def gvns_improve(self, chromosome, instance):
        """
        GVNS: последовательно применяет все 5 операторов (1-5)
        Если найден лучший сосед - обновляем решение и начинаем сначала
        """
        if not chromosome:
            return chromosome

        current = chromosome[:]
        operators = self.get_all_operators()

        # Оценка текущего решения
        routes = decode(current, instance)
        distance, penalty = evaluate_solution(instance, routes)
        current_fitness = (penalty, len(routes), distance)

        improved = True
        attempts = 0

        while improved and attempts < self.gvns_attempts:
            improved = False
            attempts += 1

            for operator in operators:
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

    # ========================================================================
    # Кроссовер (Operator 6 - Cross)
    # ========================================================================

    def crossover(self, parent1, parent2):
        """Cross operator (Operator 6)"""
        if random.random() > self.crossover_rate:
            return parent1[:], parent2[:]

        return self.operator_6_cross(parent1, parent2)

    # ========================================================================
    # Fitness
    # ========================================================================

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

    # ========================================================================
    # Selection (Roulette)
    # ========================================================================

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

    # ========================================================================
    # Initialization
    # ========================================================================

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

        # # Clarke-Wright solution
        # try:
        #     cw_solution = ClarkeWrightSolver().solve(instance)
        #     cw_chromosome = encode([route.clients for route in cw_solution.routes])
        #     population.append(cw_chromosome)
        #     penalty, vehicles, distance = self.fitness_tuple(cw_chromosome, instance)
        #     print(f"  [GA init] Clarke-Wright: penalty={penalty}, vehicles={vehicles}, distance={distance:.2f}")
        # except Exception as e:
        #     print(f"  [GA init] Clarke-Wright failed: {e}")

        # Random chromosomes
        clients_objects = instance.clients[:]

        while len(population) < self.population_size:
            random_chrom = clients_objects[:]
            random.shuffle(random_chrom)
            population.append(random_chrom)

        return population

    # ========================================================================
    # Main loop
    # ========================================================================

    def solve(self, instance):
        start_time = time.perf_counter()

        population = self.initialize_population(instance)

        best_chromosome = None
        best_fitness_tuple = None

        print(f"  [GA] Starting evolution: pop={self.population_size}, generations={self.generations}")
        print(f"  [GA] Operators: Relocation, 2-opt, 3-opt, Or-opt, Swap, Cross")

        # Initial evaluation
        fitnesses = [self.fitness_tuple(c, instance) for c in population]

        for chrom, fit in zip(population, fitnesses):
            if best_fitness_tuple is None or self.is_better(fit, best_fitness_tuple):
                best_fitness_tuple = fit
                best_chromosome = chrom[:]

        print(
            f"  [GA] Init best: penalty={best_fitness_tuple[0]}, vehicles={best_fitness_tuple[1]}, cost={best_fitness_tuple[2]:.2f}")

        for generation in range(self.generations):
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
            print("  [GA] No valid solution found!")
            if population:
                best_chromosome = population[0]
                best_fitness_tuple = fitnesses[0]

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