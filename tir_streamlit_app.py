import streamlit as st
import numpy as np
import numpy_financial as npf
from scipy.optimize import brentq
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Simulador de Flujo y Día Óptimo de Egreso para Alcanzar TIR Objetiva")

# === Entradas del usuario ===
col1, col2 = st.columns(2)
with col1:
    inversion_inicial = st.number_input("Inversión inicial (mes 0)", value=1_000_000.0)
    egreso = st.number_input("Egreso único (negativo)", value=-5_000_000.0)
    plazo_meses = st.number_input("Plazo total (meses)", min_value=1, value=36, step=1)
    tir_objetivo_anual = st.number_input("TIR objetivo anual (%)", value=16.0) / 100
with col2:
    flujo_mensual = st.number_input("Flujo mensual (renta) [opcional]", value=0.0)
    tasa_nominal_anual = st.number_input("Tasa nominal anual estimada (%)", value=0.0)

tir_objetivo_mensual = (1 + tir_objetivo_anual)**(1/12) - 1
dias_totales = int(plazo_meses * 30)
n_total = plazo_meses + 1

# === Si no se proporciona flujo mensual, calcularlo ===
def calcular_renta(flujo_base, inversion_inicial, egreso, tir_mensual, plazo):
    def f(renta):
        flujo = [inversion_inicial]
        flujo += [renta] * int(plazo * 12)
        flujo[int(plazo/3)] += egreso
        return npf.irr(flujo) - tir_mensual
    try:
        return brentq(f, 0.01, abs(egreso))
    except:
        return None

if flujo_mensual <= 0:
    flujo_mensual = calcular_renta(flujo_mensual, inversion_inicial, egreso, tir_objetivo_mensual, plazo_meses)
    if flujo_mensual:
        st.info(f"Renta mensual calculada: ${round(flujo_mensual, 2)}")
    else:
        st.error("No fue posible calcular una renta que alcance la TIR indicada.")

# === Función de búsqueda de TIR por día ===
def tir_diferencia_dia(dia_egreso):
    try:
        mes_egreso = dia_egreso / 30
        flujo = [inversion_inicial]
        for i in range(1, int(plazo_meses) + 1):
            if i == int(np.floor(mes_egreso)):
                fraccion = mes_egreso - np.floor(mes_egreso)
                flujo.append(egreso * fraccion + flujo_mensual * (1 - fraccion))
            elif i == int(np.floor(mes_egreso)) + 1:
                fraccion = mes_egreso - np.floor(mes_egreso)
                flujo.append(egreso * (1 - fraccion) + flujo_mensual * fraccion)
            else:
                flujo.append(flujo_mensual)
        tir = npf.irr(flujo)
        if tir is None or np.isnan(tir):
            return 9999
        return tir - tir_objetivo_mensual
    except:
        return 9999

# === Cálculo del día óptimo ===
st.subheader("Resultado del Análisis")
if st.button("Calcular día óptimo del egreso"):
    try:
        dia_ideal = brentq(tir_diferencia_dia, 1, (plazo_meses - 1) * 30)
        tir_final = tir_objetivo_mensual * 12
        st.success(f"Día exacto del egreso: {round(dia_ideal, 2)}")
        st.success(f"TIR objetivo anual alcanzada: {round(tir_final * 100, 2)}%")

        # === Tabla y gráfica ===
        flujo_diario = [0.0 for _ in range(dias_totales + 1)]
        flujo_diario[0] = inversion_inicial
        flujo_diario[int(dia_ideal)] = egreso
        for i in range(1, plazo_meses + 1):
            flujo_diario[i * 30] += flujo_mensual

        df = pd.DataFrame({"Día": list(range(dias_totales + 1)), "Flujo": flujo_diario})
        st.line_chart(df.set_index("Día"))

        with st.expander("Ver tabla de flujos diarios"):
            st.dataframe(df)
    except Exception as e:
        st.error(f"No se pudo calcular: {e}")