"""Desenho das árvores com matplotlib (biblioteca só de PLOTAGEM, não de árvore)."""
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")  # desenha em arquivo; a imagem é aberta pelo visualizador do sistema
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from .rubro_negra import ArvoreRubroNegra, VERMELHO

COR_V = "#c0392b"
COR_P = "#1f1f1f"
COR_ACAI = "#4a1a4f"
DESTAQUE = "#f1c40f"


# ------------------------------------------------------------ Rubro-Negra
def desenhar_rn(ax, rn, destacar=(), titulo=""):
    nos = rn.em_ordem()
    pos = {}

    def profundidade(no):
        d = 0
        while no.pai is not rn.NIL:
            no, d = no.pai, d + 1
        return d
    for x, no in enumerate(nos):
        pos[id(no)] = (x, -profundidade(no))
    for no in nos:
        x, y = pos[id(no)]
        for f in (no.esq, no.dir):
            if f is not rn.NIL:
                fx, fy = pos[id(f)]
                ax.plot([x, fx], [y, fy], color="#888", lw=1.4, zorder=1)
    for no in nos:
        x, y = pos[id(no)]
        cor = COR_V if no.cor == VERMELHO else COR_P
        borda = DESTAQUE if no.chave in destacar else "white"
        ax.scatter([x], [y], s=620, c=cor, edgecolors=borda, linewidths=3 if borda == DESTAQUE else 1, zorder=2)
        ax.text(x, y, str(no.chave), color="white", ha="center", va="center", fontsize=8, fontweight="bold", zorder=3)
        if len(no.lotes) > 1:
            ax.text(x + 0.32, y + 0.28, f"×{len(no.lotes)}", fontsize=7, color=COR_ACAI, fontweight="bold", zorder=3)
    ax.set_title(titulo or f"Rubro-Negra — {rn.qtd_nos} nós, altura {rn.altura()}", fontsize=11)
    ax.axis("off")
    if nos:
        ax.set_xlim(-1, len(nos))
        ax.set_ylim(min(p[1] for p in pos.values()) - 0.8, 0.8)


# ------------------------------------------------------------------ 2-3-4
def desenhar_234(ax, raiz, destacar=(), titulo=""):
    if raiz is None:
        ax.axis("off")
        ax.set_title(titulo or "2-3-4 vazia")
        return
    LARG, GAP = 1.0, 0.7
    pos = {}
    cursor = [0.0]

    def layout(no, d):
        if no.folha:
            w = len(no.chaves) * LARG
            pos[id(no)] = (cursor[0] + w / 2, -d * 1.6)
            cursor[0] += w + GAP
        else:
            for f in no.filhos:
                layout(f, d + 1)
            xs = [pos[id(f)][0] for f in no.filhos]
            pos[id(no)] = ((xs[0] + xs[-1]) / 2, -d * 1.6)
    layout(raiz, 0)

    def desenha(no):
        cx, cy = pos[id(no)]
        w = len(no.chaves) * LARG
        x0 = cx - w / 2
        for j, f in enumerate(no.filhos):
            fx, fy = pos[id(f)]
            ax.plot([x0 + j * LARG, fx], [cy - 0.3, fy + 0.3], color="#888", lw=1.3, zorder=1)
            desenha(f)
        for j, k in enumerate(no.chaves):
            cor = DESTAQUE if k in destacar else "#efe3f1"
            ax.add_patch(FancyBboxPatch((x0 + j * LARG + 0.04, cy - 0.3), LARG - 0.08, 0.6,
                                        boxstyle="round,pad=0.02", fc=cor, ec=COR_ACAI, lw=1.4, zorder=2))
            ax.text(x0 + j * LARG + LARG / 2, cy, str(k), ha="center", va="center", fontsize=8,
                    fontweight="bold", color=COR_ACAI, zorder=3)
            if len(no.baldes[j]) > 1:
                ax.text(x0 + j * LARG + LARG - 0.1, cy + 0.38, f"×{len(no.baldes[j])}", fontsize=7,
                        color=COR_V, fontweight="bold", ha="right", zorder=3)
    desenha(raiz)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 2, max(xs) + 2)
    ax.set_ylim(min(ys) - 0.9, 0.9)
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_title(titulo, fontsize=11)


def _titulo_234(t):
    return f"2-3-4 — {t.qtd_chaves} chaves, {len(t.nos())} nós, altura {t.altura()}"


# ------------------------------------------------------------- utilitários
def figura(arvore, destacar=(), titulo=None, legenda=None, arquivo=None, mostrar=False):
    n = arvore.qtd_nos if isinstance(arvore, ArvoreRubroNegra) else arvore.qtd_chaves
    fig, ax = plt.subplots(figsize=(max(8, n * 0.42), 5.2))
    if isinstance(arvore, ArvoreRubroNegra):
        desenhar_rn(ax, arvore, destacar, titulo)
    else:
        desenhar_234(ax, arvore.raiz, destacar, titulo or _titulo_234(arvore))
    if legenda:
        fig.text(0.5, 0.02, legenda, ha="center", fontsize=9, wrap=True,
                 bbox=dict(fc="#fff8dc", ec="#d4ac0d"))
    _finaliza(fig, arquivo, mostrar)


def lado_a_lado(rn, t, destacar=(), arquivo=None, mostrar=False):
    n = max(rn.qtd_nos, 10)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(max(10, n * 0.45), 10))
    desenhar_rn(a1, rn, destacar)
    desenhar_234(a2, t.raiz, destacar, _titulo_234(t))
    _finaliza(fig, arquivo, mostrar)


def abrir_imagem(arquivo):
    """Abre o PNG no visualizador de imagens do sistema SEM travar o menu."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(arquivo)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", arquivo])
        else:
            subprocess.Popen(["xdg-open", arquivo], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print("  (abra a imagem manualmente:", arquivo, ")")


def _finaliza(fig, arquivo, mostrar):
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    if arquivo:
        os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
        fig.savefig(arquivo, dpi=130)
    plt.close(fig)
    if mostrar and arquivo:
        abrir_imagem(arquivo)


class GravadorPassos:
    """Observador: salva um quadro PNG a cada rotação/recoloração/split/fusão."""

    def __init__(self, pasta, prefixo):
        self.pasta, self.prefixo, self.quadros = pasta, prefixo, []
        os.makedirs(pasta, exist_ok=True)

    def __call__(self, arvore, msg):
        arq = os.path.join(self.pasta, f"{self.prefixo}_{len(self.quadros):03d}.png")
        figura(arvore, legenda=f"Passo {len(self.quadros) + 1}: {msg}", arquivo=arq)
        self.quadros.append(arq)
