from collections import defaultdict
from statistics import mean
from statistics import median
from statistics import stdev
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from pathlib import Path


class Metrics:

    @staticmethod
    def average_cost(results):

        if not results:
            return 0.0

        return mean(
            result.total_cost
            for result in results
        )

    @staticmethod
    def average_distance(results):

        if not results:
            return 0.0

        return mean(
            result.total_distance
            for result in results
        )

    @staticmethod
    def average_execution_time(results):

        if not results:
            return 0.0

        return mean(
            result.execution_time
            for result in results
        )

    @staticmethod
    def average_vehicle_count(results):

        if not results:
            return 0.0

        return mean(
            result.used_vehicles
            for result in results
        )

    @staticmethod
    def average_coverage(results):

        if not results:
            return 0.0

        return mean(
            result.coverage_ratio
            for result in results
        )

    @staticmethod
    def best_result(results):

        if not results:
            return None

        return min(
            results,
            key=lambda result:
            result.total_cost
        )

    @staticmethod
    def worst_result(results):

        if not results:
            return None

        return max(
            results,
            key=lambda result:
            result.total_cost
        )

    @staticmethod
    def median_cost(results):

        if not results:
            return 0.0

        return median(
            result.total_cost
            for result in results
        )

    @staticmethod
    def cost_std(results):

        if len(results) < 2:
            return 0.0

        return stdev(
            result.total_cost
            for result in results
        )

    @staticmethod
    def algorithm_groups(results):

        groups = defaultdict(list)

        for result in results:

            groups[
                result.algorithm
            ].append(
                result
            )

        return groups

    @staticmethod
    def dataset_groups(results):

        groups = defaultdict(list)

        for result in results:

            groups[
                result.dataset
            ].append(
                result
            )

        return groups

    @staticmethod
    def algorithm_summary(results):

        summary = {}

        groups = (
            Metrics.algorithm_groups(
                results
            )
        )

        for algorithm, group in groups.items():

            summary[
                algorithm
            ] = {

                "runs":
                    len(group),

                "average_cost":
                    Metrics.average_cost(
                        group
                    ),

                "average_distance":
                    Metrics.average_distance(
                        group
                    ),

                "average_time":
                    Metrics.average_execution_time(
                        group
                    ),

                "average_vehicles":
                    Metrics.average_vehicle_count(
                        group
                    ),

                "average_coverage":
                    Metrics.average_coverage(
                        group
                    ),

                "median_cost":
                    Metrics.median_cost(
                        group
                    ),

                "cost_std":
                    Metrics.cost_std(
                        group
                    )
            }

        return summary

    @staticmethod
    def gap_to_reference(
        results,
        reference_algorithm="OR-Tools"
    ):

        groups = (
            Metrics.dataset_groups(
                results
            )
        )

        gaps = defaultdict(list)

        for dataset, dataset_results in groups.items():

            reference = None

            for result in dataset_results:

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
                continue

            for result in dataset_results:

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
                ) * 100.0

                gaps[
                    result.algorithm
                ].append(
                    gap
                )

        return {

            algorithm:
            mean(values)

            for algorithm, values
            in gaps.items()

            if values

        }

    @staticmethod
    def print_summary(results):

        summary = (
            Metrics.algorithm_summary(
                results
            )
        )

        print()

        print(
            "=" * 80
        )

        print(
            "ALGORITHM SUMMARY"
        )

        print(
            "=" * 80
        )

        for algorithm, data in summary.items():

            print()

            print(
                algorithm
            )

            print(
                f"Runs: "
                f"{data['runs']}"
            )

            print(
                f"Average cost: "
                f"{data['average_cost']:.2f}"
            )

            print(
                f"Average distance: "
                f"{data['average_distance']:.2f}"
            )

            print(
                f"Average time: "
                f"{data['average_time']:.4f} sec"
            )

            print(
                f"Average vehicles: "
                f"{data['average_vehicles']:.2f}"
            )

            print(
                f"Average coverage: "
                f"{data['average_coverage']:.2%}"
            )

            print(
                f"Median cost: "
                f"{data['median_cost']:.2f}"
            )

            print(
                f"Cost std: "
                f"{data['cost_std']:.2f}"
            )

    @staticmethod
    def to_dataframe(results) -> pd.DataFrame:
        """
        Преобразует список результатов в pandas DataFrame для анализа
        """
        data = []
        for result in results:
            data.append({
                'algorithm': result.algorithm,
                'dataset': result.dataset,
                'total_cost': result.total_cost,
                'total_distance': result.total_distance,
                'execution_time': result.execution_time,
                'used_vehicles': result.used_vehicles,
                'coverage_ratio': result.coverage_ratio
            })
        return pd.DataFrame(data)

    def comparative_table(results) -> pd.DataFrame:
        """
        Создает сравнительную таблицу алгоритмов для отчета
        """
        summary = Metrics.algorithm_summary(results)

        rows = []
        for algo, metrics in summary.items():
            rows.append({
                'Алгоритм': algo,
                'Кол-во запусков': metrics['runs'],
                'Средняя стоимость': f"{metrics['average_cost']:.2f}",
                'Среднее расстояние': f"{metrics['average_distance']:.2f}",
                'Среднее время (сек)': f"{metrics['average_time']:.4f}",
                'Среднее число машин': f"{metrics['average_vehicles']:.2f}",
                'Медиана стоимости': f"{metrics['median_cost']:.2f}",
                'Стд. отклонение': f"{metrics['cost_std']:.2f}"
            })

        df = pd.DataFrame(rows)

        # Сортируем по стоимости
        df['_sort_cost'] = df['Средняя стоимость'].astype(float)
        df = df.sort_values('_sort_cost').drop('_sort_cost', axis=1)

        return df

    @staticmethod
    def gap_table(results, reference_algorithm="OR-Tools") -> pd.DataFrame:
        """
        Таблица отклонений от референсного алгоритма (в процентах)
        """
        gaps = Metrics.gap_to_reference(results, reference_algorithm)

        if not gaps:
            return pd.DataFrame()

        rows = []
        for algo, gap in sorted(gaps.items(), key=lambda x: x[1]):
            rows.append({
                'Алгоритм': algo,
                f'Отклонение от {reference_algorithm} (%)': f"{gap:+.2f}%",
                'Оценка': 'Лучше' if gap < 0 else 'Хуже' if gap > 0 else 'Равно'
            })

        return pd.DataFrame(rows)

    @staticmethod
    def dataset_performance(results) -> pd.DataFrame:
        """
        Анализ производительности алгоритмов на разных датасетах
        """
        groups = Metrics.dataset_groups(results)

        rows = []
        for dataset, dataset_results in groups.items():
            summary = Metrics.algorithm_summary(dataset_results)

            for algo, metrics in summary.items():
                rows.append({
                    'Датасет': dataset,
                    'Алгоритм': algo,
                    'Стоимость': metrics['average_cost'],
                    'Расстояние': metrics['average_distance'],
                    'Время (сек)': metrics['average_time'],
                    'Машины': metrics['average_vehicles']
                })

        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def export_to_latex(results, filename="results_table.tex"):
        """
        Экспортирует таблицу в формат LaTeX для вставки в курсовую
        """
        df = Metrics.comparative_table(results)

        # Преобразуем в LaTeX
        latex = df.to_latex(
            index=False,
            escape=False,
            column_format='|' + 'c|' * len(df.columns),
            caption='Сравнение эффективности алгоритмов маршрутизации',
            label='tab:algorithms_comparison'
        )

        # Сохраняем
        path = Path(filename)
        path.write_text(latex, encoding='utf-8')
        print(f"✅ LaTeX таблица сохранена в {filename}")

        return latex

    @staticmethod
    def export_to_csv(results, filename="results_summary.csv"):
        """
        Экспортирует результаты в CSV для дальнейшего анализа
        """
        df = Metrics.to_dataframe(results)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ CSV файл сохранен в {filename}")

        return df