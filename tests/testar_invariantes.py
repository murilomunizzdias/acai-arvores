"""Teste de estresse: milhares de inserções/remoções aleatórias, conferindo as
propriedades das árvores depois de CADA operação e comparando com um dicionário.

Executar a partir da pasta do projeto:  python -m tests.testar_invariantes
"""
import random

from arvores.lote import Lote
from arvores.rubro_negra import ArvoreRubroNegra
from arvores.arvore234 import Arvore234, rubro_negra_para_234


def rodar(semente, operacoes=3000):
    rnd = random.Random(semente)
    rn, t = ArvoreRubroNegra(), Arvore234()
    referencia = {}          # preço -> lista de ids
    cont = 0
    for _ in range(operacoes):
        if rnd.random() < 0.6 or not referencia:
            cont += 1
            lote = Lote(f"L{cont}", rnd.randint(1, 300), "X", "B", 1, "00:00")
            rn.inserir(lote)
            t.inserir(Lote(lote.id, lote.preco, "X", "B", 1, "00:00"))
            referencia.setdefault(lote.preco, []).append(lote.id)
        else:
            preco = rnd.choice(list(referencia))
            if rnd.random() < 0.5:
                id_ = rnd.choice(referencia[preco])
                rn.remover(preco, id_)
                t.remover(preco, id_)
                referencia[preco].remove(id_)
                if not referencia[preco]:
                    del referencia[preco]
            else:
                rn.remover(preco)
                t.remover(preco)
                del referencia[preco]
        rn.verificar()
        t.verificar()
        assert [n.chave for n in rn.em_ordem()] == sorted(referencia)
        assert rn.qtd_nos == t.qtd_chaves == len(referencia)
        if referencia:
            view = rubro_negra_para_234(rn)
            assert view is not None
    # buscas e faixas
    for k in range(0, 320):
        a, _ = rn.buscar(k)
        b, _, _ = t.buscar(k)
        assert (a is not None) == (b is not None) == (k in referencia)
    for _ in range(50):
        a = rnd.randint(0, 300)
        b = rnd.randint(a, 300)
        esperado = sorted(i for p, ids in referencia.items() if a <= p <= b for i in ids)
        assert sorted(l.id for l in rn.faixa(a, b)) == esperado
        assert sorted(l.id for l in t.faixa(a, b)) == esperado


def checar_visao_234():
    """A visão 2-3-4 da Rubro-Negra também precisa ser uma 2-3-4 válida."""
    rnd = random.Random(7)
    rn = ArvoreRubroNegra()
    for i in range(500):
        rn.inserir(Lote(f"L{i}", rnd.randint(1, 10000), "X", "B", 1, "00:00"))
        if i % 3 == 0:
            n = rnd.choice(rn.em_ordem())
            rn.remover(n.chave)
        t = Arvore234()
        t.raiz = rubro_negra_para_234(rn)
        t.verificar()
        assert t.altura() == rn.verificar() - 1   # altura negra (sem contar NIL)


if __name__ == "__main__":
    for s in range(15):
        rodar(s)
    checar_visao_234()
    print("OK - todas as propriedades Rubro-Negra e 2-3-4 conferidas em 45.000 operações.")
