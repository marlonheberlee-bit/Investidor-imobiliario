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
# CSS - PAINEL EXECUTIVO
# ============================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#061936 0%,#020817 100%);} 
[data-testid="stSidebar"] * {color:white!important;}
.logo {font-size:27px;font-weight:900;margin-bottom:0px;}
.logo-sub {font-size:11px;letter-spacing:2.5px;color:#93c5fd!important;margin-bottom:28px;}
.hero {background:linear-gradient(135deg,#061936,#123a75,#2563eb);padding:30px;border-radius:28px;color:white;margin-bottom:22px;box-shadow:0 20px 45px rgba(15,23,42,.18)}
.hero h1 {font-size:36px;font-weight:900;margin:0 0 5px 0;}
.hero p {color:#dbeafe;margin:0;font-size:16px;}
.card {background:white;padding:24px;border-radius:24px;border:1px solid #e5eaf3;box-shadow:0 12px 32px rgba(15,23,42,.075);margin-bottom:20px;}
.kpi {background:white;padding:22px;border-radius:22px;border:1px solid #e5eaf3;box-shadow:0 12px 32px rgba(15,23,42,.08);min-height:142px;}
.kpi-label {font-size:12px;color:#64748b;font-weight:900;text-transform:uppercase;letter-spacing:.3px;}
.kpi-value {font-size:26px;font-weight:900;color:#071735;margin-top:10px;line-height:1.1;}
.good {color:#059669;font-weight:800;font-size:13px;margin-top:9px;}
.mid {color:#d97706;font-weight:800;font-size:13px;margin-top:9px;}
.bad {color:#dc2626;font-weight:800;font-size:13px;margin-top:9px;}
.metric-line {display:flex;justify-content:space-between;gap:14px;border-bottom:1px solid #edf2f7;padding:10px 0;font-size:14px;}
.metric-line span {color:#64748b;}
.metric-line b {color:#0f172a;text-align:right;}
.section-title {font-size:20px;font-weight:900;color:#0f172a;margin-bottom:12px;}
.small-note {color:#64748b;font-size:13px;}
.stButton > button {background:linear-gradient(90deg,#1d4ed8,#4f46e5);color:white;border:none;border-radius:14px;font-weight:800;padding:.65rem 1.15rem;}
.stButton > button:hover {color:white;background:linear-gradient(90deg,#1e40af,#3730a3);}
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


def pct(v) -> str:
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"


def numero_br_para_float(v) -> float:
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


# ============================================================
# PDF PARSER
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
                            linhas.append(linha)
            except Exception:
                pass

            paginas.append({"page": idx, "text": page_text, "lines": page_lines, "table_lines": table_lines})
            linhas.extend(page_lines)
    return texto, linhas, paginas


def extrair_info_pagina_ap_towers(page_text: str) -> Dict:
    info = {}
    m = re.search(r"(PR[ÉE]-LAN[ÇC]AMENTO\s+.+?FASE\s*\d+)", page_text, flags=re.I)
    if m:
        info["empreendimento"] = re.sub(r"\s+", " ", m.group(1)).strip().title()
    else:
        info["empreendimento"] = "Empreendimento identificado no PDF"

    m = re.search(r"TORRE\s*(\d+)\s*-\s*ENTREGA\s*EM\s*(\d{4})", page_text, flags=re.I)
    if m:
        info["torre"] = f"Torre {int(m.group(1)):02d}"
        info["entrega_ano"] = int(m.group(2))

    m = re.search(r"LOCALIZA[ÇC][ÃA]O\s*-\s*(.+)", page_text, flags=re.I)
    if m:
        info["localizacao"] = re.sub(r"\s+", " ", m.group(1)).strip()

    reforcos = re.findall(r"(\d{1,2})\s+REFOR[ÇC]OS", page_text, flags=re.I)
    if reforcos:
        info["qtd_reforcos_pre"] = int(reforcos[0])
        if len(reforcos) > 1:
            info["qtd_reforcos_pos"] = int(reforcos[1])
    return info


def extrair_areas_por_tipo(page_text: str) -> Dict[str, Dict]:
    # Exemplo no PDF: TIPO 01 / 1 Suíte + / 2 Dormitórios / 84,81m²
    areas = {}
    pattern = re.compile(r"TIPO\s*(\d{2}).{0,80}?(\d{2,3}[,.]\d{2})\s*m[²2]", re.I | re.S)
    for tipo, area in pattern.findall(page_text):
        areas[tipo] = {
            "tipo": f"TIPO {tipo}",
            "area": numero_br_para_float(area),
            "descricao": "1 Suíte + 2 Dormitórios",
        }
    return areas


def expandir_apartamentos(expr: str) -> List[str]:
    expr = expr.strip()
    partes = re.split(r"\s+e\s+|\s*,\s*", expr)
    resultado = []
    for parte in partes:
        parte = parte.strip()
        m = re.match(r"^(\d{3,4})\s+ao\s+(\d{3,4})$", parte)
        if m:
            ini, fim = m.group(1), m.group(2)
            sufixo_ini = int(ini[-2:])
            sufixo_fim = int(fim[-2:])
            andar_ini = int(ini[:-2])
            andar_fim = int(fim[:-2])
            if sufixo_ini == sufixo_fim and andar_fim >= andar_ini:
                for andar in range(andar_ini, andar_fim + 1):
                    resultado.append(f"{andar}{sufixo_ini:02d}")
            else:
                resultado.extend([ini, fim])
        else:
            nums = re.findall(r"\d{3,4}", parte)
            resultado.extend(nums)
    return resultado


def linhas_comerciais_ap_towers(page_text: str) -> List[Dict]:
    page_info = extrair_info_pagina_ap_towers(page_text)
    areas_tipo = extrair_areas_por_tipo(page_text)
    rows = []

    # Captura linhas do tipo:
    # 1301 e 2401 R$ 55.500,00 120x R$ 2.600,00 R$ 24.450,00 R$ 84.924,25 R$ 1.340.294,00
    rgx = re.compile(
        r"(?P<apts>(?:\d{3,4})(?:\s+(?:e|ao)\s+\d{3,4})?)\s+"
        r"R\$\s*(?P<entrada>[\d\.]+,\d{2})\s+"
        r"(?P<qtd>\d+)x\s+R\$\s*(?P<parcela>[\d\.]+,\d{2})\s+"
        r"R\$\s*(?P<ref_pre>[\d\.]+,\d{2})\s+"
        r"R\$\s*(?P<ref_pos>[\d\.]+,\d{2})\s+"
        r"R\$\s*(?P<total>[\d\.]+,\d{2})",
        flags=re.I,
    )

    # Define o TIPO pela seção anterior mais próxima no texto.
    tipo_atual = None
    for linha in page_text.splitlines():
        mtipo = re.search(r"TIPO\s*(\d{2})", linha, flags=re.I)
        if mtipo:
            tipo_atual = mtipo.group(1)
        m = rgx.search(linha)
        if not m:
            continue
        apts_expr = m.group("apts")
        unidades = expandir_apartamentos(apts_expr)
        if unidades:
            # fallback: pelo final da unidade, se não conseguiu tipo pela seção
            tipo_linha = tipo_atual or unidades[0][-2:]
        else:
            tipo_linha = tipo_atual

        for unidade in unidades:
            tipo_final = tipo_linha or unidade[-2:]
            area_info = areas_tipo.get(tipo_final, {})
            rows.append({
                **page_info,
                "unidade": unidade,
                "apartamento_grupo": apts_expr,
                "tipo": area_info.get("tipo", f"TIPO {tipo_final}"),
                "descricao_tipo": area_info.get("descricao", ""),
                "area": area_info.get("area", 0.0),
                "entrada": numero_br_para_float(m.group("entrada")),
                "qtd_parcelas": int(m.group("qtd")),
                "valor_parcela": numero_br_para_float(m.group("parcela")),
                "reforco_pre_valor": numero_br_para_float(m.group("ref_pre")),
                "reforco_pos_valor": numero_br_para_float(m.group("ref_pos")),
                "preco_total": numero_br_para_float(m.group("total")),
                "qtd_reforcos_pre": page_info.get("qtd_reforcos_pre", 0),
                "qtd_reforcos_pos": page_info.get("qtd_reforcos_pos", 0),
                "pagina": page_info.get("page", None),
            })
    return rows


def parser_ap_towers(paginas: List[Dict]) -> List[Dict]:
    todos = []
    for p in paginas:
        rows = linhas_comerciais_ap_towers(p["text"])
        for r in rows:
            r["pagina"] = p["page"]
        todos.extend(rows)
    return todos


def buscar_unidade_generico(texto: str, linhas: List[str], unidade: str) -> Optional[Dict]:
    todas = [l.strip() for l in texto.splitlines() if l.strip()] + linhas
    blocos = []
    for i, linha in enumerate(todas):
        if re.search(rf"\b{re.escape(str(unidade))}\b", linha):
            blocos.append(" ".join(todas[max(0, i - 1): min(len(todas), i + 2)]))
    if not blocos:
        return None
    bloco = " ".join(blocos)
    vals = [numero_br_para_float(v) for v in re.findall(r"R\$\s*[\d\.]+,\d{2}", bloco)]
    areas = [numero_br_para_float(a) for a in re.findall(r"(\d{2,3}[,.]\d{2})\s*m[²2]", bloco, flags=re.I)]
    return {
        "unidade": str(unidade),
        "empreendimento": "Empreendimento identificado no PDF",
        "localizacao": "Não identificada",
        "torre": "Não identificada",
        "tipo": "Não identificado",
        "area": areas[0] if areas else 0.0,
        "entrada": vals[0] if len(vals) > 0 else 0.0,
        "qtd_parcelas": 120,
        "valor_parcela": vals[1] if len(vals) > 1 else 0.0,
        "reforco_pre_valor": vals[2] if len(vals) > 2 else 0.0,
        "reforco_pos_valor": vals[3] if len(vals) > 3 else 0.0,
        "preco_total": max(vals) if vals else 0.0,
        "qtd_reforcos_pre": 0,
        "qtd_reforcos_pos": 0,
        "trecho": bloco,
        "parser": "genérico",
    }


def buscar_unidade_pdf(texto: str, linhas: List[str], paginas: List[Dict], unidade: str) -> Optional[Dict]:
    rows = parser_ap_towers(paginas)
    for r in rows:
        if str(r["unidade"]) == str(unidade).strip():
            r["parser"] = "AP Towers"
            return r
    return buscar_unidade_generico(texto, linhas, unidade)


# ============================================================
# FLUXO E ANÁLISE
# ============================================================
def meses_entre(base: date, alvo: date) -> int:
    return max(1, (alvo.year - base.year) * 12 + (alvo.month - base.month))


def cronograma_reforcos_ap_towers(d: Dict) -> List[Dict]:
    base = date(2026, 4, 1)  # data da tabela AP Towers: 02.04.2026
    eventos = []
    entrega = int(d.get("entrega_ano") or 2029)

    # Pré-entrega AP Towers: julho e outubro de 2026 + junho/outubro até o ano da entrega.
    qtd_pre = int(d.get("qtd_reforcos_pre") or 0)
    anos_pre = [2026] + list(range(2027, entrega + 1))
    datas_pre = []
    for ano in anos_pre:
        meses = [7, 10] if ano == 2026 else [6, 10]
        for mes in meses:
            datas_pre.append(date(ano, mes, 1))
    datas_pre = datas_pre[:qtd_pre]

    for dt in datas_pre:
        eventos.append({"mes": meses_entre(base, dt), "valor": float(d.get("reforco_pre_valor", 0)), "tipo": "Reforço antes da entrega"})

    # Pós-entrega: junho e outubro dos 4 anos seguintes, geralmente 8 reforços.
    qtd_pos = int(d.get("qtd_reforcos_pos") or 0)
    datas_pos = []
    for ano in range(entrega + 1, entrega + 6):
        for mes in [6, 10]:
            datas_pos.append(date(ano, mes, 1))
    datas_pos = datas_pos[:qtd_pos]

    for dt in datas_pos:
        eventos.append({"mes": meses_entre(base, dt), "valor": float(d.get("reforco_pos_valor", 0)), "tipo": "Reforço depois da entrega"})
    return eventos


def criar_fluxo(d: Dict) -> pd.DataFrame:
    preco = float(d.get("preco_total", 0))
    entrada = float(d.get("entrada", 0))
    qtd_parcelas = int(d.get("qtd_parcelas", 120))
    parcela = float(d.get("valor_parcela", 0))
    entrega_ano = int(d.get("entrega_ano") or 2029)

    cub_mensal = (1 + float(d.get("cub_anual", 4.3)) / 100) ** (1 / 12) - 1
    val_mensal = (1 + float(d.get("valorizacao_anual", 12)) / 100) ** (1 / 12) - 1

    base = date(2026, 4, 1)
    mes_entrega = meses_entre(base, date(entrega_ano, 12, 1))
    prazo_total = max(qtd_parcelas, mes_entrega + 48)

    eventos = cronograma_reforcos_ap_towers(d) if d.get("parser") == "AP Towers" else []
    eventos_por_mes = {}
    for e in eventos:
        eventos_por_mes.setdefault(e["mes"], 0)
        eventos_por_mes[e["mes"]] += e["valor"]

    investido = entrada
    rows = []
    for mes in range(1, prazo_total + 1):
        pagamento = 0.0
        if mes <= qtd_parcelas:
            pagamento += parcela * ((1 + cub_mensal) ** mes)
        pagamento += eventos_por_mes.get(mes, 0.0)

        investido += pagamento
        valor_proj = preco * ((1 + val_mensal) ** mes)
        lucro = valor_proj - investido
        roi = lucro / investido * 100 if investido > 0 else 0
        rows.append({
            "Mês": mes,
            "Fase": "Até entrega" if mes <= mes_entrega else "Pós-entrega",
            "Parcela Corrigida": parcela * ((1 + cub_mensal) ** mes) if mes <= qtd_parcelas else 0,
            "Reforços": eventos_por_mes.get(mes, 0.0),
            "Pagamento Mensal": pagamento,
            "Total Investido": investido,
            "Valor Projetado": valor_proj,
            "Lucro Bruto": lucro,
            "ROI %": roi,
        })
    return pd.DataFrame(rows)


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


def fig_fluxo(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Mês"], y=df["Parcela Corrigida"], name="Parcelas"))
    fig.add_trace(go.Bar(x=df["Mês"], y=df["Reforços"], name="Reforços"))
    fig.update_layout(
        title="Fluxo real de pagamentos do PDF",
        barmode="stack",
        height=370,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=15, r=15, t=50, b=15),
        yaxis=dict(gridcolor="#e5e7eb"),
        xaxis=dict(showgrid=False),
    )
    return fig


def fig_patrimonio(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Valor Projetado"], mode="lines", name="Valor projetado", line=dict(width=4)))
    fig.add_trace(go.Scatter(x=df["Mês"], y=df["Total Investido"], mode="lines", name="Total investido", line=dict(width=4)))
    fig.update_layout(
        title="Patrimônio projetado x capital aportado",
        height=370,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=15, r=15, t=50, b=15),
        yaxis=dict(gridcolor="#e5e7eb"),
        xaxis=dict(showgrid=False),
    )
    return fig


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
    st.caption("Base v2.0: leitura por unidade + fluxo extraído do PDF.")

# ============================================================
# IMPORTAR PDF
# ============================================================
if menu == "Importar PDF":
    st.markdown('<div class="hero"><h1>Importar PDF da Construtora</h1><p>Envie a tabela, digite a unidade e o app aplica automaticamente os dados comerciais e o fluxo.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    arquivo = st.file_uploader("PDF da tabela de vendas", type=["pdf"])
    if arquivo:
        texto, linhas, paginas = ler_pdf(arquivo)
        st.session_state.pdf_texto = texto
        st.session_state.pdf_linhas = linhas
        st.session_state.pdf_paginas = paginas
        st.success("PDF carregado. Agora digite a unidade.")

    c1, c2 = st.columns([1, 3])
    with c1:
        unidade = st.text_input("Apartamento / unidade", value=str(d.get("unidade", "")), placeholder="Ex.: 2401")
        buscar = st.button("Buscar e analisar")
    with c2:
        st.info("Para PDFs diferentes de outras construtoras, o app tenta o modo genérico. Para ficar perfeito em cada construtora, basta criar um parser específico mantendo esta mesma estrutura.")

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
                st.success(f"Unidade {unidade} aplicada na análise.")
            else:
                st.error("Não encontrei essa unidade na tabela do PDF.")

    if st.session_state.ultimo_resultado:
        r = st.session_state.ultimo_resultado
        st.markdown("### Unidade aplicada")
        cols = st.columns(6)
        vals = [
            ("Empreendimento", r.get("empreendimento", "")),
            ("Torre", r.get("torre", "")),
            ("Unidade", r.get("unidade", "")),
            ("Área", f"{r.get('area', 0):.2f} m²"),
            ("Entrada", moeda(r.get("entrada", 0))),
            ("Total", moeda(r.get("preco_total", 0))),
        ]
        for col, (lab, val) in zip(cols, vals):
            col.metric(lab, val)
        st.caption(f"Parser usado: {r.get('parser', 'genérico')}")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PREMISSAS
# ============================================================
elif menu == "Dados e Premissas":
    st.markdown('<div class="hero"><h1>Dados e Premissas</h1><p>Confira ou ajuste os dados extraídos antes da análise.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        d["empreendimento"] = st.text_input("Empreendimento", d.get("empreendimento", ""))
        d["localizacao"] = st.text_input("Localização", d.get("localizacao", ""))
        d["torre"] = st.text_input("Torre", d.get("torre", ""))
        d["unidade"] = st.text_input("Unidade", d.get("unidade", ""))
    with c2:
        d["tipo"] = st.text_input("Tipo", d.get("tipo", ""))
        d["descricao_tipo"] = st.text_input("Descrição", d.get("descricao_tipo", ""))
        d["area"] = st.number_input("Área m²", value=float(d.get("area", 0)), min_value=0.0)
        d["preco_total"] = st.number_input("Preço total", value=float(d.get("preco_total", 0)), step=10000.0)
    with c3:
        d["entrada"] = st.number_input("Entrada", value=float(d.get("entrada", 0)), step=5000.0)
        d["qtd_parcelas"] = st.number_input("Qtd. parcelas", value=int(d.get("qtd_parcelas", 120)), min_value=1)
        d["valor_parcela"] = st.number_input("Valor parcela", value=float(d.get("valor_parcela", 0)), step=500.0)
        d["entrega_ano"] = st.number_input("Ano de entrega", value=int(d.get("entrega_ano", 2029)), min_value=2026)

    c4, c5, c6, c7 = st.columns(4)
    with c4:
        d["reforco_pre_valor"] = st.number_input("Valor reforço pré-entrega", value=float(d.get("reforco_pre_valor", 0)), step=1000.0)
    with c5:
        d["qtd_reforcos_pre"] = st.number_input("Qtd. reforços pré", value=int(d.get("qtd_reforcos_pre", 0)), min_value=0)
    with c6:
        d["reforco_pos_valor"] = st.number_input("Valor reforço pós-entrega", value=float(d.get("reforco_pos_valor", 0)), step=1000.0)
    with c7:
        d["qtd_reforcos_pos"] = st.number_input("Qtd. reforços pós", value=int(d.get("qtd_reforcos_pos", 0)), min_value=0)

    c8, c9, c10 = st.columns(3)
    with c8:
        d["cub_anual"] = st.slider("CUB anual", 0.0, 15.0, float(d.get("cub_anual", 4.3)), 0.1)
    with c9:
        d["valorizacao_anual"] = st.slider("Valorização anual", 0.0, 30.0, float(d.get("valorizacao_anual", 12.0)), 0.5)
    with c10:
        d["valor_m2_ref"] = st.number_input("Valor m² referência", value=float(d.get("valor_m2_ref", 17000)), step=500.0)
    st.session_state.dados = d
    st.success("Dados salvos.")
    st.markdown('</div>', unsafe_allow_html=True)

# Cálculos para abas de análise
try:
    df = criar_fluxo(d)
except Exception:
    df = pd.DataFrame()

if not df.empty:
    valor_m2 = float(d.get("preco_total", 0)) / float(d.get("area", 1)) if float(d.get("area", 0)) > 0 else 0
    entrega_mes = meses_entre(date(2026, 4, 1), date(int(d.get("entrega_ano", 2029)), 12, 1))
    linha_entrega = df[df["Mês"] == entrega_mes].iloc[0] if entrega_mes in df["Mês"].values else df.iloc[min(len(df)-1, entrega_mes-1)]
    linha_final = df.iloc[-1]
    investido_entrega = linha_entrega["Total Investido"]
    valor_entrega = linha_entrega["Valor Projetado"]
    lucro_entrega = linha_entrega["Lucro Bruto"]
    roi_entrega = linha_entrega["ROI %"]
    investido_final = linha_final["Total Investido"]
    valor_final = linha_final["Valor Projetado"]
    lucro_final = linha_final["Lucro Bruto"]
    roi_final = linha_final["ROI %"]
    nota = calcular_score(d, valor_m2, roi_entrega, lucro_entrega)
else:
    valor_m2 = valor_entrega = investido_entrega = lucro_entrega = roi_entrega = investido_final = valor_final = lucro_final = roi_final = nota = 0

# ============================================================
# PAINEL
# ============================================================
if menu == "Painel Executivo":
    st.markdown(f'<div class="hero"><h1>Painel Executivo</h1><p>{d.get("empreendimento", "")} | {d.get("torre", "")} | Unidade {d.get("unidade", "")}</p></div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        ("Preço Total", moeda(d.get("preco_total", 0)), "Valor extraído do PDF", "mid"),
        ("Valor por m²", moeda(valor_m2), f"Área {float(d.get('area', 0)):.2f} m²", "good"),
        ("Investido até entrega", moeda(investido_entrega), f"Entrada + fluxo até {d.get('entrega_ano', '')}", "mid"),
        ("Lucro na entrega", moeda(lucro_entrega), f"ROI {pct(roi_entrega)}", "good" if lucro_entrega > 0 else "bad"),
        ("Score", f"{nota:.1f}/10", "Nota executiva", "good" if nota >= 7 else "mid" if nota >= 5 else "bad"),
    ]
    for col, (lab, val, sub, cls) in zip([k1, k2, k3, k4, k5], kpis):
        col.markdown(f'<div class="kpi"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div><div class="{cls}">{sub}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            st.plotly_chart(fig_fluxo(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            st.plotly_chart(fig_patrimonio(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4, c5 = st.columns(3)
    with c3:
        st.markdown('<div class="card"><div class="section-title">Ativo</div>', unsafe_allow_html=True)
        for lab, val in [("Empreendimento", d.get("empreendimento", "")), ("Localização", d.get("localizacao", "")), ("Torre", d.get("torre", "")), ("Unidade", d.get("unidade", "")), ("Tipo", d.get("tipo", "")), ("Área", f"{float(d.get('area',0)):.2f} m²")]:
            st.markdown(f'<div class="metric-line"><span>{lab}</span><b>{val}</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="card"><div class="section-title">Fluxo do PDF</div>', unsafe_allow_html=True)
        for lab, val in [("Entrada", moeda(d.get("entrada", 0))), ("Parcelas", f"{int(d.get('qtd_parcelas',0))}x de {moeda(d.get('valor_parcela',0))}"), ("Reforços pré", f"{int(d.get('qtd_reforcos_pre',0))}x de {moeda(d.get('reforco_pre_valor',0))}"), ("Reforços pós", f"{int(d.get('qtd_reforcos_pos',0))}x de {moeda(d.get('reforco_pos_valor',0))}"), ("CUB", pct(d.get("cub_anual",0)))]:
            st.markdown(f'<div class="metric-line"><span>{lab}</span><b>{val}</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="card"><div class="section-title">Diagnóstico</div>', unsafe_allow_html=True)
        if nota >= 8:
            st.success("Excelente oportunidade")
        elif nota >= 6:
            st.warning("Boa oportunidade")
        else:
            st.error("Cautela")
        st.write(f"A análise considera o fluxo extraído do PDF, CUB, valorização projetada e aporte acumulado.")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# FLUXO DETALHADO
# ============================================================
elif menu == "Fluxo Detalhado":
    st.markdown('<div class="hero"><h1>Fluxo Detalhado</h1><p>Parcela, reforços, aporte acumulado e projeção do imóvel mês a mês.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not df.empty:
        df_show = df.copy()
        for col in ["Parcela Corrigida", "Reforços", "Pagamento Mensal", "Total Investido", "Valor Projetado", "Lucro Bruto"]:
            df_show[col] = df_show[col].apply(moeda)
        df_show["ROI %"] = df_show["ROI %"].apply(pct)
        st.dataframe(df_show, use_container_width=True, height=600)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RELATÓRIO
# ============================================================
elif menu == "Relatório":
    st.markdown('<div class="hero"><h1>Relatório Executivo</h1><p>Resumo pronto para avaliação de investimento.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"""
# Relatório Executivo Imobiliário

## Ativo
**Empreendimento:** {d.get('empreendimento','')}  
**Localização:** {d.get('localizacao','')}  
**Torre:** {d.get('torre','')}  
**Unidade:** {d.get('unidade','')}  
**Tipo:** {d.get('tipo','')} - {d.get('descricao_tipo','')}  
**Área privativa:** {float(d.get('area',0)):.2f} m²  

## Condições extraídas do PDF
**Preço total:** {moeda(d.get('preco_total',0))}  
**Entrada:** {moeda(d.get('entrada',0))}  
**Parcelas:** {int(d.get('qtd_parcelas',0))}x de {moeda(d.get('valor_parcela',0))}  
**Reforços antes da entrega:** {int(d.get('qtd_reforcos_pre',0))}x de {moeda(d.get('reforco_pre_valor',0))}  
**Reforços depois da entrega:** {int(d.get('qtd_reforcos_pos',0))}x de {moeda(d.get('reforco_pos_valor',0))}  
**Entrega:** {d.get('entrega_ano','')}  

## Projeção
**Valor por m²:** {moeda(valor_m2)}  
**Investido até entrega:** {moeda(investido_entrega)}  
**Valor projetado na entrega:** {moeda(valor_entrega)}  
**Lucro bruto na entrega:** {moeda(lucro_entrega)}  
**ROI na entrega:** {pct(roi_entrega)}  

**Investido final:** {moeda(investido_final)}  
**Valor final projetado:** {moeda(valor_final)}  
**Lucro final:** {moeda(lucro_final)}  
**ROI final:** {pct(roi_final)}  

## Score
**Nota da oportunidade:** {nota:.1f}/10

A leitura do PDF foi feita pelo parser: **{d.get('parser','')}**.
""")
    st.markdown('</div>', unsafe_allow_html=True)
