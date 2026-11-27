"""Bolsa do Açaí — índice de lotes da Feira do Açaí (Ver-o-Peso, Belém).

Os barcos chegam de madrugada e cada lote tem um preço por rasa. O comprador
quer achar rápido: um preço exato, o lote mais barato, os lotes que cabem no
orçamento (faixa de preço). Os lotes entram e saem a noite toda -> a árvore
precisa continuar balanceada. Os mesmos lotes vão para uma Rubro-Negra e para
uma 2-3-4 ao mesmo tempo, para comparar os dois balanceamentos.

Execução:  python main.py
"""
import os
import sys

from arvores.lote import Lote, carregar_csv
from arvores.rubro_negra import ArvoreRubroNegra
from arvores.arvore234 import Arvore234, rubro_negra_para_234
from arvores import visual, kd

PASTA = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(PASTA, "saida")
CSV = os.path.join(PASTA, "dados", "lotes_madrugada.csv")


class Sistema:
    def __init__(self):
        self.rn = ArvoreRubroNegra()
        self.t = Arvore234()
        self.passo_a_passo = False
        self.n_op = 0

    # liga/desliga a gravação de cada passo de balanceamento
    def _preparar(self, rotulo):
        self.rn.limpar_eventos()
        self.t.limpar_eventos()
        self.n_op += 1
        if self.passo_a_passo:
            pasta = os.path.join(SAIDA, "passos", f"{self.n_op:02d}_{rotulo}")
            self.g_rn = visual.GravadorPassos(pasta, "rubro_negra")
            self.g_t = visual.GravadorPassos(pasta, "arvore234")
            self.rn.observador, self.t.observador = self.g_rn, self.g_t
        else:
            self.rn.observador = self.t.observador = None

    def _relatar(self):
        print("\n  [Rubro-Negra]")
        for e in self.rn.eventos:
            print("    -", e)
        print("  [2-3-4]")
        for e in self.t.eventos:
            print("    -", e)
        if self.passo_a_passo:
            for g in (self.g_rn, self.g_t):
                gif = g.gerar_gif()
                if gif:
                    print("  GIF do passo a passo:", os.path.relpath(gif, PASTA))
        self.rn.observador = self.t.observador = None
        self.rn.verificar()
        self.t.verificar()

    def inserir(self, lote, falar=True):
        if falar:
            self._preparar(f"insere_{lote.preco}")
        self.rn.inserir(lote)
        self.t.inserir(Lote(**vars(lote)))
        if falar:
            self._relatar()

    def remover(self, preco, id_lote=None):
        self._preparar(f"remove_{preco}")
        r1 = self.rn.remover(preco, id_lote)
        r2 = self.t.remover(preco, id_lote)
        print(f"  Rubro-Negra: {r1} | 2-3-4: {r2}")
        self._relatar()

    def mostrar(self, destacar=(), nome="arvores"):
        arq = os.path.join(SAIDA, f"{nome}.png")
        visual.lado_a_lado(self.rn, self.t, destacar, arquivo=arq, mostrar=True)
        print("  Figura salva em", os.path.relpath(arq, PASTA))


def ler_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("  digite um número inteiro")


def menu():
    s = Sistema()
    lotes = carregar_csv(CSV)
    for l in lotes:
        s.inserir(l, falar=False)
    prox_id = len(lotes)
    print(f"\n{len(lotes)} lotes da madrugada carregados ({s.rn.qtd_nos} preços distintos).")

    opcoes = """
=================== BOLSA DO AÇAÍ — Ver-o-Peso ===================
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
11  Modo passo a passo: {pp}
 0  Sair
================================================================="""
    while True:
        print(opcoes.format(pp="LIGADO" if s.passo_a_passo else "desligado"))
        op = input("Opção: ").strip()
        if op == "1":
            s.mostrar()
        elif op == "2":
            preco = ler_int("  Preço da rasa (R$): ")
            origem = input("  Origem: ") or "Combu"
            barco = input("  Barco: ") or "Sem nome"
            rasas = ler_int("  Quantidade de rasas: ")
            hora = input("  Chegada (HH:MM): ") or "05:00"
            prox_id += 1
            novo = Lote(f"L{prox_id:02d}", preco, origem, barco, rasas, hora)
            s.inserir(novo)
            print("  Inserido:", novo)
        elif op == "3":
            preco = ler_int("  Preço: ")
            no, _ = s.rn.buscar(preco)
            if no is None:
                print("  Não há lotes com esse preço.")
                continue
            for l in no.lotes:
                print("   ", l)
            id_ = input("  ID do lote (Enter = remover o preço inteiro): ").strip() or None
            s.remover(preco, id_)
        elif op == "4":
            preco = ler_int("  Preço: ")
            no, cam = s.rn.buscar(preco)
            no2, _, cam2 = s.t.buscar(preco)
            print(f"  Rubro-Negra: {len(cam)} comparações, caminho {cam}")
            print(f"  2-3-4      : {len(cam2)} nós visitados, caminho {cam2}")
            if no:
                for l in no.lotes:
                    print("   ", l)
                s.mostrar(destacar=set(cam) | {preco}, nome=f"busca_{preco}")
            else:
                print("  Não encontrado.")
        elif op == "5":
            a, b = ler_int("  De R$: "), ler_int("  Até R$: ")
            achados = s.rn.faixa(a, b)
            assert [l.id for l in achados] == [l.id for l in s.t.faixa(a, b)]
            print(f"  {len(achados)} lotes (mesmo resultado nas duas árvores):")
            for l in achados:
                print("   ", l)
        elif op == "6":
            nos = s.rn.em_ordem()
            if nos:
                print("  Mais barato:", *nos[0].lotes, sep="\n    ")
                print("  Mais caro  :", *nos[-1].lotes, sep="\n    ")
        elif op == "7":
            raiz = rubro_negra_para_234(s.rn)
            arq = os.path.join(SAIDA, "equivalencia.png")
            visual.lado_a_lado(s.rn, raiz, arquivo=arq, mostrar=True,
                               titulo_t="A MESMA Rubro-Negra agrupando cada nó preto com seus filhos vermelhos")
            print("  Cada nó preto + filhos vermelhos = um nó 2-3-4 (2, 3 ou 4 filhos).")
            print("  Figura salva em", os.path.relpath(arq, PASTA))
        elif op == "8":
            print(f"  Rubro-Negra: altura {s.rn.altura()}, altura negra {s.rn.verificar()}, "
                  f"rotações {s.rn.stats['rotacoes']}, recolorações {s.rn.stats['recoloracoes']}")
            print(f"  2-3-4      : altura {s.t.altura()}, nós {len(s.t.nos())}, "
                  f"splits {s.t.stats['splits']}, fusões {s.t.stats['fusoes']}, "
                  f"empréstimos {s.t.stats['emprestimos']}")
        elif op == "9":
            print(f"  Rubro-Negra OK (altura negra {s.rn.verificar()}) | 2-3-4 OK (altura {s.t.verificar()})")
        elif op == "10":
            x, y = ler_int("  Posição x do comprador (0-100 m): "), ler_int("  Posição y (0-100 m): ")
            arq = os.path.join(SAIDA, "kd_tree.png")
            kd.demonstracao((x, y), arquivo=arq, mostrar=True)
            print("  Figura salva em", os.path.relpath(arq, PASTA))
        elif op == "11":
            s.passo_a_passo = not s.passo_a_passo
            if s.passo_a_passo:
                print("  Cada rotação/split/fusão vira um quadro em saida/passos/ + GIF.")
        elif op == "0":
            break


if __name__ == "__main__":
    os.makedirs(SAIDA, exist_ok=True)
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
