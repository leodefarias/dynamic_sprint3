# 🏥 Desafio – Gestão de Insumos com Programação Dinâmica

## 👩‍💻 Integrantes
- Leonardo de Farias - RM: 555211
- Gustavo Laur - RM: 556603
- Giancarlo Cestarolli - RM: 555248

## 📌 Contexto
Em um laboratório de patologia, técnicos utilizam insumos (reagentes, lâminas, cassetes, etc.) com lotes diferentes (quantidade, custo e validade). Há uma demanda diária de consumo para cada insumo. 

Este projeto implementa uma solução computacional que simula e otimiza a gestão desses insumos, atendendo às demandas diárias de forma eficiente.

## 🎯 Objetivos
- **Fila e Pilha (30 pts)**
  - Implementar uma **fila** para registrar o consumo diário em ordem cronológica.
  - Implementar uma **pilha** para simular consultas em ordem inversa (últimos consumos primeiro).

- **Estruturas de Busca (20 pts)**
  - Implementar **busca sequencial** e **busca binária** para localizar insumos específicos nos registros de consumo.

- **Ordenação (30 pts)**
  - Implementar algoritmos de ordenação (**Merge Sort** e **Quick Sort**) para organizar insumos por validade ou quantidade consumida.

- **Programação Dinâmica**
  - Planejar automaticamente a escolha de lotes para atender à demanda diária com **custo mínimo**, penalizando:
    - **Desperdício** (sobra de volume).
    - **Risco de expiração** (uso de lotes próximos do vencimento).

- **Relatório (20 pts)**
  - Geração de um relatório final com estatísticas, ranking de consumo e resumo das decisões.

## 🛠️ Tecnologias utilizadas
- **Python 3** (padrão, sem bibliotecas externas além da padrão).
- Estruturas de dados básicas: listas, dicionários, deque.
- Técnicas de programação: **Fila, Pilha, Busca, Ordenação, Programação Dinâmica**.

## 📂 Estrutura do projeto
```
📦 desafio_lab_patologia
 ┣ 📜 desafio_lab_patologia_dp.py   # Código principal
 ┗ 📜 README.md                     # Documentação do projeto
```

## ▶️ Como executar
1. Clone o repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO/desafio_lab_patologia.git
   ```
2. Acesse a pasta do projeto:
   ```bash
   cd desafio_lab_patologia
   ```
3. Execute o programa:
   ```bash
   python desafio_lab_patologia_dp.py
   ```

## 📊 Exemplo de saída
```
🏥 Desafio – Gestão de Insumos com Programação Dinâmica
======================================================================
Total de lotes: 15

🔎 Busca sequencial por 'Hematoxilina': 2 lotes
🔎 Busca binária por 'Hematoxilina': 2 lotes

Lotes mais urgentes por validade (Merge Sort)
--------------------------------------------
 HematoFix | Lote L001 | un=10 | estoque=5 | custo=50.00 | validade=12d
 ...

🧠 Planejamento ótimo por DP para 'Hematoxilina' (7 dias)
  Dia 01 | Demanda= 30 | Atendido=True | Custo≈ 120.50 | Escolhas=[('L005', 2)]
  ...

📊 Relatório
----------
Tempo de planejamento (DP): 0.0123s
Top consumos por insumo (desc):
  - Hematoxilina: 280 unidades de volume
  ...

📚 Últimas consultas (Pilha, inverso)
  Dia 07 -> Hematoxilina demanda=50
  Dia 06 -> Hematoxilina demanda=30
  Dia 05 -> Hematoxilina demanda=20

✅ Demonstração concluída.
```
