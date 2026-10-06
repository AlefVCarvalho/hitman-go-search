# Jogo Hitman GO - Comparação de resultados busca cega e informada

Projeto desenvolvido para a disciplina de **Inteligência Artificial**, com o objetivo de modelar um problema por meio de um espaço de estados e comparar uma estratégia de **busca cega** com uma estratégia de **busca informada**.

O domínio escolhido é inspirado em **Hitman GO**. O cenário é representado como um grafo no qual o agente parte de uma posição inicial e deve alcançar um ponto objetivo, interagindo com guardas segundo as regras do ambiente.

## Objetivo do problema

Encontrar uma sequência válida de movimentos que leve o agente do ponto inicial até o ponto de saída com o menor número de movimentos possível.

Cada deslocamento entre dois nós adjacentes possui custo unitário. O estado considera a posição atual do agente e a configuração dos guardas ainda presentes.

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


Embora existam guardas no cenário, eles não são tratados como agentes adversariais independentes. Nesta modelagem eles são elementos do ambiente submetidos a regras determinísticas.

## Especificação do problema

| Elemento | Especificação |
|---|---|
| Problema | Encontrar uma sequência de movimentos que leve o agente do ponto inicial até a saída sem violar as regras do ambiente. |
| Representação do mapa | Grafo `G = (V, E)`, em que cada nó representa uma posição válida e cada aresta representa um caminho permitido. |
| Estado | `s = (p, Ga)`, onde `p` é a posição do agente e `Ga` representa os guardas ainda ativos. |
| Estado inicial | Posição inicial do agente com todos os guardas da fase presentes. |
| Estado objetivo | Qualquer estado em que o agente esteja no nó de saída. |
| Operadores | Mover o agente para um nó adjacente conectado por uma aresta válida. |
| Pré-condição | Deve existir uma aresta entre o nó atual e o destino. |
| Efeito | O agente passa ao nó escolhido e o estado é atualizado conforme as regras de interação. |
| Custo do operador | `1` por movimento. |
| Custo da solução | Número total de movimentos até a saída. |
| Espaço de estados | Combinações alcançáveis entre posição do agente e configuração dos guardas. |
| Solução | Sequência ordenada de movimentos do estado inicial até um estado objetivo. |

## Estratégias de busca

### Busca em largura — BFS

A **Breadth-First Search (BFS)** é utilizada como estratégia de busca não informada. Como todas as ações possuem custo `1`, ela explora os estados por profundidade crescente e fornece uma solução de custo mínimo para a modelagem atual.

### A\*

A estratégia informada utiliza:

```text
f(n) = g(n) + h(n)
```

onde:

- `g(n)` é o custo acumulado desde o estado inicial;
- `h(n)` é a estimativa do custo restante até a saída.

Na versão inicial, `h(n)` é a **menor distância no grafo entre a posição atual e a saída, ignorando os guardas**. Essa distância é pré-calculada por BFS no problema relaxado.

## Fases iniciais

Foram incluídas duas fases simplificadas baseadas nos layouts estudados:

- `1-3`: caso inicial menor;
- `1-4`: caso com maior quantidade de nós, ciclos e guardas.

Um terceiro caso mais complexo deverá ser adicionado posteriormente, possivelmente envolvendo **maleta** e/ou **guardas móveis**.

## Estrutura do projeto

```text
hitman-go-search/
├── src/
│   ├── __init__.py
│   ├── levels.py       # grafos e configuração das fases
│   ├── main.py         # execução pelo terminal
│   ├── models.py       # State e Level
│   ├── problem.py      # operadores, transições e heurística relaxada
│   └── search.py       # BFS e A*
├── .gitignore
└── README.md
```

## Como executar

A partir da raiz do projeto:

```bash
python -m src.main
```

Por padrão, são executados BFS e A* na fase `1-3`.

### Escolher a fase

```bash
python -m src.main --level 1-4
```

### Executar apenas BFS

```bash
python -m src.main --level 1-3 --algorithm bfs
```

### Executar apenas A\*

```bash
python -m src.main --level 1-3 --algorithm astar
```

### Executar os dois algoritmos

```bash
python -m src.main --level 1-4 --algorithm both
```

## Saída atual

Para cada estratégia são exibidos:

- se uma solução foi encontrada;
- custo da solução;
- caminho encontrado;
- quantidade de estados expandidos;
- quantidade de estados gerados;
- maior tamanho observado da fronteira;
- tempo de execução.

Essas métricas servirão como base para a comparação experimental entre as duas estratégias.