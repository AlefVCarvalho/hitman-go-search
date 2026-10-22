# Regras que dizem se um movimento pode acontecer
# Monta os próximos estados e já calcula distâncias para o A* (evita repetição)
from __future__ import annotations

from collections import deque
from functools import lru_cache
from typing import Iterable

from .models import Level, MovingGuardState, State


# Confere se o agente chegou a saída
# Se a maleta é obrigatória, também verifica se foi coletada
def is_goal(level: Level, state: State, require_briefcase: bool = False) -> bool:
    if state.position != level.goal:
        return False
    if require_briefcase:
        return state.briefcase_collected
    return True


# Verifica se algum guarda parado (e ativo) está olhando para o nó
# Quando o nó é um arbusto é ignorado
def watched_by_static_guard(level: Level, state: State, node: str) -> bool:
    if node in level.hiding_nodes:
        return False
    return any(
        level.guards[guard_position] is not None
        and level.guards[guard_position] == node
        for guard_position in state.active_guards
    )


# Descobre em qual nó está um guarda móvel usando a posição atual na rota
def _moving_guard_position(
    level: Level,
    guard_index: int,
    guard_state: MovingGuardState,
) -> str:
    return level.moving_guards[guard_index].route[guard_state.index]


# Descobre qual nó fica frente de um guarda móvel
# Leva em conta o sentido da patrulha e volta nas pontas da rota
def _moving_guard_front(
    level: Level,
    guard_index: int,
    guard_state: MovingGuardState,
) -> str | None:
    # Sem outro ponto na rota o guarda não tem um próximo nó pra olhar
    guard = level.moving_guards[guard_index]
    if len(guard.route) <= 1:
        return None

    direction = guard_state.direction
    next_index = guard_state.index + direction
    # chegar no fim da rota muda de sentido
    if not 0 <= next_index < len(guard.route):
        direction *= -1
        next_index = guard_state.index + direction

    return guard.route[next_index]


# Atualiza a posição do guarda móvel depois de um turno
# Guardas eliminados não andam
def _advance_moving_guard(
    level: Level,
    guard_index: int,
    guard_state: MovingGuardState,
) -> MovingGuardState:
    if not guard_state.active:
        return guard_state

    # Sem outro ponto na rota o guarda não tem um próximo nó pra olhar
    guard = level.moving_guards[guard_index]
    if len(guard.route) <= 1:
        return guard_state

    direction = guard_state.direction
    next_index = guard_state.index + direction

    # chegar no fim da rota muda de sentido
    if not 0 <= next_index < len(guard.route):
        direction *= -1
        next_index = guard_state.index + direction

    return MovingGuardState(index=next_index, direction=direction, active=True)


# faz agente andar para um nó vizinho
# Se o movimento for seguro monta o novo estado do jogo
# Se alguma regra impedir a jogada retorna None
def apply_move(level: Level, state: State, destination: str) -> State | None:
    # Primeiro confere se existe caminho para o destino
    # Uma tentativa fora do mapa é tratada como erro
    if destination not in level.graph[state.position]:
        raise ValueError(
            f"Movimento inválido: {state.position} -> {destination} não é uma aresta."
        )

    # Prepara as informações dos guardas pra jogada sem mexer no estado que existe
    active_guards = state.active_guards
    moving_states = list(state.moving_guards)

    # Se houver um guarda parado no destino o agente só elimina se não for pela frente
    if destination in active_guards:
        if level.guards[destination] == state.position:
            return None
        active_guards = frozenset(
            guard for guard in active_guards if guard != destination
        )

    # Faz a mesma verificação para os guardas móveis no destino
    # Se o agente chegar por um lado elimina
    for index, guard_state in enumerate(moving_states):
        if not guard_state.active:
            continue
        if _moving_guard_position(level, index, guard_state) != destination:
            continue

        if _moving_guard_front(level, index, guard_state) == state.position:
            return None

        moving_states[index] = MovingGuardState(
            index=guard_state.index,
            direction=guard_state.direction,
            active=False,
        )

    # Guarda se a maleta já foi pega
    briefcase_collected = state.briefcase_collected or destination == level.briefcase

    # Monta uma situação temporária depois do passo do agente antes dos guardas móveis andarem
    after_agent = State(
        position=destination,
        active_guards=active_guards,
        moving_guards=tuple(moving_states),
        briefcase_collected=briefcase_collected,
    )

    # Não deixa o agente na frente de um guarda fixo que continua ativo
    if watched_by_static_guard(level, after_agent, destination):
        return None

    # Antes de movimentar os guardas confere se o agente ficou na frente de guarda móvel (sem arbusto)
    if destination not in level.hiding_nodes:
        for index, guard_state in enumerate(after_agent.moving_guards):
            if not guard_state.active:
                continue
            if _moving_guard_front(level, index, guard_state) == destination:
                return None

    # Depois do agente guardas móveis ativos avançam pela rota
    advanced_states = tuple(
        _advance_moving_guard(level, index, guard_state)
        for index, guard_state in enumerate(after_agent.moving_guards)
    )

    # Monta a situação completa depois do movimento dos guardas
    next_state = State(
        position=destination,
        active_guards=active_guards,
        moving_guards=advanced_states,
        briefcase_collected=briefcase_collected,
    )

    # Impede que um guarda móvel termine o turno no mesmo nó do agente (sem arbusto)
    for index, guard_state in enumerate(next_state.moving_guards):
        if not guard_state.active:
            continue
        if (
            _moving_guard_position(level, index, guard_state) == destination
            and destination not in level.hiding_nodes
        ):
            return None

    # última checagem com os guardas móveis nas posições novas (arbusto)
    if destination not in level.hiding_nodes:
        for index, guard_state in enumerate(next_state.moving_guards):
            if not guard_state.active:
                continue
            if _moving_guard_front(level, index, guard_state) == destination:
                return None

    # Se passou por tudo -> movimento é válido
    return next_state


# Testa as saídas possíveis a partir da posição atual do agente
# Só entrega os movimentos válidos e considera cada passo com custo 1
def successors(level: Level, state: State) -> Iterable[tuple[str, State, int]]:
    for destination in level.graph[state.position]:
        next_state = apply_move(level, state, destination)
        if next_state is None:
            continue
        yield destination, next_state, 1


# Calcula a menor distância em passos entre nós
# busca simples sem considerar guardas
# cache guarda resultados anteriores para não refazer a mesma conta
@lru_cache(maxsize=None)
def _distances_from(
    graph_items: tuple[tuple[str, tuple[str, ...]], ...],
    source: str,
) -> dict[str, int]:
    # Começa pela origem (0)
    # fila guarda quais nós ainda precisam ser examinados
    graph = dict(graph_items)
    distance = {source: 0}
    queue = deque([source])

    # Visita os vizinhos e registra a distância quando encontra nó pela primeira vez
    # acha os caminhos mais curtos
    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

    return distance


# Organiza as conexões do mapa e distâncias a partir de um nó
# A* usa esses valores como base pra heurística
def relaxed_distances(level: Level, source: str) -> dict[str, int]:
    graph_items = tuple(
        sorted((node, tuple(neighbors)) for node, neighbors in level.graph.items())
    )
    return _distances_from(graph_items, source)
