import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

try:
    import pdfplumber
except:
    pdfplumber = None


st.set_page_config(
    page_title="Painel Executivo Imobiliário",
    page_icon="🏢",
    layout="wide"
)


# =========================
# CSS PROFISSIONAL
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #061936 0%, #031024 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.main {
    background: #f5f7fb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero-title {
    font-size: 36px;
    font-weight: 800;
    color: #081a3a;
    margin-bottom: 4px;
}

.hero-subtitle {
    font-size: 16px;
    color: #64748b;
    margin-bottom: 24px;
}

.kpi-card {
    background: white;
    padding: 24px;
    border-radius: 22px;
    box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
    border: 1px solid #e5eaf3;
    min-height: 150px;
}

.kpi-label {
    color: #64748b;
    font-size: 14px;
    font-weight: 600;
}

.kpi-value {
    color: #071735;
    font-size: 30px;
    font-weight: 800;
    margin-top: 10px;
}

.kpi-positive {
    color: #059669;
    font-size: 13px;
    font-weight: 600;
    margin-top: 8px;
}

.kpi-negative {
    color: #dc2626;
    font-size: 13px;
    font-weight: 600;
    margin-top: 8px;
}

.panel-card {
    background: white;
    padding: 24px;
    border-radius: 24px;
    box-shadow: 0 12px 35px rgba(15, 23, 42, 0.07);
    border: 1px solid #e5eaf3;
    margin-bottom: 20px;
}

.section-title {
    color: #081a3a;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 12px;
}

.badge-good {
    background: #dcfce7;
    color: #166534;
    padding: 8px 14px;
    border-radius: 999px;
    font-weight: 700;
    display: inline-block;
}

.badge-mid {
    background: #fef3c7;
    color: #92400e;
    padding: 8px 14px;
    border-radius: 999px;
    font-weight: 700;
    display: inline-block;
}

.badge-bad {
    background: #fee2e2;
    color: #991b1b;
    padding: 8px 14px;
    border-radius: 999px;
    font-weight: 700;
    display: inline-block;
}

.metric-line {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #edf2f7;
    padding: 10px 0;
    font-size: 15px;
}

.metric-line b {
    color: #0f172a;
}

.sidebar-logo {
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 4px;
}

.sidebar-sub {
    font-size: 12px;
    letter-spacing: 2px;
    color: #93c5fd !important;
    margin-bottom: 25px;
}

.stButton > button {
    background: linear-gradient(90deg, #2563eb, #4f46e5);
    color: white;
    border-radius: 14px;
    border: none;
    padding: 0.7rem 1.2rem;
    font-weight: 700;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #1d4ed8, #4338ca);
    color: white;
}
</style>
""", unsafe_allow_html=True)


# =========================
# FUNÇÕES
# =========================
def moeda(v):
    try:
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"


def pct(v):
    try:
        return f"{v:.2f}%".replace(".", ",")
    except:
        return "0,00%"


def numero_br(v):
    try:
        return f"{v:,.0f}".replace(",", ".")
    except:
        return "0"


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
    except:
        texto = ""
    return texto


def tentar_extrair_valores(texto):
    dados = {}

    valores = re.findall(r'R\$\s?[\d\.\,]+', texto)
    areas = re.findall(r'(\d{2,3}[\,\.]?\d*)\s?m²', texto.lower())

    if valores:
        nums = []
        for v in valores:
            limpo = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                nums.append(float(limpo))
            except:
                pass
        if nums:
            dados["preco_total"] = max(nums)

    if areas:
        try:
            dados["area"] = float(areas[0].replace(",", "."))
        except:
            pass

    aptos = re.findall(r'(apto|apartamento|unidade)\s?[:\-]?\s?(\d+)', texto.lower())
    if aptos:
        dados["unidade"] = aptos[0][1]

    return dados


def calcular_nota(roi_entrega, valor_m2, valor_m2_ref, risco, prazo_entrega):
    nota = 5

    if roi_entrega >= 60:
        nota += 2
    elif roi_entrega >= 35:
        nota += 1
    elif roi_entrega < 20:
        nota -= 1

    if valor_m2_ref > 0:
        desconto = (valor_m2_ref - valor_m2) / valor_m2_ref
        if desconto >= 0.15:
            nota += 1.5
        elif desconto >= 0.05:
            nota += 0.7
        elif desconto < -0.05:
            nota -= 1

    if risco == "Baixo":
        nota += 1
    elif risco == "Alto":
        nota -= 1.5

    if prazo_entrega <= 24:
        nota += 0.7
    elif prazo_entrega >= 60:
        nota -= 0.7

    return max(0, min(10, nota))


def grafico_linha(df, x, y, titulo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x],
        y=df[y],
        mode="lines+markers",
        fill="tozeroy",
        line=dict(width=4),
        marker=dict(size=8),
        name=titulo
    ))
    fig.update_layout(
        title=titulo,
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#0f172a"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )
    return fig


def grafico_barras(df, x, y, titulo):
    fig = px.bar(df, x=x, y=y, text_auto=True)
    fig.update_layout(
        title=titulo,
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#0f172a"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )
    return fig


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🏢 ImobInvest</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">ANÁLISE EXECUTIVA</div>', unsafe_allow_html=True)

    menu = st.radio(
        "Menu",
        [
            "Painel Executivo",
            "Cadastro do Imóvel",
            "Fluxo de Pagamento",
            "Comparativo",
            "Relatório"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Painel profissional para análise de oportunidades imobiliárias.")


# =========================
# ESTADO
# =========================
if "dados" not in st.session_state:
    st.session_state.dados = {
        "empreendimento": "Residencial Vista Mar",
        "localizacao": "Porto Belo / SC",
        "unidade": "1201",
        "tipo": "Apartamento",
        "area": 90.0,
        "vagas": 2,
        "preco_total": 1351000.0,
        "entrada": 120000.0,
        "parcelas_mensais": 48,
        "valor_parcela": 6500.0,
        "reforco_pre": 30000.0,
        "qtd_reforcos_pre": 4,
        "reforco_pos": 25000.0,
        "qtd_reforcos_pos": 6,
        "cub_anual": 4.3,
        "valorizacao_anual": 12.0,
        "valor_m2_ref": 17000.0,
        "prazo_entrega": 36,
        "risco": "Médio"
    }


dados = st.session_state.dados


# =========================
# CADASTRO
# =========================
if menu == "Cadastro do Imóvel":
    st.markdown('<div class="hero-title">Cadastro do Imóvel</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Alimente os dados manualmente ou envie um PDF da construtora.</div>', unsafe_allow_html=True)

    col_pdf, col_manual = st.columns([1, 2])

    with col_pdf:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Leitura de PDF</div>', unsafe_allow_html=True)
        arquivo = st.file_uploader("Enviar PDF da construtora", type=["pdf"])

        if arquivo:
            texto = extrair_texto_pdf(arquivo)
            extraidos = tentar_extrair_valores(texto)

            if extraidos:
                st.success("Algumas informações foram identificadas no PDF.")

                if "preco_total" in extraidos:
                    dados["preco_total"] = extraidos["preco_total"]

                if "area" in extraidos:
                    dados["area"] = extraidos["area"]

                if "unidade" in extraidos:
                    dados["unidade"] = extraidos["unidade"]

                st.session_state.dados = dados
            else:
                st.warning("Não consegui extrair dados suficientes automaticamente. Preencha manualmente ao lado.")

            with st.expander("Ver texto extraído"):
                st.text_area("Texto do PDF", texto, height=300)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_manual:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Dados principais</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            dados["empreendimento"] = st.text_input("Empreendimento", dados["empreendimento"])
            dados["localizacao"] = st.text_input("Localização", dados["localizacao"])
            dados["unidade"] = st.text_input("Unidade", dados["unidade"])

        with c2:
            dados["tipo"] = st.selectbox("Tipo", ["Apartamento", "Flat", "Terreno", "Casa", "Sala Comercial"], index=0)
            dados["area"] = st.number_input("Área privativa m²", min_value=1.0, value=float(dados["area"]))
            dados["vagas"] = st.number_input("Vagas", min_value=0, value=int(dados["vagas"]))

        with c3:
            dados["preco_total"] = st.number_input("Preço total", min_value=0.0, value=float(dados["preco_total"]), step=10000.0)
            dados["valor_m2_ref"] = st.number_input("Valor m² médio da região", min_value=0.0, value=float(dados["valor_m2_ref"]), step=500.0)
            dados["prazo_entrega"] = st.number_input("Prazo até entrega em meses", min_value=1, value=int(dados["prazo_entrega"]))

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Premissas de valorização</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            dados["valorizacao_anual"] = st.slider("Valorização anual estimada", 0.0, 30.0, float(dados["valorizacao_anual"]), 0.5)

        with c2:
            dados["cub_anual"] = st.slider("CUB anual estimado", 0.0, 15.0, float(dados["cub_anual"]), 0.1)

        with c3:
            dados["risco"] = st.selectbox("Risco percebido", ["Baixo", "Médio", "Alto"], index=["Baixo", "Médio", "Alto"].index(dados["risco"]))

        st.session_state.dados = dados
        st.success("Dados atualizados.")
        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# FLUXO
# =========================
elif menu == "Fluxo de Pagamento":
    st.markdown('<div class="hero-title">Fluxo de Pagamento</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Configure entrada, parcelas e reforços antes e depois da entrega.</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        dados["entrada"] = st.number_input("Entrada", min_value=0.0, value=float(dados["entrada"]), step=5000.0)
        dados["parcelas_mensais"] = st.number_input("Quantidade de parcelas mensais", min_value=1, value=int(dados["parcelas_mensais"]))

    with c2:
        dados["valor_parcela"] = st.number_input("Valor da parcela mensal", min_value=0.0, value=float(dados["valor_parcela"]), step=500.0)
        dados["reforco_pre"] = st.number_input("Valor do reforço antes da entrega", min_value=0.0, value=float(dados["reforco_pre"]), step=5000.0)

    with c3:
        dados["qtd_reforcos_pre"] = st.number_input("Qtd. reforços antes da entrega", min_value=0, value=int(dados["qtd_reforcos_pre"]))
        dados["reforco_pos"] = st.number_input("Valor do reforço depois da entrega", min_value=0.0, value=float(dados["reforco_pos"]), step=5000.0)
        dados["qtd_reforcos_pos"] = st.number_input("Qtd. reforços depois da entrega", min_value=0, value=int(dados["qtd_reforcos_pos"]))

    st.session_state.dados = dados
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# CÁLCULOS
# =========================
area = dados["area"]
preco_total = dados["preco_total"]
valor_m2 = preco_total / area if area > 0 else 0

meses = int(dados["prazo_entrega"])
valorizacao_mensal = (1 + dados["valorizacao_anual"] / 100) ** (1 / 12) - 1
cub_mensal = (1 + dados["cub_anual"] / 100) ** (1 / 12) - 1

valor_entrega = preco_total * ((1 + valorizacao_mensal) ** meses)

total_parcelas = 0
fluxo = []

for m in range(1, dados["parcelas_mensais"] + 1):
    parcela_corrigida = dados["valor_parcela"] * ((1 + cub_mensal) ** m)
    total_parcelas += parcela_corrigida

total_reforcos_pre = dados["reforco_pre"] * dados["qtd_reforcos_pre"]
total_reforcos_pos = dados["reforco_pos"] * dados["qtd_reforcos_pos"]

investido_ate_entrega = dados["entrada"]

for m in range(1, meses + 1):
    pagamento = 0

    if m <= dados["parcelas_mensais"]:
        pagamento += dados["valor_parcela"] * ((1 + cub_mensal) ** m)

    if dados["qtd_reforcos_pre"] > 0:
        intervalo = max(1, meses // dados["qtd_reforcos_pre"])
        if m % intervalo == 0 and m <= meses:
            pagamento += dados["reforco_pre"]

    investido_ate_entrega += pagamento

    valor_imovel_mes = preco_total * ((1 + valorizacao_mensal) ** m)

    fluxo.append({
        "Mês": m,
        "Valor do Imóvel": valor_imovel_mes,
        "Total Investido": investido_ate_entrega,
        "Lucro Bruto": valor_imovel_mes - investido_ate_entrega,
        "Pagamento Mensal": pagamento
    })

df_fluxo = pd.DataFrame(fluxo)

lucro_entrega = valor_entrega - investido_ate_entrega
roi_entrega = (lucro_entrega / investido_ate_entrega) * 100 if investido_ate_entrega > 0 else 0
media_mensal = investido_ate_entrega / meses if meses > 0 else 0

nota = calcular_nota(
    roi_entrega,
    valor_m2,
    dados["valor_m2_ref"],
    dados["risco"],
    dados["prazo_entrega"]
)


# =========================
# PAINEL EXECUTIVO
# =========================
if menu == "Painel Executivo":
    st.markdown('<div class="hero-title">Painel Executivo</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero-subtitle">Análise profissional do empreendimento <b>{dados["empreendimento"]}</b> — Unidade {dados["unidade"]}</div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Preço Total</div>
            <div class="kpi-value">{moeda(preco_total)}</div>
            <div class="kpi-positive">Valor de tabela</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Valor por m²</div>
            <div class="kpi-value">{moeda(valor_m2)}</div>
            <div class="kpi-positive">Referência: {moeda(dados["valor_m2_ref"])}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Valor Projetado na Entrega</div>
            <div class="kpi-value">{moeda(valor_entrega)}</div>
            <div class="kpi-positive">Valorização de {pct(dados["valorizacao_anual"])} ao ano</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Lucro Bruto Estimado</div>
            <div class="kpi-value">{moeda(lucro_entrega)}</div>
            <div class="kpi-positive">ROI: {pct(roi_entrega)}</div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        cor_badge = "kpi-positive" if nota >= 7 else "kpi-negative" if nota < 5 else "kpi-positive"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Nota da Oportunidade</div>
            <div class="kpi-value">{nota:.1f}/10</div>
            <div class="{cor_badge}">Análise estratégica</div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(grafico_linha(df_fluxo, "Mês", "Valor do Imóvel", "Evolução Projetada do Imóvel"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(grafico_linha(df_fluxo, "Mês", "Lucro Bruto", "Lucro Bruto Projetado"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4, c5 = st.columns([1, 1, 1])

    with c3:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Resumo do Ativo</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-line"><span>Empreendimento</span><b>{dados["empreendimento"]}</b></div>
        <div class="metric-line"><span>Localização</span><b>{dados["localizacao"]}</b></div>
        <div class="metric-line"><span>Unidade</span><b>{dados["unidade"]}</b></div>
        <div class="metric-line"><span>Tipo</span><b>{dados["tipo"]}</b></div>
        <div class="metric-line"><span>Área privativa</span><b>{dados["area"]} m²</b></div>
        <div class="metric-line"><span>Vagas</span><b>{dados["vagas"]}</b></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Indicadores Financeiros</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-line"><span>Total investido até entrega</span><b>{moeda(investido_ate_entrega)}</b></div>
        <div class="metric-line"><span>Média mensal investida</span><b>{moeda(media_mensal)}</b></div>
        <div class="metric-line"><span>Lucro bruto estimado</span><b>{moeda(lucro_entrega)}</b></div>
        <div class="metric-line"><span>ROI total</span><b>{pct(roi_entrega)}</b></div>
        <div class="metric-line"><span>Prazo até entrega</span><b>{meses} meses</b></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Diagnóstico Executivo</div>', unsafe_allow_html=True)

        if nota >= 8:
            badge = '<span class="badge-good">Excelente oportunidade</span>'
            texto = "O imóvel apresenta forte potencial de valorização em relação ao capital aportado."
        elif nota >= 6:
            badge = '<span class="badge-mid">Boa oportunidade</span>'
            texto = "A operação é interessante, mas depende da confirmação do mercado, fluxo e liquidez."
        else:
            badge = '<span class="badge-bad">Atenção elevada</span>'
            texto = "O negócio exige cautela. O retorno estimado pode não compensar o risco ou o fluxo."

        st.markdown(badge, unsafe_allow_html=True)
        st.write("")
        st.write(texto)

        st.markdown(f"""
        <div class="metric-line"><span>Risco</span><b>{dados["risco"]}</b></div>
        <div class="metric-line"><span>Perfil ideal</span><b>Revenda / Valorização</b></div>
        <div class="metric-line"><span>Estratégia</span><b>Comprar no fluxo e vender valorizado</b></div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Tabela Executiva do Fluxo</div>', unsafe_allow_html=True)
    st.dataframe(
        df_fluxo.style.format({
            "Valor do Imóvel": "R$ {:,.2f}",
            "Total Investido": "R$ {:,.2f}",
            "Lucro Bruto": "R$ {:,.2f}",
            "Pagamento Mensal": "R$ {:,.2f}"
        }),
        use_container_width=True,
        height=360
    )
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# COMPARATIVO
# =========================
elif menu == "Comparativo":
    st.markdown('<div class="hero-title">Comparativo de Cenários</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Compare cenários conservador, base e agressivo.</div>', unsafe_allow_html=True)

    cenarios = []

    for nome, val in [
        ("Conservador", 8),
        ("Base", dados["valorizacao_anual"]),
        ("Agressivo", 15)
    ]:
        vm = (1 + val / 100) ** (1 / 12) - 1
        vf = preco_total * ((1 + vm) ** meses)
        lucro = vf - investido_ate_entrega
        roi = lucro / investido_ate_entrega * 100 if investido_ate_entrega > 0 else 0

        cenarios.append({
            "Cenário": nome,
            "Valorização Anual": val,
            "Valor na Entrega": vf,
            "Lucro Bruto": lucro,
            "ROI": roi
        })

    df_cenarios = pd.DataFrame(cenarios)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(grafico_barras(df_cenarios, "Cenário", "Valor na Entrega", "Valor Projetado por Cenário"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(grafico_barras(df_cenarios, "Cenário", "ROI", "ROI por Cenário"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.dataframe(
        df_cenarios.style.format({
            "Valorização Anual": "{:.2f}%",
            "Valor na Entrega": "R$ {:,.2f}",
            "Lucro Bruto": "R$ {:,.2f}",
            "ROI": "{:.2f}%"
        }),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# RELATÓRIO
# =========================
elif menu == "Relatório":
    st.markdown('<div class="hero-title">Relatório Executivo</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Resumo pronto para apresentar a investidores.</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    st.markdown(f"""
# Relatório de Análise Imobiliária

## 1. Identificação do Ativo

**Empreendimento:** {dados["empreendimento"]}  
**Localização:** {dados["localizacao"]}  
**Unidade:** {dados["unidade"]}  
**Tipo:** {dados["tipo"]}  
**Área privativa:** {dados["area"]} m²  
**Vagas:** {dados["vagas"]}  

---

## 2. Dados Comerciais

**Preço total:** {moeda(preco_total)}  
**Valor por m²:** {moeda(valor_m2)}  
**Valor médio de referência da região:** {moeda(dados["valor_m2_ref"])}  
**Prazo até entrega:** {meses} meses  

---

## 3. Projeção Financeira

**Valorização anual considerada:** {pct(dados["valorizacao_anual"])}  
**Valor projetado na entrega:** {moeda(valor_entrega)}  
**Total investido até a entrega:** {moeda(investido_ate_entrega)}  
**Lucro bruto estimado:** {moeda(lucro_entrega)}  
**ROI total estimado:** {pct(roi_entrega)}  
**Aporte médio mensal:** {moeda(media_mensal)}  

---

## 4. Avaliação Estratégica

**Nota da oportunidade:** {nota:.1f}/10  
**Risco:** {dados["risco"]}  
**Perfil ideal:** Revenda com foco em valorização patrimonial.  

### Leitura executiva

O ativo apresenta uma relação entre capital aportado, valorização esperada e prazo de entrega que deve ser analisada principalmente pelo fluxo financeiro.  
Quanto menor o desencaixe até a entrega e maior a valorização projetada, maior tende a ser a eficiência do capital investido.

---

## 5. Conclusão

Esta operação é mais indicada para investidores que buscam ganho de capital através da valorização do imóvel durante o período de obra, aproveitando o parcelamento direto com a construtora e possível revenda futura.
""")

    st.markdown('</div>', unsafe_allow_html=True)
