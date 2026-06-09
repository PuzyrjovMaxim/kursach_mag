# visualization/benchmark_plotter_extended.py
"""
Расширенный визуализатор для сравнения с оптимальными решениями
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

from utils.optimal_solutions_loader import OptimalSolutionsLoader


class BenchmarkPlotter:

    def __init__(self, output_dir: str = "benchmark_results/plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.optimal_loader = OptimalSolutionsLoader()

        # Настройка стиля
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("Set2")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 11

    def _save_or_show(self, save_path, show=False):
        plt.tight_layout()
        if save_path:
            plt.savefig(self.output_dir / save_path, dpi=300, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_gap_comparison(self, results):
        """График сравнения GAP по алгоритмам"""
        data = []
        for r in results:
            gap_info = self.optimal_loader.calculate_gap(r.dataset, r.total_distance, r.used_vehicles)
            if gap_info["distance_gap"] is not None:
                data.append({
                    "Algorithm": r.algorithm,
                    "GAP (%)": gap_info["distance_gap"],
                    "Instance": r.dataset
                })

        df = pd.DataFrame(data)

        plt.figure(figsize=(14, 6))
        ax = sns.boxplot(data=df, x="Algorithm", y="GAP (%)")
        ax.set_title("Comparison of Algorithm Performance (GAP to Optimal)", fontsize=14, fontweight='bold')
        ax.set_ylabel("GAP to Optimal (%)")
        ax.set_xlabel("Algorithm")

        # Добавляем горизонтальную линию на 0
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7)

        # Добавляем значения на график
        for i, algo in enumerate(df["Algorithm"].unique()):
            algo_data = df[df["Algorithm"] == algo]["GAP (%)"]
            median = algo_data.median()
            ax.text(i, median + 0.5, f'{median:.1f}%', ha='center', fontsize=9)

        self._save_or_show("gap_comparison.png")

    def plot_group_comparison(self, results, group_name):
        """Сравнение алгоритмов внутри группы"""
        data = []
        for r in results:
            data.append({
                "Algorithm": r.algorithm,
                "Distance": r.total_distance,
                "Vehicles": r.used_vehicles,
                "Time": r.execution_time
            })

        df = pd.DataFrame(data)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Расстояние
        sns.barplot(data=df, x="Algorithm", y="Distance", ax=axes[0])
        axes[0].set_title(f"{group_name} - Total Distance", fontweight='bold')
        axes[0].tick_params(axis='x', rotation=45)

        # Машины
        sns.barplot(data=df, x="Algorithm", y="Vehicles", ax=axes[1])
        axes[1].set_title(f"{group_name} - Number of Vehicles", fontweight='bold')
        axes[1].tick_params(axis='x', rotation=45)

        # Время
        sns.barplot(data=df, x="Algorithm", y="Time", ax=axes[2])
        axes[2].set_title(f"{group_name} - Execution Time", fontweight='bold')
        axes[2].tick_params(axis='x', rotation=45)

        plt.suptitle(f"Performance by Algorithm - {group_name}", fontsize=14, fontweight='bold')
        self._save_or_show(f"group_{group_name}_comparison.png")

    def plot_vehicles_comparison(self, results):
        """Сравнение количества машин с оптимальным"""
        data = []
        for r in results:
            optimal = self.optimal_loader.get_optimal(r.dataset)
            data.append({
                "Algorithm": r.algorithm,
                "Instance": r.dataset,
                "Vehicles": r.used_vehicles,
                "Optimal Vehicles": optimal["vehicles"] if optimal else None
            })

        df = pd.DataFrame(data)

        # Группируем по алгоритму
        fig, ax = plt.subplots(figsize=(12, 6))

        algorithms = df["Algorithm"].unique()
        x = np.arange(len(algorithms))
        width = 0.35

        avg_vehicles = [df[df["Algorithm"] == algo]["Vehicles"].mean() for algo in algorithms]
        avg_optimal = []
        for algo in algorithms:
            opt_vals = []
            for _, row in df[df["Algorithm"] == algo].iterrows():
                if row["Optimal Vehicles"] is not None:
                    opt_vals.append(row["Optimal Vehicles"])
            avg_optimal.append(np.mean(opt_vals) if opt_vals else 0)

        bars1 = ax.bar(x - width / 2, avg_vehicles, width, label='Algorithm', color='steelblue')
        bars2 = ax.bar(x + width / 2, avg_optimal, width, label='Optimal', color='coral')

        ax.set_xlabel('Algorithm')
        ax.set_ylabel('Number of Vehicles')
        ax.set_title('Vehicles Comparison: Algorithm vs Optimal')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45)
        ax.legend()

        # Добавляем значения
        for bar, val in zip(bars1, avg_vehicles):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=9)

        self._save_or_show("vehicles_comparison.png")

    def plot_gap_heatmap(self, all_results):
        """Тепловая карта GAP по инстансам и алгоритмам"""
        data = []

        for group_name, results in all_results.items():
            for r in results:
                gap_info = self.optimal_loader.calculate_gap(r.dataset, r.total_distance, r.used_vehicles)
                if gap_info["distance_gap"] is not None:
                    data.append({
                        "Instance": r.dataset,
                        "Algorithm": r.algorithm,
                        "GAP (%)": gap_info["distance_gap"]
                    })

        df = pd.DataFrame(data)

        # Создаем сводную таблицу
        pivot = df.pivot(index="Instance", columns="Algorithm", values="GAP (%)")

        plt.figure(figsize=(14, 10))
        ax = sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlGn_r', center=0)
        ax.set_title("GAP to Optimal by Instance and Algorithm (%)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Instance")

        self._save_or_show("gap_heatmap.png")

    def plot_convergence_by_group(self, results, group_name):
        """График сходимости по группе"""
        data = []
        for r in results:
            data.append({
                "Algorithm": r.algorithm,
                "Distance": r.total_distance,
                "Instance": r.dataset
            })

        df = pd.DataFrame(data)

        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x="Algorithm", y="Distance")
        plt.title(f"Distance Distribution - {group_name}", fontsize=14, fontweight='bold')
        plt.ylabel("Total Distance")
        plt.xlabel("Algorithm")
        plt.xticks(rotation=45)

        self._save_or_show(f"convergence_{group_name}.png")

    def create_radar_chart(self, results):
        """Радарная диаграмма для многокритериального сравнения"""
        algorithms = list(set(r.algorithm for r in results))

        # Метрики для сравнения
        metrics = ["Distance", "Vehicles", "Time", "GAP"]

        # Нормализация метрик
        data = {}
        for algo in algorithms:
            algo_results = [r for r in results if r.algorithm == algo]

            avg_distance = np.mean([r.total_distance for r in algo_results])
            avg_vehicles = np.mean([r.used_vehicles for r in algo_results])
            avg_time = np.mean([r.execution_time for r in algo_results])

            gaps = []
            for r in algo_results:
                gap_info = self.optimal_loader.calculate_gap(r.dataset, r.total_distance, r.used_vehicles)
                if gap_info["distance_gap"] is not None:
                    gaps.append(gap_info["distance_gap"])
            avg_gap = np.mean(gaps) if gaps else 0

            data[algo] = [avg_distance, avg_vehicles, avg_time, avg_gap]

        # Нормализация
        min_max = {}
        for i, metric in enumerate(metrics):
            values = [data[algo][i] for algo in algorithms]
            min_val, max_val = min(values), max(values)
            if max_val > min_val:
                min_max[metric] = (min_val, max_val)

        # Радар
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})

        colors = plt.cm.Set3(np.linspace(0, 1, len(algorithms)))

        for idx, algo in enumerate(algorithms):
            values = []
            for i, metric in enumerate(metrics):
                raw_val = data[algo][i]
                if metric in min_max:
                    min_val, max_val = min_max[metric]
                    norm_val = (raw_val - min_val) / (max_val - min_val)
                    values.append(1 - norm_val)  # Инвертируем (чем меньше, тем лучше)
                else:
                    values.append(0.5)

            values += values[:1]
            ax.plot(angles, values, 'o-', linewidth=2, label=algo, color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title("Multi-Criteria Algorithm Comparison", fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

        self._save_or_show("radar_chart_comparison.png")