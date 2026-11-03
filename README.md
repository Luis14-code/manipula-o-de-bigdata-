# Manipulação de Big Data — Queimadas × Saúde Respiratória

Projeto de Extensão — **Centro Universitário FACIMP WYDEN** (Imperatriz/MA).

Análise da relação entre **focos de queimada** (incêndios florestais) e **internações
por doenças respiratórias** no Norte/Nordeste do Brasil, nos estados do **Pará (PA)**,
**Amazonas (AM)** e **Maranhão (MA)**, no período de **2020 a 2024**.

## 🎯 Objetivo

Verificar se os meses com mais queimadas apresentam mais internações respiratórias,
gerando subsídio para ações comunitárias (alertas de qualidade do ar) e para órgãos
de resposta (Defesa Civil, Corpo de Bombeiros).

## 📥 Fontes de dados

| Fonte | O que é | Órgão |
|-------|---------|-------|
| **INPE – Programa Queimadas** | Focos de calor detectados por satélite | Instituto Nacional de Pesquisas Espaciais |
| **DataSUS – SIH/SUS** | Internações por doenças respiratórias (CID-10, Cap. X) | Ministério da Saúde |

## 🗂️ Estrutura

```
big data/
├── scripts/                              # o código (isto sobe pro GitHub)
│   ├── 00_testar_ambiente.py             # confere as bibliotecas
│   ├── 01_baixar_queimadas_mensal.py
│   ├── 02_criar_banco.py                 # cria o banco SQLite + carrega focos 2024
│   ├── 03_explorar_focos.py              # consultas SQL de exploração
│   ├── 04_carregar_saude.py              # limpa e carrega a saúde (DataSUS)
│   ├── 05_carregar_queimadas_mensal.py   # focos mensais 2020-2024
│   ├── 06_cruzar_queimada_saude.py       # JOIN SQL + correlação de Spearman
│   ├── 07_graficos.py                    # perfil sazonal, séries, dispersão, heatmap
│   └── 08_painel.py                      # painel de focos das últimas 24 h (Streamlit)
├── graficos/                             # figuras geradas pelo 07
└── dados/
    └── brutos/                           # dados pequenos de referência (sobem)
```

> ⚠️ Os dados grandes (banco `.db` de ~479 MB e os focos brutos de 2024) **não ficam
> no repositório** — são regenerados ao rodar os scripts. Veja o `.gitignore`.

## 🛠️ Tecnologias

- **Python** + **pandas** (manipulação), **sqlite3** (banco), **requests** (download)
- **SQLite** — banco relacional em arquivo único (`dados/queimadas_saude.db`)
- **scipy** — correlação de Spearman
- **matplotlib**, **seaborn**, **plotly** — gráficos e mapas
- **Streamlit** — painel interativo
- **scikit-learn** — análise estatística

## ▶️ Como rodar

```bash
python -m pip install pandas scipy matplotlib seaborn plotly scikit-learn requests streamlit

python scripts/00_testar_ambiente.py             # confere o ambiente
python scripts/04_carregar_saude.py              # cria o banco + carrega a saúde
python scripts/05_carregar_queimadas_mensal.py   # carrega queimadas mensais
python scripts/06_cruzar_queimada_saude.py       # cruza queimadas × internações
python scripts/07_graficos.py                    # gera as figuras em graficos/
python -m streamlit run scripts/08_painel.py     # abre o painel no navegador
```
