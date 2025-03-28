import numpy_financial as npf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def calcular_dia_tir_objetivo(inversion_inicial, flujo_diario, dias, tir_anual_objetivo):
    tir_diaria_obj = (1 + tir_anual_objetivo) ** (1/365) - 1
    fechas = [datetime.today() + timedelta(days=i) for i in range(dias + 1)]

    def van_con_flujo_negativo_en_dia(dia_negativo):
        van = 0
        for i in range(dias + 1):
            flujo = flujo_diario
            if i == dia_negativo:
                flujo = inversion_inicial
            van += flujo / (1 + tir_diaria_obj) ** i
        return van

    mejor_van = float('inf')
    mejor_dia = None

    for dia in range(dias + 1):
        van = van_con_flujo_negativo_en_dia(dia)
        if abs(van) < abs(mejor_van):
            mejor_van = van
            mejor_dia = dia

    flujos = [flujo_diario] * (dias + 1)
    flujos[mejor_dia] = inversion_inicial

    df = pd.DataFrame({
        "Fecha": fechas,
        "Flujo": flujos
    })
    df["Flujo descontado"] = df["Flujo"] / (1 + tir_diaria_obj) ** df.index
    df["Acumulado descontado"] = df["Flujo descontado"].cumsum()

    nombre_archivo = "Flujos_TIR_{:.0f}_por_ciento.xlsx".format(tir_anual_objetivo * 100)
    df.to_excel(nombre_archivo, index=False)

    print(f"DÃ­a Ã³ptimo para flujo negativo: {mejor_dia}")
    print(f"Archivo guardado como: {nombre_archivo}")

    plt.figure(figsize=(10, 6))
    plt.plot(df["Fecha"], df["Acumulado descontado"])
    plt.axhline(0, color='gray', linestyle='--')
    plt.title(f"Flujo Acumulado Descontado - TIR {tir_anual_objetivo*100:.0f}%")
    plt.xlabel("Fecha")
    plt.ylabel("Valor presente acumulado")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # EDITA ESTAS VARIABLES SEGÃN TU CASO
    inversion_inicial = -8179959
    flujo_diario = 8670.68
    dias = 1080
    tir_anual_objetivo = 0.15

    calcular_dia_tir_objetivo(inversion_inicial, flujo_diario, dias, tir_anual_objetivo)