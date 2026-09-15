import streamlit as st
import pandas as pd
import urllib.request
import json
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

LOGO = Path(__file__).parent / "logo_mahjong_madrid.png"

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon=str(LOGO),
    layout="wide"
)


# ============================================================
# CONFIGURACIÓN SUPABASE
# ============================================================

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


# ============================================================
# FUNCIÓN PARA CONSULTAR SUPABASE
# ============================================================

def obtener_datos(tabla):

    url = f"{SUPABASE_URL}/{tabla}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    request = urllib.request.Request(
        url,
        headers=headers,
        method="GET"
    )

    try:
        with urllib.request.urlopen(request) as response:
            datos = json.loads(response.read().decode("utf-8"))

        return pd.DataFrame(datos)

    except Exception as e:
        st.error(f"Error al consultar Supabase ({tabla}): {e}")
        return pd.DataFrame()


# ============================================================
# CARGAR DATOS
# ============================================================

jugadores = obtener_datos("jugadores")
partidas = obtener_datos("partidas")
resultados = obtener_datos("resultados_partidas")


# ============================================================
# COMPROBAR QUE LOS DATOS EXISTEN
# ============================================================

if jugadores.empty:
    st.error("No se han encontrado jugadores.")
    st.stop()

if partidas.empty:
    st.error("No se han encontrado partidas.")
    st.stop()

if resultados.empty:
    st.error("No se han encontrado resultados.")
    st.stop()


# ============================================================
# COMPROBAR COLUMNAS
# ============================================================

columnas_jugadores = {"id", "nombre"}
columnas_partidas = {"id", "fecha", "creado_por", "tipo_juego"}
columnas_resultados = {
    "partida_id",
    "jugador_id",
    "posicion",
    "puntuacion"
}

if not columnas_jugadores.issubset(jugadores.columns):
    st.error("La tabla jugadores no tiene las columnas esperadas.")
    st.stop()

if not columnas_partidas.issubset(partidas.columns):
    st.error("La tabla partidas no tiene las columnas esperadas.")
    st.stop()

if not columnas_resultados.issubset(resultados.columns):
    st.error(
        "La tabla resultados_partidas no tiene las columnas esperadas."
    )
    st.stop()


# ============================================================
# PREPARAR DATOS
# ============================================================

jugadores["id"] = pd.to_numeric(
    jugadores["id"],
    errors="coerce"
)

partidas["id"] = pd.to_numeric(
    partidas["id"],
    errors="coerce"
)

resultados["partida_id"] = pd.to_numeric(
    resultados["partida_id"],
    errors="coerce"
)

resultados["jugador_id"] = pd.to_numeric(
    resultados["jugador_id"],
    errors="coerce"
)

resultados["puntuacion"] = pd.to_numeric(
    resultados["puntuacion"],
    errors="coerce"
).fillna(0)

resultados["posicion"] = pd.to_numeric(
    resultados["posicion"],
    errors="coerce"
)


# ============================================================
# UNIR LAS TABLAS
# ============================================================

datos = resultados.merge(
    partidas[
        ["id", "fecha", "tipo_juego"]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)

datos = datos.merge(
    jugadores[
        ["id", "nombre"]
    ],
    left_on="jugador_id",
    right_on="id",
    how="left",
    suffixes=("", "_jugador")
)


# ============================================================
# NORMALIZAR TIPO DE JUEGO
# ============================================================

datos["tipo_juego"] = (
    datos["tipo_juego"]
    .astype(str)
    .str.strip()
    .str.upper()
)


# ============================================================
# CREAR RANKING
# ============================================================

def crear_ranking(tipo):

    datos_tipo = datos[
        datos["tipo_juego"] == tipo
    ].copy()

    if datos_tipo.empty:
        return pd.DataFrame()

    ranking = (
        datos_tipo
        .groupby(
            ["jugador_id", "nombre"],
            as_index=False
        )
        .agg(
            Partidas=("partida_id", "nunique"),
            Puntos=("puntuacion", "sum"),
            Primero=(
                "posicion",
                lambda x: (x == 1).sum()
            ),
            Segundo=(
                "posicion",
                lambda x: (x == 2).sum()
            ),
            Tercero=(
                "posicion",
                lambda x: (x == 3).sum()
            ),
            Cuarto=(
                "posicion",
                lambda x: (x == 4).sum()
            ),
            Quinto=(
                "posicion",
                lambda x: (x == 5).sum()
            )
        )
    )

    ranking["Media"] = (
        ranking["Puntos"] /
        ranking["Partidas"]
    )

    ranking["Mejor posición"] = (
        datos_tipo
        .groupby("jugador_id")["posicion"]
        .min()
        .values
    )

    ranking = ranking.sort_values(
        by="Puntos",
        ascending=False
    ).reset_index(drop=True)

    ranking.insert(
        0,
        "Pos.",
        range(1, len(ranking) + 1)
    )

    ranking = ranking.rename(
        columns={
            "nombre": "Jugador",
            "Primero": "1º",
            "Segundo": "2º",
            "Tercero": "3º",
            "Cuarto": "4º",
            "Quinto": "5º"
        }
    )

    return ranking


# ============================================================
# MOSTRAR RANKING
# ============================================================

def mostrar_ranking(tipo):

    ranking = crear_ranking(tipo)

    if ranking.empty:

        st.warning(
            f"No hay partidas registradas de {tipo}."
        )

        return

    datos_tipo = datos[
        datos["tipo_juego"] == tipo
    ].copy()

    total_partidas = datos_tipo[
        "partida_id"
    ].nunique()

    total_jugadores = datos_tipo[
        "jugador_id"
    ].nunique()


    # ========================================================
    # TÍTULO
    # ========================================================

    if tipo == "MCR":
        st.title("🀄 Ranking MCR")
    else:
        st.title("🇯🇵 Ranking RIICHI")


    # ========================================================
    # RESUMEN
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Partidas",
            total_partidas
        )

    with col2:
        st.metric(
            "Jugadores",
            total_jugadores
        )


    st.divider()


    # ========================================================
    # TABLA RANKING
    # ========================================================

    columnas_mostrar = [
        "Pos.",
        "Jugador",
        "Partidas",
        "Puntos",
        "Media",
        "1º",
        "2º",
        "3º",
        "4º",
        "5º"
    ]

    tabla = ranking[columnas_mostrar].copy()

    tabla["Media"] = tabla["Media"].round(2)

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True
    )


    st.divider()


    # ========================================================
    # ESTADÍSTICAS INDIVIDUALES
    # ========================================================

    st.subheader("Estadísticas de jugador")

    jugadores_ranking = ranking[
        "Jugador"
    ].tolist()

    jugador_seleccionado = st.selectbox(
        "Selecciona un jugador",
        jugadores_ranking,
        key=f"jugador_{tipo}"
    )


    jugador = ranking[
        ranking["Jugador"] == jugador_seleccionado
    ].iloc[0]


    # ========================================================
    # DATOS PRINCIPALES
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Partidas",
            int(jugador["Partidas"])
        )

    with col2:
        st.metric(
            "Puntos",
            int(jugador["Puntos"])
        )

    with col3:
        st.metric(
            "Media",
            round(jugador["Media"], 2)
        )

    with col4:

        mejor_posicion = jugador["Mejor posición"]

        if pd.isna(mejor_posicion):
            texto_mejor = "-"
        else:
            texto_mejor = f"{int(mejor_posicion)}º"

        st.metric(
            "Mejor posición",
            texto_mejor
        )


    # ========================================================
    # POSICIONES
    # ========================================================

    st.subheader("Posiciones")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "🥇 1º",
            int(jugador["1º"])
        )

    with col2:
        st.metric(
            "🥈 2º",
            int(jugador["2º"])
        )

    with col3:
        st.metric(
            "🥉 3º",
            int(jugador["3º"])
        )

    with col4:
        st.metric(
            "4º",
            int(jugador["4º"])
        )

    with col5:
        st.metric(
            "5º",
            int(jugador["5º"])
        )


    # ========================================================
    # HISTORIAL DEL JUGADOR
    # ========================================================

    st.subheader("Historial de partidas")

    jugador_id = jugador["jugador_id"]

    historial = datos[
        (datos["tipo_juego"] == tipo) &
        (datos["jugador_id"] == jugador_id)
    ].copy()


    if historial.empty:

        st.info(
            "Este jugador todavía no tiene partidas."
        )

    else:

        historial = historial.sort_values(
            by="fecha",
            ascending=False
        )

        historial_mostrar = historial[
            [
                "fecha",
                "partida_id",
                "posicion",
                "puntuacion"
            ]
        ].copy()

        historial_mostrar = historial_mostrar.rename(
            columns={
                "fecha": "Fecha",
                "partida_id": "Partida",
                "posicion": "Posición",
                "puntuacion": "Puntos"
            }
        )

        st.dataframe(
            historial_mostrar,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# CABECERA PRINCIPAL
# ============================================================

st.title("🏆 Liga Mahjong Madrid")

st.write(
    "Ranking de jugadores de la Liga Mahjong Madrid"
)


# ============================================================
# LOGO MAHJONG MADRID
# ============================================================

if LOGO.exists():

    st.image(
        str(LOGO),
        width=180
    )


st.divider()


# ============================================================
# PESTAÑAS MCR / RIICHI
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    [
        "🀄 RANKING MCR",
        "🇯🇵 RANKING RIICHI"
    ]
)


with tab_mcr:

    mostrar_ranking("MCR")


with tab_riichi:

    mostrar_ranking("RIICHI")