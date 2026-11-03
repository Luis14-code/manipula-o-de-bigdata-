"""
Missão 8 — Gráficos: queimadas × internações respiratórias (PA, AM, MA, 2020-2024)

Lê as tabelas queimadas_mensal e saude do banco dados/queimadas_saude.db
e salva as figuras na pasta graficos/ do projeto.

Rodar (da pasta do projeto):
    python scripts/07_graficos.py
"""

import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # salva arquivos, sem abrir janela
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
from scipy.stats import spearmanr

# ---------------------------------------------------------------
# Passo A — caminhos (relativos à pasta do projeto, funcionam em qualquer PC)
# ---------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
BANCO = RAIZ / "dados" / "queimadas_saude.db"
SAIDA = RAIZ / "graficos"
SAIDA.mkdir(exist_ok=True)

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

sns.set_theme(style="whitegrid")

# ---------------------------------------------------------------
# Passo B — ler e juntar (mesmo JOIN da Missão 7)
# ---------------------------------------------------------------
con = sqlite3.connect(BANCO)
base = pd.read_sql("""
    SELECT q.uf, q.ano, q.mes, q.focos, s.internacoes
    FROM queimadas_mensal q
    JOIN saude s ON q.uf = s.uf AND q.ano = s.ano AND q.mes = s.mes
    ORDER BY q.uf, q.ano, q.mes
""", con)
con.close()

base["data"] = pd.to_datetime(dict(year=base["ano"], month=base["mes"], day=1))
print("Linhas no JOIN:", len(base), "(esperado: 180)")

# ---------------------------------------------------------------
# Gráfico 1 — Perfil sazonal (o gráfico-chave do relatório)
# Mostra que o pico de focos (ago/set) não coincide com o de internações
# ---------------------------------------------------------------
sazonal = base.groupby("mes")[["focos", "internacoes"]].mean()

fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.bar(sazonal.index, sazonal["focos"], color="orangered", alpha=0.65,
        label="Focos de queimada (média mensal)")
ax1.set_ylabel("Focos de queimada", color="orangered")
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(MESES)

ax2 = ax1.twinx()
ax2.plot(sazonal.index, sazonal["internacoes"], color="navy", lw=2.5,
         marker="o", label="Internações respiratórias (média mensal)")
ax2.set_ylabel("Internações respiratórias", color="navy")
ax2.grid(False)

ax1.set_title("Perfil sazonal: queimadas × internações (média PA + AM + MA, 2020-2024)")
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left")
fig.tight_layout()
fig.savefig(SAIDA / "01_perfil_sazonal.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# Gráfico 2 — Série temporal por estado (focos em barras, internações em linha)
# ---------------------------------------------------------------
ufs = sorted(base["uf"].unique())
fig, eixos = plt.subplots(len(ufs), 1, figsize=(11, 3.6 * len(ufs)), sharex=True)
eixos = [eixos] if len(ufs) == 1 else eixos

for ax, uf in zip(eixos, ufs):
    g = base[base["uf"] == uf]
    ax.bar(g["data"], g["focos"], width=20, color="orangered", alpha=0.6)
    ax.set_ylabel("Focos")
    ax.set_title(uf, loc="left", fontweight="bold")
    ax_b = ax.twinx()
    ax_b.plot(g["data"], g["internacoes"], color="navy", lw=2)
    ax_b.set_ylabel("Internações")
    ax_b.grid(False)

fig.suptitle("Focos de queimada (barras) × internações respiratórias (linha)", y=1.0)
fig.tight_layout()
fig.savefig(SAIDA / "02_serie_temporal.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# Gráfico 3 — Dispersão SEM sazonalidade
# Cada ponto = quanto aquele mês fugiu da média do mesmo mês nos outros anos
# ---------------------------------------------------------------
for col in ["focos", "internacoes"]:
    media_mes = base.groupby(["uf", "mes"])[col].transform("mean")
    base[f"{col}_desvio"] = base[col] - media_mes

fig, eixos = plt.subplots(1, len(ufs), figsize=(5 * len(ufs), 4.5))
eixos = [eixos] if len(ufs) == 1 else eixos

for ax, uf in zip(eixos, ufs):
    g = base[base["uf"] == uf]
    sns.regplot(data=g, x="focos_desvio", y="internacoes_desvio", ax=ax,
                scatter_kws={"alpha": 0.6, "color": "orangered"},
                line_kws={"color": "navy"})
    rho, p = spearmanr(g["focos_desvio"], g["internacoes_desvio"])
    ax.set_title(f"{uf}  (rho = {rho:.2f}, p = {p:.3f})")
    ax.set_xlabel("Focos: desvio da média do mês")
    ax.set_ylabel("Internações: desvio da média do mês")

fig.suptitle("Associação sem sazonalidade (cada mês vs. média do mesmo mês)")
fig.tight_layout()
fig.savefig(SAIDA / "03_dispersao_sem_sazonalidade.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# Gráfico 4 — Heatmap mês × ano de focos, um painel por estado
# ---------------------------------------------------------------
fig, eixos = plt.subplots(1, len(ufs), figsize=(5 * len(ufs), 5))
eixos = [eixos] if len(ufs) == 1 else eixos

for ax, uf in zip(eixos, ufs):
    piv = base[base["uf"] == uf].pivot_table(index="mes", columns="ano",
                                              values="focos", aggfunc="sum")
    sns.heatmap(piv, cmap="YlOrRd", annot=True, fmt=".0f", ax=ax,
                cbar=False, yticklabels=MESES, annot_kws={"size": 7})
    ax.set_title(uf)
    ax.set_ylabel("")

fig.suptitle("Focos de queimada por mês e ano")
fig.tight_layout()
fig.savefig(SAIDA / "04_heatmap_focos.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# Gráfico 5 — Interativo (Plotly): abre no navegador
# ---------------------------------------------------------------
long = base.melt(id_vars=["uf", "data"], value_vars=["focos", "internacoes"],
                 var_name="indicador", value_name="valor")
fig = px.line(long, x="data", y="valor", color="uf", facet_row="indicador",
              title="Focos e internações por estado")
fig.update_yaxes(matches=None)
fig.write_html(SAIDA / "05_interativo.html")

print("Pronto! Figuras salvas em:", SAIDA)
for arq in sorted(SAIDA.iterdir()):
    print(" -", arq.name)
