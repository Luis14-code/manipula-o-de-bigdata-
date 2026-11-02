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
├── scripts/                       # o código (isto sobe pro GitHub)
│   ├── 00_testar_ambiente.py      # confere as 7 bibliotecas
│   ├── 01_baixar_queimadas_mensal.py
│   ├── 02_criar_banco.py          # cria o banco SQLite + carrega focos 2024
│   ├── 03_explorar_focos.py       # consultas SQL de exploração
│   ├── 04_carregar_saude.py       # limpa e carrega a saúde (DataSUS)
│   └── 05_carregar_queimadas_mensal.py  # focos mensais 2020-2024
└── dados/
    └── brutos/                    # dados pequenos de referência (sobem)
```

> ⚠️ Os dados grandes (banco `.db` de ~479 MB e os focos brutos de 2024) **não ficam
> no repositório** — são regenerados ao rodar os scripts. Veja o `.gitignore`.

## 🛠️ Tecnologias

- **Python** + **pandas** (manipulação), **sqlite3** (banco), **requests** (download)
- **SQLite** — banco relacional em arquivo único (`dados/queimadas_saude.db`)
- **matplotlib**, **seaborn**, **plotly** — gráficos e mapas
- **scikit-learn** — análise estatística

## ▶️ Como rodar

```bash
python -I scripts/00_testar_ambiente.py          # confere o ambiente
python -I scripts/02_criar_banco.py              # cria o banco + focos 2024
python -I scripts/04_carregar_saude.py           # carrega a saúde
python -I scripts/05_carregar_queimadas_mensal.py  # carrega queimadas mensais
```
