import streamlit as st
import numpy as np
import numpy_financial as npf
from scipy.optimize import brentq
import pandas as pd

st.set_page_config(layout="wide")
st.title("Simulador de Flujo de Arrendamiento - TIR vs Día de Pago al Proveedor")

# === Entradas del usuario ===
col1, col2 = st.columns(2)
with col1:
    enganche = st.number_input("Enganche recibido (día 0)", value=1_000_000.0)
    pago_proveedor = st.number_input("Pago al proveedor (egreso negativo)", value=-5_000_000.0)
    plazo_meses = st.number_input("Plazo total (meses)", min_value=1, value=36, step=1)
    tir_objetivo_anual = st.number_input("TIR objetivo anual esperada (%)", value=16.0) / 100
with col2:
    renta_mensual = st.number_input("Renta mensual (pagos del cliente)", value=160_000.0)
    dia_min = st.number_input("Día mínimo para el pago al proveedor", value=1, step=1)
    dia_max = st.number_input("Día máximo para el pago al proveedor", value=900, step=1)

tir_objetivo_mensual = (1 + tir_objetivo_anual)**(1/12) - 1
dias_totales = int(plazo_meses * 30)

# === Validación de flujo total recuperado vs egreso ===
total_recuperado = enganche + (renta_mensual * plazo_meses)
st.write(f"Total recuperado por arrendadora: ${total_recuperado:,.2f}")
if total_recuperado <= abs(pago_proveedor):
    st.error("El monto recuperado no es suficiente para cubrir el pago al proveedor. Ajusta enganche o renta.")
else:
    # === Función de flujo por día ===
    def construir_flujo_por_dia(dia_pago_proveedor):
        flujo = [0.0 for _ in range(dias_totales + 1)]
        flujo[0] = enganche
        flujo[int(dia_pago_proveedor)] = pago_proveedor
        for i in range(1, plazo_meses + 1):
            flujo[i * 30] += renta_mensual
        return flujo

    # === Cálculo de TIR diaria en el rango definido ===
    dias = list(range(int(dia_min), int(dia_max) + 1))
    tirs = []
    for d in dias:
        flujo = construir_flujo_por_dia(d)
        tir = npf.irr(flujo)
        if tir is not None and not np.isnan(tir):
            tirs.append(tir * 12)
        else:
            tirs.append(np.nan)

    # === Visualización ===
    st.subheader("Gráfica de TIR vs Día del Pago al Proveedor")
    grafico = pd.DataFrame({
        "Día de Pago al Proveedor": dias,
        "TIR Anual (%)": [round(t * 100, 4) if not np.isnan(t) else None for t in tirs]
    })

    st.line_chart(grafico.set_index("Día de Pago al Proveedor"))
    with st.expander("Ver datos de TIR por día"):
        st.dataframe(grafico)