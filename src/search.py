# Implementa BFS e A*, reconstrói soluções, coleta métricas e fornece eventos opcionais de execução.
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
import itertools
import time
from typing import Callable

from .models import Level, State
from .problem import is_goal, relaxed_distances, successors


# Guarda o resultado final, como caminho, custo e quantidade de estados
@dataclass(slots=True)
class SearchResult:
    algorithm: str
    found: bool
    path: list[str]
    cost: int | None
    expanded: int
    generated: int
    max_frontier: int
    elapsed_seconds: float
    require_briefcase: bool = False


# Guarda as informações de cada etapa para mostrar o passo a passo
@dataclass(frozen=True, slots=True)
class SearchStep:
    algorithm: str
    number: int
    current: State
    frontier: tuple[State, ...]
    visited_nodes: tuple[str, ...]
    expanded: int
    generated: int
    g: int
    h: int | None = None
    f: int | None = None
    goal: bool = False


# Define o tipo de função que recebe as etapas da busca
StepCallback = Callable[[SearchStep], None]


# Refaz o caminho do objetivo até o início e depois inverte a ordem
def _reconstruct_path(
    parents: dict[State, State | None],
    goal: State,
) -> list[str]:
    path: list[str] = []
    current: State | None = goal

    while current is not None:
        path.append(current.position)
        current = parents[current]

    path.reverse()
    return path


def bfs(
    level: Level,
    require_briefcase: bool = False,
    on_step: StepCallback | None = None,
) -> SearchResult:
    # BFS expande os estados por camadas de profundidade usando uma fila FIFO.
    # Como cada movimento custa 1, o primeiro objetivo encontrado tem custo mínimo.
    start_time = time.perf_counter()
    start = level.initial_state()

    # Prepara a fila, os estados já vistos e o histórico do caminho
    frontier = deque([start])
    visited = {start}
    parents: dict[State, State | None] = {start: None}
    depths = {start: 0} if on_step else None
    visited_nodes = [start.position] if on_step else None
    visited_node_set = {start.position} if on_step else None

    # Inicia a contagem dos estados e do tamanho da fila
    expanded = 0
    generated = 1
    max_frontier = 1

    # Retira o próximo estado da fila para analisá-lo
    while frontier:
        state = frontier.popleft()
        expanded += 1

        # Se chegou ao objetivo, guarda o passo final e devolve o resultado
        if is_goal(level, state, require_briefcase):
            if on_step and depths is not None and visited_nodes is not None:
                on_step(
                    SearchStep(
                        algorithm="BFS",
                        number=expanded,
                        current=state,
                        frontier=tuple(frontier),
                        visited_nodes=tuple(visited_nodes),
                        expanded=expanded,
                        generated=generated,
                        g=depths[state],
                        goal=True,
                    )
                )

            path = _reconstruct_path(parents, state)
            return SearchResult(
                algorithm="BFS",
                found=True,
                path=path,
                cost=len(path) - 1,
                expanded=expanded,
                generated=generated,
                max_frontier=max_frontier,
                elapsed_seconds=time.perf_counter() - start_time,
                require_briefcase=require_briefcase,
            )

        # Coloca na fila os próximos estados que ainda não apareceram
        for _, next_state, _ in successors(level, state):
            if next_state in visited:
                continue
            visited.add(next_state)
            parents[next_state] = state
            frontier.append(next_state)
            generated += 1

            # Registra a profundidade e as posições para a exibição
            if on_step and depths is not None:
                depths[next_state] = depths[state] + 1
                if (
                    visited_nodes is not None
                    and visited_node_set is not None
                    and next_state.position not in visited_node_set
                ):
                    visited_node_set.add(next_state.position)
                    visited_nodes.append(next_state.position)

        # Anota o maior tamanho que a fila alcançou
        max_frontier = max(max_frontier, len(frontier))

        # Envia esta etapa para mostrar o andamento da busca
        if on_step and depths is not None and visited_nodes is not None:
            on_step(
                SearchStep(
                    algorithm="BFS",
                    number=expanded,
                    current=state,
                    frontier=tuple(frontier),
                    visited_nodes=tuple(visited_nodes),
                    expanded=expanded,
                    generated=generated,
                    g=depths[state],
                )
            )

    # Se a fila acabar sem chegar ao objetivo, informa que não achou caminho
    return SearchResult(
        algorithm="BFS",
        found=False,
        path=[],
        cost=None,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        elapsed_seconds=time.perf_counter() - start_time,
        require_briefcase=require_briefcase,
    )


def astar(
    level: Level,
    require_briefcase: bool = False,
    on_step: StepCallback | None = None,
) -> SearchResult:
    # A* prioriza o menor f(n)=g(n)+h(n), combinando custo já percorrido e estimativa restante.
    # A heurística ignora guardas e usa distâncias no grafo, reduzindo expansões sem perder otimalidade.
    start_time = time.perf_counter()
    start = level.initial_state()

    # Calcula as distâncias no mapa sem considerar os guardas
    to_goal = relaxed_distances(level, level.goal)
    to_briefcase = (
        relaxed_distances(level, level.briefcase)
        if require_briefcase and level.briefcase
        else None
    )

    # Estima o que falta andar, incluindo a maleta quando necessário
    def heuristic(state: State) -> int:
        if to_briefcase is not None and not state.briefcase_collected:
            return to_briefcase[state.position] + to_goal[level.briefcase]
        return to_goal[state.position]

    # Prepara a fila por prioridade, os custos e o histórico do caminho
    counter = itertools.count()
    frontier: list[tuple[int, int, int, int, State]] = []
    start_h = heuristic(start)
    heapq.heappush(frontier, (start_h, start_h, 0, next(counter), start))

    g_score: dict[State, int] = {start: 0}
    parents: dict[State, State | None] = {start: None}
    visited_nodes = [start.position] if on_step else None
    visited_node_set = {start.position} if on_step else None

    # Começa a contar os estados analisados e gerados
    expanded = 0
    generated = 1
    max_frontier = 1

    # Pega da fila o estado com melhor prioridade
    while frontier:
        _, _, queued_g, _, state = heapq.heappop(frontier)

        # Ignora uma entrada antiga se já existe um caminho melhor
        if queued_g != g_score.get(state):
            continue

        expanded += 1
        current_g = g_score[state]
        current_h = heuristic(state)

        # Se chegou ao objetivo, registra o passo final e retorna o caminho
        if is_goal(level, state, require_briefcase):
            if on_step and visited_nodes is not None:
                # Deixa na fronteira só as entradas com custo ainda válido
                active_frontier = tuple(
                    item[4]
                    for item in sorted(frontier, key=lambda item: item[:4])
                    if item[2] == g_score.get(item[4])
                )
                on_step(
                    SearchStep(
                        algorithm="A*",
                        number=expanded,
                        current=state,
                        frontier=active_frontier,
                        visited_nodes=tuple(visited_nodes),
                        expanded=expanded,
                        generated=generated,
                        g=current_g,
                        h=current_h,
                        f=current_g + current_h,
                        goal=True,
                    )
                )

            path = _reconstruct_path(parents, state)
            return SearchResult(
                algorithm="A*",
                found=True,
                path=path,
                cost=current_g,
                expanded=expanded,
                generated=generated,
                max_frontier=max_frontier,
                elapsed_seconds=time.perf_counter() - start_time,
                require_briefcase=require_briefcase,
            )

        # Testa os próximos movimentos possíveis e seus custos
        for _, next_state, step_cost in successors(level, state):
            tentative_g = current_g + step_cost

            # Descarta o caminho se ele não melhora o custo conhecido
            if tentative_g >= g_score.get(next_state, float("inf")):
                continue

            # Salva o caminho melhor e coloca o estado na fila
            g_score[next_state] = tentative_g
            parents[next_state] = state
            h = heuristic(next_state)
            heapq.heappush(
                frontier,
                (tentative_g + h, h, tentative_g, next(counter), next_state),
            )
            generated += 1

            # Guarda as novas posições para mostrar no passo a passo
            if (
                on_step
                and visited_nodes is not None
                and visited_node_set is not None
                and next_state.position not in visited_node_set
            ):
                visited_node_set.add(next_state.position)
                visited_nodes.append(next_state.position)

        # Registra o maior tamanho alcançado pela fronteira
        max_frontier = max(max_frontier, len(frontier))

        # Envia os dados desta etapa para a visualização
        if on_step and visited_nodes is not None:
            active_frontier = tuple(
                item[4]
                for item in sorted(frontier, key=lambda item: item[:4])
                if item[2] == g_score.get(item[4])
            )
            on_step(
                SearchStep(
                    algorithm="A*",
                    number=expanded,
                    current=state,
                    frontier=active_frontier,
                    visited_nodes=tuple(visited_nodes),
                    expanded=expanded,
                    generated=generated,
                    g=current_g,
                    h=current_h,
                    f=current_g + current_h,
                )
            )

    # Se a fila acabar, retorna o resultado sem caminho encontrado
    return SearchResult(
        algorithm="A*",
        found=False,
        path=[],
        cost=None,
        expanded=expanded,
        generated=generated,
        max_frontier=max_frontier,
        elapsed_seconds=time.perf_counter() - start_time,
        require_briefcase=require_briefcase,
    )
