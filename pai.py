# ============================================================
# PAINEL ANALÍTICO INSTITUCIONAL — UFT
# Universidade Federal do Tocantins
# Versão FINAL — baseada nos dados reais do perfil.xlsx
# 5.987 registros: 1.533 técnicos + 4.454 docentes
# ============================================================
#
# COMO EXECUTAR:
#   pip install streamlit pandas plotly openpyxl
#   perfil.xlsx (ou ajuste ARQUIVO abaixo)
#   streamlit run painel_uft.py
# ============================================================

import asyncio, sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PÁGINA
# ============================================================
st.set_page_config(
    page_title="PROGRAD · UFT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PALETA
# ============================================================
P   = "#0D2B4E"
S   = "#1A4A7A"
A   = "#1E6FBF"
D   = "#C8A84B"
FG  = "#F4F6F9"
BD  = "#DDE3EC"
TL  = "#6B7A99"
AL  = "#D95F2B"
OK  = "#1B7A4A"

ESC_AZUL = [[0,"#EBF3FB"],[0.25,"#9DC3E6"],[0.55,"#2F6FAC"],[0.8,"#0D4C8B"],[1,"#0A2E5C"]]
ESC_OURO = [[0,"#FDF6E3"],[0.3,"#F0D080"],[0.65,"#C8A84B"],[1,"#6B4F0A"]]
ESC_VERDE= [[0,"#E8F8F0"],[0.5,"#52BE80"],[1,"#1B7A4A"]]
CATS     = [P, D, A, OK, AL, "#8E44AD","#C0392B","#2980B9","#16A085","#D35400"]

BL = dict(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="DM Sans, sans-serif", color=P),
    margin=dict(t=28, b=16, l=8, r=8),
)

# ============================================================
# CSS
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');
html,body{{font-family:'DM Sans',sans-serif;color:{P};}}
.main{{background:{FG};padding-top:.3rem;}}
[data-testid="stSidebar"]{{background:linear-gradient(175deg,{P} 0%,{S} 100%);}}
[data-testid="stSidebar"] *{{color:white!important;}}
[data-testid="stSidebar"] label{{font-size:.7rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;opacity:.8;}}
[data-testid="stSidebar"] p{{font-size:.65rem;opacity:.45;letter-spacing:.1em;text-transform:uppercase;margin:0;}}
.krow{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;}}
.kc{{background:white;border:1px solid {BD};border-radius:12px;padding:13px 12px 9px;flex:1;min-width:140px;position:relative;}}
.kc-bar{{position:absolute;top:0;left:0;right:0;height:3px;border-radius:12px 12px 0 0;}}
.kc-ico{{font-size:1.15rem;margin-bottom:2px;}}
.kc-val{{font-family:'Lora',serif;font-size:1.6rem;font-weight:700;color:{P};line-height:1.1;}}
.kc-lbl{{font-size:.63rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:{TL};}}
.kc-sub{{font-size:.61rem;color:{TL};margin-top:1px;}}
.card{{background:white;border:1px solid {BD};border-radius:12px;padding:15px 15px 5px;
       box-shadow:0 1px 6px rgba(13,43,78,.05);margin-bottom:11px;}}
.sec{{font-family:'Lora',serif;font-size:.93rem;font-weight:700;color:{P};
      padding-bottom:5px;border-bottom:2px solid {D};margin:18px 0 11px;}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS UI
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
ARQUIVO = "perfil.xlsx"        # renomeie teste.xlsx → perfil.xlsx
ARQUIVO_ALT = "teste.xlsx"     # fallback automático

# Agrupamento de titulação (12 → 7)
TIT_GRUPO = {
    "DOUTORADO":                             "Doutorado",
    "PÓS DOUTORADO":                         "Pós-Doutorado",
    "MESTRADO":                              "Mestrado",
    "ESPECIALIZAÇÃO":                        "Especialização",
    "APERFEIÇOAMENTO":                       "Especialização",
    "PÓS GRADUADO":                          "Especialização",
    "GRADUAÇÃO":                             "Graduação",
    "2 GRAU COMPLETO OU TÉCNICO":            "Médio/Técnico",
    "1 GRAU COMPLETO - ATÉ 8 SÉRIE COMPLETO":"Fundamental",
    "1 GRAU INCOMPLETO ATÉ 4 SÉRIE INCOMPLETA":"Fundamental",
    "ANALFABETO":                            "Fundamental",
    "ESCOLARIDADE/TITULAÇÃO INDEFINIDA":     "Não informado",
}
ORDEM_TIT  = ["Pós-Doutorado","Doutorado","Mestrado","Especialização",
               "Graduação","Médio/Técnico","Fundamental","Não informado"]
PESOS_TIT  = {"Pós-Doutorado":5,"Doutorado":4,"Mestrado":3,
               "Especialização":2,"Graduação":1,"Médio/Técnico":0,
               "Fundamental":0,"Não informado":0}

# Agrupamento de ingresso
def grupo_ingresso(v):
    v = str(v).upper()
    if "CONCURSO" in v:                return "Concurso Público"
    if "CONTRAT" in v:                 return "Contratação Direta"
    if "CONVIDADO" in v:               return "Convidado"
    if "BOLSISTA" in v or "PROFESSOR BOLSISTA" in v: return "Bolsista"
    if "REDISTRIBUIÇÃO" in v or "REDISTRIB" in v: return "Redistribuição"
    if "VOLUNTÁRIO" in v or "VOLUNTARIO" in v: return "Voluntário"
    return "Outros"

# Extração de campus
CAMPUS_KEYS = [
    ("palmas",         "Palmas"),
    ("araguaína",      "Araguaína"), ("araguaina","Araguaína"),
    ("porto nacional", "Porto Nacional"),
    ("gurupi",         "Gurupi"),
    ("arraias",        "Arraias"),
    ("tocantinópolis", "Tocantinópolis"),("tocantinopolis","Tocantinópolis"),
    ("miracema",       "Miracema"),
    ("reitoria",       "Reitoria"),
    ("universidade federal do tocantins","UFT – Geral"),
]
def extrai_campus(s):
    if pd.isna(s) or str(s).strip() == "": return "Não informado"
    sl = str(s).lower()
    for kw, nm in CAMPUS_KEYS:
        if kw in sl: return nm
    return "Outras Unidades"

# Agrupamento de carga horária
def grupo_carga(v):
    v = str(v).upper().strip()
    if v in ("40 HORAS",): return "40 h"
    if v == "DEDICAÇÃO EXCLUSIVA": return "D.E."
    if v in ("20 HORAS",): return "20 h"
    if v in ("30 HORAS","25 HORAS","24 HORAS","12 HORAS"): return "Parcial"
    return "Convidado/Bolsista/Vol."

FAIXAS    = [(0,30,"Até 30"),(31,40,"31–40"),(41,50,"41–50"),(51,60,"51–60"),(61,999,"61+")]
ORD_FXAS  = [f[2] for f in FAIXAS]
COLUNAS_SENSIVEIS = ["CPF","CPF_SERVIDOR","RG","DOCUMENTO","NOME"]

# ============================================================
# CARREGAMENTO (com cache)
# ============================================================
@st.cache_data(show_spinner="📂 Carregando dados…")
def carrega():
    # Tenta nome de produção, depois fallback
    import os
    arq = ARQUIVO if os.path.exists(ARQUIVO) else ARQUIVO_ALT

    tec = pd.read_excel(arq, sheet_name="técnico", dtype=str)
    doc = pd.read_excel(arq, sheet_name="docente", dtype=str)
    tec["CATEGORIA"] = "TÉCNICO"
    doc["CATEGORIA"] = "DOCENTE"
    df = pd.concat([tec, doc], ignore_index=True)

    # Remove colunas sensíveis se existirem
    df.drop(columns=[c for c in COLUNAS_SENSIVEIS if c in df.columns],
            errors="ignore", inplace=True)

    # Strip em todas as strings
    for c in df.select_dtypes(include=["object","string"]).columns:
        df[c] = df[c].str.strip()

    # --- Datas e Idade ---
    df["DT_NASC"] = pd.to_datetime(df["DT_NASC"], dayfirst=True, errors="coerce")
    hoje = pd.Timestamp.today()
    df["IDADE"] = ((hoje - df["DT_NASC"]).dt.days / 365.25).round(1)
    # Invalida idades impossíveis (> 100 anos ou < 14)
    df.loc[(df["IDADE"] > 100) | (df["IDADE"] < 14), "IDADE"] = np.nan

    # --- Faixa etária ---
    conds  = [(df["IDADE"] >= lo) & (df["IDADE"] <= hi) for lo,hi,_ in FAIXAS]
    labels = [r for *_,r in FAIXAS]
    df["FAIXA"] = np.select(conds, labels, default="Não inf.")

    # --- Titulação normalizada → grupo ---
    tit_up = df["TITULAÇÃO"].str.upper().str.strip().fillna("ESCOLARIDADE/TITULAÇÃO INDEFINIDA")
    df["TIT_GRUPO"] = tit_up.map(TIT_GRUPO).fillna("Não informado")
    df["TIT_GRUPO"] = pd.Categorical(df["TIT_GRUPO"], categories=ORDEM_TIT, ordered=True)

    # --- Campus ---
    df["CAMPUS"] = df["LOTAÇÃO_OFICIAL"].apply(extrai_campus)

    # --- Ingresso agrupado ---
    df["INGRESSO_GRUPO"] = df["INGRESSO"].apply(grupo_ingresso)

    # --- Carga agrupada ---
    df["CARGA_GRUPO"] = df["CARGA"].apply(grupo_carga)

    # --- Desvio: OFICIAL ≠ VINCULADA ---
    lot_of = df["LOTAÇÃO_OFICIAL"].fillna("")
    lot_vi = df["LOTAÇÃO_VINCULADA"].fillna("")
    df["DESVIO"] = lot_of != lot_vi

    return df, arq

# ---- Carrega ----
try:
    df, arquivo_usado = carrega()
except FileNotFoundError:
    st.error(f"❌ Arquivo **{ARQUIVO}** (ou **{ARQUIVO_ALT}**) não encontrado.\n\n"
             "Coloque o arquivo na mesma pasta do script.")
    st.stop()
except Exception as e:
    st.error(f"Erro ao carregar: {e}")
    st.stop()

# ============================================================
# SIDEBAR — FILTROS
# ============================================================
st.sidebar.markdown(f"""
<div style="padding:.5rem 0 .3rem">
  <div style="font-family:'Lora',serif;font-size:1.1rem;font-weight:700;">🎓 UFT · PROGRAD</div>
  <div style="font-size:.68rem;opacity:.55;margin-top:.1rem;">Coordenação de Avaliação e Educação - CAE</div>
</div>
""", unsafe_allow_html=True)

# ─── Categoria & Sexo ────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("Categoria & Sexo")
cat_sel  = st.sidebar.multiselect("Categoria",
               ["DOCENTE","TÉCNICO"], default=["DOCENTE","TÉCNICO"])
sexo_sel = st.sidebar.multiselect("Sexo",
               sorted(df["SEXO"].dropna().unique()), default=sorted(df["SEXO"].dropna().unique()))

# ─── Campus ──────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("Campus / Lotação")
campus_opts = sorted(df["CAMPUS"].dropna().unique())
campus_sel  = st.sidebar.multiselect("Campus", campus_opts, default=campus_opts)

# ─── Situação ────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("Situação Funcional")
sit_opts = sorted(df["SITUAÇÃO"].dropna().unique())
sit_sel  = st.sidebar.multiselect("Situação", sit_opts, default=sit_opts)

# ─── Titulação ───────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("Qualificação")
tit_opts = [t for t in ORDEM_TIT if t in df["TIT_GRUPO"].values]
tit_sel  = st.sidebar.multiselect("Titulação", tit_opts, default=tit_opts)

# ─── Regime ──────────────────────────────────────────────────
reg_opts = sorted(df["REGIME_JURIDICO"].dropna().unique())
reg_sel  = st.sidebar.multiselect("Regime Jurídico", reg_opts, default=reg_opts)

# ─── Carga & Ingresso ────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("Carga & Ingresso")
carga_opts   = sorted(df["CARGA_GRUPO"].dropna().unique())
carga_sel    = st.sidebar.multiselect("Carga Horária", carga_opts, default=carga_opts)
ing_opts     = sorted(df["INGRESSO_GRUPO"].dropna().unique())
ingresso_sel = st.sidebar.multiselect("Forma de Ingresso", ing_opts, default=ing_opts)

# ============================================================
# APLICA FILTROS
# ============================================================
df_f = df[
    df["CATEGORIA"].isin(cat_sel) &
    df["SEXO"].isin(sexo_sel) &
    df["CAMPUS"].isin(campus_sel) &
    df["SITUAÇÃO"].isin(sit_sel) &
    df["TIT_GRUPO"].isin(tit_sel) &
    df["REGIME_JURIDICO"].isin(reg_sel) &
    df["CARGA_GRUPO"].isin(carga_sel) &
    df["INGRESSO_GRUPO"].isin(ingresso_sel)
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
dout_pdoc = df_f["TIT_GRUPO"].isin(["Doutorado","Pós-Doutorado"]).sum()
mestres   = (df_f["TIT_GRUPO"] == "Mestrado").sum()
ativos    = (df_f["SITUAÇÃO"].str.upper() == "ATIVO").sum()
desvios   = df_f["DESVIO"].sum()
pct_desv  = round(desvios / max(total,1) * 100, 1)
score     = sum(len(df_f[df_f["TIT_GRUPO"]==n])*p for n,p in PESOS_TIT.items())
idx_qual  = round(score / max(total,1), 2)
nivel     = ("MUITO ALTA" if idx_qual>=4 else "ALTA" if idx_qual>=3
             else "MODERADA" if idx_qual>=2 else "BAIXA")
idade_m   = df_f["IDADE"].mean()
idade_str = f"{idade_m:.1f} a" if not pd.isna(idade_m) else "—"

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div style="background:linear-gradient(130deg,{P} 0%,{S} 55%,{A} 100%);
    border-radius:14px;padding:22px 30px;margin-bottom:16px;
    display:flex;align-items:center;gap:16px;
    box-shadow:0 6px 26px rgba(13,43,78,.22);">
  <div style="font-size:2.4rem;">🎓</div>
  <div style="flex:1">
    <div style="font-family:'Lora',serif;font-size:1.4rem;font-weight:700;color:white;">
      Painel Docentes e Técnicos</div>
    <div style="font-size:.8rem;color:rgba(255,255,255,.62);margin-top:3px;">
     · Universidade Federal do Tocantins · </div>
  </div>
  <div style="background:rgba(200,168,75,.2);border:1px solid rgba(200,168,75,.5);
      color:{D};padding:5px 15px;border-radius:17px;font-size:.74rem;font-weight:700;">
    📊 {total:,} registros
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# KPI CARDS
# ============================================================
st.markdown(
    '<div class="krow">'
    + kpi("👥", f"{total:,}", "Total", P)
    + kpi("🏫", f"{docentes:,}", "Docentes", A, f"{docentes/max(total,1)*100:.1f}% do total")
    + kpi("🔧", f"{tecnicos:,}", "Técnicos", D, f"{tecnicos/max(total,1)*100:.1f}% do total")
    + kpi("✅", f"{ativos:,}", "Ativos", OK, f"{ativos/max(total,1)*100:.1f}% do total")
    + kpi("🎓", f"{dout_pdoc:,}", "Doutores/PD", D, f"{dout_pdoc/max(total,1)*100:.1f}% do total")
    + kpi("📚", f"{mestres:,}", "Mestres", A, f"{mestres/max(total,1)*100:.1f}% do total")
    + kpi("⭐", f"{idx_qual}/5.0", "Qualificação", OK, nivel)
    + kpi("🎂", idade_str, "Idade Média", A)
    + kpi("⚠️", f"{pct_desv}%", "Desvio Lotação", AL, f"{desvios:,} servidores")
    + '</div>',
    unsafe_allow_html=True
)

# ============================================================
# ABAS PRINCIPAIS
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎓 Qualificação",
    "🏢 Lotação & Campus",
    "⚖️ Regime & Situação",
    "📈 Perfil Etário",
    "⚠️ Desvio & Ingresso",
    "📄 Tabela & Download",
])

# ══════════════════════════════════════════════════════════════
# ABA 1 — QUALIFICAÇÃO
# ══════════════════════════════════════════════════════════════
with tab1:
    sec("🎓 Titulação por Categoria")
    c1, c2 = st.columns([3, 2])

    with c1:
        tg = (df_f.groupby(["TIT_GRUPO","CATEGORIA"])
              .size().reset_index(name="Qtd"))
        tg["TIT_GRUPO"] = pd.Categorical(tg["TIT_GRUPO"], categories=ORDEM_TIT, ordered=True)
        tg = tg.sort_values("TIT_GRUPO")
        fig = px.bar(
            tg, x="Qtd", y="TIT_GRUPO", color="CATEGORIA", orientation="h",
            barmode="stack", height=380,
            color_discrete_map={"DOCENTE": P, "TÉCNICO": D},
            labels={"TIT_GRUPO":"Titulação","Qtd":"Quantidade","CATEGORIA":"Categoria"},
            text_auto=True,
        )
        fig.update_layout(**BL, legend=dict(orientation="h", y=-0.18, font_size=12),
                          xaxis=dict(showgrid=True, gridcolor="#EEF2F8"))
        card(fig)

    with c2:
        sd = pct(df_f["SEXO"].map({"M":"Masculino","F":"Feminino"}).fillna(df_f["SEXO"]), "Sexo")
        fig = px.pie(sd, names="Sexo", values="Qtd", hole=0.58, height=380,
                     color_discrete_sequence=[P, D])
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
            textposition="outside", textfont_size=12)
        fig.update_layout(**BL)
        card(fig)

    sec("💼 Top Cargos")
    tc1, tc2 = st.columns(2)

    with tc1:
        st.caption("**Técnico-Administrativos**")
        ct = pct(df_f[df_f["CATEGORIA"]=="TÉCNICO"]["CARGO"], "Cargo")
        ct = ct.head(15)
        fig = px.bar(ct, x="Qtd", y="Cargo", orientation="h", text="Label",
                     color="Qtd", color_continuous_scale=ESC_OURO, height=480)
        fig.update_traces(textposition="outside", textfont_size=10)
        fig.update_layout(**BL, coloraxis_showscale=False,
                          xaxis=dict(showgrid=True, gridcolor="#F8F4EA",
                                     range=[0, ct["Qtd"].max()*1.35]))
        card(fig)

    with tc2:
        st.caption("**Docentes**")
        cd = pct(df_f[df_f["CATEGORIA"]=="DOCENTE"]["CARGO"], "Cargo")
        cd = cd.head(15)
        fig = px.bar(cd, x="Qtd", y="Cargo", orientation="h", text="Label",
                     color="Qtd", color_continuous_scale=ESC_AZUL, height=480)
        fig.update_traces(textposition="outside", textfont_size=10)
        fig.update_layout(**BL, coloraxis_showscale=False,
                          xaxis=dict(showgrid=True, gridcolor="#EEF2F8",
                                     range=[0, cd["Qtd"].max()*1.35]))
        card(fig)

    sec("📊 Índice Médio de Qualificação")
    fig_g = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=idx_qual,
        delta={"reference": 3.0, "increasing": {"color": OK}, "decreasing": {"color": AL}},
        number={"suffix": " / 5.0", "font": {"size": 40, "color": P}},
        title={"text": f"Índice Médio · Referência 3,0 · Nível: <b>{nivel}</b>",
               "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, 5], "tickwidth": 1, "tickcolor": P},
            "bar":  {"color": P, "thickness": 0.25},
            "bgcolor": "white", "borderwidth": 2, "bordercolor": BD,
            "steps": [
                {"range": [0, 1], "color": "#F0F4FA"},
                {"range": [1, 2], "color": "#C8D8EE"},
                {"range": [2, 3], "color": "#93B5D8"},
                {"range": [3, 4], "color": "#4A90D9"},
                {"range": [4, 5], "color": "#1A4A7A"},
            ],
            "threshold": {"line": {"color": D, "width": 4},
                          "thickness": 0.8, "value": idx_qual},
        },
    ))
    fig_g.update_layout(**BL, height=280)
    card(fig_g)

# ══════════════════════════════════════════════════════════════
# ABA 2 — LOTAÇÃO & CAMPUS
# ══════════════════════════════════════════════════════════════
with tab2:
    sec("🗺️ Distribuição por Campus")
    ca1, ca2 = st.columns(2)

    with ca1:
        cp = pct(df_f["CAMPUS"], "Campus")
        cp = cp.sort_values("Qtd", ascending=True)
        fig = px.bar(cp, x="Qtd", y="Campus", orientation="h", text="Label",
                     color="Qtd", color_continuous_scale=ESC_AZUL, height=420)
        fig.update_traces(textposition="outside", textfont_size=11)
        fig.update_layout(**BL, coloraxis_showscale=False,
                          xaxis=dict(showgrid=True, gridcolor="#EEF2F8",
                                     range=[0, cp["Qtd"].max()*1.32]))
        card(fig)

    with ca2:
        # Heatmap: Campus x Categoria
        heat = pd.crosstab(df_f["CAMPUS"], df_f["CATEGORIA"])
        fig  = px.imshow(heat, text_auto=True, aspect="auto",
                         color_continuous_scale=ESC_AZUL, height=420,
                         labels=dict(x="Categoria", y="Campus", color="Qtd"))
        fig.update_layout(**BL)
        card(fig)

    sec("🔥 Heatmap Campus × Titulação")
    heat2 = pd.crosstab(df_f["CAMPUS"], df_f["TIT_GRUPO"])
    # Reordena colunas pela ordem de titulação
    cols_ord = [c for c in ORDEM_TIT if c in heat2.columns]
    heat2 = heat2[cols_ord]
    fig = px.imshow(heat2, text_auto=True, aspect="auto",
                    color_continuous_scale=ESC_AZUL, height=460,
                    labels=dict(x="Titulação", y="Campus", color="Qtd"))
    fig.update_layout(**BL)
    card(fig)

    sec("🗂️ Lotação de Exercício — Top 20 Unidades")
    lex = df_f["LOTAÇÃO_EXERCÍCIO"].value_counts().head(20).reset_index()
    lex.columns = ["Unidade", "Qtd"]
    lex["%"] = (lex["Qtd"] / lex["Qtd"].sum() * 100).round(1)
    lex["Label"] = lex["Qtd"].astype(str) + " (" + lex["%"].astype(str) + "%)"
    lex = lex.sort_values("Qtd", ascending=True)
    fig = px.bar(lex, x="Qtd", y="Unidade", orientation="h", text="Label",
                 color="Qtd", color_continuous_scale=ESC_AZUL, height=580)
    fig.update_traces(textposition="outside", textfont_size=10)
    fig.update_layout(**BL, coloraxis_showscale=False,
                      xaxis=dict(showgrid=True, gridcolor="#EEF2F8",
                                 range=[0, lex["Qtd"].max()*1.3]),
                      yaxis=dict(tickfont_size=10))
    card(fig)

# ══════════════════════════════════════════════════════════════
# ABA 3 — REGIME & SITUAÇÃO
# ══════════════════════════════════════════════════════════════
with tab3:
    sec("⚖️ Regime Jurídico")
    r1, r2, r3 = st.columns(3)

    with r1:
        rg = pct(df_f["REGIME_JURIDICO"], "Regime")
        fig = px.pie(rg, names="Regime", values="Qtd", hole=0.54, height=360,
                     color_discrete_sequence=CATS)
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
            textposition="outside", textfont_size=10)
        fig.update_layout(**BL)
        card(fig)

    with r2:
        rcat = (df_f.groupby(["REGIME_JURIDICO","CATEGORIA"])
                .size().reset_index(name="Qtd"))
        fig  = px.bar(rcat, x="REGIME_JURIDICO", y="Qtd", color="CATEGORIA",
                      barmode="group", height=360,
                      color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                      text_auto=True,
                      labels={"REGIME_JURIDICO":"Regime","Qtd":"Qtd"})
        fig.update_layout(**BL, xaxis_tickangle=-30,
                          legend=dict(orientation="h",y=-0.3,font_size=11))
        card(fig)

    with r3:
        rtit = (df_f.groupby(["REGIME_JURIDICO","TIT_GRUPO"])
                .size().reset_index(name="Qtd"))
        rtit["TIT_GRUPO"] = pd.Categorical(rtit["TIT_GRUPO"],
                            categories=ORDEM_TIT, ordered=True)
        fig = px.bar(rtit, x="REGIME_JURIDICO", y="Qtd", color="TIT_GRUPO",
                     barmode="stack", height=360,
                     color_discrete_sequence=CATS,
                     text_auto=True,
                     labels={"REGIME_JURIDICO":"Regime","Qtd":"Qtd","TIT_GRUPO":"Titulação"})
        fig.update_layout(**BL, xaxis_tickangle=-30,
                          legend=dict(orientation="h",y=-0.3,font_size=10))
        card(fig)

    sec("✅ Situação Funcional")
    s1, s2 = st.columns([2, 3])

    with s1:
        sit = pct(df_f["SITUAÇÃO"], "Situação")
        fig = px.bar(sit.sort_values("Qtd"), x="Qtd", y="Situação",
                     orientation="h", text="Label",
                     color="Qtd", color_continuous_scale=ESC_AZUL, height=500)
        fig.update_traces(textposition="outside", textfont_size=10)
        fig.update_layout(**BL, coloraxis_showscale=False,
                          xaxis=dict(showgrid=True, gridcolor="#EEF2F8",
                                     range=[0, sit["Qtd"].max()*1.4]),
                          yaxis=dict(tickfont_size=10))
        card(fig)

    with s2:
        scat = (df_f.groupby(["SITUAÇÃO","CATEGORIA"])
                .size().reset_index(name="Qtd"))
        scat = scat.merge(sit[["Situação","Qtd"]].rename(
                    columns={"Situação":"SITUAÇÃO","Qtd":"Total"}), on="SITUAÇÃO")
        scat = scat.sort_values("Total", ascending=False)
        fig  = px.bar(scat, x="Qtd", y="SITUAÇÃO", color="CATEGORIA",
                      orientation="h", barmode="group", height=500,
                      color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                      text_auto=True,
                      labels={"SITUAÇÃO":"Situação","Qtd":"Qtd"})
        fig.update_layout(**BL, legend=dict(orientation="h",y=-0.1,font_size=12),
                          yaxis=dict(tickfont_size=10))
        card(fig)

# ══════════════════════════════════════════════════════════════
# ABA 4 — PERFIL ETÁRIO
# ══════════════════════════════════════════════════════════════
with tab4:
    df_id = df_f.dropna(subset=["IDADE"])

    sec("📈 Distribuição de Idades")
    e1, e2 = st.columns(2)

    with e1:
        fig = px.histogram(df_id, x="IDADE", nbins=25, color="CATEGORIA",
                           barmode="overlay", height=360, opacity=0.75,
                           color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                           marginal="rug",
                           labels={"IDADE":"Idade (anos)"})
        fig.update_layout(**BL, bargap=0.05,
                          legend=dict(orientation="h",y=-0.2,font_size=12),
                          xaxis=dict(showgrid=True, gridcolor="#EEF2F8"))
        card(fig)

    with e2:
        fig = px.box(df_id, x="CATEGORIA", y="IDADE", color="CATEGORIA",
                     points="outliers", height=360,
                     color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                     labels={"IDADE":"Idade","CATEGORIA":"Categoria"})
        fig.update_layout(**BL, showlegend=False)
        card(fig)

    sec("📊 Faixas Etárias")
    e3, e4 = st.columns(2)

    with e3:
        fx = (df_id["FAIXA"].value_counts()
              .reindex(ORD_FXAS).dropna().reset_index())
        fx.columns = ["Faixa","Qtd"]
        fx["%"] = (fx["Qtd"]/fx["Qtd"].sum()*100).round(1)
        fx["Label"] = fx["Qtd"].astype(str)+" ("+fx["%"].astype(str)+"%)"
        fig = px.bar(fx, x="Faixa", y="Qtd", text="Label",
                     color="Qtd", color_continuous_scale=ESC_AZUL, height=340)
        fig.update_traces(textposition="outside", textfont_size=12)
        fig.update_layout(**BL, coloraxis_showscale=False,
                          yaxis=dict(showgrid=True, gridcolor="#EEF2F8",
                                     range=[0, fx["Qtd"].max()*1.18]))
        card(fig)

    with e4:
        fxcat = (df_id.groupby(["FAIXA","CATEGORIA"])
                 .size().reset_index(name="Qtd"))
        fxcat["FAIXA"] = pd.Categorical(fxcat["FAIXA"],
                         categories=ORD_FXAS, ordered=True)
        fxcat = fxcat.sort_values("FAIXA")
        fig   = px.bar(fxcat, x="FAIXA", y="Qtd", color="CATEGORIA",
                       barmode="group", height=340,
                       color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                       text_auto=True,
                       labels={"FAIXA":"Faixa Etária","Qtd":"Quantidade"})
        fig.update_layout(**BL, legend=dict(orientation="h",y=-0.2,font_size=12))
        card(fig)

    sec("📋 Estatísticas Etárias por Categoria")
    stats = (df_id.groupby("CATEGORIA")["IDADE"]
             .agg(Contagem="count",Mínima="min",Mediana="median",Média="mean",Máxima="max")
             .round(1).reset_index())
    st.dataframe(stats, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# ABA 5 — DESVIO & INGRESSO
# ══════════════════════════════════════════════════════════════
with tab5:
    sec("⚠️ Desvio de Lotação (Oficial ≠ Vinculada)")
    d1, d2 = st.columns([1, 2])

    with d1:
        dv = pct(df_f["DESVIO"].map({True:"Com desvio",False:"Sem desvio"}), "Status")
        fig = px.pie(dv, names="Status", values="Qtd", hole=0.58, height=320,
                     color="Status",
                     color_discrete_map={"Com desvio":AL,"Sem desvio":OK})
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
            textposition="outside", textfont_size=12)
        fig.update_layout(**BL)
        card(fig)

    with d2:
        dcmp = (df_f[df_f["DESVIO"]].groupby("CAMPUS").size()
                .reset_index(name="Com Desvio")
                .merge(df_f.groupby("CAMPUS").size().reset_index(name="Total"),on="CAMPUS"))
        dcmp["% Desvio"] = (dcmp["Com Desvio"]/dcmp["Total"]*100).round(1)
        dcmp = dcmp.sort_values("% Desvio", ascending=True)
        fig  = px.bar(dcmp, x="% Desvio", y="CAMPUS", orientation="h",
                      text="% Desvio", color="% Desvio", height=320,
                      color_continuous_scale=[[0,OK],[0.4,"#F5C842"],[1,AL]],
                      labels={"CAMPUS":"Campus","% Desvio":"% com Desvio"})
        fig.update_traces(texttemplate="%{text}%", textposition="outside", textfont_size=11)
        fig.update_layout(**BL, coloraxis_showscale=False,
                          xaxis=dict(range=[0,115], showgrid=True, gridcolor="#EEF2F8"))
        card(fig)

    sec("🚪 Forma de Ingresso")
    i1, i2, i3 = st.columns(3)

    with i1:
        ig = pct(df_f["INGRESSO_GRUPO"], "Ingresso")
        fig = px.pie(ig, names="Ingresso", values="Qtd", hole=0.54, height=340,
                     color_discrete_sequence=CATS)
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
            textposition="outside", textfont_size=10)
        fig.update_layout(**BL)
        card(fig)

    with i2:
        igcat = (df_f.groupby(["INGRESSO_GRUPO","CATEGORIA"])
                 .size().reset_index(name="Qtd"))
        fig   = px.bar(igcat, x="INGRESSO_GRUPO", y="Qtd", color="CATEGORIA",
                       barmode="group", height=340,
                       color_discrete_map={"DOCENTE":P,"TÉCNICO":D},
                       text_auto=True,
                       labels={"INGRESSO_GRUPO":"Ingresso","Qtd":"Qtd"})
        fig.update_layout(**BL, xaxis_tickangle=-25,
                          legend=dict(orientation="h",y=-0.3,font_size=11))
        card(fig)

    with i3:
        chg = pct(df_f["CARGA_GRUPO"], "Carga")
        fig = px.pie(chg, names="Carga", values="Qtd", hole=0.54, height=340,
                     color_discrete_sequence=CATS)
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{value:,} (%{percent:.1%})",
            textposition="outside", textfont_size=10)
        fig.update_layout(**BL, title_text="Carga Horária",
                          title_font=dict(size=13,family="Lora,serif"))
        card(fig)

# ══════════════════════════════════════════════════════════════
# ABA 6 — TABELA & DOWNLOAD
# ══════════════════════════════════════════════════════════════
with tab6:
    sec("📄 Base Consolidada Filtrada")

    cb, ci = st.columns([3,1])
    with cb:
        busca = st.text_input("🔍 Buscar na tabela",
                              placeholder="Cargo, campus, situação, titulação…",
                              label_visibility="collapsed")
    with ci:
        st.metric("Registros filtrados", f"{total:,}")

    EXIB = ["CATEGORIA","SEXO","CARGO","TIT_GRUPO","CARGA_GRUPO",
            "CAMPUS","LOTAÇÃO_EXERCÍCIO","SITUAÇÃO","REGIME_JURIDICO",
            "INGRESSO_GRUPO","IDADE","DESVIO"]
    df_exib = df_f[[c for c in EXIB if c in df_f.columns]].copy()
    df_exib.columns = df_exib.columns.str.replace("_GRUPO","").str.replace("_"," ")

    if busca:
        mask = df_exib.apply(
            lambda col: col.astype(str).str.upper().str.contains(busca.upper(), na=False)
        ).any(axis=1)
        df_exib = df_exib[mask]
        st.caption(f"🔎 {len(df_exib):,} resultado(s) para '{busca}'")

    st.dataframe(df_exib, use_container_width=True, height=440)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            "⬇️ Baixar Base Filtrada (.csv)",
            data=df_f.drop(columns=["DT_NASC","DESVIO","FAIXA"], errors="ignore")
                      .to_csv(index=False).encode("utf-8"),
            file_name="base_filtrada_uft.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_d2:
        st.info(f"📁 Fonte: `{arquivo_usado}` · {total:,} registros após filtros")
