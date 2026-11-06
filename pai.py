# ============================================================
# PAINEL ANALÍTICO INSTITUCIONAL — UFT
# Versão com identidade visual oficial da UFT
# ============================================================

import asyncio, sys, os
import base64
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="PROGRAD · UFT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# ▼▼▼ PALETA DE CORES — ALTERE AQUI PARA MUDAR AS CORES ▼▼▼
#
# Todas as cores do dashboard vêm deste único bloco.
# Para trocar qualquer cor, basta editar o valor hex aqui.
#
# Cores extraídas diretamente do brasão oficial da UFT:
# ============================================================

P   = "#002B49"   # NAVY UFT — identidade principal
S   = "#0A2540"   # NAVY ESCURO — sidebar e superfícies profundas
A   = "#0369A1"   # AZUL — destaques e gráficos
D   = "#F3A61E"   # DOURADO — acento institucional
VD  = "#008566"   # VERDE UFT — estados positivos
CZ  = "#64748B"   # SLATE — textos auxiliares
BN  = "#0F172A"   # SLATE ESCURO — texto de alto contraste

# Cores de apoio (interface)
FG  = "#F4F6F9"   # FUNDO — superfície clara do dashboard
BD  = "#E2E8F0"   # BORDA — linhas e separadores
TL  = "#64748B"   # TEXTO LEVE — subtítulos e labels
AL  = "#DC2626"   # ALERTA — vermelho para avisos
OK  = "#009E73"   # SUCESSO — verde de confirmação

# ▲▲▲ FIM DA SEÇÃO DE CORES ▲▲▲

# Escalas de cor para gráficos (gradientes)
ESC_AZUL = [[0,"#C5D9F0"],[0.3,"#5A9AD4"],[0.6,"#1A5FA8"],[0.85,"#003C78"],[1,"#002050"]]
ESC_OURO = [[0,"#FDF6E3"],[0.3,"#F8D87A"],[0.65,"#F0B41E"],[1,"#A07800"]]
ESC_TEAL = [[0,"#C8EDED"],[0.4,"#4AABAB"],[0.75,"#007878"],[1,"#004444"]]
CATS     = [P, D, VD, A, AL, CZ, "#8E44AD","#2980B9","#16A085","#D35400"]

BL = dict(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", color=P),
    margin=dict(t=28, b=16, l=8, r=8),
)

# ============================================================
# CAMINHO DA LOGO — sem base64, sem data: URI
# Coloque logo_uft.jpg (ou .png) na mesma pasta que servidores.py.
# st.image() e st.sidebar.image() carregam o arquivo diretamente.
# Funciona no terminal local e no Streamlit Cloud.
# ============================================================
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = next(
    (os.path.join(BASE_DIR, n)
     for n in ["logo_uft.jpg", "logo_uft.png", "images.jpg"]
     if os.path.exists(os.path.join(BASE_DIR, n))),
    None   # None se nenhum arquivo encontrado → exibe emoji
)

# ============================================================
# CSS GLOBAL — tokens visuais derivados do protótipo Stitch
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {
    --uft-navy: #002B49;
    --uft-navy-dark: #0A2540;
    --uft-navy-input: #001A30;
    --uft-green: #008566;
    --uft-green-light: #009E73;
    --uft-yellow: #F3A61E;
    --uft-surface: #F4F6F9;
    --uft-border: #E2E8F0;
    --uft-muted: #64748B;
    --uft-text: #0F172A;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--uft-text);
}

.stApp {
    background: var(--uft-surface);
}

[data-testid="stAppViewContainer"] > .main {
    background: var(--uft-surface);
    padding-top: .5rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--uft-navy) 0%, var(--uft-navy-dark) 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, var(--uft-navy) 0%, var(--uft-navy-dark) 100%);
}

[data-testid="stSidebar"] [data-testid="stImage"] {
    margin-inline: auto;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #CBD5E1;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #CBD5E1 !important;
    font-size: .78rem;
    font-weight: 500;
    letter-spacing: normal;
    text-transform: none;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] input {
    background: var(--uft-navy-input) !important;
    border-color: rgba(148,163,184,.35) !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] [data-baseweb="tag"],
[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: var(--uft-green) !important;
    border-color: rgba(255,255,255,.15) !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #001730;
    border: 1px solid #263C53;
    border-radius: 8px;
    margin-bottom: 0;
    overflow: hidden;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    background: transparent !important;
    color: #F8FAFC !important;
    font-size: .78rem;
    font-weight: 700;
    padding: 12px 10px !important;
    gap: 8px;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
    background: #15344D !important;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary::before {
    content: "";
    width: 18px;
    height: 18px;
    flex: 0 0 18px;
    background: center / contain no-repeat;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
    font-size: .76rem !important;
    font-weight: 600;
    line-height: 1.4;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary > span:has([data-testid="stIconMaterial"]) {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    min-width: 0;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary > span > span:has([data-testid="stIconMaterial"]) {
    order: 2;
    margin-left: auto;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary:focus-visible {
    outline: 2px solid #F3A61E;
    outline-offset: -3px;
}

[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
    border-top: 1px solid #263C53;
    padding: 10px !important;
    background: rgba(15,23,42,.45);
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: .65rem;
}

[data-testid="stSidebar"] [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"] {
    gap: .15rem;
}

[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.uft-filter-marker),
[data-testid="stSidebar"] [data-testid="element-container"]:has(.uft-filter-marker) {
    display: none;
}

[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
    width: 100%;
    padding: 5px 6px;
    border-radius: 5px;
    align-items: center;
}

[data-testid="stSidebar"] [data-testid="stCheckbox"] label:hover {
    background: rgba(148,163,184,.10);
}

[data-testid="stSidebar"] [data-testid="stCheckbox"] label:not(:has(input[role="switch"])) > div:first-of-type {
    background: #001730;
    border: 1px solid #64748B;
    border-radius: 4px;
}

[data-testid="stSidebar"] [data-testid="stCheckbox"] label:not(:has(input[role="switch"])):has(input:checked) > div:first-of-type {
    background: var(--uft-green);
    border-color: #34D399;
}

[data-testid="stSidebar"] [data-testid="stCheckbox"] label p,
[data-testid="stSidebar"] [data-testid="stToggle"] label p {
    color: #E2E8F0 !important;
    font-size: .76rem !important;
    line-height: 1.4;
}

[data-testid="stSidebar"] [data-testid="stToggle"] label,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label:has(input[role="switch"]) {
    padding: 8px 6px;
    background: #152E45;
    border: 1px solid #3B5065;
    border-radius: 8px;
    width: 100%;
    gap: 5px;
}

[data-testid="stSidebar"] [data-testid="stToggle"] label:has(input:checked),
[data-testid="stSidebar"] [data-testid="stCheckbox"] label:has(input[role="switch"]:checked) {
    background: #005D50;
    border-color: #008566;
}

[data-testid="stSidebar"] [data-testid="stToggle"] label:has(input:checked) > div:first-of-type,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label:has(input[role="switch"]:checked) > div:first-of-type {
    background: #009E73 !important;
}

[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
    gap: 8px;
}

[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:has(input[role="switch"]) {
    flex-wrap: nowrap !important;
}

[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:has(input[role="switch"]) > :is([data-testid="stColumn"], [data-testid="column"]) {
    flex: 1 1 0 !important;
    width: calc(50% - 4px) !important;
    min-width: 0 !important;
}

[data-testid="stSidebar"] .uft-filter-heading {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #CBD5E1;
    font-size: .68rem;
    font-weight: 700;
    letter-spacing: .065em;
    text-transform: uppercase;
    margin: 12px 0 2px;
}

.uft-filter-heading svg { width: 17px; height: 17px; flex-shrink: 0; }

[data-testid="stSidebar"] .uft-filter-divider {
    border-top: 1px solid #334155;
    padding-top: 16px;
    margin: 12px 0 4px;
    color: #94A3B8;
    font-size: .64rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
}

[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
[data-testid="stSidebar"] [data-testid="stExpander"] summary span {
    color: #F8FAFC !important;
}

.sidebar-stripe {
    height: 3px;
    background: linear-gradient(90deg, var(--uft-yellow) 0%, var(--uft-green-light) 100%);
    margin: 0 -1rem .8rem;
    border-radius: 999px;
}

.uft-brand {
    text-align: center;
    padding: 10px 8px 12px;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(226,232,240,.14);
}

.uft-brand-title {
    color: #FFFFFF;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.uft-brand-subtitle {
    color: #6EE7B7;
    font-size: .68rem;
    font-weight: 600;
    margin-top: 3px;
}

.uft-header-anchor + div [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    background: #FFFFFF;
    border: 1px solid var(--uft-border);
    border-top: 4px solid var(--uft-yellow);
    border-radius: 12px;
    box-shadow: 0 4px 18px rgba(15,23,42,.07);
    padding: 10px 18px;
    position: sticky;
    top: .5rem;
    z-index: 20;
}

.uft-header-title {
    color: var(--uft-navy);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.16rem;
    font-weight: 800;
    letter-spacing: -.02em;
    line-height: 1.2;
}

.uft-header-meta {
    color: var(--uft-muted);
    font-size: .72rem;
    font-weight: 500;
    margin-top: 4px;
}

.uft-header-meta strong {
    color: var(--uft-green);
}

.header-actions {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
}

.count-pill,
.access-pill {
    border-radius: 999px;
    font-size: .68rem;
    font-weight: 700;
    padding: 7px 11px;
    text-align: center;
    white-space: nowrap;
}

.count-pill {
    background: linear-gradient(90deg, var(--uft-navy), #0D3868);
    color: #FFFFFF;
}

.access-pill {
    background: #FFFFFF;
    border: 1px solid var(--uft-border);
    color: var(--uft-muted);
}

.uft-header-stripe {
    background: linear-gradient(90deg, var(--uft-yellow), var(--uft-green-light));
    border-radius: 0 0 6px 6px;
    height: 3px;
    margin-bottom: 14px;
}

.krow {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 18px;
}

.kc {
    background: #FFFFFF;
    border: 1px solid rgba(226,232,240,.95);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(15,23,42,.04);
    flex: 1;
    min-width: 138px;
    padding: 12px 13px 10px;
    position: relative;
    transition: box-shadow .2s ease, transform .2s ease;
}

.kc:hover {
    box-shadow: 0 6px 18px rgba(15,23,42,.09);
    transform: translateY(-1px);
}

.kc-bar {
    border-radius: 12px 12px 0 0;
    height: 4px;
    left: 0;
    position: absolute;
    right: 0;
    top: 0;
}

.kc-ico {
    font-size: 1.05rem;
    margin-bottom: 5px;
}

.kc-val {
    color: var(--uft-text);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.42rem;
    font-weight: 800;
    line-height: 1.15;
}

.kc-lbl {
    color: var(--uft-muted);
    font-size: .61rem;
    font-weight: 800;
    letter-spacing: .06em;
    margin-top: 3px;
    text-transform: uppercase;
}

.kc-sub {
    color: #94A3B8;
    font-size: .61rem;
    margin-top: 2px;
}

.card {
    background: #FFFFFF;
    border: 1px solid var(--uft-border);
    border-radius: 12px;
    box-shadow: 0 2px 9px rgba(15,23,42,.045);
    margin-bottom: 12px;
    padding: 14px 14px 5px;
}

.sec {
    border-bottom: 2px solid var(--uft-yellow);
    color: var(--uft-navy);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: .9rem;
    font-weight: 800;
    margin: 20px 0 12px;
    padding-bottom: 6px;
}

.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border: 1px solid var(--uft-border);
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    color: var(--uft-muted);
    font-size: .73rem;
    font-weight: 700;
    padding: 8px 11px;
}

.stTabs [aria-selected="true"] {
    background: #E8F5F1;
    color: var(--uft-green) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--uft-border);
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stDownloadButton"] button {
    border-radius: 8px;
    font-weight: 700;
}

@media (max-width: 900px) {
    .uft-header-anchor + div [data-testid="stHorizontalBlock"] {
        padding: 8px 12px;
        position: static;
    }
    .uft-header-title { font-size: 1rem; }
    .header-actions { justify-content: flex-start; margin-top: 6px; }
    .kc { min-width: 125px; }
}

@media (max-width: 600px) {
    [data-testid="stAppViewContainer"] > .main { padding-top: .2rem; }
    .krow { gap: 7px; }
    .kc { min-width: calc(50% - 7px); }
    .stTabs [data-baseweb="tab"] { font-size: .66rem; padding: 7px 6px; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def card(fig):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False, "responsive": True},
    )
    st.markdown("</div>", unsafe_allow_html=True)

def sec(t):
    st.markdown(f'<div class="sec">{t}</div>', unsafe_allow_html=True)

def kpi(ico, val, lbl, cor, sub=""):
    s = f'<div class="kc-sub">{sub}</div>' if sub else ""
    return (f'<div class="kc"><div class="kc-bar" style="background:{cor}"></div>'
            f'<div class="kc-ico">{ico}</div><div class="kc-val">{val}</div>'
            f'<div class="kc-lbl">{lbl}</div>{s}</div>')

def pct(serie, nome="Valor"):
    ct = serie.value_counts().reset_index()
    ct.columns = [nome, "Qtd"]
    ct["%"] = (ct["Qtd"] / ct["Qtd"].sum() * 100).round(1)
    ct["Label"] = ct["Qtd"].astype(str) + " (" + ct["%"].astype(str) + "%)"
    return ct

# ============================================================
# CLASSIFICAÇÕES
# ============================================================
TIT_GRUPO = {
    "DOUTORADO":"Doutorado","PÓS DOUTORADO":"Pós-Doutorado","MESTRADO":"Mestrado",
    "ESPECIALIZAÇÃO":"Especialização","APERFEIÇOAMENTO":"Especialização",
    "PÓS GRADUADO":"Especialização","GRADUAÇÃO":"Graduação",
    "2 GRAU COMPLETO OU TÉCNICO":"Médio/Técnico",
    "1 GRAU COMPLETO - ATÉ 8 SÉRIE COMPLETO":"Fundamental",
    "1 GRAU INCOMPLETO ATÉ 4 SÉRIE INCOMPLETA":"Fundamental",
    "ANALFABETO":"Fundamental","ESCOLARIDADE/TITULAÇÃO INDEFINIDA":"Não informado",
}
ORDEM_TIT = ["Pós-Doutorado","Doutorado","Mestrado","Especialização",
             "Graduação","Médio/Técnico","Fundamental","Não informado"]
# Pesos do IQCD (Índice de Qualificação do Corpo Docente — INEP/SINAES):
# Doutor 5, Mestre 3, Especialista 2, Graduado 1. Pós-doutorado não é
# titulação acadêmica no SIAPE, por isso conta como Doutorado.
PESOS_TIT = {"Pós-Doutorado":5,"Doutorado":5,"Mestrado":3,"Especialização":2,
             "Graduação":1,"Médio/Técnico":0,"Fundamental":0,"Não informado":0}
CAMPUS_KEYS = [
    ("palmas","Palmas"),("araguaína","Araguaína"),("araguaina","Araguaína"),
    ("porto nacional","Porto Nacional"),("gurupi","Gurupi"),("arraias","Arraias"),
    ("tocantinópolis","Tocantinópolis"),("tocantinopolis","Tocantinópolis"),
    ("miracema","Miracema"),("reitoria","Reitoria"),
    ("universidade federal do tocantins","UFT – Geral"),
]
def extrai_campus(s):
    if pd.isna(s) or not str(s).strip(): return "Não informado"
    sl = str(s).lower()
    for kw, nm in CAMPUS_KEYS:
        if kw in sl: return nm
    return "Outras Unidades"

# Campus que não identificam um local específico: não dá para comparar
CAMPUS_INDEF = {"Não informado", "Outras Unidades", "UFT – Geral"}

def grupo_ingresso(v):
    v = str(v).upper()
    if "CONCURSO"  in v: return "Concurso Público"
    if "CONTRAT"   in v: return "Contratação Direta"
    if "CONVIDADO" in v: return "Convidado"
    if "BOLSISTA"  in v: return "Bolsista"
    if "REDISTRIB" in v: return "Redistribuição"
    if "VOLUNTÁRI" in v or "VOLUNTARIO" in v: return "Voluntário"
    return "Outros"

def grupo_carga(v):
    v = str(v).upper().strip()
    if v == "40 HORAS":            return "40 h"
    if v == "DEDICAÇÃO EXCLUSIVA": return "D.E."
    if v == "20 HORAS":            return "20 h"
    if v in ("30 HORAS","25 HORAS","24 HORAS","12 HORAS"): return "Parcial"
    return "Conv./Bol./Vol."

FAIXAS   = [(0,30,"Até 30"),(31,40,"31–40"),(41,50,"41–50"),(51,60,"51–60"),(61,999,"61+")]
ORD_FXAS = [f[2] for f in FAIXAS]
ARQUIVO  = os.path.join(BASE_DIR, "perfil.xlsx")
ABAS     = {"TÉCNICO": ("técnico", "tecnico"), "DOCENTE": ("docente",)}

def acha_aba(nomes, candidatos):
    for n in nomes:
        if n.strip().lower() in candidatos:
            return n
    return None

# ============================================================
# CARREGAMENTO
# ============================================================
@st.cache_data(show_spinner="📂 Carregando dados…")
def carrega():
    if not os.path.exists(ARQUIVO):
        return None, f"Arquivo não encontrado: {ARQUIVO}"
    try:
        xl    = pd.ExcelFile(ARQUIVO, engine="openpyxl")
        partes = []
        for cat, candidatos in ABAS.items():
            aba = acha_aba(xl.sheet_names, candidatos)
            if aba is None:
                return None, (f"Aba '{candidatos[0]}' não encontrada em perfil.xlsx "
                              f"(abas existentes: {', '.join(xl.sheet_names)})")
            parte = xl.parse(aba, dtype=str)
            parte["CATEGORIA"] = cat
            partes.append(parte)
    except Exception as e:
        return None, f"Erro ao ler Excel: {e}"

    df = pd.concat(partes, ignore_index=True)

    for c in ["CPF","CPF_SERVIDOR","RG","DOCUMENTO","NOME"]:
        if c in df.columns: df.drop(columns=c, inplace=True)

    for c in df.select_dtypes(include=["object","string"]).columns:
        df[c] = df[c].str.strip()

    # Linhas idênticas em todas as colunas são registros duplicados
    n_antes = len(df)
    df = df.drop_duplicates(ignore_index=True)
    df.attrs["duplicados"] = n_antes - len(df)

    df["DT_NASC"] = pd.to_datetime(df["DT_NASC"], dayfirst=True, errors="coerce")
    hoje = pd.Timestamp.today()
    df["IDADE"] = ((hoje - df["DT_NASC"]).dt.days / 365.25).round(1)
    df.loc[(df["IDADE"] > 100) | (df["IDADE"] < 14), "IDADE"] = np.nan

    conds  = [(df["IDADE"] >= lo) & (df["IDADE"] <= hi) for lo,hi,_ in FAIXAS]
    rotulos= [r for *_,r in FAIXAS]
    df["FAIXA"] = np.select(conds, rotulos, default="Não inf.")

    tit_up = df["TITULAÇÃO"].str.upper().str.strip().fillna("")
    df["TIT_GRUPO"] = tit_up.map(TIT_GRUPO).fillna("Não informado")
    df["TIT_GRUPO"] = pd.Categorical(df["TIT_GRUPO"], categories=ORDEM_TIT, ordered=True)

    df["CAMPUS"]         = df["LOTAÇÃO_OFICIAL"].apply(extrai_campus)
    df["INGRESSO_GRUPO"] = df["INGRESSO"].apply(grupo_ingresso)
    df["CARGA_GRUPO"]    = df["CARGA"].apply(grupo_carga)
    # Desvio de lotação: compara o CAMPUS das duas lotações, não o texto.
    # Os textos têm níveis diferentes ("Câmpus Universitário de Palmas" x
    # "Direção do Câmpus de Palmas") e quase nunca são iguais.
    # Só é avaliável quando os dois lados apontam para um local específico.
    campus_vinc          = df["LOTAÇÃO_VINCULADA"].apply(extrai_campus)
    df["DESVIO_AVAL"]    = ~df["CAMPUS"].isin(CAMPUS_INDEF) & ~campus_vinc.isin(CAMPUS_INDEF)
    df["DESVIO"]         = df["DESVIO_AVAL"] & (df["CAMPUS"] != campus_vinc)
    return df, None

df_raw, erro = carrega()
if erro:
    st.error(f"❌ {erro}")
    st.stop()

# ============================================================
# ▼▼▼ SIDEBAR — Logo + Filtros ▼▼▼
#
# A logo é exibida com st.sidebar.image().
# O cabeçalho da sidebar usa HTML com as cores P e D definidas acima.
# ============================================================

# ── Logo na sidebar ──────────────────────────────────────────
# st.sidebar.image() carrega o arquivo direto — sem base64,
# sem filtro CSS. Funciona localmente e no Streamlit Cloud.
# Para centralizar a imagem usamos 3 colunas dentro da sidebar.
if LOGO_PATH:
    sb1, sb2, sb3 = st.sidebar.columns([1.5, 1.4, 1.5])
    with sb2:
        st.image(LOGO_PATH, width=78)
else:
    st.sidebar.markdown(
        '<div style="text-align:center;font-size:2.4rem;padding:.5rem 0;">🎓</div>',
        unsafe_allow_html=True
    )

# =================================================================
# SIDEBAR — BLOCO DE TÍTULO
# -----------------------------------------------------------------
# Caixinha com fundo semi-transparente claro dentro da sidebar escura.
# Bordas: topo dourado (D) + lateral teal suave (VD).
# Textos: branco para título, dourado claro para subtítulo.
# Para mudar cores: ajuste as variáveis D, VD e P na PALETA acima.
# =================================================================
st.sidebar.markdown(f"""
<div class="sidebar-stripe"></div>

<div class="uft-brand">
  <div class="uft-brand-title">PROGRAD</div>
  <div class="uft-brand-subtitle">Pró-Reitoria de Graduação</div>
  <div style="font-size:.64rem;color:#CBD5E1;margin-top:5px;">
    Coordenação de Avaliação e Educação
  </div>
</div>
""", unsafe_allow_html=True)

# Ícones vetoriais locais, com o mesmo traço e acentos do protótipo.
# Não dependem de Font Awesome, fontes de ícones ou conexão externa.
FILTER_ICONS = {
    "category": ('#F3A61E', '<circle cx="9" cy="7" r="4"/><path d="M2 21v-3a7 7 0 0 1 12-5m3 1 2-2 3 3-2 2m-6 1 5-5 3 3-5 5-4 1z"/>'),
    "gender": ('#A5B4FC', '<circle cx="8" cy="9" r="4"/><path d="M8 13v8m-3-3h6m2-7 7-7m-5 0h5v5"/>'),
    "qualification": ('#F3A61E', '<circle cx="12" cy="8" r="5"/><path d="m8 12-2 9 6-3 6 3-2-9"/>'),
    "workload": ('#38BDF8', '<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>'),
    "status": ('#34D399', '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 2h6v4H9zM9 17h6"/><circle cx="12" cy="11" r="2"/>'),
    "legal": ('#C4B5FD', '<path d="M12 3v18M4 21h16M3 7h18M6 7l-4 8h8L6 7zm12 0-4 8h8l-4-8z"/>'),
    "entry": ('#FB923C', '<path d="M14 4h6v16h-6M3 12h12m-4-4 4 4-4 4"/>'),
    "campus": ('#38BDF8', '<path d="m3 9 9-6 9 6H3zm2 3v7m5-7v7m4-7v7m5-7v7M2 22h20"/>'),
}


def filter_icon(name):
    color, paths = FILTER_ICONS[name]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'fill="none" stroke="{color}" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{paths}</svg>')


icon_rules = []
for icon_name in FILTER_ICONS:
    icon_data = base64.b64encode(filter_icon(icon_name).encode()).decode()
    icon_rules.append(
        '[data-testid="stSidebar"] [data-testid="stExpander"]'
        f':has(.uft-filter-{icon_name}) summary::before '
        f'{{background-image:url("data:image/svg+xml;base64,{icon_data}");}}'
    )
st.sidebar.markdown('<style>' + '\n'.join(icon_rules) + '</style>', unsafe_allow_html=True)


def toggle_filters(title, column, options, icon, labels=None):
    """Seleção independente: ambas as opções podem estar ligadas ou desligadas."""
    st.sidebar.markdown(
        f'<div class="uft-filter-heading">{filter_icon(icon)}{title}</div>',
        unsafe_allow_html=True,
    )
    selected = []
    columns = st.sidebar.columns(2)
    for index, option in enumerate(options):
        label = (labels or {}).get(str(option).upper(), str(option))
        with columns[index % 2]:
            if st.toggle(label, value=True, key=f"uft_filter_{column}_{option}"):
                selected.append(option)
    return selected


def checkbox_filters(title, column, icon, options=None, default=None, expanded=False):
    """Retorna os valores originais da base, mantendo o contrato dos filtros."""
    if options is None:
        options = sorted(df_raw[column].dropna().unique())
    defaults = set(options if default is None else default)
    selected = []
    with st.sidebar.expander(title, expanded=expanded):
        st.markdown(
            f'<span class="uft-filter-marker uft-filter-{icon}"></span>',
            unsafe_allow_html=True,
        )
        for option in options:
            label = str(option)
            if label.isupper():
                label = label.capitalize()
            if st.checkbox(label, value=option in defaults,
                           key=f"uft_filter_{column}_{option}"):
                selected.append(option)
    return selected


cat_sel = toggle_filters(
    "Categoria funcional", "CATEGORIA", ["DOCENTE", "TÉCNICO"], "category",
    {"DOCENTE": "Docente", "TÉCNICO": "Técnico"},
)
sexo_sel = toggle_filters(
    "Sexo / Gênero", "SEXO", sorted(df_raw["SEXO"].dropna().unique()), "gender",
    {"M": "Masculino", "F": "Feminino", "MASCULINO": "Masculino", "FEMININO": "Feminino"},
)

st.sidebar.markdown('<div class="uft-filter-divider">Filtros avançados</div>',
                    unsafe_allow_html=True)
tit_opts = [t for t in ORDEM_TIT if t in df_raw["TIT_GRUPO"].values]
tit_sel = checkbox_filters("Qualificação e titulação", "TIT_GRUPO", "qualification",
                           options=tit_opts, expanded=True)
carga_sel = checkbox_filters("Carga horária / Regime", "CARGA_GRUPO", "workload")
sit_opts = sorted(df_raw["SITUAÇÃO"].dropna().unique())
# Mantém o padrão anterior: somente ativos, se essa situação existir na base.
sit_sel = checkbox_filters("Situação funcional", "SITUAÇÃO", "status",
                           options=sit_opts,
                           default=[s for s in sit_opts if s.upper() == "ATIVO"] or sit_opts)
reg_sel = checkbox_filters("Regime jurídico", "REGIME_JURIDICO", "legal")
ing_sel = checkbox_filters("Forma de ingresso", "INGRESSO_GRUPO", "entry")
campus_sel = checkbox_filters("Campus universitário", "CAMPUS", "campus")
st.sidebar.caption("Marque as opções desejadas. Os indicadores são atualizados automaticamente.")

# ============================================================
# FILTROS
# ============================================================
df_f = df_raw[
    df_raw["CATEGORIA"].isin(cat_sel) &
    df_raw["SEXO"].isin(sexo_sel) &
    df_raw["CAMPUS"].isin(campus_sel) &
    df_raw["SITUAÇÃO"].isin(sit_sel) &
    df_raw["TIT_GRUPO"].isin(tit_sel) &
    df_raw["REGIME_JURIDICO"].isin(reg_sel) &
    df_raw["CARGA_GRUPO"].isin(carga_sel) &
    df_raw["INGRESSO_GRUPO"].isin(ing_sel)
].copy()

if df_f.empty:
    st.warning("⚠️ Nenhum registro com os filtros selecionados.")
    st.stop()

# ============================================================
# KPIs
# ============================================================
total    = len(df_f)
docentes = (df_f["CATEGORIA"] == "DOCENTE").sum()
tecnicos = (df_f["CATEGORIA"] == "TÉCNICO").sum()
ativos   = (df_f["SITUAÇÃO"].str.upper() == "ATIVO").sum()
dout_pd  = df_f["TIT_GRUPO"].isin(["Doutorado","Pós-Doutorado"]).sum()
mestres  = (df_f["TIT_GRUPO"] == "Mestrado").sum()
desvios  = int(df_f["DESVIO"].sum())
n_aval   = int(df_f["DESVIO_AVAL"].sum())
pct_desv = round(desvios / max(n_aval,1) * 100, 1)

def iqcd(d):
    """Média ponderada da titulação (pesos IQCD). None se não houver registros."""
    if d.empty: return None
    return round(d["TIT_GRUPO"].astype(str).map(PESOS_TIT).fillna(0).mean(), 2)

iqcd_doc = iqcd(df_f[df_f["CATEGORIA"] == "DOCENTE"])
iqcd_tec = iqcd(df_f[df_f["CATEGORIA"] == "TÉCNICO"])
iqcd_s   = f"{iqcd_doc:.2f}/5" if iqcd_doc is not None else "—"
idade_v  = df_f["IDADE"].mean()
idade_s  = f"{idade_v:.1f} a" if pd.notna(idade_v) else "—"

# ============================================================
# ▼▼▼ HEADER — Altere aqui a cor/estilo do título principal ▼▼▼
#
# background: usa as variáveis P, S e D da paleta acima.
# Para mudar o fundo do cabeçalho, troque P, S ou D.
# A logo aparece à esquerda (se disponível) ou um emoji.
# ============================================================
# =================================================================
# HEADER PRINCIPAL — composição inspirada na tela do Stitch
# =================================================================
st.markdown('<div class="uft-header-anchor" style="display:none;"></div>',
            unsafe_allow_html=True)

# ── Colunas do header: [logo | título | ações] ───────────────
col_logo, col_titulo, col_badge = st.columns([0.8, 6.2, 3])

with col_logo:
    if LOGO_PATH:
        # st.image() lê o arquivo diretamente — sem base64 nem data: URI
        st.image(LOGO_PATH, width=76)
    else:
        st.markdown(
            '<div style="font-size:3rem;text-align:center;padding-top:4px;">🎓</div>',
            unsafe_allow_html=True
        )

with col_titulo:
    st.markdown("""
<div style="padding:4px 0;">
  <div class="uft-header-title">Painel Docentes e Técnicos</div>
  <div class="uft-header-meta">
    Universidade Federal do Tocantins · <strong>Gestão Estratégica de Pessoas &amp; PROGRAD</strong>
  </div>
</div>
""", unsafe_allow_html=True)

with col_badge:
    st.markdown(f"""
<div class="header-actions">
  <div class="count-pill">👥 {total:,} registros filtrados</div>
  <div class="access-pill">🔒 Acesso Restrito · Entrar</div>
</div>
""", unsafe_allow_html=True)

# Faixa decorativa abaixo das colunas
st.markdown('<div class="uft-header-stripe"></div>', unsafe_allow_html=True)

# ============================================================
# KPI CARDS
# ============================================================
st.markdown(
    '<div class="krow">'
    + kpi("👥", f"{total:,}",      "Total",         P)
    + kpi("🏫", f"{docentes:,}",   "Docentes",      A,  f"{docentes/max(total,1)*100:.1f}%")
    + kpi("🔧", f"{tecnicos:,}",   "Técnicos",      D,  f"{tecnicos/max(total,1)*100:.1f}%")
    + kpi("✅", f"{ativos:,}",     "Ativos",        VD, f"{ativos/max(total,1)*100:.1f}%")
    + kpi("🎓", f"{dout_pd:,}",    "Doutores/PD",   D,  f"{dout_pd/max(total,1)*100:.1f}%")
    + kpi("📚", f"{mestres:,}",    "Mestres",       A,  f"{mestres/max(total,1)*100:.1f}%")
    + kpi("⭐", iqcd_s,            "IQCD Docente",  VD, "pesos INEP")
    + kpi("🎂", idade_s,           "Idade Média",   A)
    + kpi("⚠️", f"{pct_desv}%",   "Desvio Lot.",   AL, f"{desvios:,} de {n_aval:,} avaliáveis")
    + '</div>',
    unsafe_allow_html=True
)

# ============================================================
# ABAS
# ============================================================
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🎓 Qualificação","🏢 Lotação & Campus",
    "⚖️ Regime & Situação","📈 Perfil Etário",
    "⚠️ Desvio & Ingresso","📄 Tabela & Download",
])

with tab1:
    sec("🎓 Titulação por Categoria")
    c1,c2 = st.columns([3,2])
    with c1:
        tg = df_f.groupby(["TIT_GRUPO","CATEGORIA"]).size().reset_index(name="Qtd")
        tg["TIT_GRUPO"] = pd.Categorical(tg["TIT_GRUPO"],categories=ORDEM_TIT,ordered=True)
        fig = px.bar(tg.sort_values("TIT_GRUPO"),x="Qtd",y="TIT_GRUPO",color="CATEGORIA",
                     orientation="h",barmode="stack",height=380,text_auto=True,
                     color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                     labels={"TIT_GRUPO":"Titulação","Qtd":"Quantidade"})
        fig.update_layout(**BL,legend=dict(orientation="h",y=-0.18,font_size=12),
                          xaxis=dict(showgrid=True,gridcolor="#EEF2F8"))
        card(fig)
    with c2:
        sd = pct(df_f["SEXO"].map({"M":"Masculino","F":"Feminino"}).fillna(df_f["SEXO"]),"Sexo")
        fig = px.pie(sd,names="Sexo",values="Qtd",hole=0.58,height=380,
                     color_discrete_sequence=[P,D])
        fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
                          textposition="outside",textfont_size=12)
        fig.update_layout(**BL)
        card(fig)

    sec("💼 Top 15 Cargos")
    tc1,tc2 = st.columns(2)
    with tc1:
        st.caption("**Técnico-Administrativos**")
        ct = pct(df_f[df_f["CATEGORIA"]=="TÉCNICO"]["CARGO"],"Cargo").head(15)
        fig = px.bar(ct,x="Qtd",y="Cargo",orientation="h",text="Label",
                     color="Qtd",color_continuous_scale=ESC_OURO,height=480)
        fig.update_traces(textposition="outside",textfont_size=10)
        fig.update_layout(**BL,coloraxis_showscale=False,
                          xaxis=dict(showgrid=True,gridcolor="#F8F4EA",
                                     range=[0,ct["Qtd"].max()*1.35]))
        card(fig)
    with tc2:
        st.caption("**Docentes**")
        cd = pct(df_f[df_f["CATEGORIA"]=="DOCENTE"]["CARGO"],"Cargo").head(15)
        fig = px.bar(cd,x="Qtd",y="Cargo",orientation="h",text="Label",
                     color="Qtd",color_continuous_scale=ESC_AZUL,height=480)
        fig.update_traces(textposition="outside",textfont_size=10)
        fig.update_layout(**BL,coloraxis_showscale=False,
                          xaxis=dict(showgrid=True,gridcolor="#EEF2F8",
                                     range=[0,cd["Qtd"].max()*1.35]))
        card(fig)

    sec("📊 Índice de Qualificação (pesos IQCD: Doutor 5 · Mestre 3 · Especialista 2 · Graduado 1)")
    def gauge(valor, titulo):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",value=valor,
            number={"suffix":" / 5","font":{"size":40,"color":P}},
            title={"text":titulo,"font":{"size":14}},
            gauge={"axis":{"range":[0,5],"tickwidth":1,"tickcolor":P},
                   "bar":{"color":P,"thickness":0.25},"bgcolor":"white",
                   "borderwidth":2,"bordercolor":BD,
                   "steps":[{"range":[0,1],"color":"#F0F4FA"},{"range":[1,2],"color":"#C5D9F0"},
                             {"range":[2,3],"color":"#5A9AD4"},{"range":[3,4],"color":"#1A5FA8"},
                             {"range":[4,5],"color":P}]},
        ))
        fig.update_layout(**BL,height=280)
        return fig
    g1,g2 = st.columns(2)
    with g1:
        if iqcd_doc is not None: card(gauge(iqcd_doc, "<b>Docentes</b> · IQCD"))
        else: st.info("Nenhum docente nos filtros selecionados.")
    with g2:
        if iqcd_tec is not None: card(gauge(iqcd_tec, "<b>Técnicos</b> · mesma escala (referência)"))
        else: st.info("Nenhum técnico nos filtros selecionados.")
    st.caption("Docentes e técnicos são calculados separadamente: os perfis de titulação "
               "das duas carreiras não são comparáveis. O IQCD oficial se aplica apenas a docentes.")

with tab2:
    sec("🗺️ Distribuição por Campus")
    ca1,ca2 = st.columns(2)
    with ca1:
        cp = pct(df_f["CAMPUS"],"Campus").sort_values("Qtd",ascending=True)
        fig = px.bar(cp,x="Qtd",y="Campus",orientation="h",text="Label",
                     color="Qtd",color_continuous_scale=ESC_AZUL,height=420)
        fig.update_traces(textposition="outside",textfont_size=11)
        fig.update_layout(**BL,coloraxis_showscale=False,
                          xaxis=dict(showgrid=True,gridcolor="#EEF2F8",
                                     range=[0,cp["Qtd"].max()*1.32]))
        card(fig)
    with ca2:
        heat = pd.crosstab(df_f["CAMPUS"],df_f["CATEGORIA"])
        fig  = px.imshow(heat,text_auto=True,aspect="auto",
                         color_continuous_scale=ESC_AZUL,height=420,
                         labels=dict(x="Categoria",y="Campus",color="Qtd"))
        fig.update_layout(**BL)
        card(fig)

    sec("🔥 Heatmap Campus × Titulação")
    heat2    = pd.crosstab(df_f["CAMPUS"],df_f["TIT_GRUPO"])
    cols_ord = [c for c in ORDEM_TIT if c in heat2.columns]
    fig = px.imshow(heat2[cols_ord],text_auto=True,aspect="auto",
                    color_continuous_scale=ESC_TEAL,height=460,
                    labels=dict(x="Titulação",y="Campus",color="Qtd"))
    fig.update_layout(**BL)
    card(fig)

    sec("🗂️ Lotação de Exercício — Top 20 Unidades")
    lex = df_f["LOTAÇÃO_EXERCÍCIO"].value_counts().head(20).reset_index()
    lex.columns = ["Unidade","Qtd"]
    lex["%"]    = (lex["Qtd"]/lex["Qtd"].sum()*100).round(1)
    lex["Label"]= lex["Qtd"].astype(str)+" ("+lex["%"].astype(str)+"%)"
    lex = lex.sort_values("Qtd",ascending=True)
    fig = px.bar(lex,x="Qtd",y="Unidade",orientation="h",text="Label",
                 color="Qtd",color_continuous_scale=ESC_AZUL,height=580)
    fig.update_traces(textposition="outside",textfont_size=10)
    fig.update_layout(**BL,coloraxis_showscale=False,
                      xaxis=dict(showgrid=True,gridcolor="#EEF2F8",
                                 range=[0,lex["Qtd"].max()*1.3]),
                      yaxis=dict(tickfont_size=10))
    card(fig)

with tab3:
    sec("⚖️ Regime Jurídico")
    r1,r2,r3 = st.columns(3)
    with r1:
        rg = pct(df_f["REGIME_JURIDICO"],"Regime")
        fig = px.pie(rg,names="Regime",values="Qtd",hole=0.54,height=360,
                     color_discrete_sequence=CATS)
        fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
                          textposition="outside",textfont_size=10)
        fig.update_layout(**BL)
        card(fig)
    with r2:
        rcat = df_f.groupby(["REGIME_JURIDICO","CATEGORIA"]).size().reset_index(name="Qtd")
        fig  = px.bar(rcat,x="REGIME_JURIDICO",y="Qtd",color="CATEGORIA",
                      barmode="group",height=360,text_auto=True,
                      color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                      labels={"REGIME_JURIDICO":"Regime","Qtd":"Qtd"})
        fig.update_layout(**BL,xaxis_tickangle=-30,
                          legend=dict(orientation="h",y=-0.3,font_size=11))
        card(fig)
    with r3:
        rtit = df_f.groupby(["REGIME_JURIDICO","TIT_GRUPO"]).size().reset_index(name="Qtd")
        rtit["TIT_GRUPO"] = pd.Categorical(rtit["TIT_GRUPO"],categories=ORDEM_TIT,ordered=True)
        fig = px.bar(rtit,x="REGIME_JURIDICO",y="Qtd",color="TIT_GRUPO",
                     barmode="stack",height=360,text_auto=True,
                     color_discrete_sequence=CATS,
                     labels={"REGIME_JURIDICO":"Regime","Qtd":"Qtd","TIT_GRUPO":"Titulação"})
        fig.update_layout(**BL,xaxis_tickangle=-30,
                          legend=dict(orientation="h",y=-0.3,font_size=10))
        card(fig)

    sec("✅ Situação Funcional")
    s1,s2 = st.columns([2,3])
    with s1:
        sit = pct(df_f["SITUAÇÃO"],"Situação")
        fig = px.bar(sit.sort_values("Qtd"),x="Qtd",y="Situação",
                     orientation="h",text="Label",
                     color="Qtd",color_continuous_scale=ESC_AZUL,height=520)
        fig.update_traces(textposition="outside",textfont_size=10)
        fig.update_layout(**BL,coloraxis_showscale=False,
                          xaxis=dict(showgrid=True,gridcolor="#EEF2F8",
                                     range=[0,sit["Qtd"].max()*1.4]),
                          yaxis=dict(tickfont_size=10))
        card(fig)
    with s2:
        scat = df_f.groupby(["SITUAÇÃO","CATEGORIA"]).size().reset_index(name="Qtd")
        scat = scat.merge(sit[["Situação","Qtd"]].rename(
                    columns={"Situação":"SITUAÇÃO","Qtd":"Total"}),on="SITUAÇÃO")
        scat = scat.sort_values("Total",ascending=False)
        fig  = px.bar(scat,x="Qtd",y="SITUAÇÃO",color="CATEGORIA",
                      orientation="h",barmode="group",height=520,text_auto=True,
                      color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                      labels={"SITUAÇÃO":"Situação","Qtd":"Qtd"})
        fig.update_layout(**BL,legend=dict(orientation="h",y=-0.1,font_size=12),
                          yaxis=dict(tickfont_size=10))
        card(fig)

with tab4:
    df_id = df_f.dropna(subset=["IDADE"])
    sec("📈 Distribuição de Idades")
    e1,e2 = st.columns(2)
    with e1:
        fig = px.histogram(df_id,x="IDADE",nbins=25,color="CATEGORIA",
                           barmode="overlay",height=360,opacity=0.75,marginal="rug",
                           color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                           labels={"IDADE":"Idade (anos)"})
        fig.update_layout(**BL,bargap=0.05,
                          legend=dict(orientation="h",y=-0.2,font_size=12),
                          xaxis=dict(showgrid=True,gridcolor="#EEF2F8"))
        card(fig)
    with e2:
        fig = px.box(df_id,x="CATEGORIA",y="IDADE",color="CATEGORIA",
                     points="outliers",height=360,
                     color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                     labels={"IDADE":"Idade","CATEGORIA":"Categoria"})
        fig.update_layout(**BL,showlegend=False)
        card(fig)

    sec("📊 Faixas Etárias")
    e3,e4 = st.columns(2)
    with e3:
        fx = df_id["FAIXA"].value_counts().reindex(ORD_FXAS).dropna().reset_index()
        fx.columns = ["Faixa","Qtd"]
        fx["%"]    = (fx["Qtd"]/fx["Qtd"].sum()*100).round(1)
        fx["Label"]= fx["Qtd"].astype(str)+" ("+fx["%"].astype(str)+"%)"
        fig = px.bar(fx,x="Faixa",y="Qtd",text="Label",
                     color="Qtd",color_continuous_scale=ESC_TEAL,height=340)
        fig.update_traces(textposition="outside",textfont_size=12)
        fig.update_layout(**BL,coloraxis_showscale=False,
                          yaxis=dict(showgrid=True,gridcolor="#EEF2F8",
                                     range=[0,fx["Qtd"].max()*1.18]))
        card(fig)
    with e4:
        fxcat = df_id.groupby(["FAIXA","CATEGORIA"]).size().reset_index(name="Qtd")
        fxcat["FAIXA"] = pd.Categorical(fxcat["FAIXA"],categories=ORD_FXAS,ordered=True)
        fig = px.bar(fxcat.sort_values("FAIXA"),x="FAIXA",y="Qtd",color="CATEGORIA",
                     barmode="group",height=340,text_auto=True,
                     color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                     labels={"FAIXA":"Faixa Etária","Qtd":"Quantidade"})
        fig.update_layout(**BL,legend=dict(orientation="h",y=-0.2,font_size=12))
        card(fig)

    sec("📋 Estatísticas por Categoria")
    stats = (df_id.groupby("CATEGORIA")["IDADE"]
             .agg(Contagem="count",Mínima="min",Mediana="median",Média="mean",Máxima="max")
             .round(1).reset_index())
    st.dataframe(stats,use_container_width=True,hide_index=True)

with tab5:
    sec("⚠️ Desvio de Lotação (campus oficial ≠ campus vinculado)")
    st.caption("Compara o campus das duas lotações. Registros em que uma das lotações não "
               "indica um campus específico (ex.: \"Coordenação Acadêmica - CORDAC\", "
               "\"Universidade Federal do Tocantins\") entram como **Não avaliável**.")
    d1,d2 = st.columns([1,2])
    with d1:
        status = np.select([~df_f["DESVIO_AVAL"], df_f["DESVIO"]],
                           ["Não avaliável","Com desvio"], default="Sem desvio")
        dv = pct(pd.Series(status),"Status")
        fig = px.pie(dv,names="Status",values="Qtd",hole=0.58,height=320,
                     color="Status",color_discrete_map={"Com desvio":AL,"Sem desvio":VD,
                                                        "Não avaliável":BD})
        fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
                          textposition="outside",textfont_size=12)
        fig.update_layout(**BL)
        card(fig)
    with d2:
        dc = (df_f[df_f["DESVIO"]].groupby("CAMPUS").size()
              .reset_index(name="Com Desvio")
              .merge(df_f[df_f["DESVIO_AVAL"]].groupby("CAMPUS").size()
                     .reset_index(name="Total"),on="CAMPUS"))
        dc["% Desvio"] = (dc["Com Desvio"]/dc["Total"]*100).round(1)
        dc = dc.sort_values("% Desvio",ascending=True)
        fig = px.bar(dc,x="% Desvio",y="CAMPUS",orientation="h",
                     text="% Desvio",color="% Desvio",height=320,
                     color_continuous_scale=[[0,VD],[0.4,D],[1,AL]],
                     labels={"CAMPUS":"Campus","% Desvio":"% com Desvio"})
        fig.update_traces(texttemplate="%{text}%",textposition="outside",textfont_size=11)
        fig.update_layout(**BL,coloraxis_showscale=False,
                          xaxis=dict(range=[0,max(dc["% Desvio"].max()*1.3,1)],
                                     showgrid=True,gridcolor="#EEF2F8"))
        if dc.empty: st.info("Nenhum desvio de lotação nos filtros selecionados.")
        else: card(fig)

    sec("🚪 Forma de Ingresso & Carga Horária")
    i1,i2,i3 = st.columns(3)
    with i1:
        ig = pct(df_f["INGRESSO_GRUPO"],"Ingresso")
        fig = px.pie(ig,names="Ingresso",values="Qtd",hole=0.54,height=340,
                     color_discrete_sequence=CATS)
        fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
                          textposition="outside",textfont_size=10)
        fig.update_layout(**BL)
        card(fig)
    with i2:
        igc = df_f.groupby(["INGRESSO_GRUPO","CATEGORIA"]).size().reset_index(name="Qtd")
        fig = px.bar(igc,x="INGRESSO_GRUPO",y="Qtd",color="CATEGORIA",
                     barmode="group",height=340,text_auto=True,
                     color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                     labels={"INGRESSO_GRUPO":"Ingresso","Qtd":"Qtd"})
        fig.update_layout(**BL,xaxis_tickangle=-25,
                          legend=dict(orientation="h",y=-0.3,font_size=11))
        card(fig)
    with i3:
        chg = pct(df_f["CARGA_GRUPO"],"Carga")
        fig = px.pie(chg,names="Carga",values="Qtd",hole=0.54,height=340,
                     color_discrete_sequence=CATS,title="Carga Horária")
        fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
                          textposition="outside",textfont_size=10)
        fig.update_layout(**BL,title_font=dict(size=13,family="Lora,serif"))
        card(fig)

with tab6:
    sec("📄 Base Consolidada Filtrada")
    cb,ci = st.columns([3,1])
    with cb:
        busca = st.text_input("🔍 Buscar",
                              placeholder="Cargo, campus, situação…",
                              label_visibility="collapsed")
    with ci:
        st.metric("Registros",f"{total:,}")

    EXIB = ["CATEGORIA","SEXO","CARGO","TIT_GRUPO","CARGA_GRUPO","CAMPUS",
            "LOTAÇÃO_EXERCÍCIO","SITUAÇÃO","REGIME_JURIDICO","INGRESSO_GRUPO","IDADE","DESVIO"]
    df_exib = df_f[[c for c in EXIB if c in df_f.columns]].copy()
    df_exib.columns = (df_exib.columns
                       .str.replace("_GRUPO","",regex=False)
                       .str.replace("_"," ",regex=False))

    if busca:
        mask = df_exib.apply(
            lambda col: col.astype(str).str.upper().str.contains(busca.upper(),na=False,regex=False)
        ).any(axis=1)
        df_exib = df_exib[mask]
        st.caption(f"🔎 {len(df_exib):,} resultado(s) para '{busca}'")

    st.dataframe(df_exib,use_container_width=True,height=440)
    c1,c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Baixar Base Filtrada (.csv)",
            data=(df_f.drop(columns=["DT_NASC","DESVIO","DESVIO_AVAL","FAIXA"],errors="ignore")
                      .to_csv(index=False).encode("utf-8")),
            file_name="base_filtrada_uft.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        dup = df_raw.attrs.get("duplicados", 0)
        st.info(f"📁 `perfil.xlsx` · {total:,} registros filtrados"
                + (f" · {dup} linhas duplicadas removidas" if dup else ""))
