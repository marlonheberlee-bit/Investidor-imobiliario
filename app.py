import re
import json
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    from fpdf import FPDF
except Exception:
    FPDF = None

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
    padding:20px 18px;
    border-radius:24px;
    border:1px solid #e5eaf3;
    box-shadow:0 14px 36px rgba(15,23,42,.075);
    min-height:148px;
    overflow:hidden;
}
.kpi-icon {width:38px;height:38px;border-radius:14px;background:#eef4ff;color:#2563eb;display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:12px;}
.kpi-label {font-size:11px;color:#64748b;font-weight:900;text-transform:uppercase;letter-spacing:.45px;margin-bottom:8px;}
.kpi-value {font-size:18px;font-weight:900;color:#071735;line-height:1.15;white-space:nowrap;letter-spacing:-.8px;}
.kpi-sub {font-size:12px;font-weight:800;margin-top:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.executive-row {margin-top:4px;}
.chart-card {min-height:420px;}
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


.decision-box {
    margin-bottom: 18px !important;
}

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
    """Formata sempre com valor cheio, sem abreviar em mil/mi."""
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def moeda_card(v) -> str:
    # Mantém valores completos também nos cards do painel.
    return moeda(v)

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
    # Mapa fixo do AP Towers: o final da unidade define o tipo e a metragem.
    # Ex.: 2401 termina com 01 => TIPO 01 => 84,81 m².
    # Mantemos também a leitura por texto para outros PDFs parecidos.
    areas = {
        "01": {"tipo": "TIPO 01", "area": 84.81, "descricao_tipo": "1 Suíte + 2 Dormitórios"},
        "02": {"tipo": "TIPO 02", "area": 85.87, "descricao_tipo": "1 Suíte + 2 Dormitórios"},
        "03": {"tipo": "TIPO 03", "area": 83.50, "descricao_tipo": "1 Suíte + 2 Dormitórios"},
        "04": {"tipo": "TIPO 04", "area": 83.50, "descricao_tipo": "1 Suíte + 2 Dormitórios"},
        "05": {"tipo": "TIPO 05", "area": 85.87, "descricao_tipo": "1 Suíte + 2 Dormitórios"},
        "06": {"tipo": "TIPO 06", "area": 90.93, "descricao_tipo": "1 Suíte + 2 Dormitórios"},
    }

    pattern = re.compile(r"TIPO\s*(\d{2}).{0,90}?(\d{2,3}[,.]\d{2})\s*m[²2]", re.I | re.S)
    for tipo, area in pattern.findall(page_text):
        area_lida = num_br(area)
        if area_lida > 0:
            areas[tipo] = {
                "tipo": f"TIPO {tipo}",
                "area": area_lida,
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
                "area": area_info.get("area", {"01":84.81,"02":85.87,"03":83.50,"04":83.50,"05":85.87,"06":90.93}.get(tipo_codigo, 0.0)),
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

    if d.get("parser") == "AP Towers":
        eventos = cronograma_reforcos_ap_towers(d)
    else:
        eventos = []
        qtd_pre_manual = int(d.get("qtd_reforcos_pre", 0) or 0)
        qtd_pos_manual = int(d.get("qtd_reforcos_pos", 0) or 0)
        valor_pre_manual = float(d.get("reforco_pre_valor", 0) or 0)
        valor_pos_manual = float(d.get("reforco_pos_valor", 0) or 0)
        if qtd_pre_manual > 0 and valor_pre_manual > 0:
            intervalo_pre = max(1, mes_entrega // qtd_pre_manual)
            for i in range(1, qtd_pre_manual + 1):
                eventos.append({"mes": min(mes_entrega, i * intervalo_pre), "valor": valor_pre_manual, "tipo": "Reforço até entrega"})
        if qtd_pos_manual > 0 and valor_pos_manual > 0:
            intervalo_pos = max(1, 48 // qtd_pos_manual)
            for i in range(1, qtd_pos_manual + 1):
                eventos.append({"mes": mes_entrega + i * intervalo_pos, "valor": valor_pos_manual, "tipo": "Reforço pós-entrega"})
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
        rows.append({
            "Mês": mes,
            "Fase": "Até entrega" if mes <= mes_entrega else "Pós-entrega",
            "Parcela Corrigida": parcela_corrigida,
            "Reforços": reforcos,
            "Pagamento Mensal": pagamento,
            "Total Investido": investido,
            "Valor Projetado": valor_proj,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Cálculo corrigido do lucro:
    # Antes: valor de mercado - capital investido até a entrega.
    # Agora: valor de mercado - saldo devedor - capital investido.
    # Isso evita inflar o resultado quando ainda existe saldo a pagar.
    total_contrato_simulado = float(df["Total Investido"].iloc[-1])
    df["Saldo Devedor"] = (total_contrato_simulado - df["Total Investido"]).clip(lower=0)
    df["Lucro Bruto"] = df["Valor Projetado"] - df["Saldo Devedor"] - df["Total Investido"]
    df["ROI %"] = df.apply(
        lambda r: (r["Lucro Bruto"] / r["Total Investido"] * 100) if r["Total Investido"] > 0 else 0,
        axis=1,
    )
    return df


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

# ============================================================
# RELATÓRIO PDF E ANÁLISES SALVAS
# ============================================================
def texto_relatorio(d: Dict, ind: Dict) -> str:
    return f"""Relatório Executivo Imobiliário

Ativo
Empreendimento: {d.get('empreendimento','')}
Torre: {d.get('torre','')}
Unidade: {d.get('unidade','')}
Localização: {d.get('localizacao','')}
Tipo: {d.get('tipo','')} - {d.get('descricao_tipo','')}
Área: {float(d.get('area',0) or 0):.2f} m²

Dados Comerciais
Preço total: {moeda(d.get('preco_total',0))}
Entrada: {moeda(d.get('entrada',0))}
Parcelas: {int(d.get('qtd_parcelas',0) or 0)}x de {moeda(d.get('valor_parcela',0))}
Reforços até entrega: {int(d.get('qtd_reforcos_pre',0) or 0)}x de {moeda(d.get('reforco_pre_valor',0))}
Reforços pós-entrega: {int(d.get('qtd_reforcos_pos',0) or 0)}x de {moeda(d.get('reforco_pos_valor',0))}
Entrega: {d.get('entrega_ano','')}
CUB anual simulado: {pct(d.get('cub_anual',0))}
Valorização anual simulada: {pct(d.get('valorizacao_anual',0))}

Indicadores
Valor por m²: {moeda(ind.get('valor_m2',0))}
Investido até entrega: {moeda(ind.get('investido_entrega',0))}
Valor projetado na entrega: {moeda(ind.get('valor_entrega',0))}
Lucro bruto na entrega: {moeda(ind.get('lucro_entrega',0))}
ROI na entrega: {pct(ind.get('roi_entrega',0))}
Valor final projetado: {moeda(ind.get('valor_final',0))}
Investido final: {moeda(ind.get('investido_final',0))}
Lucro final: {moeda(ind.get('lucro_final',0))}
ROI final: {pct(ind.get('roi_final',0))}
Score: {ind.get('score',0):.1f}/10

Conclusão
Esta análise considera o fluxo de pagamento informado ou extraído do PDF, correção mensal por CUB, valorização anual estimada e capital aportado até a entrega. Antes da decisão final, valide documentação, liquidez de revenda, qualidade da construtora e preço real praticado no mercado.
"""


def _pdf_safe_text(texto: str) -> str:
    texto = str(texto or "")
    troca = {"–": "-", "—": "-", "“": "\"", "”": "\"", "‘": "'", "’": "'", "•": "-", "²": "2"}
    for a, b in troca.items():
        texto = texto.replace(a, b)
    return texto.encode("latin-1", "ignore").decode("latin-1")


def _quebrar_linha_pdf(texto: str, limite: int = 105) -> List[str]:
    texto = _pdf_safe_text(texto)
    if len(texto) <= limite:
        return [texto]
    partes = []
    atual = ""
    for palavra in texto.split(" "):
        if len(palavra) > limite:
            if atual:
                partes.append(atual)
                atual = ""
            for i in range(0, len(palavra), limite):
                partes.append(palavra[i:i + limite])
        elif len(atual) + len(palavra) + 1 <= limite:
            atual = (atual + " " + palavra).strip()
        else:
            partes.append(atual)
            atual = palavra
    if atual:
        partes.append(atual)
    return partes


def gerar_pdf_bytes(relatorio: str) -> Optional[bytes]:
    if FPDF is None:
        return None

    pdf = FPDF(format="A4")
    pdf.set_margins(14, 14, 14)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    pdf.set_fill_color(6, 25, 54)
    pdf.rect(0, 0, 210, 28, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(14, 8)
    pdf.cell(0, 8, "Relatorio Executivo Imobiliario", ln=True)

    pdf.set_text_color(15, 23, 42)
    pdf.set_y(36)
    titulos = {"Ativo", "Dados Comerciais", "Indicadores", "Conclusão", "Conclusao"}

    for linha in str(relatorio or "").splitlines():
        linha_original = linha.strip()
        if not linha_original:
            pdf.ln(3)
            continue

        if linha_original in titulos:
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(8, 26, 58)
            pdf.set_x(14)
            pdf.multi_cell(182, 7, _pdf_safe_text(linha_original), align="L")
            pdf.set_text_color(15, 23, 42)
            pdf.set_font("Helvetica", "", 10)
            continue

        pdf.set_font("Helvetica", "", 10)
        for parte in _quebrar_linha_pdf(linha_original, limite=105):
            pdf.set_x(14)
            pdf.multi_cell(182, 6, parte, align="L")

    out = pdf.output(dest="S")
    if isinstance(out, bytes):
        return out
    if isinstance(out, bytearray):
        return bytes(out)
    return str(out).encode("latin-1", "ignore")

def salvar_analise_atual(nome: str, d: Dict, ind: Dict):
    if 'analises_salvas' not in st.session_state:
        st.session_state.analises_salvas = []
    item = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
        'nome': nome,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'dados': dict(d),
        'indicadores': dict(ind),
    }
    st.session_state.analises_salvas.insert(0, item)


def render_inputs_proposta(d: Dict, prefixo: str = 'manual'):
    c1, c2, c3 = st.columns(3)
    with c1:
        d['empreendimento'] = st.text_input('Empreendimento', d.get('empreendimento', ''), key=f'{prefixo}_empreendimento')
        d['torre'] = st.text_input('Torre', d.get('torre', ''), key=f'{prefixo}_torre')
        d['unidade'] = st.text_input('Unidade', d.get('unidade', ''), key=f'{prefixo}_unidade')
        d['localizacao'] = st.text_input('Localização', d.get('localizacao', ''), key=f'{prefixo}_localizacao')
    with c2:
        d['area'] = st.number_input('Área privativa m²', min_value=0.0, value=float(d.get('area', 0) or 0), step=0.01, key=f'{prefixo}_area')
        d['preco_total'] = st.number_input('Preço total', min_value=0.0, value=float(d.get('preco_total', 0) or 0), step=10000.0, key=f'{prefixo}_preco_total')
        d['entrada'] = st.number_input('Entrada / ato', min_value=0.0, value=float(d.get('entrada', 0) or 0), step=5000.0, key=f'{prefixo}_entrada')
        d['valor_parcela'] = st.number_input('Valor da parcela mensal', min_value=0.0, value=float(d.get('valor_parcela', 0) or 0), step=500.0, key=f'{prefixo}_valor_parcela')
    with c3:
        d['qtd_parcelas'] = st.number_input('Quantidade de parcelas mensais', min_value=1, value=int(d.get('qtd_parcelas', 120) or 120), step=1, key=f'{prefixo}_qtd_parcelas')
        d['entrega_ano'] = st.number_input('Ano de entrega', min_value=2026, value=int(d.get('entrega_ano', 2029) or 2029), step=1, key=f'{prefixo}_entrega_ano')
        d['valor_m2_ref'] = st.number_input('Valor m² de referência', min_value=0.0, value=float(d.get('valor_m2_ref', 17000) or 17000), step=500.0, key=f'{prefixo}_valor_m2_ref')
        d['parser'] = st.selectbox('Origem do fluxo', ['Manual / Proposta', 'AP Towers', 'Genérico'], index=0 if d.get('parser') not in ['AP Towers','Genérico'] else ['Manual / Proposta','AP Towers','Genérico'].index(d.get('parser')), key=f'{prefixo}_parser')

    st.markdown('### Reforços')
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        d['qtd_reforcos_pre'] = st.number_input('Qtd. reforços até entrega', min_value=0, value=int(d.get('qtd_reforcos_pre', 0) or 0), step=1, key=f'{prefixo}_qtd_ref_pre')
    with r2:
        d['reforco_pre_valor'] = st.number_input('Valor de cada reforço até entrega', min_value=0.0, value=float(d.get('reforco_pre_valor', 0) or 0), step=5000.0, key=f'{prefixo}_ref_pre_valor')
    with r3:
        d['qtd_reforcos_pos'] = st.number_input('Qtd. reforços pós-entrega', min_value=0, value=int(d.get('qtd_reforcos_pos', 0) or 0), step=1, key=f'{prefixo}_qtd_ref_pos')
    with r4:
        d['reforco_pos_valor'] = st.number_input('Valor de cada reforço pós-entrega', min_value=0.0, value=float(d.get('reforco_pos_valor', 0) or 0), step=5000.0, key=f'{prefixo}_ref_pos_valor')

    st.markdown('### Premissas para cenários')
    p1, p2 = st.columns(2)
    with p1:
        d['cub_anual'] = st.slider('CUB anual estimado', 0.0, 15.0, float(d.get('cub_anual', 4.3) or 4.3), 0.1, key=f'{prefixo}_cub')
    with p2:
        d['valorizacao_anual'] = st.slider('Valorização anual estimada', 0.0, 30.0, float(d.get('valorizacao_anual', 12) or 12), 0.5, key=f'{prefixo}_val')
    return d
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
if "analises_salvas" not in st.session_state:
    st.session_state.analises_salvas = []


d = st.session_state.dados

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="logo">🏢 ImobInvest</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">ANÁLISE EXECUTIVA</div>', unsafe_allow_html=True)
    menu = st.radio("Menu", ["Importar PDF", "Painel Executivo", "Proposta Manual", "Dados e Premissas", "Cenários", "Fluxo Detalhado", "Relatório", "Análises Salvas"], label_visibility="collapsed")
    st.divider()
    st.caption("v3.1 painel premium + proposta manual + relatórios salvos.")

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
        st.empty()

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
                    <div class="hero-pill">Análise da unidade aplicada</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            kpi_card("🏷️", "Preço total", moeda(d.get("preco_total", 0)), "Valor da tabela", "mid")
        with c2:
            area_txt = f"Área {float(d.get('area',0) or 0):.2f} m²"
            kpi_card("📐", "Valor por m²", moeda(ind.get("valor_m2", 0)), area_txt, "good" if ind.get("valor_m2", 0) > 0 else "bad")
        with c3:
            kpi_card("💰", "Investido até entrega", moeda(ind.get("investido_entrega", 0)), f"Até {d.get('entrega_ano','')}", "mid")
        with c4:
            kpi_card("📈", "Lucro na entrega", moeda(ind.get("lucro_entrega", 0)), f"ROI {pct(ind.get('roi_entrega',0))}", "good" if ind.get("lucro_entrega", 0) > 0 else "bad")
        with c5:
            score_val = ind.get("score", 0)
            kpi_card("⭐", "Score", f"{score_val:.1f}/10", "Nota executiva", "good" if score_val >= 7 else "mid" if score_val >= 5 else "bad")

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        # Faixa executiva horizontal: decisão + score
        decision_html(ind.get("score", 0), ind.get("roi_entrega", 0))

        def card_html(titulo, linhas):
            linhas_html = "".join(
                [f'<div class="metric-line"><span>{label}</span><b>{value}</b></div>' for label, value in linhas]
            )
            st.markdown(
                f'<div class="panel-card"><div class="section-title">{titulo}</div>{linhas_html}</div>',
                unsafe_allow_html=True,
            )

        score_val = ind.get("score", 0)
        if score_val >= 8:
            status = "Oportunidade forte"
            leitura = "Prioridade para análise documental, negociação e validação de liquidez."
        elif score_val >= 6:
            status = "Boa oportunidade"
            leitura = "Avançar com cautela, validando preço de revenda, prazo e força da construtora."
        else:
            status = "Cautela"
            leitura = "Comparar com outras unidades antes de assumir o fluxo."

        col_resumo, col_fluxo = st.columns(2)
        with col_resumo:
            card_html("Resumo do ativo", [
                ("Empreendimento", str(d.get("empreendimento", ""))),
                ("Torre / unidade", f"{d.get('torre','')} / {d.get('unidade','')}"),
                ("Tipo", f"{d.get('tipo','')} - {d.get('descricao_tipo','')}"),
                ("Área privativa", f"{float(d.get('area',0) or 0):.2f} m²"),
                ("Preço total", moeda(d.get("preco_total", 0))),
                ("Valor por m²", moeda(ind.get("valor_m2", 0))),
            ])
        with col_fluxo:
            card_html("Fluxo extraído / ajustado", [
                ("Entrada", moeda(d.get("entrada", 0))),
                ("Parcelas", f"{int(d.get('qtd_parcelas',0) or 0)}x de {moeda(d.get('valor_parcela',0))}"),
                ("Reforços até entrega", f"{int(d.get('qtd_reforcos_pre',0) or 0)}x de {moeda(d.get('reforco_pre_valor',0))}"),
                ("Reforços pós-entrega", f"{int(d.get('qtd_reforcos_pos',0) or 0)}x de {moeda(d.get('reforco_pos_valor',0))}"),
                ("CUB simulado", pct(d.get("cub_anual", 0))),
                ("Valorização simulada", pct(d.get("valorizacao_anual", 0))),
            ])

        col_retorno, col_estrategia = st.columns(2)
        with col_retorno:
            card_html("Retorno projetado", [
                ("Valor na entrega", moeda(ind.get("valor_entrega", 0))),
                ("Investido na entrega", moeda(ind.get("investido_entrega", 0))),
                ("Saldo a assumir na entrega", moeda(ind.get("saldo_devedor_entrega", 0))),
                ("Lucro líquido na entrega", moeda(ind.get("lucro_entrega", 0))),
                ("ROI na entrega", pct(ind.get("roi_entrega", 0))),
                ("Valor projetado final", moeda(ind.get("valor_final", 0))),
            ])
        with col_estrategia:
            card_html("Decisão executiva", [
                ("Status", status),
                ("Score", f"{score_val:.1f}/10"),
                ("Risco", str(d.get("risco", "Médio"))),
                ("Liquidez", str(d.get("liquidez", "Alta"))),
                ("Estratégia", leitura),
            ])

        chart_left, chart_right = st.columns([1.1, 1])
        with chart_left:
            st.plotly_chart(fig_patrimonio(df), use_container_width=True)
        with chart_right:
            st.plotly_chart(fig_fluxo(df), use_container_width=True)

# ============================================================
# PROPOSTA MANUAL
# ============================================================
elif menu == "Proposta Manual":
    st.markdown('<div class="hero-premium"><h1 class="hero-title">Proposta Manual</h1><p class="hero-sub">Monte ou ajuste a proposta conforme sua negociação: entrada, parcelas, prazo, reforços, CUB e valorização.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    d = render_inputs_proposta(d, prefixo="proposta")
    st.session_state.dados = d
    st.success("Proposta manual atualizada. O painel, os cenários e o relatório já usam estes valores.")
    st.markdown('</div>', unsafe_allow_html=True)

    df_manual, ind_manual = indicadores(d)
    if float(d.get("preco_total", 0) or 0) > 0:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card("🏷️", "Preço", moeda(d.get("preco_total", 0)), "Valor da proposta", "mid")
        with c2:
            kpi_card("📐", "Valor m²", moeda(ind_manual.get("valor_m2", 0)), f"Área {float(d.get('area',0) or 0):.2f} m²", "good")
        with c3:
            kpi_card("💰", "Investido até entrega", moeda(ind_manual.get("investido_entrega", 0)), f"CUB {pct(d.get('cub_anual',0))}", "mid")
        with c4:
            kpi_card("📈", "Lucro na entrega", moeda(ind_manual.get("lucro_entrega", 0)), f"ROI {pct(ind_manual.get('roi_entrega',0))}", "good" if ind_manual.get("lucro_entrega", 0) > 0 else "bad")

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_fluxo(df_manual), use_container_width=True)
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
# ============================================================
# CENÁRIOS
# ============================================================
elif menu == "Cenários":
    st.markdown('<div class="hero-premium"><h1 class="hero-title">Cenários de CUB e Valorização</h1><p class="hero-sub">Simule cenários conservador, base e agressivo sem perder os dados extraídos do PDF.</p></div>', unsafe_allow_html=True)

    if float(d.get("preco_total", 0) or 0) <= 0:
        st.warning("Importe uma unidade primeiro para criar cenários.")
    else:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Premissas dos cenários</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Conservador**")
            cub_conservador = st.slider("CUB conservador a.a.", 0.0, 15.0, 6.0, 0.1, key="cub_conservador")
            val_conservador = st.slider("Valorização conservadora a.a.", 0.0, 30.0, 8.0, 0.5, key="val_conservador")
        with c2:
            st.markdown("**Base**")
            cub_base = st.slider("CUB base a.a.", 0.0, 15.0, float(d.get("cub_anual", 4.3) or 4.3), 0.1, key="cub_base")
            val_base = st.slider("Valorização base a.a.", 0.0, 30.0, float(d.get("valorizacao_anual", 12.0) or 12.0), 0.5, key="val_base")
        with c3:
            st.markdown("**Agressivo**")
            cub_agressivo = st.slider("CUB agressivo a.a.", 0.0, 15.0, 4.3, 0.1, key="cub_agressivo")
            val_agressivo = st.slider("Valorização agressiva a.a.", 0.0, 30.0, 15.0, 0.5, key="val_agressivo")

        cenarios = [
            ("Conservador", cub_conservador, val_conservador),
            ("Base", cub_base, val_base),
            ("Agressivo", cub_agressivo, val_agressivo),
        ]

        linhas_cenarios = []
        for nome, cub_c, val_c in cenarios:
            temp = d.copy()
            temp["cub_anual"] = cub_c
            temp["valorizacao_anual"] = val_c
            df_temp, ind_temp = indicadores(temp)
            linhas_cenarios.append({
                "Cenário": nome,
                "CUB anual": cub_c,
                "Valorização anual": val_c,
                "Valor por m²": ind_temp.get("valor_m2", 0),
                "Investido até entrega": ind_temp.get("investido_entrega", 0),
                "Valor na entrega": ind_temp.get("valor_entrega", 0),
                "Lucro na entrega": ind_temp.get("lucro_entrega", 0),
                "ROI na entrega": ind_temp.get("roi_entrega", 0),
                "Score": ind_temp.get("score", 0),
            })

        df_cenarios = pd.DataFrame(linhas_cenarios)

        k1, k2, k3 = st.columns(3)
        for col, row in zip([k1, k2, k3], linhas_cenarios):
            with col:
                kpi_card("📊", row["Cenário"], moeda(row["Lucro na entrega"]), f"ROI {pct(row['ROI na entrega'])} | Score {row['Score']:.1f}", "good" if row["Lucro na entrega"] > 0 else "bad")

        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_cenarios["Cenário"], y=df_cenarios["Lucro na entrega"], name="Lucro na entrega"))
            fig.update_layout(title="Lucro na entrega por cenário", height=360, plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=15, r=15, t=50, b=15), yaxis=dict(gridcolor="#e5e7eb"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_cenarios["Cenário"], y=df_cenarios["ROI na entrega"], name="ROI na entrega"))
            fig.update_layout(title="ROI na entrega por cenário", height=360, plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=15, r=15, t=50, b=15), yaxis=dict(gridcolor="#e5e7eb"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Comparativo executivo</div>', unsafe_allow_html=True)
        df_view = df_cenarios.copy()
        for col in ["Valor por m²", "Investido até entrega", "Valor na entrega", "Lucro na entrega"]:
            df_view[col] = df_view[col].apply(moeda)
        for col in ["CUB anual", "Valorização anual", "ROI na entrega"]:
            df_view[col] = df_view[col].apply(pct)
        df_view["Score"] = df_view["Score"].map(lambda x: f"{x:.1f}/10")
        st.dataframe(df_view, use_container_width=True, height=180)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Aplicar cenário base no painel"):
            d["cub_anual"] = cub_base
            d["valorizacao_anual"] = val_base
            st.session_state.dados = d
            st.success("Cenário base aplicado no painel executivo.")

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
    st.markdown('<div class="hero-premium"><h1 class="hero-title">Relatório Executivo</h1><p class="hero-sub">Gere PDF e salve esta análise para consultar ou apagar depois.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    if float(d.get("preco_total", 0) or 0) <= 0:
        st.warning("Importe uma unidade ou monte uma proposta manual primeiro.")
    else:
        relatorio = texto_relatorio(d, ind)
        st.text_area("Prévia do relatório", relatorio, height=430)
        nome_padrao = f"{d.get('empreendimento','Empreendimento')} - {d.get('torre','')} - Unidade {d.get('unidade','')}"
        nome_analise = st.text_input("Nome para salvar a análise", value=nome_padrao)
        c1, c2, c3 = st.columns(3)
        with c1:
            pdf_bytes = gerar_pdf_bytes(relatorio)
            if pdf_bytes:
                st.download_button(
                    "📄 Baixar relatório PDF",
                    data=pdf_bytes,
                    file_name=f"relatorio_{str(d.get('unidade','analise')).replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
            else:
                st.warning("Para gerar PDF, adicione fpdf2 no requirements.txt.")
        with c2:
            st.download_button(
                "⬇️ Baixar dados da análise",
                data=json.dumps({"dados": d, "indicadores": ind}, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=f"analise_{str(d.get('unidade','imovel')).replace(' ', '_')}.json",
                mime="application/json",
            )
        with c3:
            if st.button("💾 Salvar nesta sessão"):
                salvar_analise_atual(nome_analise, d, ind)
                st.success("Análise salva na aba Análises Salvas.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ANÁLISES SALVAS
# ============================================================
elif menu == "Análises Salvas":
    st.markdown('<div class="hero-premium"><h1 class="hero-title">Análises Salvas</h1><p class="hero-sub">Consulte, baixe em PDF ou apague análises salvas durante esta sessão.</p></div>', unsafe_allow_html=True)
    if not st.session_state.analises_salvas:
        st.info("Nenhuma análise salva ainda. Gere uma análise na aba Relatório e clique em salvar.")
    else:
        for idx, item in enumerate(list(st.session_state.analises_salvas)):
            dados_item = item.get('dados', {})
            ind_item = item.get('indicadores', {})
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown(f"### {item.get('nome','Análise')}  \nSalva em: **{item.get('data','')}**")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Unidade", dados_item.get('unidade',''))
            with c2:
                st.metric("Preço", moeda(dados_item.get('preco_total',0)))
            with c3:
                st.metric("Lucro entrega", moeda(ind_item.get('lucro_entrega',0)))
            with c4:
                st.metric("Score", f"{ind_item.get('score',0):.1f}/10")

            rel = texto_relatorio(dados_item, ind_item)
            b1, b2, b3 = st.columns(3)
            with b1:
                pdf = gerar_pdf_bytes(rel)
                if pdf:
                    st.download_button("Baixar PDF", data=pdf, file_name=f"relatorio_salvo_{idx+1}.pdf", mime="application/pdf", key=f"pdf_salvo_{item['id']}")
            with b2:
                if st.button("Carregar no painel", key=f"carregar_{item['id']}"):
                    st.session_state.dados = dict(dados_item)
                    st.success("Análise carregada no painel.")
            with b3:
                if st.button("Apagar", key=f"apagar_{item['id']}"):
                    st.session_state.analises_salvas = [x for x in st.session_state.analises_salvas if x.get('id') != item.get('id')]
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
