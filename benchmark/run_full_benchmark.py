# run_full_benchmark.py
"""
Полный бенчмарк для всех типов инстансов Solomon
Сравнение с оптимальными решениями с сайта SINTEF
"""

import sys
from pathlib import Path
from collections import defaultdict

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from utils.dataset_loader import DatasetLoader
from benchmark.benchmark_runner import BenchmarkRunner
from visualization.benchmark_plotter import BenchmarkPlotter

# Импорт алгоритмов
from algorithms.greedy import GreedySolver
from algorithms.clarke_wright import ClarkeWrightSolver
from algorithms.genetic import GeneticSolver
from algorithms.immune import ImmuneSolver


def group_instances_by_type(instances):
    """Группировка инстансов по типу (C1, C2, R1, R2, RC1, RC2)"""
    groups = defaultdict(list)

    for inst in instances:
        name = inst.name.upper()

        if name.startswith("C10"):
            groups["C1"].append(inst)
        elif name.startswith("C20"):
            groups["C2"].append(inst)
        elif name.startswith("R10"):
            groups["R1"].append(inst)
        elif name.startswith("R20"):
            groups["R2"].append(inst)
        elif name.startswith("RC10"):
            groups["RC1"].append(inst)
        elif name.startswith("RC20"):
            groups["RC2"].append(inst)

    return groups


def main():
    print("=" * 80)
    print("FULL BENCHMARK - VRPTW SOLOMON INSTANCES")
    print("Comparing with optimal solutions from SINTEF")
    print("=" * 80)

    # ========================================================================
    # 1. Загрузка всех инстансов
    # ========================================================================
    print("\n[1] Loading instances...")
    loader = DatasetLoader()

    # Загружаем все инстансы из папки Solomon
    instances = loader.load_folder("datasets/Solomon", recursive=False)

    if not instances:
        print("  No instances found in datasets/Solomon/")
        print("  Please ensure the Solomon dataset files are present.")
        return

    # Группируем по типам
    groups = group_instances_by_type(instances)

    print(f"  Total instances loaded: {len(instances)}")
    for group_name, group_instances in groups.items():
        print(f"    {group_name}: {len(group_instances)} instances")

    # ========================================================================
    # 2. Создание солверов
    # ========================================================================
    print("\n[2] Initializing solvers...")
    solvers = [
        GreedySolver(),
        ClarkeWrightSolver(),
        GeneticSolver(
            population_size=100,
            generations=100,
            elite_fraction=0.1,
            crossover_rate=0.9,
            mutation_rate=0.3
        ),
        ImmuneSolver(
            population_size=100,
            generations=100
        ),
    ]

    print(f"  Solvers: {[s.name for s in solvers]}")

    # ========================================================================
    # 3. Запуск бенчмарка
    # ========================================================================
    print("\n[3] Running benchmark...")
    runner = BenchmarkRunner(solvers, results_dir="benchmark_results")
    all_results = runner.run_all_groups(groups)

    # ========================================================================
    # 4. Создание сводной таблицы
    # ========================================================================
    print("\n[4] Creating summary...")

    # Объединяем все результаты
    combined_results = []
    for group_results in all_results.values():
        combined_results.extend(group_results)

    summary_df = runner.create_summary_table(combined_results)
    print("\nSummary Table:")
    print(summary_df.to_string(index=False))

    # ========================================================================
    # 5. Построение графиков
    # ========================================================================
    print("\n[5] Generating plots...")
    plotter = BenchmarkPlotter(output_dir="benchmark_results/plots")

    # График сравнения алгоритмов по GAP
    plotter.plot_gap_comparison(combined_results)

    # Графики по группам
    for group_name, group_results in all_results.items():
        plotter.plot_group_comparison(group_results, group_name)
        plotter.plot_convergence_by_group(group_results, group_name)

    # График сравнения количества машин
    plotter.plot_vehicles_comparison(combined_results)

    # Тепловая карта GAP по всем инстансам
    plotter.plot_gap_heatmap(all_results)

    # ========================================================================
    # 6. Вывод статистики
    # ========================================================================
    print("\n[6] Statistics by group:")
    print("=" * 70)

    for group_name, group_results in all_results.items():
        print(f"\n{group_name}:")

        # По алгоритмам
        by_algo = defaultdict(list)
        for r in group_results:
            by_algo[r.algorithm].append(r)

        for algo, results in by_algo.items():
            avg_gap = 0
            gap_count = 0
            for r in results:
                gap_info = OptimalSolutionsLoader.calculate_gap(
                    r.dataset, r.total_distance, r.used_vehicles
                )
                if gap_info["distance_gap"] is not None:
                    avg_gap += gap_info["distance_gap"]
                    gap_count += 1

            avg_gap = avg_gap / gap_count if gap_count > 0 else 0
            avg_distance = sum(r.total_distance for r in results) / len(results)
            avg_vehicles = sum(r.used_vehicles for r in results) / len(results)

            print(f"  {algo:<20}: Avg Dist={avg_distance:.2f}, "
                  f"Avg Veh={avg_vehicles:.1f}, Avg GAP={avg_gap:.2f}%")

    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETED!")
    print(f"Results saved in: benchmark_results/")
    print("=" * 80)


if __name__ == "__main__":
    main()