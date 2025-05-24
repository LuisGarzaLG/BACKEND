import simpy
import random
import pandas as pd
import matplotlib.pyplot as plt
import sys
import json

# ============================
# PARÁMETROS DE CONFIGURACIÓN
# ============================
NUM_PERSONAS = 100
TIEMPO_ENTRE_LLEGADAS = 10
TIEMPO_SIMULACION = 1000

DURACION_BN = (1, 3)
DURACION_COLOR = (4, 10)

IMPRESORAS_BN = 1
IMPRESORAS_COLOR = 1

# =====================================
# LISTA PARA REGISTRAR CADA IMPRESIÓN
# =====================================
registros = []

# =====================================
# FUNCIÓN DE TRABAJO DE IMPRESIÓN
# =====================================
def trabajo_impresion(env, nombre, tipo, impresora, id_impresora):
    llegada = env.now
    duracion = random.randint(*DURACION_BN if tipo == 'BN' else DURACION_COLOR)

    with impresora.request() as req:
        yield req
        inicio = env.now
        espera = inicio - llegada
        yield env.timeout(duracion)
        salida = env.now

        registros.append({
            'Empleado': nombre,
            'Tipo': tipo,
            'Llegada': round(llegada, 2),
            'Inicio': round(inicio, 2),
            'Salida': round(salida, 2),
            'Espera': round(espera, 2),
            'Duración': duracion,
            'Impresora_ID': id_impresora
        })

# =====================================
# GENERADOR DE TRABAJOS
# =====================================
def generador_trabajos(env, impresoras_bn, impresoras_color):
    for i in range(NUM_PERSONAS):
        yield env.timeout(random.expovariate(1.0 / TIEMPO_ENTRE_LLEGADAS))
        tipo = random.choice(['BN', 'COLOR'])
        nombre = f'Empleado_{i+1}'

        if tipo == 'BN':
            impresora_idx = i % len(impresoras_bn)
            env.process(trabajo_impresion(env, nombre, tipo, impresoras_bn[impresora_idx], f'BN-{impresora_idx+1}'))
        else:
            impresora_idx = i % len(impresoras_color)
            env.process(trabajo_impresion(env, nombre, tipo, impresoras_color[impresora_idx], f'Color-{impresora_idx+1}'))

# =====================================
# FUNCIÓN PRINCIPAL DE SIMULACIÓN
# =====================================
def simular_impresion():
    env = simpy.Environment()
    impresoras_bn = [simpy.Resource(env, capacity=1) for _ in range(IMPRESORAS_BN)]
    impresoras_color = [simpy.Resource(env, capacity=1) for _ in range(IMPRESORAS_COLOR)]

    env.process(generador_trabajos(env, impresoras_bn, impresoras_color))
    env.run(until=TIEMPO_SIMULACION)

    return pd.DataFrame(registros)

# ========================
# EJECUTAR Y MOSTRAR
# ========================
df_resultado = simular_impresion()

# Mostrar primeros resultados
print("\nPrimeros 10 registros:")
print(df_resultado.head(11))

# Estadísticas por tipo
print("\n=== ESTADÍSTICAS ===")
for tipo in ['BN', 'COLOR']:
    subset = df_resultado[df_resultado['Tipo'] == tipo]
    print(f"\n{tipo}")
    print(f" - Total impresiones: {len(subset)}")
    print(f" - Promedio espera: {subset['Espera'].mean():.2f}")
    print(f" - Máxima espera: {subset['Espera'].max():.2f}")
    print(f" - Mínima espera: {subset['Espera'].min():.2f}")

# Guardar Excel con manejo de error
try:
    df_resultado.to_excel("registro_impresiones.xlsx", index=False)
    print("\n📄 Archivo Excel guardado exitosamente: registro_impresiones.xlsx")
except PermissionError:
    print("\n❌ No se pudo guardar 'registro_impresiones.xlsx'. ¿Está abierto?")
    df_resultado.to_csv("registro_impresiones_backup.csv", index=False)
    print("✅ Se guardó una copia en: registro_impresiones_backup.csv")
# ========================================
# COMPARACIÓN ENTRE DOS ESCENARIOS
# ========================================
def simular_comparacion(impresoras_bn, impresoras_color):
    global registros
    registros = []  # Reiniciar registros
    env = simpy.Environment()
    impresoras_bn_res = [simpy.Resource(env, capacity=1) for _ in range(impresoras_bn)]
    impresoras_color_res = [simpy.Resource(env, capacity=1) for _ in range(impresoras_color)]

    env.process(generador_trabajos(env, impresoras_bn_res, impresoras_color_res))
    env.run(until=TIEMPO_SIMULACION)

    return pd.DataFrame(registros)

# Ejecutar los dos escenarios
print("\n🏁 Ejecutando comparación de escenarios...")

escenario_1 = simular_comparacion(1, 1)
escenario_2 = simular_comparacion(2, 2)

# Comparar resultados
def resumen(df):
    return {
        'Promedio_Espera': df['Espera'].mean(),
        'Max_Espera': df['Espera'].max(),
        'Min_Espera': df['Espera'].min(),
        'Total_Impresiones': len(df)
    }

resumen_1 = resumen(escenario_1)
resumen_2 = resumen(escenario_2)

df_comparacion = pd.DataFrame([resumen_1, resumen_2], index=['1_impresora', '2_impresoras'])

# Mostrar resumen
print("\n📊 Comparación de escenarios:")
print(df_comparacion)

# Guardar archivo de comparación
df_comparacion.to_excel("comparacion_escenarios.xlsx")
print("✅ Archivo 'comparacion_escenarios.xlsx' generado.")

# ========================
# VISUALIZACIÓN
# ========================
fig, axs = plt.subplots(1, 2, figsize=(14, 5))

# Subplot 1: Histograma por tipo
axs[0].hist(df_resultado[df_resultado['Tipo'] == 'BN']['Espera'], bins=15, alpha=0.7, label='B/N')
axs[0].hist(df_resultado[df_resultado['Tipo'] == 'COLOR']['Espera'], bins=15, alpha=0.7, label='Color')
axs[0].set_title("Distribución de Tiempos de Espera")
axs[0].set_xlabel("Tiempo de espera")
axs[0].set_ylabel("Número de empleados")
axs[0].legend()
axs[0].grid(True)

# Subplot 2: Comparación de escenarios
axs[1].bar(['1 Impresora', '2 Impresoras'], 
           [resumen_1['Promedio_Espera'], resumen_2['Promedio_Espera']], 
           color=['red', 'green'])
axs[1].set_title("Comparación: Tiempo Promedio de Espera")
axs[1].set_ylabel("Tiempo de espera promedio")
axs[1].grid(True)

plt.tight_layout()
plt.show()


# ========================
# ACTIVIDADES DEL ESTUDIANTE
# ========================

# 1. Describir el entorno
print("\n1. 📘 Descripción del entorno:")
print("   En esta simulación, múltiples empleados utilizan una o más impresoras compartidas (B/N y Color).")
print("   Cada trabajo llega aleatoriamente en el tiempo y se procesa según el orden de llegada (FIFO).")

# 2. Recolectar supuestos
print("\n2. 📋 Supuestos considerados:")
print(f"   - Tiempo entre llegadas: {TIEMPO_ENTRE_LLEGADAS} unidades (media exponencial).")
print(f"   - Duración impresión B/N: entre {DURACION_BN[0]} y {DURACION_BN[1]} unidades.")
print(f"   - Duración impresión Color: entre {DURACION_COLOR[0]} y {DURACION_COLOR[1]} unidades.")
print(f"   - Número de empleados: {NUM_PERSONAS}")
print(f"   - Tiempo total de simulación: {TIEMPO_SIMULACION}")
print(f"   - Número de impresoras B/N: {IMPRESORAS_BN}")
print(f"   - Número de impresoras Color: {IMPRESORAS_COLOR}")

# 3. Simular la cola
print("\n3. 🔁 Simulación de la cola:")
print("   Se ha utilizado SimPy con recursos tipo FIFO.")
print("   Cada impresora representa un servidor con capacidad 1 (una impresión a la vez).")
print("   Los trabajos son encolados si la impresora está ocupada.")

# 4. Medir rendimiento
print("\n4. 📈 Medición de rendimiento:")

promedio_espera = df_resultado['Espera'].mean()
uso_por_impresora = df_resultado.groupby("Impresora_ID")["Duración"].sum()
uso_porcentaje = (uso_por_impresora / TIEMPO_SIMULACION * 100).round(2)

print(f"   - Tiempo promedio en cola: {promedio_espera:.2f} unidades.")
print(f"   - Uso de impresoras (% del tiempo ocupado):\n{uso_porcentaje.to_string()}")

# 5. Analizar impacto
print("\n5. 🔍 Análisis de impacto del modelo:")
if IMPRESORAS_BN == 1 and IMPRESORAS_COLOR == 1:
    print("   ⚠️ Solo hay una impresora de cada tipo. Esto puede causar cuellos de botella.")
    print("   🔄 Puedes duplicar el número de impresoras y repetir la simulación para comparar.")
else:
    print("   ✅ Se ha configurado más de una impresora. Esto ayuda a reducir el tiempo de espera.")
print("   💡 Más usuarios o menos impresoras tienden a aumentar el tiempo en cola.")
print("   Puedes probar con diferentes configuraciones para ver cómo afecta el rendimiento.")

# 6. Validar el modelo
print("\n6. ✅ Validación del modelo:")
print("   Este modelo sigue lógica de colas simple (FIFO), con tiempos aleatorios y reglas razonables.")
print("   Para validarlo, se puede comparar con registros reales de una oficina o los tiempos que esperarías.")

# 7. Generar informe
print("\n7. 📊 Generación del informe:")
print("   Los datos de cada impresión se guardaron en 'registro_impresiones.xlsx'.")
print("   Se generó un histograma visual de los tiempos de espera.")
print("   También se exportará un resumen estadístico a 'resumen_estudiante.xlsx'.")

# Exportar resumen a Excel
resumen = {
    'Promedio_Espera': [df_resultado['Espera'].mean()],
    'Max_Espera': [df_resultado['Espera'].max()],
    'Min_Espera': [df_resultado['Espera'].min()],
    'Promedio_Duracion': [df_resultado['Duración'].mean()],
    'Total_Impresiones': [len(df_resultado)],
    'Uso_Impresoras': [uso_porcentaje.to_dict()]
}
df_resumen = pd.DataFrame(resumen)
df_resumen.to_excel("resumen_estudiante.xlsx", index=False)
print("   📁 Se creó el archivo 'resumen_estudiante.xlsx' con estadísticas clave.")


