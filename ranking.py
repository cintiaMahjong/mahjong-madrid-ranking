import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

RUTA_LOGO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "logo_mahjong_madrid.png"
)

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon=RUTA_LOGO if os.path.exists(RUTA_LOGO) else "🀄",
    layout="centered"
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- CONTENEDOR PRINCIPAL ---------- */

    .block-container {
        max-width: 900px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }


    /* ---------- TÍTULOS ---------- */

    h1 {
        font-size: 2rem !important;
        margin-bottom: 0.3rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

    h3 {
        font-size: 1.2rem !important;
    }


    /* ---------- BOTONES ---------- */

    .stButton > button {
        border-radius: 8px;
        min-height: 38px;
        font-weight: 500;
    }


    /* ---------- MÉTRICAS ---------- */

    [data-testid="stMetric"] {
        padding: 8px 4px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.35rem;
    }


    /* ---------- TABS ---------- */

    button[data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
    }


    /* ---------- MÓVIL ---------- */

    @media (max-width: 600px) {

        .block-container {
            padding-left: 0.65rem;
            padding-right: 0.65rem;
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

        [data-testid="stMetricValue"] {
            font-size: 1.1rem;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.72rem;
        }

        button[data-baseweb="tab"] {
            font-size: 0.9rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = (
    "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"
)


def supabase_get(tabla, params=None):

    key = st.secrets["SUPABASE_KEY"]

    url = f"{SUPABASE_URL}/{tabla}"

    if params:
        url += "?" + urllib.parse.urlencode(
            params,
            doseq=True
        )

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

@st.cache_data(ttl=60)
def cargar_datos():

    jugadores = supabase_get("jugadores")
    partidas = supabase_get("partidas")
    resultados = supabase_get("resultados_partidas")

    df_jugadores = pd.DataFrame(jugadores)
    df_partidas = pd.DataFrame(partidas)
    df_resultados = pd.DataFrame(resultados)

    # --------------------------------------------------------
    # NORMALIZAR JUGADORES
    # --------------------------------------------------------

    if not df_jugadores.empty:

        if "nombre" not in df_jugadores.columns:

            if "name" in df_jugadores.columns:
                df_jugadores["nombre"] = (
                    df_jugadores["name"]
                )

    # --------------------------------------------------------
    # NORMALIZAR PARTIDAS
    # --------------------------------------------------------

    if not df_partidas.empty:

        if "fecha" in df_partidas.columns:

            df_partidas["fecha"] = pd.to_datetime(
                df_partidas["fecha"],
                errors="coerce"
            )

    # --------------------------------------------------------
    # UNIR RESULTADOS + PARTIDAS
    # --------------------------------------------------------

    if not df_resultados.empty and not df_partidas.empty:

        df = df_resultados.merge(
            df_partidas,
            left_on="partida_id",
            right_on="id",
            how="left",
            suffixes=("", "_partida")
        )

    else:

        df = df_resultados.copy()

    # --------------------------------------------------------
    # UNIR NOMBRES DE JUGADORES
    # --------------------------------------------------------

    if (
        not df.empty
        and not df_jugadores.empty
        and "jugador_id" in df.columns
        and "id" in df_jugadores.columns
    ):

        columnas_jugador = ["id"]

        if "nombre" in df_jugadores.columns:
            columnas_jugador.append("nombre")

        df = df.merge(
            df_jugadores[columnas_jugador],
            left_on="jugador_id",
            right_on="id",
            how="left"
        )

        if "nombre" in df.columns:

            df["nombre_jugador"] = (
                df["nombre"]
                .fillna(df["jugador_id"].astype(str))
            )

        else:

            df["nombre_jugador"] = (
                df["jugador_id"].astype(str)
            )

    elif not df.empty:

        df["nombre_jugador"] = (
            df["jugador_id"].astype(str)
        )

    # --------------------------------------------------------
    # LIMPIAR COLUMNAS DUPLICADAS
    # --------------------------------------------------------

    if "id_x" in df.columns and "id" not in df.columns:
        df["id"] = df["id_x"]

    # --------------------------------------------------------
    # PUNTUACIÓN NUMÉRICA
    # --------------------------------------------------------

    if "puntuacion" in df.columns:

        df["puntuacion"] = pd.to_numeric(
            df["puntuacion"],
            errors="coerce"
        ).fillna(0)

    # --------------------------------------------------------
    # POSICIÓN NUMÉRICA
    # --------------------------------------------------------

    if "posicion" in df.columns:

        df["posicion"] = pd.to_numeric(
            df["posicion"],
            errors="coerce"
        )

    return df, df_jugadores, df_partidas


try:

    datos, df_jugadores, df_partidas = cargar_datos()

except Exception as e:

    st.error(
        "No se han podido cargar los datos de Supabase."
    )

    st.exception(e)

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "jugador_seleccionado" not in st.session_state:

    st.session_state.jugador_seleccionado = None


# ============================================================
# CREAR RANKING
# ============================================================

def crear_ranking(tipo_juego, temporada):

    df = datos.copy()

    if df.empty:
        return pd.DataFrame()

    if "tipo_juego" not in df.columns:
        return pd.DataFrame()

    if "temporada" not in df.columns:
        return pd.DataFrame()

    df = df[
        (df["tipo_juego"] == tipo_juego)
        &
        (df["temporada"] == temporada)
    ].copy()

    if df.empty:
        return pd.DataFrame()

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
    # GANADAS
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
    # MEDIA
    # --------------------------------------------------------

    ranking["Media"] = (
        ranking["Puntos"]
        /
        ranking["Partidas"]
    ).round(1)

    # --------------------------------------------------------
    # MEDIA POSICIÓN
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
            ranking["SumaPosiciones"]
            /
            ranking["Partidas"]
        ).round(2)

    else:

        ranking["MediaPosicion"] = 0

    # --------------------------------------------------------
    # ORDENAR
    # --------------------------------------------------------

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
            "nombre_jugador",
            "Puntos",
            "Partidas",
            "Ganadas",
            "Media",
            "MediaPosicion"
        ]
    ]


# ============================================================
# RANKING
# ============================================================

def mostrar_ranking(
    tipo_juego,
    temporada
):

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

    # --------------------------------------------------------
    # CABECERA
    # --------------------------------------------------------

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
        st.markdown("**Pos.**")

    with cab2:
        st.markdown("**Jugador**")

    with cab3:
        st.markdown("**Puntos**")

    with cab4:
        st.markdown("**Partidas**")

    with cab5:
        st.markdown("**Ganadas**")

    with cab6:
        st.markdown("**Media**")

    with cab7:
        st.markdown("**Media pos.**")

    st.divider()

    # --------------------------------------------------------
    # FILAS
    # --------------------------------------------------------

    for _, fila in ranking.iterrows():

        posicion = fila["Posición"]
        nombre = fila["nombre_jugador"]
        jugador_id = fila["jugador_id"]
        puntos = fila["Puntos"]
        partidas = fila["Partidas"]
        ganadas = fila["Ganadas"]
        media = fila["Media"]
        media_posicion = fila["MediaPosicion"]

        (
            col1,
            col2,
            col3,
            col4,
            col5,
            col6,
            col7
        ) = st.columns(
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

            if posicion == 1:
                st.write("🥇")

            elif posicion == 2:
                st.write("🥈")

            elif posicion == 3:
                st.write("🥉")

            else:
                st.write(int(posicion))

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

                st.session_state.jugador_seleccionado = (
                    str(jugador_id)
                )

                st.rerun()

        with col3:
            st.write(int(puntos))

        with col4:
            st.write(int(partidas))

        with col5:
            st.write(int(ganadas))

        with col6:
            st.write(
                f"{float(media):.1f}"
            )

        with col7:
            st.write(
                f"{float(media_posicion):.2f}"
            )


# ============================================================
# INDICADORES DEL JUGADOR
# ============================================================

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
        ==
        jugador_id_texto
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
            f"{float(fila['Media']):.1f}"
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


# ============================================================
# DISTRIBUCIÓN DE POSICIONES
# ============================================================

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

    # Una sola fila por jugador y partida

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

    st.subheader("📊 Posiciones")

    c1, c2, c3, c4, c5 = st.columns(5)

    posiciones = [
        (c1, "🥇 1ª", posicion_1),
        (c2, "🥈 2ª", posicion_2),
        (c3, "🥉 3ª", posicion_3),
        (c4, "4ª", posicion_4),
        (c5, "5ª", posicion_5)
    ]

    for columna, titulo, cantidad in posiciones:

        with columna:

            st.markdown(
                f"""
                <div style="
                    border: 1px solid #dddddd;
                    border-radius: 8px;
                    padding: 8px 2px;
                    text-align: center;
                    margin: 0 2px;
                    background: #fafafa;
                ">

                    <div style="
                        font-size: 13px;
                        font-weight: 600;
                        white-space: nowrap;
                    ">
                        {titulo}
                    </div>

                    <div style="
                        font-size: 21px;
                        font-weight: 700;
                        margin-top: 3px;
                    ">
                        {cantidad}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# HISTORIAL
# ============================================================

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
        return

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------

    if "fecha" in partidas_jugador.columns:

        partidas_jugador = partidas_jugador.sort_values(
            "fecha",
            ascending=False,
            na_position="last"
        )

    else:

        partidas_jugador = (
            partidas_jugador
            .drop_duplicates("partida_id")
        )

    ids_ordenados = (
        partidas_jugador["partida_id"]
        .drop_duplicates()
        .tolist()
    )

    # --------------------------------------------------------
    # CADA PARTIDA
    # --------------------------------------------------------

    for numero_partida, partida_id in enumerate(
        ids_ordenados
    ):

        partida = partidas_jugador[
            partidas_jugador["partida_id"] == partida_id
        ].copy()

        if partida.empty:
            continue

        # Orden por posición

        if "posicion" in partida.columns:

            partida = partida.sort_values(
                "posicion",
                ascending=True,
                na_position="last"
            )

        # ----------------------------------------------------
        # DATOS DE LA PARTIDA
        # ----------------------------------------------------

        fila_partida = partida.iloc[0]

        fecha_texto = ""

        if "fecha" in partida.columns:

            fecha = fila_partida["fecha"]

            if pd.notna(fecha):

                try:

                    fecha_texto = (
                        pd.to_datetime(fecha)
                        .strftime("%d/%m/%Y")
                    )

                except Exception:

                    fecha_texto = str(fecha)

        nombre_partida = ""

        if "nombre_partida" in partida.columns:

            valor = fila_partida["nombre_partida"]

            if pd.notna(valor):

                nombre_partida = str(valor)

        elif "nombre" in partida.columns:

            valor = fila_partida["nombre"]

            if pd.notna(valor):

                nombre_partida = str(valor)

        if fecha_texto and nombre_partida:

            titulo_partida = (
                f"📅 {fecha_texto} · "
                f"{nombre_partida}"
            )

        elif fecha_texto:

            titulo_partida = (
                f"📅 {fecha_texto}"
            )

        elif nombre_partida:

            titulo_partida = nombre_partida

        else:

            titulo_partida = (
                f"Partida {numero_partida + 1}"
            )

        # ----------------------------------------------------
        # CABECERA PARTIDA
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
                font-size: 15px;
            ">
                {titulo_partida}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # CABECERA JUGADORES
        # ----------------------------------------------------

        hc1, hc2, hc3 = st.columns(
            [3, 1.2, 1]
        )

        with hc1:
            st.markdown("**Jugador**")

        with hc2:
            st.markdown("**Puntos**")

        with hc3:
            st.markdown("**Pos.**")

        # ----------------------------------------------------
        # JUGADORES
        # ----------------------------------------------------

        for _, fila in partida.iterrows():

            nombre = fila.get(
                "nombre_jugador",
                fila["jugador_id"]
            )

            puntuacion = fila.get(
                "puntuacion",
                0
            )

            posicion = fila.get(
                "posicion",
                ""
            )

            es_jugador = (
                str(fila["jugador_id"])
                ==
                jugador_id_texto
            )

            if es_jugador:

                fondo = "#eeeeee"
                peso = "600"

            else:

                fondo = "#ffffff"
                peso = "400"

            if pd.notna(puntuacion):

                try:
                    puntos_texto = str(
                        int(float(puntuacion))
                    )

                except Exception:

                    puntos_texto = str(
                        puntuacion
                    )

            else:

                puntos_texto = "-"

            if pd.notna(posicion):

                try:

                    posicion_num = int(
                        float(posicion)
                    )

                    if posicion_num == 1:
                        posicion_texto = "🥇"

                    elif posicion_num == 2:
                        posicion_texto = "🥈"

                    elif posicion_num == 3:
                        posicion_texto = "🥉"

                    else:
                        posicion_texto = str(
                            posicion_num
                        )

                except Exception:

                    posicion_texto = str(
                        posicion
                    )

            else:

                posicion_texto = "-"

            rc1, rc2, rc3 = st.columns(
                [3, 1.2, 1]
            )

            with rc1:

                st.markdown(
                    f"""
                    <div style="
                        background:{fondo};
                        padding:7px 8px;
                        border-radius:6px;
                        font-weight:{peso};
                        margin-bottom:3px;
                        overflow:hidden;
                        text-overflow:ellipsis;
                        white-space:nowrap;
                    ">
                        {nombre}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with rc2:

                st.markdown(
                    f"""
                    <div style="
                        background:{fondo};
                        padding:7px 4px;
                        border-radius:6px;
                        text-align:center;
                        font-weight:{peso};
                        margin-bottom:3px;
                    ">
                        {puntos_texto}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with rc3:

                st.markdown(
                    f"""
                    <div style="
                        background:{fondo};
                        padding:7px 4px;
                        border-radius:6px;
                        text-align:center;
                        font-weight:{peso};
                        margin-bottom:3px;
                    ">
                        {posicion_texto}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Separación entre partidas

        if numero_partida < len(ids_ordenados) - 1:

            st.markdown(
                "<div style='height:8px'></div>",
                unsafe_allow_html=True
            )


# ============================================================
# FICHA DEL JUGADOR
# ============================================================

def mostrar_ficha(jugador_id):

    jugador_id_texto = str(jugador_id)

    # --------------------------------------------------------
    # VOLVER ARRIBA
    # --------------------------------------------------------

    if st.button(
        "← Volver al ranking",
        key="volver_arriba",
        use_container_width=True
    ):

        st.session_state.jugador_seleccionado = None

        st.rerun()

    # --------------------------------------------------------
    # BUSCAR JUGADOR
    # --------------------------------------------------------

    jugadores_busqueda = df_jugadores[
        df_jugadores["id"].astype(str)
        ==
        jugador_id_texto
    ]

    nombre_jugador = None

    if not jugadores_busqueda.empty:

        fila_jugador = (
            jugadores_busqueda.iloc[0]
        )

        if "nombre" in fila_jugador.index:

            nombre_jugador = (
                fila_jugador["nombre"]
            )

    # Fallback desde datos

    if not nombre_jugador:

        datos_nombre = datos[
            datos["jugador_id"].astype(str)
            ==
            jugador_id_texto
        ]

        if not datos_nombre.empty:

            nombre_jugador = (
                datos_nombre.iloc[0]
                .get(
                    "nombre_jugador",
                    jugador_id_texto
                )
            )

    if not nombre_jugador:

        nombre_jugador = jugador_id_texto

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    st.title("🀄 Ficha del jugador")

    st.markdown(
        f"### {nombre_jugador}"
    )

    st.divider()

    # ========================================================
    # MCR / RIICHI
    # ========================================================

    tab_mcr, tab_riichi = st.tabs(
        [
            "🀄 MCR",
            "🀄 RIICHI"
        ]
    )

    temporadas = [
        "Oct 2025 - Sept 2026",
        "Oct 2026 - Sept 2027"
    ]

    # ========================================================
    # MCR
    # ========================================================

    with tab_mcr:

        temporada_mcr = st.tabs(
            [
                "Oct 2025 - Sept 2026",
                "Oct 2026 - Sept 2027"
            ]
        )

        # ----------------------------------------------------
        # MCR TEMPORADA 1
        # ----------------------------------------------------

        with temporada_mcr[0]:

            mostrar_indicadores(
                jugador_id,
                "MCR",
                temporadas[0]
            )

            st.divider()

            mostrar_distribucion_posiciones(
                jugador_id,
                "MCR",
                temporadas[0]
            )

            st.divider()

            st.subheader("📋 Historial")

            mostrar_historial(
                jugador_id,
                "MCR",
                temporadas[0]
            )

        # ----------------------------------------------------
        # MCR TEMPORADA 2
        # ----------------------------------------------------

        with temporada_mcr[1]:

            mostrar_indicadores(
                jugador_id,
                "MCR",
                temporadas[1]
            )

            st.divider()

            mostrar_distribucion_posiciones(
                jugador_id,
                "MCR",
                temporadas[1]
            )

            st.divider()

            st.subheader("📋 Historial")

            mostrar_historial(
                jugador_id,
                "MCR",
                temporadas[1]
            )

    # ========================================================
    # RIICHI
    # ========================================================

    with tab_riichi:

        temporada_riichi = st.tabs(
            [
                "Oct 2025 - Sept 2026",
                "Oct 2026 - Sept 2027"
            ]
        )

        # ----------------------------------------------------
        # RIICHI TEMPORADA 1
        # ----------------------------------------------------

        with temporada_riichi[0]:

            mostrar_indicadores(
                jugador_id,
                "RIICHI",
                temporadas[0]
            )

            st.divider()

            mostrar_distribucion_posiciones(
                jugador_id,
                "RIICHI",
                temporadas[0]
            )

            st.divider()

            st.subheader("📋 Historial")

            mostrar_historial(
                jugador_id,
                "RIICHI",
                temporadas[0]
            )

        # ----------------------------------------------------
        # RIICHI TEMPORADA 2
        # ----------------------------------------------------

        with temporada_riichi[1]:

            mostrar_indicadores(
                jugador_id,
                "RIICHI",
                temporadas[1]
            )

            st.divider()

            mostrar_distribucion_posiciones(
                jugador_id,
                "RIICHI",
                temporadas[1]
            )

            st.divider()

            st.subheader("📋 Historial")

            mostrar_historial(
                jugador_id,
                "RIICHI",
                temporadas[1]
            )

    # --------------------------------------------------------
    # VOLVER ABAJO
    # --------------------------------------------------------

    st.divider()

    if st.button(
        "← Volver al ranking",
        key="volver_abajo",
        use_container_width=True
    ):

        st.session_state.jugador_seleccionado = None

        st.rerun()


# ============================================================
# MOSTRAR FICHA SI HAY JUGADOR SELECCIONADO
# ============================================================

if st.session_state.jugador_seleccionado is not None:

    mostrar_ficha(
        st.session_state.jugador_seleccionado
    )

    st.stop()


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

if os.path.exists(RUTA_LOGO):

    col_logo1, col_logo2, col_logo3 = st.columns(
        [1, 2, 1]
    )

    with col_logo2:

        st.image(
            RUTA_LOGO,
            width=180
        )


st.title("🀄 Liga Mahjong Madrid")

st.caption(
    "Ranking oficial · MCR y RIICHI"
)

st.divider()


# ============================================================
# MCR / RIICHI
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    [
        "🀄 MCR",
        "🀄 RIICHI"
    ]
)


temporadas = [
    "Oct 2025 - Sept 2026",
    "Oct 2026 - Sept 2027"
]


# ============================================================
# MCR
# ============================================================

with tab_mcr:

    temporada_mcr = st.tabs(
        [
            "Oct 2025 - Sept 2026",
            "Oct 2026 - Sept 2027"
        ]
    )

    with temporada_mcr[0]:

        st.subheader(
            "Ranking MCR"
        )

        st.caption(
            "Oct 2025 - Sept 2026"
        )

        mostrar_ranking(
            "MCR",
            temporadas[0]
        )

    with temporada_mcr[1]:

        st.subheader(
            "Ranking MCR"
        )

        st.caption(
            "Oct 2026 - Sept 2027"
        )

        mostrar_ranking(
            "MCR",
            temporadas[1]
        )


# ============================================================
# RIICHI
# ============================================================

with tab_riichi:

    temporada_riichi = st.tabs(
        [
            "Oct 2025 - Sept 2026",
            "Oct 2026 - Sept 2027"
        ]
    )

    with temporada_riichi[0]:

        st.subheader(
            "Ranking RIICHI"
        )

        st.caption(
            "Oct 2025 - Sept 2026"
        )

        mostrar_ranking(
            "RIICHI",
            temporadas[0]
        )

    with temporada_riichi[1]:

        st.subheader(
            "Ranking RIICHI"
        )

        st.caption(
            "Oct 2026 - Sept 2027"
        )

        mostrar_ranking(
            "RIICHI",
            temporadas[1]
        )
