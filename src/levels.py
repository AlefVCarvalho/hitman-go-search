# Fases que podem ser escolhidas no terminal
# Cada fase informa o caminho possível entre os nós e onde ficam:
# agente, saída, guardas e outros elementos do mapa
from __future__ import annotations

from .models import Level, MovingGuard


# Fase 1-3: mapa pequeno, com 1 guarda fixo
PHASE_1_3 = Level(
    name="Capítulo 1 - Fase 3",

    graph={
        "N0": ("N2",),
        "N1": ("N2", "N5"),
        "N2": ("N0", "N1", "N3", "N6"),
        "N3": ("N2", "N4", "N7"),
        "N4": ("N3",),
        "N5": ("N1", "N6"),
        "N6": ("N2", "N5", "N7"),
        "N7": ("N3", "N6"),
    },

    start="N4",
    goal="N0",

    guards={
        "N1": "N2",
    },
)


# Fase 1-4: mapa maior, com vários guardas parados
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


# Fase 1-12: guardas moveis, arbustos e maleta (opcional na fase)
PHASE_1_12 = Level(
    name="Capítulo 1 - Fase 12",

    graph={
        "N0": ("N5",),
        "N1": ("N2", "N6"),
        "N2": ("N1", "N3"),
        "N3": ("N2", "N4"),
        "N4": ("N3", "N5", "N9"),
        "N5": ("N0", "N4", "N10"),
        "N6": ("N1", "N11"),
        "N7": ("N8", "N12"),
        "N8": ("N7", "N9", "N13"),
        "N9": ("N4", "N8"),
        "N10": ("N5", "N14"),
        "N11": ("N6",),
        "N12": ("N7", "N13"),
        "N13": ("N8", "N12"),
        "N14": ("N10",),
    },

    start="N13",
    goal="N11",

    guards={},

    moving_guards=(
        MovingGuard(
            name="amarelo_N7",
            route=("N7", "N8", "N9"),
            start_index=0,
            start_direction=1,
        ),
        MovingGuard(
            name="amarelo_N5",
            route=("N1", "N2", "N3", "N4", "N5"),
            start_index=4,
            start_direction=-1,
        ),
    ),

    hiding_nodes=frozenset({"N2", "N8"}),

    briefcase="N0",
)


# Fase 1-15: guardas fixos e móveis, arbusto e maleta
PHASE_1_15 = Level(
    name="Capítulo 1 - Fase 15",

    graph={
        "N0": ("N5",),
        "N1": ("N2", "N6"),
        "N2": ("N1", "N3", "N7"),
        "N3": ("N2", "N4"),
        "N4": ("N3", "N9"),
        "N5": ("N0", "N6", "N10"),
        "N6": ("N1", "N5", "N7", "N11"),
        "N7": ("N2", "N6", "N8"),
        "N8": ("N7", "N9", "N13"),
        "N9": ("N4", "N8", "N14"),
        "N10": ("N5", "N11", "N15"),
        "N11": ("N6", "N10", "N12", "N16"),
        "N12": ("N11", "N13"),
        "N13": ("N8", "N12"),
        "N14": ("N9", "N19"),
        "N15": ("N10",),
        "N16": ("N11", "N17", "N20"),
        "N17": ("N16", "N18"),
        "N18": ("N17", "N19", "N22"),
        "N19": ("N14", "N18"),
        "N20": ("N16", "N21"),
        "N21": ("N20", "N22"),
        "N22": ("N18", "N21"),
    },

    start="N21",
    goal="N0",

    guards={
        "N10": "N5",
        "N13": "N8",
        "N1": "N6",
    },

    moving_guards=(
        MovingGuard(
            name="amarelo_N10",
            route=("N15", "N10", "N5", "N0"),
            start_index=1,
            start_direction=-1,
        ),
        MovingGuard(
            name="amarelo_N18",
            route=("N16", "N17", "N18", "N19"),
            start_index=2,
            start_direction=-1,
        ),
        MovingGuard(
            name="amarelo_N6",
            route=("N5", "N6", "N7", "N8", "N9"),
            start_index=1,
            start_direction=1,
        ),
        MovingGuard(
            name="amarelo_N2",
            route=("N1", "N2", "N3", "N4"),
            start_index=1,
            start_direction=-1,
        ),
    ),

    hiding_nodes=frozenset({"N11"}),

    briefcase="N14",
)


# Liga o número digitado no terminal e configuração da fase
# encontra o mapa escolhido mais facil
LEVELS = {
    "1-3": PHASE_1_3,
    "1-4": PHASE_1_4,
    "1-12": PHASE_1_12,
    "1-15": PHASE_1_15,
}
