# Implementa BFS e A*, reconstrói soluções e coleta métricas das buscas.
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
import itertools
import time

from .models import Level, State
from .problem import is_goal, relaxed_distances, successors


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


def bfs(level: Level, require_briefcase: bool = False) -> SearchResult:
    # BFS expande os estados por camadas de profundidade usando uma fila FIFO.
    # Como cada movimento custa 1, o primeiro objetivo encontrado tem custo mínimo.
    start_time = time.perf_counter()
    start = level.initial_state()

    frontier = deque([start])
    visited = {start}
    parents: dict[State, State | None] = {start: None}

    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        state = frontier.popleft()
        expanded += 1

        if is_goal(level, state, require_briefcase):
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

        for _, next_state, _ in successors(level, state):
            if next_state in visited:
                continue
            visited.add(next_state)
            parents[next_state] = state
            frontier.append(next_state)
            generated += 1

        max_frontier = max(max_frontier, len(frontier))

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


def astar(level: Level, require_briefcase: bool = False) -> SearchResult:
    # A* prioriza o menor f(n)=g(n)+h(n), combinando custo já percorrido e estimativa restante.
    # A heurística ignora guardas e usa distâncias no grafo, reduzindo expansões sem perder otimalidade.
    start_time = time.perf_counter()
    start = level.initial_state()

    to_goal = relaxed_distances(level, level.goal)
    to_briefcase = (
        relaxed_distances(level, level.briefcase)
        if require_briefcase and level.briefcase
        else None
    )

    def heuristic(state: State) -> int:
        if to_briefcase is not None and not state.briefcase_collected:
            return to_briefcase[state.position] + to_goal[level.briefcase]
        return to_goal[state.position]

    counter = itertools.count()
    frontier: list[tuple[int, int, int, int, State]] = []
    start_h = heuristic(start)
    heapq.heappush(frontier, (start_h, start_h, 0, next(counter), start))

    g_score: dict[State, int] = {start: 0}
    parents: dict[State, State | None] = {start: None}

    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        _, _, queued_g, _, state = heapq.heappop(frontier)

        if queued_g != g_score.get(state):
            continue

        expanded += 1

        if is_goal(level, state, require_briefcase):
            path = _reconstruct_path(parents, state)
            return SearchResult(
                algorithm="A*",
                found=True,
                path=path,
                cost=g_score[state],
                expanded=expanded,
                generated=generated,
                max_frontier=max_frontier,
                elapsed_seconds=time.perf_counter() - start_time,
                require_briefcase=require_briefcase,
            )

        current_g = g_score[state]
        for _, next_state, step_cost in successors(level, state):
            tentative_g = current_g + step_cost

            if tentative_g >= g_score.get(next_state, float("inf")):
                continue

            g_score[next_state] = tentative_g
            parents[next_state] = state
            h = heuristic(next_state)
            heapq.heappush(
                frontier,
                (tentative_g + h, h, tentative_g, next(counter), next_state),
            )
            generated += 1

        max_frontier = max(max_frontier, len(frontier))

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
