import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd

st.set_page_config(layout="wide")
st.title("Cotizador de Arrendamiento - Cálculo de Renta, Flujos y TIR")

# === Entradas del usuario ===
st.header("1. Parámetros del Arrendamiento")
col1, col2 = st.columns(2)
with col1:
    costo_equipo = st.number_input("Costo del equipo (pago al proveedor)", value=1_000_000.0)
    pago_anticipo = st.number_input("Enganche o anticipo del cliente", value=100_000.0)
    plazo_meses = st.number_input("Plazo del arrendamiento (meses)", min_value=1, value=36)
with col2:
    tasa_anual = st.number_input("Tasa de interés anual (%)", value=16.0) / 100

tasa_mensual = (1 + tasa_anual) ** (1/12) - 1
capital_a_financiar = costo_equipo - pago_anticipo
dias_totales = int(plazo_meses * 30)

# === Cálculo de la renta mensual ===
renta_mensual = -npf.pmt(tasa_mensual, plazo_meses, capital_a_financiar)

# === Construcción del flujo de caja mensual (flujo 0 con pago al proveedor y enganche) ===
flujo_mensual = [-costo_equipo + pago_anticipo] + [renta_mensual] * int(plazo_meses)
tir_mensual = npf.irr(flujo_mensual)
tir_anual = tir_mensual * 12 if tir_mensual else None

# === Mostrar resultados ===
st.subheader("2. Resultados del Cotizador")
st.write(f"**Renta mensual estimada:** ${renta_mensual:,.2f}")
st.write(f"**TIR anual de la operación:** {tir_anual * 100:.2f}%" if tir_anual else "TIR no válida")

# === Mostrar tabla de flujos ===
df_flujo = pd.DataFrame({
    "Mes": list(range(len(flujo_mensual))),
    "Flujo de caja": flujo_mensual
})
st.subheader("Flujo de Caja del Arrendamiento")
st.dataframe(df_flujo)
st.line_chart(df_flujo.set_index("Mes"))

# === Análisis de TIR según el día del egreso ===
st.header("3. Análisis del Mejor Día para Pagar al Proveedor")
st.write("Se evalúa la TIR según el día en que se hace el egreso por el equipo, manteniendo constante el enganche en el día 0 y las rentas mensuales.")

dia_min = st.number_input("Día mínimo de análisis", value=1, step=1)
dia_max = st.number_input("Día máximo de análisis", value=720, step=1)

def flujo_diario_con_pago_en(dia_pago):
    flujo = [0.0 for _ in range(dias_totales + 1)]
    flujo[0] = pago_anticipo
    flujo[int(dia_pago)] = -costo_equipo
    for i in range(1, int(plazo_meses) + 1):
        flujo[i * 30] += renta_mensual
    return flujo

dias = list(range(int(dia_min), int(dia_max) + 1))
tirs = []
for d in dias:
    flujo = flujo_diario_con_pago_en(d)
    tir_d = npf.irr(flujo)
    tirs.append(tir_d * 12 if tir_d is not None and not np.isnan(tir_d) else None)

grafico_df = pd.DataFrame({
    "Día": dias,
    "TIR Anual (%)": [round(t * 100, 4) if t is not None else None for t in tirs]
})

st.subheader("Gráfica de TIR vs Día del Pago al Proveedor")
st.line_chart(grafico_df.set_index("Día"))

with st.expander("Ver tabla de TIR por día"):
    st.dataframe(grafico_df)