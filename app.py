import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Investidor Imobiliário PRO",
    page_icon="🏢",
    layout="wide"
)

# =====================================================
# CSS - VISUAL EXECUTIVO IGUAL AO MODELO PROFISSIONAL
# =====================================================

st.markdown("""
<style>
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    background: #f1f5f9;
}

.hero {
    background: linear-gradient(135deg, #111827 0%, #1f2937 60%, #374151 100%);
    padding: 30px 36px;
    border-radius: 0 0 24px 24px;
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 10px 28px rgba(0,0,0,.16);
}
.hero h1 {
    margin: 0;
    font-size: 36px;
    font-weight: 900;
}
.hero p {
    margin-top: 10px;
    color: #d1d5db;
    font-size: 16px;
}

.class-card {
    background: linear-gradient(145deg, #073ec7, #0057ff);
    border-radius: 22px;
    padding: 30px;
    color: white;
    min-height: 420px;
    box-shadow: 0 14px 35px rgba(37, 99, 235, 0.25);
}
.class-label {
    font-size: 15px;
    font-weight: 800;
    letter-spacing: .5px;
}
.class-grade {
    font-size: 56px;
    font-weight: 900;
    line-height: .98;
    margin: 26px 0 18px 0;
}
.class-score {
    display: inline-block;
    background: rgba(15, 23, 42, 0.25);
    padding: 10px 18px;
    border-radius: 999px;
    font-size: 20px;
    font-weight: 900;
}
.quick-box {
    margin-top: 28px;
    background: rgba(15, 23, 42, 0.22);
    padding: 20px;
    border-radius: 16px;
    line-height: 1.55;
}
.quick-title {
    font-size: 17px;
    font-weight: 900;
    margin-bottom: 12px;
}

.metric-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 24px 18px;
    text-align: center;
    min-height: 205px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    margin-bottom: 14px;
    overflow: hidden;
}
.metric-title {
    font-size: 15px;
    font-weight: 900;
    color: #0f172a;
    margin-bottom: 12px;
}
.metric-icon {
    width: 58px;
    height: 58px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 14px auto;
    font-size: 29px;
    background: #dbeafe;
}
.metric-icon.green-bg { background: #dcfce7; }
.metric-icon.purple-bg { background: #ede9fe; }
.metric-icon.orange-bg { background: #ffedd5; }
.metric-value {
    font-size: 28px;
    font-weight: 900;
    line-height: 1.1;
    white-space: nowrap;
}
.metric-sub {
    margin-top: 8px;
    color: #64748b;
    font-size: 13px;
}
.metric-pill {
    display: inline-block;
    margin-top: 10px;
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 800;
}
.blue { color: #0b4ad9; }
.green { color: #087a20; }
.purple { color: #5b21b6; }
.orange { color: #ea580c; }
.pill-blue { background: #dbeafe; color: #0b4ad9; }
.pill-green { background: #dcfce7; color: #087a20; }
.pill-purple { background: #ede9fe; color: #5b21b6; }
.pill-orange { background: #ffedd5; color: #ea580c; }

.section-box {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 22px;
    margin-top: 16px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}
.section-title {
    color: #0b4ad9;
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 2px;
}
.section-subtitle {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 16px;
}

.summary-box {
    background: linear-gradient(90deg, #f0fdf4, #ffffff);
    border: 1px solid #86efac;
    border-radius: 18px;
    padding: 24px;
    margin-top: 20px;
    display: grid;
    grid-template-columns: 1.8fr 1fr 1fr 1fr 1fr;
    gap: 14px;
    align-items: center;
}
.summary-title {
    color: #087a20;
    font-size: 17px;
    font-weight: 900;
    margin-bottom: 8px;
}
.summary-text {
    font-size: 15px;
    line-height: 1.55;
    color: #0f172a;
}
.summary-metric {
    text-align: center;
    border-left: 1px solid #d1fae5;
    padding-left: 12px;
}
.summary-value {
    color: #087a20;
    font-size: 24px;
    font-weight: 900;
    white-space: nowrap;
}
.summary-label {
    color: #475569;
    font-size: 13px;
    margin-top: 6px;
}
.notice {
    margin-top: 18px;
    padding: 12px 16px;
    border-radius: 12px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #334155;
    font-size: 13px;
}

@media (max-width: 1100px) {
    .summary-box { grid-template-columns: 1fr; }
    .summary-metric { border-left: none; border-top: 1px solid #d1fae5; padding-top: 12px; }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÕES
# =====================================================

def moeda(valor):
    try:
        return f"R$ {float(valor):,.0f}".replace(",", ".")
    except Exception:
        return "R$ 0"


def percentual(valor):
    try:
        return f"{float(valor):.2f}%".replace(".", ",")
    except Exception:
        return "0,00%"


def ler_reforcos(texto):
    reforcos = {}
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or "=" not in linha:
            continue
        try:
            mes_txt, valor_txt = linha.split("=", 1)
            mes = int(mes_txt.strip())
            valor = float(valor_txt.strip().replace(".", "").replace(",", "."))
            if mes > 0 and valor >= 0:
                reforcos[mes] = valor
        except Exception:
            pass
    return reforcos


def calcular_nota(roi_total, multiplo_capital, aporte_sobre_valor, anos_entrega):
    nota = 0
    if roi_total >= 100:
        nota += 30
    elif roi_total >= 70:
        nota += 25
    elif roi_total >= 50:
        nota += 20
    elif roi_total >= 30:
        nota += 13
    elif roi_total >= 15:
        nota += 8

    if multiplo_capital >= 2.0:
        nota += 30
    elif multiplo_capital >= 1.7:
        nota += 25
    elif multiplo_capital >= 1.4:
        nota += 20
    elif multiplo_capital >= 1.2:
        nota += 12
    elif multiplo_capital >= 1.0:
        nota += 7

    if aporte_sobre_valor <= 35:
        nota += 20
    elif aporte_sobre_valor <= 50:
        nota += 15
    elif aporte_sobre_valor <= 70:
        nota += 10
    else:
        nota += 5

    if anos_entrega <= 2:
        nota += 20
    elif anos_entrega <= 3:
        nota += 15
    elif anos_entrega <= 5:
        nota += 10
    else:
        nota += 5

    return min(round(nota), 100)


def classificar(nota):
    if nota >= 85:
        return "EXCELENTE"
    if nota >= 70:
        return "BOM"
    if nota >= 55:
        return "ACEITÁVEL"
    return "FRACO"


def leitura_rapida(nota):
    if nota >= 85:
        return "Excelente potencial de retorno com boa multiplicação do capital e relação risco/retorno atrativa."
    if nota >= 70:
        return "Bom potencial de retorno, com capital bem aproveitado e resultado projetado interessante."
    if nota >= 55:
        return "Operação aceitável, mas exige atenção ao fluxo, prazo, reajustes e valorização real."
    return "Operação fraca ou arriscada. O retorno projetado pode não compensar o capital imobilizado."


def card(titulo, icone, valor, subtitulo, pill, cor="blue", fundo=""):
    bg_class = f" {fundo}" if fundo else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{titulo}</div>
        <div class="metric-icon{bg_class}">{icone}</div>
        <div class="metric-value {cor}">{valor}</div>
        <div class="metric-sub">{subtitulo}</div>
        <div class="metric-pill pill-{cor}">{pill}</div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# CABEÇALHO
# =====================================================

st.markdown("""
<div class="hero">
    <h1>🏢 Investidor Imobiliário PRO</h1>
    <p>Simulador profissional de saída: fluxo, CUB/INCC, valorização, dinheiro na mão, lucro real e ponto ideal de venda.</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("⚙️ Parâmetros")

valor_imovel = st.sidebar.number_input("Valor atual do imóvel", min_value=0.0, value=1300000.0, step=10000.0)
entrada = st.sidebar.number_input("Entrada / sinal", min_value=0.0, value=25000.0, step=5000.0)
parcela_mensal = st.sidebar.number_input("Parcela mensal inicial", min_value=0.0, value=2500.0, step=500.0)
prazo_meses = st.sidebar.number_input("Prazo total em meses", min_value=1, value=120, step=1)
mes_entrega = st.sidebar.number_input("Mês de entrega do empreendimento", min_value=1, value=48, step=1)

st.sidebar.subheader("📌 Reforços antes da entrega")
reforcos_antes_texto = st.sidebar.text_area(
    "Antes da entrega — formato: mês=valor",
    value="12=10000
24=10000
36=10000
48=50000",
    height=120,
    help="Exemplo: 24=10000 significa reforço de R$ 10.000 no mês 24, antes ou no mês da entrega."
)

st.sidebar.subheader("🏗️ Reforços depois da entrega")
reforcos_depois_texto = st.sidebar.text_area(
    "Depois da entrega — formato: mês=valor",
    value="60=15000
72=15000",
    height=100,
    help="Exemplo: 60=15000 significa reforço de R$ 15.000 no mês 60, depois da entrega."
)

valorizacao_anual = st.sidebar.slider("Valorização anual estimada", 0.0, 30.0, 15.0, 0.5) / 100
cub_anual = st.sidebar.slider("CUB/INCC anual estimado", 0.0, 15.0, 4.3, 0.1) / 100
anos_analise = st.sidebar.slider("Anos para análise", 1, 10, 5)
metragem = st.sidebar.number_input("Metragem privativa m²", min_value=1.0, value=90.0, step=1.0)

reforcos_antes_dict = ler_reforcos(reforcos_antes_texto)
reforcos_depois_dict = ler_reforcos(reforcos_depois_texto)
reforcos_dict = {**reforcos_antes_dict, **reforcos_depois_dict}
anos_entrega = max(mes_entrega / 12, 1)
valor_m2 = valor_imovel / metragem if metragem > 0 else 0

# =====================================================
# CÁLCULOS
# =====================================================

linhas_mes = []
linhas_ano = []

for mes in range(1, int(prazo_meses) + 1):
    ano_corrente = ((mes - 1) // 12) + 1
    reajuste = (1 + cub_anual) ** ((mes - 1) / 12)
    parcela_corrigida = parcela_mensal * reajuste
    reforco_antes = reforcos_antes_dict.get(mes, 0) * reajuste
    reforco_depois = reforcos_depois_dict.get(mes, 0) * reajuste
    reforco = reforco_antes + reforco_depois

    aporte_mes = parcela_corrigida + reforco
    if mes == 1:
        aporte_mes += entrada

    aporte_acumulado = sum([x["Aporte do mês"] for x in linhas_mes]) + aporte_mes
    valor_estimado = valor_imovel * ((1 + valorizacao_anual) ** (mes / 12))
    lucro = valor_estimado - valor_imovel
    dinheiro_mao = aporte_acumulado + lucro
    roi = (lucro / aporte_acumulado) * 100 if aporte_acumulado > 0 else 0
    multiplo = dinheiro_mao / aporte_acumulado if aporte_acumulado > 0 else 0

    linhas_mes.append({
        "Mês": mes,
        "Ano": ano_corrente,
        "Parcela corrigida": parcela_corrigida,
        "Reforço antes da entrega": reforco_antes,
        "Reforço depois da entrega": reforco_depois,
        "Reforço total": reforco,
        "Aporte do mês": aporte_mes,
        "Aporte acumulado": aporte_acumulado,
        "Valor estimado do imóvel": valor_estimado,
        "Lucro bruto": lucro,
        "💰 Dinheiro na mão": dinheiro_mao,
        "Múltiplo": multiplo,
        "ROI": roi
    })

for ano in range(1, anos_analise + 1):
    meses_ate_ano = min(ano * 12, int(prazo_meses))
    dados_ate_ano = [x for x in linhas_mes if x["Mês"] <= meses_ate_ano]
    dados_do_ano = [x for x in linhas_mes if x["Ano"] == ano]
    if not dados_ate_ano:
        continue
    ultimo = dados_ate_ano[-1]
    linhas_ano.append({
        "Ano": ano,
        "Aporte no ano": sum([x["Aporte do mês"] for x in dados_do_ano]),
        "Reforços antes da entrega": sum([x["Reforço antes da entrega"] for x in dados_do_ano]),
        "Reforços depois da entrega": sum([x["Reforço depois da entrega"] for x in dados_do_ano]),
        "Reforços totais": sum([x["Reforço total"] for x in dados_do_ano]),
        "Aporte acumulado": ultimo["Aporte acumulado"],
        "Valor estimado do imóvel": ultimo["Valor estimado do imóvel"],
        "Lucro bruto": ultimo["Lucro bruto"],
        "💰 Retorno total na venda": ultimo["💰 Dinheiro na mão"],
        "Múltiplo do capital": ultimo["Múltiplo"],
        "ROI acumulado": ultimo["ROI"]
    })

df_mes = pd.DataFrame(linhas_mes)
df_ano = pd.DataFrame(linhas_ano)

ultimo = df_ano.iloc[-1]
aporte_final = ultimo["Aporte acumulado"]
valor_final = ultimo["Valor estimado do imóvel"]
lucro_final = ultimo["Lucro bruto"]
dinheiro_mao_final = ultimo["💰 Retorno total na venda"]
roi_final = ultimo["ROI acumulado"]
multiplo_final = ultimo["Múltiplo do capital"]
valorizacao_total = ((valor_final / valor_imovel) - 1) * 100 if valor_imovel > 0 else 0
aporte_sobre_valor = (aporte_final / valor_imovel) * 100 if valor_imovel > 0 else 0
fluxo_medio_mes = aporte_final / max(anos_analise * 12, 1)
nota = calcular_nota(roi_final, multiplo_final, aporte_sobre_valor, anos_entrega)
classificacao = classificar(nota)

# =====================================================
# ABAS REAIS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Painel executivo",
    "📆 Fluxo mensal",
    "🗓️ Ano a ano",
    "✅ Critérios",
    "📝 Dados variáveis"
])

with tab1:
    col_class, col_cards = st.columns([1.05, 2.95])

    with col_class:
        st.markdown(f"""
        <div class="class-card">
            <div class="class-label">CLASSIFICAÇÃO</div>
            <div class="class-grade">{classificacao}</div>
            <div class="class-score">Nota: {nota}/100</div>
            <div class="quick-box">
                <div class="quick-title">💡 Leitura rápida</div>
                {leitura_rapida(nota)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_cards:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            card("Investido no fluxo", "$", moeda(aporte_final), "Total aportado", "Capital imobilizado", "blue")
        with c2:
            card("Dinheiro na mão", "💰", moeda(dinheiro_mao_final), "Retorno total na venda", f"{multiplo_final:.2f}x o capital", "green", "green-bg")
        with c3:
            card("Lucro real", "📈", moeda(lucro_final), "Ganho bruto estimado", f"{percentual(roi_final)} sobre aporte", "purple", "purple-bg")
        with c4:
            card("ROI real", "🎯", percentual(roi_final), "Retorno sobre o capital", "Total do investimento", "orange", "orange-bg")

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            card("Valor inicial do imóvel", "🏠", moeda(valor_imovel), "Valor atual hoje", "Base inicial", "blue")
        with c6:
            card("Valor projetado na venda", "🏢", moeda(valor_final), "Valor estimado futuro", "Projeção", "green", "green-bg")
        with c7:
            card("Valorização total", "⬆️", percentual(valorizacao_total), "Crescimento do imóvel", "Ganho de mercado", "purple", "purple-bg")
        with c8:
            card("Fluxo médio / mês", "📅", moeda(fluxo_medio_mes), "Média de aporte", "Desembolso médio", "orange", "orange-bg")

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 DESEMPENHO ANO A ANO</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Projeção de aportes, reforços personalizados, valorização e retorno total na venda.</div>', unsafe_allow_html=True)

    df_show = df_ano.copy()
    for col in ["Aporte no ano", "Reforços antes da entrega", "Reforços depois da entrega", "Reforços totais", "Aporte acumulado", "Valor estimado do imóvel", "Lucro bruto", "💰 Retorno total na venda"]:
        df_show[col] = df_show[col].apply(moeda)
    df_show["Múltiplo do capital"] = df_show["Múltiplo do capital"].apply(lambda x: f"{x:.2f}x")
    df_show["ROI acumulado"] = df_show["ROI acumulado"].apply(percentual)
    st.dataframe(df_show, width="stretch", hide_index=True, height=280)

    st.markdown(f"""
    <div class="summary-box">
        <div>
            <div class="summary-title">🏆 Resumo final do investimento</div>
            <div class="summary-text">
                Você investiu <b>{moeda(aporte_final)}</b> e receberia <b style="color:#087a20;">{moeda(dinheiro_mao_final)}</b> na venda do imóvel.<br>
                Lucro bruto de <b style="color:#087a20;">{moeda(lucro_final)}</b> com valorização de <b>{percentual(valorizacao_total)}</b>.
            </div>
        </div>
        <div class="summary-metric"><div class="summary-value">{moeda(dinheiro_mao_final)}</div><div class="summary-label">Retorno total</div></div>
        <div class="summary-metric"><div class="summary-value">{moeda(lucro_final)}</div><div class="summary-label">Lucro bruto</div></div>
        <div class="summary-metric"><div class="summary-value">{multiplo_final:.2f}x</div><div class="summary-label">Múltiplo do capital</div></div>
        <div class="summary-metric"><div class="summary-value">{percentual(roi_final)}</div><div class="summary-label">ROI total</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📆 Fluxo mensal</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Acompanhamento mês a mês do desembolso, reforços, valorização e retorno estimado.</div>', unsafe_allow_html=True)
    dfm = df_mes.copy()
    for col in ["Parcela corrigida", "Reforço antes da entrega", "Reforço depois da entrega", "Reforço total", "Aporte do mês", "Aporte acumulado", "Valor estimado do imóvel", "Lucro bruto", "💰 Dinheiro na mão"]:
        dfm[col] = dfm[col].apply(moeda)
    dfm["Múltiplo"] = dfm["Múltiplo"].apply(lambda x: f"{x:.2f}x")
    dfm["ROI"] = dfm["ROI"].apply(percentual)
    st.dataframe(dfm, width="stretch", hide_index=True, height=520)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗓️ Ano a ano</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Resumo anual para comparar o melhor momento de saída.</div>', unsafe_allow_html=True)
    dfa = df_ano.copy()
    for col in ["Aporte no ano", "Reforços antes da entrega", "Reforços depois da entrega", "Reforços totais", "Aporte acumulado", "Valor estimado do imóvel", "Lucro bruto", "💰 Retorno total na venda"]:
        dfa[col] = dfa[col].apply(moeda)
    dfa["Múltiplo do capital"] = dfa["Múltiplo do capital"].apply(lambda x: f"{x:.2f}x")
    dfa["ROI acumulado"] = dfa["ROI acumulado"].apply(percentual)
    st.dataframe(dfa, width="stretch", hide_index=True, height=420)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✅ Critérios de avaliação</div>', unsafe_allow_html=True)
    st.write("**Nota final:**", f"{nota}/100 — {classificacao}")
    st.progress(min(nota / 100, 1.0), text=f"Nota geral: {nota}/100")
    st.progress(min(roi_final / 200, 1.0), text=f"ROI: {percentual(roi_final)}")
    st.progress(min(multiplo_final / 3, 1.0), text=f"Múltiplo do capital: {multiplo_final:.2f}x")
    st.progress(min((100 - aporte_sobre_valor) / 100, 1.0), text=f"Capital imobilizado: {percentual(aporte_sobre_valor)} do valor do imóvel")
    st.write("**Comentário:**")
    st.write("O ponto central da análise é considerar o retorno total como capital aportado + lucro da valorização. Esse é o dinheiro estimado que volta para sua mão na venda.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Dados variáveis usados na simulação</div>', unsafe_allow_html=True)
    reforcos_antes_formatados = ", ".join([f"Mês {m}: {moeda(v)}" for m, v in sorted(reforcos_antes_dict.items())]) if reforcos_antes_dict else "Nenhum"
    reforcos_depois_formatados = ", ".join([f"Mês {m}: {moeda(v)}" for m, v in sorted(reforcos_depois_dict.items())]) if reforcos_depois_dict else "Nenhum"
    dados = pd.DataFrame([
        ["Valor atual do imóvel", moeda(valor_imovel)],
        ["Entrada", moeda(entrada)],
        ["Parcela mensal inicial", moeda(parcela_mensal)],
        ["Prazo total", f"{prazo_meses} meses"],
        ["Mês de entrega", f"{mes_entrega}"],
        ["Reforços antes da entrega", reforcos_antes_formatados],
        ["Reforços depois da entrega", reforcos_depois_formatados],
        ["Valorização anual", percentual(valorizacao_anual * 100)],
        ["CUB/INCC anual", percentual(cub_anual * 100)],
        ["Anos de análise", f"{anos_analise}"],
        ["Metragem", f"{metragem:.0f} m²"],
        ["Valor por m²", moeda(valor_m2)],
    ], columns=["Campo", "Valor"])
    st.dataframe(dados, width="stretch", hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="notice">
ℹ️ As projeções são estimativas e não garantem resultados futuros. Esta análise não considera impostos, corretagem, ITBI, escritura, financiamento, distrato, condomínio, vacância ou variações reais de mercado.
</div>
""", unsafe_allow_html=True)
