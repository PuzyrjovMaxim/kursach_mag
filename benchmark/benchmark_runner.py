# benchmark/benchmark_runner_extended.py
"""
Расширенный бенчмарк раннер для сравнения с оптимальными решениями
С сохранением картинок маршрутов
"""

import time
import pandas as pd
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

from benchmark.benchmark_result import BenchmarkResult
from utils.optimal_solutions_loader import OptimalSolutionsLoader


class BenchmarkRunner:

    def __init__(self, solvers: List, results_dir: str = "benchmark_results",
                 save_routes: bool = True):
        self.solvers = solvers
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.optimal_loader = OptimalSolutionsLoader()
        self.save_routes = save_routes

    def run_instance(self, instance) -> List[BenchmarkResult]:
        """Запуск всех алгоритмов на одном инстансе"""
        results = []

        print(
            f"\n  {'Algorithm':<25} {'Distance':<12} {'Time (s)':<10} {'Vehicles':<10} {'GAP(%)':<10} {'Feasible':<10}")
        print(f"  {'-' * 25} {'-' * 12} {'-' * 10} {'-' * 10} {'-' * 10} {'-' * 10}")

        for solver in self.solvers:
            try:
                algo_name = solver.name
                solution = solver.solve(instance)

                result = BenchmarkResult.from_solution(instance.name, solution)
                result.solution = solution

                # Вычисляем GAP
                gap_info = self.optimal_loader.calculate_gap(
                    instance.name,
                    result.total_distance,
                    result.used_vehicles
                )

                gap_str = f"{gap_info['distance_gap']:.2f}%" if gap_info['distance_gap'] is not None else "N/A"

                print(f"  {algo_name:<25} {result.total_distance:<12.2f} {result.execution_time:<10.4f} "
                      f"{result.used_vehicles:<10} {gap_str:<10} {result.status:<10}")

                # Сохраняем картинку маршрута
                if self.save_routes and solution.routes:
                    self._save_route_plot(instance, solution, algo_name)

                results.append(result)

            except Exception as error:
                print(f"  {solver.name:<25} {'ERROR':<12} {'-':<10} {'-':<10} {'-':<10} {'-':<10}")
                print(f"    Error: {error}")

        return results

    def _save_route_plot(self, instance, solution, algo_name: str):
        """Сохранение картинки маршрута"""
        try:
            # Создаем папку для картинок маршрутов
            routes_dir = self.results_dir / "routes"
            routes_dir.mkdir(exist_ok=True)

            # Формируем имя файла
            filename = f"{instance.name}_{algo_name.replace(' ', '_').replace('-', '_')}.png"
            filepath = routes_dir / filename

            # Используем простую отрисовку
            self._plot_route_simple(instance, solution, str(filepath))

        except Exception as e:
            print(f"    Warning: Could not save route plot for {algo_name}: {e}")

    def _plot_route_simple(self, instance, solution, filepath):
        """Простая отрисовка маршрута"""
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 10))

        # Цвета для разных маршрутов
        colors = plt.cm.tab20.colors

        # Депо
        depot = instance.depot
        plt.plot(depot.x, depot.y, 'ks', markersize=12, label='Depot', zorder=5)

        # Клиенты
        for client in instance.clients:
            plt.plot(client.x, client.y, 'bo', markersize=6, alpha=0.7)
            plt.annotate(str(client.id), (client.x, client.y),
                         fontsize=8, ha='center', va='bottom')

        # Маршруты
        for idx, route in enumerate(solution.routes):
            if not route.clients:
                continue

            color = colors[idx % len(colors)]

            # Координаты маршрута (депо -> клиенты -> депо)
            x_coords = [depot.x] + [c.x for c in route.clients] + [depot.x]
            y_coords = [depot.y] + [c.y for c in route.clients] + [depot.y]

            plt.plot(x_coords, y_coords, 'o-', color=color, linewidth=1.5,
                     markersize=4, label=f'Vehicle {route.vehicle_id}')

        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title(f'Routes for {instance.name} - {solution.algorithm}\n'
                  f'Distance: {solution.total_distance:.2f}, Vehicles: {len(solution.routes)}')
        plt.legend(loc='upper right', fontsize=8, ncol=2)
        plt.grid(True, alpha=0.3)
        plt.axis('equal')

        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

    def run_instances_by_group(self, instances, group_name: str = None) -> List[BenchmarkResult]:
        """Запуск бенчмарка на группе инстансов"""
        all_results = []

        for idx, instance in enumerate(instances, 1):
            # Фильтрация по группе
            if group_name:
                if not instance.name.startswith(group_name):
                    continue

            print(f"\n{'=' * 70}")
            print(f"[{idx}/{len(instances)}] INSTANCE: {instance.name}")
            print(f"  Type: {instance.name[:3]}")
            print(f"  Customers: {instance.customer_count}")
            print(f"  Vehicle limit: {instance.vehicle_count}")
            print(f"  Capacity: {instance.vehicle_capacity}")

            optimal = self.optimal_loader.get_optimal(instance.name)
            if optimal:
                print(f"  Optimal: distance={optimal['distance']:.2f}, vehicles={optimal['vehicles']}")

            print(f"{'=' * 70}")

            results = self.run_instance(instance)
            all_results.extend(results)

        return all_results

    def run_all_groups(self, instances_by_group: Dict[str, List]) -> Dict[str, List[BenchmarkResult]]:
        """Запуск бенчмарка на всех группах"""
        all_group_results = {}

        for group_name, instances in instances_by_group.items():
            print(f"\n{'#' * 70}")
            print(f"# GROUP: {group_name} ({len(instances)} instances)")
            print(f"{'#' * 70}")

            results = self.run_instances_by_group(instances, group_name)
            all_group_results[group_name] = results

            # Сохраняем промежуточные результаты
            self._save_group_results(group_name, results)

        return all_group_results

    def _save_group_results(self, group_name: str, results: List[BenchmarkResult]):
        """Сохранение результатов группы в CSV"""
        data = []
        for r in results:
            gap_info = self.optimal_loader.calculate_gap(r.dataset, r.total_distance, r.used_vehicles)

            data.append({
                "instance": r.dataset,
                "algorithm": r.algorithm,
                "distance": r.total_distance,
                "vehicles": r.used_vehicles,
                "time": r.execution_time,
                "feasible": r.feasible,
                "optimal_distance": gap_info.get("optimal_distance", None),
                "optimal_vehicles": gap_info.get("optimal_vehicles", None),
                "gap_percent": gap_info.get("distance_gap", None),
                "gap_vehicles": gap_info.get("vehicles_gap", None)
            })

        df = pd.DataFrame(data)
        df.to_csv(self.results_dir / f"results_{group_name}.csv", index=False)
        print(f"  Saved: {self.results_dir / f'results_{group_name}.csv'}")

    def create_summary_table(self, all_results: List[BenchmarkResult]) -> pd.DataFrame:
        """Создание сводной таблицы по всем результатам"""
        summary = []

        # Группируем по алгоритму
        by_algorithm = defaultdict(list)
        for r in all_results:
            by_algorithm[r.algorithm].append(r)

        for algo, results in by_algorithm.items():
            # Средние показатели
            avg_distance = sum(r.total_distance for r in results) / len(results)
            avg_time = sum(r.execution_time for r in results) / len(results)
            avg_vehicles = sum(r.used_vehicles for r in results) / len(results)
            feasible_count = sum(1 for r in results if r.feasible)

            # Средний GAP
            gaps = []
            for r in results:
                gap_info = self.optimal_loader.calculate_gap(r.dataset, r.total_distance, r.used_vehicles)
                if gap_info["distance_gap"] is not None:
                    gaps.append(gap_info["distance_gap"])
            avg_gap = sum(gaps) / len(gaps) if gaps else None

            summary.append({
                "Algorithm": algo,
                "Avg Distance": f"{avg_distance:.2f}",
                "Avg Vehicles": f"{avg_vehicles:.1f}",
                "Avg Time (s)": f"{avg_time:.4f}",
                "Feasible Rate": f"{feasible_count}/{len(results)} ({100 * feasible_count / len(results):.0f}%)",
                "Avg GAP (%)": f"{avg_gap:.2f}%" if avg_gap else "N/A",
                "Best Distance": f"{min(r.total_distance for r in results):.2f}",
                "Best Vehicles": f"{min(r.used_vehicles for r in results)}"
            })

        df = pd.DataFrame(summary)
        df.to_csv(self.results_dir / "summary_all.csv", index=False)

        return df