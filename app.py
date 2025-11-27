import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import requests

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="TitanTrade App", layout="wide", page_icon="🦁")

# Estilos visuales (Modo Oscuro Profesional)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 26px; color: #00e676; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #2962ff;
        color: white;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CONEXIÓN CON BINANCE (LEGAL Y GRATIS) ---
def obtener_datos(symbol, interval):
    # API Pública de Binance
    url = "https://api.binance.com/api/v3/klines"
    # Ajustamos el símbolo (ej: BTC-USD a BTCUSDT)
    symbol_clean = symbol.replace("-", "").replace("USD", "USDT")
    
    params = {"symbol": symbol_clean, "interval": interval, "limit": 100}
    
    try:
        r = requests.get(url, params=params).json()
        df = pd.DataFrame(r, columns=["Time", "Open", "High", "Low", "Close", "Vol", "x", "y", "z", "w", "v", "u"])
        df["Date"] = pd.to_datetime(df["Time"], unit='ms')
        df.set_index("Date", inplace=True)
        cols = ["Open", "High", "Low", "Close"]
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        return df
    except:
        return pd.DataFrame()

# --- 3. BARRA LATERAL (MENÚ) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/12435/12435429.png", width=80)
    st.title("TitanTrade")
    st.caption("Versión V10.0 - Móvil")
    
    menu = st.radio("Navegación", ["📈 Trading", "📚 Curso", "ℹ️ Info"])
    
    st.markdown("---")
    
    if menu == "📈 Trading":
        st.header("Panel de Control")
        ticker = st.selectbox("Criptomoneda:", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "DOGE-USD", "SHIB-USD"])
        tempo = st.selectbox("Temporalidad:", ["1m", "15m", "1h", "4h", "1d"], index=1)
        
        st.info("Configuración Visual")
        modo_movil = st.checkbox("📱 Modo Celular", value=True)
        
        if st.button("🔄 Actualizar Datos"):
            st.rerun()

# --- 4. LÓGICA PRINCIPAL ---

if menu == "📈 Trading":
    # Descargar datos
    df = obtener_datos(ticker, tempo)

    if not df.empty:
        # Calcular Indicadores
        df['EMA_200'] = ta.ema(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        bb = ta.bbands(df['Close'], length=20)
        df['BBU'] = bb['BBU_20_2.0']
        df['BBL'] = bb['BBL_20_2.0']

        # Valores actuales
        precio_actual = df['Close'].iloc[-1]
        rsi_actual = df['RSI'].iloc[-1]
        ema_actual = df['EMA_200'].iloc[-1]
        
        # Encabezado
        col1, col2 = st.columns([2, 1])
        col1.title(ticker)
        col2.metric("Precio", f"${precio_actual:,.2f}")

        # --- SEÑALES INTELIGENTES (TEXTO) ---
        st.write("---")
        col_sen1, col_sen2 = st.columns(2)
        
        with col_sen1:
            if precio_actual > ema_actual:
                st.success("🟢 TENDENCIA: ALCISTA")
            else:
                st.error("🔴 TENDENCIA: BAJISTA")
                
        with col_sen2:
            if rsi_actual < 30:
                st.info("💎 SOBREVENTA (Barato)")
            elif rsi_actual > 70:
                st.warning("⚠️ SOBRECOMPRA (Caro)")
            else:
                st.write("⚪ RSI Neutral")

        # --- GRÁFICO ---
        fig = go.Figure()
        
        # Velas
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Precio'))
        
        # EMA 200 (Línea Amarilla)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], line=dict(color='yellow', width=2), name='EMA 200'))
        
        # Bandas Bollinger (Solo si NO estamos en modo móvil para limpiar pantalla)
        if not modo_movil:
            fig.add_trace(go.Scatter(x=df.index, y=df['BBU'], line=dict(color='cyan', width=1), name='BB Sup'))
            fig.add_trace(go.Scatter(x=df.index, y=df['BBL'], line=dict(color='cyan', width=1), name='BB Inf'))

        # Ajustes de tamaño para celular
        fig.update_layout(
            template="plotly_dark", 
            height=400 if modo_movil else 600, 
            xaxis_rangeslider_visible=False, 
            margin=dict(l=0, r=0, t=10, b=0),
            dragmode='pan' if modo_movil else 'zoom'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Barra de progreso RSI
        st.caption(f"Fuerza del Mercado (RSI): {rsi_actual:.1f}")
        st.progress(int(rsi_actual))

    else:
        st.warning("⏳ Conectando con Binance... Pulsa 'Actualizar'")

elif menu == "📚 Curso":
    st.header("🎓 Escuela de Trading")
    st.write("Aprende a usar esta App para ganar dinero.")
    
    with st.expander("1. La Línea Amarilla (EMA 200)"):
        st.markdown("""
        Es tu semáforo.
        * **Si el precio está ARRIBA:** Solo busca botones de COMPRAR 🟢.
        * **Si el precio está ABAJO:** Solo busca botones de VENDER 🔴.
        * *Nunca operes en contra de la línea amarilla.*
        """)
        
    with st.expander("2. El Indicador RSI (Barra de abajo)"):
        st.markdown("""
        Es como un resorte.
        * **Si está muy bajo (menos de 30):** El precio está barato, puede subir.
        * **Si está muy alto (más de 70):** El precio está caro, puede bajar.
        """)

elif menu == "ℹ️ Info":
    st.header("Sobre TitanTrade")
    st.info("Desarrollado para Ricardo Rodriguez")
    st.write("Datos proporcionados por Binance API.")