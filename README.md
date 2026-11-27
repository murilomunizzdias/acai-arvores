# Bolsa do Açaí — Árvores Rubro-Negra e 2-3-4 aplicadas à Feira do Açaí do Ver-o-Peso

Trabalho do 2º bimestre — Estruturas de Dados (árvores balanceadas).

**Equipe**
- Murilo Muniz Dias
- João Paulo Koury
- Lucas Pinto
- Pedro Antônio

## O problema

Toda madrugada os barcos das ilhas descarregam açaí na Feira do Açaí, ao lado do Ver-o-Peso.
Cada **lote** tem um **preço por rasa**. Os lotes chegam (inserção) e são vendidos (exclusão) a noite
toda, e o comprador quer achar rápido um lote por preço (busca). Como a ordem de chegada é
imprevisível, a árvore precisa se manter balanceada.

Os mesmos lotes entram em uma **Árvore Rubro-Negra** e em uma **Árvore 2-3-4** ao mesmo tempo,
para comparar os dois métodos de balanceamento.

## O que foi implementado

| Árvore | Arquivo | Inserção + balanceamento | Exclusão + balanceamento | Busca |
|---|---|---|---|---|
| Rubro-Negra | `arvores/rubro_negra.py` | recoloração + rotações | casos do "duplo preto" | ✔ |
| 2-3-4 | `arvores/arvore234.py` | split do 4-nó | empréstimo do irmão / fusão | ✔ |

- Árvores feitas do zero com **nós encadeados** (ponteiros para os filhos e para o pai, ao estilo
  de lista duplamente encadeada). **Nenhuma biblioteca de árvore** foi usada.
- **matplotlib** é usada só para **desenhar** as árvores e cada passo do balanceamento.
- A Árvore k-D é apresentada apenas com explicação e exemplo nos slides, como pede o enunciado.

### Elementos repetidos

A chave é o **preço da rasa (R$)**. Lotes com o mesmo preço ficam num **balde** (lista) dentro do
mesmo nó:
- **Inserir** um preço que já existe: o lote entra no balde; nenhum nó é criado e a árvore não muda.
- **Remover** um lote: ele sai do balde. O nó só sai da árvore (com balanceamento) quando o balde
  fica vazio. Remover sem informar o lote remove o preço inteiro.

Nos desenhos, `×3` ao lado do nó indica 3 lotes no balde.

## Como executar

Requisitos: **Python 3.9+**

```bash
git clone https://github.com/murilomunizzdias/acai-arvores.git
cd acai-arvores
pip install -r requirements.txt
python main.py
```

O programa carrega os 30 lotes de `dados/lotes_madrugada.csv` (23 preços distintos = **23 nós**) e
abre o menu:

```
 1  Ver as duas árvores (figura)
 2  Chegou barco: inserir lote
 3  Vendeu: remover lote (um lote ou o preço inteiro)
 4  Buscar preço
 5  Modo passo a passo (uma figura por rotação/recoloração/split/fusão)
 0  Sair
```

Cada operação mostra no terminal o que o algoritmo fez nas duas árvores. As figuras ficam em `saida/`.

## Estrutura

```
acai-arvores/
├── main.py                    # menu
├── requirements.txt
├── dados/lotes_madrugada.csv  # 30 lotes, 23 preços distintos
└── arvores/
    ├── lote.py                # registro do lote + leitura do CSV
    ├── rubro_negra.py         # Árvore Rubro-Negra
    ├── arvore234.py           # Árvore 2-3-4
    └── visual.py              # desenho das árvores (matplotlib)
```
