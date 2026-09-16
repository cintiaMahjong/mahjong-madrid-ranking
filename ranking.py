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
# =========================================================

datos = df_resultados.copy()


# ---------------------------------------------------------
# AÑADIR INFORMACIÓN DE LAS PARTIDAS
# ---------------------------------------------------------

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
        df_partidas[columnas_partidas]
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


# ---------------------------------------------------------
# AÑADIR NOMBRE DEL JUGADOR
# ---------------------------------------------------------

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
        df_jugadores[columnas_jugadores]
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


if "posicion" in datos.columns:

    datos["posicion"] = pd.to_numeric(
        datos["posicion"],
        errors="coerce"
    )


if "tipo_juego" not in datos.columns:

    datos["tipo_juego"] = ""


if "temporada" not in datos.columns:

    datos["temporada"] = ""


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

def crear_ranking(tipo_juego, temporada):

    df = datos.copy()

    # -----------------------------------------------------
    # FILTRAR JUEGO Y TEMPORADA
    # -----------------------------------------------------

    df = df[
        (df["tipo_juego"] == tipo_juego)
        &
        (df["temporada"] == temporada)
    ].copy()

    if df.empty:
        return pd.DataFrame()

    # -----------------------------------------------------
    # UNA SOLA FILA POR JUGADOR Y PARTIDA
    # -----------------------------------------------------

    df = df.drop_duplicates(
        subset=[
            "partida_id",
            "jugador_id"
        ]
    ).copy()

    # -----------------------------------------------------
    # NORMALIZAR PUNTUACIÓN
    # -----------------------------------------------------

    df["puntuacion"] = pd.to_numeric(
        df["puntuacion"],
        errors="coerce"
    ).fillna(0)

    # -----------------------------------------------------
    # NORMALIZAR POSICIÓN
    # -----------------------------------------------------

    if "posicion" in df.columns:

        df["posicion"] = pd.to_numeric(
            df["posicion"],
            errors="coerce"
        )

    # -----------------------------------------------------
    # ESTADÍSTICAS PRINCIPALES
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PARTIDAS GANADAS
    # -----------------------------------------------------

    if "posicion" in df.columns:

        ganadas = (
            df[df["posicion"] == 1]
            .groupby("jugador_id")["partida_id"]
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

    # -----------------------------------------------------
    # WINRATE
    # -----------------------------------------------------

    ranking["Winrate"] = (
        ranking["Ganadas"]
        / ranking["Partidas"]
        * 100
    ).fillna(0)

    # -----------------------------------------------------
    # MEDIA DE POSICIÓN
    # -----------------------------------------------------

    if "posicion" in df.columns:

        posiciones = (
            df.groupby("jugador_id")["posicion"]
            .mean()
            .reset_index(
                name="MediaPosicion"
            )
        )

        ranking = ranking.merge(
            posiciones,
            on="jugador_id",
            how="left"
        )

    else:

        ranking["MediaPosicion"] = 0

    # -----------------------------------------------------
    # REDONDEAR
    # -----------------------------------------------------

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

    ranking["Winrate"] = (
        ranking["Winrate"]
        .round(1)
    )

    ranking["MediaPosicion"] = (
        ranking["MediaPosicion"]
        .fillna(0)
        .round(2)
    )

    # -----------------------------------------------------
    # ORDEN DEL RANKING
    # -----------------------------------------------------

    ranking = ranking.sort_values(
        by=[
            "Puntos",
            "Media"
        ],
        ascending=[
            False,
            False
        ]
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # POSICIÓN
    # -----------------------------------------------------

    ranking["Posición"] = (
        ranking.index + 1
    )

    # -----------------------------------------------------
    # COLUMNAS FINALES
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PRIMERA FILA
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # SEGUNDA FILA
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # TERCERA FILA
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # UNA FILA POR PARTIDA
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CONTAR POSICIONES
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # TÍTULO
    # -----------------------------------------------------

    st.subheader("📊 Posiciones")

    # -----------------------------------------------------
    # TABLA
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # OBTENER PARTIDAS DEL JUGADOR
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # INFORMACIÓN DE LAS PARTIDAS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # MOSTRAR CADA PARTIDA
    # -----------------------------------------------------

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

        # -------------------------------------------------
        # FECHA
        # -------------------------------------------------

        fecha = partida["fecha"]

        try:

            fecha_formateada = pd.to_datetime(
                fecha
            ).strftime("%d/%m/%Y")

        except Exception:

            fecha_formateada = str(fecha)

        # -------------------------------------------------
        # NOMBRE DE LA PARTIDA
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CABECERA DE PARTIDA
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CABECERA DE JUGADORES
        # -------------------------------------------------

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

        # -------------------------------------------------
        # JUGADORES
        # -------------------------------------------------

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

            try:

                puntuacion = int(
                    round(
                        float(puntuacion)
                    )
                )

            except Exception:

                puntuacion = 0

            try:

                posicion = int(
                    float(posicion)
                )

            except Exception:

                posicion = ""

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
    # CABECERA
    # =====================================================

    cabecera_titulo, cabecera_boton = st.columns(
        [3, 1]
    )

    with cabecera_titulo:

        st.title("🀄 Ficha del jugador")

    with cabecera_boton:

        if st.button(
            "← Volver",
            key="volver_arriba"
        ):

            st.session_state.jugador_seleccionado = None
            st.rerun()

    # =====================================================
    # IDENTIFICAR JUGADOR
    # =====================================================

    jugador_id_texto = str(jugador_id)

    jugadores_busqueda = df_jugadores[
        df_jugadores["id"].astype(str)
        == jugador_id_texto
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
            == jugador_id_texto
        ]

        if datos_busqueda.empty:

            st.error(
                "No se ha encontrado el jugador."
            )

            return

        nombre_jugador = str(
            datos_busqueda.iloc[0]["nombre_jugador"]
        )

    st.subheader(nombre_jugador)

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
    # TEMPORADAS DINÁMICAS
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

        def ordenar_temporada_ficha(temporada):

            try:

                return int(
                    temporada.split()[1]
                )

            except Exception:

                return 9999

        temporadas_ficha = sorted(
            temporadas_ficha,
            key=ordenar_temporada_ficha
        )

    else:

        temporadas_ficha = []

    # =====================================================
    # SI NO HAY TEMPORADAS
    # =====================================================

    if not temporadas_ficha:

        st.warning(
            "No se han encontrado temporadas "
            "en la tabla de partidas."
        )

        return


