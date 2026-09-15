import streamlit as st
import pandas as pd
import urllib.request
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
    page_icon=RUTA_LOGO,
    layout="centered"
)

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"

TEMPORADAS = [
    "Oct 2025 - Sept 2026",
    "Oct 2026 - Sept 2027"
]

TIPOS_JUEGO = [
    "MCR",
    "RIICHI"
]


# =========================================================
# CONEXIÓN SUPABASE
# =========================================================

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


# =========================================================
# CARGAR DATOS
# =========================================================

try:

    jugadores = supabase_get("jugadores")
    partidas = supabase_get("partidas")
    resultados = supabase_get("resultados_partidas")

except Exception as e:

    st.error(f"Error al conectar con Supabase: {e}")
    st.stop()


df_jugadores = pd.DataFrame(jugadores)
df_partidas = pd.DataFrame(partidas)
df_resultados = pd.DataFrame(resultados)


# =========================================================
# NORMALIZACIÓN
# =========================================================

if "id" in df_jugadores.columns:
    df_jugadores["id"] = df_jugadores["id"].astype(str)

if "jugador_id" in df_resultados.columns:
    df_resultados["jugador_id"] = (
        df_resultados["jugador_id"].astype(str)
    )

if "partida_id" in df_resultados.columns:
    df_resultados["partida_id"] = (
        df_resultados["partida_id"].astype(str)
    )

if "id" in df_partidas.columns:
    df_partidas["id"] = df_partidas["id"].astype(str)


# =========================================================
# PREPARAR NOMBRES
# =========================================================

if "nombre" in df_jugadores.columns:

    df_jugadores["nombre_jugador"] = (
        df_jugadores["nombre"]
    )

elif "name" in df_jugadores.columns:

    df_jugadores["nombre_jugador"] = (
        df_jugadores["name"]
    )

else:

    df_jugadores["nombre_jugador"] = (
        df_jugadores["id"].astype(str)
    )


# =========================================================
# UNIR RESULTADOS + JUGADORES
# =========================================================

datos = df_resultados.merge(
    df_jugadores[
        ["id", "nombre_jugador"]
    ],
    left_on="jugador_id",
    right_on="id",
    how="left"
)


# =========================================================
# UNIR RESULTADOS + PARTIDAS
# =========================================================

columnas_partidas = [
    c for c in [
        "id",
        "fecha",
        "tipo_juego",
        "temporada",
        "nombre_partida",
        "nombre"
    ]
    if c in df_partidas.columns
]

datos = datos.merge(
    df_partidas[columnas_partidas],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)


# =========================================================
# LIMPIAR TIPO DE JUEGO
# =========================================================

if "tipo_juego_partida" in datos.columns:

    datos["tipo_juego"] = datos[
        "tipo_juego"
    ].fillna(
        datos["tipo_juego_partida"]
    )


# =========================================================
# LIMPIAR TEMPORADA
# =========================================================

if "temporada_partida" in datos.columns:

    datos["temporada"] = datos[
        "temporada"
    ].fillna(
        datos["temporada_partida"]
    )


# =========================================================
# CREAR RANKING
# =========================================================

def crear_ranking(tipo_juego, temporada):

    df = datos.copy()

    df = df[
        (df["tipo_juego"] == tipo_juego) &
        (df["temporada"] == temporada)
    ]

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

    # -----------------------------
    # PARTIDAS GANADAS
    # -----------------------------

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

    # -----------------------------
    # MEDIA DE PUNTOS
    # -----------------------------

    ranking["Media"] = (
        ranking["Puntos"] /
        ranking["Partidas"]
    ).round(1)

    # -----------------------------
    # MEDIA DE POSICIÓN
    # -----------------------------

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

    # -----------------------------
    # ORDENAR
    # -----------------------------

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


# =========================================================
# INDICADORES DEL JUGADOR
# =========================================================

def mostrar_indicadores(
    jugador_id,
    tipo_juego,
    temporada
):

    jugador_id_texto = str(jugador_id)

    df = datos[
        (datos["jugador_id"].astype(str) == jugador_id_texto) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()

    if df.empty:

        st.info(
            f"No hay datos de {tipo_juego} "
            f"para esta temporada."
        )

        return

    partidas_jugadas = df[
        "partida_id"
    ].nunique()

    puntos = df[
        "puntuacion"
    ].sum()

    if "posicion" in df.columns:

        victorias = df[
            df["posicion"] == 1
        ]["partida_id"].nunique()

        media_posicion = (
            df["posicion"].sum()
            / partidas_jugadas
        )

    else:

        victorias = 0
        media_posicion = 0

    media = (
        puntos / partidas_jugadas
    )

    # =====================================================
    # INDICADORES
    # =====================================================

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Partidas",
            partidas_jugadas
        )

    with c2:
        st.metric(
            "Puntos",
            int(round(puntos))
        )

    with c3:
        st.metric(
            "Ganadas",
            victorias
        )

    with c4:
        st.metric(
            "Media",
            f"{media:.1f}"
        )

    with c5:
        st.metric(
            "Media pos.",
            f"{media_posicion:.2f}"
        )


# =========================================================
# TABLA DE POSICIONES
# =========================================================

def mostrar_distribucion_posiciones(
    jugador_id,
    tipo_juego,
    temporada
):

    jugador_id_texto = str(jugador_id)

    df = datos[
        (datos["jugador_id"].astype(str) == jugador_id_texto) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()

    if df.empty or "posicion" not in df.columns:
        return

    # Aseguramos que posición sea numérica
    df["posicion"] = pd.to_numeric(
        df["posicion"],
        errors="coerce"
    )

    # Contamos las posiciones 1 a 5
    conteo = {}

    for posicion in range(1, 6):

        conteo[posicion] = int(
            (
                df["posicion"] == posicion
            ).sum()
        )

    st.markdown(
        "### Distribución de posiciones"
    )

    # Una columna por posición
    c1, c2, c3, c4, c5 = st.columns(5)

    columnas = [
        (c1, "🥇 1ª", conteo[1]),
        (c2, "🥈 2ª", conteo[2]),
        (c3, "🥉 3ª", conteo[3]),
        (c4, "4ª", conteo[4]),
        (c5, "5ª", conteo[5])
    ]

    for columna, posicion, cantidad in columnas:

        with columna:

            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    border: 1px solid #dddddd;
                    border-radius: 8px;
                    padding: 8px 4px;
                    margin-bottom: 10px;
                ">
                    <div style="
                        font-size: 14px;
                        font-weight: 600;
                    ">
                        {posicion}
                    </div>

                    <div style="
                        font-size: 20px;
                        font-weight: 700;
                        margin-top: 3px;
                    ">
                        {cantidad}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
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
        (datos["jugador_id"].astype(str) == jugador_id_texto) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()

    if datos_jugador.empty:

        st.info(
            f"Este jugador no tiene partidas de "
            f"{tipo_juego} en esta temporada."
        )

        return

    # =====================================================
    # PARTIDAS DEL JUGADOR
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
        (partidas_jugador["tipo_juego"] == tipo_juego) &
        (partidas_jugador["temporada"] == temporada)
    ].copy()

    # =====================================================
    # FECHA
    # =====================================================

    if "fecha" in partidas_jugador.columns:

        partidas_jugador["_fecha"] = pd.to_datetime(
            partidas_jugador["fecha"],
            errors="coerce"
        )

    else:

        partidas_jugador["_fecha"] = pd.NaT

    # =====================================================
    # ORDENAR PARTIDAS
    # =====================================================

    lista_partidas = (
        partidas_jugador[
            [
                "partida_id",
                "_fecha"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "_fecha",
            ascending=False,
            na_position="last"
        )
    )

    # =====================================================
    # MOSTRAR CADA PARTIDA
    # =====================================================

    for _, partida in lista_partidas.iterrows():

        partida_id = partida["partida_id"]
        fecha = partida["_fecha"]

        # -----------------------------
        # FECHA
        # -----------------------------

        if pd.notna(fecha):

            fecha_texto = fecha.strftime(
                "%d/%m/%Y"
            )

        else:

            fecha_texto = ""

        # -----------------------------
        # NOMBRE DE LA PARTIDA
        # -----------------------------

        nombre_partida = ""

        if (
            "nombre_partida" in partidas_jugador.columns
        ):

            valores = partidas_jugador[
                partidas_jugador["partida_id"] == partida_id
            ]["nombre_partida"].dropna()

            if not valores.empty:
                nombre_partida = str(
                    valores.iloc[0]
                )

        if not nombre_partida:

            if "nombre" in partidas_jugador.columns:

                valores = partidas_jugador[
                    partidas_jugador["partida_id"] == partida_id
                ]["nombre"].dropna()

                if not valores.empty:
                    nombre_partida = str(
                        valores.iloc[0]
                    )

        # -----------------------------
        # TÍTULO
        # -----------------------------

        if fecha_texto and nombre_partida:

            titulo_partida = (
                f"{fecha_texto} · {nombre_partida}"
            )

        elif nombre_partida:

            titulo_partida = nombre_partida

        else:

            titulo_partida = fecha_texto

        # =================================================
        # CABECERA DE PARTIDA
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
        # DATOS DE LA PARTIDA
        # =================================================

        partido = partidas_jugador[
            partidas_jugador["partida_id"] == partida_id
        ].copy()

        if "posicion" in partido.columns:

            partido["posicion"] = pd.to_numeric(
                partido["posicion"],
                errors="coerce"
            )

            partido = partido.sort_values(
                "posicion",
                ascending=True,
                na_position="last"
            )

        # =================================================
        # CABECERAS
        # =================================================

        c1, c2, c3 = st.columns(
            [3, 1.2, 1.2]
        )

        with c1:
            st.markdown(
                "**Jugador**"
            )

        with c2:
            st.markdown(
                "**Puntos**"
            )

        with c3:
            st.markdown(
                "**Pos.**"
            )

        # =================================================
        # JUGADORES
        # =================================================

        for _, fila in partido.iterrows():

            jugador_fila = str(
                fila["jugador_id"]
            )

            nombre = fila.get(
                "nombre_jugador",
                ""
            )

            puntos = fila.get(
                "puntuacion",
                ""
            )

            posicion = fila.get(
                "posicion",
                ""
            )

            # Comprobar si es el jugador de la ficha
            es_jugador = (
                jugador_fila == jugador_id_texto
            )

            if es_jugador:

                fondo = "#eeeeee"
                peso = "600"

            else:

                fondo = "#ffffff"
                peso = "400"

            # ---------------------------------------------
            # NOMBRE
            # ---------------------------------------------

            c1, c2, c3 = st.columns(
                [3, 1.2, 1.2]
            )

            with c1:

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 6px 8px;
                        border-radius: 5px;
                        font-weight: {peso};
                    ">
                        {nombre}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ---------------------------------------------
            # PUNTOS
            # ---------------------------------------------

            with c2:

                try:
                    puntos_texto = str(
                        int(round(float(puntos)))
                    )
                except:
                    puntos_texto = str(puntos)

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 6px 8px;
                        border-radius: 5px;
                        font-weight: {peso};
                    ">
                        {puntos_texto}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ---------------------------------------------
            # POSICIÓN
            # ---------------------------------------------

            with c3:

                try:
                    posicion_texto = str(
                        int(posicion)
                    )
                except:
                    posicion_texto = str(posicion)

                st.markdown(
                    f"""
                    <div style="
                        background-color: {fondo};
                        padding: 6px 8px;
                        border-radius: 5px;
                        font-weight: {peso};
                    ">
                        {posicion_texto}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Separación entre partidas
        st.markdown(
            "<div style='height: 4px;'></div>",
            unsafe_allow_html=True
        )


# =========================================================
# FICHA DEL JUGADOR
# =========================================================

def mostrar_ficha(jugador_id):

    jugador_id_texto = str(jugador_id)

    # =====================================================
    # BUSCAR JUGADOR
    # =====================================================

    jugadores_busqueda = df_jugadores[
        df_jugadores["id"].astype(str)
        == jugador_id_texto
    ]

    if not jugadores_busqueda.empty:

        nombre_jugador = str(
            jugadores_busqueda.iloc[0][
                "nombre_jugador"
            ]
        )

    else:

        datos_jugador_busqueda = datos[
            datos["jugador_id"].astype(str)
            == jugador_id_texto
        ]

        if not datos_jugador_busqueda.empty:

            nombre_jugador = str(
                datos_jugador_busqueda.iloc[0][
                    "nombre_jugador"
                ]
            )

        else:

            st.error(
                "No se encuentra el jugador."
            )

            return

    # =====================================================
    # CABECERA
    # =====================================================

    st.title("🀄 Ficha del jugador")

    st.subheader(nombre_jugador)

    st.divider()

    # =====================================================
    # MCR / RIICHI
    # =====================================================

    pestaña_mcr, pestaña_riichi = st.tabs(
        [
            "MCR",
            "RIICHI"
        ]
    )

    # =====================================================
    # MCR
    # =====================================================

    with pestaña_mcr:

        temporadas_mcr = st.tabs(
            TEMPORADAS
        )

        for i, temporada in enumerate(
            TEMPORADAS
        ):

            with temporadas_mcr[i]:

                mostrar_indicadores(
                    jugador_id,
                    "MCR",
                    temporada
                )

                st.divider()

                st.subheader(
                    "📋 Historial de partidas"
                )

                mostrar_historial(
                    jugador_id,
                    "MCR",
                    temporada
                )

                # -----------------------------------------
                # DISTRIBUCIÓN DE POSICIONES
                # -----------------------------------------

                st.divider()

                mostrar_distribucion_posiciones(
                    jugador_id,
                    "MCR",
                    temporada
                )

    # =====================================================
    # RIICHI
    # =====================================================

    with pestaña_riichi:

        temporadas_riichi = st.tabs(
            TEMPORADAS
        )

        for i, temporada in enumerate(
            TEMPORADAS
        ):

            with temporadas_riichi[i]:

                mostrar_indicadores(
                    jugador_id,
                    "RIICHI",
                    temporada
                )

                st.divider()

                st.subheader(
                    "📋 Historial de partidas"
                )

                mostrar_historial(
                    jugador_id,
                    "RIICHI",
                    temporada
                )

                # -----------------------------------------
                # DISTRIBUCIÓN DE POSICIONES
                # -----------------------------------------

                st.divider()

                mostrar_distribucion_posiciones(
                    jugador_id,
                    "RIICHI",
                    temporada
                )

    # =====================================================
    # VOLVER
    # =====================================================

    st.divider()

    if st.button(
        "← Volver al ranking"
    ):

        st.session_state.jugador_seleccionado = None
        st.rerun()


# =========================================================
# SESSION STATE
# =========================================================

if "jugador_seleccionado" not in st.session_state:

    st.session_state.jugador_seleccionado = None


# =========================================================
# SI HAY JUGADOR SELECCIONADO
# =========================================================

if (
    st.session_state.jugador_seleccionado
    is not None
):

    mostrar_ficha(
        st.session_state.jugador_seleccionado
    )

    st.stop()


# =========================================================
# TÍTULO PRINCIPAL
# =========================================================

if os.path.exists(RUTA_LOGO):

    st.image(
        RUTA_LOGO,
        width=180
    )

st.title(
    "Liga Mahjong Madrid"
)

st.divider()


# =========================================================
# TIPO DE JUEGO
# =========================================================

pestaña_mcr, pestaña_riichi = st.tabs(
    [
        "MCR",
        "RIICHI"
    ]
)


# =========================================================
# FUNCIÓN PARA MOSTRAR RANKING
# =========================================================

def mostrar_ranking(
    tipo_juego
):

    temporadas = st.tabs(
        TEMPORADAS
    )

    for i, temporada in enumerate(
        TEMPORADAS
    ):

        with temporadas[i]:

            ranking = crear_ranking(
                tipo_juego,
                temporada
            )

            if ranking.empty:

                st.info(
                    "No hay partidas registradas "
                    "para esta temporada."
                )

                continue

            # ---------------------------------------------
            # CABECERAS
            # ---------------------------------------------

            (
                cab1,
                cab2,
                cab3,
                cab4,
                cab5,
                cab6,
                cab7
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
                    "**Partidas**"
                )

            with cab5:
                st.markdown(
                    "**Ganadas**"
                )

            with cab6:
                st.markdown(
                    "**Media**"
                )

            with cab7:
                st.markdown(
                    "**Media pos.**"
                )

            # ---------------------------------------------
            # FILAS
            # ---------------------------------------------

            for _, fila in ranking.iterrows():

                (
                    c1,
                    c2,
                    c3,
                    c4,
                    c5,
                    c6,
                    c7
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

                with c1:

                    st.write(
                        int(fila["Posición"])
                    )

                with c2:

                    if st.button(
                        str(
                            fila["nombre_jugador"]
                        ),
                        key=(
                            f"jugador_"
                            f"{tipo_juego}_"
                            f"{temporada}_"
                            f"{fila['jugador_id']}"
                        )
                    ):

                        st.session_state.jugador_seleccionado = (
                            str(fila["jugador_id"])
                        )

                        st.rerun()

                with c3:

                    st.write(
                        int(fila["Puntos"])
                    )

                with c4:

                    st.write(
                        int(fila["Partidas"])
                    )

                with c5:

                    st.write(
                        int(fila["Ganadas"])
                    )

                with c6:

                    st.write(
                        f"{fila['Media']:.1f}"
                    )

                with c7:

                    st.write(
                        f"{fila['MediaPosicion']:.2f}"
                    )


# =========================================================
# RANKING MCR
# =========================================================

with pestaña_mcr:

    mostrar_ranking(
        "MCR"
    )


# =========================================================
# RANKING RIICHI
# =========================================================

with pestaña_riichi:

    mostrar_ranking(
        "RIICHI"
    )
