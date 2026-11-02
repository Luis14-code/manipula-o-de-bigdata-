# -*- coding: utf-8 -*-
# =====================================================================
# Script 00 - Teste de ambiente
# Objetivo: importar as 7 bibliotecas e confirmar que todas funcionam.
# Se este script rodar sem erro, o ambiente esta pronto para o projeto.
# =====================================================================

# Cada 'import' carrega uma biblioteca para dentro do nosso programa.
# O 'as' cria um apelido curto (convencao usada no mundo todo).
import pandas as pd        # manipulacao e limpeza de dados (tabelas)
import numpy as np         # operacoes numericas (a base de tudo)
import matplotlib          # graficos
import seaborn as sns      # graficos estatisticos bonitos
import sklearn             # machine learning / estatistica
import plotly              # graficos interativos (ex.: mapas)
import requests            # baixar dados da internet (APIs)

# Agora so imprimimos a versao de cada uma para confirmar que carregou.
print("Ambiente OK! Versoes instaladas:")
print("  pandas      ", pd.__version__)
print("  numpy       ", np.__version__)
print("  matplotlib  ", matplotlib.__version__)
print("  seaborn     ", sns.__version__)
print("  scikit-learn", sklearn.__version__)
print("  plotly      ", plotly.__version__)
print("  requests    ", requests.__version__)
print()
print("Tudo pronto para comecar a Etapa 2: baixar os dados.")
