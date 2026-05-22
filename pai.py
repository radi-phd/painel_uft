# ============================================================
# PAINEL ANALÍTICO INSTITUCIONAL — UFT
# VERSÃO EXECUTIVA · COMPLETA · ESTÁVEL
# ============================================================

import os
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Painel RH · UFT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PALETA INSTITUCIONAL
# ============================================================

P = "#0D2B4E"
S = "#1A4A7A"
A = "#1E6FBF"
D = "#C8A84B"
FG = "#F4F6F9"
BD = "#DDE3EC"
TL = "#6B7A99"
AL = "#D95F2B"
OK = "#1B7A4A"

ESC_AZUL = [
    [0, "#EBF3FB"],
    [0.2, "#9DC3E6"],
    [0.5, "#2F6FAC"],
    [0.8, "#0D4C8B"],
    [1, "#0A2E5C"]
]

ESC_OURO = [
    [0, "#FDF6E3"],
    [0.3, "#F0D080"],
    [0.7, "#C8A84B"],
    [1, "#6B4F0A"]
]

BASE_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(
        family="Arial",
        color=P
    ),
    margin=dict(
        t=30,
        b=20,
        l=10,
        r=10
    ),
)

# ============================================================
# CSS GLOBAL
# ============================================================

st.markdown(f"""
<style>

.main {{
    background-color: {FG};
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {P} 0%, {S} 100%);
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

.card {{
    background: white;
    border: 1px solid {BD};
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}}

.kpi {{
    background: white;
    border: 1px solid {BD};
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}}

.kpi h1 {{
    color: {P};
    font-size: 2rem;
    margin: 0;
}}

.kpi p {{
    color: {TL};
    font-size: 0.8rem;
}}

.sec {{
    font-size: 1.1rem;
    font-weight: bold;
    color: {P};
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid {D};
    padding-bottom: 0.4rem;
}}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================

def sec(titulo):
    st.markdown(
        f'<div class="sec">{titulo}</div>',
        unsafe_allow_html=True
    )

def card_open():
    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

def card_close():
    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

# ============================================================
# LEITURA DO EXCEL
# ============================================================

ARQUIVO = "perfil.xlsx"

if not os.path.exists(ARQUIVO):

    st.error(
        f"Arquivo '{ARQUIVO}' não encontrado."
    )

    st.stop()

# ============================================================
# CARREGAMENTO
# ============================================================

@st.cache_data(show_spinner=True)

def carregar_dados():

    try:

        excel = pd.ExcelFile(
            ARQUIVO,
            engine="openpyxl"
        )

        abas = {
            a.strip().lower(): a
            for a in excel.sheet_names
        }

        if "técnico" not in abas:

            st.error(
                f"Aba 'técnico' não encontrada.\n\n"
                f"Abas disponíveis: {excel.sheet_names}"
            )

            st.stop()

        if "docente" not in abas:

            st.error(
                f"Aba 'docente' não encontrada.\n\n"
                f"Abas disponíveis: {excel.sheet_names}"
            )

            st.stop()

        tecnico = pd.read_excel(
            excel,
            sheet_name=abas["técnico"]
        )

        docente = pd.read_excel(
            excel,
            sheet_name=abas["docente"]
        )

        tecnico["CATEGORIA"] = "TÉCNICO"
        docente["CATEGORIA"] = "DOCENTE"

        df = pd.concat(
            [tecnico, docente],
            ignore_index=True
        )

        # ====================================================
        # PADRONIZAÇÃO
        # ====================================================

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        # ====================================================
        # REMOVE LGPD
        # ====================================================

        SENSIVEIS = [
            "CPF",
            "NOME",
            "RG",
            "DOCUMENTO"
        ]

        for c in SENSIVEIS:

            if c in df.columns:

                df.drop(
                    columns=c,
                    inplace=True
                )

        # ====================================================
        # LIMPEZA GERAL
        # ====================================================

        for c in df.columns:

            try:

                if df[c].dtype == "object":

                    df[c] = (
                        df[c]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )

            except:
                pass

        # ====================================================
        # IDADE
        # ====================================================

        if "DT_NASC" in df.columns:

            df["DT_NASC"] = pd.to_datetime(
                df["DT_NASC"],
                errors="coerce",
                dayfirst=True
            )

            hoje = pd.Timestamp.today()

            df["IDADE"] = (
                (hoje - df["DT_NASC"]).dt.days / 365.25
            ).round(1)

        # ====================================================
        # TITULAÇÃO
        # ====================================================

        if "TITULAÇÃO" in df.columns:

            tit = (
                df["TITULAÇÃO"]
                .astype(str)
                .str.upper()
            )

            df["TIT_CLASS"] = "OUTROS"

            df.loc[
                tit.str.contains("DOUT", na=False),
                "TIT_CLASS"
            ] = "DOUTORADO"

            df.loc[
                tit.str.contains("MEST", na=False),
                "TIT_CLASS"
            ] = "MESTRADO"

            df.loc[
                tit.str.contains("ESPECIAL", na=False),
                "TIT_CLASS"
            ] = "ESPECIALIZAÇÃO"

            df.loc[
                tit.str.contains("GRAD", na=False),
                "TIT_CLASS"
            ] = "GRADUAÇÃO"

            df.loc[
                tit.str.contains("2 GRAU|TECNICO", na=False),
                "TIT_CLASS"
            ] = "ENSINO MÉDIO/TÉCNICO"

        # ====================================================
        # DESVIO
        # ====================================================

        if (
            "LOTAÇÃO_OFICIAL" in df.columns
            and
            "LOTAÇÃO_EXERCÍCIO" in df.columns
        ):

            df["DESVIO"] = np.where(
                df["LOTAÇÃO_OFICIAL"]
                !=
                df["LOTAÇÃO_EXERCÍCIO"],
                "SIM",
                "NÃO"
            )

        return df

    except Exception as e:

        st.error(
            f"Erro ao carregar Excel:\n\n{e}"
        )

        st.stop()

# ============================================================
# CARREGA DADOS
# ============================================================

df = carregar_dados()

# ============================================================
# SIDEBAR DINÂMICA
# ============================================================

st.sidebar.title("🎓 Painel RH · UFT")

st.sidebar.markdown("---")

COLUNAS_IGNORADAS = [
    "DT_NASC"
]

filtros = {}

for coluna in df.columns:

    if coluna in COLUNAS_IGNORADAS:
        continue

    if df[coluna].isna().all():
        continue

    try:

        qtd_unicos = df[coluna].nunique()

        # evita filtros enormes
        if qtd_unicos > 200:
            continue

        valores = sorted(
            [
                str(v)
                for v in df[coluna]
                .dropna()
                .unique()
            ]
        )

        filtros[coluna] = st.sidebar.multiselect(
            coluna,
            valores,
            default=valores
        )

    except:
        pass

# ============================================================
# APLICA FILTROS
# ============================================================

df_f = df.copy()

for coluna, valores in filtros.items():

    if len(valores) > 0:

        df_f = df_f[
            df_f[coluna]
            .astype(str)
            .isin(valores)
        ]

# ============================================================
# CONTADOR
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    f"{len(df_f)} registros filtrados"
)

# ============================================================
# KPIs
# ============================================================

total = len(df_f)

docentes = len(
    df_f[df_f["CATEGORIA"] == "DOCENTE"]
)

tecnicos = len(
    df_f[df_f["CATEGORIA"] == "TÉCNICO"]
)

doutores = 0
mestres = 0

if "TIT_CLASS" in df_f.columns:

    doutores = len(
        df_f[df_f["TIT_CLASS"] == "DOUTORADO"]
    )

    mestres = len(
        df_f[df_f["TIT_CLASS"] == "MESTRADO"]
    )

# ============================================================
# SCORE
# ============================================================

pesos = {
    "DOUTORADO": 4,
    "MESTRADO": 3,
    "ESPECIALIZAÇÃO": 2,
    "GRADUAÇÃO": 1,
    "ENSINO MÉDIO/TÉCNICO": 0
}

score = 0

for nivel, peso in pesos.items():

    score += (
        len(
            df_f[
                df_f["TIT_CLASS"] == nivel
            ]
        ) * peso
    )

indice = round(
    score / max(total, 1),
    2
)

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div style="
background: linear-gradient(130deg, {P} 0%, {S} 60%, {A} 100%);
padding: 2rem;
border-radius: 18px;
margin-bottom: 1.5rem;
color: white;
">
<h1>🎓 Painel Analítico Institucional</h1>
<p>Universidade Federal do Tocantins</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# KPIs
# ============================================================

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:

    st.markdown(f"""
    <div class='kpi'>
    <h1>{total}</h1>
    <p>TOTAL</p>
    </div>
    """, unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div class='kpi'>
    <h1>{docentes}</h1>
    <p>DOCENTES</p>
    </div>
    """, unsafe_allow_html=True)

with c3:

    st.markdown(f"""
    <div class='kpi'>
    <h1>{tecnicos}</h1>
    <p>TÉCNICOS</p>
    </div>
    """, unsafe_allow_html=True)

with c4:

    st.markdown(f"""
    <div class='kpi'>
    <h1>{doutores}</h1>
    <p>DOUTORES</p>
    </div>
    """, unsafe_allow_html=True)

with c5:

    st.markdown(f"""
    <div class='kpi'>
    <h1>{mestres}</h1>
    <p>MESTRES</p>
    </div>
    """, unsafe_allow_html=True)

with c6:

    st.markdown(f"""
    <div class='kpi'>
    <h1>{indice}/4</h1>
    <p>QUALIFICAÇÃO</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# SCORE GAUGE
# ============================================================

sec("📊 Índice Médio de Qualificação")

fig_g = go.Figure(go.Indicator(
    mode="gauge+number",
    value=indice,
    number={
        "suffix": " / 4.0"
    },
    gauge={
        "axis": {
            "range": [0, 4]
        },
        "bar": {
            "color": P
        },
        "steps": [
            {"range": [0,1], "color": "#EEF2F8"},
            {"range": [1,2], "color": "#C8D8EE"},
            {"range": [2,3], "color": "#93B5D8"},
            {"range": [3,4], "color": "#4A90D9"},
        ],
    }
))

fig_g.update_layout(
    height=280,
    **BASE_LAYOUT
)

card_open()

st.plotly_chart(
    fig_g,
    width='stretch'
)

card_close()

# ============================================================
# TITULAÇÃO
# ============================================================

if "TIT_CLASS" in df_f.columns:

    sec("🎓 Titulação")

    tit_df = (
        df_f["TIT_CLASS"]
        .value_counts()
        .reset_index()
    )

    tit_df.columns = [
        "Titulação",
        "Qtd"
    ]

    fig_tit = px.bar(
        tit_df,
        x="Qtd",
        y="Titulação",
        orientation="h",
        text="Qtd",
        color="Qtd",
        color_continuous_scale=ESC_AZUL,
        height=400
    )

    fig_tit.update_layout(
        **BASE_LAYOUT,
        coloraxis_showscale=False
    )

    card_open()

    st.plotly_chart(
        fig_tit,
        width='stretch'
    )

    card_close()

# ============================================================
# SEXO
# ============================================================

if "SEXO" in df_f.columns:

    sec("👥 Distribuição por Sexo")

    sexo_df = (
        df_f["SEXO"]
        .value_counts()
        .reset_index()
    )

    sexo_df.columns = [
        "Sexo",
        "Qtd"
    ]

    fig_sexo = px.pie(
        sexo_df,
        names="Sexo",
        values="Qtd",
        hole=0.6,
        height=400,
        color_discrete_sequence=[P, D]
    )

    fig_sexo.update_layout(
        **BASE_LAYOUT
    )

    card_open()

    st.plotly_chart(
        fig_sexo,
        width='stretch'
    )

    card_close()

# ============================================================
# CARGOS
# ============================================================

if "CARGO" in df_f.columns:

    sec("💼 Distribuição por Cargo")

    cargo_df = (
        df_f["CARGO"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    cargo_df.columns = [
        "Cargo",
        "Qtd"
    ]

    fig_cargo = px.bar(
        cargo_df,
        x="Qtd",
        y="Cargo",
        orientation="h",
        text="Qtd",
        color="Qtd",
        color_continuous_scale=ESC_OURO,
        height=700
    )

    fig_cargo.update_layout(
        **BASE_LAYOUT,
        coloraxis_showscale=False
    )

    card_open()

    st.plotly_chart(
        fig_cargo,
        width='stretch'
    )

    card_close()

# ============================================================
# LOTAÇÃO
# ============================================================

if "LOTAÇÃO_OFICIAL" in df_f.columns:

    sec("🏢 Distribuição por Lotação")

    lot_df = (
        df_f["LOTAÇÃO_OFICIAL"]
        .value_counts()
        .head(20)
        .reset_index()
    )

    lot_df.columns = [
        "Lotação",
        "Qtd"
    ]

    fig_lot = px.bar(
        lot_df,
        x="Qtd",
        y="Lotação",
        orientation="h",
        text="Qtd",
        color="Qtd",
        color_continuous_scale=ESC_AZUL,
        height=700
    )

    fig_lot.update_layout(
        **BASE_LAYOUT,
        coloraxis_showscale=False
    )

    card_open()

    st.plotly_chart(
        fig_lot,
        width='stretch'
    )

    card_close()

# ============================================================
# HEATMAP
# ============================================================

if (
    "LOTAÇÃO_OFICIAL" in df_f.columns
    and
    "CATEGORIA" in df_f.columns
):

    sec("🔥 Heatmap Institucional")

    heat = pd.crosstab(
        df_f["LOTAÇÃO_OFICIAL"],
        df_f["CATEGORIA"]
    )

    fig_heat = px.imshow(
        heat,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=ESC_AZUL,
        height=700
    )

    fig_heat.update_layout(
        **BASE_LAYOUT
    )

    card_open()

    st.plotly_chart(
        fig_heat,
        width='stretch'
    )

    card_close()

# ============================================================
# PERFIL ETÁRIO
# ============================================================

if "IDADE" in df_f.columns:

    sec("📈 Perfil Etário")

    c1, c2 = st.columns(2)

    with c1:

        fig_hist = px.histogram(
            df_f,
            x="IDADE",
            nbins=20,
            height=400,
            color_discrete_sequence=[A]
        )

        fig_hist.update_layout(
            **BASE_LAYOUT
        )

        card_open()

        st.plotly_chart(
            fig_hist,
            width='stretch'
        )

        card_close()

    with c2:

        fig_box = px.box(
            df_f,
            x="CATEGORIA",
            y="IDADE",
            color="CATEGORIA",
            height=400
        )

        fig_box.update_layout(
            **BASE_LAYOUT
        )

        card_open()

        st.plotly_chart(
            fig_box,
            width='stretch'
        )

        card_close()

# ============================================================
# DESVIO
# ============================================================

if "DESVIO" in df_f.columns:

    sec("⚠️ Desvio de Lotação")

    desvio_df = (
        df_f["DESVIO"]
        .value_counts()
        .reset_index()
    )

    desvio_df.columns = [
        "Status",
        "Qtd"
    ]

    fig_dev = px.pie(
        desvio_df,
        names="Status",
        values="Qtd",
        hole=0.6,
        height=400,
        color="Status",
        color_discrete_map={
            "SIM": AL,
            "NÃO": OK
        }
    )

    fig_dev.update_layout(
        **BASE_LAYOUT
    )

    card_open()

    st.plotly_chart(
        fig_dev,
        width='stretch'
    )

    card_close()

# ============================================================
# MATRIZ CARGO X TITULAÇÃO
# ============================================================

if (
    "CARGO" in df_f.columns
    and
    "TIT_CLASS" in df_f.columns
):

    sec("📚 Cargo x Titulação")

    cruz = pd.crosstab(
        df_f["CARGO"],
        df_f["TIT_CLASS"]
    )

    fig_cruz = px.imshow(
        cruz,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=ESC_OURO,
        height=700
    )

    fig_cruz.update_layout(
        **BASE_LAYOUT
    )

    card_open()

    st.plotly_chart(
        fig_cruz,
        width='stretch'
    )

    card_close()

# ============================================================
# BASE CONSOLIDADA
# ============================================================

sec("📄 Base Consolidada")

busca = st.text_input(
    "Buscar",
    placeholder="Digite qualquer informação..."
)

df_exib = df_f.copy()

if busca:

    mask = df_exib.apply(
        lambda col:
        col.astype(str)
        .str.contains(
            busca,
            case=False,
            na=False
        )
    ).any(axis=1)

    df_exib = df_exib[mask]

st.dataframe(
    df_exib,
    width='stretch',
    height=600
)

# ============================================================
# DOWNLOAD
# ============================================================

csv = df_exib.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Baixar CSV Filtrado",
    data=csv,
    file_name="base_filtrada_uft.csv",
    mime="text/csv",
    width='stretch'
)