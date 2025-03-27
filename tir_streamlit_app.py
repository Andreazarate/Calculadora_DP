
import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd
from scipy.optimize import minimize_scalar

st.set_page_config(layout="wide")
st.title("Cotizador de Arrendamiento - Buscar Día Óptimo para Alcanzar TIR Deseada")

# === Entradas del usuario ===
st.header("1. Parámetros del Arrendamiento")
col1, col2 = st.columns(2)
with col1:
    costo_equipo = st.number_input("Costo del equipo (pago al proveedor)", value=8_179_959.0)
    pago_anticipo = st.number_input("Enganche o anticipo del cliente", value=0.0)
    plazo_meses = st.number_input("Plazo del arrendamiento (meses)", min_value=1, value=36)
with col2:
    tasa_anual = st.number_input("Tasa nominal anual (%)", value=9.0) / 100
    tir_deseada_anual = st.number_input("TIR objetivo anual deseada (%)", value=16.0) / 100

# Cálculo de renta mensual con fórmula tipo Excel: tasa anual / 12
tasa_mensual = tasa_anual / 12
capital_a_financiar = costo_equipo - pago_anticipo
dias_totales = int(plazo_meses * 30)
renta_mensual = -npf.pmt(tasa_mensual, plazo_meses, capital_a_financiar)

tir_deseada_mensual = tir_deseada_anual / 12

# === Funciones ===
def flujo_diario_con_dia_pago(dia):
    flujo = [0.0 for _ in range(dias_totales + 1)]
    flujo[0] = pago_anticipo
    if int(dia) <= dias_totales:
        flujo[int(dia)] = -costo_equipo
    for i in range(1, int(plazo_meses) + 1):
        if i * 30 <= dias_totales:
            flujo[i * 30] += renta_mensual
    return flujo

def tir_diferencia(dia):
    flujo = flujo_diario_con_dia_pago(dia)
    tir = npf.irr(flujo)
    if tir is None or np.isnan(tir):
        return 1e6
    return abs(tir - tir_deseada_mensual)

# === Optimización ===
st.header("2. Resultado del Análisis")
result = minimize_scalar(tir_diferencia, bounds=(1, dias_totales - 30), method='bounded')

if result.success:
    mejor_dia = round(result.x)
    flujo_optimo = flujo_diario_con_dia_pago(mejor_dia)
    tir_obtenida = npf.irr(flujo_optimo) * 12

    st.success(f"Mejor día estimado para el pago al proveedor: {mejor_dia}")
    st.info(f"TIR obtenida con ese día: {tir_obtenida*100:.2f}%")

    df_flujo = pd.DataFrame({
        "Día": list(range(len(flujo_optimo))),
        "Flujo de Caja": flujo_optimo
    })
    st.subheader("3. Flujo Diario de Caja")
    st.dataframe(df_flujo)
else:
    st.error("No fue posible calcular el día óptimo.")
