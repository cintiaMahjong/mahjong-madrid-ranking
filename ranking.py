import streamlit as st
import pandas as pd
import urllib.request
import json


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered"
)

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"


# ============================================================
# CONEXIÓN SUPABASE
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


# ============================================================
# DATAFRAMES
# ============================================================

df_jugadores = pd.DataFrame(jugadores)

df_partidas = pd.DataFrame(partidas)

df_resultados = pd.DataFrame(resultados)


# ============================================================
# NORMALIZAR PARTIDAS
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


# ============================================================
# NORMALIZAR RESULTADOS
# ============================================================

if "puntuacion" in df_resultados.columns:

    df_resultados["puntuacion"] = pd.to_numeric(
        df_resultados["puntuacion"],
        errors="coerce"
    ).fillna(0)


if "posicion" in df_resultados.columns:

    df_resultados["posicion"] = pd.to_numeric(
        df_resultados["posicion"],
        errors="coerce"
    )


# ============================================================
# UNIR RESULTADOS + JUGADORES
# ============================================================

datos = df_resultados.copy()


if (
    "jugador_id" in datos.columns
    and "id" in df_jugadores.columns
):

    datos = datos.merge(
        df_jugadores,
        left_on="jugador_id",
        right_on="id",
        how="left",
        suffixes=("", "_jugador")
    )


# ============================================================
# UNIR RESULTADOS + PARTIDAS
# ============================================================

if (
    "partida_id" in datos.columns
    and "id" in df_partidas.columns
):

    columnas_partida = ["id"]

    if "fecha" in df_partidas.columns:
        columnas_partida.append("fecha")

    if "tipo_juego" in df_partidas.columns:
        columnas_partida.append("tipo_juego")

    if "temporada" in df_partidas.columns:
        columnas_partida.append("temporada")

    datos = datos.merge(
        df_partidas[columnas_partida],
        left_on="partida_id",
        right_on="id",
        how="left",
        suffixes=("", "_partida")
    )


# ============================================================
# ASEGURAR NOMBRE
# ============================================================

if "nombre" not in datos.columns:

    posibles_nombres = [
        "nombre_jugador",
        "name",
        "jugador"
    ]

    columna_nombre = None

    for columna in posibles_nombres:

        if columna in datos.columns:

            columna_nombre = columna

            break


    if columna_nombre:

        datos["nombre"] = datos[columna_nombre]

    else:

        datos["nombre"] = (
            datos["jugador_id"]
            .astype(str)
        )


datos["nombre"] = (
    datos["nombre"]
    .fillna("Jugador")
    .astype(str)
    .str.strip()
)


# ============================================================
# TEMPORADAS
# ============================================================

TEMPORADAS = [
    "Oct 2025 - Sept 2026",
    "Oct 2026 - Sept 2027"
]


# ============================================================
# FUNCIÓN CREAR RANKING
# ============================================================

def crear_ranking(tipo_juego, temporada):

    df = datos.copy()

    df = df[
        df["tipo_juego"] == tipo_juego
    ]

    df = df[
        df["temporada"] == temporada
    ]

    if df.empty:

        return pd.DataFrame()

    ranking = (
        df.groupby(
            ["jugador_id", "nombre"],
            as_index=False
        )
        .agg(
            Puntos=("puntuacion", "sum"),
            Partidas=("partida_id", "nunique")
        )
    )

    ranking = ranking.sort_values(
        "Puntos",
        ascending=False
    ).reset_index(drop=True)

    ranking["Posición"] = (
        ranking.index + 1
    )

    ranking["Puntos"] = (
        ranking["Puntos"]
        .round()
        .astype(int)
    )

    return ranking[
        [
            "Posición",
            "jugador_id",
            "nombre",
            "Puntos",
            "Partidas"
        ]
    ]


# ============================================================
# FUNCIÓN MOSTRAR FICHA
# ============================================================

def mostrar_ficha(jugador_id):

    # --------------------------------------------------------
    # BUSCAR INFORMACIÓN DEL JUGADOR
    # --------------------------------------------------------

    jugador = df_jugadores[
        df_jugadores["id"].astype(str)
        == str(jugador_id)
    ]

    if jugador.empty:

        st.error(
            "No se ha encontrado el jugador."
        )

        return


    jugador = jugador.iloc[0]


    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    if "nombre" in jugador.index:

        nombre = jugador["nombre"]

    elif "name" in jugador.index:

        nombre = jugador["name"]

    else:

        nombre = "Jugador"


    # --------------------------------------------------------
    # CABECERA
    # --------------------------------------------------------

    st.title("🀄 Ficha del jugador")

    st.header(
        str(nombre)
    )

    st.divider()


    # --------------------------------------------------------
    # DATOS DEL JUGADOR
    # --------------------------------------------------------

    datos_jugador = datos[
        datos["jugador_id"].astype(str)
        == str(jugador_id)
    ].copy()


    if datos_jugador.empty:

        st.info(
            "Este jugador no tiene partidas registradas."
        )

        return


    # ========================================================
    # MCR
    # ========================================================

    st.header("MCR")


    pestañas_mcr = st.tabs(
        TEMPORADAS
    )


    for i, temporada in enumerate(
        TEMPORADAS
    ):

        with pestañas_mcr[i]:

            df = datos_jugador[
                (datos_jugador["tipo_juego"] == "MCR")
                &
                (datos_jugador["temporada"] == temporada)
            ].copy()


            if df.empty:

                st.info(
                    "No tiene partidas en esta temporada."
                )

                continue


            # --------------------------------------------
            # ESTADÍSTICAS
            # --------------------------------------------

            puntos = int(
                df["puntuacion"].sum()
            )

            partidas_jugadas = int(
                df["partida_id"].nunique()
            )

            media = round(
                puntos / partidas_jugadas,
                1
            ) if partidas_jugadas else 0


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Puntos",
                    puntos
                )


            with col2:

                st.metric(
                    "Partidas",
                    partidas_jugadas
                )


            with col3:

                st.metric(
                    "Media",
                    media
                )


            # --------------------------------------------
            # POSICIÓN EN RANKING
            # --------------------------------------------

            ranking = crear_ranking(
                "MCR",
                temporada
            )


            jugador_ranking = ranking[
                ranking["jugador_id"].astype(str)
                == str(jugador_id)
            ]


            if not jugador_ranking.empty:

                posicion = int(
                    jugador_ranking.iloc[0]["Posición"]
                )

                st.write(
                    f"**Posición en el ranking: {posicion}**"
                )


            # --------------------------------------------
            # HISTORIAL
            # --------------------------------------------

            st.subheader(
                "Partidas"
            )


            columnas = []


            if "fecha" in df.columns:

                columnas.append("fecha")


            columnas.append(
                "puntuacion"
            )


            if "posicion" in df.columns:

                columnas.append(
                    "posicion"
                )


            historial = df[
                [
                    columna
                    for columna in columnas
                    if columna in df.columns
                ]
            ].copy()


            historial = historial.rename(
                columns={
                    "fecha": "Fecha",
                    "puntuacion": "Puntuación",
                    "posicion": "Posición"
                }
            )


            st.dataframe(
                historial,
                use_container_width=True,
                hide_index=True
            )


    # ========================================================
    # RIICHI
    # ========================================================

    st.divider()

    st.header("RIICHI")


    pestañas_riichi = st.tabs(
        TEMPORADAS
    )


    for i, temporada in enumerate(
        TEMPORADAS
    ):

        with pestañas_riichi[i]:

            df = datos_jugador[
                (datos_jugador["tipo_juego"] == "RIICHI")
                &
                (datos_jugador["temporada"] == temporada)
            ].copy()


            if df.empty:

                st.info(
                    "No tiene partidas en esta temporada."
                )

                continue


            # --------------------------------------------
            # ESTADÍSTICAS
            # --------------------------------------------

            puntos = int(
                df["puntuacion"].sum()
            )

            partidas_jugadas = int(
                df["partida_id"].nunique()
            )

            media = round(
                puntos / partidas_jugadas,
                1
            ) if partidas_jugadas else 0


            col1, col2, col3 = st.columns(3)


            with col1:

                st.metric(
                    "Puntos",
                    puntos
                )


            with col2:

                st.metric(
                    "Partidas",
                    partidas_jugadas
                )


            with col3:

                st.metric(
                    "Media",
                    media
                )


            # --------------------------------------------
            # POSICIÓN EN RANKING
            # --------------------------------------------

            ranking = crear_ranking(
                "RIICHI",
                temporada
            )


            jugador_ranking = ranking[
                ranking["jugador_id"].astype(str)
                == str(jugador_id)
            ]


            if not jugador_ranking.empty:

                posicion = int(
                    jugador_ranking.iloc[0]["Posición"]
                )

                st.write(
                    f"**Posición en el ranking: {posicion}**"
                )


            # --------------------------------------------
            # HISTORIAL
            # --------------------------------------------

            st.subheader(
                "Partidas"
            )


            columnas = []


            if "fecha" in df.columns:

                columnas.append("fecha")


            columnas.append(
                "puntuacion"
            )


            if "posicion" in df.columns:

                columnas.append(
                    "posicion"
                )


            historial = df[
                [
                    columna
                    for columna in columnas
                    if columna in df.columns
                ]
            ].copy()


            historial = historial.rename(
                columns={
                    "fecha": "Fecha",
                    "puntuacion": "Puntuación",
                    "posicion": "Posición"
                }
            )


            st.dataframe(
                historial,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# ESTADO DEL JUGADOR SELECCIONADO
# ============================================================

if "jugador_seleccionado" not in st.session_state:

    st.session_state.jugador_seleccionado = None


# ============================================================
# SI HAY JUGADOR SELECCIONADO
# ============================================================

if st.session_state.jugador_seleccionado is not None:

    if st.button(
        "← Volver al ranking"
    ):

        st.session_state.jugador_seleccionado = None

        st.rerun()


    mostrar_ficha(
        st.session_state.jugador_seleccionado
    )

    st.stop()


# ============================================================
# RANKING PRINCIPAL
# ============================================================

st.title("🀄 Liga Mahjong Madrid")

st.write(
    "Ranking de jugadores"
)


# ============================================================
# PESTAÑAS MCR / RIICHI
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    [
        "MCR",
        "RIICHI"
    ]
)


# ============================================================
# FUNCIÓN MOSTRAR RANKING
# ============================================================

def mostrar_modalidad(tipo_juego):

    st.subheader(
        f"Ranking {tipo_juego}"
    )


    pestañas = st.tabs(
        TEMPORADAS
    )


    for i, temporada in enumerate(
        TEMPORADAS
    ):

        with pestañas[i]:

            ranking = crear_ranking(
                tipo_juego,
                temporada
            )


            if ranking.empty:

                st.info(
                    f"No hay partidas de "
                    f"{tipo_juego} para "
                    f"{temporada}."
                )

                continue


            # ------------------------------------------------
            # ENCABEZADOS
            # ------------------------------------------------

            cab1, cab2, cab3, cab4 = st.columns(
                [0.7, 3, 1.2, 1]
            )


            with cab1:

                st.write(
                    "**Pos.**"
                )


            with cab2:

                st.write(
                    "**Jugador**"
                )


            with cab3:

                st.write(
                    "**Puntos**"
                )


            with cab4:

                st.write(
                    "**Partidas**"
                )


            # ------------------------------------------------
            # JUGADORES
            # ------------------------------------------------

            for _, fila in ranking.iterrows():

                jugador_id = fila[
                    "jugador_id"
                ]

                nombre = fila[
                    "nombre"
                ]

                posicion = int(
                    fila["Posición"]
                )

                puntos = int(
                    fila["Puntos"]
                )

                numero_partidas = int(
                    fila["Partidas"]
                )


                col1, col2, col3, col4 = st.columns(
                    [0.7, 3, 1.2, 1]
                )


                with col1:

                    st.write(
                        posicion
                    )


                with col2:

                    if st.button(
                        nombre,
                        key=(
                            f"{tipo_juego}_"
                            f"{temporada}_"
                            f"{jugador_id}"
                        ),
                        use_container_width=True
                    ):

                        st.session_state.jugador_seleccionado = (
                            jugador_id
                        )

                        st.rerun()


                with col3:

                    st.write(
                        puntos
                    )


                with col4:

                    st.write(
                        numero_partidas
                    )


# ============================================================
# MCR
# ============================================================

with tab_mcr:

    mostrar_modalidad(
        "MCR"
    )


# ============================================================
# RIICHI
# ============================================================

with tab_riichi:

    mostrar_modalidad(
        "RIICHI"
    )
