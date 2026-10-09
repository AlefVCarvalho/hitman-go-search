# Jogo Hitman GO - Comparação de resultados busca cega e informada

Projeto desenvolvido para a disciplina de **Inteligência Artificial**, com o objetivo de modelar um problema por meio de um espaço de estados e comparar uma estratégia de **busca cega** com uma estratégia de **busca informada**.

O domínio escolhido é inspirado em **Hitman GO**. O cenário é representado como um grafo no qual o agente parte de uma posição inicial e deve alcançar um ponto objetivo, interagindo com guardas segundo as regras do ambiente.

## Sumário

- [Objetivo do problema](#objetivo-do-problema)
- [Classificação do problema](#classificação-do-problema)
- [Modelagem](#modelagem)
- [Regras implementadas](#regras-implementadas)
- [Estratégias de busca](#estratégias-de-busca)
  - [BFS](#bfs)
  - [A*](#a)
- [Casos experimentais](#casos-experimentais)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como executar](#como-executar)
- [Métricas exibidas](#métricas-exibidas)
- [Observação sobre fidelidade ao jogo](#observação-sobre-fidelidade-ao-jogo)

## Objetivo do problema

Encontrar uma sequência válida de movimentos que leve o agente da posição inicial até o objetivo final com o menor número de turnos possível.

Nas fases em que o experimento exige a maleta, ela deve ser coletada antes da conclusão da fase.

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

A modelagem separa os dados fixos de cada fase das informações que mudam durante a busca.

### Mapa

> **`G = (V, E)`** — `V` representa o conjunto de posições válidas do tabuleiro e `E` representa as conexões que permitem o deslocamento entre duas posições.

O grafo, as rotas dos guardas, os arbustos, a posição da maleta e o objetivo são dados fixos da fase e não são duplicados em cada estado da busca.

### Estado

> **`s = (p, Ge, Gm, b)`** — `p` é a posição atual do agente; `Ge` representa os guardas estáticos ainda ativos; `Gm` representa a configuração dos guardas móveis, incluindo posição, direção e situação; `b` indica se a maleta já foi coletada.

O estado inicial é construído com o agente no nó inicial da fase, todos os guardas ativos em suas configurações iniciais e a maleta ainda não coletada.

### Operadores e custo

> **`mover(p, q)`**, com **`q ∈ Adj(p)`** — o agente pode mover-se de `p` para qualquer nó adjacente `q`, desde que a transição resulte em um estado válido segundo as regras do ambiente.
>
> **`c(p, q) = 1`** — cada movimento realizado pelo agente corresponde a um turno e possui custo unitário.

### Estado objetivo

> **Modo normal:** `objetivo(s) ⇔ p = goal`
>
> **Modo com maleta:** `objetivo(s) ⇔ (p = goal) ∧ (b = verdadeiro)`

Assim, o custo de uma solução corresponde ao número total de movimentos do agente até atingir um estado objetivo válido.

## Regras implementadas

### Ordem de um turno

1. O agente escolhe e executa um movimento para um nó adjacente.
2. São resolvidos encontros e campos de visão relacionados à nova posição do agente.
3. Os guardas amarelos ativos realizam seu movimento de patrulha.
4. São verificadas novamente colisões e situações de detecção após o movimento dos guardas.
5. O estado resultante é utilizado como sucessor na busca.

### Guardas estáticos

Os guardas azuis permanecem no mesmo nó e possuem uma direção de observação. Entrar frontalmente em sua área de ataque causa derrota. Uma aproximação válida pelas costas ou lateral elimina o guarda, que deixa de fazer parte dos estados seguintes.

### Guardas móveis

Os guardas amarelos patrulham uma rota linear conhecida. Após o movimento do agente, cada guarda amarelo ativo avança uma posição em sua rota. Ao chegar a uma extremidade, ele inverte a direção imediatamente e continua a patrulha no turno seguinte, sem gastar um turno apenas para virar.

A direção da patrulha também determina a orientação frontal utilizada nas interações com o agente. Um guarda móvel pode ser eliminado quando a aproximação é válida e deixa de se mover nos estados seguintes.

### Arbustos

Alguns nós representam arbustos. Quando o agente está escondido em um desses nós, não é detectado pelo campo de visão frontal e um guarda móvel pode atravessar a mesma posição sem capturá-lo.

### Maleta

A maleta é coletada automaticamente quando o agente visita o nó em que ela está localizada. A coleta altera o estado e permanece registrada nos estados seguintes.

No modo padrão, a busca termina ao alcançar a saída. Quando a opção `--briefcase` está ativa, a saída somente é aceita como estado objetivo se a maleta já tiver sido coletada.

## Estratégias de busca

As duas estratégias utilizam exatamente a mesma modelagem, regras de transição e casos experimentais. A diferença está apenas na forma como escolhem qual estado explorar a seguir.

### BFS

A **Breadth-First Search (BFS)** é utilizada como estratégia de busca não informada. Ela mantém uma fila FIFO e expande os estados em níveis crescentes de profundidade.

Como todas as ações possuem custo `1`, o primeiro estado objetivo encontrado pela BFS corresponde a uma solução de custo mínimo.

### A*

O **A\*** utiliza uma função de avaliação que combina o custo já percorrido com uma estimativa do custo restante:

> **`f(n) = g(n) + h(n)`** — `g(n)` é o número de movimentos realizados desde o estado inicial até `n`; `h(n)` estima quantos movimentos ainda são necessários para alcançar o objetivo.

A heurística utiliza as menores distâncias no grafo da fase, desconsiderando os guardas e demais restrições dinâmicas.

> **Sem maleta obrigatória ou após a coleta:** `h(n) = d(p, goal)` — `d(p, goal)` é a menor distância entre a posição atual `p` e a saída.
>
> **Com maleta obrigatória ainda não coletada:** `h(n) = d(p, m) + d(m, goal)` — `m` é o nó da maleta; a estimativa considera o menor caminho até ela e, em seguida, até a saída.

Ao ignorar os guardas, a heurística resolve uma versão relaxada do problema. Ela não acrescenta desvios causados pelas ameaças do ambiente e, portanto, fornece uma estimativa otimista do custo restante. Para esta modelagem com custos unitários, a heurística é admissível e consistente.

## Casos experimentais

Os quatro níveis modelados são distribuídos em três grupos de teste com dificuldade crescente. As mesmas instâncias são executadas com BFS e A* para permitir uma comparação direta.

| Teste | Fases | Elementos principais | Critério de sucesso |
|---|---|---|---|
| **1** | `1-3` e `1-4` | Guardas estáticos | Alcançar a saída |
| **2** | `1-12` e `1-15` | Guardas móveis, guardas estáticos e arbustos | Alcançar a saída |
| **3** | `1-12` e `1-15` | Mesmas mecânicas do Teste 2 + maleta obrigatória | Coletar a maleta e alcançar a saída |

### Teste 1 — guardas estáticos

```bash
python -m src.main --test 1
```

### Teste 2 — guardas móveis

```bash
python -m src.main --test 2
```

### Teste 3 — guardas móveis + maleta obrigatória

```bash
python -m src.main --test 3
```

Essa organização aumenta gradualmente a quantidade de informação armazenada no estado e as restrições que precisam ser consideradas durante a busca.

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
- sequência de nós percorridos;
- estados expandidos;
- estados gerados;
- pico da fronteira;
- tempo de execução.

Exemplo de saída para a fase `1-12` utilizando A*:

```text
Algoritmo: A*
Objetivo: objetivo final
Solução encontrada: sim
Custo: 16
Caminho: N0 -> N5 -> N4 -> N5 -> N6 -> N11 -> N12 -> N7 -> N2 -> N7 -> N12 -> N11 -> N10 -> N9 -> N8 -> N3 -> N14
Estados expandidos: 28
Estados gerados: 36
Pico da fronteira: 9
Tempo: 0.00035316 s
```

O tempo exibido varia de acordo com a máquina e a execução. As demais métricas permitem comparar diretamente quanto do espaço de estados foi explorado por cada estratégia.

## Observação sobre fidelidade ao jogo

O objetivo deste projeto é estudar **algoritmos de busca**, e não reproduzir integralmente Hitman GO. Os níveis utilizados preservam a topologia e as mecânicas relevantes para os experimentos, validadas por comparação com o funcionamento observado no jogo.

Elementos que não interferem no problema de busca estudado foram deixados de fora para manter o ambiente determinístico, controlado e adequado à comparação entre BFS e A*.
