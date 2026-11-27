"""Árvore 2-3-4 (não-binária) implementada do zero.

Cada nó tem 1 a 3 chaves e 2 a 4 filhos; todos os nós apontam para o PAI.
Inserção TOP-DOWN: todo 4-nó encontrado na descida é dividido (split) antes,
então a inserção na folha nunca estoura.
Remoção TOP-DOWN: antes de descer para um filho com só 1 chave, ele recebe
uma chave emprestada de um irmão (rotação) ou é fundido com ele (fusão), então
a remoção na folha nunca deixa um nó vazio.

Política de repetidos: igual à Rubro-Negra -> balde de lotes por chave.
"""


class No234:
    __slots__ = ("chaves", "baldes", "filhos", "pai")

    def __init__(self, pai=None):
        self.chaves = []    # 1..3 chaves ordenadas
        self.baldes = []    # baldes[i] = lista de lotes com preço chaves[i]
        self.filhos = []    # 0 (folha) ou len(chaves)+1
        self.pai = pai

    @property
    def folha(self):
        return not self.filhos

    def tipo(self):
        return f"{len(self.chaves) + 1}-nó"

    def __repr__(self):
        return "[" + "|".join(map(str, self.chaves)) + "]"


def _posicao(chaves, k):
    """Primeira posição i com chaves[i] >= k (busca linear: no máx. 3 chaves)."""
    i = 0
    while i < len(chaves) and chaves[i] < k:
        i += 1
    return i


class Arvore234:
    nome = "2-3-4"

    def __init__(self, observador=None):
        self.raiz = None
        self.observador = observador
        self.eventos = []
        self.qtd_chaves = 0
        self.stats = {"splits": 0, "fusoes": 0, "emprestimos": 0}

    def _log(self, msg):
        self.eventos.append(msg)
        if self.observador:
            self.observador(self, msg)

    def limpar_eventos(self):
        self.eventos = []

    @staticmethod
    def _ajustar_pais(no):
        for f in no.filhos:
            f.pai = no

    # ---------------------------------------------------------------- busca
    def buscar(self, chave):
        """Retorna (nó, índice, caminho) ou (None, None, caminho)."""
        no, caminho = self.raiz, []
        while no is not None:
            caminho.append(repr(no))
            i = _posicao(no.chaves, chave)
            if i < len(no.chaves) and no.chaves[i] == chave:
                return no, i, caminho
            no = None if no.folha else no.filhos[i]
        return None, None, caminho

    def faixa(self, a, b):
        saida = []

        def visita(no):
            if no is None:
                return
            for i, k in enumerate(no.chaves):
                if not no.folha and a < k:
                    visita(no.filhos[i])
                if a <= k <= b:
                    saida.extend(no.baldes[i])
            if not no.folha and no.chaves[-1] < b:
                visita(no.filhos[-1])
        visita(self.raiz)
        return saida

    def altura(self):
        h, no = 0, self.raiz
        while no is not None:
            h += 1
            no = None if no.folha else no.filhos[0]
        return h

    def nos(self):
        saida, fila = [], [self.raiz] if self.raiz else []
        while fila:
            n = fila.pop(0)
            saida.append(n)
            fila.extend(n.filhos)
        return saida

    # -------------------------------------------------------------- inserção
    def _split(self, x, i):
        """Divide o 4-nó x.filhos[i]: a chave do meio sobe para x."""
        y = x.filhos[i]
        antes = repr(y)
        z = No234(pai=x)
        k_meio, b_meio = y.chaves[1], y.baldes[1]
        z.chaves, z.baldes = [y.chaves[2]], [y.baldes[2]]
        if y.filhos:
            z.filhos = y.filhos[2:]
            y.filhos = y.filhos[:2]
            self._ajustar_pais(z)
        y.chaves, y.baldes = [y.chaves[0]], [y.baldes[0]]
        x.chaves.insert(i, k_meio)
        x.baldes.insert(i, b_meio)
        x.filhos.insert(i + 1, z)
        y.pai = x
        self.stats["splits"] += 1
        self._log(f"SPLIT do 4-nó {antes}: {k_meio} sobe, sobram {y} e {z}")

    def inserir(self, lote):
        k = lote.preco
        no, i, _ = self.buscar(k)
        if no is not None:
            no.baldes[i].append(lote)
            self._log(f"Preço {k} já existe -> lote {lote.id} vai para o balde "
                      f"(agora {len(no.baldes[i])} lotes). Árvore não muda.")
            return "duplicata"

        self.qtd_chaves += 1
        if self.raiz is None:
            self.raiz = No234()
            self.raiz.chaves, self.raiz.baldes = [k], [[lote]]
            self._log(f"Árvore vazia: {k} vira a raiz")
            return "novo"

        if len(self.raiz.chaves) == 3:                 # raiz cheia: cresce para cima
            nova = No234()
            nova.filhos = [self.raiz]
            self.raiz.pai = nova
            self.raiz = nova
            self._log("Raiz é um 4-nó: cria raiz nova (altura +1)")
            self._split(nova, 0)

        x = self.raiz
        while not x.folha:
            i = _posicao(x.chaves, k)
            if len(x.filhos[i].chaves) == 3:
                self._split(x, i)
                if k > x.chaves[i]:
                    i += 1
            x = x.filhos[i]
        i = _posicao(x.chaves, k)
        x.chaves.insert(i, k)
        x.baldes.insert(i, [lote])
        self._log(f"Inseriu {k} na folha -> {x} ({x.tipo()})")
        return "novo"

    # -------------------------------------------------------------- exclusão
    def remover(self, chave, id_lote=None):
        no, i, _ = self.buscar(chave)
        if no is None:
            return "não encontrado"
        if id_lote is not None:
            balde = no.baldes[i]
            lote = next((l for l in balde if l.id == id_lote), None)
            if lote is None:
                return "lote não está neste preço"
            balde.remove(lote)
            if balde:
                self._log(f"Lote {id_lote} saiu do balde de {chave}; ainda restam "
                          f"{len(balde)}. Nó continua.")
                return "lote removido do balde"
        self._remover(self.raiz, chave)
        self.qtd_chaves -= 1
        if self.raiz is not None and not self.raiz.chaves:
            self.raiz = None
        return "nó removido"

    def _fundir(self, x, i):
        """Junta filhos[i] + chave[i] de x + filhos[i+1] num só nó."""
        y, z = x.filhos[i], x.filhos[i + 1]
        desc = f"{y} + {x.chaves[i]} + {z}"
        y.chaves = y.chaves + [x.chaves[i]] + z.chaves
        y.baldes = y.baldes + [x.baldes[i]] + z.baldes
        y.filhos = y.filhos + z.filhos
        self._ajustar_pais(y)
        x.chaves.pop(i)
        x.baldes.pop(i)
        x.filhos.pop(i + 1)
        self.stats["fusoes"] += 1
        if x is self.raiz and not x.chaves:
            self.raiz = y
            y.pai = None
            self._log(f"FUSÃO {desc} -> {y}; raiz ficou vazia e sai (altura -1)")
        else:
            self._log(f"FUSÃO {desc} -> {y}")
        return y

    def _emprestar_esquerda(self, x, i):
        c, e = x.filhos[i], x.filhos[i - 1]
        c.chaves.insert(0, x.chaves[i - 1])
        c.baldes.insert(0, x.baldes[i - 1])
        x.chaves[i - 1] = e.chaves.pop()
        x.baldes[i - 1] = e.baldes.pop()
        if e.filhos:
            f = e.filhos.pop()
            c.filhos.insert(0, f)
            f.pai = c
        self.stats["emprestimos"] += 1
        self._log(f"EMPRÉSTIMO (rotação) do irmão esquerdo: {x.chaves[i-1]} sobe, "
                  f"{c.chaves[0]} desce para {c}")

    def _emprestar_direita(self, x, i):
        c, d = x.filhos[i], x.filhos[i + 1]
        c.chaves.append(x.chaves[i])
        c.baldes.append(x.baldes[i])
        x.chaves[i] = d.chaves.pop(0)
        x.baldes[i] = d.baldes.pop(0)
        if d.filhos:
            f = d.filhos.pop(0)
            c.filhos.append(f)
            f.pai = c
        self.stats["emprestimos"] += 1
        self._log(f"EMPRÉSTIMO (rotação) do irmão direito: {x.chaves[i]} sobe, "
                  f"{c.chaves[-1]} desce para {c}")

    def _remover(self, x, k):
        while True:
            i = _posicao(x.chaves, k)
            if i < len(x.chaves) and x.chaves[i] == k:
                if x.folha:                                   # caso 1: está na folha
                    x.chaves.pop(i)
                    x.baldes.pop(i)
                    self._log(f"Removeu {k} da folha -> {x}")
                    return
                y, z = x.filhos[i], x.filhos[i + 1]
                if len(y.chaves) >= 2:                        # caso 2a: predecessor
                    p = y
                    while not p.folha:
                        p = p.filhos[-1]
                    pk, pb = p.chaves[-1], p.baldes[-1]
                    x.chaves[i], x.baldes[i] = pk, pb
                    self._log(f"{k} é interno: troca pelo predecessor {pk}")
                    x, k = y, pk
                elif len(z.chaves) >= 2:                      # caso 2b: sucessor
                    s = z
                    while not s.folha:
                        s = s.filhos[0]
                    sk, sb = s.chaves[0], s.baldes[0]
                    x.chaves[i], x.baldes[i] = sk, sb
                    self._log(f"{k} é interno: troca pelo sucessor {sk}")
                    x, k = z, sk
                else:                                         # caso 2c: funde
                    x = self._fundir(x, i)
            else:
                if x.folha:
                    return                                    # não existe
                c = x.filhos[i]
                if len(c.chaves) == 1:                        # caso 3: garantir >= 2
                    if i > 0 and len(x.filhos[i - 1].chaves) >= 2:
                        self._emprestar_esquerda(x, i)
                    elif i < len(x.filhos) - 1 and len(x.filhos[i + 1].chaves) >= 2:
                        self._emprestar_direita(x, i)
                    elif i > 0:
                        c = self._fundir(x, i - 1)
                    else:
                        c = self._fundir(x, i)
                x = c

    # ------------------------------------------------------------ validação
    def verificar(self):
        if self.raiz is None:
            return 0
        assert self.raiz.pai is None
        profundidades = set()

        def checa(no, lo, hi, prof):
            assert 1 <= len(no.chaves) <= 3, f"nó com {len(no.chaves)} chaves"
            assert len(no.baldes) == len(no.chaves)
            assert all(no.baldes), "balde vazio"
            assert no.chaves == sorted(no.chaves)
            assert all((lo is None or k > lo) and (hi is None or k < hi) for k in no.chaves)
            if no.folha:
                profundidades.add(prof)
                return
            assert len(no.filhos) == len(no.chaves) + 1, "nº de filhos errado"
            limites = [lo] + no.chaves + [hi]
            for j, f in enumerate(no.filhos):
                assert f.pai is no, "ponteiro pai quebrado"
                checa(f, limites[j], limites[j + 1], prof + 1)
        checa(self.raiz, None, None, 0)
        assert len(profundidades) == 1, "folhas em níveis diferentes"
        return self.altura()


def rubro_negra_para_234(rn):
    """Mostra a equivalência: cada nó PRETO + seus filhos VERMELHOS = 1 nó 2-3-4."""
    from .rubro_negra import VERMELHO
    NIL = rn.NIL

    def agrupa(no, pai=None):
        n = No234(pai)
        partes, filhos = [], []
        if no.esq is not NIL and no.esq.cor == VERMELHO:
            partes.append(no.esq)
            filhos += [no.esq.esq, no.esq.dir]
        else:
            filhos.append(no.esq)
        partes.append(no)
        if no.dir is not NIL and no.dir.cor == VERMELHO:
            partes.append(no.dir)
            filhos += [no.dir.esq, no.dir.dir]
        else:
            filhos.append(no.dir)
        n.chaves = [p.chave for p in partes]
        n.baldes = [p.lotes for p in partes]
        n.filhos = [agrupa(f, n) for f in filhos if f is not NIL]
        return n

    if rn.raiz is NIL:
        return None
    return agrupa(rn.raiz)
