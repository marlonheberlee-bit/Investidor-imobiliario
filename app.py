import streamlit as st
import pandas as pd
import re
import pdfplumber
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Investidor Imobiliário Pro", page_icon="🏢", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"]{background:linear-gradient(180deg,#061936,#020817)}
[data-testid="stSidebar"] *{color:white!important}
.block-container{padding-top:1.5rem}
.hero{background:linear-gradient(135deg,#061936,#123a75,#2563eb);padding:28px;border-radius:28px;color:white;margin-bottom:24px}
.hero h1{font-size:36px;font-weight:900;margin-bottom:4px}
.hero p{color:#dbeafe}
.card{background:white;padding:24px;border-radius:24px;border:1px solid #e5eaf3;box-shadow:0 12px 32px rgba(15,23,42,.08);margin-bottom:20px}
.kpi{background:white;padding:22px;border-radius:22px;border:1px solid #e5eaf3;box-shadow:0 12px 32px rgba(15,23,42,.08);min-height:140px}
.kpi-label{font-size:13px;color:#64748b;font-weight:800;text-transform:uppercase}
.kpi-value{font-size:27px;font-weight:900;color:#071735;margin-top:10px}
.good{color:#059669;font-weight:800;font-size:13px}
.mid{color:#d97706;font-weight:800;font-size:13px}
.bad{color:#dc2626;font-weight:800;font-size:13px}
.metric-line{display:flex;justify-content:space-between;border-bottom:1px solid #edf2f7;padding:10px 0;font-size:14px}
.metric-line span{color:#64748b}.metric-line b{color:#0f172a;text-align:right}
</style>
""", unsafe_allow_html=True)


def moeda(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"


def pct(v):
    try:
        return f"{float(v):.2f}%".replace(".", ",")
    except:
        return "0,00%"


def num(v):
    if v is None:
        return 0.0
    t = str(v).replace("R$", "").replace("m²", "").replace("m2", "")
    t = re.sub(r"[^\d,\.]", "", t)
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except:
        return 0.0


def ler_pdf(file):
    texto = ""
    linhas_tabela = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texto += "\n" + t

            try:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        linha = " | ".join([str(c) for c in row if c not in [None, ""]])
                        if linha.strip():
                            linhas_tabela.append(linha)
            except:
                pass

    return texto, linhas_tabela


def buscar_apartamento(texto, linhas_tabela, apto):
    apto = str(apto).strip()
    encontrados = []

    todas_linhas = []

    for l in texto.splitlines():
        if l.strip():
            todas_linhas.append(l.strip())

    todas_linhas += linhas_tabela

    for i, linha in enumerate(todas_linhas):
        if re.search(rf"\b{re.escape(apto)}\b", linha):
            contexto = []
            for j in range(max(0, i - 2), min(len(todas_linhas), i + 3)):
                contexto.append(todas_linhas[j])
            encontrados.append(" ".join(contexto))

    if not encontrados:
        return None, []

    bloco = " ".join(encontrados)

    valores = re.findall(r"R\$\s*[\d\.\,]+", bloco)
    valores_num = [num(v) for v in valores if num(v) > 1000]

    areas = re.findall(r"(\d{2,3}(?:[\.,]\d{1,2})?)\s*(?:m²|m2)", bloco.lower())
    areas_num = [num(a) for a in areas if num(a) > 10]

    vagas = re.findall(r"(\d+)\s*(?:vaga|vagas)", bloco.lower())
    vagas_num = [int(v) for v in vagas if int(v) <= 6]

    dados = {
        "unidade": apto,
        "linha_encontrada": bloco,
    }

    if valores_num:
        dados["preco_total"] = max(valores_num)

    if areas_num:
        dados["area"] = areas_num[0]

    if vagas_num:
        dados["vagas"] = vagas_num[0]

    return dados, encontrados


def criar_fluxo(d):
    preco = float(d["preco_total"])
    entrada = float(d["entrada"])
    parcela = float(d["valor_parcela"])
    qtd = int(d["qtd_parcelas"])
    entrega = int(d["prazo_entrega"])
    total = int(d["prazo_total"])

    cub_m = (1 + float(d["cub_anual"]) / 100) ** (1 / 12) - 1
    val_m = (1 + float(d["valorizacao_anual"]) / 100) ** (1 / 12) - 1

    investido = entrada
    rows = []

    for mes in range(1, total + 1):
        pagamento = 0

        if mes <= qtd:
            pagamento += parcela * ((1 + cub_m) ** mes)

        for r in d["reforcos_pre"]:
            if mes <= entrega and mes % int(r["intervalo"]) == 0:
                pagamento += float(r["valor"])

        for r in d["reforcos_pos"]:
            mes_pos = mes - entrega
            if mes > entrega and mes_pos % int(r["intervalo"]) == 0:
                pagamento += float(r["valor"])

        investido += pagamento
        valor_proj = preco * ((1 + val_m) ** mes)
        lucro = valor_proj - investido
        roi = lucro / investido * 100 if investido > 0 else 0

        rows.append({
            "Mês": mes,
            "Fase": "Antes da entrega" if mes <= entrega else "Depois da entrega",
            "Pagamento Mensal": pagamento,
            "Total Investido": investido,
            "Valor Projetado": valor_proj,
            "Lucro Bruto": lucro,
            "ROI %": roi
        })

    return pd.DataFrame(rows)


def score(d, valor_m2, roi):
    nota = 5

    if roi >= 80:
        nota += 2
    elif roi >= 50:
        nota += 1.5
    elif roi >= 30:
        nota += 1
    elif roi < 15:
        nota -= 1

    ref = float(d["valor_m2_ref"])
    if ref > 0:
        desconto = (ref - valor_m2) / ref
        if desconto >= .15:
            nota += 1.5
        elif desconto >= .05:
            nota += .8
        elif desconto < -.05:
            nota -= 1

    if d["risco"] == "Baixo":
        nota += 1
    elif d["risco"] == "Alto":
        nota -= 1

    return max(0, min(10, nota))


def grafico(df, y, titulo):
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
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=15, r=15, t=50, b=15)
    )
    return fig


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
        "reforcos_pre": [{"intervalo": 6, "valor": 30000.0}, {"intervalo": 10, "valor": 50000.0}],
        "reforcos_pos": [{"intervalo": 6, "valor": 25000.0}, {"intervalo": 10, "valor": 40000.0}],
    }

if "pdf_texto" not in st.session_state:
    st.session_state.pdf_texto = ""

if "pdf_linhas" not in st.session_state:
    st.session_state.pdf_linhas = []

if "ultimo_resultado_apto" not in st.session_state:
    st.session_state.ultimo_resultado_apto = None


d = st.session_state.dados

with st.sidebar:
    st.markdown("## 🏢 ImobInvest Pro")
    st.caption("PAINEL EXECUTIVO")

    menu = st.radio(
        "Menu",
        [
            "Painel Executivo",
            "Importar PDF e Buscar Apto",
            "Cadastro Manual",
            "Fluxo de Pagamento",
            "Cenários",
        ],
        label_visibility="collapsed"
    )


if menu == "Importar PDF e Buscar Apto":
    st.markdown("""
    <div class="hero">
        <h1>Importar PDF e Buscar Apartamento</h1>
        <p>Envie o PDF da construtora, digite o número do apartamento e o app usa a linha daquela unidade como base.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    arquivo = st.file_uploader("Enviar PDF da construtora", type=["pdf"])

    if arquivo:
        texto, linhas = ler_pdf(arquivo)
        st.session_state.pdf_texto = texto
        st.session_state.pdf_linhas = linhas
        st.success("PDF carregado. Agora digite o número do apartamento.")

    apto_busca = st.text_input("Digite o número do apartamento/unidade", value=str(d["unidade"]))

    if st.button("Buscar apartamento no PDF"):
        if not st.session_state.pdf_texto and not st.session_state.pdf_linhas:
            st.error("Primeiro envie o PDF.")
        else:
            resultado, encontrados = buscar_apartamento(
                st.session_state.pdf_texto,
                st.session_state.pdf_linhas,
                apto_busca
            )

            if resultado:
                st.session_state.ultimo_resultado_apto = resultado
                st.success(f"Apartamento {apto_busca} encontrado no PDF.")
            else:
                st.error("Não encontrei esse apartamento no PDF. Confira se o número está exatamente igual.")

    if st.session_state.ultimo_resultado_apto:
        r = st.session_state.ultimo_resultado_apto

        st.markdown("### Dados encontrados para essa unidade")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            preco_pdf = st.number_input(
                "Preço encontrado",
                value=float(r.get("preco_total", d["preco_total"])),
                step=10000.0
            )

        with c2:
            area_pdf = st.number_input(
                "Área encontrada",
                value=float(r.get("area", d["area"])),
                step=1.0
            )

        with c3:
            unidade_pdf = st.text_input(
                "Unidade encontrada",
                value=str(r.get("unidade", d["unidade"]))
            )

        with c4:
            vagas_pdf = st.number_input(
                "Vagas encontradas",
                value=int(r.get("vagas", d["vagas"])),
                min_value=0
            )

        st.text_area("Trecho do PDF usado como base", r.get("linha_encontrada", ""), height=180)

        if st.button("Aplicar essa unidade no painel"):
            d["preco_total"] = preco_pdf
            d["area"] = area_pdf
            d["unidade"] = unidade_pdf
            d["vagas"] = vagas_pdf
            st.session_state.dados = d
            st.success("Unidade aplicada no painel. Agora vá em Painel Executivo.")

    with st.expander("Ver texto completo extraído do PDF"):
        st.text_area("Texto", st.session_state.pdf_texto, height=300)

    with st.expander("Ver linhas de tabela extraídas"):
        st.write(st.session_state.pdf_linhas)

    st.markdown('</div>', unsafe_allow_html=True)


elif menu == "Cadastro Manual":
    st.markdown("""
    <div class="hero">
        <h1>Cadastro Manual</h1>
        <p>Ajuste os dados do imóvel e as premissas da análise.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        d["empreendimento"] = st.text_input("Empreendimento", d["empreendimento"])
        d["construtora"] = st.text_input("Construtora", d["construtora"])
        d["localizacao"] = st.text_input("Localização", d["localizacao"])

    with c2:
        d["unidade"] = st.text_input("Unidade", d["unidade"])
        d["tipo"] = st.selectbox("Tipo", ["Apartamento", "Flat", "Casa", "Terreno", "Sala Comercial"], index=0)
        d["vagas"] = st.number_input("Vagas", value=int(d["vagas"]), min_value=0)

    with c3:
        d["area"] = st.number_input("Área privativa m²", value=float(d["area"]), min_value=1.0)
        d["preco_total"] = st.number_input("Preço total", value=float(d["preco_total"]), step=10000.0)
        d["valor_m2_ref"] = st.number_input("Valor m² médio da região", value=float(d["valor_m2_ref"]), step=500.0)

    c4, c5, c6, c7 = st.columns(4)

    with c4:
        d["valorizacao_anual"] = st.slider("Valorização anual", 0.0, 30.0, float(d["valorizacao_anual"]), 0.5)

    with c5:
        d["cub_anual"] = st.slider("CUB anual", 0.0, 15.0, float(d["cub_anual"]), 0.1)

    with c6:
        d["risco"] = st.selectbox("Risco", ["Baixo", "Médio", "Alto"], index=["Baixo", "Médio", "Alto"].index(d["risco"]))

    with c7:
        d["liquidez"] = st.selectbox("Liquidez", ["Alta", "Média", "Baixa"], index=["Alta", "Média", "Baixa"].index(d["liquidez"]))

    d["perfil"] = st.text_input("Perfil ideal", d["perfil"])

    st.session_state.dados = d
    st.success("Dados salvos.")
    st.markdown('</div>', unsafe_allow_html=True)


elif menu == "Fluxo de Pagamento":
    st.markdown("""
    <div class="hero">
        <h1>Fluxo de Pagamento</h1>
        <p>Configure parcelas e reforços antes/depois da entrega.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

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

    st.markdown("### Reforços antes da entrega")
    qtd_pre = st.number_input("Quantidade de tipos de reforço antes", min_value=0, max_value=10, value=len(d["reforcos_pre"]))

    novos_pre = []
    for i in range(qtd_pre):
        base = d["reforcos_pre"][i] if i < len(d["reforcos_pre"]) else {"intervalo": 6, "valor": 0}
        a, b = st.columns(2)
        with a:
            intervalo = st.number_input(f"Antes #{i+1} - repetir a cada X meses", min_value=1, value=int(base["intervalo"]), key=f"pre_i_{i}")
        with b:
            valor = st.number_input(f"Antes #{i+1} - valor", min_value=0.0, value=float(base["valor"]), step=5000.0, key=f"pre_v_{i}")
        novos_pre.append({"intervalo": intervalo, "valor": valor})

    st.markdown("### Reforços depois da entrega")
    qtd_pos = st.number_input("Quantidade de tipos de reforço depois", min_value=0, max_value=10, value=len(d["reforcos_pos"]))

    novos_pos = []
    for i in range(qtd_pos):
        base = d["reforcos_pos"][i] if i < len(d["reforcos_pos"]) else {"intervalo": 6, "valor": 0}
        a, b = st.columns(2)
        with a:
            intervalo = st.number_input(f"Depois #{i+1} - repetir a cada X meses", min_value=1, value=int(base["intervalo"]), key=f"pos_i_{i}")
        with b:
            valor = st.number_input(f"Depois #{i+1} - valor", min_value=0.0, value=float(base["valor"]), step=5000.0, key=f"pos_v_{i}")
        novos_pos.append({"intervalo": intervalo, "valor": valor})

    d["reforcos_pre"] = novos_pre
    d["reforcos_pos"] = novos_pos
    st.session_state.dados = d

    st.success("Fluxo salvo.")
    st.markdown('</div>', unsafe_allow_html=True)


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
nota = score(d, valor_m2, roi_entrega)


if menu == "Painel Executivo":
    st.markdown(f"""
    <div class="hero">
        <h1>Painel Executivo</h1>
        <p>{d["empreendimento"]} | Unidade {d["unidade"]} | {d["localizacao"]}</p>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Preço</div><div class="kpi-value">{moeda(d["preco_total"])}</div><div class="mid">Tabela</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Valor por m²</div><div class="kpi-value">{moeda(valor_m2)}</div><div class="good">Ref.: {moeda(d["valor_m2_ref"])}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Valor na entrega</div><div class="kpi-value">{moeda(valor_entrega)}</div><div class="good">{pct(d["valorizacao_anual"])} a.a.</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Lucro na entrega</div><div class="kpi-value">{moeda(lucro_entrega)}</div><div class="good">ROI {pct(roi_entrega)}</div></div>', unsafe_allow_html=True)
    with k5:
        classe = "good" if nota >= 7 else "mid" if nota >= 5 else "bad"
        st.markdown(f'<div class="kpi"><div class="kpi-label">Score</div><div class="kpi-value">{nota:.1f}/10</div><div class="{classe}">Nota executiva</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(grafico(df, "Valor Projetado", "Evolução Projetada do Imóvel"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(grafico(df, "Lucro Bruto", "Lucro Bruto Projetado"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4, c5 = st.columns(3)

    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Resumo do Ativo")
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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Indicadores")
        st.markdown(f"""
        <div class="metric-line"><span>Investido até entrega</span><b>{moeda(investido_entrega)}</b></div>
        <div class="metric-line"><span>Aporte médio mensal</span><b>{moeda(media_mensal)}</b></div>
        <div class="metric-line"><span>Valor final projetado</span><b>{moeda(valor_final)}</b></div>
        <div class="metric-line"><span>Lucro final</span><b>{moeda(lucro_final)}</b></div>
        <div class="metric-line"><span>ROI final</span><b>{pct(roi_final)}</b></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Diagnóstico")
        if nota >= 8:
            st.success("Excelente oportunidade")
        elif nota >= 6:
            st.warning("Boa oportunidade")
        else:
            st.error("Cautela")
        st.write(f"Risco: **{d['risco']}**")
        st.write(f"Liquidez: **{d['liquidez']}**")
        st.write(f"Perfil: **{d['perfil']}**")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Fluxo Executivo")
    df_show = df.copy()
    for col in ["Pagamento Mensal", "Total Investido", "Valor Projetado", "Lucro Bruto"]:
        df_show[col] = df_show[col].apply(moeda)
    df_show["ROI %"] = df_show["ROI %"].apply(pct)
    st.dataframe(df_show, use_container_width=True, height=380)
    st.markdown('</div>', unsafe_allow_html=True)


elif menu == "Cenários":
    st.markdown("""
    <div class="hero">
        <h1>Cenários</h1>
        <p>Conservador, base e agressivo.</p>
    </div>
    """, unsafe_allow_html=True)

    cenarios = []

    for nome, valorizacao in [("Conservador", 8), ("Base", d["valorizacao_anual"]), ("Agressivo", 15)]:
        temp = d.copy()
        temp["valorizacao_anual"] = valorizacao
        temp_df = criar_fluxo(temp)
        ent = temp_df[temp_df["Mês"] == int(temp["prazo_entrega"])].iloc[0]
        fim = temp_df.iloc[-1]

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

    dfc = pd.DataFrame(cenarios)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(dfc, x="Cenário", y="Lucro na Entrega", text_auto=".2s")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(dfc, x="Cenário", y="ROI na Entrega", text_auto=".2s")
        st.plotly_chart(fig, use_container_width=True)

    df_view = dfc.copy()
    for col in ["Valor na Entrega", "Lucro na Entrega", "Valor Final", "Lucro Final"]:
        df_view[col] = df_view[col].apply(moeda)
    for col in ["Valorização Anual", "ROI na Entrega", "ROI Final"]:
        df_view[col] = df_view[col].apply(pct)

    st.dataframe(df_view, use_container_width=True)
