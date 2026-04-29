import streamlit as st
import pandas as pd
import re
import pdfplumber
import plotly.graph_objects as go

st.set_page_config(page_title="Investidor Imobiliário Pro", layout="wide")

# =========================
# FUNÇÕES BASE
# =========================
def moeda(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def num(v):
    t = str(v).replace("R$", "")
    t = re.sub(r"[^\d,\.]", "", t)
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except:
        return 0

# =========================
# LEITURA REAL DO PDF
# =========================
def ler_pdf(file):
    texto = ""
    linhas = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texto += "\n" + t

            try:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        linha = " | ".join([str(c) for c in row if c])
                        if linha.strip():
                            linhas.append(linha)
            except:
                pass

    return texto, linhas

# =========================
# BUSCA INTELIGENTE POR APTO
# =========================
def buscar_unidade(texto, linhas, apto):
    apto = str(apto)

    todas = texto.splitlines() + linhas

    matches = []

    for i, l in enumerate(todas):
        if re.search(rf"\b{apto}\b", l):
            bloco = todas[max(0, i-2):i+3]
            matches.append(" ".join(bloco))

    if not matches:
        return None

    bloco = " ".join(matches)

    valores = [num(v) for v in re.findall(r"R\$\s*[\d\.\,]+", bloco)]
    areas = [num(a) for a in re.findall(r"(\d{2,3}(?:[\.,]\d+)?)\s*m", bloco.lower())]
    vagas = [int(v) for v in re.findall(r"(\d)\s*vaga", bloco.lower())]

    return {
        "unidade": apto,
        "preco_total": max(valores) if valores else 0,
        "area": areas[0] if areas else 0,
        "vagas": vagas[0] if vagas else 0,
        "trecho": bloco
    }

# =========================
# ESTADO
# =========================
if "dados" not in st.session_state:
    st.session_state.dados = {
        "unidade": "1201",
        "preco_total": 0,
        "area": 0,
        "vagas": 0
    }

if "pdf_texto" not in st.session_state:
    st.session_state.pdf_texto = ""

if "pdf_linhas" not in st.session_state:
    st.session_state.pdf_linhas = []

if "resultado_pdf" not in st.session_state:
    st.session_state.resultado_pdf = None

d = st.session_state.dados

# =========================
# MENU
# =========================
menu = st.sidebar.radio(
    "Menu",
    ["Importar PDF", "Painel Executivo"]
)

# =========================
# IMPORTAR PDF
# =========================
if menu == "Importar PDF":

    st.title("📄 Leitura de PDF por Apartamento")

    file = st.file_uploader("Enviar PDF da construtora")

    if file:
        texto, linhas = ler_pdf(file)
        st.session_state.pdf_texto = texto
        st.session_state.pdf_linhas = linhas
        st.success("PDF carregado")

    apto = st.text_input("Digite o número do apartamento")

    if st.button("Buscar unidade"):
        resultado = buscar_unidade(
            st.session_state.pdf_texto,
            st.session_state.pdf_linhas,
            apto
        )

        if resultado:
            st.session_state.resultado_pdf = resultado
            st.success("Unidade encontrada")
        else:
            st.error("Apartamento não encontrado")

    if st.session_state.resultado_pdf:
        r = st.session_state.resultado_pdf

        st.subheader("Dados encontrados")

        preco = st.number_input("Preço", value=float(r["preco_total"]))
        area = st.number_input("Área", value=float(r["area"]))
        vagas = st.number_input("Vagas", value=int(r["vagas"]))

        st.text_area("Trecho do PDF", r["trecho"], height=150)

        if st.button("Aplicar no painel"):
            d["preco_total"] = preco
            d["area"] = area
            d["vagas"] = vagas
            d["unidade"] = r["unidade"]
            st.session_state.dados = d
            st.success("Dados aplicados")

# =========================
# PAINEL
# =========================
elif menu == "Painel Executivo":

    st.title("📊 Painel Executivo")

    if d["preco_total"] == 0:
        st.warning("Importe um PDF primeiro")
    else:
        st.metric("Unidade", d["unidade"])
        st.metric("Preço", moeda(d["preco_total"]))
        st.metric("Área", f"{d['area']} m²")
        st.metric("Vagas", d["vagas"])

        valor_m2 = d["preco_total"] / d["area"] if d["area"] else 0
        st.metric("Valor por m²", moeda(valor_m2))

        df = pd.DataFrame({
            "Mes": list(range(1, 25)),
            "Valor": [d["preco_total"] * (1 + 0.01 * i) for i in range(24)]
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Mes"], y=df["Valor"]))
        st.plotly_chart(fig)
