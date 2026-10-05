"""Dashboard Streamlit - Queimadas no Brasil (2015-2024)."""
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

"""Projeto da Avaliação G1 — Linguagem de Programação
Professor: Alexandre Neves Louzada
Aluno: Bernardo Teixeira de Oliveira Arce

Repositório: https://github.com/BernardoArce/Projeto-G1
Página do projeto: https://bernardoarce.github.io/Projeto-G1/
"""

warnings.filterwarnings("ignore", category=FutureWarning)
BASE = Path(__file__).parent
CSV_PATH = BASE / "dados" / "queimadas.csv"
DB_PATH = BASE / "database" / "queimadas.db"
ORDEM_RISCO = ["Baixo", "Médio", "Alto", "Crítico"]
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Centroides aproximados das UFs (lat, lon) para o mapa
COORDS = {
    "AM": (-3.4, -65.0), "PA": (-3.8, -52.0), "RO": (-10.9, -62.8), "TO": (-10.2, -48.3),
    "DF": (-15.8, -47.9), "GO": (-15.9, -49.8), "MT": (-12.9, -55.9), "MS": (-20.5, -54.8),
    "BA": (-12.9, -41.7), "PE": (-8.4, -37.9), "CE": (-5.2, -39.3), "MA": (-5.0, -45.3),
    "PB": (-7.2, -36.8), "SP": (-22.3, -48.7), "RJ": (-22.2, -42.7), "MG": (-18.5, -44.6),
    "ES": (-19.6, -40.7), "PR": (-24.6, -51.6), "SC": (-27.2, -50.5), "RS": (-29.7, -53.3),
}

Base = declarative_base()


class Registro(Base):
    """Modelo relacional: um registro por UF/mês."""
    __tablename__ = "registros"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, index=True)
    mes = Column(Integer)
    regiao = Column(String)
    uf = Column(String, index=True)
    bioma = Column(String)
    focos_queimada = Column(Integer)
    temperatura_media = Column(Float)
    chuva_mm = Column(Float)
    area_atingida_km2 = Column(Float)
    indice_seca = Column(Float)
    qualidade_ar = Column(Float)
    nivel_risco = Column(String)


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza e engenharia de atributos."""
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"])
    df = df.drop_duplicates().dropna()
    df["nivel_risco"] = pd.Categorical(df["nivel_risco"], categories=ORDEM_RISCO, ordered=True)
    df["periodo_seco"] = np.where(df["mes"].between(7, 10), "Seco (Jul-Out)", "Demais meses")
    df["mes_nome"] = df["mes"].map(lambda m: MESES[m - 1])
    return df


@st.cache_resource
def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}")


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    """Persiste o CSV no SQLite (SQLAlchemy) na primeira execução e lê do banco."""
    engine = get_engine()
    DB_PATH.parent.mkdir(exist_ok=True)
    Base.metadata.create_all(engine)
    if not pd.read_sql("SELECT COUNT(*) AS n FROM registros", engine)["n"][0]:
        bruto = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        bruto = bruto.drop(columns=["data"])
        bruto.to_sql("registros", engine, if_exists="append", index=False)
    df = pd.read_sql("SELECT * FROM registros", engine).drop(columns="id")
    df["data"] = pd.to_datetime(dict(year=df["ano"], month=df["mes"], day=1))
    return preparar(df)


st.set_page_config(page_title="Queimadas no Brasil", page_icon="🔥", layout="wide")

# ---------------------------------------------------------------- Título
st.title("🔥 Queimadas no Brasil (2015–2024)")
st.markdown(
    """
**Problema:** quais regiões, biomas e épocas do ano concentram mais focos de queimada, e como
clima (temperatura, chuva, seca) e qualidade do ar se relacionam com eles?
O dashboard permite explorar a base simulada de 20 UFs, de 2015 a 2024, com filtros dinâmicos.
"""
)

df = carregar_dados()

# ---------------------------------------------------------------- Upload opcional
with st.sidebar:
    st.header("Filtros")
    arq = st.file_uploader("Enviar outro CSV (mesmas colunas)", type="csv")
    if arq is not None:
        try:
            df = preparar(pd.read_csv(arq, encoding="utf-8-sig"))
            st.success("Arquivo carregado.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Não foi possível ler o arquivo: {e}")

    anos = st.slider("Período (ano)", int(df.ano.min()), int(df.ano.max()),
                     (int(df.ano.min()), int(df.ano.max())))
    regioes = st.multiselect("Região", sorted(df.regiao.unique()), default=sorted(df.regiao.unique()))
    ufs_disp = sorted(df[df.regiao.isin(regioes)].uf.unique())
    ufs = st.multiselect("UF", ufs_disp, default=ufs_disp)
    biomas = st.multiselect("Bioma", sorted(df.bioma.unique()), default=sorted(df.bioma.unique()))
    riscos = st.multiselect("Nível de risco", ORDEM_RISCO, default=ORDEM_RISCO)

f = df[
    df.ano.between(*anos) & df.regiao.isin(regioes) & df.uf.isin(ufs)
    & df.bioma.isin(biomas) & df.nivel_risco.isin(riscos)
]
if f.empty:
    st.warning("Nenhum registro para os filtros escolhidos.")
    st.stop()

# ---------------------------------------------------------------- KPIs
st.header("1. Indicadores (KPIs)")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total de focos", f"{f.focos_queimada.sum():,}".replace(",", "."))
c2.metric("Área atingida (km²)", f"{f.area_atingida_km2.sum():,.0f}".replace(",", "."))
c3.metric("Média de focos / UF-mês", f"{f.focos_queimada.mean():.1f}")
c4.metric("Qualidade do ar (média)", f"{f.qualidade_ar.mean():.1f}")
pct_critico = (f.nivel_risco.isin(["Alto", "Crítico"])).mean() * 100
c5.metric("% registros Alto/Crítico", f"{pct_critico:.1f}%")

# ---------------------------------------------------------------- Temporal
st.header("2. Análise temporal")
col_a, col_b = st.columns(2)
anual = f.groupby("ano", as_index=False).focos_queimada.sum()
fig = px.line(anual, x="ano", y="focos_queimada", markers=True,
              title="Focos de queimada por ano", labels={"focos_queimada": "Focos", "ano": "Ano"})
col_a.plotly_chart(fig)

sazonal = f.groupby("mes", as_index=False).focos_queimada.mean()
fig, ax = plt.subplots(figsize=(6, 3.6))
sns.barplot(data=sazonal, x="mes", y="focos_queimada", color="#d9531e", ax=ax)
ax.set_xticks(range(12)); ax.set_xticklabels(MESES)
ax.set_title("Sazonalidade: média de focos por mês"); ax.set_xlabel(""); ax.set_ylabel("Focos (média)")
col_b.pyplot(fig)

mensal = f.groupby("data", as_index=False).focos_queimada.sum().sort_values("data")
mensal["media_movel_12m"] = mensal.focos_queimada.rolling(12).mean()
fig = px.line(mensal, x="data", y=["focos_queimada", "media_movel_12m"],
              title="Série mensal com média móvel de 12 meses",
              labels={"value": "Focos", "data": "Data", "variable": "Série"})
st.plotly_chart(fig)
st.info("**Interpretação:** os focos crescem ao longo da década e se concentram de julho a outubro, "
        "o período seco. A média móvel de 12 meses deixa a tendência de alta mais clara.")

# ---------------------------------------------------------------- Comparativos
st.header("3. Visualizações comparativas")
col_a, col_b = st.columns(2)
reg = f.groupby("regiao", as_index=False).focos_queimada.sum().sort_values("focos_queimada", ascending=False)
fig, ax = plt.subplots(figsize=(6, 3.6))
sns.barplot(data=reg, x="regiao", y="focos_queimada", palette="YlOrRd_r", ax=ax)
ax.set_title("Focos por região"); ax.set_xlabel(""); ax.set_ylabel("Focos")
col_a.pyplot(fig)

bio = f.groupby("bioma", as_index=False).agg(focos=("focos_queimada", "sum"),
                                              area=("area_atingida_km2", "sum"))
fig = px.bar(bio.sort_values("focos"), x="focos", y="bioma", orientation="h",
             color="area", color_continuous_scale="YlOrRd", title="Focos por bioma (cor = área atingida)")
col_b.plotly_chart(fig)

col_a, col_b = st.columns(2)
fig, ax = plt.subplots(figsize=(6, 3.6))
sns.boxplot(data=f, x="nivel_risco", y="indice_seca", order=ORDEM_RISCO, palette="YlOrRd", ax=ax)
ax.set_title("Índice de seca por nível de risco"); ax.set_xlabel("")
col_a.pyplot(fig)

fig = px.box(f, x="periodo_seco", y="focos_queimada", color="periodo_seco",
             title="Focos: período seco vs. demais meses")
col_b.plotly_chart(fig)

# ---------------------------------------------------------------- Geográfica
st.header("4. Análise geográfica")
geo = f.groupby("uf", as_index=False).agg(focos=("focos_queimada", "sum"),
                                           area=("area_atingida_km2", "sum"))
geo["lat"] = geo.uf.map(lambda u: COORDS[u][0])
geo["lon"] = geo.uf.map(lambda u: COORDS[u][1])
fig = px.scatter_geo(geo, lat="lat", lon="lon", size="focos", color="area", hover_name="uf",
                     color_continuous_scale="YlOrRd", scope="south america",
                     title="Focos por UF (tamanho) e área atingida (cor)")
fig.update_geos(lonaxis_range=[-75, -33], lataxis_range=[-35, 6], showcountries=True)
st.plotly_chart(fig)

# ---------------------------------------------------------------- Correlação
st.header("5. Correlação estatística")
num = ["focos_queimada", "temperatura_media", "chuva_mm", "area_atingida_km2",
       "indice_seca", "qualidade_ar"]
corr = f[num].corr()
col_a, col_b = st.columns([3, 2])
fig, ax = plt.subplots(figsize=(6.5, 4.8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax)
ax.set_title("Matriz de correlação (Pearson)")
col_a.pyplot(fig)
with col_b:
    st.markdown("**Correlação com o número de focos**")
    st.dataframe(corr["focos_queimada"].drop("focos_queimada").sort_values(key=abs, ascending=False)
                 .rename("r").round(3).to_frame())
    x = st.selectbox("Variável X", [c for c in num if c != "focos_queimada"], index=3)
    st.caption(f"Coeficiente de determinação (R²) entre {x} e focos: "
               f"{np.corrcoef(f[x], f.focos_queimada)[0, 1] ** 2:.2f}")
fig = px.scatter(f, x=x, y="focos_queimada", color="nivel_risco", opacity=0.6,
                 category_orders={"nivel_risco": ORDEM_RISCO},
                 title=f"Focos × {x}")
st.plotly_chart(fig)
st.info("**Interpretação:** o índice de seca tem a correlação positiva mais forte com os focos, e a chuva "
        "tem correlação negativa. A qualidade do ar piora (cai) quando há mais focos; a correlação é "
        "praticamente perfeita, o que sugere que, nesta base simulada, essa variável foi gerada a partir dos focos.")

# ---------------------------------------------------------------- Tabelas
st.header("6. Tabelas")
tab1, tab2, tab3 = st.tabs(["Resumo por UF", "Ranking de meses críticos", "Dados filtrados"])
with tab1:
    st.dataframe(f.groupby(["regiao", "uf"]).agg(
        focos=("focos_queimada", "sum"), area_km2=("area_atingida_km2", "sum"),
        seca_media=("indice_seca", "mean"), ar_medio=("qualidade_ar", "mean")
    ).round(2).sort_values("focos", ascending=False))
with tab2:
    top = f.sort_values("focos_queimada", ascending=False).head(15)
    st.dataframe(top[["data", "uf", "bioma", "focos_queimada", "area_atingida_km2", "nivel_risco"]])
with tab3:
    st.dataframe(f)
    st.download_button("Baixar CSV filtrado", f.to_csv(index=False).encode("utf-8"),
                       "queimadas_filtrado.csv", "text/csv")

# ---------------------------------------------------------------- Conclusão
st.header("7. Conclusão executiva")
mes_pico = int(f.groupby("mes").focos_queimada.mean().idxmax())
uf_top = geo.sort_values("focos", ascending=False).iloc[0]
st.success(
    f"""
- No recorte atual há **{f.focos_queimada.sum():,}** focos, com maior concentração em **{uf_top.uf}**
  e pico sazonal em **{MESES[mes_pico - 1]}**.
- Os meses de julho a outubro têm cerca do dobro de focos dos demais meses: ações de prevenção e
  brigadas devem ser reforçadas nesse período.
- Seca e baixa chuva são os principais fatores associados ao aumento de focos, enquanto a temperatura
  tem associação mais fraca.
- Recomenda-se monitorar o índice de seca como indicador antecipado de risco.
""".replace(",", ".")
)
st.caption("Base: dados simulados de queimadas no Brasil, fornecida pelo professor para fins didáticos.")
