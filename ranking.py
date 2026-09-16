import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import os
import streamlit.components.v1 as components

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
        max-width: 900px;
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

        query = urllib.parse.urlencode(
            parametros
        )

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

        contenido = response.read().decode(
            "utf-8"
        )

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

    df_jugadores = pd.DataFrame(
        jugadores
    )

    df_partidas = pd.DataFrame(
        partidas
    )

    df_resultados = pd.DataFrame(
        resultados
    )

    return (
        df_jugadores,
        df_partidas,
        df_resultados
    )


# =========================================================
# EJECUTAR CARGA DE DATOS
# =========================================================

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
# =========================================================

datos = df_resultados.copy()


# =========================================================
# UNIR DATOS DE LAS PARTIDAS
# =========================================================

if not df_partidas.empty:

    columnas_partidas = [
        columna
        for columna in [
            "id",
            "fecha",
            "tipo_juego",
            "temporada",
            "nombre",
            "nombre_partida"
        ]
        if columna in df_partidas.columns
    ]

    df_partidas_merge = (
        df_partidas[
            columnas_partidas
        ]
        .copy()
    )

    df_partidas_merge = (
        df_partidas_merge.rename(
            columns={
                "id": "partida_id"
            }
        )
    )

    datos = datos.merge(
        df_partidas_merge,
        on="partida_id",
        how="left"
    )


# =========================================================
# UNIR DATOS DE LOS JUGADORES
# =========================================================

if not df_jugadores.empty:

    columnas_jugadores = [
        columna
        for columna in [
            "id",
            "nombre",
            "name"
        ]
        if columna in df_jugadores.columns
    ]

    df_jugadores_merge = (
        df_jugadores[
            columnas_jugadores
        ]
        .copy()
    )

    if "nombre" not in df_jugadores_merge.columns:

        if "name" in df_jugadores_merge.columns:

            df_jugadores_merge["nombre"] = (
                df_jugadores_merge["name"]
            )

    df_jugadores_merge = df_jugadores_merge[
        ["id", "nombre"]
    ]

    df_jugadores_merge = (
        df_jugadores_merge.rename(
            columns={
                "id": "jugador_id",
                "nombre": "nombre_jugador"
            }
        )
    )

    datos = datos.merge(
        df_jugadores_merge,
        on="jugador_id",
        how="left"
    )
# =========================================================
# NORMALIZAR COLUMNAS
# =========================================================

if "puntuacion" in datos.columns:

    datos["puntuacion"] = pd.to_numeric(
        datos["puntuacion"],
        errors="coerce"
    ).fillna(0)

else:

    datos["puntuacion"] = 0


# =========================================================
# NORMALIZAR POSICIÓN
# =========================================================

if "posicion" in datos.columns:

    datos["posicion"] = pd.to_numeric(
        datos["posicion"],
        errors="coerce"
    )


# =========================================================
# TIPO DE JUEGO
# =========================================================

if "tipo_juego" not in datos.columns:

    datos["tipo_juego"] = ""


# =========================================================
# TEMPORADA
# =========================================================

if "temporada" not in datos.columns:

    datos["temporada"] = ""


# =========================================================
# NOMBRE DEL JUGADOR
# =========================================================

if "nombre_jugador" not in datos.columns:

    datos["nombre_jugador"] = "Jugador"


# =========================================================
# SESIÓN
# =========================================================

if "jugador_seleccionado" not in st.session_state:

    st.session_state.jugador_seleccionado = None

# =========================================================
# CREAR RANKING
# =========================================================

def crear_ranking(
    tipo_juego,
    temporada
):

    df = datos.copy()

    # =====================================================
    # FILTRAR TIPO DE JUEGO Y TEMPORADA
    # =====================================================

    df = df[
        (df["tipo_juego"] == tipo_juego)
        &
        (df["temporada"] == temporada)
    ].copy()

    if df.empty:

        return pd.DataFrame()

    # =====================================================
    # UNA SOLA FILA POR JUGADOR Y PARTIDA
    # =====================================================

    df = df.drop_duplicates(
        subset=[
            "partida_id",
            "jugador_id"
        ]
    ).copy()

    # =====================================================
    # NORMALIZAR PUNTUACIÓN
    # =====================================================

    df["puntuacion"] = pd.to_numeric(
        df["puntuacion"],
        errors="coerce"
    ).fillna(0)

    # =====================================================
    # NORMALIZAR POSICIÓN
    # =====================================================

    if "posicion" in df.columns:

        df["posicion"] = pd.to_numeric(
            df["posicion"],
            errors="coerce"
        )

    # =====================================================
    # ESTADÍSTICAS PRINCIPALES
    # =====================================================

    ranking = (
        df.groupby(
            [
                "jugador_id",
                "nombre_jugador"
            ],
            as_index=False
        )
        .agg(
            Puntos=(
                "puntuacion",
                "sum"
            ),

            Partidas=(
                "partida_id",
                "nunique"
            ),

            Media=(
                "puntuacion",
                "mean"
            ),

            PuntuacionMaxima=(
                "puntuacion",
                "max"
            )
        )
    )

    # =====================================================
    # PARTIDAS GANADAS
    # =====================================================

    if "posicion" in df.columns:

        ganadas = (
            df[
                df["posicion"] == 1
            ]
            .groupby(
                "jugador_id"
            )["partida_id"]
            .nunique()
            .reset_index(
                name="Ganadas"
            )
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

    # =====================================================
    # WINRATE
    # =====================================================

    ranking["Winrate"] = (
        ranking["Ganadas"]
        /
        ranking["Partidas"]
        *
        100
    ).fillna(0).round(1)

    # =====================================================
    # MEDIA DE POSICIÓN
    # =====================================================

    if "posicion" in df.columns:

        posiciones = (
            df.groupby(
                "jugador_id"
            )
            .agg(
                SumaPosiciones=(
                    "posicion",
                    "sum"
                )
            )
            .reset_index()
        )

        ranking = ranking.merge(
            posiciones,
            on="jugador_id",
            how="left"
        )

        ranking["MediaPosicion"] = (
            ranking["SumaPosiciones"]
            /
            ranking["Partidas"]
        ).round(2)

    else:

        ranking["MediaPosicion"] = 0

    # =====================================================
    # REDONDEAR VALORES
    # =====================================================

    ranking["Puntos"] = (
        ranking["Puntos"]
        .round()
        .astype(int)
    )

    ranking["Media"] = (
        ranking["Media"]
        .round(1)
    )

    ranking["PuntuacionMaxima"] = (
        ranking["PuntuacionMaxima"]
        .round()
        .astype(int)
    )

    ranking["MediaPosicion"] = (
        ranking["MediaPosicion"]
        .fillna(0)
        .round(2)
    )

    # =====================================================
    # ORDENAR RANKING
    # =====================================================

    ranking = ranking.sort_values(
        "Puntos",
        ascending=False
    ).reset_index(
        drop=True
    )

    # =====================================================
    # POSICIÓN DEL RANKING
    # =====================================================

    ranking["Posición"] = (
        ranking.index + 1
    )

    # =====================================================
    # COLUMNAS FINALES
    # =====================================================

    return ranking[
        [
            "Posición",
            "jugador_id",
            "nombre_jugador",
            "Puntos",
            "Partidas",
            "Ganadas",
            "Winrate",
            "Media",
            "PuntuacionMaxima",
            "MediaPosicion"
        ]
    ]

# =========================================================
# INDICADORES DEL JUGADOR
# =========================================================

def mostrar_indicadores(
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

    # =====================================================
    # PRIMERA FILA
    # =====================================================

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

    # =====================================================
    # SEGUNDA FILA
    # =====================================================

    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "WINRATE",
            f"{float(fila['Winrate']):.1f}%"
        )

    with col5:

        st.metric(
            "Ganadas",
            int(fila["Ganadas"])
        )

    with col6:

        st.metric(
            "Media posición",
            f"{float(fila['MediaPosicion']):.2f}"
        )

    # =====================================================
    # TERCERA FILA
    # =====================================================

    col7, col8 = st.columns(2)

    with col7:

        st.metric(
            "Puntuación media",
            f"{float(fila['Media']):.1f}"
        )

    with col8:

        st.metric(
            "Puntuación máxima",
            int(fila["PuntuacionMaxima"])
        )


# =========================================================
# DISTRIBUCIÓN DE POSICIONES
# =========================================================

def mostrar_distribucion_posiciones(
    jugador_id,
    tipo_juego,
    temporada
):

    jugador_id_texto = str(jugador_id)

    df = datos[
        (datos["jugador_id"].astype(str) == jugador_id_texto)
        &
        (datos["tipo_juego"] == tipo_juego)
        &
        (datos["temporada"] == temporada)
    ].copy()

    if df.empty:

        return

    if "posicion" not in df.columns:

        return

    # =====================================================
    # UNA FILA POR PARTIDA
    # =====================================================

    df = df.drop_duplicates(
        subset=[
            "partida_id",
            "jugador_id"
        ]
    )

    df["posicion"] = pd.to_numeric(
        df["posicion"],
        errors="coerce"
    )

    # =====================================================
    # CONTAR POSICIONES
    # =====================================================

    posicion_1 = int(
        (df["posicion"] == 1).sum()
    )

    posicion_2 = int(
        (df["posicion"] == 2).sum()
    )

    posicion_3 = int(
        (df["posicion"] == 3).sum()
    )

    posicion_4 = int(
        (df["posicion"] == 4).sum()
    )

    posicion_5 = int(
        (df["posicion"] == 5).sum()
    )

    # =====================================================
    # TÍTULO
    # =====================================================

    st.subheader(
        "📊 Posiciones"
    )

    # =====================================================
    # TABLA HORIZONTAL
    # =====================================================

    tabla_posiciones = pd.DataFrame(
        {
            "🥇 1ª": [posicion_1],
            "🥈 2ª": [posicion_2],
            "🥉 3ª": [posicion_3],
            "4ª": [posicion_4],
            "5ª": [posicion_5]
        }
    )

    st.table(
        tabla_posiciones
    )

# =========================================================
# HISTORIAL
# =========================================================

def mostrar_historial(
    jugador_id,
    tipo_juego,
    temporada
):

    jugador_id_texto = str(jugador_id)

    datos_jugador = datos[
        (datos["jugador_id"].astype(str) == jugador_id_texto)
        &
        (datos["tipo_juego"] == tipo_juego)
        &
        (datos["temporada"] == temporada)
    ].copy()

    if datos_jugador.empty:

        st.info(
            f"Este jugador no tiene partidas de "
            f"{tipo_juego} en esta temporada."
        )

        return

    # =====================================================
    # IDENTIFICAR PARTIDAS
    # =====================================================

    ids_partidas = (
        datos_jugador["partida_id"]
        .dropna()
        .unique()
    )

    partidas_jugador = datos[
        datos["partida_id"].isin(ids_partidas)
    ].copy()

    partidas_jugador = partidas_jugador[
        (partidas_jugador["tipo_juego"] == tipo_juego)
        &
        (partidas_jugador["temporada"] == temporada)
    ].copy()

    if partidas_jugador.empty:

        st.info(
            "No hay historial."
        )

        return

    # =====================================================
    # INFORMACIÓN DE PARTIDAS
    # =====================================================

    partidas_info = (
        partidas_jugador[
            [
                "partida_id",
                "fecha"
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    partidas_info["fecha_orden"] = pd.to_datetime(
        partidas_info["fecha"],
        errors="coerce"
    )

    partidas_info = partidas_info.sort_values(
        "fecha_orden",
        ascending=False
    )

    # =====================================================
    # CADA PARTIDA
    # =====================================================

    for _, partida in partidas_info.iterrows():

        partida_id = partida["partida_id"]

        datos_partida = partidas_jugador[
            partidas_jugador["partida_id"] == partida_id
        ].copy()

        if datos_partida.empty:

            continue

        datos_partida = datos_partida.sort_values(
            "posicion",
            ascending=True,
            na_position="last"
        )

        # =================================================
        # FECHA
        # =================================================

        fecha = partida["fecha"]

        try:

            fecha_formateada = pd.to_datetime(
                fecha
            ).strftime(
                "%d/%m/%Y"
            )

        except Exception:

            fecha_formateada = str(
                fecha
            )

        # =================================================
        # NOMBRE DE LA PARTIDA
        # =================================================

        nombre_partida = ""

        if "nombre_partida" in datos_partida.columns:

            valores = datos_partida[
                "nombre_partida"
            ].dropna()

            if not valores.empty:

                nombre_partida = str(
                    valores.iloc[0]
                )

        if not nombre_partida:

            if "nombre" in datos_partida.columns:

                valores = datos_partida[
                    "nombre"
                ].dropna()

                if not valores.empty:

                    nombre_partida = str(
                        valores.iloc[0]
                    )

        if nombre_partida:

            titulo_partida = (
                f"{fecha_formateada} · "
                f"{nombre_partida}"
            )

        else:

            titulo_partida = fecha_formateada

        # =================================================
        # CABECERA DE LA PARTIDA
        # =================================================

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
                {titulo_partida}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =================================================
        # CABECERA DE JUGADORES
        # =================================================

        cab1, cab2, cab3 = st.columns(
            [3, 1, 1]
        )

        with cab1:

            st.markdown(
                "**Jugador**"
            )

        with cab2:

            st.markdown(
                "**Puntos**"
            )

        with cab3:

            st.markdown(
                "**Pos.**"
            )

        # =================================================
        # JUGADORES
        # =================================================

        for _, fila in datos_partida.iterrows():

            nombre = str(
                fila.get(
                    "nombre_jugador",
                    "Jugador"
                )
            )

            puntuacion = fila.get(
                "puntuacion",
                0
            )

            posicion = fila.get(
                "posicion",
                ""
            )

            # =============================================
            # FORMATEAR PUNTUACIÓN
            # =============================================

            try:

                puntuacion = int(
                    round(
                        float(
                            puntuacion
                        )
                    )
                )

            except Exception:

                puntuacion = 0

            # =============================================
            # FORMATEAR POSICIÓN
            # =============================================

            try:

                posicion = int(
                    float(
                        posicion
                    )
                )

            except Exception:

                posicion = ""

            # =============================================
            # JUGADOR SELECCIONADO
            # =============================================

            es_jugador = (
                str(
                    fila["jugador_id"]
                )
                ==
                jugador_id_texto
            )

            if es_jugador:

                fondo = "#eeeeee"
                peso = "600"

            else:

                fondo = "#ffffff"
                peso = "400"

            # =============================================
            # COLUMNAS
            # =============================================

            c1, c2, c3 = st.columns(
                [3, 1, 1]
            )

            with c1:

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 7px 6px;
                        font-weight: {peso};
                        border-radius: 5px;
                        margin-bottom: 3px;
                    ">
                        {nombre}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 7px 6px;
                        font-weight: {peso};
                        border-radius: 5px;
                        margin-bottom: 3px;
                        text-align: center;
                    ">
                        {puntuacion}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c3:

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 7px 6px;
                        font-weight: {peso};
                        border-radius: 5px;
                        margin-bottom: 3px;
                        text-align: center;
                    ">
                        {posicion}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(
            "<div style='height: 8px;'></div>",
            unsafe_allow_html=True
        )
# =========================================================
# FICHA DEL JUGADOR
# =========================================================

def mostrar_ficha(jugador_id):

    # =====================================================
    # CABECERA DE LA FICHA
    # =====================================================

    cabecera_titulo, cabecera_boton = st.columns(
        [3, 1]
    )

    with cabecera_titulo:

        st.title(
            "🀄 Ficha del jugador"
        )

    with cabecera_boton:

        if st.button(
            "← Volver",
            key="volver_arriba",
            use_container_width=True
        ):

            st.session_state.jugador_seleccionado = None
            st.rerun()

    # =====================================================
    # IDENTIFICAR JUGADOR
    # =====================================================

    jugador_id_texto = str(
        jugador_id
    )

    jugadores_busqueda = df_jugadores[
        df_jugadores["id"].astype(str)
        ==
        jugador_id_texto
    ]

    if not jugadores_busqueda.empty:

        if "nombre" in jugadores_busqueda.columns:

            nombre_jugador = str(
                jugadores_busqueda.iloc[0]["nombre"]
            )

        elif "name" in jugadores_busqueda.columns:

            nombre_jugador = str(
                jugadores_busqueda.iloc[0]["name"]
            )

        else:

            nombre_jugador = "Jugador"

    else:

        datos_busqueda = datos[
            datos["jugador_id"].astype(str)
            ==
            jugador_id_texto
        ]

        if datos_busqueda.empty:

            st.error(
                "No se ha encontrado el jugador."
            )

            return

        nombre_jugador = str(
            datos_busqueda.iloc[0]["nombre_jugador"]
        )

    # =====================================================
    # NOMBRE DEL JUGADOR
    # =====================================================

    st.subheader(
        nombre_jugador
    )

    # =====================================================
    # OBTENER TEMPORADAS DINÁMICAMENTE
    # =====================================================

    if "temporada" in df_partidas.columns:

        temporadas_ficha = (
            df_partidas["temporada"]
            .dropna()
            .astype(str)
            .str.strip()
            .drop_duplicates()
            .tolist()
        )

    else:

        temporadas_ficha = []

    # =====================================================
    # ORDENAR TEMPORADAS
    # =====================================================

    def ordenar_temporada_ficha(
        temporada
    ):

        try:

            partes = temporada.split()

            for parte in partes:

                if parte.isdigit():

                    return int(parte)

            return 9999

        except Exception:

            return 9999

    temporadas_ficha = sorted(
        temporadas_ficha,
        key=ordenar_temporada_ficha
    )

    # =====================================================
    # SI NO HAY TEMPORADAS
    # =====================================================

    if not temporadas_ficha:

        st.warning(
            "No se han encontrado temporadas "
            "en la tabla de partidas."
        )

        return

    # =====================================================
    # TABS MCR / RIICHI
    # =====================================================

    tab_mcr, tab_riichi = st.tabs(
        [
            "🀄 MCR",
            "🀄 RIICHI"
        ]
    )

    # =====================================================
    # MCR
    # =====================================================

    with tab_mcr:

        tabs_mcr = st.tabs(
            temporadas_ficha
        )

        for temporada, tab_temporada in zip(
            temporadas_ficha,
            tabs_mcr
        ):

            with tab_temporada:

                st.subheader(
                    temporada
                )

                # -----------------------------------------
                # INDICADORES
                # -----------------------------------------

                mostrar_indicadores(
                    jugador_id,
                    "MCR",
                    temporada
                )

                # -----------------------------------------
                # POSICIONES
                # -----------------------------------------

                st.divider()

                mostrar_distribucion_posiciones(
                    jugador_id,
                    "MCR",
                    temporada
                )

                # -----------------------------------------
                # HISTORIAL
                # -----------------------------------------

                st.divider()

                st.subheader(
                    "📋 Historial"
                )

                mostrar_historial(
                    jugador_id,
                    "MCR",
                    temporada
                )

    # =====================================================
    # RIICHI
    # =====================================================

    with tab_riichi:

        tabs_riichi = st.tabs(
            temporadas_ficha
        )

        for temporada, tab_temporada in zip(
            temporadas_ficha,
            tabs_riichi
        ):

            with tab_temporada:

                st.subheader(
                    temporada
                )

                # -----------------------------------------
                # INDICADORES
                # -----------------------------------------

                mostrar_indicadores(
                    jugador_id,
                    "RIICHI",
                    temporada
                )

                # -----------------------------------------
                # POSICIONES
                # -----------------------------------------

                st.divider()

                mostrar_distribucion_posiciones(
                    jugador_id,
                    "RIICHI",
                    temporada
                )

                # -----------------------------------------
                # HISTORIAL
                # -----------------------------------------

                st.divider()

                st.subheader(
                    "📋 Historial"
                )

                mostrar_historial(
                    jugador_id,
                    "RIICHI",
                    temporada
                )

    # =====================================================
    # BOTÓN VOLVER ABAJO
    # =====================================================

    st.divider()

    if st.button(
        "← Volver al ranking",
        key="volver_abajo",
        use_container_width=True
    ):

        st.session_state.jugador_seleccionado = None
        st.rerun()

# =========================================================
# MOSTRAR FICHA SI HAY JUGADOR SELECCIONADO
# =========================================================

if st.session_state.jugador_seleccionado is not None:

    mostrar_ficha(
        st.session_state.jugador_seleccionado
    )

    st.stop()


# =========================================================
# RANKING PRINCIPAL
# =========================================================

st.title(
    "🀄 Liga Mahjong Madrid"
)

# =========================================================
# FUNCIÓN MOSTRAR RANKING
# =========================================================

# =========================================================
# >>> BLOQUE 11 - RANKING PC + MÓVIL <<<
# =========================================================

def mostrar_ranking(
    tipo_juego,
    temporada
):

    # =====================================================
    # CREAR RANKING
    # =====================================================

    ranking = crear_ranking(
        tipo_juego,
        temporada
    )

    if ranking.empty:

        st.info(
            f"No hay datos de {tipo_juego} "
            f"para {temporada}."
        )

        return


    # =====================================================
    # SELECTOR DE ORDENACIÓN
    # =====================================================

    criterio = st.radio(
        "Ordenar ranking por:",
        [
            "📈 Winrate",
            "🏆 Puntos",
            "🎯 Media posición"
        ],
        index=0,
        horizontal=False,
        key=(
            f"criterio_ranking_"
            f"{tipo_juego}_"
            f"{temporada}"
        )
    )


    # =====================================================
    # DEFINIR ORDEN
    # =====================================================

    if criterio == "📈 Winrate":

        columna_orden = "Winrate"
        ascendente = False

    elif criterio == "🏆 Puntos":

        columna_orden = "Puntos"
        ascendente = False

    else:

        columna_orden = "MediaPosicion"
        ascendente = True


    # =====================================================
    # ORDENAR
    # =====================================================

    ranking = ranking.sort_values(
        by=columna_orden,
        ascending=ascendente,
        kind="mergesort"
    ).reset_index(
        drop=True
    )


    # =====================================================
    # ASIGNAR POSICIÓN
    # =====================================================

    ranking["Posición"] = (
        ranking.index + 1
    )


    # =====================================================
    # DETECTAR MÓVIL
    # =====================================================

    user_agent = ""

    try:

        user_agent = (
            st.context.headers
            .get(
                "User-Agent",
                ""
            )
            .lower()
        )

    except Exception:

        user_agent = ""


    es_movil = any(
        palabra in user_agent
        for palabra in [
            "android",
            "iphone",
            "ipad",
            "ipod",
            "mobile"
        ]
    )


    # =====================================================
    # RANKING MÓVIL
    # =====================================================

  # =========================================================
# BLOQUE 11B - RANKING MÓVIL
# =========================================================

if es_movil:

    # -----------------------------------------------------
    # TÍTULO
    # -----------------------------------------------------

    nombre_criterio = (
        criterio
        .replace("📈 ", "")
        .replace("🏆 ", "")
        .replace("🎯 ", "")
    )

    st.subheader(
        f"Ranking por {nombre_criterio}"
    )


    # -----------------------------------------------------
    # CABECERA
    # -----------------------------------------------------

    if columna_orden == "Winrate":

        nombre_columna = "Winrate"

    elif columna_orden == "Puntos":

        nombre_columna = "Puntos"

    else:

        nombre_columna = "Media pos."


    cab1, cab2, cab3 = st.columns(
        [0.6, 2.6, 0.9]
    )

    with cab1:

        st.caption("Pos.")

    with cab2:

        st.caption("Jugador")

    with cab3:

        st.caption(nombre_columna)


    # -----------------------------------------------------
    # FILAS
    # -----------------------------------------------------

    for _, fila in ranking.iterrows():

        posicion = int(
            fila["Posición"]
        )

        jugador_id = fila[
            "jugador_id"
        ]

        nombre = str(
            fila["nombre_jugador"]
        )


        # -------------------------------------------------
        # VALOR QUE SE MUESTRA
        # -------------------------------------------------

        if columna_orden == "Winrate":

            valor = (
                f"{float(fila['Winrate']):.1f}%"
            )

        elif columna_orden == "Puntos":

            valor = str(
                int(fila["Puntos"])
            )

        else:

            valor = (
                f"{float(fila['MediaPosicion']):.2f}"
            )


        # -------------------------------------------------
        # FILA
        # -------------------------------------------------

        col1, col2, col3 = st.columns(
            [0.6, 2.6, 0.9]
        )


        # -------------------------------------------------
        # POSICIÓN
        # -------------------------------------------------

        with col1:

            if posicion == 1:

                st.markdown(
                    "🥇"
                )

            elif posicion == 2:

                st.markdown(
                    "🥈"
                )

            elif posicion == 3:

                st.markdown(
                    "🥉"
                )

            else:

                st.markdown(
                    f"**{posicion}**"
                )


        # -------------------------------------------------
        # JUGADOR
        # -------------------------------------------------

        with col2:

            if st.button(
                nombre,
                key=(
                    f"movil_"
                    f"{tipo_juego}_"
                    f"{temporada}_"
                    f"{jugador_id}"
                ),
                use_container_width=True
            ):

                st.session_state.jugador_seleccionado = (
                    str(jugador_id)
                )

                st.rerun()


        # -------------------------------------------------
        # VALOR
        # -------------------------------------------------

        with col3:

            st.markdown(
                f"**{valor}**"
            )


    # -----------------------------------------------------
    # NO MOSTRAR RANKING DE PC
    # -----------------------------------------------------

    return



    # =====================================================
    # RANKING PC
    # =====================================================

    st.markdown(
        f"**Ranking por {criterio.replace('📈 ', '').replace('🏆 ', '').replace('🎯 ', '')}**"
    )


    # =====================================================
    # ANCHOS
    # =====================================================

    anchos = [
        0.55,
        2.30,
        0.95,
        0.85,
        0.85,
        1.00,
        0.95,
        0.95,
        1.10
    ]


    # =====================================================
    # CABECERA
    # =====================================================

    (
        cab1,
        cab2,
        cab3,
        cab4,
        cab5,
        cab6,
        cab7,
        cab8,
        cab9
    ) = st.columns(
        anchos
    )


    with cab1:

        st.markdown(
            "**Pos.**"
        )


    with cab2:

        st.markdown(
            "**Jugador**"
        )


    with cab3:

        st.markdown(
            "**Puntos**"
        )


    with cab4:

        st.markdown(
            "**Part.**"
        )


    with cab5:

        st.markdown(
            "**Gan.**"
        )


    with cab6:

        st.markdown(
            "**Winrate**"
        )


    with cab7:

        st.markdown(
            "**Media**"
        )


    with cab8:

        st.markdown(
            "**Máx.**"
        )


    with cab9:

        st.markdown(
            "**Media pos.**"
        )


    # =====================================================
    # FILAS PC
    # =====================================================

    for _, fila in ranking.iterrows():

        posicion = int(
            fila["Posición"]
        )

        jugador_id = fila[
            "jugador_id"
        ]

        nombre = str(
            fila["nombre_jugador"]
        )

        puntos = int(
            fila["Puntos"]
        )

        partidas = int(
            fila["Partidas"]
        )

        ganadas = int(
            fila["Ganadas"]
        )

        winrate = float(
            fila["Winrate"]
        )

        media = float(
            fila["Media"]
        )

        puntuacion_maxima = int(
            fila["PuntuacionMaxima"]
        )

        media_posicion = float(
            fila["MediaPosicion"]
        )


        # -------------------------------------------------
        # COLUMNAS
        # -------------------------------------------------

        (
            col1,
            col2,
            col3,
            col4,
            col5,
            col6,
            col7,
            col8,
            col9
        ) = st.columns(
            anchos
        )


        # -------------------------------------------------
        # POSICIÓN
        # -------------------------------------------------

        with col1:

            st.write(
                posicion
            )


        # -------------------------------------------------
        # JUGADOR
        # -------------------------------------------------

        with col2:

            if st.button(
                nombre,
                key=(
                    f"pc_"
                    f"{tipo_juego}_"
                    f"{temporada}_"
                    f"{jugador_id}"
                ),
                use_container_width=True
            ):

                st.session_state.jugador_seleccionado = (
                    str(jugador_id)
                )

                st.rerun()


        # -------------------------------------------------
        # PUNTOS
        # -------------------------------------------------

        with col3:

            st.write(
                puntos
            )


        # -------------------------------------------------
        # PARTIDAS
        # -------------------------------------------------

        with col4:

            st.write(
                partidas
            )


        # -------------------------------------------------
        # GANADAS
        # -------------------------------------------------

        with col5:

            st.write(
                ganadas
            )


        # -------------------------------------------------
        # WINRATE
        # -------------------------------------------------

        with col6:

            st.write(
                f"{winrate:.1f}%"
            )


        # -------------------------------------------------
        # MEDIA
        # -------------------------------------------------

        with col7:

            st.write(
                f"{media:.1f}"
            )


        # -------------------------------------------------
        # PUNTUACIÓN MÁXIMA
        # -------------------------------------------------

        with col8:

            st.write(
                puntuacion_maxima
            )


        # -------------------------------------------------
        # MEDIA POSICIÓN
        # -------------------------------------------------

        with col9:

            st.write(
                f"{media_posicion:.2f}"
            )







# =========================================================
# TEMPORADAS DINÁMICAS
# =========================================================

if "temporada" in df_partidas.columns:

    temporadas = (
        df_partidas["temporada"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )

else:

    temporadas = []


# =========================================================
# ORDENAR TEMPORADAS
# =========================================================

def ordenar_temporada(
    temporada
):

    try:

        partes = temporada.split()

        for parte in partes:

            if parte.isdigit():

                return int(parte)

        return 9999

    except Exception:

        return 9999


temporadas = sorted(
    temporadas,
    key=ordenar_temporada
)


# =========================================================
# COMPROBAR QUE EXISTEN TEMPORADAS
# =========================================================

if not temporadas:

    st.warning(
        "No se han encontrado temporadas "
        "en la tabla de partidas."
    )

    st.stop()


# =========================================================
# TABS PRINCIPALES
# =========================================================

tab_mcr, tab_riichi = st.tabs(
    [
        "🀄 MCR",
        "🀄 RIICHI"
    ]
)


# =========================================================
# MCR
# =========================================================

with tab_mcr:

    tabs_mcr = st.tabs(
        temporadas
    )

    for temporada, tab_temporada in zip(
        temporadas,
        tabs_mcr
    ):

        with tab_temporada:

            st.subheader(
                temporada
            )

            mostrar_ranking(
                "MCR",
                temporada
            )


# =========================================================
# RIICHI
# =========================================================

with tab_riichi:

    tabs_riichi = st.tabs(
        temporadas
    )

    for temporada, tab_temporada in zip(
        temporadas,
        tabs_riichi
    ):

        with tab_temporada:

            st.subheader(
                temporada
            )

            mostrar_ranking(
                "RIICHI",
                temporada
            )


