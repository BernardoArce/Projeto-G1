# 🔥 Queimadas no Brasil (2015–2024) — Análise e Dashboard

Projeto da **Avaliação G1** — Linguagem de Programação: Análise e Visualização de Dados com Python.

* 🔗 Repositório: *colar link do GitHub*
* 🌐 Página do projeto: *colar link do GitHub Pages*
* 📊 Dashboard: *colar link do Streamlit Community Cloud*

## Problema

Quais regiões, biomas e épocas do ano concentram mais focos de queimada, e como temperatura, chuva, seca e qualidade do ar se relacionam com eles?

## Base de dados

`dados/queimadas.csv`: base simulada com 2.400 registros (20 UFs × 120 meses, 2015–2024) e 13 colunas (focos, temperatura, chuva, área atingida, índice de seca, qualidade do ar, nível de risco etc.).

## Tecnologias

Python · Pandas · NumPy · Matplotlib · Seaborn · Streamlit · Plotly · SQLAlchemy + SQLite · GitHub

## Funcionalidades

**Intermediárias:** filtros múltiplos · KPIs dinâmicos · análise temporal · upload de arquivos · dashboard em seções · visualizações comparativas · análise geográfica
**Avançadas:** persistência em banco (SQLAlchemy + SQLite) · correlação estatística (Pandas/NumPy) · mapa interativo (Plotly) · séries temporais (média móvel)

## Estrutura

```
projeto-g1/
├── app.py              # dashboard Streamlit
├── requirements.txt
├── README.md
├── index.html          # página do projeto (GitHub Pages)
├── dados/              # queimadas.csv
├── database/           # queimadas.db (criado automaticamente pelo app)
├── notebooks/          # analise\_queimadas.ipynb
└── imagens/            # gráficos usados no notebook e na página
```

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Notebook: abra `notebooks/analise\_queimadas.ipynb` no Jupyter/VS Code/Colab e execute todas as células.

## Principais resultados

* Os focos cresceram cerca de 30% entre 2015 e 2024.
* De julho a outubro (período seco) a média de focos é cerca do dobro dos demais meses.
* O índice de seca é a variável mais associada aos focos (r ≈ 0,81); a chuva tem correlação negativa (r ≈ −0,39).

## Limitações

Base simulada: o bioma não corresponde ao bioma real da UF, e `nivel\_risco` e `qualidade\_ar` são derivados do número de focos.

## Autor

*Bernardo Teixeira de Oliveira Arce* — Linguagem de programação

