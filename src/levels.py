from __future__ import annotations

from .models import Level, MovingGuard


PHASE_1_3 = Level(
    name="Capítulo 1 - Fase 3",
    graph={
        "N0": ("N1",),
        "N1": ("N0", "N2", "N6"),
        "N2": ("N1", "N3", "N5", "N7"),
        "N3": ("N2", "N4"),
        "N4": ("N3", "N5"),
        "N5": ("N2", "N4", "N6"),
        "N6": ("N1", "N5"),
        "N7": ("N2",),
    },
    start="N0",
    goal="N7",
    guards={
        "N3": "N2",
    },
)


PHASE_1_4 = Level(
    name="Capítulo 1 - Fase 4",
    graph={
        "N0": ("N1", "N4"),
        "N1": ("N0", "N2", "N5"),
        "N2": ("N1", "N3"),
        "N3": ("N2", "N7"),
        "N4": ("N0", "N5", "N9"),
        "N5": ("N1", "N4", "N6", "N10"),
        "N6": ("N5", "N11"),
        "N7": ("N3", "N8", "N12"),
        "N8": ("N7", "N13"),
        "N9": ("N4", "N10", "N14"),
        "N10": ("N5", "N9", "N11", "N15"),
        "N11": ("N6", "N10", "N12", "N16"),
        "N12": ("N7", "N11", "N17"),
        "N13": ("N8",),
        "N14": ("N9", "N15"),
        "N15": ("N10", "N14", "N16"),
        "N16": ("N11", "N15", "N17"),
        "N17": ("N12", "N16"),
    },
    start="N0",
    goal="N13",
    guards={
        "N3": "N7",
        "N5": "N1",
        "N6": "N5",
        "N10": "N5",
        "N11": "N10",
        "N12": "N11",
        "N14": "N15",
    },
)


# Fase 1-12
#
# Numeração fornecida a partir do tabuleiro: N0 é o início, N14 é a saída,
# N13 contém a maleta e N5/N9 são arbustos. Os dois guardas amarelos
# patrulham as rotas lineares informadas e se movem depois do agente.
PHASE_1_12 = Level(
    name="Capítulo 1 - Fase 12",
    graph={
        "N0": ("N1", "N5"),
        "N1": ("N0", "N4"),
        "N2": ("N7",),
        "N3": ("N14", "N8"),
        "N4": ("N1", "N5"),
        "N5": ("N4", "N6", "N0"),
        "N6": ("N5", "N11"),
        "N7": ("N2", "N12"),
        "N8": ("N9", "N3"),
        "N9": ("N8", "N10"),
        "N10": ("N9", "N11"),
        "N11": ("N10", "N6", "N12"),
        # A conexão N11-N12 aparece no tabuleiro; foi incluída nos dois sentidos.
        "N12": ("N7", "N11", "N13"),
        "N13": ("N12",),
        "N14": ("N3",),
    },
    start="N0",
    goal="N14",
    guards={},
    moving_guards=(
        MovingGuard(
            name="amarelo_N4",
            route=("N4", "N5", "N6"),
            start_index=0,
            start_direction=1,
        ),
        MovingGuard(
            name="amarelo_N12",
            route=("N8", "N9", "N10", "N11", "N12"),
            start_index=4,
            start_direction=-1,
        ),
    ),
    hiding_nodes=frozenset({"N5", "N9"}),
    briefcase="N13",
)


# Fase 1-15
#
# N0 é o início, N22 é a saída, N12 contém a maleta e N9 é arbusto.
# Os guardas azuis são estáticos. Os amarelos usam posição e direção iniciais
# observadas no tabuleiro e patrulham as rotas fornecidas pelo usuário.
PHASE_1_15 = Level(
    name="Capítulo 1 - Fase 15",
    graph={
        "N0": ("N1", "N2"),
        "N1": ("N0", "N4"),
        "N2": ("N0", "N6"),
        "N3": ("N8",),
        "N4": ("N1", "N5", "N9"),
        "N5": ("N6", "N4"),
        "N6": ("N5", "N7", "N2"),
        "N7": ("N6", "N12"),
        "N8": ("N3", "N9", "N13"),
        "N9": ("N4", "N8", "N10", "N14"),
        "N10": ("N9", "N11"),
        "N11": ("N10", "N16"),
        "N12": ("N7", "N17"),
        "N13": ("N8", "N14", "N22"),
        "N14": ("N13", "N15", "N9", "N18"),
        "N15": ("N19", "N14", "N16"),
        "N16": ("N15", "N17", "N11"),
        "N17": ("N16", "N12", "N21"),
        "N18": ("N14", "N19"),
        "N19": ("N18", "N20", "N15"),
        "N20": ("N19", "N21"),
        "N21": ("N17", "N20"),
        "N22": ("N13",),
    },
    start="N0",
    goal="N22",
    guards={
        "N8": "N13",
        "N11": "N16",
        "N18": "N14",
    },
    moving_guards=(
        MovingGuard(
            name="amarelo_N8",
            route=("N3", "N8", "N13", "N22"),
            start_index=1,
            start_direction=-1,  # olhando para N3
        ),
        MovingGuard(
            name="amarelo_N6",
            route=("N4", "N5", "N6", "N7"),
            start_index=2,
            start_direction=-1,  # olhando para N5
        ),
        MovingGuard(
            name="amarelo_N14",
            route=("N13", "N14", "N15", "N16", "N17"),
            start_index=1,
            start_direction=1,   # olhando para N15
        ),
        MovingGuard(
            name="amarelo_N19",
            route=("N18", "N19", "N20", "N21"),
            start_index=1,
            start_direction=-1,  # olhando para N18
        ),
    ),
    hiding_nodes=frozenset({"N9"}),
    briefcase="N12",
)


LEVELS = {
    "1-3": PHASE_1_3,
    "1-4": PHASE_1_4,
    "1-12": PHASE_1_12,
    "1-15": PHASE_1_15,
}


# Três grupos experimentais definidos para o trabalho.
TEST_CASES = {
    "1": (
        ("1-3", False),
        ("1-4", False),
    ),
    "2": (
        ("1-12", False),
        ("1-15", False),
    ),
    "3": (
        ("1-12", True),
        ("1-15", True),
    ),
}
