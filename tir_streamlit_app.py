import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd

st.set_page_config(layout="wide")
st.title("Cotizador de Arrendamiento - Cálculo de Renta y TIR")

# === Entradas del usuario ===
col1, col2 = st.columns(2)
with col1:
    costo_equipo = st.number_input("Costo del equipo (pago al proveedor)", value=1_000_000.0)
    pago_anticipo = st.number_input("Enganche o anticipo del cliente", value=100_000.0)
    plazo_meses = st.number_input("Plazo del arrendamiento (meses)", min_value=1, value=36)
with col2:
    tasa_anual = st.number_input("Tasa de interés anual (%)", value=16.0) / 100

tasa_mensual = (1 + tasa_anual) ** (1/12) - 1
capital_a_financiar = costo_equipo - pago_anticipo

# === Cálculo de la renta mensual ===
renta_mensual = -npf.pmt(tasa_mensual, plazo_meses, capital_a_financiar)

# === Construcción del flujo de caja ===
# Día 0: egreso por pago al proveedor y entrada por enganche del cliente
flujo = [-costo_equipo + pago_anticipo] + [renta_mensual] * int(plazo_meses)
tir = npf.irr(flujo) * 12

# === Mostrar resultados ===
st.subheader("Resultados del Cotizador")
st.write(f"**Renta mensual estimada:** ${renta_mensual:,.2f}")
st.write(f"**TIR anual de la operación:** {tir * 100:.2f}%")

# === Mostrar tabla de flujos ===
df_flujo = pd.DataFrame({
    "Mes": list(range(len(flujo))),
    "Flujo de caja": flujo
})
st.subheader("Flujo de Caja del Arrendamiento")
st.dataframe(df_flujo)

# === Gráfica del flujo ===
st.line_chart(df_flujo.set_index("Mes"))