import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Analisador Imobiliário V8.1",
    page_icon="🏢",
    layout="wide"
)

# =============================
# CSS VISUAL PROFISSIONAL
# =============================

st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0px;
    }

    .subtitle {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 22px;
    }

    .tabs-bar {
        display: flex;
        gap: 26px;
        padding: 12px 8px 14px 8px;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 18px;
        font-weight: 700;
        color: #0f172a;
    }

    .tab-active {
        color: #1d4ed8;
        border-bottom: 3px solid #1d4ed8;
        padding-bottom: 12px;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.1fr 3fr;
        gap: 18px;
        margin-bottom: 18px;
    }

    .classification-card {
        background: linear-gradient(145deg, #073ec7, #0057ff);
        border-radius: 22px;
        padding: 30px;
        color: white;
        min-height: 405px;
        box-shadow: 0 14px 35px rgba(37, 99, 235, 0.25);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .classification-card .label {
        font-size: 15px;
        font-weight: 800;
        letter-spacing: .5px;
        opacity: .95;
    }

    .classification-card .grade {
        font-size: 68px;
        font-weight: 900;
        line-height: 1;
        margin: 20px 0 10px 0;
    }

    .classification-card .score {
        display: inline-block;
        background: rgba(15, 23, 42, 0.22);
        padding: 9px 16px;
        border-radius: 999px;
        font-size: 20px;
        font-weight: 800;
    }

    .quick-reading {
        background: rgba(15, 23, 42, 0.20);
        border-radius: 18px;
        padding: 20px;
        margin-top: 22px;
    }

    .quick-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .quick-text {
        font-size: 15px;
        line-height: 1.55;
        opacity: .96;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
    }

    .kpi-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 24px 18px;
        text-align: center;
        min-height: 190px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    .kpi-icon {
        width: 58px;
        height: 58px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 14px auto;
        font-size: 28px;
        background: #dbeafe;
    }

    .kpi-title {
        color: #0f172a;
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 10px;
        white-space: normal;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 8px;
        white-space: nowrap;
    }

    .kpi-sub {
        color: #64748b;
        font-size: 14px;
        min-height: 18px;
    }

    .pill {
        display: inline-block;
        margin-top: 9px;
        font-size: 13px;
        font-weight: 800;
        padding: 6px 10px;
        border-radius: 8px;
    }

    .blue { color: #0b4ad9; }
    .green { color: #087a20; }
    .purple { color: #5b21b6; }
    .orange { color: #ea580c; }
    .pill-blue { background: #dbeafe; color: #0b4ad9; }
    .pill-green { background: #dcfce7; color: #087a20; }
    .pill-purple { background: #ede9fe; color: #5b21b6; }
    .pill-orange { background: #ffedd5; color: #ea580c; }

    .section-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px;
        margin-top: 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
    }

    .section-title {
        color: #0b4ad9;
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 2px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 18px;
    }

    .summary-box {
        background: linear-gradient(90deg, #f0fdf4, #ffffff);
        border: 1px solid #86efac;
        border-radius: 18px;
        padding: 24px;
        display: grid;
        grid-template-columns: 1.6fr repeat(4, 1fr);
        gap: 16px;
        align-items: center;
        margin-top: 20px;
    }

    .summary-title {
        color: #087a20;
        font-weight: 900;
        font-size: 17px;
        margin-bottom: 8px;
    }

    .summary-text {
        color: #0f172a;
        font-size: 15px;
        line-height: 1.55;
    }

    .summary-metric {
        text-align: center;
        border-left: 1px solid #d1fae5;
        padding-left: 14px;
    }

    .summary-metric-value {
        color: #087a20;
        font-size: 24px;
        font-weight: 900;
        white-space: nowrap;
    }

    .summary-metric-label {
        color: #475569;
        font-size: 13px;
        margin-top: 6px;
    }

    .warning-box {
        margin-top: 16px;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #334155;
        padding: 12px 16px;
        border-radius: 12px;
        font-size: 13px;
    }

    @media (max-width: 1100px) {
        .hero-grid { grid-template-columns: 1fr; }
        .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .summary-box { grid-template-columns: 1fr; }
        .summary-metric { border-left: none; border-top: 1px solid #d1fae5; padding-top: 12px; }
    }
</style>
""", unsafe_allow_html=True)

# =============================
# FUNÇÕES
# =============================

def moeda(valor):
    if pd.isna(valor) or valor is None:
        return "R$ 0"
    return f"R$ {valor:,.0f}".replace(",", ".")


def percentual(valor):
    if pd.isna(valor) or valor is None:
        return "0,00%"
    return f"{valor:.2f}%".replace(".", ",")


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


def classificar_nota(nota):
    if nota >= 85:
        return "EXCELENTE"
    elif nota >= 70:
        return "BOM"
    elif nota >= 55:
        return "ACEITÁVEL"
    return "FRACO"


def leitura_rapida(nota, multiplo, roi):
    if nota >= 85:
        return "Excelente potencial de retorno, boa multiplicação do capital e relação risco/retorno muito atrativa."
    if nota >= 70:
        return "Bom potencial de retorno, com capital bem aproveitado e resultado projetado interessante."
    if nota >= 55:
        return "Operação aceitável, mas exige atenção ao fluxo, prazo, reajustes e velocidade real de valorização."
    return "Operação fraca ou arriscada. O retorno projetado pode não compensar o capital imobilizado."

# =============================
# CABEÇALHO
# =============================

st.markdown('<div class="main-title">🏢 Analisador Imobiliário Profissional V8.1</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Painel executivo com foco em dinheiro na mão, valorização, aporte, ROI e decisão de investimento.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="tabs-bar">
    <span class="tab-active">📊 Painel executivo</span>
    <span>📆 Fluxo mensal</span>
    <span>🗓️ Ano a ano</span>
    <span>✅ Critérios</span>
    <span>📝 Dados variáveis</span>
</div>
""", unsafe_allow_html=True)

# =============================
# ENTRADAS EM EXPANDER
# =============================

with st.expander("📝 Dados variáveis do empreendimento", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        nome = st.text_input("Nome do empreendimento", "Empreendimento Exemplo")
        localizacao = st.text_input("Localização", "Porto Belo / SC")
        valor_imovel = st.number_input("Valor atual do imóvel", min_value=0.0, value=1200000.0, step=10000.0)
        metragem = st.number_input("Metragem privativa m²", min_value=0.0, value=90.0, step=1.0)

    with col2:
        ano_atual = datetime.now().year
        ano_entrega = st.number_input("Ano de entrega", min_value=ano_atual, max_value=2045, value=2030, step=1)
        valorizacao_anual = st.slider("Valorização anual estimada", 0.0, 30.0, 15.0, 0.5) / 100
        cub_anual = st.slider("Reajuste anual estimado CUB/INCC", 0.0, 15.0, 4.3, 0.1) / 100
        anos_analise = st.slider("Anos para simulação", 1, 10, 5)

    with col3:
        entrada = st.number_input("Entrada", min_value=0.0, value=120000.0, step=5000.0)
        parcela_mensal = st.number_input("Parcela mensal inicial", min_value=0.0, value=2500.0, step=500.0)
        meses_parcelas = st.number_input("Quantidade de parcelas", min_value=0, value=48, step=1)
        reforco_anual = st.number_input("Reforço anual", min_value=0.0, value=30000.0, step=5000.0)

# =============================
# CÁLCULOS
# =============================

anos_entrega = max(ano_entrega - ano_atual, 1)
valor_m2 = valor_imovel / metragem if metragem > 0 else 0

linhas = []
for ano in range(1, anos_analise + 1):
    meses_no_ano = min(12, max(meses_parcelas - ((ano - 1) * 12), 0))
    parcela_reajustada = parcela_mensal * ((1 + cub_anual) ** (ano - 1))
    reforco_reajustado = reforco_anual * ((1 + cub_anual) ** (ano - 1))
    aporte_parcelas = parcela_reajustada * meses_no_ano
    aporte_reforco = reforco_reajustado if meses_no_ano > 0 else 0
    aporte_ano = entrada + aporte_parcelas + aporte_reforco if ano == 1 else aporte_parcelas + aporte_reforco

    total_aportado = sum([l["Aporte no ano"] for l in linhas]) + aporte_ano
    valor_estimado = valor_imovel * ((1 + valorizacao_anual) ** ano)
    lucro_bruto = valor_estimado - valor_imovel
    dinheiro_mao = total_aportado + lucro_bruto
    roi = (lucro_bruto / total_aportado) * 100 if total_aportado > 0 else 0
    multiplo = dinheiro_mao / total_aportado if total_aportado > 0 else 0
    fluxo_medio_mes = (aporte_ano / 12) if ano > 0 else 0

    linhas.append({
        "Ano": ano,
        "Aporte no ano": aporte_ano,
        "Aporte acumulado": total_aportado,
        "Valor estimado do imóvel": valor_estimado,
        "Lucro bruto": lucro_bruto,
        "💰 Retorno total na venda": dinheiro_mao,
        "Múltiplo do capital": multiplo,
        "ROI acumulado": roi,
        "Fluxo médio mês": fluxo_medio_mes
    })

df = pd.DataFrame(linhas)
ultimo = df.iloc[-1]

aporte_final = ultimo["Aporte acumulado"]
valor_final = ultimo["Valor estimado do imóvel"]
lucro_final = ultimo["Lucro bruto"]
dinheiro_mao_final = ultimo["💰 Retorno total na venda"]
roi_final = ultimo["ROI acumulado"]
multiplo_final = ultimo["Múltiplo do capital"]
fluxo_medio_final = aporte_final / max(anos_analise * 12, 1)
valorizacao_total = ((valor_final / valor_imovel) - 1) * 100 if valor_imovel > 0 else 0
aporte_sobre_valor = (aporte_final / valor_imovel) * 100 if valor_imovel > 0 else 0
nota = calcular_nota(roi_final, multiplo_final, aporte_sobre_valor, anos_entrega)
classificacao = classificar_nota(nota)
texto_leitura = leitura_rapida(nota, multiplo_final, roi_final)

# =============================
# PAINEL EXECUTIVO VISUAL
# =============================

st.markdown(f"""
<div class="hero-grid">
    <div class="classification-card">
        <div>
            <div class="label">CLASSIFICAÇÃO</div>
            <div class="grade">{classificacao}</div>
            <div class="score">Nota: {nota}/100</div>
        </div>
        <div class="quick-reading">
            <div class="quick-title">💡 Leitura rápida</div>
            <div class="quick-text">{texto_leitura}</div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-title">Investido no fluxo</div>
            <div class="kpi-icon">💵</div>
            <div class="kpi-value blue">{moeda(aporte_final)}</div>
            <div class="kpi-sub">Total aportado</div>
            <div class="pill pill-blue">Capital imobilizado</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Dinheiro na mão</div>
            <div class="kpi-icon">💰</div>
            <div class="kpi-value green">{moeda(dinheiro_mao_final)}</div>
            <div class="kpi-sub">Aporte + lucro na venda</div>
            <div class="pill pill-green">{multiplo_final:.2f}x o capital</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Lucro real</div>
            <div class="kpi-icon">📈</div>
            <div class="kpi-value purple">{moeda(lucro_final)}</div>
            <div class="kpi-sub">Ganho pela valorização</div>
            <div class="pill pill-purple">{percentual(roi_final)} sobre aporte</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">ROI real</div>
            <div class="kpi-icon">🎯</div>
            <div class="kpi-value orange">{percentual(roi_final)}</div>
            <div class="kpi-sub">Retorno sobre capital</div>
            <div class="pill pill-orange">Total do investimento</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Valor inicial do imóvel</div>
            <div class="kpi-icon">🏠</div>
            <div class="kpi-value blue">{moeda(valor_imovel)}</div>
            <div class="kpi-sub">Valor atual hoje</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Valor projetado na venda</div>
            <div class="kpi-icon">🏢</div>
            <div class="kpi-value green">{moeda(valor_final)}</div>
            <div class="kpi-sub">Valor estimado futuro</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Valorização total</div>
            <div class="kpi-icon">⬆️</div>
            <div class="kpi-value purple">{percentual(valorizacao_total)}</div>
            <div class="kpi-sub">Crescimento do imóvel</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Fluxo médio / mês</div>
            <div class="kpi-icon">📅</div>
            <div class="kpi-value orange">{moeda(fluxo_medio_final)}</div>
            <div class="kpi-sub">Média de desembolso</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================
# TABELA PROFISSIONAL
# =============================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📊 DESEMPENHO ANO A ANO</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Projeção de aportes, valorização e retorno total na venda.</div>', unsafe_allow_html=True)

# tabela formatada
df_tabela = df.copy()
df_tabela["Ano"] = df_tabela["Ano"].apply(lambda x: f"📅 {x}" + (" (Entrega)" if x == anos_entrega else ""))
df_tabela["Aporte no ano"] = df_tabela["Aporte no ano"].apply(moeda)
df_tabela["Aporte acumulado"] = df_tabela["Aporte acumulado"].apply(moeda)
df_tabela["Valor estimado do imóvel"] = df_tabela["Valor estimado do imóvel"].apply(moeda)
df_tabela["Lucro bruto"] = df_tabela["Lucro bruto"].apply(moeda)
df_tabela["💰 Retorno total na venda"] = df_tabela["💰 Retorno total na venda"].apply(lambda x: "💰 " + moeda(x))
df_tabela["Múltiplo do capital"] = df_tabela["Múltiplo do capital"].apply(lambda x: f"{x:.2f}x")
df_tabela["ROI acumulado"] = df_tabela["ROI acumulado"].apply(percentual)
df_tabela = df_tabela.drop(columns=["Fluxo médio mês"])

st.dataframe(
    df_tabela,
    use_container_width=True,
    hide_index=True,
    height=300
)

st.markdown(f"""
<div class="summary-box">
    <div>
        <div class="summary-title">🏆 RESUMO FINAL DO INVESTIMENTO</div>
        <div class="summary-text">
            Você investiu <b>{moeda(aporte_final)}</b> e receberia aproximadamente <b style="color:#087a20;">{moeda(dinheiro_mao_final)}</b> na venda do imóvel.<br>
            Lucro bruto estimado de <b style="color:#087a20;">{moeda(lucro_final)}</b>, com valorização total de <b>{percentual(valorizacao_total)}</b>.
        </div>
    </div>
    <div class="summary-metric">
        <div class="summary-metric-value">{moeda(dinheiro_mao_final)}</div>
        <div class="summary-metric-label">Retorno total</div>
    </div>
    <div class="summary-metric">
        <div class="summary-metric-value">{moeda(lucro_final)}</div>
        <div class="summary-metric-label">Lucro bruto</div>
    </div>
    <div class="summary-metric">
        <div class="summary-metric-value">{multiplo_final:.2f}x</div>
        <div class="summary-metric-label">Múltiplo do capital</div>
    </div>
    <div class="summary-metric">
        <div class="summary-metric-value">{percentual(roi_final)}</div>
        <div class="summary-metric-label">ROI total</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =============================
# AVALIAÇÃO FINAL
# =============================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">✅ AVALIAÇÃO DO INVESTIMENTO</div>', unsafe_allow_html=True)

col_av1, col_av2, col_av3 = st.columns([1, 1.2, 1.4])

with col_av1:
    st.metric("Nota final", f"{nota}/100")
    st.metric("Classificação", classificacao)
    st.metric("Valor por m²", moeda(valor_m2))

with col_av2:
    st.write("**Critérios analisados**")
    st.progress(min(nota / 100, 1.0), text=f"Nota geral: {nota}/100")
    st.progress(min(roi_final / 200, 1.0), text=f"ROI: {percentual(roi_final)}")
    st.progress(min(multiplo_final / 3, 1.0), text=f"Múltiplo: {multiplo_final:.2f}x")
    st.progress(min((100 - aporte_sobre_valor) / 100, 1.0), text=f"Capital imobilizado: {percentual(aporte_sobre_valor)} do imóvel")

with col_av3:
    st.write("**Comentário do investidor**")
    st.write(f"O empreendimento **{nome}**, em **{localizacao}**, apresenta classificação **{classificacao}**.")
    st.write(f"Na simulação, o aporte acumulado é de **{moeda(aporte_final)}** e o dinheiro estimado que volta na venda é de **{moeda(dinheiro_mao_final)}**.")
    st.write(f"O ponto central da análise é que o retorno total considera **capital aportado + lucro da valorização**, que é exatamente o dinheiro que volta para sua mão na saída.")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
    ℹ️ As projeções são estimativas e não garantem resultados futuros. Esta análise não considera impostos, corretagem, ITBI, escritura, distrato, financiamento, condomínio, vacância ou variações reais de mercado.
</div>
""", unsafe_allow_html=True)
