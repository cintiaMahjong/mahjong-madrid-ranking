import streamlit as st
import pandas as pd
import urllib.request
import json
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).parent

LOGO = BASE_DIR / "logo_mahjong_madrid.png"


# ============================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================

if LOGO.exists():
    PAGE_ICON = str(LOGO)
else:
    PAGE_ICON = "🀄"


st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon=PAGE_ICON,
    layout="wide"
)


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"

SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


# ============================================================
# FUNCIÓN PARA OBTENER DATOS
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

            datos = json.loads(
                response.read().decode("utf-8")
            )

        return pd.DataFrame(datos)

    except Exception as e:

        st.error(
            f"Error al consultar Supabase ({tabla}): {e}"
        )

        return pd.DataFrame()


# ============================================================
# CARGAR DATOS
# ============================================================

jugadores = obtener_datos("jugadores")

partidas = obtener_datos("partidas")

resultados = obtener_datos("resultados_partidas")


# ============================================================
# COMPROBAR DATOS
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

columnas_jugadores = {
    "id",
    "nombre"
}

columnas_partidas = {
    "id",
    "fecha",
    "creado_por",
    "tipo_juego"
}

columnas_resultados = {
    "partida_id",
    "jugador_id",
    "posicion",
    "puntuacion"
}


if not columnas_jugadores.issubset(
    jugadores.columns
):

    st.error(
        "La tabla jugadores no tiene las columnas esperadas."
    )

    st.stop()


if not columnas_partidas.issubset(
    partidas.columns
):

    st.error(
        "La tabla partidas no tiene las columnas esperadas."
    )

    st.stop()


if not columnas_resultados.issubset(
    resultados.columns
):

    st.error(
        "La tabla resultados_partidas no tiene las columnas esperadas."
    )

    st.stop()


# ============================================================
# CONVERTIR TIPOS
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
# UNIR RESULTADOS + PARTIDAS
# ============================================================

datos = resultados.merge(
    partidas[
        [
            "id",
            "fecha",
            "creado_por",
            "tipo_juego"
        ]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)


# ============================================================
# UNIR CON JUGADORES
# ============================================================

datos = datos.merge(
    jugadores[
        [
            "id",
            "nombre"
        ]
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
            [
                "jugador_id",
                "nombre"
            ],
            as_index=False
        )
        .agg(

            Partidas=(
                "partida_id",
                "nunique"
            ),

            Puntos=(
                "puntuacion",
                "sum"
            ),

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


    # ========================================================
    # MEDIA
    # ========================================================

    ranking["Media"] = (
        ranking["Puntos"] /
        ranking["Partidas"]
    )


    # ========================================================
    # MEJOR POSICIÓN
    # ========================================================

    mejores = (
        datos_tipo
        .groupby("jugador_id")["posicion"]
        .min()
        .reset_index()
    )


    mejores = mejores.rename(
        columns={
            "posicion": "Mejor posición"
        }
    )


    ranking = ranking.merge(
        mejores,
        on="jugador_id",
        how="left"
    )


    # ========================================================
    # ORDENAR POR PUNTOS
    # ========================================================

    ranking = ranking.sort_values(
        by="Puntos",
        ascending=False
    ).reset_index(drop=True)


    # ========================================================
    # POSICIÓN EN EL RANKING
    # ========================================================

    ranking.insert(
        0,
        "Pos.",
        range(
            1,
            len(ranking) + 1
        )
    )


    # ========================================================
    # RENOMBRAR
    # ========================================================

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
# ESTADÍSTICAS DEL JUGADOR
# ============================================================

def mostrar_jugador(
    jugador_id,
    tipo,
    ranking
):

    fila = ranking[
        ranking["jugador_id"] == jugador_id
    ]


    if fila.empty:

        st.warning(
            "No se han encontrado datos del jugador."
        )

        return


    jugador = fila.iloc[0]


    st.divider()


    # ========================================================
    # NOMBRE
    # ========================================================

    st.subheader(
        f"📊 Estadísticas de {jugador['Jugador']}"
    )


    # ========================================================
    # DATOS PRINCIPALES
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "🏆 Posición",
            f"{int(jugador['Pos.'])}º"
        )


    with col2:

        st.metric(
            "🎮 Partidas",
            int(jugador["Partidas"])
        )


    with col3:

        st.metric(
            "💰 Puntos",
            int(jugador["Puntos"])
        )


    with col4:

        st.metric(
            "📊 Media",
            f"{jugador['Media']:.2f}"
        )


    # ========================================================
    # POSICIONES
    # ========================================================

    st.markdown("### 🏆 Posiciones")


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
    # MEJOR POSICIÓN
    # ========================================================

    mejor_posicion = jugador["Mejor posición"]


    if pd.isna(mejor_posicion):

        mejor_texto = "-"

    else:

        mejor_texto = f"{int(mejor_posicion)}º"


    st.write(
        f"**Mejor posición conseguida:** {mejor_texto}"
    )


    # ========================================================
    # HISTORIAL
    # ========================================================

    st.markdown(
        "### 📅 Historial de partidas"
    )


    historial = datos[
        (datos["tipo_juego"] == tipo)
        &
        (datos["jugador_id"] == jugador_id)
    ].copy()


    if historial.empty:

        st.info(
            "Este jugador todavía no tiene partidas."
        )

        return


    historial = historial.sort_values(
        by="fecha",
        ascending=False
    )


    historial = historial[
        [
            "fecha",
            "partida_id",
            "posicion",
            "puntuacion"
        ]
    ].copy()


    historial = historial.rename(
        columns={
            "fecha": "Fecha",
            "partida_id": "Partida",
            "posicion": "Posición",
            "puntuacion": "Puntos"
        }
    )


    st.dataframe(
        historial,
        use_container_width=True,
        hide_index=True
    )


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


    # ========================================================
    # RESUMEN
    # ========================================================

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

        st.header("🀄 Ranking MCR")

    else:

        st.header("🇯🇵 Ranking RIICHI")


    # ========================================================
    # INFORMACIÓN GENERAL
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
    # TABLA DEL RANKING
    # ========================================================

    st.subheader(
        "🏆 Clasificación"
    )


    tabla = ranking[
        [
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
    ].copy()


    tabla["Media"] = tabla[
        "Media"
    ].round(2)


    # ========================================================
    # TABLA CLICABLE
    # ========================================================

    evento = st.dataframe(

        tabla,

        use_container_width=True,

        hide_index=True,

        on_select="rerun",

        selection_mode="single-row",

        key=f"tabla_ranking_{tipo}"
    )


    # ========================================================
    # JUGADOR SELECCIONADO
    # ========================================================

    filas_seleccionadas = (
        evento.selection.rows
    )


    if filas_seleccionadas:

        indice = filas_seleccionadas[0]


        jugador_id = ranking.iloc[
            indice
        ]["jugador_id"]


        mostrar_jugador(

            jugador_id,

            tipo,

            ranking
        )


    else:

        st.info(
            "👆 Haz clic sobre un jugador "
            "para ver sus estadísticas."
        )


# ============================================================
# CABECERA PRINCIPAL
# ============================================================

st.title(
    "🏆 Liga Mahjong Madrid"
)


st.write(
    "Ranking de jugadores de la Liga Mahjong Madrid"
)


# ============================================================
# LOGO
# ============================================================

if LOGO.exists():

    st.image(
        str(LOGO),
        width=180
    )

else:

    st.warning(
        "No se encuentra "
        "'logo_mahjong_madrid.png'. "
        "Colócalo en la misma carpeta que ranking.py."
    )


st.divider()


# ============================================================
# PESTAÑAS
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    [
        "🀄 RANKING MCR",
        "🇯🇵 RANKING RIICHI"
    ]
)


# ============================================================
# RANKING MCR
# ============================================================

with tab_mcr:

    mostrar_ranking("MCR")


# ============================================================
# RANKING RIICHI
# ============================================================

with tab_riichi:

    mostrar_ranking("RIICHI")
