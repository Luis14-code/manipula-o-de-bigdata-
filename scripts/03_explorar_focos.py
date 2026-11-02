# -*- coding: utf-8 -*-
# =====================================================================
# MISSAO 2 - Fazer o banco "falar" com SQL
#
# O banco ja tem a tabela 'focos' com 3,19 milhoes de linhas.
# Agora voce vai PERGUNTAR coisas pra ele usando SQL.
#
# A ferramenta: pd.read_sql("<sua pergunta em SQL>", conexao)
#   -> devolve a resposta ja em formato de tabela (DataFrame).
#
# >>> Preencha os 4 TODO com o SQL de cada pergunta. <<<
# =====================================================================

import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding="utf-8")   # pra acentos nao quebrarem no terminal

BANCO = r"C:\Users\luis\Downloads\big data\dados\queimadas_saude.db"
conexao = sqlite3.connect(BANCO)

# =====================================================================
# MINI-GUIA DE SQL (tudo que voce precisa pras 4 perguntas)
# ---------------------------------------------------------------------
#   SELECT coluna, COUNT(*) AS apelido   -> escolhe colunas e CONTA linhas
#   FROM focos                           -> de qual tabela
#   GROUP BY coluna                      -> agrupa (ex.: 1 linha por estado)
#   ORDER BY apelido DESC                -> ordena (DESC = maior pro menor)
#   LIMIT 10                             -> so as 10 primeiras
#
# COUNT(*) conta quantas linhas cairam em cada grupo. E o coracao disso tudo.
# =====================================================================


# ---------------------------------------------------------------------
# PERGUNTA 1: Quantos focos tem em CADA ESTADO? (maior pro menor)
# DICA: SELECT estado, COUNT(*) AS focos FROM focos GROUP BY estado ORDER BY focos DESC
sql_estados = "SELECT estado, COUNT(*) AS focos FROM focos GROUP BY estado ORDER BY focos DESC"
print("\n=== Focos por estado ===")
print(pd.read_sql(sql_estados, conexao))


# ---------------------------------------------------------------------
# PERGUNTA 2: Quantos focos cada SATELITE registrou? (maior pro menor)
# (Isso vai te mostrar uma coisa IMPORTANTE - veja meu recado depois de rodar.)
# DICA: igual a de cima, mas agrupando por 'satelite' em vez de 'estado'.
sql_satelites = "SELECT SATELITE, COUNT(*) AS focos FROM focos GROUP BY SATELITE ORDER BY focos DESC"
print("\n=== Focos por satelite ===")
print(pd.read_sql(sql_satelites, conexao))


# ---------------------------------------------------------------------
# PERGUNTA 3: Quais os 10 MUNICIPIOS com mais focos?
# DICA: agrupe por municipio E estado (pra nao misturar cidades de nome igual),
#       ordene por focos DESC e use LIMIT 10.
#       SELECT municipio, estado, COUNT(*) AS focos FROM focos
#       GROUP BY municipio, estado ORDER BY focos DESC LIMIT 10
sql_municipios = "SELECT municipio, estado, COUNT(*) AS focos FROM focos GROUP BY municipio, estado ORDER BY focos DESC LIMIT 10"
print("\n=== Top 10 municipios ===")
print(pd.read_sql(sql_municipios, conexao))


# ---------------------------------------------------------------------
# PERGUNTA 4: Quantos focos em cada MES de 2024?
# A coluna de data e 'data_hora_gmt' (ex.: "2024-08-15 13:40:00").
# Pra pegar so o mes dela, o SQLite tem a funcao strftime('%m', data_hora_gmt).
# DICA: SELECT strftime('%m', data_hora_gmt) AS mes, COUNT(*) AS focos
#       FROM focos GROUP BY mes ORDER BY mes
sql_meses = "SELECT strftime('%m', data_hora_gmt) AS mes, COUNT(*) AS focos FROM focos GROUP BY mes ORDER BY mes"
print("\n=== Focos por mes ===")
print(pd.read_sql(sql_meses, conexao))





# PERGUNTA 4:
sql_AQUAMT="SELECT estado, COUNT(*) AS focos FROM focos WHERE satelite = 'AQUA_M-T' GROUP BY estado ORDER BY focos DESC"
print("\n=== Focos por estado (so AQUA_M-T) ===")
print(pd.read_sql(sql_AQUAMT,conexao))
conexao.close()
print("\nPronto! Voce acabou de fazer 5 consultas SQL. :)")