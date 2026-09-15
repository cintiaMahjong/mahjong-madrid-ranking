import os
import streamlit as st
import pandas as pd
import urllib.request
import json


# ============================================================
# CONFIGURACIÓN
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

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"

TEMPORADAS = [
    "Oct 2025 - Sept 2026",
    "Oct 2026 - Sept 2027"
]


# ============================================================
# CONEXIÓN CON SUPABASE
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

    st.error("No se han podido cargar los datos de Supabase.")
    st.code(str(e))
    st.stop()


# ============================================================
# DATAFRAMES
# ============================================================

df_jugadores = pd.DataFrame(jugadores)
df_partidas = pd.DataFrame(partidas)
df_resultados = pd.DataFrame(resultados)


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
# NORMALIZAR DATOS
# ============================================================

if "tipo_juego" in df_partidas.columns:

    df_partidas["tipo_juego"] = (
        df_partidas["tipo_juego"]
        .astype(str)
        .str.upper()
        .str.strip()
    )


if "temporada" in df_partidas.columns:

    df_partidas["temporada"] = (
        df_partidas["temporada"]
        .astype(str)
        .str.strip()
    )


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
# NOMBRE DEL JUGADOR
# ============================================================

if "nombre" in df_jugadores.columns:

    COLUMNA_NOMBRE_JUGADOR = "nombre"

elif "name" in df_jugadores.columns:

    COLUMNA_NOMBRE_JUGADOR = "name"

else:

    st.error(
        "No encuentro la columna nombre/name en la tabla jugadores."
    )
    st.stop()


# ============================================================
# UNIR RESULTADOS + JUGADORES + PARTIDAS
# ============================================================

datos = df_resultados.merge(
    df_jugadores[
        [
            "id",
            COLUMNA_NOMBRE_JUGADOR
        ]
    ],
    left_on="jugador_id",
    right_on="id",
    how="left"
)


datos = datos.merge(
    df_partidas,
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)


datos["nombre_jugador"] = (
    datos[COLUMNA_NOMBRE_JUGADOR]
    .fillna("Sin nombre")
)


# ============================================================
# CREAR RANKING
# ============================================================

def crear_ranking(tipo_juego, temporada):

    df = datos.copy()

    df = df[
        (df["tipo_juego"] == tipo_juego) &
        (df["temporada"] == temporada)
    ]

    if df.empty:
        return pd.DataFrame()


    # --------------------------------------------------------
    # PUNTOS Y PARTIDAS
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
    # --------------------------------------------------------

    ranking["Media"] = (
        ranking["Puntos"] /
        ranking["Partidas"]
    ).round(1)


    # --------------------------------------------------------
    # MEDIA DE POSICIÓN
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
    # ORDENAR POR PUNTOS
    # --------------------------------------------------------

    ranking = ranking.sort_values(
        "Puntos",
        ascending=False
    ).reset_index(drop=True)


    ranking["Posición"] = ranking.index + 1


    ranking["Puntos"] = (
        ranking["Puntos"]
        .round()
        .astype(int)
    )


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
# HISTORIAL DE PARTIDAS
# ============================================================

def mostrar_historial(jugador_id, tipo_juego, temporada):

    jugador_id_texto = str(jugador_id)

    # --------------------------------------------------------
    # FILTRAR POR JUGADOR + JUEGO + TEMPORADA
    # --------------------------------------------------------

    datos_jugador = datos[
        (datos["jugador_id"].astype(str) == jugador_id_texto) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()


    if datos_jugador.empty:

        st.info(
            f"Este jugador no tiene partidas de {tipo_juego} "
            f"en esta temporada."
        )

        return


    # --------------------------------------------------------
    # PARTIDAS DEL JUGADOR
    # --------------------------------------------------------

    ids_partidas = (
        datos_jugador["partida_id"]
        .dropna()
        .unique()
    )


    # --------------------------------------------------------
    # TODAS LAS FILAS DE ESAS PARTIDAS
    # --------------------------------------------------------

    partidas_jugador = datos[
        datos["partida_id"].isin(ids_partidas)
    ].copy()


    # --------------------------------------------------------
    # ASEGURAR FILTRO DE JUEGO Y TEMPORADA
    # --------------------------------------------------------

    partidas_jugador = partidas_jugador[
        (partidas_jugador["tipo_juego"] == tipo_juego) &
        (partidas_jugador["temporada"] == temporada)
    ].copy()


    # --------------------------------------------------------
    # LISTA DE PARTIDAS
    # --------------------------------------------------------

    lista_partidas = []


    for partida_id in ids_partidas:

        partida = partidas_jugador[
            partidas_jugador["partida_id"] == partida_id
        ].copy()


        if partida.empty:
            continue


        # FECHA

        if "fecha" in partida.columns:

            fecha = partida.iloc[0]["fecha"]

        else:

            fecha = ""


        # NOMBRE PARTIDA

        nombre_partida = ""


        if "nombre_partida" in partida.columns:

            valor = partida.iloc[0]["nombre_partida"]

            if pd.notna(valor):

                nombre_partida = str(valor)


        elif "nombre" in partida.columns:

            valor = partida.iloc[0]["nombre"]

            if pd.notna(valor):

                nombre_partida = str(valor)


        lista_partidas.append(
            {
                "partida_id": partida_id,
                "fecha": fecha,
                "nombre_partida": nombre_partida
            }
        )


    # --------------------------------------------------------
    # ORDENAR POR FECHA
    # --------------------------------------------------------

    lista_partidas = sorted(
        lista_partidas,
        key=lambda x: (
            pd.to_datetime(
                x["fecha"],
                errors="coerce"
            )
            if pd.notna(x["fecha"])
            else pd.Timestamp.min
        ),
        reverse=True
    )


    # --------------------------------------------------------
    # MOSTRAR PARTIDAS
    # --------------------------------------------------------

    for info in lista_partidas:

        partida_id = info["partida_id"]

        fecha = info["fecha"]

        nombre_partida = info["nombre_partida"]


        partida_completa = partidas_jugador[
            partidas_jugador["partida_id"] == partida_id
        ].copy()


        if partida_completa.empty:
            continue


        # ORDENAR POR POSICIÓN

        if "posicion" in partida_completa.columns:

            partida_completa = (
                partida_completa
                .sort_values(
                    "posicion",
                    ascending=True
                )
            )


        # FORMATO FECHA

        try:

            fecha_formateada = pd.to_datetime(
                fecha
            ).strftime("%d/%m/%Y")

        except:

            fecha_formateada = str(fecha)


        # TÍTULO

        titulo = fecha_formateada


        if nombre_partida:

            titulo += f" — {nombre_partida}"


        # ----------------------------------------------------
        # CABECERA VERDE
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                background-color: #e8f5e9;
                padding: 10px 14px;
                border-radius: 8px;
                margin-top: 14px;
                margin-bottom: 6px;
                color: #2e7d32;
                font-weight: 600;
                font-size: 16px;
            ">
                {titulo}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # CABECERAS
        # ----------------------------------------------------

        c1, c2, c3 = st.columns(
            [3, 1.2, 1.2]
        )


        with c1:
            st.write("**Jugador**")


        with c2:
            st.write("**Puntos**")


        with c3:
            st.write("**Pos.**")


        # ----------------------------------------------------
        # JUGADORES
        # ----------------------------------------------------

        for _, fila in partida_completa.iterrows():

            jugador_id_fila = str(
                fila["jugador_id"]
            )

            nombre_fila = str(
                fila["nombre_jugador"]
            )


            # PUNTOS

            if pd.notna(fila["puntuacion"]):

                puntos_fila = int(
                    fila["puntuacion"]
                )

            else:

                puntos_fila = 0


            # POSICIÓN

            if (
                "posicion" in fila.index
                and pd.notna(fila["posicion"])
            ):

                posicion_fila = int(
                    fila["posicion"]
                )

            else:

                posicion_fila = ""


            # COMPROBAR JUGADOR ACTUAL

            es_actual = (
                jugador_id_fila
                == jugador_id_texto
            )


            if es_actual:

                fondo = "#eeeeee"
                peso = "600"

            else:

                fondo = "#ffffff"
                peso = "400"


            # FILA

            col1, col2, col3 = st.columns(
                [3, 1.2, 1.2]
            )


            with col1:

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 5px 8px;
                        border-radius: 5px;
                        font-weight: {peso};
                    ">
                        {nombre_fila}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with col2:

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 5px 8px;
                        border-radius: 5px;
                        font-weight: {peso};
                    ">
                        {puntos_fila}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            with col3:

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 5px 8px;
                        border-radius: 5px;
                        font-weight: {peso};
                    ">
                        {posicion_fila}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ESPACIO ENTRE PARTIDAS

        st.markdown(
            "<div style='height: 12px;'></div>",
            unsafe_allow_html=True
        )


# ============================================================
# MOSTRAR ESTADÍSTICAS DE UNA TEMPORADA
# ============================================================

def mostrar_estadisticas_jugador(
    jugador_id,
    tipo_juego,
    temporada
):

    jugador_id_texto = str(jugador_id)


    ranking = crear_ranking(
        tipo_juego,
        temporada
    )


    if ranking.empty:

        st.info(
            "No hay datos para esta temporada."
        )

        return


    jugador_ranking = ranking[
        ranking["jugador_id"].astype(str)
        == jugador_id_texto
    ]


    if jugador_ranking.empty:

        st.info(
            f"Este jugador no tiene partidas de "
            f"{tipo_juego} en esta temporada."
        )

        return


    fila = jugador_ranking.iloc[0]


    # --------------------------------------------------------
    # PRIMERA FILA
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Puntos",
            int(fila["Puntos"])
        )


    with col2:

        st.metric(
            "Partidas",
            int(fila["Partidas"])
        )


    with col3:

        st.metric(
            "Posición",
            int(fila["Posición"])
        )


    # --------------------------------------------------------
    # SEGUNDA FILA
    # --------------------------------------------------------

    col4, col5, col6 = st.columns(3)


    with col4:

        st.metric(
            "Media",
            f"{fila['Media']:.1f}"
        )


    with col5:

        st.metric(
            "Ganadas",
            int(fila["Ganadas"])
        )


    with col6:

        st.metric(
            "Media posición",
            f"{fila['MediaPosicion']:.2f}"
        )


# ============================================================
# FICHA DEL JUGADOR
# ============================================================

def mostrar_ficha(jugador_id):

    jugador_id_texto = str(jugador_id)


    # --------------------------------------------------------
    # BUSCAR NOMBRE
    # --------------------------------------------------------

    jugadores_busqueda = df_jugadores[
        df_jugadores["id"].astype(str)
        == jugador_id_texto
    ]


    if not jugadores_busqueda.empty:

        nombre_jugador = (
            jugadores_busqueda.iloc[0][
                COLUMNA_NOMBRE_JUGADOR
            ]
        )

    else:

        datos_jugador_busqueda = datos[
            datos["jugador_id"].astype(str)
            == jugador_id_texto
        ]


        if datos_jugador_busqueda.empty:

            st.error("No se encuentra el jugador.")
            return


        nombre_jugador = (
            datos_jugador_busqueda.iloc[0][
                "nombre_jugador"
            ]
        )


    # ========================================================
    # CABECERA
    # ========================================================

    st.title("🀄 Ficha del jugador")

    st.header(str(nombre_jugador))


    # ========================================================
    # MCR
    # ========================================================

    st.markdown(
        """
        <div style="
            background-color: #e8f5e9;
            padding: 12px 16px;
            border-radius: 8px;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #1b5e20;
            font-size: 22px;
            font-weight: 700;
        ">
            🀄 MCR
        </div>
        """,
        unsafe_allow_html=True
    )


    pestañas_mcr = st.tabs(
        TEMPORADAS
    )


    for i, temporada in enumerate(TEMPORADAS):

        with pestañas_mcr[i]:

            # ----------------------------------------------
            # ESTADÍSTICAS
            # ----------------------------------------------

            mostrar_estadisticas_jugador(
                jugador_id,
                "MCR",
                temporada
            )


            st.divider()


            # ----------------------------------------------
            # HISTORIAL
            # ----------------------------------------------

            st.markdown(
                "### 📋 Historial de partidas"
            )


            mostrar_historial(
                jugador_id,
                "MCR",
                temporada
            )


    # ========================================================
    # RIICHI
    # ========================================================

    st.markdown(
        """
        <div style="
            background-color: #e8f5e9;
            padding: 12px 16px;
            border-radius: 8px;
            margin-top: 30px;
            margin-bottom: 10px;
            color: #1b5e20;
            font-size: 22px;
            font-weight: 700;
        ">
            🀄 RIICHI
        </div>
        """,
        unsafe_allow_html=True
    )


    pestañas_riichi = st.tabs(
        TEMPORADAS
    )


    for i, temporada in enumerate(TEMPORADAS):

        with pestañas_riichi[i]:

            # ----------------------------------------------
            # ESTADÍSTICAS
            # ----------------------------------------------

            mostrar_estadisticas_jugador(
                jugador_id,
                "RIICHI",
                temporada
            )


            st.divider()


            # ----------------------------------------------
            # HISTORIAL
            # ----------------------------------------------

            st.markdown(
                "### 📋 Historial de partidas"
            )


            mostrar_historial(
                jugador_id,
                "RIICHI",
                temporada
            )


    # ========================================================
    # VOLVER
    # ========================================================

    st.divider()


    if st.button(
        "← Volver al ranking",
        use_container_width=True
    ):

        st.session_state.jugador_seleccionado = None

        st.rerun()


# ============================================================
# SESSION STATE
# ============================================================

if "jugador_seleccionado" not in st.session_state:

    st.session_state.jugador_seleccionado = None


# ============================================================
# MOSTRAR FICHA SI HAY JUGADOR SELECCIONADO
# ============================================================

if st.session_state.jugador_seleccionado is not None:

    mostrar_ficha(
        st.session_state.jugador_seleccionado
    )

    st.stop()


# ============================================================
# MOSTRAR RANKING
# ============================================================

def mostrar_ranking(tipo_juego):

    st.subheader(
        f"Ranking {tipo_juego}"
    )


    pestañas = st.tabs(
        TEMPORADAS
    )


    for i, temporada in enumerate(TEMPORADAS):

        with pestañas[i]:

            ranking = crear_ranking(
                tipo_juego,
                temporada
            )


            if ranking.empty:

                st.info(
                    "No hay datos para esta temporada."
                )

                continue


            # =================================================
            # CABECERAS
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
            # FILAS
            # =================================================

            for _, fila in ranking.iterrows():

                jugador_id = fila[
                    "jugador_id"
                ]

                nombre = fila[
                    "nombre_jugador"
                ]

                posicion = fila[
                    "Posición"
                ]

                puntos = fila[
                    "Puntos"
                ]

                partidas_jugadas = fila[
                    "Partidas"
                ]

                ganadas = fila[
                    "Ganadas"
                ]

                media = fila[
                    "Media"
                ]

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


                with col1:

                    st.write(
                        f"**{posicion}**"
                    )


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


                with col3:

                    st.write(
                        f"**{puntos}**"
                    )


                with col4:

                    st.write(
                        str(partidas_jugadas)
                    )


                with col5:

                    st.write(
                        str(ganadas)
                    )


                with col6:

                    st.write(
                        f"{media:.1f}"
                    )


                with col7:

                    st.write(
                        f"{media_posicion:.2f}"
                    )


# ============================================================
# TÍTULO PRINCIPAL
# ============================================================

st.title("🀄 Liga Mahjong Madrid")


# ============================================================
# MCR / RIICHI
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    [
        "MCR",
        "RIICHI"
    ]
)


with tab_mcr:

    mostrar_ranking("MCR")


with tab_riichi:

    mostrar_ranking("RIICHI")
