# Bolsa do Açaí 🫐 — Árvores Rubro-Negra, 2-3-4 e k-D aplicadas à Feira do Açaí do Ver-o-Peso

Trabalho do 2º bimestre — Estruturas de Dados (árvores balanceadas).

**Equipe**
- Murilo Muniz Dias
- João Paulo Koury
- Lucas Pinto
- Pedro Antônio

---

## O problema

Toda madrugada os barcos das ilhas (Combu, Cotijuba, Igarapé-Miri, Abaetetuba, Cametá...)
descarregam açaí na Feira do Açaí, ao lado do Ver-o-Peso. Cada **lote** tem um **preço por rasa**,
e esse preço muda conforme os barcos chegam e os lotes são vendidos.

O comprador (batedor de açaí, dono de restaurante) precisa responder rápido:

| Pergunta do comprador | Operação na árvore |
|---|---|
| "Tem lote a R$ 245?" | **busca** |
| "Quais lotes cabem no meu orçamento, de R$ 170 a R$ 210?" | **busca por faixa** (percurso em ordem com poda) |
| "Qual o lote mais barato agora?" | mínimo (nó mais à esquerda) |
| "Chegou barco novo" | **inserção + balanceamento** |
| "Vendi um lote / acabou esse preço" | **exclusão + balanceamento** |
| "Qual a barraca mais próxima de mim?" | **árvore k-D** (vizinho mais próximo) |

Como os lotes entram e saem **a noite toda, em ordem imprevisível**, uma árvore de busca comum
pode degenerar numa lista. Por isso usamos árvores **auto-balanceadas** — e colocamos os
mesmos lotes em **duas árvores ao mesmo tempo** (Rubro-Negra e 2-3-4) para comparar os métodos
de balanceamento ao vivo.

## O que foi implementado (sem nenhuma biblioteca de árvore)

| Estrutura | Arquivo | Inserção + balanceamento | Exclusão + balanceamento | Busca |
|---|---|---|---|---|
| Rubro-Negra | `arvores/rubro_negra.py` | recoloração + rotações (casos 1, 2, 3) | duplo-preto (casos 1 a 4) | ✔ + faixa |
| 2-3-4 | `arvores/arvore234.py` | split top-down de 4-nós | empréstimo (rotação) / fusão top-down | ✔ + faixa |
| k-D (k=2) | `arvores/kd.py` | inserção alternando eixo x/y | — (só explicação/demonstração, como pedido) | vizinho mais próximo com poda |

- **Nós encadeados**: todo nó tem ponteiro para os filhos **e para o pai** (estilo lista duplamente
  encadeada). A Rubro-Negra usa um nó sentinela `NIL` preto, como no Cormen.
- **matplotlib** é usada apenas para **desenhar** as árvores (permitido: biblioteca de plotagem).
- **Pillow** (dependência do matplotlib) junta os quadros num GIF do passo a passo.
- Função extra `rubro_negra_para_234()`: mostra que **a Rubro-Negra É uma 2-3-4 disfarçada**
  (cada nó preto + seus filhos vermelhos = um nó 2-3-4).

### Política de elementos repetidos (exigida no enunciado)

A chave é o **preço da rasa (R$, inteiro)**. Vários lotes podem ter o mesmo preço.

> **Escolhemos "balde por nó" (multiconjunto):** cada nó (ou cada chave do nó 2-3-4) guarda uma
> **lista de lotes** com aquele preço.
> - **Inserir** um preço que já existe → o lote é **anexado ao balde**; nenhum nó novo é criado,
>   então **não há rebalanceamento** e a forma da árvore não muda.
> - **Remover** passando o ID do lote → tira só aquele lote do balde. O **nó só sai da árvore
>   (com rebalanceamento) quando o balde fica vazio**. Remover sem ID → remove o preço inteiro.
>
> Por quê? Colocar repetidos "sempre à direita" quebraria as rotações (um repetido poderia ir
> parar à esquerda depois de girar) e aumentaria a altura à toa. Com o balde, a altura depende só
> do número de **preços distintos**.

Nos desenhos, um `×3` ao lado do nó indica que o balde tem 3 lotes.

## Como executar

Requisitos: **Python 3.9+**

```bash
git clone https://github.com/murilomunizzdias/acai-arvores.git
cd acai-arvores
pip install -r requirements.txt
```

**Programa interativo (menu):**
```bash
python main.py
```
Carrega os 30 lotes de `dados/lotes_madrugada.csv` (23 preços distintos → **23 nós**, acima do
mínimo de 21) e abre o menu:

```
 1  Ver as duas árvores (figura)
 2  Chegou barco: inserir lote
 3  Vendeu: remover lote (um lote ou o preço inteiro)
 4  Buscar preço exato
 5  Orçamento: lotes entre R$ A e R$ B
 6  Lote mais barato / mais caro
 7  Equivalência: Rubro-Negra vista como 2-3-4
 8  Comparativo de balanceamento (rotações x splits)
 9  Verificar propriedades das árvores
10  Demonstração da árvore k-D (barraca mais próxima)
11  Modo passo a passo (gera um quadro + GIF por rotação/split/fusão)
```
Cada operação imprime **o que o algoritmo fez** (qual caso, qual rotação, qual split) nas duas árvores.
As figuras abrem numa janela e também são salvas em `saida/`.

**Roteiro da apresentação (gera todas as figuras e GIFs de uma vez):**
```bash
python demo_apresentacao.py
```
Saída em `saida/apresentacao/`.

**Teste de correção (45.000 operações aleatórias):**
```bash
python -m tests.testar_invariantes
```
Depois de **cada** inserção/remoção confere: raiz preta, sem vermelho-vermelho, mesma altura
negra, ponteiros de pai, ordem de busca (Rubro-Negra); 1 a 3 chaves por nó, todas as folhas no
mesmo nível, nº de filhos (2-3-4); e compara buscas e faixas com um dicionário.

## Estrutura

```
acai-arvores/
├── main.py                    # menu interativo
├── demo_apresentacao.py       # gera as figuras/GIFs usados nos slides
├── requirements.txt
├── dados/lotes_madrugada.csv  # 30 lotes, 23 preços distintos
├── arvores/
│   ├── lote.py                # registro Lote + leitura do CSV
│   ├── rubro_negra.py         # Rubro-Negra (nós com pai, sentinela NIL)
│   ├── arvore234.py           # 2-3-4 top-down + equivalência RN -> 2-3-4
│   ├── kd.py                  # árvore 2-D + vizinho mais próximo
│   └── visual.py              # desenho (matplotlib) + gravador de passos/GIF
└── tests/testar_invariantes.py
```

## Resumo dos balanceamentos

| | Rubro-Negra | 2-3-4 |
|---|---|---|
| Ideia | BST com 1 bit de cor por nó | nó com 1 a 3 chaves |
| Garante | caminho mais longo ≤ 2× o mais curto | todas as folhas no mesmo nível |
| Altura | ≤ 2·log₂(n+1) | ≤ log₂(n+1) |
| Inserção quebra regra quando | pai e filho vermelhos | nó passaria de 3 chaves |
| Conserta com | recolorir (tio vermelho) ou 1–2 rotações | **split**: chave do meio sobe |
| Remoção quebra regra quando | sai um nó preto ("duplo preto") | nó ficaria sem chave |
| Conserta com | casos 1–4: recolorir/rotacionar (máx. 3 rotações) | **empréstimo** do irmão ou **fusão** |
| Equivalência | recolorir no caso 1 = split de um 4-nó; rotação = arrumar um 3-nó/4-nó torto | |

A árvore 2-3-4 cresce **para cima** (só a raiz dividindo aumenta a altura) e encolhe **por cima**
(só a fusão na raiz diminui a altura) — por isso as folhas ficam sempre no mesmo nível.
