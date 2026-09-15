import streamlit as st
import pandas as pd
import urllib.request
import json

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered"
)

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"


def supabase_get(tabla):
    key = st.secrets["SUPABASE_KEY"]

    url = f"{SUPABASE_URL}/{tabla}"

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


# ------------------------------------------------------------
# TÍTULO
# ------------------------------------------------------------

st.title("🀄 Liga Mahjong Madrid")

st.write("Cargando datos...")


# ------------------------------------------------------------
# CARGAR SUPABASE
# ------------------------------------------------------------

try:
    jugadores = supabase_get("jugadores")
    partidas = supabase_get("partidas")
    resultados = supabase_get("resultados_partidas")

except Exception as e:

    st.error("Error conectando con Supabase")

    st.exception(e)

    st.stop()


# ------------------------------------------------------------
# CONVERTIR A DATAFRAME
# ------------------------------------------------------------

df_jugadores = pd.DataFrame(jugadores)
df_partidas = pd.DataFrame(partidas)
df_resultados = pd.DataFrame(resultados)


# ------------------------------------------------------------
# CONFIRMACIÓN
# ------------------------------------------------------------

st.success("Conexión con Supabase correcta")


# ------------------------------------------------------------
# DATOS
# ------------------------------------------------------------

st.subheader("Datos")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Jugadores",
        len(df_jugadores)
    )

with col2:
    st.metric(
        "Partidas",
        len(df_partidas)
    )

with col3:
    st.metric(
        "Resultados",
        len(df_resultados)
    )


# ------------------------------------------------------------
# COLUMNAS DE PARTIDAS
# ------------------------------------------------------------

st.subheader("Columnas de partidas")

st.write(
    list(df_partidas.columns)
)


# ------------------------------------------------------------
# TEMPORADAS
# ------------------------------------------------------------

if "temporada" in df_partidas.columns:

    st.subheader("Temporadas")

    temporadas = (
        df_partidas["temporada"]
        .fillna("")
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    for temporada in temporadas:

        if temporada:

            st.write(
                temporada
            )

else:

    st.error(
        "No existe la columna 'temporada' en la tabla partidas."
    )


# ------------------------------------------------------------
# TIPOS DE JUEGO
# ------------------------------------------------------------

if "tipo_juego" in df_partidas.columns:

    st.subheader("Tipos de juego")

    tipos = (
        df_partidas["tipo_juego"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
        .unique()
        .tolist()
    )

    for tipo in tipos:

        if tipo:

            st.write(
                tipo
            )

else:

    st.error(
        "No existe la columna 'tipo_juego' en la tabla partidas."
    )


# ------------------------------------------------------------
# TABLA PARTIDAS
# ------------------------------------------------------------

st.subheader("Partidas")

st.dataframe(
    df_partidas,
    use_container_width=True,
    hide_index=True
)
