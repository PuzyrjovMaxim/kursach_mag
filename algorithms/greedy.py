import time
from math import inf

from algorithms.base_solver import BaseSolver

from models.route import Route
from models.solution import Solution

from routing.route_utils import (
    route_distance,
    served_clients,
    route_completion_time
)


class GreedySolver(BaseSolver):

    @property
    def name(self):
        return "Greedy"

    def solve(self, instance):
        """
        Улучшенный жадный алгоритм для CVRPTW.

        Стратегия:
        1. Сортируем клиентов по due_date (ранние окна раньше)
        2. Для каждого клиента пытаемся вставить в существующий маршрут
        3. Если не вставляется - создаем новый маршрут
        """
        start_time = time.perf_counter()

        depot = instance.depot
        capacity = instance.vehicle_capacity
        distance_matrix = instance.distance_matrix

        # Сортируем клиентов по due_date (Earliest Due Date rule)
        # Это стандартная эвристика для задач с временными окнами
        unvisited = sorted(
            instance.clients,
            key=lambda c: (c.due_date, c.ready_time)
        )

        routes = []

        for client in unvisited:
            best_route_idx = -1
            best_cost = inf
            best_position = -1

            # Пробуем вставить клиента в существующие маршруты
            for route_idx, route in enumerate(routes):
                # Пробуем вставить на все возможные позиции
                for pos in range(len(route.clients) + 1):
                    # Создаем временный маршрут с вставкой
                    temp_clients = route.clients[:]
                    temp_clients.insert(pos, client)

                    # Проверка вместимости
                    total_demand = sum(c.demand for c in temp_clients)
                    if total_demand > capacity:
                        continue

                    # Проверка временных окон
                    if self._check_time_feasibility(depot, temp_clients, distance_matrix):
                        # Считаем прирост расстояния
                        new_distance = self._calculate_route_distance(depot, temp_clients, distance_matrix)
                        old_distance = route.distance if route.distance > 0 else self._calculate_route_distance(depot,
                                                                                                                route.clients,
                                                                                                                distance_matrix)
                        cost_increase = new_distance - old_distance

                        if cost_increase < best_cost:
                            best_cost = cost_increase
                            best_route_idx = route_idx
                            best_position = pos

            if best_route_idx >= 0:
                # Вставляем в существующий маршрут
                route = routes[best_route_idx]
                route.clients.insert(best_position, client)
                route.load += client.demand
                route.distance = self._calculate_route_distance(depot, route.clients, distance_matrix)
                route.total_time = route_completion_time(depot, route.clients, distance_matrix)
            else:
                # Создаем новый маршрут
                new_route = Route(vehicle_id=len(routes) + 1)
                new_route.clients = [client]
                new_route.load = client.demand
                new_route.distance = self._calculate_route_distance(depot, [client], distance_matrix)
                new_route.total_time = route_completion_time(depot, [client], distance_matrix)
                routes.append(new_route)

        # Подсчет результатов
        total_distance = sum(route.distance for route in routes)
        served = served_clients([route.clients for route in routes])
        unserved = len(instance.clients) - served

        # Проверка лимита машин (если превышает, значит решение невалидное)
        feasible = (len(routes) <= instance.vehicle_count and unserved == 0)

        execution_time = time.perf_counter() - start_time

        return Solution(
            algorithm=self.name,
            routes=routes,
            total_distance=total_distance,
            total_penalty=0.0,
            execution_time=execution_time,
            feasible=feasible,
            served_clients=served,
            unserved_clients=unserved
        )

    def _check_time_feasibility(self, depot, clients, distance_matrix):
        """
        Проверка временных окон для маршрута
        """
        current_time = 0.0
        current_node = depot

        for client in clients:
            travel = distance_matrix.get(current_node.id, client.id)
            arrival = current_time + travel

            # Время начала обслуживания
            service_start = max(arrival, client.ready_time)

            # Проверка опоздания
            if service_start > client.due_date:
                return False

            # Время убытия
            current_time = service_start + client.service_time
            current_node = client

        # Проверка возврата в депо
        return_time = current_time + distance_matrix.get(current_node.id, depot.id)
        return return_time <= depot.due_date

    def _calculate_route_distance(self, depot, clients, distance_matrix):
        """
        Вычисление полной длины маршрута
        """
        if not clients:
            return 0.0

        total = 0.0
        current = depot

        for client in clients:
            total += distance_matrix.get(current.id, client.id)
            current = client

        total += distance_matrix.get(current.id, depot.id)
        return total