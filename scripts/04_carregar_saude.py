# -*- coding: utf-8 -*-
# =====================================================================
# MISSAO 3 (parte 1) - Ler o arquivo SUJO de saude do DataSUS
#
# Objetivo desta parte: so fazer o pandas LER o arquivo direito.
# Depois (parte 2) a gente limpa e joga no banco.
#
# O arquivo tem 3 pegadinhas; cada uma se resolve com UM parametro
# dentro do pd.read_csv(). Preencha o TODO com os 3 parametros.
# =====================================================================

import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Raiz do projeto = pasta acima de "scripts" (funciona em qualquer computador)
RAIZ = Path(__file__).resolve().parent.parent

sys.stdout.reconfigure(encoding="utf-8")

ARQUIVO = RAIZ / "dados" / "brutos" / "saude" / "internacoes_resp_AM_PA_MA_2020_2024.csv"

# ---------------------------------------------------------------------
# AS 3 PEGADINHAS E SEUS PARAMETROS:
#
#   Pegadinha 1: o separador e ponto-e-virgula, nao virgula
#       -> sep=";"
#
#   Pegadinha 2: o arquivo e latin-1 (por isso os acentos quebram)
#       -> encoding="latin-1"
#
#   Pegadinha 3: as 5 primeiras linhas sao lixo; o cabecalho esta na 6a
#       -> skiprows=5     (pula as 5 primeiras linhas)
#
# TODO: complete a chamada abaixo com os 3 parametros, separados por virgula.
#       Modelo: pd.read_csv(ARQUIVO, sep=..., encoding=..., skiprows=...)
saude = pd.read_csv(ARQUIVO,sep= ";", encoding="latin-1", skiprows=5)   # <- adicione os 3 parametros aqui dentro

# ---------------------------------------------------------------------
# Conferindo se leu certo:
print("Colunas encontradas:", list(saude.columns))
print("Numero de linhas:", len(saude))
print("\nPrimeiras 15 linhas:")
print(saude.head(15))


# =====================================================================
# MISSAO 3 (parte 2) - LIMPAR a tabela
# =====================================================================

# ---------------------------------------------------------------------
# PASSO A: renomear as colunas pra nomes simples (sem acento, faceis de usar).
# Isso evita ter que digitar "Ano/mês atendimento" com acento toda hora.
# DICA: saude.columns = ["periodo", "AM", "PA", "MA", "Total"]
#       (a ORDEM tem que bater com a ordem atual das 5 colunas)
# TODO: escreva a linha que renomeia as colunas
saude.columns = ["periodo", "AM", "PA", "MA", "Total"]  # <- troque None pela lista de 5 nomes

print("\nColunas renomeadas:", list(saude.columns))


# ---------------------------------------------------------------------
# PASSO B: manter SO as linhas de MES, jogando fora subtotais e rodape.
# As linhas boas tem formato "Mes/Ano" -> contem "/20" (ex.: "Janeiro/2024").
# As linhas ruins ("2020", "Total", "Fonte:...", "Notas:...") NAO tem "/20".
#
# Como filtrar no pandas:
#   saude["periodo"].str.contains("/20")  -> devolve True/False pra cada linha
#   saude[ <esses True/False> ]           -> fica so com as linhas True
#
# DICA: so_meses = saude[ saude["periodo"].str.contains("/20") ]
# TODO: escreva o filtro que mantem so as linhas de mes
so_meses = saude[ saude["periodo"].str.contains("/20") ]   # <- troque None pelo filtro

print("\nLinhas so de meses (deve dar 67):", len(so_meses))
print(so_meses.head())


# ---------------------------------------------------------------------
# PASSO C: limpar os NUMEROS.
# Problema 1: onde nao houve internacao, esta escrito "-" em vez de 0.
# Problema 2: por causa do "-", as colunas AM e MA viraram TEXTO, nao numero.
#
# C1) Trocar todo "-" por 0.
#     DICA: so_meses = so_meses.replace("-", 0)
#     (o .replace troca um valor por outro na tabela inteira)
# TODO C1: troque "-" por 0
so_meses = so_meses.replace("-", 0)   # <- use so_meses.replace("-", 0)

# C2) Garantir que AM, PA, MA e Total sejam numeros INTEIROS.
#     O "for" ja percorre as 4 colunas pra voce; falta so a conversao.
#     DICA: so_meses[coluna] = so_meses[coluna].astype(int)
#     (.astype(int) = "transforme em numero inteiro")
for coluna in ["AM", "PA", "MA", "Total"]:
    so_meses[coluna] =  so_meses[coluna].astype(int)  # <- use so_meses[coluna].astype(int)

# Conferindo: agora as 4 colunas devem aparecer como int (int64)
print("\nTipos depois da limpeza:")
print(so_meses.dtypes)
print("\nComo ficou:")
print(so_meses.head())


# ---------------------------------------------------------------------
# PASSO D: separar "periodo" em ANO e MES, e ficar so com 2020-2024.
# A coluna periodo tem o formato "..Junho/2019":
#   - ANTES da "/" esta o nome do mes (com ".." na frente)
#   - DEPOIS da "/" esta o ano
#
# Ferramenta nova: .str.split("/") quebra o texto no "/" e devolve 2 pedacos:
#   "..Junho/2019"  ->  ["..Junho", "2019"]
#                         pedaco[0]   pedaco[1]
# Pra pegar um pedaco use .str[0] (o primeiro) ou .str[1] (o segundo).

# D1) O ANO = pedaco DEPOIS da "/", virando numero.
#     DICA: so_meses["ano"] = so_meses["periodo"].str.split("/").str[1].astype(int)
# TODO D1:
so_meses["ano"] = so_meses["periodo"].str.split("/").str[1].astype(int)

# D2) O NOME DO MES = pedaco ANTES da "/", sem o "..".
#     (.str.replace("..", "", regex=False) apaga os dois pontinhos)
#     DICA: so_meses["mes_nome"] = so_meses["periodo"].str.split("/").str[0].str.replace("..", "", regex=False)
# TODO D2:
so_meses["mes_nome"] = so_meses["periodo"].str.split("/").str[0].str.replace("..", "", regex=False).str.strip()
# TODO D2:

# D3) Ficar so com 2020 em diante (jogar fora os 7 meses de 2019).
#     DICA: so_meses = so_meses[ so_meses["ano"] >= 2020 ]
# TODO D3:
so_meses = so_meses[ so_meses["ano"] >= 2020 ]


# ---------------------------------------------------------------------
# PASSO E: transformar o NOME do mes em NUMERO (1 a 12).
# Por que? Pra ordenar certo (Fevereiro vem depois de Janeiro, e nao em
# ordem alfabetica) e pra casar com o mes das queimadas la na frente.
#
# Ferramenta nova: um DICIONARIO + o .map()
#   - Um DICIONARIO liga uma CHAVE a um VALOR:  {"Janeiro": 1, "Fevereiro": 2, ...}
#   - O .map(dicionario) olha cada valor da coluna e troca pelo que o dicionario diz.
#
# O dicionario ja esta pronto pra voce (sao 12, chato de digitar na mao):
meses = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12,
}
# DICA: so_meses["mes"] = so_meses["mes_nome"].map(meses)
# TODO E1:
so_meses["mes"] = so_meses["mes_nome"].map(meses)

print("\nMes virou numero (compare as colunas mes_nome e mes):")
print(so_meses[["ano", "mes_nome", "mes"]].head())


# ---------------------------------------------------------------------
# PASSO F: virar a tabela de "LARGA" pra "COMPRIDA" (o melt).
# Hoje os estados sao COLUNAS (AM, PA, MA). Queremos eles como LINHAS.
#
# ANTES (larga):                  DEPOIS (comprida):
#   ano mes  AM   PA   MA           ano mes uf  internacoes
#   2020 1  1092 3922 3091          2020 1  AM   1092
#                                   2020 1  PA   3922
#                                   2020 1  MA   3091
#
# A ferramenta: .melt()
#   id_vars    = colunas que FICAM como estao (identificam a linha): ano, mes, mes_nome
#   value_vars = colunas que viram LINHAS: AM, PA, MA
#   var_name   = nome da coluna nova que guarda "de qual estado": "uf"
#   value_name = nome da coluna nova que guarda o numero: "internacoes"
#
# DICA:
#   saude_longo = so_meses.melt(
#       id_vars=["ano", "mes", "mes_nome"],
#       value_vars=["AM", "PA", "MA"],
#       var_name="uf",
#       value_name="internacoes",
#   )
# TODO F1:
saude_longo = so_meses.melt(
    id_vars=["ano", "mes", "mes_nome"],
    value_vars=["AM", "PA", "MA"],
    var_name="uf",
    value_name="internacoes",
)

print("\nTabela comprida (deve dar 180 linhas = 60 meses x 3 estados):", len(saude_longo))
print(saude_longo.head(6))


# =====================================================================
# PASSO G: salvar a tabela limpa no BANCO (igual voce fez na Missao 1!)
# =====================================================================
BANCO = RAIZ / "dados" / "queimadas_saude.db"
conexao = sqlite3.connect(BANCO)

# Salvar saude_longo numa tabela chamada "saude".
# Mesma ideia da Missao 1 (la a tabela era "focos"):
# DICA: saude_longo.to_sql("saude", conexao, if_exists="replace", index=False)
# TODO G1: escreva a linha do to_sql aqui embaixo
saude_longo.to_sql("saude", conexao, if_exists="replace", index=False)


# Conferir se gravou (deve dar 180):
conferencia = pd.read_sql("SELECT COUNT(*) AS total FROM saude", conexao)
print("\nLinhas na tabela 'saude' do banco:")
print(conferencia)

conexao.close()
print("\nPronto! Dados de saude limpos e salvos no banco. :)")

print("\nApos separar ano/mes e tirar 2019 (deve dar 60 linhas):", len(so_meses))
print(so_meses.head())
