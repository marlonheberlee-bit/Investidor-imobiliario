
import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title="Investidor Imobiliário PRO", page_icon="🏢", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
.hero {
    background: linear-gradient(135deg, #111827 0%, #1f2937 60%, #374151 100%);
    padding: 28px 32px;
    border-radius: 22px;
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.12);
}
.hero h1 {margin: 0; font-size: 34px; font-weight: 800;}
.hero p {margin-top: 8px; color: #d1d5db; font-size: 16px;}
.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 6px 20px rgba(15,23,42,0.07);
    border: 1px solid #e5e7eb;
    margin-bottom: 16px;
}
.section-title {color: #111827; font-size: 22px; font-weight: 800; margin-bottom: 12px;}
.grade {
    padding: 20px;
    border-radius: 18px;
    font-weight: 800;
    margin-bottom: 16px;
}
.otimo {background: #dcfce7; color: #166534; border: 1px solid #86efac;}
.bom {background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd;}
.regular {background: #fef3c7; color: #92400e; border: 1px solid #fcd34d;}
.pessimo {background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5;}
div[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 5px 15px rgba(15,23,42,0.06);
}
</style>
""", unsafe_allow_html=True)

def moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(v):
    return f"{v:.2f}%".replace(".", ",")

def nota_css(n):
    return {"ÓTIMO":"otimo","BOM":"bom","REGULAR":"regular","PÉSSIMO":"pessimo"}.get(n, "regular")

def classificar_fluxo_valorizacao(investido, valor_inicial, valor_final, fluxo_medio):
    """
    Nota baseada apenas em fluxo de pagamento x valorização do imóvel.
    Não usa banco, CDI, ROI financeiro ou custo de oportunidade.
    """
    valorizacao_reais = valor_final - valor_inicial
    valorizacao_pct = (valorizacao_reais / valor_inicial * 100) if valor_inicial > 0 else 0
    alavancagem_valorizacao = (valorizacao_reais / investido * 100) if investido > 0 else 0
    fluxo_pct_imovel = (fluxo_medio / valor_inicial * 100) if valor_inicial > 0 else 0
    cobertura_valorizacao = (valor_final / investido) if investido > 0 else 0

    score = 0

    # 1) Quanto a valorização representa sobre o dinheiro colocado
    # Ex: colocou 100 mil e valorizou 150 mil = 150%, muito forte.
    if alavancagem_valorizacao >= 150:
        score += 45
    elif alavancagem_valorizacao >= 100:
        score += 38
    elif alavancagem_valorizacao >= 70:
        score += 30
    elif alavancagem_valorizacao >= 40:
        score += 20
    elif alavancagem_valorizacao >= 20:
        score += 10
    else:
        score += 3

    # 2) Fluxo leve: quanto menor o fluxo médio mensal sobre o valor do imóvel, melhor.
    if fluxo_pct_imovel <= 0.25:
        score += 30
    elif fluxo_pct_imovel <= 0.40:
        score += 24
    elif fluxo_pct_imovel <= 0.60:
        score += 16
    elif fluxo_pct_imovel <= 0.85:
        score += 8
    else:
        score += 3

    # 3) Valorização percentual do imóvel no período.
    if valorizacao_pct >= 50:
        score += 25
    elif valorizacao_pct >= 35:
        score += 20
    elif valorizacao_pct >= 25:
        score += 15
    elif valorizacao_pct >= 15:
        score += 9
    elif valorizacao_pct >= 8:
        score += 5
    else:
        score += 1

    score = max(0, min(100, score))

    if score >= 80:
        nota = "ÓTIMO"
        leitura = "Excelente relação entre baixo fluxo e valorização. O imóvel valorizou muito em comparação ao dinheiro colocado."
    elif score >= 65:
        nota = "BOM"
        leitura = "Boa relação entre fluxo e valorização. O dinheiro colocado está sendo bem alavancado pela valorização do imóvel."
    elif score >= 45:
        nota = "REGULAR"
        leitura = "A valorização existe, mas não é tão forte diante do fluxo de pagamento exigido."
    else:
        nota = "PÉSSIMO"
        leitura = "A valorização projetada não compensa bem o fluxo de pagamento exigido."

    return score, nota, leitura, valorizacao_reais, valorizacao_pct, alavancagem_valorizacao, fluxo_pct_imovel, cobertura_valorizacao

def fator_cub_acumulado(cub_lista, mes):
    if mes <= 1:
        return 1.0
    return float(np.prod(1 + cub_lista[:mes-1]))

def montar_reforcos(prazo, tipo_reforco, valor_reforco, cub_lista, mes_entrega, aumento_pos_entrega_pct, reforcos_custom, padrao_custom):
    reforcos = np.zeros(prazo)

    def aplicar(mes, valor_base, aplicar_aumento=True):
        if 1 <= mes <= prazo:
            valor = valor_base * fator_cub_acumulado(cub_lista, mes)
            if aplicar_aumento and mes >= mes_entrega:
                valor *= (1 + aumento_pos_entrega_pct / 100)
            reforcos[mes-1] += valor

    if tipo_reforco == "Sem reforços":
        return reforcos

    if tipo_reforco == "Semestral fixo":
        for mes in range(6, prazo + 1, 6):
            aplicar(mes, valor_reforco)

    elif tipo_reforco == "Anual fixo":
        for mes in range(12, prazo + 1, 12):
            aplicar(mes, valor_reforco)

    elif tipo_reforco == "Meses-base recorrentes":
        if reforcos_custom is not None and not reforcos_custom.empty:
            for _, row in reforcos_custom.dropna().iterrows():
                mes_base = int(row.get("Mês base", 0) or 0)
                valor_base = float(row.get("Valor base", 0) or 0)
                if 1 <= mes_base <= 12 and valor_base > 0:
                    mes = mes_base
                    while mes <= prazo:
                        aplicar(mes, valor_base)
                        mes += 12

    elif tipo_reforco == "Variável por mês":
        if reforcos_custom is not None and not reforcos_custom.empty:
            for _, row in reforcos_custom.dropna().iterrows():
                mes = int(row.get("Mês", 0) or 0)
                valor_base = float(row.get("Valor", 0) or 0)
                aplicar(mes, valor_base)

    elif tipo_reforco == "Variável recorrente por fase":
        if padrao_custom is not None and not padrao_custom.empty:
            for _, row in padrao_custom.dropna().iterrows():
                fase = str(row.get("Fase", "Antes da entrega"))
                mes_base = int(row.get("Mês base", 0) or 0)
                valor_base = float(row.get("Valor base", 0) or 0)
                if 1 <= mes_base <= 12 and valor_base > 0:
                    mes = mes_base
                    while mes <= prazo:
                        if fase == "Antes da entrega" and mes < mes_entrega:
                            aplicar(mes, valor_base, aplicar_aumento=False)
                        elif fase == "Depois da entrega" and mes >= mes_entrega:
                            aplicar(mes, valor_base, aplicar_aumento=False)
                        mes += 12

    return reforcos

st.markdown("""
<div class="hero">
<h1>🏢 Investidor Imobiliário PRO</h1>
<p>Simulador profissional de saída: fluxo, CUB, saldo futuro, dinheiro na mão, lucro real e ponto ideal de venda.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Parâmetros")
    valor_imovel = st.number_input("Valor atual do imóvel", min_value=0.0, value=1300000.0, step=10000.0)
    entrada = st.number_input("Entrada / sinal", min_value=0.0, value=25000.0, step=1000.0)
    parcela_inicial = st.number_input("Parcela mensal inicial", min_value=0.0, value=2500.0, step=100.0)
    prazo = int(st.number_input("Prazo total em meses", min_value=1, max_value=240, value=120, step=1))
    mes_entrega = int(st.number_input("Mês de entrega do empreendimento", min_value=1, max_value=prazo, value=min(48, prazo), step=1))

    st.divider()
    modo_cub = st.radio("Modo de reajuste CUB", ["CUB anual estimado", "CUB mensal fixo", "CUB mensal variável"])
    cub_anual = st.number_input("CUB anual estimado (%)", min_value=0.0, max_value=30.0, value=4.3, step=0.1)
    cub_mensal = st.number_input("CUB mensal base (%)", min_value=-5.0, max_value=10.0, value=0.35, step=0.01)

    st.divider()
    valorizacao_conservadora = st.number_input("Valorização conservadora (% a.a.)", min_value=-20.0, max_value=50.0, value=7.0, step=0.5)
    valorizacao_base = st.number_input("Valorização base (% a.a.)", min_value=-20.0, max_value=50.0, value=10.0, step=0.5)
    valorizacao_otimista = st.number_input("Valorização otimista (% a.a.)", min_value=-20.0, max_value=50.0, value=15.0, step=0.5)
    cenario_nota = st.selectbox("Cenário usado na nota", ["Conservador", "Base", "Otimista"])

    st.divider()
    mes_venda = int(st.number_input("Mês em que pretende avaliar/vender", min_value=1, max_value=prazo, value=min(60, prazo), step=1))
    custo_venda_pct = st.number_input("Custos venda/comissão/impostos (%)", min_value=0.0, max_value=30.0, value=6.0, step=0.5)
    desconto_liquidez_pct = st.number_input("Desconto para vender rápido (%)", min_value=0.0, max_value=30.0, value=0.0, step=0.5)

    st.divider()
    tipo_reforco = st.selectbox("Tipo de reforço", ["Sem reforços", "Semestral fixo", "Anual fixo", "Meses-base recorrentes", "Variável por mês", "Variável recorrente por fase"])
    valor_reforco = st.number_input("Valor base do reforço padrão", min_value=0.0, value=10000.0, step=1000.0)
    aumento_pos_entrega_pct = st.number_input("Aumento automático dos reforços após entrega (%)", min_value=0.0, max_value=300.0, value=0.0, step=5.0)

tab_inputs, tab_resultado, tab_fluxo, tab_ano, tab_criterios = st.tabs(["📝 Dados variáveis", "🎯 Painel executivo", "📅 Fluxo mensal", "📆 Ano a ano", "✅ Critérios"])

with tab_inputs:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="section-title">Reforços</div>', unsafe_allow_html=True)
        if tipo_reforco == "Meses-base recorrentes":
            st.write("Informe os meses-base. O app repete automaticamente a cada 12 meses até o final.")
            reforcos_df = st.data_editor(pd.DataFrame({"Mês base": [6, 10], "Valor base": [40642.90, 40642.90]}), num_rows="dynamic", use_container_width=True)
            padrao_fase_df = pd.DataFrame(columns=["Fase", "Mês base", "Valor base"])
        elif tipo_reforco == "Variável por mês":
            st.write("Informe cada reforço individual. Esse modo não repete.")
            reforcos_df = st.data_editor(pd.DataFrame({"Mês": [6, 10, 18], "Valor": [40642.90, 40642.90, 45000.00]}), num_rows="dynamic", use_container_width=True)
            padrao_fase_df = pd.DataFrame(columns=["Fase", "Mês base", "Valor base"])
        elif tipo_reforco == "Variável recorrente por fase":
            st.write("Use quando a construtora muda os reforços depois da entrega.")
            padrao_fase_df = st.data_editor(pd.DataFrame({
                "Fase": ["Antes da entrega", "Antes da entrega", "Depois da entrega", "Depois da entrega"],
                "Mês base": [6, 12, 6, 12],
                "Valor base": [20000.0, 20000.0, 40000.0, 40000.0],
            }), num_rows="dynamic", use_container_width=True)
            reforcos_df = pd.DataFrame(columns=["Mês", "Valor"])
        else:
            reforcos_df = pd.DataFrame(columns=["Mês", "Valor"])
            padrao_fase_df = pd.DataFrame(columns=["Fase", "Mês base", "Valor base"])
            st.info("Semestral/anual será repetido até o final e corrigido pelo CUB.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="section-title">CUB mensal variável</div>', unsafe_allow_html=True)
        if modo_cub == "CUB mensal variável":
            cub_df = st.data_editor(pd.DataFrame({"Mês": list(range(1, min(13, prazo+1))), "CUB mensal (%)": [0.35]*min(12, prazo)}), num_rows="dynamic", use_container_width=True)
        else:
            cub_df = pd.DataFrame(columns=["Mês", "CUB mensal (%)"])
            st.info("Use CUB mensal variável na lateral para informar mês a mês.")
        st.markdown('</div>', unsafe_allow_html=True)

# CUB
if modo_cub == "CUB anual estimado":
    reajuste_mensal = (1 + cub_anual/100) ** (1/12) - 1
    cub_lista = np.full(prazo, reajuste_mensal)
elif modo_cub == "CUB mensal fixo":
    reajuste_mensal = cub_mensal / 100
    cub_lista = np.full(prazo, reajuste_mensal)
else:
    last = cub_mensal / 100
    mapa = {}
    for _, r in cub_df.dropna().iterrows():
        mapa[int(r["Mês"])] = float(r["CUB mensal (%)"]) / 100
    cub_lista = []
    for m in range(1, prazo+1):
        if m in mapa:
            last = mapa[m]
        cub_lista.append(last)
    cub_lista = np.array(cub_lista)
    reajuste_mensal = float(np.mean(cub_lista))

meses = np.arange(1, prazo+1)

parcelas = []
parcela = parcela_inicial
for i, m in enumerate(meses):
    if m == 1:
        parcela = parcela_inicial
    else:
        parcela *= (1 + cub_lista[i])
    parcelas.append(parcela)
parcelas = np.array(parcelas)

reforcos = montar_reforcos(prazo, tipo_reforco, valor_reforco, cub_lista, mes_entrega, aumento_pos_entrega_pct, reforcos_df, padrao_fase_df)

desembolso_mensal = parcelas + reforcos
desembolso_mensal[0] += entrada
desembolso_acumulado = np.cumsum(desembolso_mensal)

val_aa_uso = valorizacao_conservadora if cenario_nota == "Conservador" else valorizacao_base if cenario_nota == "Base" else valorizacao_otimista
val_mensal = (1 + val_aa_uso/100) ** (1/12) - 1
valor_imovel_mes = valor_imovel * ((1 + val_mensal) ** meses)

idx = mes_venda - 1
investido_ate_venda = float(desembolso_acumulado[idx])
valor_estimado = float(valor_imovel_mes[idx])
valor_liquido_estimado = valor_estimado * (1 - desconto_liquidez_pct/100) * (1 - custo_venda_pct/100)
fluxo_medio = float(np.mean(desembolso_mensal[:idx+1]))

score, nota, leitura, valorizacao_reais, valorizacao_pct, alavancagem_valorizacao, fluxo_pct_imovel, cobertura_valorizacao = classificar_fluxo_valorizacao(
    investido=investido_ate_venda,
    valor_inicial=valor_imovel,
    valor_final=valor_estimado,
    fluxo_medio=fluxo_medio,
)

saldo_futuro_assumido = float(np.sum(desembolso_mensal[idx+1:])) if idx+1 < prazo else 0.0
agio_teorico = max(0, valor_liquido_estimado - saldo_futuro_assumido)
lucro_sobre_fluxo = valorizacao_reais - investido_ate_venda

with tab_resultado:
    left, right = st.columns([1.05, 2.2])
    with left:
        st.markdown(f'<div class="grade {nota_css(nota)}"><div style="font-size:14px;">CLASSIFICAÇÃO</div><div style="font-size:44px;">{nota}</div><div style="font-size:18px;">Nota: {score:.0f}/100</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="card"><div class="section-title">Leitura rápida</div>', unsafe_allow_html=True)
        st.write(leitura)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        a,b,c,d = st.columns(4)
        a.metric("Investido no fluxo", moeda(investido_ate_venda))
        b.metric("Dinheiro na mão", moeda(max(0, valor_liquido_estimado - saldo_futuro_assumido)))
        c.metric("Lucro real", moeda(max(0, valor_liquido_estimado - saldo_futuro_assumido) - investido_ate_venda))
        d.metric("ROI real", pct(((max(0, valor_liquido_estimado - saldo_futuro_assumido) - investido_ate_venda) / investido_ate_venda * 100) if investido_ate_venda > 0 else 0))

        e,f,g,h = st.columns(4)
        e.metric("Valor inicial", moeda(valor_imovel))
        f.metric("Valor projetado", moeda(valor_estimado))
        g.metric("Valorização %", pct(valorizacao_pct))
        h.metric("Fluxo médio / imóvel", pct(fluxo_pct_imovel))
        # Projeção executiva profissional
        periodos_exec = [2, 3, 4, 5]
        linhas_exec = []
        melhor_saida = None

        for ano_exec in periodos_exec:
            mes_exec = min(ano_exec * 12, prazo)
            i_exec = mes_exec - 1

            aporte_exec = float(desembolso_acumulado[i_exec])
            valor_exec = float(valor_imovel_mes[i_exec])
            valor_venda_liquido_exec = valor_exec * (1 - desconto_liquidez_pct/100) * (1 - custo_venda_pct/100)
            saldo_restante_exec = float(np.sum(desembolso_mensal[i_exec+1:])) if i_exec+1 < prazo else 0.0

            dinheiro_na_mao_exec = max(0, valor_venda_liquido_exec - saldo_restante_exec)
            lucro_real_exec = dinheiro_na_mao_exec - aporte_exec
            roi_exec = (lucro_real_exec / aporte_exec * 100) if aporte_exec > 0 else 0
            multiplicador_exec = (dinheiro_na_mao_exec / aporte_exec) if aporte_exec > 0 else 0
            entrega_flag = "SIM" if mes_exec >= mes_entrega else "NÃO"

            linhas_exec.append({
                "Período": f"{ano_exec} anos",
                "Mês": mes_exec,
                "Entrega concluída": entrega_flag,
                "Valor aportado": aporte_exec,
                "Valor venda líquido": valor_venda_liquido_exec,
                "Saldo futuro assumido": saldo_restante_exec,
                "Dinheiro na mão": dinheiro_na_mao_exec,
                "Lucro real": lucro_real_exec,
                "ROI sobre aporte": roi_exec,
                "Multiplicador": multiplicador_exec,
            })

        exec_df = pd.DataFrame(linhas_exec)
        melhor_linha = exec_df.loc[exec_df["Lucro real"].idxmax()]
        melhor_saida_txt = f'{melhor_linha["Período"]} / mês {int(melhor_linha["Mês"])}'

        st.markdown('<div class="card"><div class="section-title">Projeção profissional de saída: 2, 3, 4 e 5 anos</div>', unsafe_allow_html=True)
        st.write("Aqui está o dado mais importante: quanto dinheiro volta para sua mão se vender em cada período.")
        st.dataframe(
            exec_df.style.format({
                "Valor aportado": "R$ {:,.2f}",
                "Valor venda líquido": "R$ {:,.2f}",
                "Saldo futuro assumido": "R$ {:,.2f}",
                "Dinheiro na mão": "R$ {:,.2f}",
                "Lucro real": "R$ {:,.2f}",
                "ROI sobre aporte": "{:,.2f}%",
                "Multiplicador": "{:,.2f}x",
            }),
            use_container_width=True
        )
        st.success(f"Melhor ponto de saída pela simulação: {melhor_saida_txt}, com lucro real estimado de {moeda(float(melhor_linha['Lucro real']))}.")
        st.markdown('</div>', unsafe_allow_html=True)


    st.markdown('<div class="card"><div class="section-title">Resumo da avaliação</div>', unsafe_allow_html=True)
    dinheiro_na_mao_atual = max(0, valor_liquido_estimado - saldo_futuro_assumido)
    lucro_real_atual = dinheiro_na_mao_atual - investido_ate_venda
    roi_real_atual = (lucro_real_atual / investido_ate_venda * 100) if investido_ate_venda > 0 else 0

    st.write(f"""
    Até o mês **{mes_venda}**, você teria desembolsado **{moeda(investido_ate_venda)}** no fluxo.  
    O imóvel sairia de **{moeda(valor_imovel)}** para **{moeda(valor_estimado)}**.  

    Mas o cálculo profissional de venda considera que o comprador assume o saldo futuro:
    - Valor líquido estimado de venda: **{moeda(valor_liquido_estimado)}**
    - Saldo futuro assumido pelo comprador: **{moeda(saldo_futuro_assumido)}**
    - **Dinheiro que volta para sua mão: {moeda(dinheiro_na_mao_atual)}**
    - **Lucro real: {moeda(lucro_real_atual)}**
    - **ROI real sobre o aporte: {pct(roi_real_atual)}**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    chart_df = pd.DataFrame({"Mês": meses, "Total investido": desembolso_acumulado, "Valor estimado do imóvel": valor_imovel_mes}).set_index("Mês")
    st.markdown('<div class="card"><div class="section-title">Fluxo investido x Valor do imóvel</div>', unsafe_allow_html=True)
    st.line_chart(chart_df)
    st.markdown('</div>', unsafe_allow_html=True)

df = pd.DataFrame({
    "Mês": meses,
    "Parcela corrigida": parcelas,
    "Reforço corrigido": reforcos,
    "Desembolso mensal": desembolso_mensal,
    "Desembolso acumulado": desembolso_acumulado,
    "Valor estimado do imóvel": valor_imovel_mes,
})

with tab_fluxo:
    st.markdown('<div class="card"><div class="section-title">Fluxo mês a mês</div>', unsafe_allow_html=True)
    st.dataframe(df.style.format({
        "Parcela corrigida": "R$ {:,.2f}",
        "Reforço corrigido": "R$ {:,.2f}",
        "Desembolso mensal": "R$ {:,.2f}",
        "Desembolso acumulado": "R$ {:,.2f}",
        "Valor estimado do imóvel": "R$ {:,.2f}",
    }), use_container_width=True, height=520)
    st.markdown('</div>', unsafe_allow_html=True)

anos = []
for ano in range(1, math.ceil(prazo/12)+1):
    m = min(ano*12, prazo)
    i = m - 1
    anos.append({
        "Ano": ano,
        "Mês": m,
        "Total investido": desembolso_acumulado[i],
        "Valor estimado imóvel": valor_imovel_mes[i],
        "Valorização acumulada": valor_imovel_mes[i] - valor_imovel,
        "Parcela no fim do ano": parcelas[i],
        "Reforços acumulados": reforcos[:i+1].sum(),
    })
ano_df = pd.DataFrame(anos)

with tab_ano:
    st.markdown('<div class="card"><div class="section-title">Projeção ano a ano</div>', unsafe_allow_html=True)
    st.dataframe(ano_df.style.format({
        "Total investido": "R$ {:,.2f}",
        "Valor estimado imóvel": "R$ {:,.2f}",
        "Valorização acumulada": "R$ {:,.2f}",
        "Parcela no fim do ano": "R$ {:,.2f}",
        "Reforços acumulados": "R$ {:,.2f}",
    }), use_container_width=True)
    st.bar_chart(ano_df.set_index("Ano")[["Total investido", "Valorização acumulada"]])
    st.markdown('</div>', unsafe_allow_html=True)

with tab_criterios:
    st.markdown('<div class="card"><div class="section-title">Como a nota é calculada agora</div>', unsafe_allow_html=True)
    st.write("""
    A nota agora considera **apenas duas coisas**:

    **1. Fluxo de pagamento**  
    Quanto dinheiro você precisa colocar até o mês de análise/venda.

    **2. Valorização do imóvel**  
    Quanto o imóvel aumentou de valor no mesmo período.

    O principal cruzamento é:

    **Valorização do imóvel ÷ Total investido no fluxo**

    Exemplo:
    - Você colocou R$ 100 mil
    - O imóvel valorizou R$ 150 mil
    - A valorização equivale a 150% do dinheiro colocado

    Isso recebe uma nota melhor porque mostra alavancagem patrimonial com baixo fluxo.

    A nota também penaliza quando o fluxo médio mensal fica pesado em relação ao valor do imóvel.
    """)
    st.info("""
    Classificação:
    - **ÓTIMO:** valorização muito superior ao fluxo exigido
    - **BOM:** valorização superior ao fluxo, com boa margem
    - **REGULAR:** valorização existe, mas a margem é apertada
    - **PÉSSIMO:** fluxo pesado demais para pouca valorização
    """)
    st.warning("A análise profissional usa o ponto central do investidor: quanto dinheiro volta para sua mão após descontar o saldo futuro assumido pelo comprador.")
    st.markdown('</div>', unsafe_allow_html=True)
