# Centraliza a formatação da saída e da visualização passo a passo das buscas
from __future__ import annotations

from .search import SearchResult, SearchStep


# Guarda as posições dos nós para desenhar os movimentos de cada fase
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


# Descobre qual seta representa o movimento entre dois nós
def movement_arrow(level_key: str, current: str, next_node: str) -> str:
    current_x, current_y = NODE_POSITIONS[level_key][current]
    next_x, next_y = NODE_POSITIONS[level_key][next_node]

    # Compara as posições para saber a direção do movimento
    if current_y == next_y:
        return "→" if next_x > current_x else "←"
    if current_x == next_x:
        return "↓" if next_y > current_y else "↑"

    raise ValueError(f"Movimento incoerente entre {current} e {next_node}")


# Converte o caminho encontrado em uma sequência de setas
def format_path(level_key: str, result: SearchResult | None) -> str:
    if result is None:
        return "não executado"
    if not result.found or not result.path:
        return "nenhum caminho encontrado"

    # Monta uma seta para cada movimento do caminho
    arrows = [
        movement_arrow(level_key, current, next_node)
        for current, next_node in zip(result.path, result.path[1:])
    ]
    return " ".join(("início", *arrows, "fim"))


# Prepara o valor de uma métrica para exibir na tabela
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


# Mostra o nome da fase e o objetivo da busca
def print_header(level_name: str, require_briefcase: bool) -> None:
    print("\n" + "=" * 40)
    print("Hitman Go Search")
    print(f"Nível: {level_name}")
    print(
        "Objetivo: "
        + ("coletar a maleta e chegar ao final" if require_briefcase else "chegar ao final")
    )
    print("=" * 40)


# Mostra o caminho do algoritmo que acabou de rodar
def print_path(level_key: str, result: SearchResult) -> None:
    print(f"\nCaminho encontrado por {result.algorithm}:")
    print(format_path(level_key, result))


# Mostra os caminhos de BFS e A* na comparação
def print_paths(
    level_key: str,
    bfs_result: SearchResult | None,
    astar_result: SearchResult | None,
) -> None:
    print("\nCaminho encontrado por BFS:")
    print(format_path(level_key, bfs_result))

    print("\nCaminho encontrado por A*:")
    print(format_path(level_key, astar_result))


# Monta a tabela que compara os resultados das duas buscas
def print_comparison(
    bfs_result: SearchResult | None,
    astar_result: SearchResult | None,
) -> None:
    # Escolhe quais métricas vão aparecer na tabela
    rows = (
        ("Custo", "cost"),
        ("Estados gerados", "generated"),
        ("Estados explorados", "expanded"),
        ("Fronteira max", "max_frontier"),
        ("Tempo", "time"),
    )

    # Prepara os valores e ajusta a largura das colunas
    bfs_values = [format_metric(bfs_result, metric) for _, metric in rows]
    astar_values = [format_metric(astar_result, metric) for _, metric in rows]

    metric_width = max(len("Métrica"), *(len(label) for label, _ in rows))
    bfs_width = max(len("BFS"), *(len(value) for value in bfs_values))
    astar_width = max(len("A*"), *(len(value) for value in astar_values))

    # Desenha o cabeçalho e as bordas da tabela
    separator = f"+-{'-' * metric_width}-+-{'-' * bfs_width}-+-{'-' * astar_width}-+"

    print("\nComparação dos algoritmos:")
    print(separator)
    print(
        f"| {'Métrica':<{metric_width}} "
        f"| {'BFS':>{bfs_width}} "
        f"| {'A*':>{astar_width}} |"
    )
    print(separator)

    # Escreve cada métrica com o resultado de cada algoritmo
    for (label, _), bfs_value, astar_value in zip(rows, bfs_values, astar_values):
        print(
            f"| {label:<{metric_width}} "
            f"| {bfs_value:>{bfs_width}} "
            f"| {astar_value:>{astar_width}} |"
        )

    print(separator)


# Mostra que a execução passo a passo começou
def print_trace_start(algorithm: str) -> None:
    print(f"\nProcesso da busca {algorithm}:")
    print("=" * 40)


# Exibe o estado atual, os nós vistos e a fronteira da busca
def print_search_step(step: SearchStep) -> None:
    # Mostra só a posição de cada estado, mesmo que algumas se repitam
    frontier_nodes = [state.position for state in step.frontier]
    frontier_text = ", ".join(frontier_nodes) if frontier_nodes else "vazia"
    visited_text = ", ".join(step.visited_nodes)

    # Mostra os custos do A* ou a profundidade da BFS
    print(f"Atual: {step.current.position}")
    if step.algorithm == "A*":
        print(f"f = {step.f} / g = {step.g} / h = {step.h}")
    else:
        print(f"Profundidade: {step.g}")
    print(f"Posições visitadas: {visited_text}")
    print(f"Fronteira: {frontier_text}")
    # Avisa quando a busca encontrou o objetivo
    if step.goal:
        print("Objetivo encontrado.")
    print("-" * 40)
