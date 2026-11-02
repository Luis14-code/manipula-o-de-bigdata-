# -*- coding: utf-8 -*-
# =====================================================================
# MISSAO 1 - Criar o banco de dados e carregar os focos de 2024
#
# Objetivo: ler os 12 arquivos brutos de 2024 (3,19 milhoes de linhas)
# e guardar tudo numa tabela chamada 'focos' dentro de um banco SQLite.
#
# >>> Preencha os trechos marcados com TODO. <<<
# Quando terminar, rode e me mande o resultado + seu codigo.
# =====================================================================

import glob          # para achar varios arquivos de uma vez
import sqlite3       # o banco de dados (ja vem com o Python)
import pandas as pd  # para ler os CSVs e jogar no banco

# ---------------------------------------------------------------------
# Caminhos (ja deixei prontos pra voce)
PASTA_FOCOS = r"C:\Users\luis\Downloads\big data\dados\brutos\queimadas\mensal"
BANCO       = r"C:\Users\luis\Downloads\big data\dados\queimadas_saude.db"

# ---------------------------------------------------------------------
# PASSO 1: achar os 12 arquivos CSV da pasta mensal.
# DICA: glob.glob(PASTA_FOCOS + r"\*.csv") devolve uma lista de caminhos.
arquivos = glob.glob(PASTA_FOCOS + r"\*.csv")   # TODO: troque None pela chamada do glob
print("Arquivos encontrados:", len(arquivos))

# ---------------------------------------------------------------------
# PASSO 2: ler cada CSV e juntar todos num unico DataFrame.
# DICA: faca uma lista lendo cada arquivo com pd.read_csv(a),
#       depois junte tudo com pd.concat(lista, ignore_index=True).
lista_tabelas=[] 
for arquivo in arquivos:
    tabela_temporaria = pd.read_csv(arquivo)
    lista_tabelas.append(tabela_temporaria)
    
df = pd.concat(lista_tabelas, ignore_index=True)# TODO: monte o DataFrame com todos os focos de 2024
print("Total de linhas lidas:", len(df))
print("Colunas:", list(df.columns))

# ---------------------------------------------------------------------
# PASSO 3: conectar (e criar, se nao existir) o banco SQLite.
# DICA: sqlite3.connect(BANCO) devolve a "conexao" com o banco.
conexao = sqlite3.connect(BANCO)    # TODO: abra a conexao com o banco

# ---------------------------------------------------------------------
# PASSO 4: salvar o DataFrame como uma tabela chamada 'focos'.
# DICA: df.to_sql("focos", conexao, if_exists="replace", index=False)
#       (if_exists="replace" = se a tabela ja existir, substitui)
# TODO: escreva a linha que salva a tabela
df.to_sql("focos", conexao, if_exists="replace", index=False)
# ---------------------------------------------------------------------
# PASSO 5: conferir se deu certo, perguntando ao banco com SQL.
# DICA: pd.read_sql("SELECT COUNT(*) AS total FROM focos", conexao)
conferencia =pd.read_sql("SELECT COUNT(*) AS total FROM focos", conexao) # TODO: rode a consulta SQL que conta as linhas da tabela
print("Linhas dentro do banco:")
print(conferencia)

conexao.close()     # sempre feche a conexao no final
print("Pronto! Banco criado em:", BANCO)
