# -*- coding: utf-8 -*-
# =====================================================================
# MISSAO 7 - CRUZAR QUEIMADA x SAUDE (Produto 1)
#
# Pergunta: os meses com MAIS focos de queimada tem MAIS internacoes
# por doencas respiratorias?
#
# O banco ja tem as duas tabelas, no mesmo formato:
#   queimadas_mensal -> ano | mes | mes_nome | uf | focos
#   saude            -> ano | mes | mes_nome | uf | internacoes
# Como as chaves sao as mesmas (uf, ano, mes), da pra JUNTAR com um JOIN.
# =====================================================================

import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Raiz do projeto = pasta acima de "scripts" (funciona em qualquer computador)
RAIZ = Path(__file__).resolve().parent.parent
from scipy.stats import spearmanr

sys.stdout.reconfigure(encoding="utf-8")

BANCO = RAIZ / "dados" / "queimadas_saude.db"
conexao = sqlite3.connect(BANCO)


# ---------------------------------------------------------------------
# PASSO A: JOIN - juntar queimadas e saude numa tabela so.
# O JOIN casa uma linha de cada tabela quando uf, ano E mes sao iguais.
#   q = apelido da tabela queimadas_mensal
#   s = apelido da tabela saude
sql_join = """
SELECT q.uf, q.ano, q.mes, q.focos, s.internacoes
FROM queimadas_mensal q
JOIN saude s
  ON q.uf = s.uf AND q.ano = s.ano AND q.mes = s.mes
ORDER BY q.uf, q.ano, q.mes
"""
base = pd.read_sql(sql_join, conexao)

print("Linhas depois do JOIN (deve dar 180 = 3 estados x 60 meses):", len(base))
print(base.head())
print("\nTotais por estado:")
print(base.groupby("uf")[["focos", "internacoes"]].sum())


# ---------------------------------------------------------------------
# PASSO B: DEFASAGEM (lag).
# A internacao pode subir DEPOIS do pico de fumaca, nao no mesmo mes.
# .shift(1) puxa o valor do mes ANTERIOR (dentro de cada estado).
#   lag0 = focos do mesmo mes
#   lag1 = focos do mes anterior
#   lag2 = focos de 2 meses antes
# O primeiro mes de cada estado fica vazio (NaN) - nao tem "mes anterior".
base = base.sort_values(["uf", "ano", "mes"])
for lag in [0, 1, 2]:
    base[f"lag{lag}"] = base.groupby("uf")["focos"].shift(lag)


# ---------------------------------------------------------------------
# PASSO C: CORRELACAO GERAL (Spearman).
# Por que Spearman e nao Pearson? Focos tem distribuicao MUITO torta
# (poucos meses com milhares, muitos com poucos). Spearman usa a ORDEM
# dos valores, entao nao se engana com os picos.
#   rho perto de 0  -> nao ha relacao
#   rho perto de +1 -> mais fogo, mais internacao
#   p < 0,05        -> improvavel ser so acaso
print("\n=== Correlacao geral (3 estados juntos) ===")
for lag in [0, 1, 2]:
    d = base.dropna(subset=[f"lag{lag}"])
    rho, p = spearmanr(d[f"lag{lag}"], d["internacoes"])
    print(f"defasagem {lag} mes(es): rho = {rho:.2f}   p = {p:.4f}")


# ---------------------------------------------------------------------
# PASSO D: CORRELACAO POR ESTADO.
print("\n=== Correlacao por estado ===")
for uf, grupo in base.groupby("uf"):
    linha = []
    for lag in [0, 1, 2]:
        d = grupo.dropna(subset=[f"lag{lag}"])
        rho, p = spearmanr(d[f"lag{lag}"], d["internacoes"])
        linha.append(f"lag{lag}: rho={rho:.2f} (p={p:.3f})")
    print(uf, "|", "  ".join(linha))


# ---------------------------------------------------------------------
# PASSO E: TIRAR A SAZONALIDADE.
# Problema: as queimadas picam em agosto/setembro, mas as internacoes
# respiratorias sao maiores em marco-maio (epoca de chuva). Esses dois
# ciclos se "escondem". Solucao: comparar cada mes com a MEDIA do mesmo
# mes (naquele estado) nos 5 anos. Sobra so o "quanto fugiu do normal".
#   anomalia = valor do mes - media daquele mes/estado
for coluna in ["focos", "internacoes"]:
    media_do_mes = base.groupby(["uf", "mes"])[coluna].transform("mean")
    base[coluna + "_anom"] = base[coluna] - media_do_mes

print("\n=== Correlacao SEM sazonalidade (anomalias) ===")
for uf, grupo in list(base.groupby("uf")) + [("TODOS", base)]:
    rho, p = spearmanr(grupo["focos_anom"], grupo["internacoes_anom"])
    print(f"{uf}: rho = {rho:.2f}   p = {p:.3f}")


# ---------------------------------------------------------------------
# PASSO F: SALVAR a tabela cruzada no banco (vai servir nos graficos
# da Missao 8). Fica como 'base_cruzada'.
base.to_sql("base_cruzada", conexao, if_exists="replace", index=False)

print("\nLinhas na tabela 'base_cruzada' (deve dar 180):")
print(pd.read_sql("SELECT COUNT(*) AS total FROM base_cruzada", conexao))

conexao.close()
print("\nPronto! Missao 7 completa: tabela 'base_cruzada' no banco. :)")
