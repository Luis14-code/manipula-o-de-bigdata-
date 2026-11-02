# -*- coding: utf-8 -*-
# =====================================================================
# Script 01 - Baixar historico de queimadas do INPE (2020-2024)
# Fonte: INPE / Programa Queimadas (dados abertos, focos de calor)
#
# Versao "a prova de queda":
#  - tenta cada mes ate 3 vezes (o servidor do INPE as vezes cai);
#  - salva cada mes num arquivo proprio e PULA os ja baixados, entao
#    voce pode rodar varias vezes que ele continua de onde parou;
#  - no fim, junta tudo num CSV unico e mostra quais meses faltam.
# =====================================================================

import os
import io
import sys
import time
import requests
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# ---- Configuracao -------------------------------------------------
BASE = ("https://dataserver-coids.inpe.br/queimadas/queimadas/"
        "focos/csv/mensal/Brasil/")

ANOS = range(2020, 2025)          # 2020 a 2024
MESES = range(1, 13)              # 1 a 12
ESTADOS_ALVO = [13, 15, 21]       # 13=Amazonas, 15=Para, 21=Maranhao

RAIZ = r"C:\Users\luis\Downloads\big data\dados\brutos\queimadas"
PASTA_MES = os.path.join(RAIZ, "mensal")      # um arquivo por mes
SAIDA = os.path.join(RAIZ, "focos_PA_AM_MA_2020_2024.csv")  # juntado

TENTATIVAS = 3                    # quantas vezes tentar cada mes
HEADERS = {"User-Agent": "Mozilla/5.0"}       # parecer um navegador

os.makedirs(PASTA_MES, exist_ok=True)

# ---- Funcao que baixa UM mes (com tentativas) ---------------------
def baixar_mes(ano, mes, sessao):
    destino = os.path.join(PASTA_MES, f"focos_{ano}{mes:02d}.csv")

    # Ja baixado antes? Pula.
    if os.path.exists(destino):
        return "pulado"

    url = BASE + f"focos_mensal_br_{ano}{mes:02d}.csv"
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            r = sessao.get(url, timeout=(30, 180), headers=HEADERS)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
            rec = df[df["estado_id"].isin(ESTADOS_ALVO)].copy()
            rec.to_csv(destino, index=False, encoding="utf-8")
            print(f"OK  {ano}-{mes:02d}: {len(rec):>6} focos salvos")
            return "ok"
        except Exception as e:
            if tentativa < TENTATIVAS:
                espera = 5 * tentativa
                print(f"... {ano}-{mes:02d} falhou (tentativa {tentativa}), "
                      f"esperando {espera}s e tentando de novo")
                time.sleep(espera)
            else:
                print(f"FALHOU {ano}-{mes:02d}: {type(e).__name__}")
                return "falha"

# ---- Modo paciente: repete ate baixar tudo ------------------------
# O servidor do INPE as vezes esta fora do ar. Como cada mes salvo e
# pulado, fazemos "rodadas": a cada rodada tentamos so o que falta,
# esperamos um pouco e tentamos de novo, ate completar os 60 meses
# (ou atingir o limite de rodadas). Aperte Ctrl+C para parar quando quiser.
sessao = requests.Session()
ESPERA_ENTRE_RODADAS = 90     # segundos de pausa quando ainda falta algo
MAX_RODADAS = 30              # ~45 min; depois para e voce roda de novo

faltando = []
for rodada in range(1, MAX_RODADAS + 1):
    print(f"\n--- Rodada {rodada} ---")
    contagem = {"ok": 0, "pulado": 0, "falha": 0}
    faltando = []
    for ano in ANOS:
        for mes in MESES:
            res = baixar_mes(ano, mes, sessao)
            contagem[res] += 1
            if res == "falha":
                faltando.append(f"{ano}-{mes:02d}")

    print(f"Baixados agora: {contagem['ok']} | "
          f"Ja existiam: {contagem['pulado']} | "
          f"Falharam: {contagem['falha']}")

    if not faltando:
        print("Todos os 60 meses foram baixados!")
        break

    if rodada < MAX_RODADAS:
        print(f"Ainda faltam {len(faltando)} meses. O INPE deve estar fora "
              f"do ar. Nova tentativa em {ESPERA_ENTRE_RODADAS}s "
              f"(Ctrl+C para parar).")
        time.sleep(ESPERA_ENTRE_RODADAS)

# ---- Juntar todos os meses baixados -------------------------------
arquivos = [os.path.join(PASTA_MES, f) for f in os.listdir(PASTA_MES)
            if f.endswith(".csv")]
if arquivos:
    completo = pd.concat((pd.read_csv(a) for a in arquivos),
                         ignore_index=True)
    completo.to_csv(SAIDA, index=False, encoding="utf-8")
    print()
    print("=" * 55)
    print(f"Arquivo juntado: {SAIDA}")
    print(f"Meses incluidos: {len(arquivos)} de 60")
    print(f"Total de focos:  {len(completo)}")
    print()
    resumo = (completo.groupby(["estado_id", "estado"])
                      .size().reset_index(name="focos"))
    print(resumo.to_string(index=False))

if faltando:
    print()
    print("Ainda faltam estes meses (rode o script de novo mais tarde):")
    print(", ".join(faltando))
