"""Árvore Rubro-Negra implementada do zero com nós duplamente encadeados
(cada nó aponta para o filho esquerdo, o filho direito e o PAI).

Usa um nó sentinela NIL (preto) no lugar de None, como no livro do Cormen.

Política de chaves repetidas: cada nó guarda um BALDE (lista) de lotes com o
mesmo preço. Repetido NÃO cria nó novo -> não altera a forma da árvore.
"""

VERMELHO, PRETO = "V", "P"


class NoRN:
    __slots__ = ("chave", "lotes", "cor", "esq", "dir", "pai")

    def __init__(self, chave, lotes, cor, nil):
        self.chave = chave
        self.lotes = lotes      # balde de lotes com a mesma chave
        self.cor = cor
        self.esq = nil
        self.dir = nil
        self.pai = nil


class ArvoreRubroNegra:
    nome = "Rubro-Negra"

    def __init__(self, observador=None):
        self.NIL = NoRN(None, [], PRETO, None)
        self.NIL.esq = self.NIL.dir = self.NIL.pai = self.NIL
        self.raiz = self.NIL
        self.observador = observador        # função chamada a cada passo (plot)
        self.eventos = []
        self.qtd_nos = 0

    # ------------------------------------------------------------ utilidades
    def _log(self, msg):
        self.eventos.append(msg)
        if self.observador:
            self.observador(self, msg)

    def limpar_eventos(self):
        self.eventos = []

    def _minimo(self, no):
        while no.esq is not self.NIL:
            no = no.esq
        return no

    # ------------------------------------------------------------- rotações
    def _rotacao_esquerda(self, x):
        y = x.dir
        x.dir = y.esq
        if y.esq is not self.NIL:
            y.esq.pai = x
        y.pai = x.pai
        if x.pai is self.NIL:
            self.raiz = y
        elif x is x.pai.esq:
            x.pai.esq = y
        else:
            x.pai.dir = y
        y.esq = x
        x.pai = y
        self._log(f"Rotação à ESQUERDA em {x.chave} ({y.chave} sobe)")

    def _rotacao_direita(self, x):
        y = x.esq
        x.esq = y.dir
        if y.dir is not self.NIL:
            y.dir.pai = x
        y.pai = x.pai
        if x.pai is self.NIL:
            self.raiz = y
        elif x is x.pai.dir:
            x.pai.dir = y
        else:
            x.pai.esq = y
        y.dir = x
        x.pai = y
        self._log(f"Rotação à DIREITA em {x.chave} ({y.chave} sobe)")

    def _pintar(self, no, cor):
        if no is not self.NIL and no.cor != cor:
            no.cor = cor

    # ---------------------------------------------------------------- busca
    def buscar(self, chave):
        """Retorna (nó ou None, caminho de chaves visitadas)."""
        no, caminho = self.raiz, []
        while no is not self.NIL:
            caminho.append(no.chave)
            if chave == no.chave:
                return no, caminho
            no = no.esq if chave < no.chave else no.dir
        return None, caminho

    def em_ordem(self):
        saida = []

        def visita(no):
            if no is not self.NIL:
                visita(no.esq)
                saida.append(no)
                visita(no.dir)
        visita(self.raiz)
        return saida

    def altura(self):
        def h(no):
            return 0 if no is self.NIL else 1 + max(h(no.esq), h(no.dir))
        return h(self.raiz)

    # -------------------------------------------------------------- inserção
    def inserir(self, lote):
        k = lote.preco
        pai, no = self.NIL, self.raiz
        while no is not self.NIL:
            pai = no
            if k == no.chave:
                no.lotes.append(lote)
                self._log(f"Preço {k} já existe -> lote {lote.id} vai para o balde "
                          f"(agora {len(no.lotes)} lotes). Árvore não muda.")
                return "duplicata"
            no = no.esq if k < no.chave else no.dir

        z = NoRN(k, [lote], VERMELHO, self.NIL)
        z.pai = pai
        if pai is self.NIL:
            self.raiz = z
        elif k < pai.chave:
            pai.esq = z
        else:
            pai.dir = z
        self.qtd_nos += 1
        self._log(f"Inseriu {k} como folha VERMELHA")
        self._corrigir_insercao(z)
        return "novo"

    def _corrigir_insercao(self, z):
        while z.pai.cor == VERMELHO:
            p, g = z.pai, z.pai.pai
            if p is g.esq:
                tio = g.dir
                if tio.cor == VERMELHO:                       # caso 1
                    self._pintar(p, PRETO)
                    self._pintar(tio, PRETO)
                    self._pintar(g, VERMELHO)
                    self._log(f"Caso 1 (tio {tio.chave} vermelho): recolore "
                              f"{p.chave},{tio.chave} pretos e {g.chave} vermelho")
                    z = g
                else:
                    if z is p.dir:                            # caso 2 (triângulo)
                        self._log(f"Caso 2 (triângulo): gira {p.chave} para virar linha")
                        z = p
                        self._rotacao_esquerda(z)
                        p = z.pai
                    self._pintar(p, PRETO)                    # caso 3 (linha)
                    self._pintar(g, VERMELHO)
                    self._log(f"Caso 3 (linha): {p.chave} preto, {g.chave} vermelho, "
                              f"gira {g.chave}")
                    self._rotacao_direita(g)
            else:                                             # espelhado
                tio = g.esq
                if tio.cor == VERMELHO:
                    self._pintar(p, PRETO)
                    self._pintar(tio, PRETO)
                    self._pintar(g, VERMELHO)
                    self._log(f"Caso 1 (tio {tio.chave} vermelho): recolore "
                              f"{p.chave},{tio.chave} pretos e {g.chave} vermelho")
                    z = g
                else:
                    if z is p.esq:
                        self._log(f"Caso 2 (triângulo): gira {p.chave} para virar linha")
                        z = p
                        self._rotacao_direita(z)
                        p = z.pai
                    self._pintar(p, PRETO)
                    self._pintar(g, VERMELHO)
                    self._log(f"Caso 3 (linha): {p.chave} preto, {g.chave} vermelho, "
                              f"gira {g.chave}")
                    self._rotacao_esquerda(g)
        if self.raiz.cor == VERMELHO:
            self._pintar(self.raiz, PRETO)
            self._log("Raiz pintada de PRETO")

    # -------------------------------------------------------------- exclusão
    def remover(self, chave, id_lote=None):
        """Remove um lote específico (id_lote) ou o preço inteiro.
        O nó só sai da árvore quando o balde fica vazio."""
        z, _ = self.buscar(chave)
        if z is None:
            return "não encontrado"
        if id_lote is not None:
            lote = next((l for l in z.lotes if l.id == id_lote), None)
            if lote is None:
                return "lote não está neste preço"
            z.lotes.remove(lote)
            if z.lotes:
                self._log(f"Lote {id_lote} saiu do balde de {chave}; ainda restam "
                          f"{len(z.lotes)}. Nó continua.")
                return "lote removido do balde"
        self._remover_no(z)
        self.qtd_nos -= 1
        return "nó removido"

    def _transplantar(self, u, v):
        if u.pai is self.NIL:
            self.raiz = v
        elif u is u.pai.esq:
            u.pai.esq = v
        else:
            u.pai.dir = v
        v.pai = u.pai

    def _remover_no(self, z):
        y, cor_original = z, z.cor
        if z.esq is self.NIL:
            x = z.dir
            self._transplantar(z, z.dir)
        elif z.dir is self.NIL:
            x = z.esq
            self._transplantar(z, z.esq)
        else:
            y = self._minimo(z.dir)                # sucessor em ordem
            cor_original = y.cor
            x = y.dir
            if y.pai is z:
                x.pai = y
            else:
                self._transplantar(y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            self._transplantar(z, y)
            y.esq = z.esq
            y.esq.pai = y
            y.cor = z.cor
            self._log(f"{z.chave} tem 2 filhos: substituído pelo sucessor {y.chave}")
        self._log(f"Removeu o nó {z.chave} (cor removida: "
                  f"{'PRETA' if cor_original == PRETO else 'VERMELHA'})")
        if cor_original == PRETO:
            self._log("Saiu um nó PRETO -> 'duplo preto', precisa corrigir")
            self._corrigir_remocao(x)

    def _corrigir_remocao(self, x):
        while x is not self.raiz and x.cor == PRETO:
            if x is x.pai.esq:
                w = x.pai.dir
                if w.cor == VERMELHO:                                  # caso 1
                    self._pintar(w, PRETO)
                    self._pintar(x.pai, VERMELHO)
                    self._log(f"Remoção caso 1: irmão {w.chave} vermelho -> gira o pai")
                    self._rotacao_esquerda(x.pai)
                    w = x.pai.dir
                if w.esq.cor == PRETO and w.dir.cor == PRETO:          # caso 2
                    self._pintar(w, VERMELHO)
                    self._log(f"Remoção caso 2: irmão {w.chave} e sobrinhos pretos -> "
                              f"{w.chave} vermelho, problema sobe")
                    x = x.pai
                else:
                    if w.dir.cor == PRETO:                             # caso 3
                        self._pintar(w.esq, PRETO)
                        self._pintar(w, VERMELHO)
                        self._log(f"Remoção caso 3: sobrinho próximo vermelho -> gira {w.chave}")
                        self._rotacao_direita(w)
                        w = x.pai.dir
                    w.cor = x.pai.cor                                  # caso 4
                    self._pintar(x.pai, PRETO)
                    self._pintar(w.dir, PRETO)
                    self._log(f"Remoção caso 4: sobrinho distante vermelho -> gira {x.pai.chave}")
                    self._rotacao_esquerda(x.pai)
                    x = self.raiz
            else:                                                      # espelhado
                w = x.pai.esq
                if w.cor == VERMELHO:
                    self._pintar(w, PRETO)
                    self._pintar(x.pai, VERMELHO)
                    self._log(f"Remoção caso 1: irmão {w.chave} vermelho -> gira o pai")
                    self._rotacao_direita(x.pai)
                    w = x.pai.esq
                if w.dir.cor == PRETO and w.esq.cor == PRETO:
                    self._pintar(w, VERMELHO)
                    self._log(f"Remoção caso 2: irmão {w.chave} e sobrinhos pretos -> "
                              f"{w.chave} vermelho, problema sobe")
                    x = x.pai
                else:
                    if w.esq.cor == PRETO:
                        self._pintar(w.dir, PRETO)
                        self._pintar(w, VERMELHO)
                        self._log(f"Remoção caso 3: sobrinho próximo vermelho -> gira {w.chave}")
                        self._rotacao_esquerda(w)
                        w = x.pai.esq
                    w.cor = x.pai.cor
                    self._pintar(x.pai, PRETO)
                    self._pintar(w.esq, PRETO)
                    self._log(f"Remoção caso 4: sobrinho distante vermelho -> gira {x.pai.chave}")
                    self._rotacao_direita(x.pai)
                    x = self.raiz
        if x is not self.NIL and x.cor == VERMELHO:
            self._pintar(x, PRETO)
            self._log(f"{x.chave} (vermelho) assume o preto que faltava: altura negra restaurada")
        x.cor = PRETO
        self.NIL.cor = PRETO
