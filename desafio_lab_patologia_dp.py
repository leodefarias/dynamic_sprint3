"""
Desafio: Gestão de insumos de um laboratório de patologia
--------------------------------------------------------

Contexto
========
Em um laboratório de patologia, técnicos utilizam insumos (reagentes, lâminas, cassetes, etc.)
com lotes diferentes (quantidade, custo e validade). Há uma demanda diária de consumo para
cada insumo. O objetivo é:
  (1) Registrar o consumo diário em ordem cronológica (Fila)
  (2) Permitir consultas em ordem inversa (Pilha)
  (3) Localizar insumos/lotes por nome ou código (Busca sequencial e binária)
  (4) Organizar listas por quantidade consumida ou por validade (Merge Sort e Quick Sort)
  (5) Planejar, via Programação Dinâmica, a escolha de lotes por dia para atender a demanda
      com custo mínimo, penalizando desperdício (sobra por abrir volumes acima da demanda)
      e risco de expiração (lotes próximos do vencimento).
  (6) Emitir um pequeno relatório final.

Observações
===========
- O DP abaixo resolve um *knapsack com cobertura mínima*: escolher combinações de lotes
  (com estoque limitado) de modo que o volume total >= demanda do dia, minimizando custo
  + penalidades. Para tornar o DP compacto, discretizamos o volume em unidades inteiras.
- O código foca em clareza didática, usando apenas Python padrão.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import deque
import bisect
import math
import random
import time

# =============================================================
# Modelos de domínio
# =============================================================

@dataclass
class Lote:
    id_lote: str
    nome_insumo: str
    volume_unidade: int
    unidades: int
    custo_unidade: float
    dias_para_validade: int

    def penalidade_validade(self, peso: float = 0.02) -> float:
        urgencia = max(0, 60 - self.dias_para_validade)
        return peso * urgencia * self.custo_unidade

    def __str__(self) -> str:
        return (f"{self.nome_insumo} | Lote {self.id_lote} | un={self.volume_unidade} | "
                f"estoque={self.unidades} | custo={self.custo_unidade:.2f} | "
                f"validade={self.dias_para_validade}d")


@dataclass
class ConsumoDia:
    dia: int
    nome_insumo: str
    demanda_volume: int
    atendido: bool = False
    custo_planejado: float = 0.0
    lotes_escolhidos: List[Tuple[str, int]] = field(default_factory=list)


# =============================================================
# FILA e PILHA
# =============================================================

class FilaConsumo:
    def __init__(self) -> None:
        self._fila: deque[ConsumoDia] = deque()

    def registrar(self, consumo: ConsumoDia) -> None:
        self._fila.append(consumo)

    def proximo(self) -> Optional[ConsumoDia]:
        return self._fila.popleft() if self._fila else None

    def __len__(self) -> int:
        return len(self._fila)

    def como_lista(self) -> List[ConsumoDia]:
        return list(self._fila)


class PilhaConsulta:
    def __init__(self) -> None:
        self._pilha: List[ConsumoDia] = []

    def empilhar(self, consumo: ConsumoDia) -> None:
        self._pilha.append(consumo)

    def desempilhar(self) -> Optional[ConsumoDia]:
        return self._pilha.pop() if self._pilha else None

    def __len__(self) -> int:
        return len(self._pilha)


# =============================================================
# BUSCA (sequencial e binária)
# =============================================================

def busca_sequencial(lotes: List[Lote], nome: str) -> List[Lote]:
    nome_l = nome.lower()
    return [l for l in lotes if nome_l in l.nome_insumo.lower()]


def busca_binaria(lotes_ordenados: List[Lote], nome: str) -> List[Lote]:
    chave = nome.lower()
    chaves = [l.nome_insumo.lower() for l in lotes_ordenados]
    i = bisect.bisect_left(chaves, chave)
    resultado: List[Lote] = []
    while i < len(lotes_ordenados) and lotes_ordenados[i].nome_insumo.lower() == chave:
        resultado.append(lotes_ordenados[i])
        i += 1
    return resultado


# =============================================================
# ORDENAÇÃO (Merge Sort iterativo e Quick Sort)
# =============================================================

def merge_sort_iterativo(lista: List[Lote], chave=lambda x: x) -> List[Lote]:
    if len(lista) <= 1:
        return lista[:]
    a = lista[:]
    n = len(a)
    tamanho = 1
    while tamanho < n:
        for inicio in range(0, n, 2 * tamanho):
            meio = min(inicio + tamanho, n)
            fim = min(inicio + 2 * tamanho, n)
            esquerda = a[inicio:meio]
            direita = a[meio:fim]
            i = j = 0
            k = inicio
            while i < len(esquerda) and j < len(direita):
                if chave(esquerda[i]) <= chave(direita[j]):
                    a[k] = esquerda[i]; i += 1
                else:
                    a[k] = direita[j]; j += 1
                k += 1
            while i < len(esquerda):
                a[k] = esquerda[i]; i += 1; k += 1
            while j < len(direita):
                a[k] = direita[j]; j += 1; k += 1
        tamanho *= 2
    return a


def quick_sort(lista: List[Lote], chave=lambda x: x) -> List[Lote]:
    a = lista[:]
    def _qs(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        pivo = chave(a[(lo + hi)//2])
        i, j = lo, hi
        while i <= j:
            while chave(a[i]) < pivo: i += 1
            while chave(a[j]) > pivo: j -= 1
            if i <= j:
                a[i], a[j] = a[j], a[i]
                i += 1; j -= 1
        _qs(lo, j); _qs(i, hi)
    _qs(0, len(a)-1)
    return a


# =============================================================
# PROGRAMAÇÃO DINÂMICA
# =============================================================

def planejar_dia_dp(lotes: List[Lote], demanda_volume: int, 
                    peso_sobra: float = 0.01, peso_validade: float = 1.0) -> Tuple[float, List[Tuple[str,int]]]:
    if demanda_volume <= 0:
        return 0.0, []

    itens: List[Tuple[int, float, str]] = []
    mapa_indices: List[Tuple[int, str]] = []
    for lote in lotes:
        custo_base = lote.custo_unidade + peso_validade * lote.penalidade_validade()
        quantidade = lote.unidades
        k = 1
        while quantidade > 0:
            usar = min(k, quantidade)
            volume = lote.volume_unidade * usar
            custo = custo_base * usar
            itens.append((volume, custo, lote.id_lote))
            mapa_indices.append((usar, lote.id_lote))
            quantidade -= usar
            k <<= 1

    if not itens:
        return math.inf, []

    capacidade_max = demanda_volume + max(v for v,_,_ in itens) - 1
    INF = 10**15

    dp = [INF]*(capacidade_max+1)
    rec: List[Optional[Tuple[int,int]]] = [None]*(capacidade_max+1)
    dp[0] = 0.0

    for idx, (vol, custo, _) in enumerate(itens):
        for c in range(capacidade_max, vol-1, -1):
            cand = dp[c - vol] + custo
            if cand < dp[c]:
                dp[c] = cand
                rec[c] = (idx, c - vol)

    melhor_c = None
    melhor_total = INF
    for c in range(demanda_volume, capacidade_max+1):
        if dp[c] >= INF: 
            continue
        total = dp[c] + peso_sobra*(c - demanda_volume)
        if total < melhor_total:
            melhor_total = total
            melhor_c = c

    if melhor_c is None:
        return math.inf, []

    conta_por_lote: Dict[str,int] = {}
    c = melhor_c
    while c > 0 and rec[c] is not None:
        idx, prev = rec[c]
        usar, id_lote = mapa_indices[idx]
        conta_por_lote[id_lote] = conta_por_lote.get(id_lote, 0) + usar
        c = prev

    escolhas = [(lid, qtd) for lid, qtd in conta_por_lote.items()]
    return melhor_total, escolhas


# =============================================================
# Geração de dados sintéticos
# =============================================================

def gerar_lotes(seed: int = 42) -> List[Lote]:
    random.seed(seed)
    nomes = ["HematoFix", "Paraform", "Xileno", "Eosina", "Hematoxilina", "Cassetes", "Laminas"]
    lotes: List[Lote] = []
    idc = 1
    for nome in nomes:
        for _ in range(random.randint(1, 3)):
            lotes.append(Lote(
                id_lote=f"L{idc:03d}",
                nome_insumo=nome,
                volume_unidade=random.choice([5, 10, 20, 50]),
                unidades=random.randint(1, 8),
                custo_unidade=round(random.uniform(10, 80), 2),
                dias_para_validade=random.randint(5, 180)
            ))
            idc += 1
    return lotes


def gerar_consumo(nome_insumo: str, dias: int = 7, seed: int = 7) -> FilaConsumo:
    random.seed(seed)
    fila = FilaConsumo()
    for d in range(1, dias+1):
        demanda = random.choice([20, 30, 40, 50, 60, 80])
        fila.registrar(ConsumoDia(dia=d, nome_insumo=nome_insumo, demanda_volume=demanda))
    return fila


# =============================================================
# Utilidades e relatório
# =============================================================

def ordenar_por_validade(lotes: List[Lote]) -> List[Lote]:
    return merge_sort_iterativo(lotes, chave=lambda l: l.dias_para_validade)


def ordenar_por_consumo(qtd_por_insumo: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
    class Wrapper:
        def __init__(self, t): self.t = t
        def __lt__(self, outro): return self.t[1] > outro.t[1]
    lista_aux = [Wrapper(t) for t in qtd_por_insumo]
    lista_ordenada = quick_sort(lista_aux, chave=lambda x: x)
    return [w.t for w in lista_ordenada]


def imprimir_top(lotes: List[Lote], n=5, titulo="") -> None:
    if titulo:
        print("\n" + titulo)
        print("-"*len(titulo))
    for lote in lotes[:n]:
        print(" ", str(lote))


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":
    print("\n🏥 Desafio – Gestão de Insumos com Programação Dinâmica\n" + "="*70)

    lotes = gerar_lotes()
    print(f"Total de lotes: {len(lotes)}")

    alvo = "Hematoxilina"
    encontrados_seq = busca_sequencial(lotes, alvo)
    lotes_ordenados = merge_sort_iterativo(lotes, chave=lambda l: l.nome_insumo.lower())
    encontrados_bin = busca_binaria(lotes_ordenados, alvo)
    print(f"\n🔎 Busca sequencial por '{alvo}': {len(encontrados_seq)} lotes")
    print(f"🔎 Busca binária por '{alvo}': {len(encontrados_bin)} lotes")

    lotes_por_validade = ordenar_por_validade(lotes)
    imprimir_top(lotes_por_validade, titulo="Lotes mais urgentes por validade (Merge Sort)")

    fila = gerar_consumo(nome_insumo="Hematoxilina", dias=7)
    pilha = PilhaConsulta()
    for c in fila.como_lista():
        pilha.empilhar(c)
    print(f"\n🗂️  Fila possui {len(fila)} registros; Pilha possui {len(pilha)} para consulta inversa.")

    print("\n🧠 Planejamento ótimo por DP para 'Hematoxilina' (7 dias)")
    consumidos: Dict[str, int] = {}
    tempo_ini = time.time()

    lotes_alvo = [l for l in lotes if l.nome_insumo == "Hematoxilina"]
    lotes_alvo = ordenar_por_validade(lotes_alvo)
    imprimir_top(lotes_alvo, titulo="Lotes disponíveis (alvo)")

    estoque: Dict[str, Lote] = {l.id_lote: Lote(**{**l.__dict__}) for l in lotes}

    while len(fila):
        dia = fila.proximo()
        if not dia:
            break
        disponiveis = [estoque[l.id_lote] for l in estoque.values() if l.nome_insumo == dia.nome_insumo and l.unidades > 0]
        custo, escolhas = planejar_dia_dp(disponiveis, dia.demanda_volume,
                                       peso_sobra=0.02, peso_validade=1.0)
        dia.atendido = math.isfinite(custo)
        dia.custo_planejado = custo if dia.atendido else 0.0
        dia.lotes_escolhidos = escolhas
        if dia.atendido:
            for lid, qtd in escolhas:
                estoque[lid].unidades -= qtd
                consumidos[dia.nome_insumo] = consumidos.get(dia.nome_insumo, 0) + estoque[lid].volume_unidade * qtd
        print(f"  Dia {dia.dia:02d} | Demanda={dia.demanda_volume:3d} | Atendido={dia.atendido} | Custo≈{dia.custo_planejado:7.2f} | Escolhas={escolhas}")

    tempo_total = time.time() - tempo_ini

    ranking_consumo = ordenar_por_consumo(list(consumidos.items()))

    print("\n📊 Relatório")
    print("-"*10)
    print(f"Tempo de planejamento (DP): {tempo_total:.4f}s")
    print("Top consumos por insumo (desc):")
    for nome, vol in ranking_consumo[:5]:
        print(f"  - {nome}: {vol} unidades de volume")

    print("\n📚 Últimas consultas (Pilha, inverso)")
    for _ in range(3):
        x = pilha.desempilhar()
        if x:
            print(f"  Dia {x.dia:02d} -> {x.nome_insumo} demanda={x.demanda_volume}")

    print("\n✅ Demonstração concluída.")
