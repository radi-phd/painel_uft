"""Painéis da aba de qualificação, calculados sobre a base filtrada."""

from html import escape
from pathlib import Path


def _number(value):
    return f"{value:,}".replace(",", ".")


def _percent(value, total):
    return f"{(100 * value / total if total else 0):.1f}".replace(".", ",") + "%"


def _heading(icon, title, subtitle, badge=""):
    badge_html = f'<span class="q-badge">{escape(badge)}</span>' if badge else ""
    return (f'<div class="q-head"><div><div class="q-title"><span class="q-icon">{icon}</span>'
            f'{escape(title)}</div><div class="q-subtitle">{escape(subtitle)}</div>'
            f'</div>{badge_html}</div>')


def _bar(label, count, total, color):
    width = 100 * count / total if total else 0
    return (f'<div class="q-bar-row"><div class="q-bar-label"><span><i class="q-swatch" '
            f'style="background:{color}"></i>{escape(label)}</span><span class="q-bar-value">'
            f'{_number(count)} <span>({_percent(count, total)})</span></span></div>'
            f'<div class="q-track"><div class="q-fill" style="width:{width:.4f}%;'
            f'background:{color}"></div></div></div>')


def _summary_table(df, campuses, colors, icon):
    """Consolida as mesmas categorias exibidas nos indicadores da aba."""
    locations = df["CAMPUS"].fillna("Não informado").astype(str).str.strip()
    locations = locations.mask(locations == "", "Não informado")
    remaining = sorted(set(locations) - set(campuses))

    def metrics(group):
        category = group["CATEGORIA"]
        titles = group["TIT_GRUPO"]
        return [int((category == "DOCENTE").sum()),
                int((category == "TÉCNICO").sum()),
                int(titles.isin(["Doutorado", "Pós-Doutorado"]).sum()),
                int((titles == "Mestrado").sum()),
                int(((category == "DOCENTE") & (group["CARGA_GRUPO"] == "D.E.")).sum()),
                len(group)]

    def row(label, group, color):
        cells = "".join(f'<td>{_number(value)}</td>' for value in metrics(group))
        return (f'<tr><th scope="row" class="q-row-name"><span class="q-row-dot" '
                f'style="background:{color}"></span>{escape(label)}</th>{cells}</tr>')

    rows = [row(name, df[locations == name], color) for name, color in zip(campuses, colors)]
    rows.extend(row(name, df[locations == name], "#94a3b8") for name in remaining)
    totals = "".join(f'<td>{_number(value)}</td>' for value in metrics(df))
    header = _heading(icon, "Resumo Sintético por Campus & Titulação",
                      "Consolidado institucional conforme os filtros selecionados")
    return (f'<section class="q-card q-summary">{header}<div class="q-table-wrap">'
            '<table class="q-table"><thead><tr><th scope="col">Campus / unidade</th>'
            '<th scope="col">Docentes</th><th scope="col">Técnicos (TAE)</th>'
            '<th scope="col">Doutores</th><th scope="col">Mestres</th>'
            '<th scope="col">Dedicação exclusiva docente</th><th scope="col">Total servidores</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody><tfoot><tr class="q-total-row">'
            f'<th scope="row">Total geral UFT</th>{totals}</tr></tfoot></table></div></section>')


def qualification_dashboard(df, iqcd_doc, icons):
    """Retorna HTML responsivo; todas as proporções usam os registros filtrados."""
    total = len(df)
    tit = df["TIT_GRUPO"].astype(str)
    tit_groups = [
        ("Doutorado / Pós-Doutorado", tit.isin(["Doutorado", "Pós-Doutorado"]).sum(), "#002b49"),
        ("Mestrado", (tit == "Mestrado").sum(), "#008566"),
        ("Especialização / Lato Sensu", (tit == "Especialização").sum(), "#f3a61e"),
        ("Graduação / Superior Completo", (tit == "Graduação").sum(), "#94a3b8"),
        ("Médio / Técnico", (tit == "Médio/Técnico").sum(), "#cbd5e1"),
        ("Fundamental", (tit == "Fundamental").sum(), "#a8b5c5"),
        ("Não informado", (tit == "Não informado").sum(), "#dbe3ec"),
    ]
    tit_bars = "".join(_bar(label, int(count), total, color)
                       for index, (label, count, color) in enumerate(tit_groups)
                       if index < 5 or count)
    stricto = int(tit_groups[0][1] + tit_groups[1][1])
    tit_card = ('<section class="q-card q-tit">' +
                _heading(icons["graduation"], "Titulação Máxima da Força de Trabalho",
                         "Distribuição entre docentes e técnicos administrativos", f"Total: {_number(total)}") +
                f'<div class="q-bars">{tit_bars}</div><div class="q-foot">'
                f'{_percent(stricto, total)} do quadro possui pós-graduação stricto sensu</div></section>')

    sex = df["SEXO"].fillna("").astype(str).str.strip().str.upper()
    men, women = int((sex == "M").sum()), int((sex == "F").sum())
    other = total - men - women
    sex_groups = [("Masculino", men, "#002b49"), ("Feminino", women, "#f3a61e")]
    if other:
        sex_groups.append(("Não informado / outros", other, "#94a3b8"))
    stops, offset = [], 0.0
    for _, count, color in sex_groups:
        end = offset + 100 * count / total if total else offset
        stops.append(f"{color} {offset:.4f}% {end:.4f}%")
        offset = end
    legend = "".join(
        f'<div class="q-legend-item"><i class="q-swatch" style="background:{color}"></i>'
        f'<div class="q-legend-text"><strong>{escape(label)}</strong><span>Docentes e técnicos</span></div>'
        f'<div class="q-legend-value"><strong>{_number(count)}</strong><span>{_percent(count, total)}</span></div></div>'
        for label, count, color in sex_groups)
    women_parts = []
    for cat, label in [("DOCENTE", "Docentes mulheres"), ("TÉCNICO", "Técnicas mulheres")]:
        group = df["CATEGORIA"] == cat
        group_total = int(group.sum())
        count = int((group & (sex == "F")).sum())
        proportion = _percent(count, group_total) if group_total else "—"
        women_parts.append(f'<div class="q-women-item"><span>{label}</span>'
                           f'<strong>{_number(count)} ({proportion})</strong></div>')
    sex_card = ('<section class="q-card q-sex">' +
                _heading(icons["people"], "Distribuição por Sexo / Gênero", "Composição da comunidade universitária") +
                f'<div class="q-gender-body"><div class="q-donut" role="img" '
                f'aria-label="Distribuição por sexo; valores detalhados na legenda" '
                f'style="background:conic-gradient({", ".join(stops)})">'
                f'<div class="q-donut-inner"><span>Total</span><strong>{_number(total)}</strong>'
                f'<small>FILTRADOS</small></div></div><div class="q-legend">{legend}</div></div>'
                f'<div class="q-women">{"".join(women_parts)}</div></section>')

    campuses = ["Palmas", "Araguaína", "Gurupi", "Porto Nacional", "Tocantinópolis", "Miracema", "Arraias", "Reitoria"]
    colors = ["#002b49", "#0369a1", "#008566", "#f3a61e", "#6366f1", "#f43f5e", "#64748b", "#a16207"]
    campus_counts = df["CAMPUS"].value_counts()
    campus_cards = []
    for name, color in zip(campuses, colors):
        count = int(campus_counts.get(name, 0))
        width = 100 * count / total if total else 0
        campus_cards.append(f'<div class="q-campus-item"><span class="q-campus-name">{name}</span>'
                            f'<strong class="q-campus-number">{_number(count)}</strong>'
                            f'<span class="q-small">{_percent(count, total)}</span>'
                            f'<div class="q-track"><div class="q-fill" style="width:{width:.4f}%;'
                            f'background:{color}"></div></div></div>')
    extra = total - sum(int(campus_counts.get(name, 0)) for name in campuses)
    extra_note = (f'{_number(extra)} {"registro" if extra == 1 else "registros"} em outras unidades ou sem câmpus identificado.'
                  if extra else 'Percentuais calculados sobre o quadro filtrado.')
    campus_card = ('<section class="q-card q-campus">' +
                   _heading(icons["building"], "Presença nos 7 Câmpus e na Reitoria",
                            "Lotação de servidores por unidade descentralizada") +
                   f'<div class="q-campus-grid">{"".join(campus_cards)}</div>'
                   f'<div class="q-foot">{extra_note}</div></section>')

    docs = df[df["CATEGORIA"] == "DOCENTE"]
    n_docs = len(docs)
    workloads = [("Dedicação Exclusiva (DE)", "D.E.", "#009e73"),
                 ("40 Horas Semanais", "40 h", "#0284c7"),
                 ("20 Horas Semanais", "20 h", "#94a3b8"),
                 ("Carga parcial", "Parcial", "#a8b5c5"),
                 ("Convênio / Bolsa / Voluntário", "Conv./Bol./Vol.", "#cbd5e1")]
    regime_bars = "".join(_bar(label, int((docs["CARGA_GRUPO"] == group).sum()), n_docs, color)
                          for index, (label, group, color) in enumerate(workloads)
                          if index < 3 or (docs["CARGA_GRUPO"] == group).any())
    iqcd_text = f'{iqcd_doc:.2f}'.replace(".", ",") + ' / 5,0' if iqcd_doc is not None else '—'
    regime_card = ('<section class="q-card q-regime">' +
                   _heading(icons["teacher"], "Regime de Trabalho Docente", "Distribuição entre docentes filtrados") +
                   (f'<div class="q-bars">{regime_bars}</div>' if n_docs else '<p class="q-small">Nenhum docente nos filtros selecionados.</p>') +
                   f'<div class="q-iqcd">{icons["star"]}<div><strong>Índice IQCD: {iqcd_text}</strong>'
                   '<span>Qualificação docente na escala de 0 a 5, com pesos por titulação.</span></div></div></section>')
    summary_card = _summary_table(df, campuses, colors, icons["building"])
    footer = ('<footer class="q-footer"><div class="q-footer-left">'
              '<strong>Universidade Federal do Tocantins</strong><span>Avenida NS 15, Quadra 109 Norte – '
              'Plano Diretor Norte, Palmas – TO, 77001-090</span></div>'
              '<div class="q-footer-right">Base de dados institucional</div></footer>')
    css = Path(__file__).with_name("qualification.css").read_text(encoding="utf-8")
    return f'<style>{css}</style><div class="q-grid">{tit_card}{sex_card}{campus_card}{regime_card}{summary_card}</div>{footer}'
