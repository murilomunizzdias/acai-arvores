"""Registro de um lote de açaí que chega de barco à Feira do Açaí (Ver-o-Peso).

A CHAVE das árvores é o preço da rasa (R$, inteiro). Vários lotes podem ter o
mesmo preço -> ver a política de repetidos no README (balde por nó).
"""
import csv
from dataclasses import dataclass


@dataclass
class Lote:
    id: str          # identificador único do lote (ex.: "L07")
    preco: int       # preço da rasa em reais -> CHAVE da árvore
    origem: str      # ilha/município de onde veio
    barco: str       # nome do barco
    rasas: int       # quantidade de rasas no lote
    chegada: str     # horário de chegada na feira (HH:MM)

    def __str__(self):
        return (f"{self.id} | R$ {self.preco}/rasa | {self.rasas} rasas | "
                f"{self.origem} | barco {self.barco} | {self.chegada}")


def carregar_csv(caminho):
    lotes = []
    with open(caminho, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            lotes.append(Lote(linha["id"], int(linha["preco"]), linha["origem"],
                              linha["barco"], int(linha["rasas"]), linha["chegada"]))
    return lotes
