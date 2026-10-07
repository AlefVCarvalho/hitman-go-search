# Jogo Hitman GO - Comparação de resultados busca cega e informada

Projeto desenvolvido para a disciplina de **Inteligência Artificial**, com o objetivo de modelar um problema por meio de um espaço de estados e comparar uma estratégia de **busca cega** com uma estratégia de **busca informada**.

O domínio escolhido é inspirado em **Hitman GO**. O cenário é representado como um grafo no qual o agente parte de uma posição inicial e deve alcançar um ponto objetivo, interagindo com guardas segundo as regras do ambiente.

## Objetivo do problema

Encontrar uma sequência válida de movimentos que leve o agente da posição inicial até o objetivo final com o menor número de turnos possível.

Nas fases que possuem maleta, o experimento também pode exigir que a maleta seja coletada antes da conclusão.

Cada movimento entre dois nós adjacentes possui custo `1`.

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

## Regras implementadas

### Guardas estáticos

Guardas azuis permanecem no mesmo nó e possuem uma direção de observação. Uma aproximação frontal causa derrota; uma aproximação válida pelas costas ou lateral elimina o guarda.

### Guardas móveis

Guardas amarelos possuem uma rota linear. A cada turno eles:

1. avançam uma posição;
2. invertem o sentido ao atingir uma extremidade;
3. mantêm uma direção frontal de observação.

A atualização da patrulha e o movimento do agente são resolvidos de forma determinística pelo simulador.

### Arbustos

Alguns nós representam arbustos. Neles, o agente não é detectado pelo campo de visão frontal dos guardas.

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
| `1-12` | Guardas móveis, arbustos, maleta e objetivo final |
| `1-15` | Guardas estáticos e móveis, arbusto, maleta e objetivo final |

## Casos experimentais

Para a avaliação foram organizados três grupos com dificuldade crescente:

### Teste 1 — guardas estáticos

- fase `1-3`;
- fase `1-4`;
- sucesso ao alcançar o objetivo final.

```bash
python -m src.main --test 1
```

### Teste 2 — guardas móveis

- fase `1-12`;
- fase `1-15`;
- sucesso ao alcançar o objetivo final;
- a coleta da maleta não é obrigatória.

```bash
python -m src.main --test 2
```

### Teste 3 — guardas móveis + maleta obrigatória

- fase `1-12`;
- fase `1-15`;
- o agente deve coletar a maleta e depois alcançar o objetivo final.

```bash
python -m src.main --test 3
```

Esse agrupamento permite aumentar gradualmente a quantidade de informação do estado e a quantidade de restrições consideradas durante a busca.

## Estrutura do projeto

```text
hitman-go-search/
├── src/
│   ├── __init__.py
│   ├── levels.py       # grafos, guardas, maletas e grupos experimentais
│   ├── main.py         # execução pelo terminal
│   ├── models.py       # estruturas de Level, State e guardas móveis
│   ├── problem.py      # regras, transições e heurística
│   └── search.py       # BFS e A*
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

### Executar apenas BFS

```bash
python -m src.main --level 1-15 --algorithm bfs
```

### Executar apenas A*

```bash
python -m src.main --level 1-15 --algorithm astar
```

## Métricas exibidas

Para cada execução são mostrados:

- solução encontrada;
- custo da solução;
- sequência de nós;
- estados expandidos;
- estados gerados;
- pico da fronteira;
- tempo de execução.

Essas informações serão usadas posteriormente para comparar o comportamento da BFS e do A* conforme o espaço de estados aumenta.

## Observação sobre fidelidade ao jogo

O objetivo deste projeto é estudar **algoritmos de busca**, e não reproduzir integralmente Hitman GO. As fases usam a topologia e as mecânicas relevantes observadas nos layouts, mas alguns detalhes de resolução de turnos são abstrações determinísticas do simulador. Isso mantém o ambiente controlado e permite aplicar exatamente o mesmo problema à BFS e ao A*.
