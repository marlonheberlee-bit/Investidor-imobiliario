import streamlit as st
import pandas as pd

st.set_page_config(page_title="Investidor Imobiliário PRO", layout="wide")

# =============================
# FUNÇÕES
# =============================

def moeda(v):
    return f"R$ {v:,.0f}".replace(",", ".")

def percentual(v):
    return f"{v:.2f}%".replace(".", ",")

def ler_reforcos(texto):
    reforcos = {}
    for linha in texto.splitlines():
        linha = linha.strip()
        if "=" in linha:
            try:
                mes, valor = linha.split("=")
                reforcos[int(mes.strip())] = float(valor.strip().replace(",", "."))
            except:
                pass
    return reforcos

# =============================
# SIDEBAR
# =============================

st.sidebar.header("Parâmetros")

valor_imovel = st.sidebar.number_input("Valor do imóvel", value=1300000.0)
entrada = st.sidebar.number_input("Entrada", value=25000.0)
parcela = st.sidebar.number_input("Parcela mensal", value=2500.0)
prazo = st.sidebar.number_input("Prazo (meses)", value=120)
mes_entrega = st.sidebar.number_input("Mês de entrega", value=48)

valorizacao = st.sidebar.slider("Valorização anual (%)", 0.0, 30.0, 15.0) / 100
cub = st.sidebar.slider("CUB anual (%)", 0.0, 15.0, 4.3) / 100

st.sidebar.subheader("📌 Reforços antes da entrega")
reforcos_antes_texto = st.sidebar.text_area(
    "",
    value="12=10000\n24=10000\n36=10000\n48=50000"
)

st.sidebar.subheader("🏗️ Reforços depois da entrega")
reforcos_depois_texto = st.sidebar.text_area(
    "",
    value="60=15000\n72=15000"
)

ref_antes = ler_reforcos(reforcos_antes_texto)
ref_depois = ler_reforcos(reforcos_depois_texto)

# =============================
# CÁLCULO
# =============================

dados = []
aporte_total = 0

for mes in range(1, int(prazo)+1):

    reajuste = (1 + cub) ** (mes/12)
    parcela_corr = parcela * reajuste

    reforco_antes = ref_antes.get(mes, 0) * reajuste
    reforco_depois = ref_depois.get(mes, 0) * reajuste
    reforco_total = reforco_antes + reforco_depois

    aporte_mes = parcela_corr + reforco_total
    if mes == 1:
        aporte_mes += entrada

    aporte_total += aporte_mes

    valor = valor_imovel * ((1 + valorizacao) ** (mes/12))
    lucro = valor - valor_imovel
    retorno = aporte_total + lucro

    dados.append([
        mes,
        aporte_total,
        valor,
        retorno
    ])

df = pd.DataFrame(dados, columns=["Mes","Aporte","Valor","Retorno"])
final = df.iloc[-1]

lucro_final = final["Valor"] - valor_imovel
roi = (lucro_final / final["Aporte"]) * 100
multiplo = final["Retorno"] / final["Aporte"]

# =============================
# CLASSIFICAÇÃO
# =============================

if roi > 150:
    classificacao = "EXCELENTE"
elif roi > 80:
    classificacao = "BOM"
else:
    classificacao = "MÉDIO"

# =============================
# UI PROFISSIONAL
# =============================

st.title("Investidor Imobiliário PRO")

colA, colB = st.columns([1,3])

# CLASSIFICAÇÃO
with colA:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d3bff,#1d4ed8);
                padding:30px;border-radius:20px;color:white">
        <h4>CLASSIFICAÇÃO</h4>
        <h1>{classificacao}</h1>
        <p>ROI: {percentual(roi)}</p>
    </div>
    """, unsafe_allow_html=True)

# CARDS
with colB:

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Investido no fluxo", moeda(final["Aporte"]))
    c2.metric("Dinheiro na mão", moeda(final["Retorno"]))
    c3.metric("Lucro real", moeda(lucro_final))
    c4.metric("ROI real", percentual(roi))

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Valor inicial", moeda(valor_imovel))
    c6.metric("Valor projetado", moeda(final["Valor"]))
    c7.metric("Valorização", percentual((final["Valor"]/valor_imovel-1)*100))
    c8.metric("Fluxo médio", moeda(final["Aporte"]/prazo))

st.subheader("Fluxo")

df_show = df.copy()
df_show["Aporte"] = df_show["Aporte"].apply(moeda)
df_show["Valor"] = df_show["Valor"].apply(moeda)
df_show["Retorno"] = df_show["Retorno"].apply(moeda)

st.dataframe(df_show)
