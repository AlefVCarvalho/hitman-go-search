from __future__ import annotations

import argparse

from .levels import LEVELS
from .search import SearchResult, astar, bfs


def print_result(result: SearchResult) -> None:
    print(f"\nAlgoritmo: {result.algorithm}")
    print(f"Solução encontrada: {'sim' if result.found else 'não'}")
    print(f"Custo: {result.cost}")
    print(f"Caminho: {' -> '.join(result.path) if result.path else '-'}")
    print(f"Estados expandidos: {result.expanded}")
    print(f"Estados gerados: {result.generated}")
    print(f"Pico da fronteira: {result.max_frontier}")
    print(f"Tempo: {result.elapsed_seconds:.8f} s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Busca cega e informada em um ambiente de infiltração."
    )
    parser.add_argument("--level", choices=LEVELS.keys(), default="1-3")
    parser.add_argument("--algorithm", choices=("bfs", "astar", "both"), default="both")
    args = parser.parse_args()

    level = LEVELS[args.level]
    print(f"Fase: {level.name}")

    if args.algorithm in ("bfs", "both"):
        print_result(bfs(level))

    if args.algorithm in ("astar", "both"):
        print_result(astar(level))


if __name__ == "__main__":
    main()
