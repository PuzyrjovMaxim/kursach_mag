from pathlib import Path

import matplotlib.pyplot as plt


class RoutePlotter:

    @staticmethod
    def plot(
        instance,
        solution,
        save_path=None,
        show=True
    ):

        depot = instance.depot

        plt.figure(
            figsize=(10, 8)
        )

        plt.scatter(
            depot.x,
            depot.y,
            s=150,
            marker="s",
            label="Depot"
        )

        for route in solution.routes:

            if not route.clients:
                continue

            x = [depot.x]
            y = [depot.y]

            for client in route.clients:

                x.append(
                    client.x
                )

                y.append(
                    client.y
                )

            x.append(
                depot.x
            )

            y.append(
                depot.y
            )

            plt.plot(
                x,
                y,
                linewidth=1.5
            )

            plt.scatter(
                x[1:-1],
                y[1:-1],
                s=25
            )

        plt.title(
            f"{solution.algorithm}\n"
            f"Distance = "
            f"{solution.total_distance:.2f}"
        )

        plt.xlabel(
            "X"
        )

        plt.ylabel(
            "Y"
        )

        plt.grid(
            True
        )

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
    def save(
        instance,
        solution,
        save_path
    ):

        RoutePlotter.plot(
            instance=instance,
            solution=solution,
            save_path=save_path,
            show=False
        )