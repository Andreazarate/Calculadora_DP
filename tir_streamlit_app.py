
import streamlit as st
import numpy as np
import numpy_financial as npf
from scipy.optimize import brentq

st.title("Calculadora de Día de Egreso para TIR Objetivo")

# Entradas del usuario
inversion_inicial = st.number_input("Inversión inicial (flujo en mes 0)", value=1792000.0)
flujo_mensual = st.number_input("Flujo mensual (ingresos periódicos)", value=260120.51)
egreso = st.number_input("Monto del egreso único", value=-9739879.49)
tir_objetivo_anual = st.number_input("TIR objetivo anual (%)", value=16.0) / 100
plazo_meses = st.number_input("Plazo total en meses", value=36, step=1)

tir_objetivo_mensual = (1 + tir_objetivo_anual) ** (1/12) - 1
n_total = int(plazo_meses) + 1

# Función de búsqueda
def tir_diferencia_dia(dia_egreso):
    mes_egreso = dia_egreso / 30
    flujo = [inversion_inicial]
    for i in range(1, n_total):
        if i == int(np.floor(mes_egreso)):
            fraccion = mes_egreso - np.floor(mes_egreso)
            flujo.append(egreso * fraccion + flujo_mensual * (1 - fraccion))
        elif i == int(np.floor(mes_egreso)) + 1:
            fraccion = mes_egreso - np.floor(mes_egreso)
            flujo.append(egreso * (1 - fraccion) + flujo_mensual * fraccion)
        else:
            flujo.append(flujo_mensual)
    tir = npf.irr(flujo)
    return tir - tir_objetivo_mensual

if st.button("Calcular día ideal del egreso"):
    try:
        dia_ideal = brentq(tir_diferencia_dia, 1, plazo_meses * 30)
        tir_final = tir_objetivo_mensual * 12
        st.success(f"Día exacto del egreso: {round(dia_ideal, 2)}")
        st.success(f"TIR objetivo anual alcanzada: {round(tir_final * 100, 2)}%")
    except Exception as e:
        st.error(f"No se pudo calcular: {e}")
