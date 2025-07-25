import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Configuração da página
st.set_page_config(page_title="Calculadora de Custo do Colaborador", layout="wide")
st.title("💼 Calculadora de Custo do Colaborador")

# Inicializa a sessão
if "colaboradores" not in st.session_state:
    st.session_state.colaboradores = []

# Carrega nomes sugeridos do Excel externo
try:
    nomes_df = pd.read_excel("lista_nomes.xlsx")
    nomes_sugeridos = nomes_df["Nome da Pessoa"].dropna().astype(str).tolist()
except Exception:
    nomes_sugeridos = []

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
    custo_anual = custo_mensal * 12

    return {
        "Salário Ajustado": salario_ajustado,
        "Férias": ferias_12,
        "1/3 Férias": um_terco_ferias,
        "13º": decimo_terceiro,
        "PLR (mensalizada)": plr_12,
        "VA/VR": va_vr,
        "Assist. Médica": assist_medica,
        "INSS": inss,
        "FGTS": fgts,
        "Total Mensal": custo_mensal,
        "Total Anual": custo_anual
    }

# Sidebar para inclusão manual
st.sidebar.subheader("➕ Adicionar colaborador manualmente")

# Campo de nome com sugestão via Excel
if nomes_sugeridos:
    nome_sel = st.sidebar.selectbox("Nome do colaborador", options=nomes_sugeridos + ["Outro"])
    if nome_sel == "Outro":
        nome = st.sidebar.text_input("Digite o nome completo")
    else:
        nome = nome_sel
else:
    nome = st.sidebar.text_input("Digite o nome do colaborador")

salario = st.sidebar.number_input("Salário (R$)", min_value=0.0, step=1000.0, format="%.2f")
plr = st.sidebar.number_input("PLR Anual (R$)", min_value=0.0, step=1000.0, format="%.2f")
ajuste = st.sidebar.number_input("Ajuste de salário (%)", min_value=0.0, step=1.0, format="%.1f")

if st.sidebar.button("Adicionar colaborador"):
    if nome:
        st.session_state.colaboradores.append({
            "Nome": nome,
            "Salário Base": salario,
            "PLR Anual": plr,
            "Ajuste (%)": ajuste
        })
    else:
        st.sidebar.warning("Por favor, insira o nome do colaborador.")

# Upload de planilha
st.subheader("📄 Ou envie uma planilha Excel com os dados")
st.markdown("Exemplo de colunas esperadas na planilha:")
st.dataframe(pd.DataFrame({
    "Nome": ["João Silva", "Maria Souza"],
    "Salário Base": [12000, 9500],
    "PLR Anual": [18000, 15000],
    "Ajuste (%)": [5, 0]
}))

arquivo = st.file_uploader("Importar colaboradores (xlsx)", type=["xlsx"])

if arquivo:
    df_upload = pd.read_excel(arquivo)
    obrigatorias = {"Nome", "Salário Base", "PLR Anual", "Ajuste (%)"}
    if obrigatorias.issubset(set(df_upload.columns)):
        novos = df_upload[["Nome", "Salário Base", "PLR Anual", "Ajuste (%)"]].to_dict(orient="records")
        st.session_state.colaboradores.extend(novos)
        st.success("Colaboradores importados com sucesso!")
    else:
        st.error(f"A planilha deve conter as colunas: {obrigatorias}")

# Exibir resultados
if st.session_state.colaboradores:
    df_base = pd.DataFrame(st.session_state.colaboradores)

    detalhes = []
    for i, row in df_base.iterrows():
        resultado = calcular_detalhado(row["Salário Base"], row["PLR Anual"], row["Ajuste (%)"])
        detalhes.append(resultado)

    df_detalhado = pd.DataFrame(detalhes)

    colunas_duplicadas = [col for col in df_detalhado.columns if col in df_base.columns]
    df_detalhado.rename(columns={col: f"{col} (calc)" for col in colunas_duplicadas}, inplace=True)

    df_final = pd.concat([df_base, df_detalhado], axis=1)

    # Exclusão segura
    indice_para_excluir = None
    for i, row in df_final.iterrows():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(
                f"**{row['Nome']}** – Total Mensal: **R\${row['Total Mensal']:,.2f}** | Total Anual: **R\${row['Total Anual']:,.2f}**",
                unsafe_allow_html=False
            )
        with col2:
            if st.button("➖", key=f"del_{i}"):
                indice_para_excluir = i

    if indice_para_excluir is not None:
        st.session_state.colaboradores.pop(indice_para_excluir)
        st.rerun()

    # Tabela detalhada
    st.subheader("📋 Detalhamento do custo por colaborador")
    df_formatado = df_final.copy()
    for col in df_formatado.columns:
        if df_formatado[col].dtype in ["float64", "int64"]:
            df_formatado[col] = df_formatado[col].apply(
                lambda x: f"R${x:,.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else x
            )
    st.dataframe(df_formatado, use_container_width=True)

    # Gráfico
    st.subheader("📊 Distribuição do custo total da equipe")
    resumo = df_final[[
        "Salário Ajustado", "Férias", "1/3 Férias", "13º",
        "PLR (mensalizada)", "VA/VR", "Assist. Médica", "INSS", "FGTS"
    ]].sum()

    fig, ax = plt.subplots(figsize=(8, 4))
    resumo.sort_values().plot(kind="barh", ax=ax)
    ax.set_title("Distribuição do custo total por componente")
    ax.set_xlabel("Custo (R$)")
    ax.set_ylabel("Componente")
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    st.pyplot(fig)

    # Exportação
    st.subheader("⬇️ Exportar resultado")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Custo por Colaborador")
    st.download_button("📥 Baixar Excel", data=buffer.getvalue(), file_name="custo_colaboradores.xlsx", mime="application/vnd.ms-excel")
else:
    st.info("Adicione colaboradores manualmente ou importe uma planilha para começar.")
