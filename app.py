import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
from fpdf import FPDF
import plotly.graph_objects as go
import plotly.express as px

try:
    import pdfplumber
except Exception:
    pdfplumber = None


st.set_page_config(
    page_title="Investidor Imobiliário Pro",
    page_icon="🏢",
    layout="wide"
)


# ======================================================
# CSS
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #061936 0%, #020817 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.hero {
    background: linear-gradient(135deg, #061936 0%, #123a75 50%, #2563eb 100%);
    padding: 28px;
    border-radius: 28px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.22);
}

.hero h1 {
    font-size: 36px;
    font-weight: 900;
    margin-bottom: 6px;
}

.hero p {
    color: #dbeafe;
    font-size: 16px;
}

.kpi-card {
    background: white;
    padding: 22px;
    border-radius: 24px;
    border: 1px solid #e5eaf3;
    box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
    min-height: 145px;
}

.kpi-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
}

.kpi-value {
    color: #071735;
    font-size: 27px;
    font-weight: 900;
    margin-top: 10px;
}

.kpi-sub-good {
    color: #059669;
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

.kpi-sub-bad {
    color: #dc2626;
    font-size: 13px;
    font-weight: 700;
    margin-top: 8px;
}

.panel-card {
    background: white;
    padding: 24px;
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

.stButton > button {
    background: linear-gradient(90deg, #1d4ed8, #4f46e5);
    color: white;
    border: none;
    border-radius: 14px;
    padding: .7rem 1.2rem;
    font-weight: 800;
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #059669, #16a34a);
    color: white;
    border: none;
    border-radius: 14px;
    padding: .7rem 1.2rem;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)


# ======================================================
# FUNÇÕES
# ======================================================
def moeda(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def pct(v):
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"


def limpar_numero(valor):
    if valor is None:
        return 0.0

    txt = str(valor)
    txt = txt.replace("R$", "")
    txt = txt.replace("m²", "")
    txt = txt.replace("m2", "")
    txt = txt.strip()

    txt = re.sub(r"[^\d,\.]", "", txt)

    if txt.count(",") == 1:
        txt = txt.replace(".", "").replace(",", ".")
    elif txt.count(".") > 1:
        txt = txt.replace(".", "")

    try:
        return float(txt)
    except Exception:
        return 0.0


def ler_pdf(uploaded_file):
    texto = ""
    tabelas = []

    if pdfplumber is None:
        return texto, tabelas

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texto += "\n" + t

                try:
                    tabs = page.extract_tables()
                    for tab in tabs:
                        if tab:
                            tabelas.append(tab)
                except Exception:
                    pass
    except Exception:
        pass

    return texto, tabelas


def extrair_pdf_inteligente(texto, tabelas):
    candidatos = {
        "unidades": [],
        "areas": [],
        "valores": [],
        "entradas": [],
        "parcelas": [],
        "reforcos": [],
        "vagas": [],
        "linhas_tabela": []
    }

    texto_lower = texto.lower()

    unidades = re.findall(r"(?:apto|apartamento|unidade|unid)\s*[:\-]?\s*([a-zA-Z0-9\-]+)", texto_lower)
    candidatos["unidades"] = list(dict.fromkeys(unidades))

    areas = re.findall(r"(\d{2,3}(?:[\.,]\d{1,2})?)\s*(?:m²|m2|m\s²)", texto_lower)
    candidatos["areas"] = list(dict.fromkeys([limpar_numero(a) for a in areas if limpar_numero(a) > 10]))

    valores = re.findall(r"R\$\s*[\d\.\,]+", texto)
    nums = [limpar_numero(v) for v in valores]
    nums = [v for v in nums if v > 1000]
    candidatos["valores"] = sorted(list(dict.fromkeys(nums)), reverse=True)

    vagas = re.findall(r"(\d+)\s*(?:vaga|vagas)", texto_lower)
    candidatos["vagas"] = list(dict.fromkeys([int(v) for v in vagas if int(v) <= 6]))

    for tab in tabelas:
        for row in tab:
            linha = " | ".join([str(c) for c in row if c])
            if linha.strip():
                candidatos["linhas_tabela"].append(linha)

                if re.search(r"R\$\s*[\d\.\,]+", linha):
                    candidatos["valores"] += [limpar_numero(v) for v in re.findall(r"R\$\s*[\d\.\,]+", linha)]

                if re.search(r"\d{2,3}(?:[\.,]\d{1,2})?\s*(?:m²|m2)", linha.lower()):
                    candidatos["areas"] += [
                        limpar_numero(a)
                        for a in re.findall(r"(\d{2,3}(?:[\.,]\d{1,2})?)\s*(?:m²|m2)", linha.lower())
                    ]

    candidatos["valores"] = sorted(list(dict.fromkeys([v for v in candidatos["valores"] if v > 1000])), reverse=True)
    candidatos["areas"] = sorted(list(dict.fromkeys([v for v in candidatos["areas"] if v > 10])))

    sugestao = {}

    if candidatos["valores"]:
        sugestao["preco_total"] = max(candidatos["valores"])

    if candidatos["areas"]:
        sugestao["area"] = candidatos["areas"][0]

    if candidatos["unidades"]:
        sugestao["unidade"] = candidatos["unidades"][0].upper()

    if candidatos["vagas"]:
        sugestao["vagas"] = candidatos["vagas"][0]

    return candidatos, sugestao


def criar_fluxo(d):
    preco = float(d["preco_total"])
    entrada = float(d["entrada"])
    parcela = float(d["valor_parcela"])
    qtd_parcelas = int(d["qtd_parcelas"])
    prazo_entrega = int(d["prazo_entrega"])
    prazo_total = int(d["prazo_total"])

    cub_mensal = (1 + float(d["cub_anual"]) / 100) ** (1 / 12) - 1
    val_mensal = (1 + float(d["valorizacao_anual"]) / 100) ** (1 / 12) - 1

    reforcos_pre = d.get("reforcos_pre", [])
    reforcos_pos = d.get("reforcos_pos", [])

    total_investido = entrada
    linhas = []

    for mes in range(1, prazo_total + 1):
        pagamento = 0.0

        if mes <= qtd_parcelas:
            pagamento += parcela * ((1 + cub_mensal) ** mes)

        for r in reforcos_pre:
            intervalo = int(r["intervalo"])
            valor = float(r["valor"])
            if mes <= prazo_entrega and intervalo > 0 and mes % intervalo == 0:
                pagamento += valor

        for r in reforcos_pos:
            intervalo = int(r["intervalo"])
            valor = float(r["valor"])
            mes_pos = mes - prazo_entrega
            if mes > prazo_entrega and intervalo > 0 and mes_pos % intervalo == 0:
                pagamento += valor

        total_investido += pagamento
        valor_projetado = preco * ((1 + val_mensal) ** mes)
        lucro = valor_projetado - total_investido
        roi = (lucro / total_investido) * 100 if total_investido > 0 else 0

        linhas.append({
            "Mês": mes,
            "Fase": "Antes da entrega" if mes <= prazo_entrega else "Depois da entrega",
            "Pagamento Mensal": pagamento,
            "Total Investido": total_investido,
            "Valor Projetado": valor_projetado,
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

    ref = float(d["valor_m2_ref"])
    if ref > 0:
        desconto = (ref - valor_m2) / ref
        if desconto >= 0.20:
            nota += 1.5
        elif desconto >= 0.10:
            nota += 1.0
        elif desconto >= 0.03:
            nota += 0.4
        elif desconto < -0.08:
            nota -= 1.0

    if int(d["prazo_entrega"]) <= 24:
        nota += 0.8
    elif int(d["prazo_entrega"]) >= 60:
        nota -= 0.7

    if d["risco"] == "Baixo":
        nota += 0.9
    elif d["risco"] == "Alto":
        nota -= 1.2

    if investido_entrega > 0 and lucro_entrega / investido_entrega > 0.5:
        nota += 0.6

    return max(0, min(10, nota))


def grafico_linha(df, y, titulo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Mês"],
        y=df[y],
        mode="lines+markers",
        fill="tozeroy",
        line=dict(width=4),
        marker=dict(size=7)
    ))

    fig.update_layout(
        title=titulo,
        height=360,
        margin=dict(l=15, r=15, t=50, b=15),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#0f172a"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#e5e7eb")
    )

    return fig


def gerar_pdf(d, resumo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "Relatorio Executivo Imobiliario", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "", 11)

    for linha in resumo:
        pdf.multi_cell(0, 8, linha.encode("latin-1", "ignore").decode("latin-1"))

    return pdf.output(dest="S").encode("latin-1")


# ======================================================
# ESTADO FIXO
# ======================================================
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
        "cub_anual": 4.3,
        "valorizacao_anual": 12.0,
        "valor_m2_ref": 17000.0,
        "risco": "Médio",
        "liquidez": "Alta",
        "perfil": "Revenda com valorização",
        "reforcos_pre": [
            {"intervalo": 6, "valor": 30000.0},
            {"intervalo": 10, "valor": 50000.0}
        ],
        "reforcos_pos": [
            {"intervalo": 6, "valor": 25000.0},
            {"intervalo": 10, "valor": 40000.0}
        ]
    }

if "pdf_texto" not in st.session_state:
    st.session_state.pdf_texto = ""

if "pdf_tabelas" not in st.session_state:
    st.session_state.pdf_tabelas = []

if "pdf_candidatos" not in st.session_state:
    st.session_state.pdf_candidatos = {}

if "pdf_sugestao" not in st.session_state:
    st.session_state.pdf_sugestao = {}


d = st.session_state.dados


# ======================================================
# MENU
# ======================================================
with st.sidebar:
    st.markdown("## 🏢 ImobInvest Pro")
    st.caption("PAINEL EXECUTIVO")

    menu = st.radio(
        "Menu",
        [
            "Painel Executivo",
            "Importar PDF",
            "Cadastro Manual",
            "Fluxo de Pagamento",
            "Cenários",
            "Relatório PDF"
        ],
        label_visibility="collapsed"
    )


# ======================================================
# IMPORTAR PDF
# ======================================================
if menu == "Importar PDF":
    st.markdown("""
    <div class="hero">
        <h1>Importar PDF da Construtora</h1>
        <p>O app lê o PDF, mostra os dados encontrados e você confirma quais informações quer aplicar.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    arquivo = st.file_uploader("Enviar PDF", type=["pdf"])

    if arquivo:
        texto, tabelas = ler_pdf(arquivo)
        candidatos, sugestao = extrair_pdf_inteligente(texto, tabelas)

        st.session_state.pdf_texto = texto
        st.session_state.pdf_tabelas = tabelas
        st.session_state.pdf_candidatos = candidatos
        st.session_state.pdf_sugestao = sugestao

        st.success("PDF lido e salvo na memória do app. Agora você pode trocar de aba sem perder os dados.")

    if st.session_state.pdf_sugestao:
        st.markdown("### Dados sugeridos pelo PDF")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            preco_pdf = st.number_input(
                "Preço total encontrado",
                value=float(st.session_state.pdf_sugestao.get("preco_total", d["preco_total"])),
                step=10000.0
            )

        with c2:
            area_pdf = st.number_input(
                "Área encontrada",
                value=float(st.session_state.pdf_sugestao.get("area", d["area"])),
                step=1.0
            )

        with c3:
            unidade_pdf = st.text_input(
                "Unidade encontrada",
                value=str(st.session_state.pdf_sugestao.get("unidade", d["unidade"]))
            )

        with c4:
            vagas_pdf = st.number_input(
                "Vagas encontradas",
                value=int(st.session_state.pdf_sugestao.get("vagas", d["vagas"])),
                min_value=0
            )

        if st.button("Aplicar dados do PDF no cadastro"):
            d["preco_total"] = preco_pdf
            d["area"] = area_pdf
            d["unidade"] = unidade_pdf
            d["vagas"] = vagas_pdf
            st.session_state.dados = d
            st.success("Dados aplicados. Agora pode ir para Painel Executivo ou Fluxo de Pagamento.")

    if st.session_state.pdf_candidatos:
        with st.expander("Ver todos os candidatos encontrados"):
            st.write(st.session_state.pdf_candidatos)

    if st.session_state.pdf_texto:
        with st.expander("Ver texto extraído do PDF"):
            st.text_area("Texto extraído", st.session_state.pdf_texto, height=350)

    st.markdown('</div>', unsafe_allow_html=True)


# ======================================================
# CADASTRO MANUAL
# ======================================================
elif menu == "Cadastro Manual":
    st.markdown("""
    <div class="hero">
        <h1>Cadastro Manual</h1>
        <p>Todos os dados ficam salvos durante a navegação entre as abas.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Dados do imóvel</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        d["empreendimento"] = st.text_input("Empreendimento", d["empreendimento"])
        d["construtora"] = st.text_input("Construtora", d["construtora"])
        d["localizacao"] = st.text_input("Localização", d["localizacao"])

    with c2:
        d["unidade"] = st.text_input("Unidade", d["unidade"])
        d["tipo"] = st.selectbox(
            "Tipo",
            ["Apartamento", "Flat", "Casa", "Terreno", "Sala Comercial"],
            index=["Apartamento", "Flat", "Casa", "Terreno", "Sala Comercial"].index(d["tipo"])
        )
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

    d["perfil"] = st.text_input("Perfil ideal", d["perfil"])

    st.session_state.dados = d
    st.success("Cadastro salvo.")
    st.markdown('</div>', unsafe_allow_html=True)


# ======================================================
# FLUXO
# ======================================================
elif menu == "Fluxo de Pagamento":
    st.markdown("""
    <div class="hero">
        <h1>Fluxo de Pagamento</h1>
        <p>Cadastre parcelas e reforços variáveis antes e depois da entrega.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        d["entrada"] = st.number_input("Entrada", value=float(d["entrada"]), step=5000.0)

    with c2:
        d["qtd_parcelas"] = st.number_input("Quantidade de parcelas", min_value=1, value=int(d["qtd_parcelas"]))

    with c3:
        d["valor_parcela"] = st.number_input("Valor da parcela", value=float(d["valor_parcela"]), step=500.0)

    with c4:
        d["prazo_entrega"] = st.number_input("Meses até entrega", min_value=1, value=int(d["prazo_entrega"]))

    d["prazo_total"] = st.number_input(
        "Prazo total analisado em meses",
        min_value=int(d["prazo_entrega"]),
        value=max(int(d["prazo_total"]), int(d["prazo_entrega"]))
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Reforços antes da entrega</div>', unsafe_allow_html=True)

    qtd_pre = st.number_input("Quantidade de tipos de reforço antes da entrega", min_value=0, max_value=10, value=len(d["reforcos_pre"]))

    novos_pre = []

    for i in range(qtd_pre):
        c1, c2 = st.columns(2)

        base = d["reforcos_pre"][i] if i < len(d["reforcos_pre"]) else {"intervalo": 6, "valor": 0.0}

        with c1:
            intervalo = st.number_input(f"Reforço antes #{i+1} - repetir a cada X meses", min_value=1, value=int(base["intervalo"]), key=f"pre_int_{i}")

        with c2:
            valor = st.number_input(f"Reforço antes #{i+1} - valor", min_value=0.0, value=float(base["valor"]), step=5000.0, key=f"pre_val_{i}")

        novos_pre.append({"intervalo": intervalo, "valor": valor})

    d["reforcos_pre"] = novos_pre

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Reforços depois da entrega</div>', unsafe_allow_html=True)

    qtd_pos = st.number_input("Quantidade de tipos de reforço depois da entrega", min_value=0, max_value=10, value=len(d["reforcos_pos"]))

    novos_pos = []

    for i in range(qtd_pos):
        c1, c2 = st.columns(2)

        base = d["reforcos_pos"][i] if i < len(d["reforcos_pos"]) else {"intervalo": 6, "valor": 0.0}

        with c1:
            intervalo = st.number_input(f"Reforço depois #{i+1} - repetir a cada X meses", min_value=1, value=int(base["intervalo"]), key=f"pos_int_{i}")

        with c2:
            valor = st.number_input(f"Reforço depois #{i+1} - valor", min_value=0.0, value=float(base["valor"]), step=5000.0, key=f"pos_val_{i}")

        novos_pos.append({"intervalo": intervalo, "valor": valor})

    d["reforcos_pos"] = novos_pos

    st.session_state.dados = d
    st.success("Fluxo salvo. Pode trocar de aba sem perder.")
    st.markdown('</div>', unsafe_allow_html=True)


# ======================================================
# CÁLCULOS
# ======================================================
df = criar_fluxo(d)

valor_m2 = float(d["preco_total"]) / float(d["area"]) if float(d["area"]) > 0 else 0

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

media_mensal = investido_entrega / int(d["prazo_entrega"])
nota = calcular_score(d, valor_m2, roi_entrega, lucro_entrega, investido_entrega)


# ======================================================
# PAINEL
# ======================================================
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
            <div class="kpi-value">{moeda(d["preco_total"])}</div>
            <div class="kpi-sub-mid">Base de compra</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Valor por m²</div>
            <div class="kpi-value">{moeda(valor_m2)}</div>
            <div class="kpi-sub-good">Ref.: {moeda(d["valor_m2_ref"])}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Valor na Entrega</div>
            <div class="kpi-value">{moeda(valor_entrega)}</div>
            <div class="kpi-sub-good">{pct(d["valorizacao_anual"])} ao ano</div>
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
        classe = "kpi-sub-good" if nota >= 7 else "kpi-sub-mid" if nota >= 5 else "kpi-sub-bad"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Score</div>
            <div class="kpi-value">{nota:.1f}/10</div>
            <div class="{classe}">Nota executiva</div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(grafico_linha(df, "Valor Projetado", "Evolução Projetada do Imóvel"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.plotly_chart(grafico_linha(df, "Lucro Bruto", "Lucro Bruto Projetado"), use_container_width=True)
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
        <div class="metric-line"><span>Aporte médio mensal</span><b>{moeda(media_mensal)}</b></div>
        <div class="metric-line"><span>Valor final projetado</span><b>{moeda(valor_final)}</b></div>
        <div class="metric-line"><span>Lucro final</span><b>{moeda(lucro_final)}</b></div>
        <div class="metric-line"><span>ROI final</span><b>{pct(roi_final)}</b></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Diagnóstico</div>', unsafe_allow_html=True)

        if nota >= 8:
            st.markdown('<span class="badge-good">Excelente oportunidade</span>', unsafe_allow_html=True)
            st.write("Operação forte, com boa relação entre aporte e valorização.")
        elif nota >= 6:
            st.markdown('<span class="badge-mid">Boa oportunidade</span>', unsafe_allow_html=True)
            st.write("Operação interessante, mas depende de liquidez, preço real de revenda e construtora.")
        else:
            st.markdown('<span class="badge-bad">Cautela</span>', unsafe_allow_html=True)
            st.write("O retorno pode não compensar o risco, prazo ou fluxo exigido.")

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


# ======================================================
# CENÁRIOS
# ======================================================
elif menu == "Cenários":
    st.markdown("""
    <div class="hero">
        <h1>Cenários</h1>
        <p>Compare cenário conservador, base e agressivo.</p>
    </div>
    """, unsafe_allow_html=True)

    cenarios = []

    for nome, valorizacao in [
        ("Conservador", 8.0),
        ("Base", float(d["valorizacao_anual"])),
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
        fig = px.bar(df_cenarios, x="Cenário", y="Lucro na Entrega", text_auto=".2s")
        fig.update_layout(height=360, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(df_cenarios, x="Cenário", y="ROI na Entrega", text_auto=".2s")
        fig.update_layout(height=360, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    df_view = df_cenarios.copy()
    for col in ["Valor na Entrega", "Lucro na Entrega", "Valor Final", "Lucro Final"]:
        df_view[col] = df_view[col].apply(moeda)

    for col in ["Valorização Anual", "ROI na Entrega", "ROI Final"]:
        df_view[col] = df_view[col].apply(pct)

    st.dataframe(df_view, use_container_width=True)


# ======================================================
# RELATÓRIO
# ======================================================
elif menu == "Relatório PDF":
    st.markdown("""
    <div class="hero">
        <h1>Relatório PDF</h1>
        <p>Resumo profissional da análise para apresentar a investidores.</p>
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
        f"Preco total: {moeda(d['preco_total'])}",
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
        "A analise considera fluxo de pagamento, valorizacao projetada, preco por metro quadrado, risco, liquidez e capital aportado.",
        "A decisao final deve considerar qualidade da construtora, documentacao, velocidade de venda e preco real praticado no mercado."
    ]

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("\n\n".join(resumo))
    st.markdown('</div>', unsafe_allow_html=True)

    pdf_bytes = gerar_pdf(d, resumo)

    st.download_button(
        "📄 Baixar relatório PDF",
        data=pdf_bytes,
        file_name="relatorio_imobiliario.pdf",
        mime="application/pdf"
    )
