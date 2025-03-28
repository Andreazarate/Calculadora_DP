import numpy_financial as npf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Parámetros
inversion_inicial = -8179959
flujo_diario = 8670.68
dias = 1080
tir_anual_objetivo = 0.15
tir_diaria_obj = (1 + tir_anual_objetivo) ** (1/365) - 1

# Fechas
inicio = datetime.today()
fechas = [inicio + timedelta(days=i) for i in range(dias + 1)]

# Función para calcular el VAN
def van_con_flujo_negativo_en_dia(dia_negativo, tir_diaria):
    van = 0
    for i in range(dias + 1):
        flujo = flujo_diario
        if i == dia_negativo:
            flujo = inversion_inicial
        van += flujo / (1 + tir_diaria) ** i
    return van

# Buscar el día ideal
mejor_van = float('inf')
mejor_dia = None

for dia in range(dias + 1):
    van = van_con_flujo_negativo_en_dia(dia, tir_diaria_obj)
    if abs(van) < abs(mejor_van):
        mejor_van = van
        mejor_dia = dia

# Crear flujos con el flujo negativo en el día ideal
nuevo_flujos = [flujo_diario] * (dias + 1)
nuevo_flujos[mejor_dia] = inversion_inicial

# Crear DataFrame
df = pd.DataFrame({
    "Fecha": fechas,
    "Flujo": nuevo_flujos
})
df["Flujo descontado"] = df["Flujo"] / (1 + tir_diaria_obj) ** df.index
df["Acumulado descontado"] = df["Flujo descontado"].cumsum()

# Guardar a Excel
df.to_excel("Flujos_TIR_15_por_ciento.xlsx", index=False)

# Graficar
plt.figure(figsize=(10, 6))
plt.plot(df["Fecha"], df["Acumulado descontado"])
plt.axhline(0, color='gray', linestyle='--')
plt.title("Flujo Acumulado Descontado - TIR 15%")
plt.xlabel("Fecha")
plt.ylabel("Valor presente acumulado")
plt.grid(True)
plt.tight_layout()
plt.show()