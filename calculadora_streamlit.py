import streamlit as st

def calcular_custo_colaborador(salario, plr):
    # Valores fixos
    va_vr = 2057.92
    assist_medica = 978.00

    # Provisões
    ferias_12 = salario / 12
    um_terco_ferias = ferias_12 / 3
    decimo_terceiro = salario / 12
    plr_12 = plr / 12

    # Base de encargos: salário + férias + 1/3 férias + 13º
    base_encargos = salario + ferias_12 + um_terco_ferias + decimo_terceiro

    inss = base_encargos * 0.282
    fgts = base_encargos * 0.08

    # Custo mensal
    custo_mensal = (
        salario + ferias_12 + um_terco_ferias + decimo_terceiro +
        plr_12 + va_vr + assist_medica + inss + fgts
    )

    # Custo anual
    custo_anual = custo_mensal * 12

    return round(custo_mensal, 2), round(custo_anual, 2)


# Interface Streamlit
st.set_page_config(page_title="Calculadora de Custo do Colaborador", layout="centered")

st.title("💼 Calculadora de Custo do Colaborador")

st.markdown("Preencha os campos abaixo para calcular o custo mensal e anual de um colaborador:")

salario = st.number_input("Salário mensal (R$)", min_value=0.0, format="%.2f")
plr = st.number_input("Valor da PLR anual (R$)", min_value=0.0, format="%.2f")

if st.button("Calcular"):
    custo_mensal, custo_anual = calcular_custo_colaborador(salario, plr)
    st.success(f"📊 Custo **mensal**: R$ {custo_mensal:,.2f}")
    st.info(f"📆 Custo **anual**: R$ {custo_anual:,.2f}")