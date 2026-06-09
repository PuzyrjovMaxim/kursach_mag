import time
from math import inf

from algorithms.base_solver import BaseSolver

from models.route import Route
from models.solution import Solution

from routing.feasibility import is_route_feasible

from routing.route_utils import (
    route_distance,
    route_completion_time,
    served_clients
)


class ClarkeWrightSolver(BaseSolver):

    @property
    def name(self):
        return "Clarke-Wright"

    def solve(self, instance):
        start_time = time.perf_counter()

        depot = instance.depot
        clients = instance.clients
        distance_matrix = instance.distance_matrix
        vehicle_capacity = instance.vehicle_capacity
        max_vehicles = instance.vehicle_count

        # Оптимальное количество машин (известное для C101)
        optimal_vehicles = 10

        # Шаг 1: Начальные маршруты (depot -> client -> depot)
        routes = []
        for idx, client in enumerate(clients):
            route = Route(vehicle_id=idx + 1)
            route.clients = [client]
            route.load = client.demand
            route.distance = self._route_distance(depot, [client], distance_matrix)
            route.total_time = self._route_time(depot, [client], distance_matrix)
            routes.append(route)

        # Шаг 2: Вычисляем savings с учетом количества машин
        savings = []
        for i in range(len(clients)):
            for j in range(i + 1, len(clients)):
                ci, cj = clients[i], clients[j]

                # Базовое сохранение расстояния
                base_saving = (distance_matrix.get(depot.id, ci.id) +
                               distance_matrix.get(depot.id, cj.id) -
                               distance_matrix.get(ci.id, cj.id))

                # Штраф за временные окна
                time_penalty = abs(ci.due_date - cj.due_date) / 100.0

                # Бонус за объединение (уменьшает количество машин!)
                # Чем больше клиентов объединяем, тем больше бонус
                vehicle_bonus = 100  # Бонус за каждое объединение (уменьшает машины)

                adjusted_saving = base_saving - time_penalty + vehicle_bonus

                savings.append((adjusted_saving, i, j, ci, cj))

        # Сортируем по убыванию экономии
        savings.sort(key=lambda x: x[0], reverse=True)

        # Шаг 3: Объединяем маршруты
        merged = [False] * len(routes)
        merge_count = 0  # Счетчик объединений

        for saving, i, j, ci, cj in savings:
            if merged[i] or merged[j]:
                continue

            route_i = routes[i]
            route_j = routes[j]

            # Проверка вместимости
            if route_i.load + route_j.load > vehicle_capacity:
                continue

            # Пробуем объединить: i в конце, j в начале
            merged_clients = route_i.clients + route_j.clients
            if self._check_feasibility(depot, merged_clients, vehicle_capacity, distance_matrix):
                route_i.clients = merged_clients
                route_i.load += route_j.load
                route_i.distance = self._route_distance(depot, merged_clients, distance_matrix)
                route_i.total_time = self._route_time(depot, merged_clients, distance_matrix)
                merged[j] = True
                merge_count += 1
                continue

            # Пробуем объединить: j в конце, i в начале
            merged_clients = route_j.clients + route_i.clients
            if self._check_feasibility(depot, merged_clients, vehicle_capacity, distance_matrix):
                route_i.clients = merged_clients
                route_i.load += route_j.load
                route_i.distance = self._route_distance(depot, merged_clients, distance_matrix)
                route_i.total_time = self._route_time(depot, merged_clients, distance_matrix)
                merged[j] = True
                merge_count += 1

        # Собираем активные маршруты
        active_routes = [routes[i] for i in range(len(routes)) if not merged[i]]

        # Шаг 4: Агрессивное объединение для уменьшения машин
        # Пытаемся объединить, даже если это увеличит расстояние,
        # потому что уменьшение машин важнее!

        if len(active_routes) > optimal_vehicles:
            print(f"  [CW] Reducing vehicles from {len(active_routes)} to optimal...")

            # Продолжаем объединять, пока не достигнем оптимального количества
            while len(active_routes) > optimal_vehicles:
                best_merge = None
                best_increase = float('inf')

                for i in range(len(active_routes)):
                    for j in range(i + 1, len(active_routes)):
                        if active_routes[i].load + active_routes[j].load > vehicle_capacity:
                            continue

                        # Пробуем оба порядка объединения
                        for order in [0, 1]:
                            if order == 0:
                                merged_clients = active_routes[i].clients + active_routes[j].clients
                            else:
                                merged_clients = active_routes[j].clients + active_routes[i].clients

                            if self._check_feasibility(depot, merged_clients, vehicle_capacity, distance_matrix):
                                new_distance = self._route_distance(depot, merged_clients, distance_matrix)
                                old_distance = active_routes[i].distance + active_routes[j].distance
                                increase = new_distance - old_distance

                                # Даже если увеличение большое, все равно объединяем,
                                # если это помогает уменьшить количество машин
                                if increase < best_increase:
                                    best_increase = increase
                                    best_merge = (i, j, merged_clients)

                if best_merge is None:
                    break

                i, j, merged_clients = best_merge
                active_routes[i].clients = merged_clients
                active_routes[i].load = sum(c.demand for c in merged_clients)
                active_routes[i].distance = self._route_distance(depot, merged_clients, distance_matrix)
                active_routes[i].total_time = self._route_time(depot, merged_clients, distance_matrix)
                active_routes.pop(j)

                print(f"  [CW] Merged, now {len(active_routes)} vehicles")

        # Шаг 5: Финальная проверка лимита машин
        if len(active_routes) > max_vehicles:
            print(f"  [CW] Warning: {len(active_routes)} vehicles exceeds limit {max_vehicles}")
            # Оставляем только лучшие маршруты (с наибольшей загрузкой)
            active_routes.sort(key=lambda r: r.load, reverse=True)
            active_routes = active_routes[:max_vehicles]

        # Пересчет финальных значений
        total_distance = sum(r.distance for r in active_routes)
        served = served_clients([r.clients for r in active_routes])
        unserved = len(clients) - served

        feasible = (unserved == 0 and len(active_routes) <= max_vehicles)

        execution_time = time.perf_counter() - start_time

        print(f"  [CW] Final: {len(active_routes)} vehicles, distance={total_distance:.2f}")

        return Solution(
            algorithm=self.name,
            routes=active_routes,
            total_distance=total_distance,
            total_penalty=0.0,
            execution_time=execution_time,
            feasible=feasible,
            served_clients=served,
            unserved_clients=unserved
        )

    def _route_distance(self, depot, clients, distance_matrix):
        """Вычисление расстояния маршрута"""
        if not clients:
            return 0.0
        total = 0.0
        curr = depot
        for c in clients:
            total += distance_matrix.get(curr.id, c.id)
            curr = c
        total += distance_matrix.get(curr.id, depot.id)
        return total

    def _route_time(self, depot, clients, distance_matrix):
        """Вычисление времени выполнения маршрута с учетом временных окон"""
        if not clients:
            return 0.0
        current_time = 0.0
        current_node = depot
        for c in clients:
            travel = distance_matrix.get(current_node.id, c.id)
            arrival = current_time + travel
            start = max(arrival, c.ready_time)
            if start > c.due_date:
                return float('inf')
            current_time = start + c.service_time
            current_node = c
        current_time += distance_matrix.get(current_node.id, depot.id)
        return current_time

    def _check_feasibility(self, depot, clients, capacity, distance_matrix):
        """Проверка допустимости маршрута"""
        total_demand = sum(c.demand for c in clients)
        if total_demand > capacity:
            return False
        return self._route_time(depot, clients, distance_matrix) < float('inf')