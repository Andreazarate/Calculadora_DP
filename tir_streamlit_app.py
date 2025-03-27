import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd
from scipy.optimize import brentq

st.set_page_config(layout="wide")
st.title("Cotizador de Arrendamiento - Día Óptimo de Pago al Proveedor")

# === Entradas del usuario ===
st.header("1. Parámetros del Arrendamiento")
st.caption("Ejemplo: tasa 9%, plazo 36 meses, valor actual $8,179,959")

col1, col2 = st.columns(2)
with col1:
    costo_equipo = st.number_input("Costo del equipo (pago al proveedor)", value=8_179_959.0)
    pago_anticipo = st.number_input("Enganche o anticipo del cliente", value=0.0)
    plazo_meses = st.number_input("Plazo del arrendamiento (meses)", min_value=1, value=36)
with col2:
    tasa_anual = st.number_input("Tasa de interés anual (%)", value=9.0) / 100

# Tasa mensual simple
tasa_mensual = tasa_anual / 12
capital_a_financiar = costo_equipo - pago_anticipo
dias_totales = int(plazo_meses * 30)

# Calcular renta mensual
renta_mensual = -npf.pmt(tasa_mensual, plazo_meses, capital_a_financiar)

# Flujo base original (día 0 incluye pago proveedor y enganche)
flujo_base = [-costo_equipo + pago_anticipo] + [renta_mensual] * int(plazo_meses)
tir_objetivo_mensual = npf.irr(flujo_base)
tir_objetivo_anual = tir_objetivo_mensual * 12

# Mostrar resultados
st.subheader("2. Renta y TIR objetivo")
st.write(f"**Renta mensual calculada:** ${renta_mensual:,.2f}")
st.write(f"**TIR objetivo anual:** {tir_objetivo_anual * 100:.2f}%")

# === Análisis: encontrar día en que debe salir el pago para mantener esa TIR ===
st.header("3. Día óptimo del pago al proveedor (ajustando los flujos)")
st.write("Este cálculo mueve el pago al proveedor dentro del plazo y encuentra el día exacto que conserva la TIR objetivo.")

def flujo_diario_con_dia_pago(dia_pago):
    flujo = [0.0 for _ in range(dias_totales + 1)]
    flujo[0] = pago_anticipo
    flujo[int(dia_pago)] = -costo_equipo
    for i in range(1, int(plazo_meses) + 1):
        flujo[i * 30] += renta_mensual
    return flujo

def tir_diferencia_dia(dia):
    flujo = flujo_diario_con_dia_pago(dia)
    tir = npf.irr(flujo)
    if tir is None or np.isnan(tir):
        return 9999
    return tir - tir_objetivo_mensual

try:
    dia_optimo = brentq(tir_diferencia_dia, 1, dias_totales - 30)
    st.success(f"**El día ideal para realizar el pago al proveedor es el día {round(dia_optimo)}** para mantener la TIR del {tir_objetivo_anual * 100:.2f}%")
except Exception as e:
    st.error(f"No fue posible encontrar el día óptimo: {e}")
