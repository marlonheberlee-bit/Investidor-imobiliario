import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import base64
from datetime import datetime

import plotly.graph_objects as go
import plotly.express as px

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    from fpdf import FPDF
except Exception:
    FPDF = None


st.set_page_config(
    page_title="Investidor Imobiliário Pro",
    page_icon="🏢",
    layout="wide"
)


# =========================================================
# CSS EXECUTIVO
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: #f4f7fb;
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #061936 0%, #020817 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.sidebar-logo {
    font-size: 26px;
    font-weight: 900;
    margin-bottom: 2px;
}

.sidebar-sub {
    font-size: 11px;
    color: #93c5fd !important;
    letter-spacing: 2.5px;
    margin-bottom: 30px;
}

.hero {
    background: linear-gradient(135deg, #061936 0%, #123a75 50%, #2563eb 100%);
    border-radius: 28px;
    padding: 30px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.20);
}

.hero h1 {
    font-size: 38px;
    font-weight: 900;
    margin-bottom: 6px;
}

.hero p {
    color: #dbeafe;
    font-size: 16px;
}

.kpi-card {
    background: white;
    padding: 24px;
    border-radius: 24px;
    border: 1px solid #e5eaf3;
    box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
    min-height: 155px;
}

.kpi-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .4px;
}

.kpi-value {
    color: #071735;
    font-size: 28px;
    font-weight: 900;
    margin-top: 10px;
}

.kpi-sub-good {
    color: #059669;
    font-size: 13px;
    font-weight: 700;
    margin-top: 8px;
}

.kpi-sub-bad {
    color: #dc2626;
    font-size: 13px;
    font-weight: 700;
    margin-top: 8px;
}

.kpi-sub-mid {
    color: #d97706;
    font-size: 13px;
    font-weight: 700;
    margin-top: 8px;
}

.panel-card {
    background: white;
    padding: 25px;
    border-radius: 26px;
    border: 1px solid #e5eaf3;
    box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
    margin-bottom: 22px;
}

.section-title {
    color: #081a3a;
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 15px;
}

.metric-line {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    border-bottom: 1px solid #edf2f7;
    padding: 11px 0;
    font-size: 14px;
}

.metric-line span {
    color: #64748b;
}

.metric-line b {
    color: #0f172a;
    text-align: right;
}

.badge-good {
    background: #dcfce7;
    color: #166534;
    padding: 9px 15px;
    border-radius: 999px;
    font-weight: 800;
    display: inline-block;
}

.badge-mid {
    background: #fef3c7;
    color: #92400e;
    padding: 9px 15px;
    border-radius: 999px;
    font-weight: 800;
    display: inline-block;
}

.badge-bad {
    background: #fee2e2;
    color: #991b1b;
    padding: 9px 15px;
    border-radius: 999px;
    font-weight: 800;
    display: inline-block;
}

.alert-box {
    padding: 18px;
    border-radius: 18px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e3a8a;
    font-weight: 600;
}

.stButton > button {
    background: linear-gradient(90deg, #1d4ed8, #4f46e5);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 0.75rem 1.2rem;
    font-weight: 800;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #1e40af, #3730a3);
    color: white;
}

div[data-testid="stMetric"] {
    background: white;
    border-radius: 20px;
    padding: 18px;
    border: 1px solid #e5eaf3;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def moeda(v):
    try:
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def pct(v):
    try:
        return f"{v:.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"


def br_num(v):
    try:
        return f"{v:,.0f}".replace(",", ".")
    except Exception:
        return "0"


def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def extrair_texto_pdf(uploaded_file):
    if pdfplumber is None:
        return ""

    texto = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += "\n" + t
    except Exception:
        texto = ""
    return texto


def extrair_dados_pdf(texto):
    dados = {}

    valores = re.findall(r'R\$\s?[\d\.\,]+', texto)
    areas = re.findall(r'(\d{2,3}[\,\.]?\d*)\s?m[²2]', texto.lower())
    unidades = re.findall(r'(apto|apartamento|unidade)\s?[:\-]?\s?(\d+)', texto.lower())

    nums = []
    for v in valores:
        limpo = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            nums.append(float(limpo))
        except Exception:
            pass

    if nums:
        dados["preco_total"] = max(nums)

    if areas:
        try:
            dados["area"] = float(areas[0].replace(",", "."))
        except Exception:
            pass

    if unidades:
        dados["unidade"] = unidades[0][1]

    return dados


def criar_fluxo(d):
    preco_total = d["preco_total"]
    meses_entrega = int(d["prazo_entrega"])
    prazo_total = int(d["prazo_total"])
    valor_parcela = d["valor_parcela"]
    entrada = d["entrada"]

    cub_mensal = (1 + d["cub_anual"] / 100) ** (1 / 12) - 1
    val_mensal = (1 + d["valorizacao_anual"] / 100) ** (1 / 12) - 1

    saldo_investido = entrada
    linhas = []

    meses_ref_pre = d.get("meses_ref_pre", "")
    valores_ref_pre = d.get("valores_ref_pre", "")

    meses_ref_pos = d.get("meses_ref_pos", "")
    valores_ref_pos = d.get("valores_ref_pos", "")

    reforcos_pre = {}
    reforcos_pos = {}

    try:
        ms = [int(x.strip()) for x in meses_ref_pre.split(",") if x.strip()]
        vs = [float(x.strip().replace(".", "").replace(",", ".")) for x in valores_ref_pre.split(",") if x.strip()]
        for m, v in zip(ms, vs):
            reforcos_pre[m] = v
    except Exception:
        pass

    try:
        ms = [int(x.strip()) for x in meses_ref_pos.split(",") if x.strip()]
        vs = [float(x.strip().replace(".", "").replace(",", ".")) for x in valores_ref_pos.split(",") if x.strip()]
        for m, v in zip(ms, vs):
            reforcos_pos[m] = v
    except Exception:
        pass

    for m in range(1, prazo_total + 1):
        pagamento = 0

        if m <= d["qtd_parcelas"]:
            pagamento += valor_parcela * ((1 + cub_mensal) ** m)

        reforco = 0

        if m <= meses_entrega:
            for mes_ref, valor_ref in reforcos_pre.items():
                if mes_ref > 0 and m % mes_ref == 0:
                    reforco += valor_ref
        else:
            mes_pos = m - meses_entrega
            for mes_ref, valor_ref in reforcos_pos.items():
                if mes_ref > 0 and mes_pos % mes_ref == 0:
                    reforco += valor_ref

        pagamento += reforco
        saldo_investido += pagamento

        valor_imovel = preco_total * ((1 + val_mensal) ** m)
        lucro = valor_imovel - saldo_investido
        roi = (lucro / saldo_investido) * 100 if saldo_investido > 0 else 0

        linhas.append({
            "Mês": m,
            "Fase": "Antes da entrega" if m <= meses_entrega else "Depois da entrega",
            "Pagamento Mensal": pagamento,
            "Total Investido": saldo_investido,
            "Valor Projetado": valor_imovel,
            "Lucro Bruto": lucro,
            "ROI %": roi
        })

    return pd.DataFrame(linhas)


def calcular_score(d, valor_m2, roi_entrega, lucro_entrega, investido_entrega):
    nota = 5.0

    if roi_entrega >= 80:
        nota += 2.2
    elif roi_entrega >= 50:
        nota += 1.6
    elif roi_entrega >= 30:
        nota += 0.9
    elif roi_entrega < 15:
        nota -= 1.2

    if d["valor_m2_ref"] > 0:
        desconto = (d["valor_m2_ref"] - valor_m2) / d["valor_m2_ref"]
        if desconto >= 0.20:
            nota += 1.5
        elif desconto >= 0.10:
            nota += 1.0
        elif desconto >= 0.03:
            nota += 0.4
        elif desconto < -0.08:
            nota -= 1.0

    if d["prazo_entrega"] <= 24:
        nota += 0.8
    elif d["prazo_entrega"] >= 60:
        nota -= 0.7

    if d["risco"] == "Baixo":
        nota += 0.9
    elif d["risco"] == "Alto":
        nota -= 1.2

    if investido_entrega > 0 and lucro_entrega / investido_entrega > 0.5:
        nota += 0.6

    return max(0, min(10, nota))


def fig_linha(df, x, y, titulo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode="lines+markers",
        fill="tozeroy",
        line=dict(width=4),
        marker=dict(size=7)
    ))
    fig.update_layout(
        title=titulo,
        height=370,
        margin=dict(l=15, r=15, t=50, b=15),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#0f172a"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )
    return fig


def fig_barra(df, x, y, titulo):
    fig = px.bar(df, x=x, y=y, text_auto=".2s")
    fig.update_layout(
        title=titulo,
        height=370,
        margin=dict(l=15, r=15, t=50, b=15),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#0f172a"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )
    return fig


def gerar_pdf_relatorio(d, resumo):
    if FPDF is None:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "Relatorio Executivo Imobiliario", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.ln(5)

    for linha in resumo:
        pdf.multi_cell(0, 8, linha.encode("latin-1", "ignore").decode("latin-1"))

    return pdf.output(dest="S").encode("latin-1")


# =========================================================
# ESTADO INICIAL
# =========================================================
if "dados" not in st.session_state:
    st.session_state.dados = {
        "empreendimento": "Residencial Vista Mar",
        "construtora": "Construtora Exemplo",
        "localizacao": "Porto Belo / SC",
        "unidade": "1201",
        "tipo": "Apartamento",
        "area": 90.0,
        "vagas": 2,
        "preco_total": 1351000.0,
        "entrada": 120000.0,
        "qtd_parcelas": 66,
        "valor_parcela": 6500.0,
        "prazo_entrega": 36,
        "prazo_total": 96,
        "meses_ref_pre": "6,10",
        "valores_ref_pre": "30000,50000",
        "meses_ref_pos": "6,10",
        "valores_ref_pos": "25000,40000",
        "cub_anual": 4.3,
        "valorizacao_anual": 12.0,
        "valor_m2_ref": 17000.0,
        "risco": "Médio",
        "liquidez": "Alta",
        "perfil": "Revenda com valorização"
    }


d = st.session_state.dados


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏢 ImobInvest Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">PAINEL EXECUTIVO</div>', unsafe_allow_html=True)

    menu = st.radio(
        "Menu",
        [
            "Painel Executivo",
            "Cadastro e PDF",
            "Fluxo de Pagamento",
            "Cenários",
            "Relatório PDF"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Modelo profissional para avaliação de oportunidades imobiliárias.")


# =========================================================
# CADASTRO
# =========================================================
if menu == "Cadastro e PDF":
    st.markdown("""
    <div class="hero">
        <h1>Cadastro do Empreendimento</h1>
        <p>Preencha os dados manualmente ou envie um PDF da construtora para tentar extrair informações automaticamente.</p>
    </div>
    """, unsafe_allow_html=True)

    col_pdf, col_form = st.columns([1, 2])

    with col_pdf:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Leitor de PDF</div>', unsafe_allow_html=True)

        arquivo = st.file_uploader("Enviar PDF", type=["pdf"])

        if arquivo:
            texto = extrair_texto_pdf(arquivo)
            extraidos = extrair_dados_pdf(texto)

            if extraidos:
                for k, v in extraidos.items():
                    d[k] = v
                st.session_state.dados = d
                st.success("Dados encontrados no PDF e aplicados.")
            else:
                st.warning("Não encontrei dados suficientes. Preencha manualmente.")

            with st.expander("Ver texto extraído"):
                st.text_area("Texto", texto, height=350)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_form:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Dados do Imóvel</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            d["empreendimento"] = st.text_input("Empreendimento", d["empreendimento"])
            d["construtora"] = st.text_input("Construtora", d["construtora"])
            d["localizacao"] = st.text_input("Localização", d["localizacao"])

        with c2:
            d["unidade"] = st.text_input("Unidade", d["unidade"])
            d["tipo"] = st.selectbox("Tipo", ["Apartamento", "Flat", "Casa", "Terreno", "Sala Comercial"], index=0)
            d["vagas"] = st.number_input("Vagas", min_value=0, value=int(d["vagas"]))

        with c3:
            d["area"] = st.number_input("Área privativa m²", min_value=1.0, value=float(d["area"]))
            d["preco_total"] = st.number_input("Preço total", min_value=0.0, value=float(d["preco_total"]), step=10000.0)
            d["valor_m2_ref"] = st.number_input("Valor m² médio da região", min_value=0.0, value=float(d["valor_m2_ref"]), step=500.0)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Premissas</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            d["valorizacao_anual"] = st.slider("Valorização anual", 0.0, 30.0, float(d["valorizacao_anual"]), 0.5)

        with c2:
            d["cub_anual"] = st.slider("CUB anual", 0.0, 15.0, float(d["cub_anual"]), 0.1)

        with c3:
            d["risco"] = st.selectbox("Risco", ["Baixo", "Médio", "Alto"], index=["Baixo", "Médio", "Alto"].index(d["risco"]))

        with c4:
            d["liquidez"] = st.selectbox("Liquidez", ["Alta", "Média", "Baixa"], index=["Alta", "Média", "Baixa"].index(d["liquidez"]))

        d["perfil"] = st.text_input("Perfil ideal da operação", d["perfil"])

        st.session_state.dados = d
        st.success("Cadastro atualizado.")
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# FLUXO
# =========================================================
elif menu == "Fluxo de Pagamento":
    st.markdown("""
    <div class="hero">
        <h1>Fluxo de Pagamento</h1>
        <p>Configure entrada, parcelas, prazo total e reforços variáveis antes e depois da entrega.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Condições Comerciais</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        d["entrada"] = st.number_input("Entrada", min_value=0.0, value=float(d["entrada"]), step=5000.0)

    with c2:
        d["qtd_parcelas"] = st.number_input("Quantidade de parcelas", min_value=1, value=int(d["qtd_parcelas"]))

    with c3:
        d["valor_parcela"] = st.number_input("Valor da parcela", min_value=0.0, value=float(d["valor_parcela"]), step=500.0)

    with c4:
        d["prazo_entrega"] = st.number_input("Meses até entrega", min_value=1, value=int(d["prazo_entrega"]))

    c5, c6 = st.columns(2)

    with c5:
        d["prazo_total"] = st.number_input("Prazo total da operação em meses", min_value=int(d["prazo_entrega"]), value=int(d["prazo_total"]))

    with c6:
        st.info("O prazo total pode continuar após a entrega, simulando parcelas e reforços posteriores.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Reforços Variáveis</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Antes da entrega")
        d["meses_ref_pre"] = st.text_input("Meses de repetição antes da entrega", d["meses_ref_pre"], help="Exemplo: 6,10")
        d["valores_ref_pre"] = st.text_input("Valores dos reforços antes da entrega", d["valores_ref_pre"], help="Exemplo: 30000,50000")

    with c2:
        st.subheader("Depois da entrega")
        d["meses_ref_pos"] = st.text_input("Meses de repetição depois da entrega", d["meses_ref_pos"], help="Exemplo: 6,10")
        d["valores_ref_pos"] = st.text_input("Valores dos reforços depois da entrega", d["valores_ref_pos"], help="Exemplo: 25000,40000")

    st.session_state.dados = d
    st.success("Fluxo atualizado.")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# CÁLCULOS GERAIS
# =========================================================
df = criar_fluxo(d)

area = d["area"]
preco_total = d["preco_total"]
valor_m2 = preco_total / area if area > 0 else 0

linha_entrega = df[df["Mês"] == int(d["prazo_entrega"])].iloc[0]
linha_final = df.iloc[-1]

valor_entrega = linha_entrega["Valor Projetado"]
investido_entrega = linha_entrega["Total Investido"]
lucro_entrega = linha_entrega["Lucro Bruto"]
roi_entrega = linha_entrega["ROI %"]

valor_final = linha_final["Valor Projetado"]
investido_final = linha_final["Total Investido"]
lucro_final = linha_final["Lucro Bruto"]
roi_final = linha_final["ROI %"]

media_mensal_entrega = investido_entrega / d["prazo_entrega"]
nota = calcular_score(d, valor_m2, roi_entrega, lucro_entrega, investido_entrega)


# =========================================================
# PAINEL EXECUTIVO
# =========================================================
if menu == "Painel Executivo":
    st.markdown(f"""
    <div class="hero">
        <h1>Painel Executivo</h1>
        <p>{d["empreendimento"]} | Unidade {d["unidade"]} | {d["localizacao"]}</p>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Preço de Tabela</div>
            <div class="kpi-value">{moeda(preco_total)}</div>
            <div class="kpi-sub-mid">Base de compra</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        sub = "Abaixo da média" if valor_m2 < d["valor_m2_ref"] else "Acima da média"
        cls = "kpi-sub-good" if valor_m2 < d["valor_m2_ref"] else "kpi-sub-bad"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Valor por m²</div>
            <div class="kpi-value">{moeda(valor_m2)}</div>
            <div class="{cls}">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Valor na Entrega</div>
            <div class="kpi-value">{moeda(valor_entrega)}</div>
            <div class="kpi-sub-good">Valorização {pct(d["valorizacao_anual"])} a.a.</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Lucro na Entrega</div>
            <div class="kpi-value">{moeda(lucro_entrega)}</div>
            <div class="kpi-sub-good">ROI {pct(roi_entrega)}</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        cls = "kpi-sub-good" if nota >= 7 else "kpi-sub-mid" if nota >= 5 else "kpi-sub-bad"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Score do Negócio</div>
            <div class="kpi-value">{nota:.1f}/10</div>
            <div class="{cls}">Nota executiva</div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_linha(df, "Mês", "Valor Projetado", "Evolução Projetada do Imóvel"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_linha(df, "Mês", "Lucro Bruto", "Lucro Bruto Projetado"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4, c5 = st.columns(3)

    with c3:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Resumo do Ativo</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-line"><span>Empreendimento</span><b>{d["empreendimento"]}</b></div>
        <div class="metric-line"><span>Construtora</span><b>{d["construtora"]}</b></div>
        <div class="metric-line"><span>Localização</span><b>{d["localizacao"]}</b></div>
        <div class="metric-line"><span>Unidade</span><b>{d["unidade"]}</b></div>
        <div class="metric-line"><span>Área</span><b>{d["area"]} m²</b></div>
        <div class="metric-line"><span>Vagas</span><b>{d["vagas"]}</b></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Indicadores</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-line"><span>Investido até entrega</span><b>{moeda(investido_entrega)}</b></div>
        <div class="metric-line"><span>Aporte médio mensal</span><b>{moeda(media_mensal_entrega)}</b></div>
        <div class="metric-line"><span>Valor projetado final</span><b>{moeda(valor_final)}</b></div>
        <div class="metric-line"><span>Lucro final</span><b>{moeda(lucro_final)}</b></div>
        <div class="metric-line"><span>ROI final</span><b>{pct(roi_final)}</b></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Diagnóstico Executivo</div>', unsafe_allow_html=True)

        if nota >= 8:
            badge = '<span class="badge-good">Excelente oportunidade</span>'
            leitura = "Operação forte, com boa assimetria entre capital aportado e ganho projetado."
        elif nota >= 6:
            badge = '<span class="badge-mid">Boa oportunidade</span>'
            leitura = "Operação interessante, mas precisa validar liquidez, construtora e preço real de revenda."
        else:
            badge = '<span class="badge-bad">Cautela</span>'
            leitura = "O retorno projetado pode não compensar o risco, prazo ou fluxo exigido."

        st.markdown(badge, unsafe_allow_html=True)
        st.write("")
        st.write(leitura)

        st.markdown(f"""
        <div class="metric-line"><span>Risco</span><b>{d["risco"]}</b></div>
        <div class="metric-line"><span>Liquidez</span><b>{d["liquidez"]}</b></div>
        <div class="metric-line"><span>Perfil</span><b>{d["perfil"]}</b></div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Fluxo Executivo</div>', unsafe_allow_html=True)

    df_show = df.copy()
    for col in ["Pagamento Mensal", "Total Investido", "Valor Projetado", "Lucro Bruto"]:
        df_show[col] = df_show[col].apply(moeda)
    df_show["ROI %"] = df_show["ROI %"].apply(pct)

    st.dataframe(df_show, use_container_width=True, height=380)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# CENÁRIOS
# =========================================================
elif menu == "Cenários":
    st.markdown("""
    <div class="hero">
        <h1>Cenários de Investimento</h1>
        <p>Simulação conservadora, base e agressiva para tomada de decisão.</p>
    </div>
    """, unsafe_allow_html=True)

    cenarios = []

    for nome, valorizacao in [
        ("Conservador", 8.0),
        ("Base", d["valorizacao_anual"]),
        ("Agressivo", 15.0)
    ]:
        temp = d.copy()
        temp["valorizacao_anual"] = valorizacao
        df_temp = criar_fluxo(temp)
        ent = df_temp[df_temp["Mês"] == int(temp["prazo_entrega"])].iloc[0]
        fim = df_temp.iloc[-1]

        cenarios.append({
            "Cenário": nome,
            "Valorização Anual": valorizacao,
            "Valor na Entrega": ent["Valor Projetado"],
            "Lucro na Entrega": ent["Lucro Bruto"],
            "ROI na Entrega": ent["ROI %"],
            "Valor Final": fim["Valor Projetado"],
            "Lucro Final": fim["Lucro Bruto"],
            "ROI Final": fim["ROI %"]
        })

    df_cenarios = pd.DataFrame(cenarios)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_barra(df_cenarios, "Cenário", "Lucro na Entrega", "Lucro na Entrega por Cenário"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_barra(df_cenarios, "Cenário", "ROI na Entrega", "ROI na Entrega por Cenário"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Tabela Comparativa</div>', unsafe_allow_html=True)

    df_view = df_cenarios.copy()
    for col in ["Valor na Entrega", "Lucro na Entrega", "Valor Final", "Lucro Final"]:
        df_view[col] = df_view[col].apply(moeda)

    for col in ["Valorização Anual", "ROI na Entrega", "ROI Final"]:
        df_view[col] = df_view[col].apply(pct)

    st.dataframe(df_view, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# RELATÓRIO PDF
# =========================================================
elif menu == "Relatório PDF":
    st.markdown("""
    <div class="hero">
        <h1>Relatório Executivo PDF</h1>
        <p>Resumo profissional para apresentar a investidores, sócios ou corretores.</p>
    </div>
    """, unsafe_allow_html=True)

    resumo = [
        "RELATORIO EXECUTIVO IMOBILIARIO",
        "",
        f"Empreendimento: {d['empreendimento']}",
        f"Construtora: {d['construtora']}",
        f"Localizacao: {d['localizacao']}",
        f"Unidade: {d['unidade']}",
        f"Tipo: {d['tipo']}",
        f"Area privativa: {d['area']} m2",
        f"Vagas: {d['vagas']}",
        "",
        f"Preco total: {moeda(preco_total)}",
        f"Valor por m2: {moeda(valor_m2)}",
        f"Referencia de mercado por m2: {moeda(d['valor_m2_ref'])}",
        "",
        f"Valorizacao anual considerada: {pct(d['valorizacao_anual'])}",
        f"CUB anual considerado: {pct(d['cub_anual'])}",
        f"Prazo ate entrega: {d['prazo_entrega']} meses",
        f"Prazo total analisado: {d['prazo_total']} meses",
        "",
        f"Investido ate entrega: {moeda(investido_entrega)}",
        f"Valor projetado na entrega: {moeda(valor_entrega)}",
        f"Lucro bruto na entrega: {moeda(lucro_entrega)}",
        f"ROI na entrega: {pct(roi_entrega)}",
        "",
        f"Valor final projetado: {moeda(valor_final)}",
        f"Total investido no prazo final: {moeda(investido_final)}",
        f"Lucro bruto final: {moeda(lucro_final)}",
        f"ROI final: {pct(roi_final)}",
        "",
        f"Score da oportunidade: {nota:.1f}/10",
        f"Risco: {d['risco']}",
        f"Liquidez: {d['liquidez']}",
        f"Perfil ideal: {d['perfil']}",
        "",
        "Conclusao:",
        "Esta analise considera fluxo de pagamento, valorizacao projetada, preco por metro quadrado, risco, liquidez e capital aportado.",
        "A decisao final deve considerar tambem qualidade da construtora, localizacao, documentacao, velocidade de venda e preco real praticado no mercado."
    ]

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("\n\n".join([f"**{x}**" if i == 0 else x for i, x in enumerate(resumo)]))
    st.markdown('</div>', unsafe_allow_html=True)

    pdf_bytes = gerar_pdf_relatorio(d, resumo)

    if pdf_bytes:
        st.download_button(
            "📄 Baixar Relatório PDF",
            data=pdf_bytes,
            file_name=f"relatorio_{d['empreendimento'].replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Para exportar PDF, adicione fpdf2 no requirements.txt.")
