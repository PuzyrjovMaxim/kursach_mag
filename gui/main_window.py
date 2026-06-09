import tkinter as tk

from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from algorithms.greedy import GreedySolver
from algorithms.clarke_wright import ClarkeWrightSolver
from algorithms.genetic import GeneticSolver
from algorithms.tabu_search import TabuSearchSolver
from algorithms.immune import ImmuneSolver
from algorithms.ortools_solver import ORToolsSolver

from benchmark.benchmark_runner import (
    BenchmarkRunner
)

from export.csv_exporter import (
    CsvExporter
)

from statistics.metrics import (
    Metrics
)

from utils.dataset_loader import (
    DatasetLoader
)


class MainWindow:

    def __init__(
        self,
        root
    ):

        self.root = root

        self.root.title(
            "CVRPTW Benchmark System"
        )

        self.root.geometry(
            "1100x700"
        )

        self.dataset_folder = None

        self.results = []

        self.create_widgets()

    def create_widgets(
        self
    ):

        title = ttk.Label(
            self.root,
            text="CVRPTW Benchmark System",
            font=("Arial", 18)
        )

        title.pack(
            pady=10
        )

        dataset_frame = ttk.LabelFrame(
            self.root,
            text="Datasets"
        )

        dataset_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.dataset_label = ttk.Label(
            dataset_frame,
            text="No folder selected"
        )

        self.dataset_label.pack(
            side="left",
            padx=10,
            pady=10
        )

        select_button = ttk.Button(
            dataset_frame,
            text="Select Folder",
            command=self.select_folder
        )

        select_button.pack(
            side="right",
            padx=10
        )

        algorithm_frame = ttk.LabelFrame(
            self.root,
            text="Algorithms"
        )

        algorithm_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.greedy_var = tk.BooleanVar(
            value=True
        )

        self.cw_var = tk.BooleanVar(
            value=True
        )

        self.genetic_var = tk.BooleanVar(
            value=True
        )

        self.tabu_var = tk.BooleanVar(
            value=True
        )

        self.immune_var = tk.BooleanVar(
            value=True
        )

        self.ortools_var = tk.BooleanVar(
            value=True
        )

        ttk.Checkbutton(
            algorithm_frame,
            text="Greedy",
            variable=self.greedy_var
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=5
        )

        ttk.Checkbutton(
            algorithm_frame,
            text="Clarke-Wright",
            variable=self.cw_var
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=5
        )

        ttk.Checkbutton(
            algorithm_frame,
            text="Genetic",
            variable=self.genetic_var
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=5
        )

        ttk.Checkbutton(
            algorithm_frame,
            text="Tabu Search",
            variable=self.tabu_var
        ).grid(
            row=0,
            column=3,
            padx=10,
            pady=5
        )

        ttk.Checkbutton(
            algorithm_frame,
            text="Immune",
            variable=self.immune_var
        ).grid(
            row=0,
            column=4,
            padx=10,
            pady=5
        )

        ttk.Checkbutton(
            algorithm_frame,
            text="OR-Tools",
            variable=self.ortools_var
        ).grid(
            row=0,
            column=5,
            padx=10,
            pady=5
        )

        control_frame = ttk.Frame(
            self.root
        )

        control_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        run_button = ttk.Button(
            control_frame,
            text="Run Benchmark",
            command=self.run_benchmark
        )

        run_button.pack(
            side="left",
            padx=5
        )

        export_button = ttk.Button(
            control_frame,
            text="Export CSV",
            command=self.export_csv
        )

        export_button.pack(
            side="left",
            padx=5
        )

        stats_button = ttk.Button(
            control_frame,
            text="Show Statistics",
            command=self.show_statistics
        )

        stats_button.pack(
            side="left",
            padx=5
        )

        self.output = tk.Text(
            self.root,
            font=("Consolas", 10)
        )

        self.output.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def select_folder(
        self
    ):

        folder = filedialog.askdirectory()

        if folder:

            self.dataset_folder = folder

            self.dataset_label.config(
                text=folder
            )

    def create_solvers(
        self
    ):

        solvers = []

        if self.greedy_var.get():

            solvers.append(
                GreedySolver()
            )

        if self.cw_var.get():

            solvers.append(
                ClarkeWrightSolver()
            )

        if self.genetic_var.get():

            solvers.append(
                GeneticSolver()
            )

        if self.tabu_var.get():

            solvers.append(
                TabuSearchSolver()
            )

        if self.immune_var.get():

            solvers.append(
                ImmuneSolver()
            )

        if self.ortools_var.get():

            solvers.append(
                ORToolsSolver()
            )

        return solvers

    def run_benchmark(
        self
    ):

        if not self.dataset_folder:

            messagebox.showerror(
                "Error",
                "Select dataset folder"
            )

            return

        self.output.delete(
            "1.0",
            tk.END
        )

        loader = DatasetLoader()

        instances = loader.load_folder(
            self.dataset_folder,
            recursive=True
        )

        solvers = self.create_solvers()

        runner = BenchmarkRunner(
            solvers
        )

        self.results = runner.run_instances(
            instances
        )

        for result in self.results:

            self.output.insert(
                tk.END,
                (
                    f"{result.dataset} | "
                    f"{result.algorithm} | "
                    f"Cost={result.total_cost:.2f} | "
                    f"Time={result.execution_time:.4f}s\n"
                )
            )

        self.output.insert(
            tk.END,
            "\nBenchmark finished.\n"
        )

    def export_csv(
        self
    ):

        if not self.results:

            return

        file_path = (
            filedialog.asksaveasfilename(
                defaultextension=".csv"
            )
        )

        if not file_path:

            return

        CsvExporter.export(
            self.results,
            file_path
        )

        messagebox.showinfo(
            "Export",
            "CSV exported successfully"
        )

    def show_statistics(
        self
    ):

        if not self.results:

            return

        summary = (
            Metrics.algorithm_summary(
                self.results
            )
        )

        self.output.insert(
            tk.END,
            "\n====================\n"
        )

        self.output.insert(
            tk.END,
            "STATISTICS\n"
        )

        self.output.insert(
            tk.END,
            "====================\n"
        )

        for algorithm, data in summary.items():

            self.output.insert(
                tk.END,
                f"\n{algorithm}\n"
            )

            self.output.insert(
                tk.END,
                f"Average cost: "
                f"{data['average_cost']:.2f}\n"
            )

            self.output.insert(
                tk.END,
                f"Average distance: "
                f"{data['average_distance']:.2f}\n"
            )

            self.output.insert(
                tk.END,
                f"Average time: "
                f"{data['average_time']:.4f}s\n"
            )