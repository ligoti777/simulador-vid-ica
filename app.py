import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Configuración de la página
st.set_page_config(
    page_title="Simulador DPV & Efecto Kamikaze - Vid",
    page_icon="🍇",
    layout="wide"
)

# Estilos CSS personalizados para una interfaz profesional y moderna
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1b4332;
        font-weight: 800;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #2d6a4f;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .author-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #2d6a4f;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown('<p class="main-header">🍇 Simulador Agrometeorológico: DPV y Efecto Kamikaze en Vid</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Herramienta de precisión para el manejo fisiológico, estrés hídrico y control estomático</p>', unsafe_allow_html=True)

# Tarjeta de Autoría y Respaldo
st.markdown("""
    <div class="author-box">
        <strong>Autoría y Validación Técnica:</strong><br>
        • <strong>Lisandro Godoy Tito ("Ligotti")</strong><br>
        • <strong>Grado:</strong> Bachiller en Ciencias Agrícolas<br>
        • <strong>Ámbito de Aplicación:</strong> Manejo termofisiológico y mitigación de estrés abiótico en uva de mesa (Valle de Ica / San José de los Molinos).
    </div>
""", unsafe_allow_html=True)

# Barra lateral para configuración de modo de entrada
st.sidebar.header("⚙️ Configuración de Datos")
modo_clima = st.sidebar.radio(
    "Selecciona el origen de los datos climáticos:",
    ["🎛️ Manual (Campo / Sin internet)", "🌐 Automático en Línea (API Open-Meteo)"]
)

# Variables climáticas base
temp_aire = 30.0
hum_rel = 45.0
vel_viento = 2.0
rad_solar = 800.0

if modo_clima == "🌐 Automático en Línea (API Open-Meteo)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Coordenadas de Ubicación (Ica / San José de los Molinos)")
    
    # Coordenadas por defecto para San José de los Molinos, Ica, Perú
    lat = st.sidebar.number_input("Latitud", value=-13.9856, format="%.4f")
    lon = st.sidebar.number_input("Longitud", value=-75.7383, format="%.4f")
    
    # Simulación de consulta a API pública gratuita (Open-Meteo)
    import urllib.request
    import json
    
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
    
    try:
        with urllib.request.urlopen(api_url, timeout=5) as response:
            data = json.loads(response.read().decode())
            current = data.get("current", {})
            temp_aire = float(current.get("temperature_2m", 30.0))
            hum_rel = float(current.get("relative_humidity_2m", 45.0))
            vel_viento = float(current.get("wind_speed_10m", 2.0)) * (1000 / 3600) # Conversión de km/h a m/s
            rad_solar = float(current.get("shortwave_radiation", 800.0))
            st.sidebar.success("✅ Conexión exitosa a datos meteorológicos en tiempo real.")
    except Exception as e:
        st.sidebar.warning(f"⚠️ No se pudo conectar a la API en este momento. Usando valores predeterminados. (Detalle: {e})")
else:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Ingrese Parámetros de Campo")
    temp_aire = st.sidebar.slider("Temperatura del Aire (°C)", 10.0, 45.0, 30.0, 0.5)
    hum_rel = st.sidebar.slider("Humedad Relativa (%)", 10.0, 100.0, 45.0, 1.0)
    vel_viento = st.sidebar.slider("Velocidad del Viento (m/s)", 0.0, 15.0, 2.0, 0.1)
    rad_solar = st.sidebar.slider("Radiación Solar (W/m²)", 100.0, 1200.0, 800.0, 10.0)

# --- MOTOR DE CÁLCULO CIENTÍFICO (DPV y Estrés) ---
# 1. Presión de vapor de saturación (SVP) en kPa usando la fórmula de Tetens
svp = 0.61078 * np.exp((17.27 * temp_aire) / (temp_aire + 237.3))

# 2. Presión de vapor real (AVP) en kPa
avp = svp * (hum_rel / 100.0)

# 3. Déficit de Presión de Vapor (DPV) base
dpv = svp - avp

# 4. Factor de corrección por microclima (Efecto Viento y Radiación sobre la hoja)
# El viento extremo y la alta radiación incrementan la temperatura efectiva de la hoja y el arrastre de la capa límite
factor_estres_microclimatico = (vel_viento * 0.08) + (rad_solar / 1000.0 * 0.15)
dpv_efectivo = dpv + factor_estres_microclimatico

# --- INTERFAZ PRINCIPAL DE RESULTADOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <h4>Temperatura Aire</h4>
            <h2>{temp_aire:.1f} °C</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <h4>Humedad Relativa</h4>
            <h2>{hum_rel:.1f} %</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <h4>DPV Calculado</h4>
            <h2>{dpv_efectivo:.2f} kPa</h2>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Evaluación del Semáforo Fisiológico y Efecto Kamikaze
st.subheader("🚥 Diagnóstico del Estado Fisiológico y Cierre Estomático")

if dpv_efectivo < 0.8:
    estado = "ÓPTIMO / BAJO ESTRÉS"
    color = "green"
    descripcion = "La demanda evaporativa es baja. Los estomas se encuentran totalmente abiertos, tasa fotosintética óptima y excelente absorción de nutrientes y agua."
    recomendacion = "Condiciones ideales para riegos normales y asimilación de fertilizantes o bioestimulantes."
elif 0.8 <= dpv_efectivo <= 2.0:
    estado = "ESTRÉS MODERADO A ALTO (Precaución)"
    color = "orange"
    descripcion = "La atmósfera comienza a demandar humedad de forma acelerada. Los estomas experimentan restricciones parciales para evitar pérdidas excesivas de agua."
    recomendacion = "Monitorear la turgencia del ápice foliar. Evaluar aplicaciones preventivas de agentes protectores (silicio, óxido de calcio o aminoácidos) y ajustar frecuencias de riego."
else:
    estado = "CRÍTICO: EFECTO KAMIKAZE ACTIVADO ⚠️"
    color = "red"
    descripcion = "¡Alerta máxima! Demanda atmosférica extrema combinada. La planta activa un mecanismo de defensa drástico cerrando completamente los estomas para evitar el colapso hidráulico del xilema, deteniendo la fotosíntesis."
    recomendacion = "Acción inmediata requerida: Aplicar riegos cortos de refrescamiento si el sistema lo permite, evitar aplicaciones de productos de síntesis pesados bajo este pico y proteger el cultivo con bioestimulantes antiestrés."

st.markdown(f"""
    <div style="background-color: {color}; color: white; padding: 20px; border-radius: 10px; text-align: center;">
        <h3>Estado del Cultivo: {estado}</h3>
        <p style="font-size: 1.1rem; margin-top: 10px;">{descripcion}</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"**Recomendación Táctica de Manejo:** {recomendacion}")

st.markdown("---")

# Sección de Fundamento Científico y Bibliografía
with st.expander("📚 Fundamento Científico y Bibliografía de Respaldo"):
    st.markdown("""
    ### Bases Termofisiológicas del Modelo
    * **Déficit de Presión de Vapor (DPV):** Representa la fuerza impulsora real que mueve el agua desde el interior de la hoja hacia la atmósfera a través de los estomas. Valores superiores a $2.0\\text{ kPa}$ superan la capacidad de compensación hídrica del sistema vascular en condiciones áridas.
    * **Efecto Kamikaze Vegetal:** Concepto agronómico aplicado al colapso funcional temporal donde la vid prioriza la supervivencia inmediata sobre la producción y acumulación de azúcares mediante el cierre estomático abrupto.
    
    ### Referencias Bibliográficas:
    1. **Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998).** *Crop evapotranspiration - Guidelines for computing crop water requirements.* FAO Irrigation and Drainage Paper 56.
    2. **Taiz, L., & Zeiger, E. (2010).** *Plant Physiology* (5th ed.). Sinauer Associates. (Capítulo sobre relaciones hídricas y transporte en plantas).
    3. **Jones, H. G. (2014).** *Plants and Microclimate: A Quantitative Approach to Environmental Plant Physiology.* Cambridge University Press.
    """)

# Pie de página
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Desarrollado para la gestión agrometeorológica avanzada en Ica | Autor: Lizandro Godoy Tito (Ligotti)</p>", unsafe_allow_html=True)
