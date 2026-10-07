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
# A numeração acompanha a topologia do print estudado. N0 é o início,
# N13 é a saída, N8 contém a maleta e N2/N10 são arbustos.
# Os guardas amarelos patrulham linhas retas e invertem a direção nas pontas.
PHASE_1_12 = Level(
    name="Capítulo 1 - Fase 12",
    graph={
        "N0": ("N1", "N2"),
        "N1": ("N0", "N14"),
        "N2": ("N0", "N3", "N9", "N14"),
        "N3": ("N2", "N4", "N6"),
        "N4": ("N3", "N5", "N9"),
        "N5": ("N4", "N6", "N8"),
        "N6": ("N3", "N5", "N7"),
        "N7": ("N6",),
        "N8": ("N5",),
        "N9": ("N2", "N4", "N10"),
        "N10": ("N9", "N11", "N14"),
        "N11": ("N10", "N12"),
        "N12": ("N11", "N13", "N14"),
        "N13": ("N12",),
        "N14": ("N1", "N2", "N10", "N12"),
    },
    start="N0",
    goal="N13",
    guards={},
    moving_guards=(
        MovingGuard(
            name="amarelo_esquerda",
            route=("N1", "N14", "N10"),
            start_index=1,
            start_direction=1,
        ),
        MovingGuard(
            name="amarelo_direita",
            route=("N8", "N5", "N6", "N7"),
            start_index=1,
            start_direction=1,
        ),
    ),
    hiding_nodes=frozenset({"N2", "N10"}),
    briefcase="N8",
)


# Fase 1-15
#
# Esta fase combina guardas azuis estáticos, quatro guardas amarelos móveis,
# um arbusto, uma maleta e o alvo vermelho como estado objetivo.
PHASE_1_15 = Level(
    name="Capítulo 1 - Fase 15",
    graph={
        "N0": ("N1", "N5"),
        "N1": ("N0", "N2"),
        "N2": ("N1", "N3", "N11"),
        "N3": ("N2", "N4"),
        "N4": ("N3", "N5", "N6"),
        "N5": ("N0", "N4"),
        "N6": ("N4", "N7"),
        "N7": ("N6", "N15"),
        "N8": ("N9",),
        "N9": ("N8", "N10", "N11", "N22"),
        "N10": ("N9",),
        "N11": ("N2", "N9", "N12"),
        "N12": ("N11", "N13"),
        "N13": ("N12", "N14"),
        "N14": ("N13", "N15", "N21"),
        "N15": ("N7", "N14", "N16"),
        "N16": ("N15", "N17"),
        "N17": ("N16", "N18"),
        "N18": ("N17", "N19", "N21"),
        "N19": ("N18", "N20"),
        "N20": ("N19", "N21", "N22"),
        "N21": ("N14", "N18", "N20"),
        "N22": ("N9", "N20", "N23"),
        "N23": ("N22",),
    },
    start="N0",
    goal="N23",
    guards={
        "N10": None,
        "N13": "N12",
        "N19": "N18",
    },
    moving_guards=(
        MovingGuard(
            name="amarelo_superior",
            route=("N18", "N17", "N16"),
            start_index=0,
            start_direction=1,
        ),
        MovingGuard(
            name="amarelo_sala_superior",
            route=("N20", "N21", "N14", "N15"),
            start_index=0,
            start_direction=1,
        ),
        MovingGuard(
            name="amarelo_corredor_central",
            route=("N9", "N11", "N12"),
            start_index=0,
            start_direction=1,
        ),
        MovingGuard(
            name="amarelo_corredor_inferior",
            route=("N2", "N3", "N4", "N6"),
            start_index=2,
            start_direction=1,
        ),
    ),
    hiding_nodes=frozenset({"N11"}),
    briefcase="N7",
)


LEVELS = {
    "1-3": PHASE_1_3,
    "1-4": PHASE_1_4,
    "1-12": PHASE_1_12,
    "1-15": PHASE_1_15,
}


# Os três grupos experimentais definidos para o trabalho.
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
