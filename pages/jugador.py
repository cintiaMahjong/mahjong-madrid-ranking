import streamlit as st
import pandas as pd
import urllib.request
import json


st.set_page_config(
    page_title="Jugador - Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered"
)


SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"


# ============================================================
# CONEXIÓN
# ============================================================

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


# ============================================================
# CARGAR DATOS
# ============================================================

try:

    jugadores = supabase_get("jugadores")
    partidas = supabase_get("partidas")
    resultados = supabase_get("resultados_partidas")

except Exception as e:

    st.error("Error conectando con Supabase")

    st.exception(e)

    st.stop()


df_jugadores = pd.DataFrame(jugadores)
df_partidas = pd.DataFrame(partidas)
df_resultados = pd.DataFrame(resultados)


# ============================================================
# NORMALIZAR
# ============================================================

if "tipo_juego" in df_partidas.columns:

    df_partidas["tipo_juego"] = (
        df_partidas["tipo_juego"]
        .fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
    )


if "temporada" in df_partidas.columns:

    df_partidas["temporada"] = (
        df_partidas["temporada"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


if "puntuacion" in df_resultados.columns:

    df_resultados["puntuacion"] = pd.to_numeric(
        df_resultados["puntuacion"],
        errors="coerce"
    ).fillna(0)


# ============================================================
# OBTENER ID DEL JUGADOR
# ============================================================

jugador_id = st.query_params.get(
    "jugador"
)


if not jugador_id:

    st.error(
        "No se ha seleccionado ningún jugador."
    )

    st.stop()


# ============================================================
# BUSCAR JUGADOR
# ============================================================

jugador = df_jugadores[
    df_jugadores["id"].astype(str)
    == str(jugador_id)
]


if jugador.empty:

    st.error(
        "No se ha encontrado el jugador."
    )

    st.stop()


jugador = jugador.iloc[0]


# ============================================================
# NOMBRE
# ============================================================

if "nombre" in jugador:

    nombre = jugador["nombre"]

elif "name" in jugador:

    nombre = jugador["name"]

else:

    nombre = f"Jugador {jugador_id}"


# ============================================================
# TÍTULO
# ============================================================

st.title("🀄 Ficha del jugador")

st.header(
    str(nombre)
)


st.divider()


# ============================================================
# UNIR RESULTADOS CON PARTIDAS
# ============================================================

datos = df_resultados.copy()


datos = datos.merge(
    df_partidas[
        [
            "id",
            "tipo_juego",
            "temporada"
        ]
    ],
    left_on="partida_id",
    right_on="id",
    how="left"
)


# ============================================================
# FILTRAR JUGADOR
# ============================================================

datos_jugador = datos[
    datos["jugador_id"].astype(str)
    == str(jugador_id)
].copy()


if datos_jugador.empty:

    st.info(
        "Este jugador todavía no tiene partidas registradas."
    )

    st.stop()


# ============================================================
# FUNCIÓN ESTADÍSTICAS
# ============================================================

def estadisticas(tipo_juego, temporada):

    df = datos_jugador[
        (datos_jugador["tipo_juego"] == tipo_juego)
        &
        (datos_jugador["temporada"] == temporada)
    ].copy()


    if df.empty:
        return None


    puntos = int(
        df["puntuacion"]
        .sum()
    )


    partidas = int(
        df["partida_id"]
        .nunique()
    )


    media = round(
        puntos / partidas,
        1
    ) if partidas > 0 else 0


    return {
        "Puntos": puntos,
        "Partidas": partidas,
        "Media": media
    }


# ============================================================
# MCR
# ============================================================

st.header("MCR")


temporadas = [
    "Oct 2025 - Sept 2026",
    "Oct 2026 - Sept 2027"
]


for temporada in temporadas:

    st.subheader(
        temporada
    )

    datos_mcr = estadisticas(
        "MCR",
        temporada
    )


    if datos_mcr is None:

        st.write(
            "Sin partidas"
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Puntos",
                datos_mcr["Puntos"]
            )

        with col2:

            st.metric(
                "Partidas",
                datos_mcr["Partidas"]
            )

        with col3:

            st.metric(
                "Media",
                datos_mcr["Media"]
            )


# ============================================================
# RIICHI
# ============================================================

st.header("RIICHI")


for temporada in temporadas:

    st.subheader(
        temporada
    )

    datos_riichi = estadisticas(
        "RIICHI",
        temporada
    )


    if datos_riichi is None:

        st.write(
            "Sin partidas"
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Puntos",
                datos_riichi["Puntos"]
            )

        with col2:

            st.metric(
                "Partidas",
                datos_riichi["Partidas"]
            )

        with col3:

            st.metric(
                "Media",
                datos_riichi["Media"]
            )
