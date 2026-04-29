import re
from datetime import date
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    import pdfplumber
except Exception:
    pdfplumber = None

st.set_page_config(page_title="ImobInvest Pro", page_icon="🏢", layout="wide")

# ============================================================
# CSS - PAINEL PREMIUM
# ============================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.block-container {padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1540px;}
.main {background:#f6f8fc;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#061936 0%,#020817 100%);} 
[data-testid="stSidebar"] * {color:white!important;}

.logo {font-size:28px;font-weight:900;line-height:1;margin-bottom:2px;}
.logo-sub {font-size:11px;letter-spacing:2.6px;color:#93c5fd!important;margin-bottom:28px;}

.hero-premium {
    background:linear-gradient(135deg,#061936 0%,#123a75 55%,#2563eb 100%);
    border-radius:30px;
    padding:30px 34px;
    color:white;
    margin-bottom:22px;
    box-shadow:0 22px 50px rgba(15,23,42,.22);
}
.hero-row {display:flex;justify-content:space-between;align-items:flex-start;gap:20px;}
.hero-title {font-size:34px;font-weight:900;margin:0 0 8px 0;letter-spacing:-.5px;}
.hero-sub {color:#dbeafe;font-size:15px;margin:0;}
.hero-pill {background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:9px 14px;font-size:13px;font-weight:800;white-space:nowrap;}

.kpi-grid {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;margin-bottom:20px;}
.kpi-card {
    background:white;
    padding:21px 22px;
    border-radius:24px;
    border:1px solid #e5eaf3;
    box-shadow:0 14px 36px rgba(15,23,42,.075);
    min-height:142px;
    overflow:hidden;
}
.kpi-icon {width:38px;height:38px;border-radius:14px;background:#eef4ff;color:#2563eb;display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:12px;}
.kpi-label {font-size:11px;color:#64748b;font-weight:900;text-transform:uppercase;letter-spacing:.45px;margin-bottom:8px;}
.kpi-value {font-size:24px;font-weight:900;color:#071735;line-height:1.08;white-space:nowrap;letter-spacing:-.8px;}
.kpi-sub {font-size:12px;font-weight:800;margin-top:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.good {color:#059669!important;}
.mid {color:#d97706!important;}
.bad {color:#dc2626!important;}
.muted {color:#64748b!important;}

.panel-card {
    background:white;
    padding:24px;
    border-radius:26px;
    border:1px solid #e5eaf3;
    box-shadow:0 14px 36px rgba(15,23,42,.065);
    margin-bottom:20px;
}
.section-title {font-size:19px;font-weight:900;color:#0f172a;margin-bottom:14px;letter-spacing:-.2px;}
.metric-line {display:flex;justify-content:space-between;gap:14px;border-bottom:1px solid #edf2f7;padding:10px 0;font-size:14px;}
.metric-line span {color:#64748b;}
.metric-line b {color:#0f172a;text-align:right;}

.decision-box {border-radius:24px;padding:22px;color:white;background:linear-gradient(135deg,#047857,#10b981);box-shadow:0 14px 32px rgba(4,120,87,.22);}
.decision-box.midbox {background:linear-gradient(135deg,#b45309,#f59e0b);box-shadow:0 14px 32px rgba(180,83,9,.22);}
.decision-box.badbox {background:linear-gradient(135deg,#991b1b,#ef4444);box-shadow:0 14px 32px rgba(153,27,27,.22);}
.decision-title {font-size:22px;font-weight:900;margin-bottom:8px;}
.decision-text {font-size:14px;color:rgba(255,255,255,.92);line-height:1.45;}
.score-big {font-size:46px;font-weight:900;line-height:1;}

.applied-card {
    background:#ffffff;
    border:1px solid #dbe4f0;
    border-radius:24px;
    padding:20px 22px;
    box-shadow:0 12px 30px rgba(15,23,42,.07);
}
.applied-grid {display:grid;grid-template-columns:1.8fr .9fr .8fr .8fr 1fr 1fr;gap:16px;align-items:center;}
.applied-label {font-size:11px;text-transform:uppercase;color:#64748b;font-weight:900;letter-spacing:.4px;margin-bottom:5px;}
.applied-value {font-size:18px;color:#0f172a;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

.alert-clean {background:#eff6ff;border:1px solid #bfdbfe;color:#1e3a8a;padding:15px 18px;border-radius:18px;font-weight:700;}
.warning-clean {background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;padding:15px 18px;border-radius:18px;font-weight:700;}

.stButton > button {background:linear-gradient(90deg,#1d4ed8,#4f46e5);color:white;border:none;border-radius:14px;font-weight:900;padding:.68rem 1.2rem;}
.stButton > button:hover {color:white;background:linear-gradient(90deg,#1e40af,#3730a3);}
.stDownloadButton > button {background:linear-gradient(90deg,#0f766e,#059669);color:white;border:none;border-radius:14px;font-weight:900;padding:.68rem 1.2rem;}

@media (max-width: 1100px){
  .kpi-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  .applied-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  .hero-row {flex-direction:column;}
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# FORMATADORES
# ============================================================
def moeda(v) -> str:
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def moeda_compacta(v) -> str:
    try:
        v = float(v)
        if abs(v) >= 1_000_000:
            return f"R$ {v/1_000_000:.2f} mi".replace(".", ",")
        if abs(v) >= 1_000:
            return f"R$ {v/1_000:.0f} mil".replace(".", ",")
        return moeda(v)
    except Exception:
        return "R$ 0,00"


def pct(v) -> str:
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"


def num_br(v) -> float:
    txt = str(v).replace("R$", "").replace("m²", "").replace("m2", "").strip()
    txt = re.sub(r"[^0-9,\.]", "", txt)
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    elif txt.count(".") > 1:
        txt = txt.replace(".", "")
    try:
        return float(txt)
    except Exception:
        return 0.0


def ano_atual_base() -> date:
    return date(2026, 4, 1)


def meses_entre(base: date, alvo: date) -> int:
    return max(1, (alvo.year - base.year) * 12 + (alvo.month - base.month))

# ============================================================
# LEITURA E PARSER PDF
# ============================================================
def ler_pdf(uploaded_file) -> Tuple[str, List[str], List[Dict]]:
    texto = ""
    linhas = []
    paginas = []
    if pdfplumber is None:
        return texto, linhas, paginas

    with pdfplumber.open(uploaded_file) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            texto += "\n" + page_text
            page_lines = [l.strip() for l in page_text.splitlines() if l.strip()]
            table_lines = []
            try:
                tables = page.extract_tables() or []
                for table in tables:
                    for row in table:
                        linha = " | ".join([str(c).strip() for c in row if c not in [None, ""]])
                        if linha.strip():
                            table_lines.append(linha)
            except Exception:
                pass
            paginas.append({"page": idx, "text": page_text, "lines": page_lines, "table_lines": table_lines})
            linhas.extend(page_lines)
            linhas.extend(table_lines)
    return texto, linhas, paginas


def titulo_limpo(t: str) -> str:
    t = re.sub(r"\s+", " ", t or "").strip()
    t = t.replace("FARASE", "FASE")
    t = t.replace("AP TO BELO", "PORTO BELO")
    t = t.replace("TAMENTOS", "")
    return t.title()


def extrair_info_pagina_ap_towers(page_text: str) -> Dict:
    info = {"empreendimento": "AP Towers Porto Belo - Fase 01"}

    m = re.search(r"PR[ÉE]-LAN[ÇC]AMENTO\s+(.+?FASE\s*\d+)", page_text, flags=re.I)
    if m:
        raw = m.group(1)
        if "AP TOWERS" in raw.upper():
            info["empreendimento"] = "AP Towers Porto Belo - Fase 01"
        else:
            info["empreendimento"] = titulo_limpo(raw)

    m = re.search(r"TORRE\s*(\d+)\s*-\s*ENTREGA\s*EM\s*(\d{4})", page_text, flags=re.I)
    if m:
        info["torre"] = f"Torre {int(m.group(1)):02d}"
        info["torre_numero"] = int(m.group(1))
        info["entrega_ano"] = int(m.group(2))

    m = re.search(r"LOCALIZA[ÇC][ÃA]O\s*-\s*(.+)", page_text, flags=re.I)
    if m:
        info["localizacao"] = re.sub(r"\s+", " ", m.group(1)).strip()

    reforcos = re.findall(r"(\d{1,2})\s+REFOR[ÇC]OS", page_text, flags=re.I)
    if reforcos:
        info["qtd_reforcos_pre"] = int(reforcos[0])
        info["qtd_reforcos_pos"] = int(reforcos[1]) if len(reforcos) > 1 else 0
    return info


def extrair_areas_por_tipo(page_text: str) -> Dict[str, Dict]:
    areas = {}
    # Captura blocos finais tipo: TIPO 01\n1 Suíte +\n2 Dormitórios\n84,81m²
    pattern = re.compile(r"TIPO\s*(\d{2}).{0,90}?(\d{2,3}[,.]\d{2})\s*m[²2]", re.I | re.S)
    for tipo, area in pattern.findall(page_text):
        areas[tipo] = {
            "tipo": f"TIPO {tipo}",
            "area": num_br(area),
            "descricao_tipo": "1 Suíte + 2 Dormitórios",
        }
    return areas


def expandir_apartamentos(expr: str) -> List[str]:
    expr = expr.strip()
    resultado = []
    # exemplos: 1301 e 2401 | 602 ao 1302 | 601
    partes = re.split(r"\s+e\s+|\s*,\s*", expr)
    for parte in partes:
        parte = parte.strip()
        m = re.match(r"^(\d{3,4})\s+ao\s+(\d{3,4})$", parte)
        if m:
            ini, fim = m.group(1), m.group(2)
            suffix_ini = int(ini[-2:])
            suffix_fim = int(fim[-2:])
            andar_ini = int(ini[:-2])
            andar_fim = int(fim[:-2])
            if suffix_ini == suffix_fim and andar_fim >= andar_ini:
                for andar in range(andar_ini, andar_fim + 1):
                    resultado.append(f"{andar}{suffix_ini:02d}")
            else:
                resultado.extend([ini, fim])
        else:
            resultado.extend(re.findall(r"\d{3,4}", parte))
    return resultado


def linhas_comerciais_ap_towers(page_text: str, page_number: int) -> List[Dict]:
    page_info = extrair_info_pagina_ap_towers(page_text)
    areas_tipo = extrair_areas_por_tipo(page_text)
    rows = []

    rgx = re.compile(
        r"(?P<apts>(?:\d{3,4})(?:\s+(?:e|ao)\s+\d{3,4})?)\s+"
        r"R\$\s*(?P<entrada>[\d\.]+,\d{2})\s+"
        r"(?P<qtd>\d+)x\s+R\$\s*(?P<parcela>[\d\.]+,\d{2})\s+"
        r"R\$\s*(?P<ref_pre>[\d\.]+,\d{2})\s+"
        r"R\$\s*(?P<ref_pos>[\d\.]+,\d{2})\s+"
        r"R\$\s*(?P<total>[\d\.]+,\d{2})",
        flags=re.I,
    )

    for linha in page_text.splitlines():
        m = rgx.search(linha)
        if not m:
            continue
        unidades = expandir_apartamentos(m.group("apts"))
        for unidade in unidades:
            tipo_codigo = unidade[-2:]
            area_info = areas_tipo.get(tipo_codigo, {})
            rows.append({
                **page_info,
                "pagina": page_number,
                "unidade": unidade,
                "apartamento_grupo": m.group("apts"),
                "tipo": area_info.get("tipo", f"TIPO {tipo_codigo}"),
                "descricao_tipo": area_info.get("descricao_tipo", ""),
                "area": area_info.get("area", 0.0),
                "entrada": num_br(m.group("entrada")),
                "qtd_parcelas": int(m.group("qtd")),
                "valor_parcela": num_br(m.group("parcela")),
                "reforco_pre_valor": num_br(m.group("ref_pre")),
                "reforco_pos_valor": num_br(m.group("ref_pos")),
                "preco_total": num_br(m.group("total")),
                "parser": "AP Towers",
                "trecho": linha,
            })
    return rows


def parser_ap_towers(paginas: List[Dict]) -> List[Dict]:
    todos = []
    for p in paginas:
        todos.extend(linhas_comerciais_ap_towers(p["text"], p["page"]))
    return todos


def buscar_unidade_generico(texto: str, linhas: List[str], unidade: str) -> Optional[Dict]:
    todas = [l.strip() for l in texto.splitlines() if l.strip()] + linhas
    blocos = []
    for i, linha in enumerate(todas):
        if re.search(rf"\b{re.escape(str(unidade))}\b", linha):
            blocos.append(" ".join(todas[max(0, i - 2): min(len(todas), i + 3)]))
    if not blocos:
        return None
    bloco = " ".join(blocos)
    vals = [num_br(v) for v in re.findall(r"R\$\s*[\d\.]+,\d{2}", bloco)]
    areas = [num_br(a) for a in re.findall(r"(\d{2,3}[,.]\d{2})\s*m[²2]", bloco, flags=re.I)]
    return {
        "empreendimento": "Empreendimento identificado no PDF",
        "torre": "",
        "localizacao": "",
        "unidade": str(unidade),
        "tipo": "",
        "descricao_tipo": "",
        "area": areas[0] if areas else 0.0,
        "entrada": vals[0] if len(vals) > 0 else 0.0,
        "qtd_parcelas": 120,
        "valor_parcela": vals[1] if len(vals) > 1 else 0.0,
        "reforco_pre_valor": vals[2] if len(vals) > 2 else 0.0,
        "reforco_pos_valor": vals[3] if len(vals) > 3 else 0.0,
        "preco_total": max(vals) if vals else 0.0,
        "qtd_reforcos_pre": 0,
        "qtd_reforcos_pos": 0,
        "entrega_ano": 2029,
        "parser": "Genérico",
        "trecho": bloco,
    }


def buscar_unidade_pdf(texto: str, linhas: List[str], paginas: List[Dict], unidade: str) -> Optional[Dict]:
    unidade = str(unidade).strip()
    rows = parser_ap_towers(paginas)
    for r in rows:
        if str(r.get("unidade")) == unidade:
            return r
    return buscar_unidade_generico(texto, linhas, unidade)

# ============================================================
# FLUXO FINANCEIRO
# ============================================================
def cronograma_reforcos_ap_towers(d: Dict) -> List[Dict]:
    base = ano_atual_base()
    eventos = []
    entrega = int(d.get("entrega_ano") or 2029)

    qtd_pre = int(d.get("qtd_reforcos_pre") or 0)
    datas_pre = []
    for ano in [2026] + list(range(2027, entrega + 1)):
        meses = [7, 10] if ano == 2026 else [6, 10]
        for mes in meses:
            datas_pre.append(date(ano, mes, 1))
    datas_pre = datas_pre[:qtd_pre]

    for dt in datas_pre:
        eventos.append({"mes": meses_entre(base, dt), "valor": float(d.get("reforco_pre_valor", 0)), "tipo": "Reforço até entrega"})

    qtd_pos = int(d.get("qtd_reforcos_pos") or 0)
    datas_pos = []
    for ano in range(entrega + 1, entrega + 6):
        for mes in [6, 10]:
            datas_pos.append(date(ano, mes, 1))
    datas_pos = datas_pos[:qtd_pos]

    for dt in datas_pos:
        eventos.append({"mes": meses_entre(base, dt), "valor": float(d.get("reforco_pos_valor", 0)), "tipo": "Reforço pós-entrega"})
    return eventos


def criar_fluxo(d: Dict) -> pd.DataFrame:
    preco = float(d.get("preco_total", 0) or 0)
    entrada = float(d.get("entrada", 0) or 0)
    qtd_parcelas = int(d.get("qtd_parcelas", 120) or 120)
    parcela = float(d.get("valor_parcela", 0) or 0)
    entrega_ano = int(d.get("entrega_ano") or 2029)
    cub_mensal = (1 + float(d.get("cub_anual", 4.3) or 4.3) / 100) ** (1 / 12) - 1
    val_mensal = (1 + float(d.get("valorizacao_anual", 12) or 12) / 100) ** (1 / 12) - 1

    base = ano_atual_base()
    mes_entrega = meses_entre(base, date(entrega_ano, 12, 1))
    prazo_total = max(qtd_parcelas, mes_entrega + 48)

    eventos = cronograma_reforcos_ap_towers(d) if d.get("parser") == "AP Towers" else []
    eventos_por_mes = {}
    for e in eventos:
        eventos_por_mes[e["mes"]] = eventos_por_mes.get(e["mes"], 0.0) + e["valor"]

    investido = entrada
    rows = []
    for mes in range(1, prazo_total + 1):
        parcela_corrigida = parcela * ((1 + cub_mensal) ** mes) if mes <= qtd_parcelas else 0.0
        reforcos = eventos_por_mes.get(mes, 0.0)
        pagamento = parcela_corrigida + reforcos
        investido += pagamento
        valor_proj = preco * ((1 + val_mensal) ** mes)
        lucro = valor_proj - investido
        roi = lucro / investido * 100 if investido > 0 else 0
        rows.append({
            "Mês": mes,
            "Fase": "Até entrega" if mes <= mes_entrega else "Pós-entrega",
            "Parcela Corrigida": parcela_corrigida,
            "Reforços": reforcos,
            "Pagamento Mensal": pagamento,
            "Total Investido": investido,
            "Valor Projetado": valor_proj,
            "Lucro Bruto": lucro,
            "ROI %": roi,
        })
    return pd.DataFrame(rows)


def indicadores(d: Dict):
    df = criar_fluxo(d)
    area = float(d.get("area", 0) or 0)
    preco = float(d.get("preco_total", 0) or 0)
    valor_m2 = preco / area if area > 0 else 0.0
    entrega_ano = int(d.get("entrega_ano") or 2029)
    mes_entrega = meses_entre(ano_atual_base(), date(entrega_ano, 12, 1))
    linha_entrega = df[df["Mês"] == mes_entrega].iloc[0] if not df.empty else None
    linha_final = df.iloc[-1] if not df.empty else None
    if linha_entrega is None:
        return df, {}
    lucro_entrega = float(linha_entrega["Lucro Bruto"])
    roi_entrega = float(linha_entrega["ROI %"])
    score = calcular_score(d, valor_m2, roi_entrega, lucro_entrega)
    return df, {
        "valor_m2": valor_m2,
        "mes_entrega": mes_entrega,
        "valor_entrega": float(linha_entrega["Valor Projetado"]),
        "investido_entrega": float(linha_entrega["Total Investido"]),
        "lucro_entrega": lucro_entrega,
        "roi_entrega": roi_entrega,
        "valor_final": float(linha_final["Valor Projetado"]),
        "investido_final": float(linha_final["Total Investido"]),
        "lucro_final": float(linha_final["Lucro Bruto"]),
        "roi_final": float(linha_final["ROI %"]),
        "score": score,
    }


def calcular_score(d: Dict, valor_m2: float, roi_entrega: float, lucro_entrega: float) -> float:
    nota = 5.0
    if roi_entrega >= 80:
        nota += 2.0
    elif roi_entrega >= 50:
        nota += 1.5
    elif roi_entrega >= 30:
        nota += 1.0
    elif roi_entrega < 15:
        nota -= 1.0

    ref = float(d.get("valor_m2_ref", 17000) or 0)
    if ref > 0 and valor_m2 > 0:
        desconto = (ref - valor_m2) / ref
        if desconto >= 0.15:
            nota += 1.3
        elif desconto >= 0.05:
            nota += 0.7
        elif desconto < -0.05:
            nota -= 0.8

    if lucro_entrega > 0:
        nota += 0.4
    return max(0, min(10, nota))

# ============================================================
# GRÁFICOS ÚTEIS
# ============================================================
def fig_fluxo(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Mês"], y=df["Parcela Corrigida"], name="Parcelas"))
    fig.add_trace(go.Bar(x=df["Mês"], y=df["Reforços"], name="Reforços"))
    fig.update_layout(
        title="Fluxo de pagamentos extraído do PDF",
        barmode="stack",
        height=360,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=15, r=15, t=50, b=15),
        yaxis=dict(gridcolor="#e5e7eb"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def fig_patrimonio(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Valor Projetado"], mode="lines", name="Valor projetado", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Total Investido"], mode="lines", name="Total investido", line=dict(width=4)))
    fig.update_layout(
        title="Patrimônio projetado x capital aportado",
        height=360,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=15, r=15, t=50, b=15),
        yaxis=dict(gridcolor="#e5e7eb"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig

# ============================================================
# COMPONENTES VISUAIS
# ============================================================
def kpi_card(icon: str, label: str, value: str, sub: str, cls: str = "muted"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub {cls}">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_line(label: str, value: str):
    st.markdown(f'<div class="metric-line"><span>{label}</span><b>{value}</b></div>', unsafe_allow_html=True)


def decision_html(score: float, roi: float):
    if score >= 8:
        cls = "decision-box"
        titulo = "Oportunidade forte"
        texto = "Boa relação entre capital aportado, valorização projetada e fluxo de pagamento. Prioridade para análise de documentação e negociação."
    elif score >= 6:
        cls = "decision-box midbox"
        titulo = "Boa oportunidade, com validação"
        texto = "O negócio tem potencial, mas precisa confirmar liquidez, preço real de revenda e qualidade da construtora."
    else:
        cls = "decision-box badbox"
        titulo = "Cautela elevada"
        texto = "O retorno estimado pode não compensar prazo, risco ou fluxo exigido. Compare com outras unidades."
    st.markdown(
        f"""
        <div class="{cls}">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                <div>
                    <div class="decision-title">{titulo}</div>
                    <div class="decision-text">{texto}</div>
                </div>
                <div style="text-align:right;">
                    <div class="score-big">{score:.1f}</div>
                    <div style="font-size:12px;font-weight:900;opacity:.9;">SCORE / 10</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# ESTADO
# ============================================================
if "dados" not in st.session_state:
    st.session_state.dados = {
        "empreendimento": "Importe um PDF",
        "construtora": "",
        "localizacao": "",
        "torre": "",
        "unidade": "",
        "tipo": "",
        "descricao_tipo": "",
        "area": 0.0,
        "preco_total": 0.0,
        "entrada": 0.0,
        "qtd_parcelas": 120,
        "valor_parcela": 0.0,
        "reforco_pre_valor": 0.0,
        "reforco_pos_valor": 0.0,
        "qtd_reforcos_pre": 0,
        "qtd_reforcos_pos": 0,
        "entrega_ano": 2029,
        "cub_anual": 4.3,
        "valorizacao_anual": 12.0,
        "valor_m2_ref": 17000.0,
        "parser": "",
        "trecho": "",
    }

for key, default in [("pdf_texto", ""), ("pdf_linhas", []), ("pdf_paginas", []), ("ultimo_resultado", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

d = st.session_state.dados

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="logo">🏢 ImobInvest</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">ANÁLISE EXECUTIVA</div>', unsafe_allow_html=True)
    menu = st.radio("Menu", ["Importar PDF", "Painel Executivo", "Dados e Premissas", "Fluxo Detalhado", "Relatório"], label_visibility="collapsed")
    st.divider()
    st.caption("v3.0 painel premium + leitura por unidade.")

# ============================================================
# IMPORTAR PDF
# ============================================================
if menu == "Importar PDF":
    st.markdown(
        '<div class="hero-premium"><div class="hero-row"><div><h1 class="hero-title">Importar PDF da Construtora</h1><p class="hero-sub">Envie a tabela, digite a unidade e o app aplica automaticamente dados comerciais e fluxo.</p></div><div class="hero-pill">PDF → Unidade → Análise</div></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    arquivo = st.file_uploader("PDF da tabela de vendas", type=["pdf"])
    if arquivo:
        texto, linhas, paginas = ler_pdf(arquivo)
        st.session_state.pdf_texto = texto
        st.session_state.pdf_linhas = linhas
        st.session_state.pdf_paginas = paginas
        st.markdown('<div class="alert-clean">PDF carregado. Digite a unidade para aplicar automaticamente na análise.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2.5])
    with c1:
        unidade = st.text_input("Apartamento / unidade", value=str(d.get("unidade", "")), placeholder="Ex.: 2401")
        buscar = st.button("Buscar unidade")
    with c2:
        st.markdown('<div class="warning-clean">Este app já possui parser específico para AP Towers. Para outras construtoras, ele tenta leitura genérica e a estrutura permite adicionar novos parsers sem quebrar o painel.</div>', unsafe_allow_html=True)

    if buscar:
        if not st.session_state.pdf_paginas:
            st.error("Envie o PDF primeiro.")
        else:
            resultado = buscar_unidade_pdf(st.session_state.pdf_texto, st.session_state.pdf_linhas, st.session_state.pdf_paginas, unidade)
            if resultado:
                resultado.setdefault("valor_m2_ref", d.get("valor_m2_ref", 17000.0))
                resultado.setdefault("cub_anual", d.get("cub_anual", 4.3))
                resultado.setdefault("valorizacao_anual", d.get("valorizacao_anual", 12.0))
                st.session_state.dados.update(resultado)
                st.session_state.ultimo_resultado = resultado
                d = st.session_state.dados
            else:
                st.error("Não encontrei essa unidade na tabela do PDF.")

    if st.session_state.ultimo_resultado:
        r = st.session_state.ultimo_resultado
        st.markdown('<br><div class="section-title">Unidade aplicada na análise</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="applied-card">
                <div class="applied-grid">
                    <div><div class="applied-label">Empreendimento</div><div class="applied-value">{r.get('empreendimento','')}</div></div>
                    <div><div class="applied-label">Torre</div><div class="applied-value">{r.get('torre','')}</div></div>
                    <div><div class="applied-label">Unidade</div><div class="applied-value">{r.get('unidade','')}</div></div>
                    <div><div class="applied-label">Área</div><div class="applied-value">{float(r.get('area',0) or 0):.2f} m²</div></div>
                    <div><div class="applied-label">Entrada</div><div class="applied-value">{moeda(r.get('entrada',0))}</div></div>
                    <div><div class="applied-label">Total</div><div class="applied-value">{moeda(r.get('preco_total',0))}</div></div>
                </div>
                <div style="margin-top:12px;color:#64748b;font-size:13px;font-weight:700;">Parser usado: {r.get('parser','genérico')} | Linha: {r.get('trecho','')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Ver texto extraído do PDF"):
        st.text_area("Texto", st.session_state.pdf_texto, height=320)

# ============================================================
# CÁLCULOS
# ============================================================
df, ind = indicadores(d)

# ============================================================
# PAINEL EXECUTIVO
# ============================================================
if menu == "Painel Executivo":
    if float(d.get("preco_total", 0) or 0) <= 0:
        st.markdown('<div class="hero-premium"><h1 class="hero-title">Painel Executivo</h1><p class="hero-sub">Importe um PDF e busque a unidade para gerar a análise.</p></div>', unsafe_allow_html=True)
        st.warning("Nenhuma unidade aplicada ainda.")
    else:
        titulo = f"{d.get('empreendimento','')}"
        subtitulo = f"{d.get('torre','')} | Unidade {d.get('unidade','')} | Entrega {d.get('entrega_ano','')} | {d.get('localizacao','')}"
        st.markdown(
            f"""
            <div class="hero-premium">
                <div class="hero-row">
                    <div>
                        <h1 class="hero-title">Painel Executivo</h1>
                        <p class="hero-sub">{titulo}</p>
                        <p class="hero-sub" style="margin-top:4px;">{subtitulo}</p>
                    </div>
                    <div class="hero-pill">Atualizado pela tabela do PDF</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            kpi_card("🏷️", "Preço total", moeda_compacta(d.get("preco_total", 0)), "Valor da tabela", "mid")
        with c2:
            area_txt = f"Área {float(d.get('area',0) or 0):.2f} m²"
            kpi_card("📐", "Valor por m²", moeda_compacta(ind.get("valor_m2", 0)), area_txt, "good" if ind.get("valor_m2", 0) > 0 else "bad")
        with c3:
            kpi_card("💰", "Investido até entrega", moeda_compacta(ind.get("investido_entrega", 0)), f"Até {d.get('entrega_ano','')}", "mid")
        with c4:
            kpi_card("📈", "Lucro na entrega", moeda_compacta(ind.get("lucro_entrega", 0)), f"ROI {pct(ind.get('roi_entrega',0))}", "good" if ind.get("lucro_entrega", 0) > 0 else "bad")
        with c5:
            score_val = ind.get("score", 0)
            kpi_card("⭐", "Score", f"{score_val:.1f}/10", "Nota executiva", "good" if score_val >= 7 else "mid" if score_val >= 5 else "bad")
        st.markdown('</div>', unsafe_allow_html=True)

        left, right = st.columns([1.25, 1])
        with left:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(fig_patrimonio(df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.plotly_chart(fig_fluxo(df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Resumo do ativo</div>', unsafe_allow_html=True)
            metric_line("Empreendimento", str(d.get("empreendimento", "")))
            metric_line("Torre / unidade", f"{d.get('torre','')} / {d.get('unidade','')}")
            metric_line("Tipo", f"{d.get('tipo','')} - {d.get('descricao_tipo','')}")
            metric_line("Área privativa", f"{float(d.get('area',0) or 0):.2f} m²")
            metric_line("Preço total", moeda(d.get("preco_total", 0)))
            metric_line("Valor por m²", moeda(ind.get("valor_m2", 0)))
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Fluxo extraído</div>', unsafe_allow_html=True)
            metric_line("Entrada", moeda(d.get("entrada", 0)))
            metric_line("Parcelas", f"{int(d.get('qtd_parcelas',0) or 0)}x de {moeda(d.get('valor_parcela',0))}")
            metric_line("Reforços até entrega", f"{int(d.get('qtd_reforcos_pre',0) or 0)}x de {moeda(d.get('reforco_pre_valor',0))}")
            metric_line("Reforços pós-entrega", f"{int(d.get('qtd_reforcos_pos',0) or 0)}x de {moeda(d.get('reforco_pos_valor',0))}")
            metric_line("CUB simulado", pct(d.get("cub_anual", 0)))
            metric_line("Valorização simulada", pct(d.get("valorizacao_anual", 0)))
            st.markdown('</div>', unsafe_allow_html=True)
        with c3:
            decision_html(ind.get("score", 0), ind.get("roi_entrega", 0))
            st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Retorno projetado</div>', unsafe_allow_html=True)
            metric_line("Valor na entrega", moeda(ind.get("valor_entrega", 0)))
            metric_line("Investido na entrega", moeda(ind.get("investido_entrega", 0)))
            metric_line("Lucro bruto", moeda(ind.get("lucro_entrega", 0)))
            metric_line("ROI na entrega", pct(ind.get("roi_entrega", 0)))
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# DADOS E PREMISSAS
# ============================================================
elif menu == "Dados e Premissas":
    st.markdown('<div class="hero-premium"><h1 class="hero-title">Dados e Premissas</h1><p class="hero-sub">Ajuste os dados comerciais, CUB e valorização sem perder a unidade importada.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        d["empreendimento"] = st.text_input("Empreendimento", d.get("empreendimento", ""))
        d["torre"] = st.text_input("Torre", d.get("torre", ""))
        d["unidade"] = st.text_input("Unidade", d.get("unidade", ""))
        d["localizacao"] = st.text_input("Localização", d.get("localizacao", ""))
    with c2:
        d["area"] = st.number_input("Área m²", value=float(d.get("area", 0) or 0), step=0.01)
        d["preco_total"] = st.number_input("Preço total", value=float(d.get("preco_total", 0) or 0), step=10000.0)
        d["entrada"] = st.number_input("Entrada", value=float(d.get("entrada", 0) or 0), step=5000.0)
        d["valor_parcela"] = st.number_input("Valor da parcela", value=float(d.get("valor_parcela", 0) or 0), step=500.0)
    with c3:
        d["qtd_parcelas"] = st.number_input("Quantidade de parcelas", value=int(d.get("qtd_parcelas", 120) or 120), min_value=1)
        d["entrega_ano"] = st.number_input("Ano de entrega", value=int(d.get("entrega_ano", 2029) or 2029), min_value=2026)
        d["cub_anual"] = st.slider("CUB anual estimado", 0.0, 15.0, float(d.get("cub_anual", 4.3) or 4.3), 0.1)
        d["valorizacao_anual"] = st.slider("Valorização anual estimada", 0.0, 30.0, float(d.get("valorizacao_anual", 12) or 12), 0.5)
        d["valor_m2_ref"] = st.number_input("Valor m² referência", value=float(d.get("valor_m2_ref", 17000) or 17000), step=500.0)
    st.session_state.dados = d
    st.success("Premissas atualizadas.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# FLUXO DETALHADO
# ============================================================
elif menu == "Fluxo Detalhado":
    st.markdown('<div class="hero-premium"><h1 class="hero-title">Fluxo Detalhado</h1><p class="hero-sub">Tabela mensal com parcelas corrigidas, reforços, capital aportado e retorno projetado.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    if float(d.get("preco_total", 0) or 0) <= 0:
        st.warning("Importe uma unidade para gerar o fluxo.")
    else:
        st.plotly_chart(fig_fluxo(df), use_container_width=True)
        df_show = df.copy()
        for col in ["Parcela Corrigida", "Reforços", "Pagamento Mensal", "Total Investido", "Valor Projetado", "Lucro Bruto"]:
            df_show[col] = df_show[col].apply(moeda)
        df_show["ROI %"] = df_show["ROI %"].apply(pct)
        st.dataframe(df_show, use_container_width=True, height=520)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RELATÓRIO
# ============================================================
elif menu == "Relatório":
    st.markdown('<div class="hero-premium"><h1 class="hero-title">Relatório Executivo</h1><p class="hero-sub">Resumo pronto para análise de investimento.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    if float(d.get("preco_total", 0) or 0) <= 0:
        st.warning("Importe uma unidade primeiro.")
    else:
        relatorio = f"""
# Relatório Executivo Imobiliário

## Ativo

**Empreendimento:** {d.get('empreendimento','')}  
**Torre:** {d.get('torre','')}  
**Unidade:** {d.get('unidade','')}  
**Localização:** {d.get('localizacao','')}  
**Tipo:** {d.get('tipo','')} - {d.get('descricao_tipo','')}  
**Área:** {float(d.get('area',0) or 0):.2f} m²  

## Dados comerciais extraídos do PDF

**Preço total:** {moeda(d.get('preco_total',0))}  
**Entrada:** {moeda(d.get('entrada',0))}  
**Parcelas:** {int(d.get('qtd_parcelas',0) or 0)}x de {moeda(d.get('valor_parcela',0))}  
**Reforços até entrega:** {int(d.get('qtd_reforcos_pre',0) or 0)}x de {moeda(d.get('reforco_pre_valor',0))}  
**Reforços pós-entrega:** {int(d.get('qtd_reforcos_pos',0) or 0)}x de {moeda(d.get('reforco_pos_valor',0))}  
**Entrega:** {d.get('entrega_ano','')}  

## Indicadores

**Valor por m²:** {moeda(ind.get('valor_m2',0))}  
**Investido até entrega:** {moeda(ind.get('investido_entrega',0))}  
**Valor projetado na entrega:** {moeda(ind.get('valor_entrega',0))}  
**Lucro bruto na entrega:** {moeda(ind.get('lucro_entrega',0))}  
**ROI na entrega:** {pct(ind.get('roi_entrega',0))}  
**Score:** {ind.get('score',0):.1f}/10  

## Conclusão

A análise considera o fluxo extraído do PDF, correção mensal por CUB, valorização anual estimada e capital aportado até a entrega. Antes da decisão final, valide documentação, liquidez de revenda, qualidade da construtora e preço real praticado no mercado.
"""
        st.markdown(relatorio)
        st.download_button("Baixar relatório em Markdown", data=relatorio.encode("utf-8"), file_name="relatorio_imobiliario.md", mime="text/markdown")
    st.markdown('</div>', unsafe_allow_html=True)
