# Jogo Hitman GO - Comparação de resultados busca cega e informada

Projeto desenvolvido para a disciplina de **Inteligência Artificial**, com o objetivo de modelar um problema por meio de um espaço de estados e comparar uma estratégia de **busca cega** com uma estratégia de **busca informada**.

O domínio escolhido é inspirado em **Hitman GO**. O cenário é representado como um grafo no qual o agente parte de uma posição inicial e deve alcançar um ponto objetivo, interagindo com guardas segundo as regras do ambiente.

## Sumário

- [Objetivo do problema](#objetivo-do-problema)
- [Classificação do problema](#classificação-do-problema)
- [Modelagem](#modelagem)
- [Regras implementadas](#regras-implementadas)
- [Estratégias de busca](#estratégias-de-busca)
- [Fases modeladas](#fases-modeladas)
- [Casos experimentais](#casos-experimentais)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como executar](#como-executar)
- [Métricas exibidas](#métricas-exibidas)
- [Observação sobre fidelidade ao jogo](#observação-sobre-fidelidade-ao-jogo)

## Objetivo do problema

Encontrar uma sequência válida de movimentos que leve o agente da posição inicial até o objetivo final com o menor número de turnos possível.

Nas fases que possuem maleta, o experimento também pode exigir que a maleta seja coletada antes da conclusão.

Cada movimento entre dois nós adjacentes possui custo `1`.

<img width="780" height="533" alt="image" src="https://github.com/user-attachments/assets/6bcdd2c5-13c5-414e-9ea6-1345628a2fe9" />

_“Exemplo de fase utilizada como problema de busca”_

## Classificação do problema

| Característica | Classificação |
|---|---|
| Número de agentes | Agente único |
| Temporalidade | Sequencial |
| Observabilidade | Totalmente observável |
| Determinismo | Determinístico |
| Natureza dos estados | Discreta |
| Natureza das ações | Discreta |
| Espaço de estados | Finito |
| Conhecimento do ambiente | Conhecido |
| Custo das ações | Uniforme |
| Objetivo | Estado objetivo explícito |
| Problema de otimização | Menor caminho válido no espaço de estados |

Os guardas não são tratados como agentes adversariais independentes. Eles fazem parte do ambiente e seguem regras determinísticas.

## Modelagem

O mapa de cada fase é representado por um grafo:

```text
G = (V, E)
```

- `V`: posições válidas do tabuleiro;
- `E`: caminhos permitidos entre duas posições.

Com a inclusão dos guardas móveis e da maleta, o estado pode ser resumido como:

```text
s = (p, Ge, Gm, b)
```

onde:

- `p`: posição atual do agente;
- `Ge`: configuração dos guardas estáticos ainda ativos;
- `Gm`: posição, sentido e situação dos guardas móveis;
- `b`: indica se a maleta já foi coletada.

As rotas completas dos guardas e o grafo da fase são dados fixos e **não são duplicados em cada estado**.

<img width="500" height="500" alt="6bb6ad42-13aa-4291-b0f5-140afe9a3bcb" src="https://github.com/user-attachments/assets/34350b2c-1e25-48e1-9fff-150271aa2d2e" />

_“Exemplo da numeração utilizada na transcrição da fase”_

## Regras implementadas

### Guardas estáticos

Guardas azuis permanecem no mesmo nó e possuem uma direção de observação. Uma aproximação frontal causa derrota; uma aproximação válida pelas costas ou lateral elimina o guarda.

### Guardas móveis

Guardas amarelos possuem uma rota linear. Em cada turno cada guarda amarelo ativo avança uma posição. Ao atingir uma extremidade da rota, o guarda inverte o sentido.

A orientação frontal acompanha o sentido da patrulha e é usada nas interações com o agente.

### Arbustos

Alguns nós representam arbustos. Neles, o agente não é detectado pelo campo de visão frontal dos guardas e um guarda móvel pode atravessar o mesmo nó sem detectar o agente escondido.

### Maleta

A maleta é coletada automaticamente quando o agente visita seu nó.

No modo normal, basta alcançar o objetivo final. No modo `--briefcase`, o estado objetivo exige que a maleta seja coletada antes do agente chegar à saída.

## Estratégias de busca

### BFS

A **Breadth-First Search** é a estratégia não informada. Como todas as ações possuem custo unitário, a primeira solução encontrada possui custo mínimo dentro da modelagem utilizada.

### A*

O A* utiliza:

```text
f(n) = g(n) + h(n)
```

- `g(n)`: quantidade de movimentos realizados;
- `h(n)`: estimativa do custo restante.

Sem exigência de maleta:

```text
h(n) = distância(posição, objetivo)
```

Com maleta obrigatória ainda não coletada:

```text
h(n) = distância(posição, maleta) + distância(maleta, objetivo)
```

As distâncias são calculadas no grafo ignorando os guardas. Dessa forma, a heurística trabalha sobre uma versão relaxada do problema.

## Fases modeladas

| Fase | Elementos principais |
|---|---|
| `1-3` | Guarda estático e objetivo final |
| `1-4` | Vários guardas estáticos e maior quantidade de caminhos |
| `1-12` | 2 guardas móveis, arbustos, maleta e saída |
| `1-15` | 3 guardas estáticos, 4 móveis, arbusto, maleta e saída |

## Casos experimentais

Para a avaliação foram organizados três grupos com dificuldade crescente:

### Teste 1 — guardas estáticos

- fase `1-3`;
- fase `1-4`;
- sucesso ao alcançar o objetivo final.

Execute as fases:

```bash
python -m src.main --level 1-3
python -m src.main --level 1-4
```

### Teste 2 — guardas móveis

- fase `1-12`;
- fase `1-15`;
- sucesso ao alcançar o objetivo final;
- a coleta da maleta não é obrigatória.

Execute as fases sem exigir a maleta:

```bash
python -m src.main --level 1-12
python -m src.main --level 1-15
```

### Teste 3 — guardas móveis + maleta obrigatória

- fase `1-12`;
- fase `1-15`;
- o agente deve coletar a maleta e depois alcançar o objetivo final.

Execute as mesmas fases com a maleta obrigatória:

```bash
python -m src.main --level 1-12 --briefcase
python -m src.main --level 1-15 --briefcase
```

Esse agrupamento permite aumentar gradualmente a quantidade de informação do estado e a quantidade de restrições consideradas durante a busca.

## Estrutura do projeto

```text
hitman-go-search/
├── src/
│   ├── __init__.py
│   ├── levels.py       # grafos, guardas, maletas e configurações das fases
│   ├── main.py         # execução e argumentos do terminal
│   ├── models.py       # estruturas de Level, State e guardas móveis
│   ├── output.py       # formatação das saídas e visualização passo a passo
│   ├── problem.py      # regras e transições do ambiente
│   └── search.py       # BFS, A* e heurística
├── .gitignore
└── README.md
```

## Como executar

A partir da raiz do projeto:

```bash
python -m src.main
```

### Escolher uma fase

```bash
python -m src.main --level 1-12
```

### Exigir a coleta da maleta

```bash
python -m src.main --level 1-12 --briefcase
```

### Visualizar a BFS passo a passo

```bash
python -m src.main --level 1-12 --bfs-step
```

Nesse modo, somente a BFS é executada. O terminal apresenta progressivamente a posição atual, a profundidade, as posições visitadas e os estados presentes na fronteira.

### Visualizar o A* passo a passo

```bash
python -m src.main --level 1-12 --astar-step
```

Nesse modo, somente o A* é executado. Além das posições visitadas e da fronteira, são apresentados os valores utilizados na avaliação do estado:

```text
f = x / g = x / h = x
```

Os modos passo a passo também podem ser combinados com a exigência da maleta:

```bash
python -m src.main --level 1-15 --briefcase --bfs-step
python -m src.main --level 1-15 --briefcase --astar-step
```

<img width="960" height="545" alt="image" src="https://github.com/user-attachments/assets/ce30906e-3991-4d98-a891-fc724d94ff98" />

_"Exemplo de prompt no terminal para executar a fase 1-15"_

## Métricas exibidas

Na execução padrão, BFS e A* são aplicados sobre a mesma fase. São mostrados os caminhos encontrados em forma de setas e uma tabela comparativa com:

- custo da solução em número de movimentos;
- estados gerados;
- estados explorados;
- pico da fronteira;
- tempo de execução.

O tempo pode variar entre execuções conforme o ambiente de execução.

Os comandos `--bfs-step` e `--astar-step` possuem finalidade demonstrativa. Nesses modos apenas a busca selecionada é executada e seu processo é exibido passo a passo, sem a tabela de comparação entre os algoritmos.

## Observação sobre fidelidade ao jogo

O objetivo deste projeto é estudar **algoritmos de busca**, e não reproduzir integralmente Hitman GO. As fases usam a topologia e as mecânicas relevantes observadas nos layouts, mas alguns detalhes de resolução de turnos são abstrações determinísticas do simulador. Isso mantém o ambiente controlado e permite aplicar exatamente o mesmo problema à BFS e ao A*.
