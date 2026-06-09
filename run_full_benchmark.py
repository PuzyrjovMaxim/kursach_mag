# run_full_benchmark.py
"""
Полный бенчмарк для всех типов инстансов Solomon
Сравнение с оптимальными решениями с сайта SINTEF
Сохранение картинок маршрутов для каждого решения

Использование:
    python run_full_benchmark.py                              # Запуск всех инстансов
    python run_full_benchmark.py --groups C1 R1               # Только C1 и R1
    python run_full_benchmark.py --group C1                   # Только C1
    python run_full_benchmark.py --instance C101              # Только C101
    python run_full_benchmark.py --instances C101 C102 R103   # Несколько инстансов
    python run_full_benchmark.py --exclude R2 RC2             # Исключить группы
    python run_full_benchmark.py --save-routes                # Сохранять картинки маршрутов
    python run_full_benchmark.py --list-groups                # Список групп
    python run_full_benchmark.py --list-instances             # Список всех инстансов
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from utils.dataset_loader import DatasetLoader
from utils.optimal_solutions_loader import OptimalSolutionsLoader
from benchmark.benchmark_runner import BenchmarkRunner
from visualization.benchmark_plotter import BenchmarkPlotter

# Импорт алгоритмов
from algorithms.greedy import GreedySolver
from algorithms.clarke_wright import ClarkeWrightSolver
from algorithms.genetic import GeneticSolver
from algorithms.immune import ImmuneSolver
from algorithms.tabu_search import TabuSearchSolver


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Run VRPTW benchmark on Solomon instances',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_full_benchmark.py                              # Run all instances
  python run_full_benchmark.py --groups C1 R1               # Run only C1 and R1 groups
  python run_full_benchmark.py --group C1                   # Run only C1 group
  python run_full_benchmark.py --instance C101              # Run only C101
  python run_full_benchmark.py --instances C101 C102 R103   # Run specific instances
  python run_full_benchmark.py --exclude R2 RC2             # Exclude R2 and RC2 groups
  python run_full_benchmark.py --save-routes                # Save route plots
  python run_full_benchmark.py --group C1 --save-routes     # Save routes for C1
  python run_full_benchmark.py --list-groups                # List available groups
  python run_full_benchmark.py --list-instances             # List all available instances
        """
    )

    parser.add_argument(
        '--groups', '-g',
        nargs='+',
        choices=['C1', 'C2', 'R1', 'R2', 'RC1', 'RC2'],
        help='Run only specified groups (e.g., --groups C1 R1)'
    )

    parser.add_argument(
        '--group',
        help='Run only one group (e.g., --group C1)'
    )

    parser.add_argument(
        '--instances', '-i',
        nargs='+',
        help='Run only specified instances (e.g., --instances C101 C102)'
    )

    parser.add_argument(
        '--instance',
        help='Run only one instance (e.g., --instance C101)'
    )

    parser.add_argument(
        '--exclude',
        nargs='+',
        choices=['C1', 'C2', 'R1', 'R2', 'RC1', 'RC2'],
        help='Exclude specified groups (e.g., --exclude R2 RC2)'
    )

    parser.add_argument(
        '--list-groups',
        action='store_true',
        help='List available instance groups and exit'
    )

    parser.add_argument(
        '--list-instances',
        action='store_true',
        help='List all available instances and exit'
    )

    parser.add_argument(
        '--save-routes',
        action='store_true',
        help='Save route plots for each solution'
    )

    parser.add_argument(
        '--no-save-routes',
        action='store_true',
        help='Disable saving route plots (overrides --save-routes)'
    )

    parser.add_argument(
        '--output-dir',
        default='benchmark_results',
        help='Output directory for results (default: benchmark_results)'
    )

    return parser.parse_args()


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


def filter_instances_by_groups(instances, include_groups=None, exclude_groups=None):
    """Фильтрация инстансов по группам"""
    if not include_groups and not exclude_groups:
        return instances

    groups = group_instances_by_type(instances)

    # Определяем какие группы оставить
    if include_groups:
        selected_groups = set(include_groups)
    else:
        selected_groups = set(groups.keys())

    if exclude_groups:
        selected_groups = selected_groups - set(exclude_groups)

    # Собираем инстансы из выбранных групп
    filtered = []
    for group in selected_groups:
        filtered.extend(groups.get(group, []))

    return filtered


def filter_instances_by_names(instances, instance_names):
    """Фильтрация инстансов по именам"""
    instance_names_set = set(name.upper() for name in instance_names)
    return [inst for inst in instances if inst.name.upper() in instance_names_set]


def list_available_groups(instances):
    """Вывод списка доступных групп"""
    groups = group_instances_by_type(instances)

    print("\n" + "=" * 60)
    print("AVAILABLE INSTANCE GROUPS")
    print("=" * 60)

    for group_name, group_instances in sorted(groups.items()):
        instance_names = [inst.name for inst in group_instances]
        print(f"\n{group_name}:")
        print(f"  Count: {len(group_instances)}")
        print(f"  Instances: {', '.join(instance_names)}")

    print("=" * 60)


def list_all_instances(instances):
    """Вывод списка всех доступных инстансов"""
    print("\n" + "=" * 60)
    print("AVAILABLE INSTANCES")
    print("=" * 60)

    # Группируем для удобства
    groups = group_instances_by_type(instances)

    for group_name, group_instances in sorted(groups.items()):
        print(f"\n{group_name} ({len(group_instances)}):")
        for inst in sorted(group_instances, key=lambda x: x.name):
            print(f"  {inst.name}")

    print("=" * 60)


def get_solvers():
    """Создание списка солверов"""
    return [
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
        TabuSearchSolver(
            ax_iterations=1000,
            neighborhood_size=100,
            tabu_tenure=50
        ),
    ]


def print_configuration(instances, groups_to_run, instance_names, save_routes, output_dir):
    """Вывод конфигурации запуска"""
    print("\n" + "=" * 80)
    print("BENCHMARK CONFIGURATION")
    print("=" * 80)

    if instance_names:
        print(f"Filter by instance names: {', '.join(instance_names)}")
    elif groups_to_run:
        print(f"Filter by groups: {', '.join(groups_to_run)}")
    else:
        print("Running all instances")

    print(f"Total instances to run: {len(instances)}")
    print(f"Save route plots: {'YES' if save_routes else 'NO'}")
    print(f"Output directory: {output_dir}/")
    print("=" * 80)


def main():
    args = parse_arguments()

    # Определяем нужно ли сохранять маршруты
    if args.no_save_routes:
        save_routes = False
    else:
        save_routes = args.save_routes

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

    # Сортируем по имени
    instances.sort(key=lambda x: x.name)

    # Если нужно только показать группы или инстансы
    if args.list_groups:
        list_available_groups(instances)
        return

    if args.list_instances:
        list_all_instances(instances)
        return

    # ========================================================================
    # 2. Фильтрация инстансов
    # ========================================================================

    # Фильтрация по конкретным инстансам
    instance_names = []
    if args.instance:
        instance_names = [args.instance]
    elif args.instances:
        instance_names = args.instances

    if instance_names:
        instances = filter_instances_by_names(instances, instance_names)

    # Фильтрация по группам
    groups_to_run = []
    if args.group:
        groups_to_run = [args.group]
    elif args.groups:
        groups_to_run = args.groups

    if groups_to_run or args.exclude:
        instances = filter_instances_by_groups(instances, groups_to_run, args.exclude)

    if not instances:
        print("\n  No instances match the specified filters!")
        print("  Use --list-instances to see available instances")
        print("  Use --list-groups to see available groups")
        return

    # Группируем отфильтрованные инстансы
    groups = group_instances_by_type(instances)

    print_configuration(instances, groups_to_run, instance_names, save_routes, args.output_dir)

    print(f"\n  Total instances loaded: {len(instances)}")
    for group_name, group_instances in groups.items():
        print(f"    {group_name}: {len(group_instances)} instances")

    # ========================================================================
    # 3. Создание солверов
    # ========================================================================
    print("\n[2] Initializing solvers...")
    solvers = get_solvers()

    print(f"  Solvers: {[s.name for s in solvers]}")

    # ========================================================================
    # 4. Запуск бенчмарка
    # ========================================================================
    print("\n[3] Running benchmark...")
    runner = BenchmarkRunner(solvers, results_dir=args.output_dir, save_routes=save_routes)
    all_results = runner.run_all_groups(groups)

    # ========================================================================
    # 5. Создание сводной таблицы
    # ========================================================================
    print("\n[4] Creating summary...")

    # Объединяем все результаты
    combined_results = []
    for group_results in all_results.values():
        combined_results.extend(group_results)

    if combined_results:
        summary_df = runner.create_summary_table(combined_results)
        print("\nSummary Table:")
        print(summary_df.to_string(index=False))

        # ========================================================================
        # 6. Построение графиков
        # ========================================================================
        print("\n[5] Generating plots...")
        plotter = BenchmarkPlotter(output_dir=f"{args.output_dir}/plots")

        # График сравнения алгоритмов по GAP
        print("  - Plotting GAP comparison...")
        plotter.plot_gap_comparison(combined_results)

        # Графики по группам
        for group_name, group_results in all_results.items():
            if group_results:
                print(f"  - Plotting group {group_name}...")
                plotter.plot_group_comparison(group_results, group_name)
                plotter.plot_convergence_by_group(group_results, group_name)

        # График сравнения количества машин
        print("  - Plotting vehicles comparison...")
        plotter.plot_vehicles_comparison(combined_results)

        # Тепловая карта GAP по всем инстансам
        print("  - Plotting GAP heatmap...")
        plotter.plot_gap_heatmap(all_results)

        # Радарная диаграмма
        print("  - Plotting radar chart...")
        plotter.create_radar_chart(combined_results)

        # ========================================================================
        # 7. Вывод статистики
        # ========================================================================
        print("\n[6] Statistics by group:")
        print("=" * 70)

        for group_name, group_results in all_results.items():
            if not group_results:
                continue

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

        # ========================================================================
        # 8. Финальная информация о сохраненных файлах
        # ========================================================================
        print("\n" + "=" * 80)
        print("BENCHMARK COMPLETED!")
        print("=" * 80)
        print(f"\nResults saved in: {args.output_dir}/")
        print(f"  - CSV files: {args.output_dir}/results_*.csv")
        print(f"  - Summary: {args.output_dir}/summary_all.csv")

        if save_routes:
            print(f"  - Route plots: {args.output_dir}/routes/")

        print(f"  - Performance plots: {args.output_dir}/plots/")

        print("\nFiles generated:")
        print(f"  {args.output_dir}/summary_all.csv - Overall summary table")

        for group_name in all_results.keys():
            print(f"  {args.output_dir}/results_{group_name}.csv - {group_name} group results")

        print(f"\n  {args.output_dir}/plots/gap_comparison.png - GAP comparison chart")
        print(f"  {args.output_dir}/plots/vehicles_comparison.png - Vehicles comparison")
        print(f"  {args.output_dir}/plots/gap_heatmap.png - GAP heatmap by instance")
        print(f"  {args.output_dir}/plots/radar_chart_comparison.png - Multi-criteria radar chart")

        for group_name in all_results.keys():
            print(f"  {args.output_dir}/plots/group_{group_name}_comparison.png - {group_name} group charts")

        if save_routes:
            print(f"\n  {args.output_dir}/routes/ - Route visualization images")

        print("=" * 80)

    else:
        print("\n  No valid results to summarize!")

    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)


if __name__ == "__main__":
    main()