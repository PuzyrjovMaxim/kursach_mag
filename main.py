from algorithms.greedy import GreedySolver
from algorithms.clarke_wright import ClarkeWrightSolver
from algorithms.genetic import GeneticSolver
# from algorithms.tabu_search import TabuSearchSolver
from algorithms.tabu_search_1 import TabuSearchSolver
from algorithms.immune import ImmuneSolver
from algorithms.ortools_solver import ORToolsSolver


from benchmark.benchmark_runner import BenchmarkRunner

from export.csv_exporter import CsvExporter

from stats.metrics import Metrics

from utils.dataset_loader import DatasetLoader

from visualization.benchmark_plotter import (
    BenchmarkPlotter
)

from visualization.route_plotter import (
    RoutePlotter
)


def create_solvers():
    return [
        GreedySolver(),
        ClarkeWrightSolver(),
        ImmuneSolver(),
        GeneticSolver(),
        TabuSearchSolver(),
        ORToolsSolver()
    ]


def main():
    dataset_folder = "datasets/Solomon"
    output_folder = "results"

    loader = DatasetLoader()

    INSTANCE_PREFIX1 = "С"
    INSTANCE_PREFIX2 = "R"
    INSTANCE_PREFIX3 = "RС"

    print("\nLoading datasets...")
    instances = loader.load_folder(dataset_folder, recursive=True)

    instances = [
        instance
        for instance in instances
        if instance.name in {
            "C101"
        }
    ]

    # instances = [
    #
    #     instance
    #
    #     for instance in instances
    #
    #     if instance.name.startswith(
    #         INSTANCE_PREFIX1
    #     )
    #
    # ]

    # instances = instances[:1]
    if not instances:
        print("No datasets found.")
        return

    print(f"Loaded {len(instances)} instances.")

    # Вывод названий всех загруженных инстансов
    print("\n" + "=" * 60)
    print("ЗАГРУЖЕННЫЕ ИНСТАНСЫ:")
    print("=" * 60)
    for idx, instance in enumerate(instances, 1):
        print(f"  {idx}. {instance.name}")
    print("=" * 60 + "\n")

    solvers = create_solvers()
    runner = BenchmarkRunner(solvers)

    print("\nRunning benchmark...")
    results = runner.run_instances(instances)

    print("\nBenchmark finished.")

    # Сохраняем CSV
    csv_file = f"{output_folder}/benchmark_results.csv"
    CsvExporter.export(results, csv_file)
    print(f"\nCSV exported to: {csv_file}")

    # Выводим статистику
    print("\nStatistics:")
    Metrics.print_summary(results)

    # Сохраняем графики
    print("\nBuilding charts...")
    BenchmarkPlotter.plot_summary(results, f"{output_folder}/plots")
    print("Charts saved.")

    # ===== ВАЖНО: Используем результаты из бенчмарка, а не запускаем заново =====
    if instances and results:
        instance = instances[0]

        # Находим лучшее решение для этого инстанса из результатов бенчмарка
        best_solution_for_instance = None
        best_algorithm = None
        best_cost = float('inf')

        for result in results:
            if result.dataset == instance.name:
                # Нужно получить само решение (Solution объект)
                # Но в BenchmarkResult нет ссылки на Solution!
                # Поэтому нужно изменить BenchmarkRunner, чтобы он сохранял решения
                pass

        print(f"\n⚠️ Route plots пропущены - нужно сохранять решения в BenchmarkResult")
        print(f"   Лучший результат для {instance.name}: cost={best_cost if best_cost != float('inf') else 'N/A'}")

    print("\nFinished.")

    # В конце main.py, после получения результатов:

    # ===== Визуализация маршрутов из сохраненных результатов =====
    if instances and results:
        instance = instances[0]

        # Находим результаты для этого инстанса
        instance_results = [r for r in results if r.dataset == instance.name]

        if instance_results:
            print(f"\nCreating route plots for {instance.name}")

            for result in instance_results:
                if result.solution:
                    try:
                        RoutePlotter.save(
                            instance,
                            result.solution,
                            f"{output_folder}/routes/{instance.name}_{result.algorithm}.png"
                        )
                        print(f"  ✓ Saved route plot for {result.algorithm}")
                    except Exception as error:
                        print(f"  ✗ Failed route plot for {result.algorithm}: {error}")
                else:
                    print(f"  ✗ No solution object for {result.algorithm}")


if __name__ == "__main__":
    main()