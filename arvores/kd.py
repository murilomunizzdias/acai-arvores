"""Árvore k-D (k = 2) — explicação + demonstração.

Problema: o comprador chega num ponto da feira e quer a BARRACA DE AÇAÍ MAIS
PRÓXIMA. Cada barraca é um ponto (x, y) em metros no mapa da feira.
Em cada nível a árvore alterna o eixo de corte: nível par corta em x
(linha vertical), nível ímpar corta em y (linha horizontal).
"""
import math


class NoKD:
    __slots__ = ("ponto", "nome", "eixo", "esq", "dir", "pai")

    def __init__(self, ponto, nome, eixo, pai=None):
        self.ponto, self.nome, self.eixo = ponto, nome, eixo
        self.esq = self.dir = None
        self.pai = pai


class ArvoreKD:
    def __init__(self, k=2):
        self.k = k
        self.raiz = None
        self.eventos = []

    def inserir(self, ponto, nome):
        if self.raiz is None:
            self.raiz = NoKD(ponto, nome, 0)
            self.eventos.append(f"{nome}{ponto} vira raiz (corta em x)")
            return
        no, prof = self.raiz, 0
        while True:
            e = no.eixo
            lado = "esq" if ponto[e] < no.ponto[e] else "dir"
            filho = getattr(no, lado)
            if filho is None:
                novo = NoKD(ponto, nome, (prof + 1) % self.k, no)
                setattr(no, lado, novo)
                self.eventos.append(
                    f"{nome}{ponto}: {'x' if e == 0 else 'y'}={ponto[e]} "
                    f"{'<' if lado == 'esq' else '>='} {no.ponto[e]} de {no.nome} -> {lado}"
                )
                return
            no, prof = filho, prof + 1

    @classmethod
    def balanceada(cls, pontos, k=2):
        """Constrói pela MEDIANA do eixo em cada nível -> altura ~ log2(n)."""
        arv = cls(k)

        def constroi(lista, prof, pai):
            if not lista:
                return None
            e = prof % k
            lista = sorted(lista, key=lambda p: p[0][e])
            m = len(lista) // 2
            no = NoKD(lista[m][0], lista[m][1], e, pai)
            no.esq = constroi(lista[:m], prof + 1, no)
            no.dir = constroi(lista[m + 1:], prof + 1, no)
            return no
        arv.raiz = constroi(list(pontos), 0, None)
        return arv

    def mais_proximo(self, alvo):
        """Vizinho mais próximo com PODA: só visita o outro lado do corte se a
        distância até a linha de corte for menor que a melhor já achada."""
        melhor = [None, math.inf]
        visitados, podados = [], []

        def busca(no):
            if no is None:
                return
            visitados.append(no.nome)
            d = math.dist(alvo, no.ponto)
            if d < melhor[1]:
                melhor[0], melhor[1] = no, d
            e = no.eixo
            dif = alvo[e] - no.ponto[e]
            perto, longe = (no.esq, no.dir) if dif < 0 else (no.dir, no.esq)
            busca(perto)
            if abs(dif) < melhor[1]:
                busca(longe)
            elif longe is not None:
                podados.append(longe.nome)
        busca(self.raiz)
        return melhor[0], melhor[1], visitados, podados

    def nos(self):
        saida, pilha = [], [self.raiz] if self.raiz else []
        while pilha:
            n = pilha.pop()
            saida.append(n)
            pilha += [f for f in (n.esq, n.dir) if f]
        return saida


BARRACAS = [
    ((42, 30), "B01"), ((15, 62), "B02"), ((70, 12), "B03"), ((28, 8), "B04"),
    ((58, 74), "B05"), ((85, 48), "B06"), ((8, 25), "B07"), ((50, 52), "B08"),
    ((33, 88), "B09"), ((92, 85), "B10"), ((64, 35), "B11"), ((20, 42), "B12"),
]


def desenhar_kd(arv, alvo=None, resultado=None, arquivo=None, mostrar=False, limites=(0, 100, 0, 100)):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6))
    xmin, xmax, ymin, ymax = limites

    def particiona(no, x0, x1, y0, y1):
        if no is None:
            return
        x, y = no.ponto
        if no.eixo == 0:
            a1.plot([x, x], [y0, y1], color="#c0392b", lw=1.6)
            particiona(no.esq, x0, x, y0, y1)
            particiona(no.dir, x, x1, y0, y1)
        else:
            a1.plot([x0, x1], [y, y], color="#2471a3", lw=1.6)
            particiona(no.esq, x0, x1, y0, y)
            particiona(no.dir, x0, x1, y, y1)
    particiona(arv.raiz, xmin, xmax, ymin, ymax)
    for n in arv.nos():
        a1.scatter(*n.ponto, s=60, c="#4a1a4f", zorder=3)
        a1.annotate(n.nome, n.ponto, xytext=(4, 4), textcoords="offset points", fontsize=8)
    if alvo:
        a1.scatter(*alvo, marker="*", s=260, c="#f1c40f", edgecolors="k", zorder=4)
        a1.annotate("comprador", alvo, xytext=(6, -12), textcoords="offset points", fontsize=8)
        if resultado:
            no, d = resultado
            a1.plot([alvo[0], no.ponto[0]], [alvo[1], no.ponto[1]], "k--", lw=1)
            a1.add_patch(plt.Circle(alvo, d, fill=False, ls=":", ec="k"))
    a1.set_xlim(xmin, xmax)
    a1.set_ylim(ymin, ymax)
    a1.set_aspect("equal")
    a1.set_title("Mapa da feira: vermelho corta em x, azul corta em y")

    # árvore
    pos, cont = {}, [0]

    def lay(no, d):
        if no is None:
            return
        lay(no.esq, d + 1)
        pos[id(no)] = (cont[0], -d)
        cont[0] += 1
        lay(no.dir, d + 1)
    lay(arv.raiz, 0)
    for n in arv.nos():
        x, y = pos[id(n)]
        for f in (n.esq, n.dir):
            if f:
                a2.plot([x, pos[id(f)][0]], [y, pos[id(f)][1]], color="#888")
    for n in arv.nos():
        x, y = pos[id(n)]
        cor = "#c0392b" if n.eixo == 0 else "#2471a3"
        a2.scatter([x], [y], s=900, c=cor, zorder=2)
        a2.text(x, y, f"{n.nome}\n{n.ponto}", ha="center", va="center", fontsize=6.5, color="white", zorder=3)
    a2.axis("off")
    a2.set_title("Árvore 2-D (nível par: x | nível ímpar: y)")
    fig.tight_layout()
    if arquivo:
        fig.savefig(arquivo, dpi=130)
    plt.close(fig)
    if mostrar and arquivo:
        from .visual import abrir_imagem
        abrir_imagem(arquivo)


def demonstracao(alvo=(60, 60), arquivo=None, mostrar=False):
    arv = ArvoreKD()
    for p, nome in BARRACAS:
        arv.inserir(p, nome)
    print("\n== Inserção na árvore 2-D (alternando eixos) ==")
    for e in arv.eventos:
        print("  ", e)
    no, d, vis, pod = arv.mais_proximo(alvo)
    forca_bruta = min(BARRACAS, key=lambda b: math.dist(alvo, b[0]))
    print(f"\nComprador em {alvo}: barraca mais próxima = {no.nome}{no.ponto} a {d:.1f} m")
    print(f"Nós visitados: {len(vis)} de {len(BARRACAS)} -> {vis}")
    print(f"Subárvores podadas (nem foram olhadas): {pod}")
    print(f"Conferência por força bruta: {forca_bruta[1]} ✔" if forca_bruta[1] == no.nome else "ERRO")
    desenhar_kd(arv, alvo, (no, d), arquivo, mostrar)
    return arv
