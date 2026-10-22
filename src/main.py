# Fornece a interface de linha de comando e coordena a execução e exibição das buscas.
from __future__ import annotations

import argparse

from .levels import LEVELS
from .output import (
    print_comparison,
    print_header,
    print_path,
    print_paths,
    print_search_step,
    print_trace_start,
)
from .search import astar, bfs


def run_level(
    level_key: str,
    require_briefcase: bool,
    step_algorithm: str | None = None,
) -> None:
    level = LEVELS[level_key]

    print_header(level.name, require_briefcase)

    if require_briefcase and level.briefcase is None:
        print("Esta fase não possui maleta configurada.")
        return

    if step_algorithm == "BFS":
        print_trace_start("BFS")
        bfs_result = bfs(
            level,
            require_briefcase=require_briefcase,
            on_step=print_search_step,
        )
        print_path(level_key, bfs_result)
        return

    if step_algorithm == "A*":
        print_trace_start("A*")
        astar_result = astar(
            level,
            require_briefcase=require_briefcase,
            on_step=print_search_step,
        )
        print_path(level_key, astar_result)
        return

    bfs_result = bfs(level, require_briefcase=require_briefcase)
    astar_result = astar(level, require_briefcase=require_briefcase)

    print_paths(level_key, bfs_result, astar_result)
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

    step_group = parser.add_mutually_exclusive_group()
    step_group.add_argument(
        "--bfs-step",
        action="store_true",
        help="Executa e exibe somente o processo da BFS passo a passo.",
    )
    step_group.add_argument(
        "--astar-step",
        action="store_true",
        help="Executa e exibe somente o processo do A* passo a passo.",
    )

    args = parser.parse_args()

    step_algorithm = None
    if args.bfs_step:
        step_algorithm = "BFS"
    elif args.astar_step:
        step_algorithm = "A*"

    run_level(args.level, args.briefcase, step_algorithm)


if __name__ == "__main__":
    main()
