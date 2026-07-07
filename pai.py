# ============================================================
# PAINEL ANALÍTICO INSTITUCIONAL — UFT
# Versão com identidade visual oficial da UFT
# ============================================================

import asyncio, sys, os
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

P   = "#003C78"   # AZUL UFT  — faixa horizontal do brasão (cor principal)
S   = "#002856"   # AZUL ESCURO — versão mais escura para degradês
A   = "#005A9E"   # AZUL MÉDIO — botões e destaques azuis
D   = "#F0B41E"   # DOURADO UFT — raios do sol no brasão (cor de destaque)
VD  = "#007878"   # VERDE-TEAL UFT — escudo inferior do brasão
CZ  = "#787878"   # CINZA UFT — letras UFT no brasão
BN  = "#1E1E1E"   # ESCURO — banner "UNIVERSIDADE FEDERAL DO TOCANTINS"

# Cores de apoio (interface)
FG  = "#F4F6F9"   # FUNDO — cinza levíssimo das páginas
BD  = "#DDE3EC"   # BORDA — linhas e separadores
TL  = "#5A6A8A"   # TEXTO LEVE — subtítulos e labels
AL  = "#C0392B"   # ALERTA — vermelho para avisos
OK  = "#007878"   # SUCESSO — reutiliza o verde-teal da UFT

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
# ▼▼▼ CSS GLOBAL — ALTERE AQUI PARA MUDAR ESTILOS ▼▼▼
#
# As variáveis {P}, {S}, {D} etc. são as cores definidas acima.
# Cada bloco CSS tem comentário explicando o que ele estiliza.
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Página geral ───────────────────────────────────────── */
html, body {{ font-family:'DM Sans',sans-serif; color:{P}; }}
.main {{ background:{FG}; padding-top:.3rem; }}

/* ── BARRA LATERAL — cor de fundo e textos ──────────────── */
/* Para mudar a cor da sidebar, altere as variáveis {P} e {S}
   na seção PALETA acima. O gradiente vai de P (topo) a S (base). */
[data-testid="stSidebar"] {{
    background: linear-gradient(175deg, {P} 0%, {S} 100%);
}}
[data-testid="stSidebar"] * {{ color: white !important; }}
[data-testid="stSidebar"] label {{
    font-size: .7rem; font-weight: 600;
    letter-spacing: .06em; text-transform: uppercase; opacity: .8;
}}
[data-testid="stSidebar"] p {{
    font-size: .65rem; opacity: .45;
    letter-spacing: .1em; text-transform: uppercase; margin: 0;
}}

/* ── KPI Cards ──────────────────────────────────────────── */
.krow  {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:16px; }}
.kc    {{ background:white; border:1px solid {BD}; border-radius:12px;
          padding:13px 12px 9px; flex:1; min-width:140px; position:relative; }}
.kc-bar {{ position:absolute; top:0; left:0; right:0;
           height:3px; border-radius:12px 12px 0 0; }}
.kc-ico {{ font-size:1.15rem; margin-bottom:2px; }}
.kc-val {{ font-family:'Lora',serif; font-size:1.6rem;
           font-weight:700; color:{P}; line-height:1.1; }}
.kc-lbl {{ font-size:.63rem; font-weight:700; letter-spacing:.07em;
           text-transform:uppercase; color:{TL}; }}
.kc-sub {{ font-size:.61rem; color:{TL}; margin-top:1px; }}

/* ── Card de gráfico ────────────────────────────────────── */
.card {{ background:white; border:1px solid {BD}; border-radius:12px;
         padding:15px 15px 5px;
         box-shadow:0 1px 6px rgba(0,60,120,.06); margin-bottom:11px; }}

/* ── Título de seção ────────────────────────────────────── */
/* A borda inferior dourada usa {D} — mude {D} acima para outra cor */
.sec {{ font-family:'Lora',serif; font-size:.93rem; font-weight:700;
        color:{P}; padding-bottom:5px;
        border-bottom:2px solid {D}; margin:18px 0 11px; }}

/* ── Faixa dourada decorativa (topo da sidebar) ─────────── */
.sidebar-stripe {{
    height: 3px;
    background: linear-gradient(90deg, {D} 0%, {VD} 100%);
    margin: 0 -1rem .8rem;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def card(fig):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
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
PESOS_TIT = {"Pós-Doutorado":5,"Doutorado":4,"Mestrado":3,"Especialização":2,
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

# ============================================================
# CARREGAMENTO
# ============================================================
@st.cache_data(show_spinner="📂 Carregando dados…")
def carrega():
    if not os.path.exists(ARQUIVO):
        return None, f"Arquivo não encontrado: {ARQUIVO}"
    try:
        xl    = pd.ExcelFile(ARQUIVO, engine="openpyxl")
        nomes = xl.sheet_names
        tec   = xl.parse(nomes[0], dtype=str)
        doc   = xl.parse(nomes[1], dtype=str)
    except Exception as e:
        return None, f"Erro ao ler Excel: {e}"

    tec["CATEGORIA"] = "TÉCNICO"
    doc["CATEGORIA"] = "DOCENTE"
    df = pd.concat([tec, doc], ignore_index=True)

    for c in ["CPF","CPF_SERVIDOR","RG","DOCUMENTO","NOME"]:
        if c in df.columns: df.drop(columns=c, inplace=True)

    for c in df.select_dtypes(include=["object","string"]).columns:
        df[c] = df[c].str.strip()

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
    df["DESVIO"]         = (df["LOTAÇÃO_OFICIAL"].fillna("") !=
                            df["LOTAÇÃO_VINCULADA"].fillna(""))
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
    sb1, sb2, sb3 = st.sidebar.columns([1, 2, 1])
    with sb2:
        st.image(LOGO_PATH, use_container_width=True)
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

<div style="
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(240,180,30,0.40);
    border-top: 3px solid {D};
    border-radius: 10px;
    padding: 10px 12px 8px;
    margin: 0 0 6px;
    text-align: center;
">
  <div style="font-family:'Lora',serif;font-size:.98rem;font-weight:700;
              color:white;letter-spacing:.04em;">
    · PROGRAD ·
  </div>
  <div style="font-size:.63rem;color:{D};margin-top:3px;
              letter-spacing:.05em;font-weight:500;">
    Coordenação de Avaliação e Educação
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Categoria & Sexo")
cat_sel  = st.sidebar.multiselect("Categoria",["DOCENTE","TÉCNICO"],
                                   default=["DOCENTE","TÉCNICO"])
sexo_sel = st.sidebar.multiselect("Sexo",
               sorted(df_raw["SEXO"].dropna().unique()),
               default=sorted(df_raw["SEXO"].dropna().unique()))

st.sidebar.markdown("---")
st.sidebar.markdown("Campus / Lotação")
campus_sel = st.sidebar.multiselect("Campus",
               sorted(df_raw["CAMPUS"].dropna().unique()),
               default=sorted(df_raw["CAMPUS"].dropna().unique()))

st.sidebar.markdown("---")
st.sidebar.markdown("Situação Funcional")
sit_sel = st.sidebar.multiselect("Situação",
               sorted(df_raw["SITUAÇÃO"].dropna().unique()),
               default=sorted(df_raw["SITUAÇÃO"].dropna().unique()))

st.sidebar.markdown("---")
st.sidebar.markdown("Qualificação")
tit_opts = [t for t in ORDEM_TIT if t in df_raw["TIT_GRUPO"].values]
tit_sel  = st.sidebar.multiselect("Titulação", tit_opts, default=tit_opts)
reg_sel  = st.sidebar.multiselect("Regime Jurídico",
               sorted(df_raw["REGIME_JURIDICO"].dropna().unique()),
               default=sorted(df_raw["REGIME_JURIDICO"].dropna().unique()))

st.sidebar.markdown("---")
st.sidebar.markdown("Carga & Ingresso")
carga_sel = st.sidebar.multiselect("Carga Horária",
               sorted(df_raw["CARGA_GRUPO"].dropna().unique()),
               default=sorted(df_raw["CARGA_GRUPO"].dropna().unique()))
ing_sel   = st.sidebar.multiselect("Ingresso",
               sorted(df_raw["INGRESSO_GRUPO"].dropna().unique()),
               default=sorted(df_raw["INGRESSO_GRUPO"].dropna().unique()))

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
pct_desv = round(desvios / max(total,1) * 100, 1)
score    = sum(len(df_f[df_f["TIT_GRUPO"]==n])*p for n,p in PESOS_TIT.items())
idx_qual = round(score / max(total,1), 2)
nivel    = ("MUITO ALTA" if idx_qual>=4 else "ALTA" if idx_qual>=3
            else "MODERADA" if idx_qual>=2 else "BAIXA")
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
# HEADER PRINCIPAL
# -----------------------------------------------------------------
# Estrutura: CSS injeta o gradiente de fundo via classe .uft-header
# Layout:    st.columns([1,7,2]) — logo | título | badge
# Logo:      st.image() carrega o arquivo direto (sem base64)
# Título:    st.markdown() com HTML simples (sem imagens)
#
# Para mudar as cores do fundo, edite H_TOPO e H_BASE abaixo.
# Para mudar o título, edite a string dentro de st.markdown().
# =================================================================

H_TOPO  = "#EDF4FF"   # azul UFT muito claro (deriva de #003C78)
H_BASE  = "#FFFBF0"   # creme dourado muito claro (deriva de #F0B41E)
H_BORDA = "#C8DDF5"   # borda azul suave

# ── Injeta CSS que estiliza apenas o bloco de colunas do header ──
# O div invisível .uft-header-anchor serve de marcador;
# o CSS ~ seleciona o próximo stHorizontalBlock.
st.markdown(f"""
<style>
/* Aplica o fundo gradiente SOMENTE nas colunas do header */
.uft-header-anchor + div [data-testid="stHorizontalBlock"] {{
    background  : linear-gradient(135deg, {H_TOPO} 0%, {H_BASE} 100%);
    border-radius : 14px;
    border        : 1px solid {H_BORDA};
    border-top    : 4px solid {D};
    padding       : 8px 20px;
    box-shadow    : 0 3px 14px rgba(0,60,120,.10);
    margin-bottom : 4px;
    align-items   : center !important;
}}
/* Faixa decorativa dourado → teal logo abaixo do header */
.uft-header-stripe {{
    height: 3px;
    background: linear-gradient(90deg, {D} 0%, {VD} 100%);
    border-radius: 0 0 6px 6px;
    margin-bottom: 16px;
}}
</style>
<div class="uft-header-anchor" style="display:none;"></div>
""", unsafe_allow_html=True)

# ── Colunas do header: [logo | título | badge] ───────────────
col_logo, col_titulo, col_badge = st.columns([1, 7, 2])

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
    st.markdown(f"""
<div style="padding:6px 0 4px;">
  <div style="font-family:'Lora',serif;font-size:1.4rem;
              font-weight:700;color:{P};letter-spacing:.01em;">
    Painel Docentes e Técnicos
  </div>
  <div style="font-size:.82rem;color:{VD};margin-top:4px;font-weight:500;">
    Universidade Federal do Tocantins · Gestão Estratégica de Pessoas
  </div>
</div>
""", unsafe_allow_html=True)

with col_badge:
    st.markdown(f"""
<div style="background:{P};color:white;padding:7px 14px;border-radius:17px;
            font-size:.74rem;font-weight:700;letter-spacing:.04em;
            text-align:center;margin-top:10px;">
  📊 {total:,} registros
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
    + kpi("⭐", f"{idx_qual}/5.0","Qualificação",  VD, nivel)
    + kpi("🎂", idade_s,           "Idade Média",   A)
    + kpi("⚠️", f"{pct_desv}%",   "Desvio Lot.",   AL, f"{desvios:,} serv.")
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

    sec("📊 Índice Médio de Qualificação")
    fig_g = go.Figure(go.Indicator(
        mode="gauge+number+delta",value=idx_qual,
        delta={"reference":3.0,"increasing":{"color":VD},"decreasing":{"color":AL}},
        number={"suffix":" / 5.0","font":{"size":40,"color":P}},
        title={"text":f"Índice Médio · Ref. 3,0 · Nível: <b>{nivel}</b>","font":{"size":14}},
        gauge={"axis":{"range":[0,5],"tickwidth":1,"tickcolor":P},
               "bar":{"color":P,"thickness":0.25},"bgcolor":"white",
               "borderwidth":2,"bordercolor":BD,
               "steps":[{"range":[0,1],"color":"#F0F4FA"},{"range":[1,2],"color":"#C5D9F0"},
                         {"range":[2,3],"color":"#5A9AD4"},{"range":[3,4],"color":"#1A5FA8"},
                         {"range":[4,5],"color":P}],
               "threshold":{"line":{"color":D,"width":4},"thickness":0.8,"value":idx_qual}},
    ))
    fig_g.update_layout(**BL,height=280)
    card(fig_g)

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
    sec("⚠️ Desvio de Lotação (Oficial ≠ Vinculada)")
    d1,d2 = st.columns([1,2])
    with d1:
        dv = pct(df_f["DESVIO"].map({True:"Com desvio",False:"Sem desvio"}),"Status")
        fig = px.pie(dv,names="Status",values="Qtd",hole=0.58,height=320,
                     color="Status",color_discrete_map={"Com desvio":AL,"Sem desvio":VD})
        fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
                          textposition="outside",textfont_size=12)
        fig.update_layout(**BL)
        card(fig)
    with d2:
        dc = (df_f[df_f["DESVIO"]].groupby("CAMPUS").size()
              .reset_index(name="Com Desvio")
              .merge(df_f.groupby("CAMPUS").size().reset_index(name="Total"),on="CAMPUS"))
        dc["% Desvio"] = (dc["Com Desvio"]/dc["Total"]*100).round(1)
        dc = dc.sort_values("% Desvio",ascending=True)
        fig = px.bar(dc,x="% Desvio",y="CAMPUS",orientation="h",
                     text="% Desvio",color="% Desvio",height=320,
                     color_continuous_scale=[[0,VD],[0.4,D],[1,AL]],
                     labels={"CAMPUS":"Campus","% Desvio":"% com Desvio"})
        fig.update_traces(texttemplate="%{text}%",textposition="outside",textfont_size=11)
        fig.update_layout(**BL,coloraxis_showscale=False,
                          xaxis=dict(range=[0,115],showgrid=True,gridcolor="#EEF2F8"))
        card(fig)

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
            lambda col: col.astype(str).str.upper().str.contains(busca.upper(),na=False)
        ).any(axis=1)
        df_exib = df_exib[mask]
        st.caption(f"🔎 {len(df_exib):,} resultado(s) para '{busca}'")

    st.dataframe(df_exib,use_container_width=True,height=440)
    c1,c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Baixar Base Filtrada (.csv)",
            data=(df_f.drop(columns=["DT_NASC","DESVIO","FAIXA"],errors="ignore")
                      .to_csv(index=False).encode("utf-8")),
            file_name="base_filtrada_uft.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.info(f"📁 `perfil.xlsx` · {total:,} registros filtrados")
