from __future__ import annotations

from .models import Level

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


LEVELS = {
    "1-3": PHASE_1_3,
    "1-4": PHASE_1_4,
}
# Caso experimental controlado para introduzir duas novas dinâmicas:
# - coleta obrigatória de maleta;
# - guarda amarelo que patrulha uma rota linear e se move a cada turno.
#
# O layout é próprio do projeto e não é apresentado como reprodução exata de
# uma fase específica de Hitman GO. As regras são inspiradas nas mecânicas do jogo.
from .models import MovingGuard

EXPERIMENTAL_MOVING_BRIEFCASE = Level(
    name="Caso experimental - Maleta e guarda móvel",
    graph={
        "N0": ("N1", "N4"),
        "N1": ("N0", "N2", "N4"),
        "N2": ("N1", "N3", "N5"),
        "N3": ("N2", "N6"),
        "N4": ("N0", "N1", "N5", "N7"),
        "N5": ("N2", "N4", "N6", "N8"),
        "N6": ("N3", "N5", "N9"),
        "N7": ("N4", "N8"),
        "N8": ("N5", "N7", "N9"),
        "N9": ("N6", "N8"),
    },
    start="N0",
    goal="N3",
    guards={},
    moving_guards=(
        MovingGuard(route=("N5", "N6", "N9"), start_index=0, start_direction=1),
    ),
    briefcase="N7",
    briefcase_required=True,
)

LEVELS["moving-briefcase"] = EXPERIMENTAL_MOVING_BRIEFCASE
