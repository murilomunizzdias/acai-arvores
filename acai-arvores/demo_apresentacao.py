"""Roteiro automático da apresentação: gera todas as figuras e GIFs em saida/.

Execução:  python demo_apresentacao.py
"""
import os

from arvores.lote import Lote, carregar_csv
from arvores.rubro_negra import ArvoreRubroNegra
from arvores.arvore234 import Arvore234, rubro_negra_para_234
from arvores import visual, kd

PASTA = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(PASTA, "saida", "apresentacao")
os.makedirs(SAIDA, exist_ok=True)


def titulo(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


def passo(rn, t, rotulo, acao):
    g1 = visual.GravadorPassos(os.path.join(SAIDA, rotulo), "rubro_negra")
    g2 = visual.GravadorPassos(os.path.join(SAIDA, rotulo), "arvore234")
    rn.observador, t.observador = g1, g2
    rn.limpar_eventos()
    t.limpar_eventos()
    acao()
    rn.observador = t.observador = None
    print("[Rubro-Negra]")
    for e in rn.eventos:
        print("  -", e)
    print("[2-3-4]")
    for e in t.eventos:
        print("  -", e)
    print("GIFs:", g1.gerar_gif(), g2.gerar_gif(), sep="\n  ")
    rn.verificar()
    t.verificar()


rn, t = ArvoreRubroNegra(), Arvore234()
lotes = carregar_csv(os.path.join(PASTA, "dados", "lotes_madrugada.csv"))

titulo("1) Construção incremental: os 6 primeiros lotes, passo a passo")
for l in lotes[:6]:
    passo(rn, t, f"01_construcao_{l.id}_{l.preco}", lambda l=l: (rn.inserir(l), t.inserir(Lote(**vars(l)))))

for l in lotes[6:]:
    rn.inserir(l)
    t.inserir(Lote(**vars(l)))
print(f"\nCarga completa: {len(lotes)} lotes, {rn.qtd_nos} preços distintos (nós).")
visual.lado_a_lado(rn, t, arquivo=os.path.join(SAIDA, "02_arvores_completas.png"))
visual.figura(rn, arquivo=os.path.join(SAIDA, "02a_rubro_negra.png"))
visual.figura(t, arquivo=os.path.join(SAIDA, "02b_arvore234.png"))

titulo("2) Repetido: chega outro lote a R$ 220")
passo(rn, t, "03_repetido", lambda: (rn.inserir(Lote("L31", 220, "Combu", "Curupira", 20, "05:10")),
                                     t.inserir(Lote("L31", 220, "Combu", "Curupira", 20, "05:10"))))

titulo("3) Inserção que força rotação / split: lote a R$ 165")
passo(rn, t, "04_insere_165", lambda: (rn.inserir(Lote("L32", 165, "Muaná", "Maré Mansa", 14, "05:20")),
                                      t.inserir(Lote("L32", 165, "Muaná", "Maré Mansa", 14, "05:20"))))

titulo("4) Busca do preço 245")
no, cam = rn.buscar(245)
no2, _, cam2 = t.buscar(245)
print("Rubro-Negra caminho:", cam, "| 2-3-4 caminho:", cam2)
visual.lado_a_lado(rn, t, destacar=set(cam), arquivo=os.path.join(SAIDA, "05_busca_245.png"))

titulo("5) Orçamento: lotes de R$ 170 a R$ 210")
for l in rn.faixa(170, 210):
    print("  ", l)

titulo("6) Venda total do preço 150 (remoção com rebalanceamento)")
passo(rn, t, "06_remove_150", lambda: (rn.remover(150), t.remover(150)))

titulo("7) Venda de UM lote de R$ 180 (balde tem mais de um)")
no, _ = rn.buscar(180)
alvo = no.lotes[0].id
passo(rn, t, "07_remove_lote_180", lambda: (rn.remover(180, alvo), t.remover(180, alvo)))

titulo("8) Remoção de nó interno: preço 260")
passo(rn, t, "08_remove_260", lambda: (rn.remover(260), t.remover(260)))

titulo("9) Equivalência Rubro-Negra <-> 2-3-4")
visual.lado_a_lado(rn, rubro_negra_para_234(rn), arquivo=os.path.join(SAIDA, "09_equivalencia.png"),
                   titulo_t="A MESMA Rubro-Negra: nó preto + filhos vermelhos = 1 nó 2-3-4")

titulo("10) Comparativo")
print(f"Rubro-Negra: {rn.qtd_nos} nós, altura {rn.altura()}, altura negra {rn.verificar()}, "
      f"rotações {rn.stats['rotacoes']}, recolorações {rn.stats['recoloracoes']}")
print(f"2-3-4      : {t.qtd_chaves} chaves em {len(t.nos())} nós, altura {t.altura()}, "
      f"splits {t.stats['splits']}, fusões {t.stats['fusoes']}, empréstimos {t.stats['emprestimos']}")

titulo("11) Árvore k-D: barraca mais próxima do comprador")
kd.demonstracao((60, 60), arquivo=os.path.join(SAIDA, "11_kd_tree.png"))
print("\nTudo salvo em", SAIDA)
