from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

import matplotlib.pyplot as plt


class BenchmarkPlotter:

    @staticmethod
    def _save_or_show(
        save_path=None,
        show=True
    ):

        plt.tight_layout()

        if save_path:

            save_path = Path(
                save_path
            )

            save_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            plt.savefig(
                save_path,
                dpi=300,
                bbox_inches="tight"
            )

        if show:

            plt.show()

        plt.close()

    @staticmethod
    def plot_distance(
        results,
        save_path=None,
        show=True
    ):

        algorithms = [
            result.algorithm
            for result in results
        ]

        distances = [
            result.total_distance
            for result in results
        ]

        plt.figure(
            figsize=(10, 6)
        )

        plt.bar(
            algorithms,
            distances
        )

        plt.title(
            "Total Distance"
        )

        plt.ylabel(
            "Distance"
        )

        plt.xticks(
            rotation=30
        )

        BenchmarkPlotter._save_or_show(
            save_path,
            show
        )

    @staticmethod
    def plot_execution_time(
        results,
        save_path=None,
        show=True
    ):

        algorithms = [
            result.algorithm
            for result in results
        ]

        times = [
            result.execution_time
            for result in results
        ]

        plt.figure(
            figsize=(10, 6)
        )

        plt.bar(
            algorithms,
            times
        )

        plt.title(
            "Execution Time"
        )

        plt.ylabel(
            "Seconds"
        )

        plt.xticks(
            rotation=30
        )

        BenchmarkPlotter._save_or_show(
            save_path,
            show
        )

    @staticmethod
    def plot_cost(
        results,
        save_path=None,
        show=True
    ):

        algorithms = [
            result.algorithm
            for result in results
        ]

        costs = [
            result.total_cost
            for result in results
        ]

        plt.figure(
            figsize=(10, 6)
        )

        plt.bar(
            algorithms,
            costs
        )

        plt.title(
            "Total Cost"
        )

        plt.ylabel(
            "Cost"
        )

        plt.xticks(
            rotation=30
        )

        BenchmarkPlotter._save_or_show(
            save_path,
            show
        )

    @staticmethod
    def plot_vehicle_usage(
        results,
        save_path=None,
        show=True
    ):

        algorithms = [
            result.algorithm
            for result in results
        ]

        vehicles = [
            result.used_vehicles
            for result in results
        ]

        plt.figure(
            figsize=(10, 6)
        )

        plt.bar(
            algorithms,
            vehicles
        )

        plt.title(
            "Used Vehicles"
        )

        plt.ylabel(
            "Vehicles"
        )

        plt.xticks(
            rotation=30
        )

        BenchmarkPlotter._save_or_show(
            save_path,
            show
        )

    @staticmethod
    def plot_gap_to_reference(
        results,
        reference_algorithm="OR-Tools",
        save_path=None,
        show=True
    ):

        reference = None

        for result in results:

            if (
                result.algorithm
                ==
                reference_algorithm
            ):

                reference = (
                    result.total_cost
                )

                break

        if reference is None:

            raise ValueError(
                f"{reference_algorithm} "
                f"result not found"
            )

        algorithms = []
        gaps = []

        for result in results:

            if (
                result.algorithm
                ==
                reference_algorithm
            ):

                continue

            gap = (
                (
                    result.total_cost
                    -
                    reference
                )
                /
                reference
            ) * 100

            algorithms.append(
                result.algorithm
            )

            gaps.append(
                gap
            )

        plt.figure(
            figsize=(10, 6)
        )

        plt.bar(
            algorithms,
            gaps
        )

        plt.title(
            f"Gap to {reference_algorithm}"
        )

        plt.ylabel(
            "Gap (%)"
        )

        plt.xticks(
            rotation=30
        )

        BenchmarkPlotter._save_or_show(
            save_path,
            show
        )

    @staticmethod
    def plot_summary(
        results,
        output_folder
    ):

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        BenchmarkPlotter.plot_distance(
            results,
            output_folder /
            "distance.png",
            False
        )

        BenchmarkPlotter.plot_execution_time(
            results,
            output_folder /
            "execution_time.png",
            False
        )

        BenchmarkPlotter.plot_cost(
            results,
            output_folder /
            "cost.png",
            False
        )

        BenchmarkPlotter.plot_vehicle_usage(
            results,
            output_folder /
            "vehicles.png",
            False
        )

    @staticmethod
    def plot_boxplot_comparison(
            results_list,  # Список списков результатов или словарь {algorithm: [results]}
            metric='total_cost',
            metric_name='Cost',
            save_path=None,
            show=True
    ):
        """
        Ящик с усами для сравнения распределений алгоритмов
        results_list: dict {'Genetic': [result1, result2, ...], 'SA': [...]}
        """
        plt.figure(figsize=(12, 7))

        # Если передан словарь
        if isinstance(results_list, dict):
            algorithms = list(results_list.keys())
            data = []
            for algo in algorithms:
                algo_data = [getattr(r, metric) for r in results_list[algo]]
                data.append(algo_data)
        else:
            # Группируем результаты по алгоритмам
            groups = defaultdict(list)
            for result in results_list:
                groups[result.algorithm].append(getattr(result, metric))
            algorithms = list(groups.keys())
            data = list(groups.values())

            # Создаем boxplot
        bp = plt.boxplot(data, labels=algorithms, patch_artist=True,
                         showmeans=True, meanline=True)

        # Раскрашиваем
        colors = plt.cm.Set3(np.linspace(0, 1, len(algorithms)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Настройки
        plt.title(f'Distribution of {metric_name}', fontsize=14, fontweight='bold')
        plt.ylabel(metric_name, fontsize=12)
        plt.xlabel('Algorithm', fontsize=12)
        plt.xticks(rotation=30)
        plt.grid(True, alpha=0.3, axis='y')

        # Легенда
        mean_line = Line2D([0], [0], color='red', linewidth=2, label='Mean')
        median_line = Line2D([0], [0], color='orange', linewidth=2, label='Median')
        plt.legend(handles=[mean_line, median_line], loc='upper right')

        BenchmarkPlotter._save_or_show(save_path, show)

    @staticmethod
    def plot_convergence(
            histories,  # dict {'Genetic': [1200, 1150, ...], 'SA': [1250, ...]}
            save_path=None,
            show=True
    ):
        """
        График сходимости алгоритмов
        histories: словарь имя_алгоритма -> список лучших значений по итерациям
        """
        plt.figure(figsize=(12, 7))

        colors = plt.cm.Set2(np.linspace(0, 1, len(histories)))

        for idx, (algo_name, history) in enumerate(histories.items()):
            generations = range(1, len(history) + 1)
            plt.plot(generations, history,
                     label=algo_name,
                     linewidth=2,
                     color=colors[idx],
                     marker='o',
                     markersize=3,
                     markevery=max(1, len(history) // 20))  # Маркеры каждые 5% точек

        plt.xlabel('Iteration / Generation', fontsize=12)
        plt.ylabel('Best Cost', fontsize=12)
        plt.title('Convergence Comparison of Algorithms', fontsize=14, fontweight='bold')
        plt.legend(loc='upper right', fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--')

        # Добавляем аннотации финальных значений
        for algo_name, history in histories.items():
            final_val = history[-1]
            plt.annotate(f'{algo_name}: {final_val:.0f}',
                         xy=(len(history), final_val),
                         xytext=(len(history) * 0.85, final_val),
                         fontsize=8,
                         alpha=0.7,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        BenchmarkPlotter._save_or_show(save_path, show)

    @staticmethod
    def plot_radar_chart(
            algorithm_summary,  # из Metrics.algorithm_summary()
            save_path=None,
            show=True
    ):
        """
        Радарная диаграмма для многокритериального сравнения
        algorithm_summary: {algo: {'average_cost': ..., 'average_time': ..., 'average_vehicles': ...}}
        """
        algorithms = list(algorithm_summary.keys())

        # Метрики для сравнения
        metrics = ['average_cost', 'average_time', 'average_vehicles', 'average_coverage']
        metric_labels = ['Cost', 'Time (sec)', 'Vehicles', 'Coverage']

        # Нормализация (Min-Max scaling)
        normalized_data = {}
        for metric in metrics:
            values = [algorithm_summary[algo][metric] for algo in algorithms]
            min_val, max_val = min(values), max(values)

            if max_val - min_val > 1e-6:
                # Инвертируем для cost, time, vehicles (чем меньше - тем лучше)
                if metric in ['average_cost', 'average_time', 'average_vehicles']:
                    normalized = [1 - (v - min_val) / (max_val - min_val) for v in values]
                else:  # coverage - чем больше тем лучше
                    normalized = [(v - min_val) / (max_val - min_val) for v in values]
            else:
                normalized = [0.5] * len(values)

            normalized_data[metric] = normalized

            # Подготовка для радара
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={'projection': 'polar'})

        colors = plt.cm.Set3(np.linspace(0, 1, len(algorithms)))

        for idx, algo in enumerate(algorithms):
            values = [normalized_data[metric][idx] for metric in metrics]
            values += values[:1]

            ax.plot(angles, values, 'o-', linewidth=2, label=algo, color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])

            # Настройки
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_labels, fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_title('Multi-criteria Algorithm Comparison\n(Higher value = Better)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=10)
        ax.grid(True, alpha=0.3)

        BenchmarkPlotter._save_or_show(save_path, show)

    @staticmethod
    def plot_metrics_barchart(
            results,
            metrics=None,
            save_path=None,
            show=True
    ):
        """
        Группированная столбчатая диаграмма для нескольких метрик
        """
        if metrics is None:
            metrics = ['total_distance', 'execution_time', 'used_vehicles']

        # Группируем по алгоритмам
        groups = defaultdict(list)
        for result in results:
            groups[result.algorithm].append(result)

        algorithms = list(groups.keys())

        # Нормализуем каждую метрику для сравнения
        normalized_data = {metric: [] for metric in metrics}

        for metric in metrics:
            values = []
            for algo in algorithms:
                algo_values = [getattr(r, metric) for r in groups[algo]]
                values.append(np.mean(algo_values))

            min_val, max_val = min(values), max(values)
            if max_val - min_val > 1e-6:
                normalized = [(v - min_val) / (max_val - min_val) for v in values]
            else:
                normalized = [0.5] * len(values)

            normalized_data[metric] = normalized

            # Построение группированного графика
        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(algorithms))
        width = 0.8 / len(metrics)

        colors = plt.cm.Set2(np.linspace(0, 1, len(metrics)))

        for idx, metric in enumerate(metrics):
            offset = (idx - len(metrics) / 2) * width + width / 2
            bars = ax.bar(x + offset, normalized_data[metric], width,
                          label=metric.replace('_', ' ').title(),
                          color=colors[idx], alpha=0.8, edgecolor='black')

        ax.set_xlabel('Algorithm', fontsize=12)
        ax.set_ylabel('Normalized Value (0=best, 1=worst)', fontsize=12)
        ax.set_title('Algorithm Performance Comparison Across Metrics',
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=30)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

        BenchmarkPlotter._save_or_show(save_path, show)

    @staticmethod
    def plot_vehicle_efficiency(
            results,
            save_path=None,
            show=True
    ):
        """
        График эффективности: стоимость на одну машину
        """
        algorithms = []
        cost_per_vehicle = []

        # Группируем по алгоритмам
        groups = defaultdict(list)
        for result in results:
            groups[result.algorithm].append(result)

        for algo, algo_results in groups.items():
            algorithms.append(algo)
            avg_cost = np.mean([r.total_cost for r in algo_results])
            avg_vehicles = np.mean([r.used_vehicles for r in algo_results])
            cost_per_vehicle.append(avg_cost / avg_vehicles if avg_vehicles > 0 else 0)

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(algorithms, cost_per_vehicle, color='steelblue',
                      alpha=0.7, edgecolor='black')

        # Добавляем значения
        for bar, val in zip(bars, cost_per_vehicle):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(cost_per_vehicle) * 0.02,
                    f'{val:.1f}', ha='center', va='bottom', fontweight='bold')

        ax.set_xlabel('Algorithm', fontsize=12)
        ax.set_ylabel('Cost per Vehicle', fontsize=12)
        ax.set_title('Vehicle Efficiency (Lower is Better)', fontsize=14, fontweight='bold')
        ax.set_xticklabels(algorithms, rotation=30)
        ax.grid(True, alpha=0.3, axis='y')

        BenchmarkPlotter._save_or_show(save_path, show)

    @staticmethod
    def plot_comprehensive_summary(
            results,
            output_folder,
            histories=None,
            reference_algorithm="OR-Tools"
    ):
        """
        Генерирует полный набор графиков для курсовой работы
        """
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        print("\n" + "=" * 60)
        print("ГЕНЕРАЦИЯ ГРАФИКОВ ДЛЯ КУРСОВОЙ РАБОТЫ")
        print("=" * 60)

        # 1. Базовые графики (твои существующие)
        print("\n1. Базовые графики...")
        BenchmarkPlotter.plot_summary(results, output_folder)

        # 2. Ящик с усами (статистика)
        print("2. Статистические распределения...")
        BenchmarkPlotter.plot_boxplot_comparison(
            results,
            metric='total_cost',
            metric_name='Total Cost',
            save_path=output_folder / "boxplot_cost.png",
            show=False
        )

        # 3. График сходимости (если есть истории)
        if histories:
            print("3. Графики сходимости...")
            BenchmarkPlotter.plot_convergence(
                histories,
                save_path=output_folder / "convergence.png",
                show=False
            )

        # 4. Радарная диаграмма
        print("4. Радарная диаграмма...")

        from stats.metrics import Metrics
        summary = Metrics.algorithm_summary(results)
        BenchmarkPlotter.plot_radar_chart(
            summary,
            save_path=output_folder / "radar_chart.png",
            show=False
        )

        # 5. Сравнение метрик
        print("5. Сравнение по метрикам...")
        BenchmarkPlotter.plot_metrics_barchart(
            results,
            save_path=output_folder / "metrics_comparison.png",
            show=False
        )

        # 6. Эффективность машин
        print("6. Эффективность ТС...")
        BenchmarkPlotter.plot_vehicle_efficiency(
            results,
            save_path=output_folder / "vehicle_efficiency.png",
            show=False
        )
        # 7. Gap-анализ
        print("7. Gap-анализ...")
        try:
            BenchmarkPlotter.plot_gap_to_reference(
                results,
                reference_algorithm=reference_algorithm,
                save_path=output_folder / "gap_analysis.png",
                show=False
            )
        except ValueError as e:
            print(f"   Пропущено: {e}")

        print(f"\n✅ Все графики сохранены в: {output_folder}")
        print("=" * 60)