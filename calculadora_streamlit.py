if st.session_state.colaboradores:
    df_base = pd.DataFrame(st.session_state.colaboradores)

    detalhes = []
    for i, row in df_base.iterrows():
        resultado = calcular_detalhado(row["Salário Base"], row["PLR Anual"], row["Ajuste (%)"])
        detalhes.append(resultado)

    df_detalhado = pd.DataFrame(detalhes)

    # Renomeia colunas duplicadas, se necessário
    colunas_duplicadas = [col for col in df_detalhado.columns if col in df_base.columns]
    df_detalhado.rename(columns={col: f"{col} (calc)" for col in colunas_duplicadas}, inplace=True)

    df_final = pd.concat([df_base, df_detalhado], axis=1)

    # 🔁 Exclusão segura
    indice_para_excluir = None
    for i, row in df_final.iterrows():
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(f"**{row['Nome']}** – R$ {row['Total Mensal']:,.2f}")
        with col2:
            if st.button("🗑️", key=f"del_{i}"):
                indice_para_excluir = i

    if indice_para_excluir is not None:
        st.session_state.colaboradores.pop(indice_para_excluir)
        st.rerun()

    # Tabela detalhada (como antes)
    st.subheader("📋 Detalhamento do custo por colaborador")
    df_formatado = df_final.copy()
    for col in df_formatado.columns:
        if df_formatado[col].dtype in ["float64", "int64"]:
            df_formatado[col] = df_formatado[col].apply(
                lambda x: f"R$ {x:,.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else x
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
