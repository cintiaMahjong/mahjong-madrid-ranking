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
# COMPROBAR COLUMNAS
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
# NORMALIZAR DATOS
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
    columna_nombre = "nombre"
elif "name" in df_jugadores.columns:
    columna_nombre = "name"
else:
    columna_nombre = None


# ============================================================
# CREAR DATOS COMPLETOS
# ============================================================

datos = df_resultados.copy()

datos = datos.merge(
    df_jugadores,
    left_on="jugador_id",
    right_on="id",
    how="left",
    suffixes=("", "_jugador")
)

datos = datos.merge(
    df_partidas[
        ["id", "fecha", "tipo_juego", "temporada"]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)


# ============================================================
# CREAR COLUMNA NOMBRE
# ============================================================

if columna_nombre is not None:

    if columna_nombre in datos.columns:
        datos["nombre_jugador"] = datos[columna_nombre]

    elif f"{columna_nombre}_jugador" in datos.columns:
        datos["nombre_jugador"] = datos[
            f"{columna_nombre}_jugador"
        ]

    else:
        datos["nombre_jugador"] = datos["jugador_id"].astype(str)

else:
    datos["nombre_jugador"] = datos["jugador_id"].astype(str)


datos["nombre_jugador"] = (
    datos["nombre_jugador"]
    .fillna(datos["jugador_id"].astype(str))
    .astype(str)
)


# ============================================================
# FUNCIÓN RANKING
# ============================================================

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
            ["jugador_id", "nombre_jugador"],
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
            "Partidas"
        ]
    ]


# ============================================================
# FUNCIÓN FICHA DEL JUGADOR
# ============================================================

def mostrar_ficha(jugador_id):

    # --------------------------------------------------------
    # Convertimos ambos IDs a texto para evitar problemas
    # de tipo UUID / int / str
    # --------------------------------------------------------

    jugador_id_texto = str(jugador_id)

    jugadores_busqueda = df_jugadores[
        df_jugadores["id"].astype(str) == jugador_id_texto
    ]

    # --------------------------------------------------------
    # Si no lo encuentra en jugadores, intentamos buscarlo
    # directamente en los datos completos
    # --------------------------------------------------------

    if jugadores_busqueda.empty:

        datos_jugador = datos[
            datos["jugador_id"].astype(str) == jugador_id_texto
        ]

        if datos_jugador.empty:
            st.error(
                f"No se encuentra el jugador con ID: {jugador_id_texto}"
            )
            return

        nombre = datos_jugador.iloc[0]["nombre_jugador"]

    else:

        jugador = jugadores_busqueda.iloc[0]

        if columna_nombre is not None:
            nombre = jugador[columna_nombre]
        else:
            nombre = jugador_id_texto

    # --------------------------------------------------------
    # CABECERA
    # --------------------------------------------------------

    if st.button("← Volver al ranking"):
        st.session_state.jugador_seleccionado = None
        st.rerun()

    st.title("🀄 Ficha del jugador")

    st.header(str(nombre))

    st.write("")

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

            total_puntos = df_mcr["puntuacion"].sum()
            numero_partidas = df_mcr["partida_id"].nunique()

            media = (
                total_puntos / numero_partidas
                if numero_partidas > 0
                else 0
            )

            ranking_mcr = crear_ranking(
                "MCR",
                temporada
            )

            fila_ranking = ranking_mcr[
                ranking_mcr["jugador_id"].astype(str)
                == jugador_id_texto
            ]

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

                st.write(
                    f"**Posición en el ranking: {posicion}º**"
                )

            st.write("### Historial")

            historial = df_mcr[
                [
                    "fecha",
                    "puntuacion"
                ]
            ].copy()

            if "posicion" in df_mcr.columns:
                historial["Posición"] = df_mcr[
                    "posicion"
                ]

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

            total_puntos = df_riichi["puntuacion"].sum()
            numero_partidas = df_riichi["partida_id"].nunique()

            media = (
                total_puntos / numero_partidas
                if numero_partidas > 0
                else 0
            )

            ranking_riichi = crear_ranking(
                "RIICHI",
                temporada
            )

            fila_ranking = ranking_riichi[
                ranking_riichi["jugador_id"].astype(str)
                == jugador_id_texto
            ]

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

                st.write(
                    f"**Posición en el ranking: {posicion}º**"
                )

            st.write("### Historial")

            historial = df_riichi[
                [
                    "fecha",
                    "puntuacion"
                ]
            ].copy()

            if "posicion" in df_riichi.columns:
                historial["Posición"] = df_riichi[
                    "posicion"
                ]

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
# SI HAY JUGADOR SELECCIONADO → MOSTRAR FICHA
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

st.write("")

tabs_juego = st.tabs(
    ["MCR", "RIICHI"]
)


# ============================================================
# MCR
# ============================================================

with tabs_juego[0]:

    tabs_temporadas = st.tabs(TEMPORADAS)

    for i, temporada in enumerate(TEMPORADAS):

        with tabs_temporadas[i]:

            ranking = crear_ranking(
                "MCR",
                temporada
            )

            if ranking.empty:

                st.info(
                    "No hay partidas MCR en esta temporada."
                )

            else:

                st.subheader(
                    f"Ranking MCR — {temporada}"
                )

                for _, fila in ranking.iterrows():

                    jugador_id = fila["jugador_id"]
                    nombre = fila["nombre_jugador"]
                    posicion = fila["Posición"]
                    puntos = fila["Puntos"]
                    partidas = fila["Partidas"]

                    col1, col2, col3, col4 = st.columns(
                        [0.5, 3, 1.2, 1.2]
                    )

                    with col1:
                        st.write(
                            f"**{posicion}**"
                        )

                    with col2:

                        if st.button(
                            str(nombre),
                            key=f"MCR_{temporada}_{str(jugador_id)}",
                            use_container_width=True
                        ):

                            # IMPORTANTE:
                            # Guardamos el ID como texto
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
                            f"{partidas} partidas"
                        )


# ============================================================
# RIICHI
# ============================================================

with tabs_juego[1]:

    tabs_temporadas = st.tabs(TEMPORADAS)

    for i, temporada in enumerate(TEMPORADAS):

        with tabs_temporadas[i]:

            ranking = crear_ranking(
                "RIICHI",
                temporada
            )

            if ranking.empty:

                st.info(
                    "No hay partidas RIICHI en esta temporada."
                )

            else:

                st.subheader(
                    f"Ranking RIICHI — {temporada}"
                )

                for _, fila in ranking.iterrows():

                    jugador_id = fila["jugador_id"]
                    nombre = fila["nombre_jugador"]
                    posicion = fila["Posición"]
                    puntos = fila["Puntos"]
                    partidas = fila["Partidas"]

                    col1, col2, col3, col4 = st.columns(
                        [0.5, 3, 1.2, 1.2]
                    )

                    with col1:
                        st.write(
                            f"**{posicion}**"
                        )

                    with col2:

                        if st.button(
                            str(nombre),
                            key=f"RIICHI_{temporada}_{str(jugador_id)}",
                            use_container_width=True
                        ):

                            # IMPORTANTE:
                            # Guardamos el ID como texto
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
                            f"{partidas} partidas"
                        )
