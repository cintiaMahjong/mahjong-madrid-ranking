import streamlit as st
import pandas as pd
import urllib.request
import json
import os
import streamlit as st

# ============================================================
# CONFIG
# ============================================================

RUTA_LOGO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logo_mahjong_madrid.png"
)

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon=RUTA_LOGO,
    layout="centered"
)

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon=RUTA_LOGO,
    layout="centered"
)

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"

TEMPORADAS = [
    "Oct 2025 - Sept 2026",
    "Oct 2026 - Sept 2027"
]


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

    jugadores_data = supabase_get("jugadores")
    partidas_data = supabase_get("partidas")
    resultados_data = supabase_get("resultados_partidas")

except Exception as e:

    st.error("Error conectando con Supabase")
    st.code(str(e))
    st.stop()


df_jugadores = pd.DataFrame(jugadores_data)
df_partidas = pd.DataFrame(partidas_data)
df_resultados = pd.DataFrame(resultados_data)


# ============================================================
# COMPROBAR DATOS
# ============================================================

if df_jugadores.empty:
    st.error("La tabla jugadores está vacía.")
    st.stop()

if df_partidas.empty:
    st.error("La tabla partidas está vacía.")
    st.stop()

if df_resultados.empty:
    st.error("La tabla resultados_partidas está vacía.")
    st.stop()


# ============================================================
# NORMALIZAR PARTIDAS
# ============================================================

df_partidas["tipo_juego"] = (
    df_partidas["tipo_juego"]
    .fillna("")
    .astype(str)
    .str.upper()
    .str.strip()
)

df_partidas["temporada"] = (
    df_partidas["temporada"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# NORMALIZAR RESULTADOS
# ============================================================

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
# DETECTAR COLUMNA DEL NOMBRE
# ============================================================

if "nombre" in df_jugadores.columns:

    columna_nombre = "nombre"

elif "name" in df_jugadores.columns:

    columna_nombre = "name"

else:

    columna_nombre = None


# ============================================================
# UNIR RESULTADOS + JUGADORES + PARTIDAS
# ============================================================

datos = df_resultados.copy()


# Unir jugadores
datos = datos.merge(
    df_jugadores,
    left_on="jugador_id",
    right_on="id",
    how="left",
    suffixes=("", "_jugador")
)


# Unir partidas
datos = datos.merge(
    df_partidas[
        [
            "id",
            "fecha",
            "tipo_juego",
            "temporada"
        ]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)


# ============================================================
# CREAR NOMBRE DEL JUGADOR
# ============================================================

if columna_nombre is not None:

    if columna_nombre in datos.columns:

        datos["nombre_jugador"] = datos[
            columna_nombre
        ]

    elif f"{columna_nombre}_jugador" in datos.columns:

        datos["nombre_jugador"] = datos[
            f"{columna_nombre}_jugador"
        ]

    else:

        datos["nombre_jugador"] = (
            datos["jugador_id"].astype(str)
        )

else:

    datos["nombre_jugador"] = (
        datos["jugador_id"].astype(str)
    )


datos["nombre_jugador"] = (
    datos["nombre_jugador"]
    .fillna(datos["jugador_id"].astype(str))
    .astype(str)
)


# ============================================================
# FUNCIÓN CREAR RANKING
# ============================================================

def crear_ranking(tipo_juego, temporada):

    df = datos.copy()

    # Filtrar por tipo de juego y temporada
    df = df[
        (df["tipo_juego"] == tipo_juego) &
        (df["temporada"] == temporada)
    ]

    if df.empty:
        return pd.DataFrame()


    # --------------------------------------------------------
    # PUNTOS Y PARTIDAS JUGADAS
    # --------------------------------------------------------

    ranking = (
        df.groupby(
            [
                "jugador_id",
                "nombre_jugador"
            ],
            as_index=False
        )
        .agg(
            Puntos=("puntuacion", "sum"),
            Partidas=("partida_id", "nunique")
        )
    )


    # --------------------------------------------------------
    # PARTIDAS GANADAS
    # posicion = 1
    # --------------------------------------------------------

    if "posicion" in df.columns:

        ganadas = (
            df[df["posicion"] == 1]
            .groupby("jugador_id")["partida_id"]
            .nunique()
            .reset_index(name="Ganadas")
        )

        ranking = ranking.merge(
            ganadas,
            on="jugador_id",
            how="left"
        )

    else:

        ranking["Ganadas"] = 0


    ranking["Ganadas"] = (
        ranking["Ganadas"]
        .fillna(0)
        .astype(int)
    )


    # --------------------------------------------------------
    # MEDIA DE PUNTOS
    # Puntos / partidas jugadas
    # --------------------------------------------------------

    ranking["Media"] = (
        ranking["Puntos"] /
        ranking["Partidas"]
    ).round(1)


    # --------------------------------------------------------
    # MEDIA DE POSICIÓN
    #
    # Suma de posiciones / partidas jugadas
    # --------------------------------------------------------

    if "posicion" in df.columns:

        posiciones = (
            df.groupby("jugador_id")
            .agg(
                SumaPosiciones=("posicion", "sum")
            )
            .reset_index()
        )

        ranking = ranking.merge(
            posiciones,
            on="jugador_id",
            how="left"
        )

        ranking["MediaPosicion"] = (
            ranking["SumaPosiciones"] /
            ranking["Partidas"]
        ).round(2)

    else:

        ranking["MediaPosicion"] = 0


    # --------------------------------------------------------
    # ORDEN DEL RANKING
    # --------------------------------------------------------

    ranking = ranking.sort_values(
        "Puntos",
        ascending=False
    ).reset_index(drop=True)


    # Posición del ranking
    ranking["Posición"] = ranking.index + 1


    # Puntos como entero
    ranking["Puntos"] = (
        ranking["Puntos"]
        .round()
        .astype(int)
    )


    # --------------------------------------------------------
    # COLUMNAS FINALES
    # --------------------------------------------------------

    return ranking[
        [
            "Posición",
            "jugador_id",
            "nombre_jugador",
            "Puntos",
            "Partidas",
            "Ganadas",
            "Media",
            "MediaPosicion"
        ]
    ]


# ============================================================
# FUNCIÓN MOSTRAR FICHA DEL JUGADOR
# ============================================================

def mostrar_ficha(jugador_id):

    jugador_id_texto = str(jugador_id)


    # --------------------------------------------------------
    # BUSCAR JUGADOR
    # --------------------------------------------------------

    jugadores_busqueda = df_jugadores[
        df_jugadores["id"].astype(str)
        == jugador_id_texto
    ]


    # --------------------------------------------------------
    # OBTENER NOMBRE
    # --------------------------------------------------------

    if jugadores_busqueda.empty:

        datos_jugador = datos[
            datos["jugador_id"].astype(str)
            == jugador_id_texto
        ]

        if datos_jugador.empty:

            st.error(
                f"No se encuentra el jugador con ID: "
                f"{jugador_id_texto}"
            )

            return

        nombre = datos_jugador.iloc[0][
            "nombre_jugador"
        ]

    else:

        jugador = jugadores_busqueda.iloc[0]

        if columna_nombre is not None:

            nombre = jugador[columna_nombre]

        else:

            nombre = jugador_id_texto


    # ========================================================
    # VOLVER
    # ========================================================

    if st.button("← Volver al ranking"):

        st.session_state.jugador_seleccionado = None

        st.rerun()


    # ========================================================
    # CABECERA
    # ========================================================

    st.title("🀄 Ficha del jugador")

    st.header(str(nombre))


    # ========================================================
    # MCR
    # ========================================================

    st.subheader("🀄 MCR")

    pestañas_mcr = st.tabs(TEMPORADAS)


    for i, temporada in enumerate(TEMPORADAS):

        with pestañas_mcr[i]:

            df_mcr = datos[
                (datos["jugador_id"].astype(str) == jugador_id_texto) &
                (datos["tipo_juego"] == "MCR") &
                (datos["temporada"] == temporada)
            ].copy()


            if df_mcr.empty:

                st.info(
                    "No hay partidas MCR en esta temporada."
                )

                continue


            total_puntos = df_mcr[
                "puntuacion"
            ].sum()

            numero_partidas = df_mcr[
                "partida_id"
            ].nunique()


            media = (
                total_puntos / numero_partidas
                if numero_partidas > 0
                else 0
            )


            # Ranking MCR
            ranking_mcr = crear_ranking(
                "MCR",
                temporada
            )


            fila_ranking = ranking_mcr[
                ranking_mcr["jugador_id"].astype(str)
                == jugador_id_texto
            ]


            # ------------------------------------------------
            # DATOS
            # ------------------------------------------------

            st.metric(
                "Puntos totales",
                int(round(total_puntos))
            )


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "Partidas",
                    numero_partidas
                )


            with col2:

                st.metric(
                    "Media",
                    round(media, 1)
                )


            if not fila_ranking.empty:

                posicion = int(
                    fila_ranking.iloc[0]["Posición"]
                )

                ganadas = int(
                    fila_ranking.iloc[0]["Ganadas"]
                )

                media_posicion = float(
                    fila_ranking.iloc[0]["MediaPosicion"]
                )


                st.write(
                    f"**Posición en el ranking: "
                    f"{posicion}º**"
                )

                st.write(
                    f"**Partidas ganadas: "
                    f"{ganadas}**"
                )

                st.write(
                    f"**Media de posición: "
                    f"{media_posicion:.2f}**"
                )


            # ------------------------------------------------
            # HISTORIAL
            # ------------------------------------------------

            st.write("### Historial")


            historial = df_mcr[
                [
                    "fecha",
                    "puntuacion"
                ]
            ].copy()


            if "posicion" in df_mcr.columns:

                historial["Posición"] = (
                    df_mcr["posicion"]
                )


            historial = historial.rename(
                columns={
                    "fecha": "Fecha",
                    "puntuacion": "Puntos"
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

    st.subheader("🀄 RIICHI")

    pestañas_riichi = st.tabs(TEMPORADAS)


    for i, temporada in enumerate(TEMPORADAS):

        with pestañas_riichi[i]:

            df_riichi = datos[
                (datos["jugador_id"].astype(str) == jugador_id_texto) &
                (datos["tipo_juego"] == "RIICHI") &
                (datos["temporada"] == temporada)
            ].copy()


            if df_riichi.empty:

                st.info(
                    "No hay partidas RIICHI en esta temporada."
                )

                continue


            total_puntos = df_riichi[
                "puntuacion"
            ].sum()

            numero_partidas = df_riichi[
                "partida_id"
            ].nunique()


            media = (
                total_puntos / numero_partidas
                if numero_partidas > 0
                else 0
            )


            # Ranking RIICHI
            ranking_riichi = crear_ranking(
                "RIICHI",
                temporada
            )


            fila_ranking = ranking_riichi[
                ranking_riichi["jugador_id"].astype(str)
                == jugador_id_texto
            ]


            # ------------------------------------------------
            # DATOS
            # ------------------------------------------------

            st.metric(
                "Puntos totales",
                int(round(total_puntos))
            )


            col1, col2 = st.columns(2)


            with col1:

                st.metric(
                    "Partidas",
                    numero_partidas
                )


            with col2:

                st.metric(
                    "Media",
                    round(media, 1)
                )


            if not fila_ranking.empty:

                posicion = int(
                    fila_ranking.iloc[0]["Posición"]
                )

                ganadas = int(
                    fila_ranking.iloc[0]["Ganadas"]
                )

                media_posicion = float(
                    fila_ranking.iloc[0]["MediaPosicion"]
                )


                st.write(
                    f"**Posición en el ranking: "
                    f"{posicion}º**"
                )

                st.write(
                    f"**Partidas ganadas: "
                    f"{ganadas}**"
                )

                st.write(
                    f"**Media de posición: "
                    f"{media_posicion:.2f}**"
                )


            # ------------------------------------------------
            # HISTORIAL
            # ------------------------------------------------

            st.write("### Historial")


            historial = df_riichi[
                [
                    "fecha",
                    "puntuacion"
                ]
            ].copy()


            if "posicion" in df_riichi.columns:

                historial["Posición"] = (
                    df_riichi["posicion"]
                )


            historial = historial.rename(
                columns={
                    "fecha": "Fecha",
                    "puntuacion": "Puntos"
                }
            )


            st.dataframe(
                historial,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# ESTADO DE LA APLICACIÓN
# ============================================================

if "jugador_seleccionado" not in st.session_state:

    st.session_state.jugador_seleccionado = None


# ============================================================
# SI HAY JUGADOR SELECCIONADO
# ============================================================

if st.session_state.jugador_seleccionado is not None:

    mostrar_ficha(
        st.session_state.jugador_seleccionado
    )

    st.stop()


# ============================================================
# RANKING PRINCIPAL
# ============================================================

st.title("🀄 Liga Mahjong Madrid")


# ============================================================
# MCR / RIICHI
# ============================================================

tabs_juego = st.tabs(
    [
        "MCR",
        "RIICHI"
    ]
)


# ============================================================
# FUNCIÓN MOSTRAR RANKING
# ============================================================

def mostrar_ranking(tipo_juego):

    pestañas_temporadas = st.tabs(
        TEMPORADAS
    )


    for i, temporada in enumerate(TEMPORADAS):

        with pestañas_temporadas[i]:

            ranking = crear_ranking(
                tipo_juego,
                temporada
            )


            if ranking.empty:

                st.info(
                    f"No hay partidas {tipo_juego} "
                    f"en esta temporada."
                )

                continue


            st.subheader(
                f"Ranking {tipo_juego} — {temporada}"
            )


            # =================================================
            # ENCABEZADOS
            # =================================================

            cab1, cab2, cab3, cab4, cab5, cab6, cab7 = st.columns(
                [
                    0.6,
                    2.8,
                    1.1,
                    1.2,
                    1.1,
                    1.2,
                    1.4
                ]
            )


            with cab1:
                st.write("**Pos.**")


            with cab2:
                st.write("**Jugador**")


            with cab3:
                st.write("**Puntos**")


            with cab4:
                st.write("**Partidas**")


            with cab5:
                st.write("**Ganadas**")


            with cab6:
                st.write("**Media**")


            with cab7:
                st.write("**Media pos.**")


            # =================================================
            # FILAS DEL RANKING
            # =================================================

            for _, fila in ranking.iterrows():

                jugador_id = fila["jugador_id"]

                nombre = fila["nombre_jugador"]

                posicion = fila["Posición"]

                puntos = fila["Puntos"]

                partidas = fila["Partidas"]

                ganadas = fila["Ganadas"]

                media = fila["Media"]

                media_posicion = fila[
                    "MediaPosicion"
                ]


                col1, col2, col3, col4, col5, col6, col7 = st.columns(
                    [
                        0.6,
                        2.8,
                        1.1,
                        1.2,
                        1.1,
                        1.2,
                        1.4
                    ]
                )


                # Posición
                with col1:

                    st.write(
                        f"**{posicion}**"
                    )


                # Jugador
                with col2:

                    if st.button(
                        str(nombre),
                        key=(
                            f"{tipo_juego}_"
                            f"{temporada}_"
                            f"{str(jugador_id)}"
                        ),
                        use_container_width=True
                    ):

                        st.session_state.jugador_seleccionado = str(
                            jugador_id
                        )

                        st.rerun()


                # Puntos
                with col3:

                    st.write(
                        f"**{puntos}**"
                    )


                # Partidas
                with col4:

                    st.write(
                        str(partidas)
                    )


                # Ganadas
                with col5:

                    st.write(
                        str(ganadas)
                    )


                # Media de puntos
                with col6:

                    st.write(
                        f"{media:.1f}"
                    )


                # Media de posición
                with col7:

                    st.write(
                        f"{media_posicion:.2f}"
                    )


# ============================================================
# PESTAÑA MCR
# ============================================================

with tabs_juego[0]:

    mostrar_ranking("MCR")


# ============================================================
# PESTAÑA RIICHI
# ============================================================

with tabs_juego[1]:

    mostrar_ranking("RIICHI")
