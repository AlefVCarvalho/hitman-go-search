# Fornece a interface de linha de comando e exibe os resultados das buscas.
from __future__ import annotations

import argparse

from .levels import LEVELS, TEST_CASES
from .search import SearchResult, astar, bfs


def print_result(result: SearchResult) -> None:
    print(f"\nAlgoritmo: {result.algorithm}")
    print(f"Objetivo: {'maleta + objetivo final' if result.require_briefcase else 'objetivo final'}")
    print(f"Solução encontrada: {'sim' if result.found else 'não'}")
    print(f"Custo: {result.cost}")
    print(f"Caminho: {' -> '.join(result.path) if result.path else '-'}")
    print(f"Estados expandidos: {result.expanded}")
    print(f"Estados gerados: {result.generated}")
    print(f"Pico da fronteira: {result.max_frontier}")
    print(f"Tempo: {result.elapsed_seconds:.8f} s")


def run_level(level_key: str, algorithm: str, require_briefcase: bool) -> None:
    level = LEVELS[level_key]
    print("\n" + "=" * 72)
    print(f"Fase: {level.name}")
    print(f"Modo: {'coletar maleta e concluir' if require_briefcase else 'concluir fase'}")

    if require_briefcase and level.briefcase is None:
        print("Esta fase não possui maleta configurada.")
        return

    if algorithm in ("bfs", "both"):
        print_result(bfs(level, require_briefcase=require_briefcase))

    if algorithm in ("astar", "both"):
        print_result(astar(level, require_briefcase=require_briefcase))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Busca cega e informada em um ambiente de infiltração."
    )
    parser.add_argument("--level", choices=LEVELS.keys(), default="1-3")
    parser.add_argument("--algorithm", choices=("bfs", "astar", "both"), default="both")
    parser.add_argument(
        "--briefcase",
        action="store_true",
        help="Exige coletar a maleta antes de concluir a fase.",
    )
    parser.add_argument(
        "--test",
        choices=TEST_CASES.keys(),
        help="Executa um dos três grupos experimentais do trabalho.",
    )
    args = parser.parse_args()

    if args.test:
        print(f"Teste experimental {args.test}")
        for level_key, require_briefcase in TEST_CASES[args.test]:
            run_level(level_key, args.algorithm, require_briefcase)
        return

    run_level(args.level, args.algorithm, args.briefcase)


if __name__ == "__main__":
    main()
