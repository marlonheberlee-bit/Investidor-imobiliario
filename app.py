import re
import math
from datetime import date
from typing import List, Dict, Optional, Tuple

import pandas as pd
import streamlit as st

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None
    Image = None

st.set_page_config(
    page_title="Analisador Imobiliário com Leitor de PDF",
    page_icon="🏢",
    layout="wide",
)

def brl_to_float(valor: str) -> float:
    if not valor:
        return 0.0
    v = str(valor).replace("R$", "").replace(" ", "").strip()
    v = v.replace(".", "").replace(",", ".")
    try:
        return float(v)
    except Exception:
        return 0.0

def float_to_brl(valor: float) -> str:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        valor = 0
    s = f"R$ {valor:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def pct(valor: float) -> str:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        valor = 0
    return f"{valor:.2f}%".replace(".", ",")

def normalizar_texto(txt: str) -> str:
    txt = txt.replace("\xa0", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    return txt

def extrair_texto_pdf(uploaded_file, usar_ocr=False) -> List[Dict]:
    paginas = []
    if pdfplumber is None:
        st.error("Biblioteca pdfplumber não encontrada. Instale com: pip install pdfplumber")
        return paginas

    with pdfplumber.open(uploaded_file) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            texto = page.extract_text() or ""
            texto = normalizar_texto(texto)

            if usar_ocr and len(texto.strip()) < 100 and pytesseract is not None:
                try:
                    img = page.to_image(resolution=200).original
                    texto_ocr = pytesseract.image_to_string(img, lang="por+eng")
                    texto = normalizar_texto(texto_ocr)
                except Exception:
                    pass

            paginas.append({"pagina": i, "texto": texto})
    return paginas

def extrair_reais(linha: str) -> List[str]:
    return re.findall(r"R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", linha)

def extrair_parcela(linha: str) -> Tuple[Optional[int], Optional[float]]:
    m = re.search(r"(\d+)\s*x\s*R\$\s?\d{1,3}(?:\.\d{3})*,\d{2}", linha, flags=re.I)
    if not m:
        return None, None
    qtd = int(m.group(1))
    trecho = linha[m.start():m.end()]
    valores = extrair_reais(trecho)
    valor = brl_to_float(valores[0]) if valores else 0.0
    return qtd, valor

def parse_unidades_expr(expr: str) -> List[int]:
    expr = expr.strip()
    expr = re.sub(r"[^0-9eao\s]", " ", expr, flags=re.I)
    expr = re.sub(r"\s+", " ", expr).strip()

    nums = [int(x) for x in re.findall(r"\d{3,4}", expr)]
    unidades = set()

    if " ao " in f" {expr.lower()} " and len(nums) >= 2:
        ini, fim = nums[0], nums[1]
        sufixo_ini, sufixo_fim = ini % 100, fim % 100
        andar_ini, andar_fim = ini // 100, fim // 100

        if sufixo_ini == sufixo_fim and andar_ini <= andar_fim:
            for andar in range(andar_ini, andar_fim + 1):
                unidades.add(andar * 100 + sufixo_ini)
        elif ini <= fim:
            for u in range(ini, fim + 1):
                unidades.add(u)
    else:
        for n in nums:
            unidades.add(n)

    return sorted(unidades)

def extrair_expr_apartamento(linha: str) -> str:
    parte = linha.split("R$")[0].strip()
    parte = re.sub(r"^(TIPO\s*\d+\s*)", "", parte, flags=re.I).strip()
    return parte

def identificar_torre_entrega(texto_pagina: str):
    torre = None
    entrega = None
    localizacao = None

    m = re.search(r"TORRE\s*(\d+)\s*-\s*ENTREGA\s*EM\s*(\d{4})", texto_pagina, flags=re.I)
    if m:
        torre = f"TORRE {int(m.group(1)):02d}"
        entrega = int(m.group(2))

    mloc = re.search(r"LOCALIZAÇÃO\s*-\s*(.+?)(?:Disponível|TIPO|\n|$)", texto_pagina, flags=re.I)
    if mloc:
        localizacao = mloc.group(1).strip()

    return torre, entrega, localizacao

def extrair_tipos(texto_total: str) -> Dict[str, Dict]:
    tipos = {}
    for m in re.finditer(r"TIPO\s*(\d{1,2}).{0,120}?(\d{2,3},\d{2})\s*m²", texto_total, flags=re.I | re.S):
        cod = m.group(1).zfill(2)
        area = brl_to_float(m.group(2))
        tipos[cod] = {"tipo": f"TIPO {cod}", "area_m2": area}
    return tipos

def parsear_linhas(paginas: List[Dict]) -> pd.DataFrame:
    registros = []
    texto_total = "\n".join(p["texto"] for p in paginas)
    tipos = extrair_tipos(texto_total)

    for p in paginas:
        pagina = p["pagina"]
        texto = p["texto"]
        torre, entrega, localizacao = identificar_torre_entrega(texto)

        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        for linha in linhas:
            valores = extrair_reais(linha)
            tem_parcela = re.search(r"\d+\s*x\s*R\$", linha, flags=re.I)

            if len(valores) >= 4 and tem_parcela:
                expr_apt = extrair_expr_apartamento(linha)
                unidades = parse_unidades_expr(expr_apt)
                qtd_parcelas, valor_parcela = extrair_parcela(linha)

                entrada = brl_to_float(valores[0])
                total = brl_to_float(valores[-1])
                reforcos = [brl_to_float(v) for v in valores[2:-1]] if len(valores) >= 5 else []

                reforco_antes = reforcos[0] if len(reforcos) >= 1 else 0
                reforco_depois = reforcos[1] if len(reforcos) >= 2 else 0

                for unidade in unidades:
                    final_tipo = str(unidade)[-2:]
                    info_tipo = tipos.get(final_tipo, {})

                    registros.append({
                        "pagina": pagina,
                        "torre": torre,
                        "entrega": entrega,
                        "localizacao": localizacao,
                        "apartamento": str(unidade),
                        "grupo_pdf": expr_apt,
                        "tipo": info_tipo.get("tipo", f"TIPO {final_tipo}"),
                        "area_m2": info_tipo.get("area_m2", None),
                        "entrada": entrada,
                        "qtd_parcelas": qtd_parcelas or 0,
                        "valor_parcela": valor_parcela or 0,
                        "reforco_antes_entrega": reforco_antes,
                        "reforco_depois_entrega": reforco_depois,
                        "total_tabela": total,
                        "linha_original": linha,
                    })

    df = pd.DataFrame(registros)

    if not df.empty:
        df = df.drop_duplicates(
            subset=["torre", "apartamento", "entrada", "valor_parcela", "total_tabela"]
        )

    return df

def calcular_investimento(row, valorizacao_anual, cub_anual, ano_atual, ano_venda, considerar_cub):
    entrega = int(row.get("entrega") or ano_atual)
    meses_total = int(row.get("qtd_parcelas") or 0)
    valor_parcela = float(row.get("valor_parcela") or 0)
    entrada = float(row.get("entrada") or 0)
    total_tabela = float(row.get("total_tabela") or 0)
    reforco_antes = float(row.get("reforco_antes_entrega") or 0)
    reforco_depois = float(row.get("reforco_depois_entrega") or 0)

    meses_ate_entrega = max(0, (entrega - ano_atual) * 12)
    meses_ate_venda = max(0, (ano_venda - ano_atual) * 12)

    tx_val_mensal = (1 + valorizacao_anual / 100) ** (1 / 12) - 1
    tx_cub_mensal = (1 + cub_anual / 100) ** (1 / 12) - 1

    fluxo = []
    saldo_aportado = entrada

    fluxo.append({
        "mes": 0,
        "descricao": "Entrada",
        "aporte": entrada,
        "valor_imovel": total_tabela,
    })

    for mes in range(1, meses_ate_venda + 1):
        fator_cub = ((1 + tx_cub_mensal) ** mes) if considerar_cub else 1
        aporte = 0.0
        descricao = []

        if mes <= meses_total:
            aporte += valor_parcela * fator_cub
            descricao.append("Parcela")

        if reforco_antes > 0 and mes <= meses_ate_entrega and mes % 6 == 0:
            aporte += reforco_antes * fator_cub
            descricao.append("Reforço antes da entrega")

        if reforco_depois > 0 and mes > meses_ate_entrega and mes <= meses_total and mes % 6 == 0:
            aporte += reforco_depois * fator_cub
            descricao.append("Reforço depois da entrega")

        saldo_aportado += aporte
        valor_imovel = total_tabela * ((1 + tx_val_mensal) ** mes)

        fluxo.append({
            "mes": mes,
            "descricao": ", ".join(descricao) if descricao else "",
            "aporte": aporte,
            "valor_imovel": valor_imovel,
        })

    valor_venda = total_tabela * ((1 + tx_val_mensal) ** meses_ate_venda)
    lucro_bruto = valor_venda - saldo_aportado

    roi_total = (lucro_bruto / saldo_aportado * 100) if saldo_aportado > 0 else 0

    if meses_ate_venda > 0 and saldo_aportado > 0:
        roi_ano = ((1 + roi_total / 100) ** (12 / meses_ate_venda) - 1) * 100
    else:
        roi_ano = 0

    preco_m2 = total_tabela / row.get("area_m2") if row.get("area_m2") else None

    nota = 5.0

    if roi_ano >= 25:
        nota += 2.0
    elif roi_ano >= 18:
        nota += 1.5
    elif roi_ano >= 12:
        nota += 1.0
    elif roi_ano >= 8:
        nota += 0.5
    else:
        nota -= 0.5

    if meses_ate_entrega <= 36:
        nota += 0.8
    elif meses_ate_entrega >= 60:
        nota -= 0.5

    if preco_m2 and preco_m2 < 16000:
        nota += 0.7
    elif preco_m2 and preco_m2 > 22000:
        nota -= 0.7

    nota = max(0, min(10, nota))

    resumo = {
        "meses_ate_entrega": meses_ate_entrega,
        "meses_ate_venda": meses_ate_venda,
        "valor_venda_projetado": valor_venda,
        "valor_aportado_ate_venda": saldo_aportado,
        "lucro_bruto": lucro_bruto,
        "roi_total": roi_total,
        "roi_ano": roi_ano,
        "preco_m2": preco_m2,
        "nota": nota,
    }

    return resumo, pd.DataFrame(fluxo)

st.title("🏢 Analisador Imobiliário Profissional + Leitor de PDF")
st.caption("Upload de tabela da construtora, busca por apartamento e relatório automático de investimento.")

with st.sidebar:
    st.header("Parâmetros de análise")

    ano_atual = st.number_input(
        "Ano base",
        min_value=2024,
        max_value=2040,
        value=date.today().year,
        step=1,
    )

    ano_venda = st.number_input(
        "Ano projetado para venda",
        min_value=int(ano_atual),
        max_value=2050,
        value=max(int(ano_atual) + 5, 2031),
        step=1,
    )

    valorizacao_anual = st.slider(
        "Valorização anual esperada",
        0.0,
        30.0,
        12.0,
        0.5,
    )

    cub_anual = st.slider(
        "CUB/INCC anual estimado",
        0.0,
        20.0,
        4.3,
        0.1,
    )

    considerar_cub = st.checkbox(
        "Corrigir parcelas/reforços pelo CUB estimado",
        value=True,
    )

    usar_ocr = st.checkbox(
        "Tentar OCR se o PDF vier como imagem",
        value=False,
    )

uploaded = st.file_uploader("Envie o PDF da construtora", type=["pdf"])

if uploaded:
    paginas = extrair_texto_pdf(uploaded, usar_ocr=usar_ocr)
    df = parsear_linhas(paginas)

    if df.empty:
        st.error("Não consegui estruturar a tabela financeira automaticamente. Tente ativar OCR ou envie outro PDF.")
        with st.expander("Ver texto bruto extraído"):
            st.text("\n\n".join([p["texto"] for p in paginas])[:20000])
        st.stop()

    st.success(f"PDF lido com sucesso. {len(df)} unidades/linhas interpretadas.")

    col_busca1, col_busca2 = st.columns([1, 1])

    with col_busca1:
        unidade_digitada = st.text_input(
            "Digite o número do apartamento/unidade",
            placeholder="Ex: 1203",
        )

    with col_busca2:
        torre_filtro = st.selectbox(
            "Filtrar torre",
            ["Todas"] + sorted([x for x in df["torre"].dropna().unique()]),
        )

    df_filtrado = df.copy()

    if torre_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["torre"] == torre_filtro]

    if unidade_digitada:
        unidade_limpa = re.sub(r"\D", "", unidade_digitada)
        df_match = df_filtrado[df_filtrado["apartamento"].astype(str) == unidade_limpa]
    else:
        df_match = pd.DataFrame()

    aba1, aba2, aba3 = st.tabs([
        "🔎 Resultado da unidade",
        "📊 Base extraída",
        "🧾 Texto bruto",
    ])

    with aba1:
        if unidade_digitada and not df_match.empty:
            if len(df_match) > 1:
                st.info("Essa unidade apareceu em mais de uma torre/linha. Escolha abaixo qual deseja analisar.")

            opcoes = []

            for idx, r in df_match.iterrows():
                opcoes.append((
                    idx,
                    f"{r['torre']} | Apto {r['apartamento']} | Entrega {r['entrega']} | Total {float_to_brl(r['total_tabela'])}",
                ))

            escolhido = st.selectbox(
                "Selecione a opção",
                opcoes,
                format_func=lambda x: x[1],
            )

            row = df.loc[escolhido[0]]

            resumo, fluxo = calcular_investimento(
                row,
                valorizacao_anual,
                cub_anual,
                int(ano_atual),
                int(ano_venda),
                considerar_cub,
            )

            st.subheader(f"Relatório — {row['torre']} | Apartamento {row['apartamento']}")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Preço total", float_to_brl(row["total_tabela"]))
            c2.metric("Entrada", float_to_brl(row["entrada"]))
            c3.metric("Parcela", f"{int(row['qtd_parcelas'])}x {float_to_brl(row['valor_parcela'])}")
            c4.metric("Nota", f"{resumo['nota']:.1f}/10".replace(".", ","))

            c5, c6, c7, c8 = st.columns(4)

            c5.metric("Valor projetado venda", float_to_brl(resumo["valor_venda_projetado"]))
            c6.metric("Total aportado até venda", float_to_brl(resumo["valor_aportado_ate_venda"]))
            c7.metric("Lucro bruto", float_to_brl(resumo["lucro_bruto"]))
            c8.metric("ROI anual aprox.", pct(resumo["roi_ano"]))

            st.markdown("### Dados extraídos do PDF")

            dados = {
                "Torre": row["torre"],
                "Entrega": row["entrega"],
                "Localização": row["localizacao"],
                "Grupo no PDF": row["grupo_pdf"],
                "Tipo": row["tipo"],
                "Área privativa": f"{row['area_m2']:.2f} m²".replace(".", ",") if pd.notna(row["area_m2"]) else "Não identificado",
                "Preço por m²": float_to_brl(resumo["preco_m2"]) if resumo["preco_m2"] else "Não identificado",
                "Reforço antes da entrega": float_to_brl(row["reforco_antes_entrega"]),
                "Reforço depois da entrega": float_to_brl(row["reforco_depois_entrega"]),
            }

            st.dataframe(
                pd.DataFrame(dados.items(), columns=["Campo", "Valor"]),
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("### Leitura estratégica")

            if resumo["nota"] >= 8:
                st.success("Oportunidade forte: bom potencial de ganho em relação ao capital aportado, considerando os parâmetros informados.")
            elif resumo["nota"] >= 6.5:
                st.warning("Oportunidade razoável: exige comparação com outras unidades e validação do preço de mercado.")
            else:
                st.error("Oportunidade fraca nos parâmetros atuais: atenção ao prazo, preço/m², fluxo e valorização assumida.")

            st.markdown("### Fluxo projetado")

            fluxo_view = fluxo.copy()
            fluxo_view["aporte"] = fluxo_view["aporte"].apply(float_to_brl)
            fluxo_view["valor_imovel"] = fluxo_view["valor_imovel"].apply(float_to_brl)

            st.dataframe(
                fluxo_view,
                use_container_width=True,
                hide_index=True,
            )

            csv = fluxo.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                "Baixar fluxo em CSV",
                data=csv,
                file_name=f"fluxo_apto_{row['apartamento']}.csv",
                mime="text/csv",
            )

            with st.expander("Linha original encontrada no PDF"):
                st.code(row["linha_original"])

        elif unidade_digitada:
            st.warning("Não encontrei essa unidade na base extraída. Tente selecionar 'Todas' as torres ou confira o número.")
        else:
            st.info("Digite uma unidade para gerar o relatório automático.")

    with aba2:
        df_view = df.copy()

        for col in [
            "entrada",
            "valor_parcela",
            "reforco_antes_entrega",
            "reforco_depois_entrega",
            "total_tabela",
            "area_m2",
        ]:
            if col in df_view.columns:
                if col != "area_m2":
                    df_view[col] = df_view[col].apply(float_to_brl)

        st.dataframe(
            df_view.drop(columns=["linha_original"], errors="ignore"),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Baixar base extraída em CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="base_extraida_pdf.csv",
            mime="text/csv",
        )

    with aba3:
        for p in paginas:
            with st.expander(f"Página {p['pagina']}"):
                st.text(p["texto"][:15000])

else:
    st.info("Envie um PDF para começar.")
