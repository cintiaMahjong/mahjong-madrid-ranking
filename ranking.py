import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import os


# =========================================================
# CONFIGURACIÓN
# =========================================================

RUTA_LOGO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logo_mahjong_madrid.png"
)

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon=RUTA_LOGO if os.path.exists(RUTA_LOGO) else "🀄",
    layout="centered"
)

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"


# =========================================================
# ESTILOS
# =========================================================

st.markdown(
    """
    <style>

    [data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    .stButton > button {
        border-radius: 8px;
    }

    [data-testid="stMetric"] {
        padding: 5px 2px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.3rem;
    }

    @media (max-width: 600px) {

        .block-container {
            padding-left: 0.6rem;
            padding-right: 0.6rem;
            padding-top: 1rem;
        }

        h1 {
            font-size: 1.55rem !important;
        }

        h2 {
            font-size: 1.3rem !important;
        }

        h3 {
            font-size: 1.05rem !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.7rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.1rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CONEXIÓN SUPABASE
# =========================================================

def supabase_get(tabla, parametros=None):

    key = st.secrets["SUPABASE_KEY"]

    url = f"{SUPABASE_URL}/{tabla}"

    if parametros:
        query = urllib.parse.urlencode(parametros)
        url += f"?{query}"

    request = urllib.request.Request(
        url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(request) as response:

        contenido = response.read().decode("utf-8")

    return json.loads(contenido)


# =========================================================
# CARGAR DATOS
# =========================================================

@st.cache_data
def cargar_datos():

    jugadores = supabase_get(
        "jugadores",
        {
            "select": "*"
        }
    )

    partidas = supabase_get(
        "partidas",
        {
            "select": "*"
        }
    )

    resultados = supabase_get(
        "resultados_partidas",
        {
            "select": "*"
        }
    )

    df_jugadores = pd.DataFrame(jugadores)
    df_partidas = pd.DataFrame(partidas)
    df_resultados = pd.DataFrame(resultados)

    return (
        df_jugadores,
        df_partidas,
        df_resultados
    )


try:

    (
        df_jugadores,
        df_partidas,
        df_resultados
    ) = cargar_datos()

except Exception as e:

    st.error(
        "No se han podido cargar los datos de Supabase."
    )

    st.exception(e)

    st.stop()


# =========================================================
# PREPARAR DATOS
