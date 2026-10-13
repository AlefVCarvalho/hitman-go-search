# Fornece a interface de linha de comando e apresenta os caminhos e resultados comparativos das buscas.
from __future__ import annotations

import argparse

from .levels import LEVELS
from .search import SearchResult, astar, bfs


NODE_POSITIONS = {
    "1-3": {
        "N0": (1, 0),
        "N1": (0, 1), "N2": (1, 1), "N3": (2, 1), "N4": (3, 1),
        "N5": (0, 2), "N6": (1, 2), "N7": (2, 2),
    },
    "1-4": {
        "N0": (0, 0), "N1": (1, 0), "N2": (2, 0), "N3": (3, 0),
        "N4": (0, 1), "N5": (1, 1), "N6": (2, 1), "N7": (3, 1), "N8": (4, 1),
        "N9": (0, 2), "N10": (1, 2), "N11": (2, 2), "N12": (3, 2), "N13": (4, 2),
        "N14": (0, 3), "N15": (1, 3), "N16": (2, 3), "N17": (3, 3),
    },
    "1-12": {
        "N0": (4, 0),
        "N1": (0, 1), "N2": (1, 1), "N3": (2, 1), "N4": (3, 1), "N5": (4, 1),
        "N6": (0, 2), "N7": (1, 2), "N8": (2, 2), "N9": (3, 2), "N10": (4, 2),
        "N11": (0, 3), "N12": (1, 3), "N13": (2, 3), "N14": (4, 3),
    },
    "1-15": {
        "N0": (0, 0), "N1": (1, 0), "N2": (2, 0), "N3": (3, 0), "N4": (4, 0),
        "N5": (0, 1), "N6": (1, 1), "N7": (2, 1), "N8": (3, 1), "N9": (4, 1),
        "N10": (0, 2), "N11": (1, 2), "N12": (2, 2), "N13": (3, 2), "N14": (4, 2),
        "N15": (0, 3), "N16": (1, 3), "N17": (2, 3), "N18": (3, 3), "N19": (4, 3),
        "N20": (1, 4), "N21": (2, 4), "N22": (3, 4),
    },
}


def movement_arrow(level_key: str, current: str, next_node: str) -> str:
    current_x, current_y = NODE_POSITIONS[level_key][current]
    next_x, next_y = NODE_POSITIONS[level_key][next_node]

    if current_y == next_y:
        return "→" if next_x > current_x else "←"
    if current_x == next_x:
        return "↓" if next_y > current_y else "↑"

    raise ValueError(f"Movimento não ortogonal entre {current} e {next_node}.")


def format_path(level_key: str, result: SearchResult | None) -> str:
    if result is None:
        return "não executado"
    if not result.found or not result.path:
        return "nenhum caminho encontrado"

    arrows = [
        movement_arrow(level_key, current, next_node)
        for current, next_node in zip(result.path, result.path[1:])
    ]
    return " ".join(("início", *arrows, "fim"))


def format_metric(result: SearchResult | None, metric: str) -> str:
    if result is None:
        return "-"

    values = {
        "cost": str(result.cost) if result.cost is not None else "-",
        "generated": str(result.generated),
        "expanded": str(result.expanded),
        "max_frontier": str(result.max_frontier),
        "time": f"{result.elapsed_seconds * 1000:.3f} ms",
    }
    return values[metric]


def print_comparison(
    bfs_result: SearchResult | None,
    astar_result: SearchResult | None,
) -> None:
    rows = (
        ("Custo (movimentos)", "cost"),
        ("Estados gerados", "generated"),
        ("Estados explorados", "expanded"),
        ("Pico de fronteira", "max_frontier"),
        ("Tempo", "time"),
    )

    bfs_values = [format_metric(bfs_result, metric) for _, metric in rows]
    astar_values = [format_metric(astar_result, metric) for _, metric in rows]

    metric_width = max(len("Métrica"), *(len(label) for label, _ in rows))
    bfs_width = max(len("BFS"), *(len(value) for value in bfs_values))
    astar_width = max(len("A*"), *(len(value) for value in astar_values))

    separator = f"+-{'-' * metric_width}-+-{'-' * bfs_width}-+-{'-' * astar_width}-+"

    print("\nComparação dos algoritmos:")
    print(separator)
    print(
        f"| {'Métrica':<{metric_width}} "
        f"| {'BFS':>{bfs_width}} "
        f"| {'A*':>{astar_width}} |"
    )
    print(separator)

    for (label, _), bfs_value, astar_value in zip(rows, bfs_values, astar_values):
        print(
            f"| {label:<{metric_width}} "
            f"| {bfs_value:>{bfs_width}} "
            f"| {astar_value:>{astar_width}} |"
        )

    print(separator)


def run_level(level_key: str, require_briefcase: bool) -> None:
    level = LEVELS[level_key]

    print("\n" + "=" * 72)
    print("Hitman Go Search")
    print(f"Nível: {level.name}")
    print(
        "Objetivo: "
        + ("coletar a maleta e chegar ao final" if require_briefcase else "chegar ao final")
    )
    print("=" * 72)

    if require_briefcase and level.briefcase is None:
        print("Esta fase não possui maleta configurada.")
        return

    bfs_result = bfs(level, require_briefcase=require_briefcase)
    astar_result = astar(level, require_briefcase=require_briefcase)

    print("\nCaminho encontrado por BFS:")
    print(format_path(level_key, bfs_result))

    print("\nCaminho encontrado por A*:")
    print(format_path(level_key, astar_result))

    print_comparison(bfs_result, astar_result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compara BFS e A* nos níveis modelados de Hitman GO."
    )
    parser.add_argument("--level", choices=LEVELS.keys(), default="1-3")
    parser.add_argument(
        "--briefcase",
        action="store_true",
        help="Exige coletar a maleta antes de concluir a fase.",
    )
    args = parser.parse_args()

    run_level(args.level, args.briefcase)


if __name__ == "__main__":
    main()
