import streamlit as st
import pandas as pd
import io

# Configuração da página
st.set_page_config(page_title="Calculadora de Custo do Colaborador", layout="wide")
st.title("💼 Calculadora de Custo do Colaborador")

# Função de cálculo detalhado
def calcular_detalhado(salario, plr, ajuste_percentual):
    salario_ajustado = salario * (1 + ajuste_percentual / 100)
    ferias_12 = salario_ajustado / 12
    um_terco_ferias = ferias_12 / 3
    decimo_terceiro = salario_ajustado / 12
    plr_12 = plr / 12
    va_vr = 2057.92
    assist_medica = 978.00

    base_encargos = salario_ajustado + ferias_12 + um_terco_ferias + decimo_terceiro
    inss = base_encargos * 0.282
    fgts = base_encargos * 0.08

    custo_mensal = salario_ajustado + ferias_12 + um_terco_ferias + decimo_terceiro + plr_12 + va_vr + assist_medica + inss + fgts
    return {
        "Salário Ajustado": salario_ajustado,
        "Férias": ferias_12,
        "1/3 Férias": um_terco_ferias,
        "13º": decimo_terceiro,
        "PLR": plr_12,
        "VA/VR": va_vr,
        "Assist. Médica": assist_medica,
        "INSS": inss,
        "FGTS": fgts,
        "Total Mensal": custo_mensal
    }

# Inicializa sessão
if "colaboradores" not in st.session_state:
    st.session_state.colaboradores = []

# Sidebar para inclusão manual
st.sidebar.subheader("➕ Adicionar colaborador manualmente")
nome = st.sidebar.text_input("Nome")
salario = st.sidebar.number_input("Salário (R$)", min_value=0.0, step=1000.0, format="%.2f")
plr = st.sidebar.number_input("PLR Anual (R$)", min_value=0.0, step=1000.0, format="%.2f")
ajuste = st.sidebar.number_input("Ajuste de salário (%)", min_value=0.0, step=1.0, format="%.1f")

if st.sidebar.button("Adicionar colaborador"):
    if nome:
        st.session_state.colaboradores.append({"Nome": nome, "Salário": salario, "PLR": plr, "Ajuste (%)": ajuste})
    else:
        st.sidebar.warning("Por favor, insira o nome do colaborador.")

# Upload de planilha
st.subheader("📤 Ou envie uma planilha Excel com os dados")
arquivo = st.file_uploader("Importar colaboradores (xlsx)", type=["xlsx"])

if arquivo:
    df_upload = pd.read_excel(arquivo)
    obrigatorias = {"Nome", "Salário", "PLR", "Ajuste (%)"}
    if obrigatorias.issubset(set(df_upload.columns)):
        novos = df_upload[["Nome", "Salário", "PLR", "Ajuste (%)"]].to_dict(orient="records")
        st.session_state.colaboradores.extend(novos)
        st.success("Colaboradores importados com sucesso!")
    else:
        st.error(f"A planilha deve conter as colunas: {obrigatorias}")

# Exibir resultados
if st.session_state.colaboradores:
    df_base = pd.DataFrame(st.session_state.colaboradores)

    detalhes = []
    for i, row in df_base.iterrows():
        resultado = calcular_detalhado(row["Salário"], row["PLR"], row["Ajuste (%)"])
        detalhes.append(resultado)

    df_detalhado = pd.DataFrame(detalhes)
    df_final = pd.concat([df_base, df_detalhado], axis=1)

    st.subheader("📋 Tabela de colaboradores com custo detalhado")

    # ✅ Formatação segura
    df_formatado = df_final.copy()
    colunas_valores = df_formatado.select_dtypes(include=['float', 'int']).columns

    for col in colunas_valores:
        df_formatado[col] = df_formatado[col].apply(
            lambda x: f"R$ {x:,.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else x
        )

    st.dataframe(df_formatado, use_container_width=True)

    # Gráfico de pizza
    st.subheader("📊 Distribuição do custo total da equipe")
    resumo = df_final[["Salário Ajustado", "Férias", "1/3 Férias", "13º", "PLR", "VA/VR", "Assist. Médica", "INSS", "FGTS"]].sum()
    st.pyplot(resumo.plot.pie(autopct="%1.1f%%", figsize=(7, 7), title="Custo total por componente").figure)

    # Exportar Excel
    st.subheader("⬇️ Exportar resultado")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Custo por Colaborador")
    st.download_button("📥 Baixar Excel", data=buffer.getvalue(), file_name="custo_colaboradores.xlsx", mime="application/vnd.ms-excel")
else:
    st.info("Adicione colaboradores manualmente ou importe uma planilha para começar.")
