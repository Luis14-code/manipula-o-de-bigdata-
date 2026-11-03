"""
Missão 9 — Painel de queimadas em tempo quase real (Produto 2: Defesa Civil / Bombeiros)

Mostra os focos de calor mais recentes do INPE (Programa Queimadas) em PA, AM e MA:
métricas, mapa, ranking de municípios e alerta por limite de focos.

Instalar (uma vez):   python -m pip install streamlit
Rodar:                python -m streamlit run scripts/08_painel.py
"""

import unicodedata
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------
# Passo A — configurações
# ---------------------------------------------------------------
ESTADOS = ["PARA", "AMAZONAS", "MARANHAO"]      # comparação sem acento e em maiúsculas

# ATENÇÃO: confira esta URL no portal de dados abertos do INPE (Programa Queimadas),
# seção de arquivos CSV das últimas 24/48 h. O caminho pode mudar. Se mudar,
# cole a URL certa na barra lateral do painel, sem precisar editar o código.
URL_MODELO = ("https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/"
              "diario/Brasil/focos_diario_br_{data}.csv")


def sem_acento(txt):
    """'MARANHÃO' -> 'MARANHAO' (evita falhar por causa de acento)."""
    txt = unicodedata.normalize("NFKD", str(txt))
    return "".join(c for c in txt if not unicodedata.combining(c)).upper().strip()


# ---------------------------------------------------------------
# Passo B — baixar os focos (cache de 10 minutos)
# ---------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Baixando focos do INPE...")
def carregar(url_modelo):
    agora = datetime.now(timezone.utc)
    partes, erros = [], []
    for dias_atras in (1, 0):                    # ontem + hoje (datas em UTC)
        dia = (agora - timedelta(days=dias_atras)).strftime("%Y%m%d")
        url = url_modelo.format(data=dia)
        try:
            partes.append(pd.read_csv(url))
        except Exception as e:                   # arquivo do dia ainda não publicado, etc.
            erros.append(f"{url}  ->  {type(e).__name__}")
    if not partes:
        return None, erros

    df = pd.concat(partes, ignore_index=True)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={"lat": "latitude", "lon": "longitude"})  # o INPE pode usar qualquer um

    df["estado_n"] = df["estado"].map(sem_acento)
    df = df[df["estado_n"].isin(ESTADOS)].copy()

    # últimas 24 h (o INPE grava a hora em GMT/UTC)
    if "data_hora_gmt" in df.columns:
        df["data_hora_gmt"] = pd.to_datetime(df["data_hora_gmt"], errors="coerce", utc=True)
        df = df[df["data_hora_gmt"] >= agora - timedelta(hours=24)]
        df["hora_local"] = df["data_hora_gmt"].dt.tz_convert("America/Fortaleza")
    return df, erros


# ---------------------------------------------------------------
# Passo C — interface
# ---------------------------------------------------------------
st.set_page_config(page_title="Painel de Queimadas", layout="wide")
st.title("🔥 Focos de queimada: últimas 24 h (PA, AM e MA)")
st.caption("Fonte: INPE, Programa Queimadas (focos detectados por satélite). "
           "Foco é um ponto de calor detectado, não um incêndio confirmado.")

with st.sidebar:
    st.header("Configurações")
    url_modelo = st.text_input("URL do CSV do INPE", URL_MODELO,
                               help="Use {data} onde entra a data AAAAMMDD.")
    limite = st.slider("Limite de alerta (focos em 24 h por município)", 5, 200, 30)
    escolha = st.multiselect("Estados", ["PARÁ", "AMAZONAS", "MARANHÃO"],
                             default=["PARÁ", "AMAZONAS", "MARANHÃO"])
    if st.button("Atualizar agora"):
        st.cache_data.clear()

df, erros = carregar(url_modelo)

if df is None:
    st.error("Não consegui baixar o arquivo do INPE. Confira a URL na barra lateral.")
    st.code("\n".join(erros))
    st.stop()

df = df[df["estado_n"].isin([sem_acento(e) for e in escolha])]

if df.empty:
    st.info("Nenhum foco nas últimas 24 h para os estados escolhidos.")
    st.stop()

# ---- métricas
c1, c2, c3 = st.columns(3)
c1.metric("Focos nas últimas 24 h", f"{len(df):,}".replace(",", "."))
c2.metric("Município com mais focos", df["municipio"].value_counts().idxmax())
c3.metric("Estado com mais focos", df["estado"].value_counts().idxmax())

# ---- alerta
ranking = (df.groupby(["estado", "municipio"]).size()
             .reset_index(name="focos")
             .sort_values("focos", ascending=False))
em_alerta = ranking[ranking["focos"] >= limite]
if len(em_alerta):
    st.warning(f"⚠️ {len(em_alerta)} município(s) com {limite} focos ou mais em 24 h")
    st.dataframe(em_alerta, use_container_width=True, hide_index=True)
else:
    st.success(f"Nenhum município passou de {limite} focos nas últimas 24 h.")

# ---- mapa
if hasattr(px, "scatter_map"):                   # plotly mais novo
    fig = px.scatter_map(df, lat="latitude", lon="longitude", color="estado",
                         hover_name="municipio", zoom=4.3,
                         map_style="open-street-map")
else:                                            # plotly mais antigo
    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="estado",
                            hover_name="municipio", zoom=4.3,
                            mapbox_style="open-street-map")
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=520)
st.plotly_chart(fig, use_container_width=True)

# ---- ranking
st.subheader("Top 10 municípios")
st.dataframe(ranking.head(10), use_container_width=True, hide_index=True)
