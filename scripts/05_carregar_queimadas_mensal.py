# -*- coding: utf-8 -*-
# =====================================================================
# MISSAO 4 - Carregar as QUEIMADAS MENSAIS (2020-2024) no banco
#
# Por que de novo? A tabela 'focos' so tem 2024 (brutos, todos satelites).
# Pra correlacionar com a saude (2020-2024) precisamos dos focos MENSAIS
# por estado, do satelite de referencia, de 2020 a 2024. Isso esta nos
# 3 CSVs "estatistica" (focos_mensal_PA/AM/MA.csv).
#
# Esses arquivos sao "largos" (1 linha por ANO, 1 coluna por MES) -
# a MESMA receita da saude: largo -> comprido -> salvar.
# =====================================================================

import pandas as pd
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

PASTA = r"C:\Users\luis\Downloads\big data\dados\brutos\queimadas\estatistica"
BANCO = r"C:\Users\luis\Downloads\big data\dados\queimadas_saude.db"

# Cada arquivo e de um estado. O dicionario liga: nome do arquivo -> sigla (UF).
arquivos_uf = {
    "focos_mensal_PA.csv": "PA",
    "focos_mensal_AM.csv": "AM",
    "focos_mensal_MA.csv": "MA",
}

# ---------------------------------------------------------------------
# PASSO A (JA PRONTO): ler os 3 CSVs, marcar a UF, e juntar num so.
# O "for" percorre o dicionario: 'arquivo' = nome, 'uf' = sigla.
lista = []
for arquivo, uf in arquivos_uf.items():
    caminho = PASTA + "\\" + arquivo
    tabela = pd.read_csv(caminho)       # separador virgula, utf-8 (padrao)
    tabela["uf"] = uf                   # cria uma coluna "uf" com PA/AM/MA
    lista.append(tabela)

focos_wide = pd.concat(lista, ignore_index=True)

print("Colunas:", list(focos_wide.columns))
print("Linhas (3 estados juntos):", len(focos_wide))
print("\nPrimeiras linhas:")
print(focos_wide.head())
print("\nValores unicos da coluna Ano (repare no fim):")
print(focos_wide["Ano"].unique())


# ---------------------------------------------------------------------
# PASSO B: ficar so com os anos 2020 a 2024.
# Isso joga fora 1998-2019, 2025-2026 E as linhas Minimo/Media/Maximo
# (porque nenhuma delas esta na lista de anos que queremos).
#
# Ferramenta nova: .isin([lista]) -> True se o valor ESTA na lista.
#   (como o "/20" de antes era um teste True/False, aqui o teste e
#    "esse ano esta na minha lista de anos?")
# Lembre que Ano esta como TEXTO, entao a lista tambem e de texto ("2020").
#
# DICA: focos_wide = focos_wide[ focos_wide["Ano"].isin(["2020","2021","2022","2023","2024"]) ]
focos_wide = focos_wide[ focos_wide["Ano"].isin(["2020", "2021", "2022", "2023", "2024"]) ]

print("\nApos filtrar 2020-2024 (deve dar 15 = 5 anos x 3 estados):", len(focos_wide))
print(focos_wide[["Ano", "uf", "Janeiro", "Agosto", "Total"]])


# ---------------------------------------------------------------------
# PASSO C: virar de LARGO pra COMPRIDO (melt) - igual fizemos na saude.
# Os 12 meses (colunas) viram linhas; cada ano-estado gera 12 linhas.
colunas_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

focos_longo = focos_wide.melt(
    id_vars=["Ano", "uf"],          # o que fica (identifica a linha)
    value_vars=colunas_meses,       # as 12 colunas de mes viram linhas
    var_name="mes_nome",            # coluna nova com o nome do mes
    value_name="focos",             # coluna nova com o numero de focos
)

print("\nApos o melt (deve dar 180 = 15 x 12 meses):", len(focos_longo))


# ---------------------------------------------------------------------
# PASSO D: limpar e formatar (mesma receita da saude).
# D1) por garantia, trocar "-" por 0 (meses sem foco)
focos_longo = focos_longo.replace("-", 0)

# D2) focos vira numero inteiro
focos_longo["focos"] = focos_longo["focos"].astype(int)

# D3) nome do mes -> numero (mesmo dicionario da saude)
meses = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12,
}
focos_longo["mes"] = focos_longo["mes_nome"].map(meses)

# D4) Ano (texto) -> ano (numero)
focos_longo["ano"] = focos_longo["Ano"].astype(int)

# Deixar so as colunas que interessam, na ordem boa
queimadas_mensal = focos_longo[["ano", "mes", "mes_nome", "uf", "focos"]]

print("\nTabela final pronta:")
print(queimadas_mensal.head())
print("Tipos:", dict(queimadas_mensal.dtypes))


# ---------------------------------------------------------------------
# PASSO E: salvar no banco como a tabela 'queimadas_mensal'.
conexao = sqlite3.connect(BANCO)
queimadas_mensal.to_sql("queimadas_mensal", conexao, if_exists="replace", index=False)

# Conferir quantas linhas gravaram
print("\nLinhas na tabela 'queimadas_mensal' do banco (deve dar 180):")
print(pd.read_sql("SELECT COUNT(*) AS total FROM queimadas_mensal", conexao))

# Validacao esperta: o total de 2024 no PA tem que bater com os 56.070
# que achamos na Missao 2 (satelite de referencia AQUA_M-T).
print("\nValidacao - total de focos 2024 no PA (tem que dar ~56.070):")
print(pd.read_sql(
    "SELECT SUM(focos) AS total_pa_2024 FROM queimadas_mensal "
    "WHERE ano=2024 AND uf='PA'", conexao))

conexao.close()
print("\nPronto! Missao 4 completa: tabela 'queimadas_mensal' no banco. :)")
