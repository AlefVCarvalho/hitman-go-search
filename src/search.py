from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
import itertools
import time

from .models import Level, State
from .problem import heuristic_cost, is_goal, successors


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


def _reconstruct_path(
    parents: dict[State, tuple[State | None, str | None]],
    goal: State,
) -> list[str]:
    path: list[str] = []
    current: State | None = goal

    while current is not None:
        path.append(current.position)
        current = parents[current][0]

    path.reverse()
    return path


def bfs(level: Level) -> SearchResult:
    start_time = time.perf_counter()
    start = level.initial_state()

    frontier = deque([start])
    visited = {start}
    parents: dict[State, tuple[State | None, str | None]] = {
        start: (None, None)
    }

    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        state = frontier.popleft()
        expanded += 1

        if is_goal(level, state):
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
            )

        for action, next_state, _ in successors(level, state):
            if next_state in visited:
                continue
            visited.add(next_state)
            parents[next_state] = (state, action)
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
    )


def astar(level: Level) -> SearchResult:
    start_time = time.perf_counter()
    start = level.initial_state()

    counter = itertools.count()
    frontier: list[tuple[int, int, int, State]] = []
    heapq.heappush(frontier, (heuristic_cost(level, start), 0, next(counter), start))

    g_score: dict[State, int] = {start: 0}
    parents: dict[State, tuple[State | None, str | None]] = {
        start: (None, None)
    }

    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        _, queued_g, _, state = heapq.heappop(frontier)

        if queued_g != g_score.get(state):
            continue

        expanded += 1

        if is_goal(level, state):
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
            )

        for action, next_state, step_cost in successors(level, state):
            tentative_g = g_score[state] + step_cost

            if tentative_g >= g_score.get(next_state, float("inf")):
                continue

            g_score[next_state] = tentative_g
            parents[next_state] = (state, action)
            h = heuristic_cost(level, next_state)
            heapq.heappush(
                frontier,
                (tentative_g + h, tentative_g, next(counter), next_state),
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
    )
