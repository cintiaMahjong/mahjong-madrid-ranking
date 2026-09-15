import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered"
)

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"


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
# NORMALIZAR
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


if "puntuacion" in df_resultados.columns:
    df_resultados["puntuacion"] = pd.to_numeric(
        df_resultados["puntuacion"],
        errors="coerce"
    ).fillna(0)


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
# NOMBRE
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

    if columna_nombre is not None:
        datos["nombre"] = datos[columna_nombre]
    else:
        datos["nombre"] = datos["jugador_id"].astype(str)


datos["nombre"] = (
    datos["nombre"]
    .fillna("Jugador")
    .astype(str)
    .str.strip()
)


# ============================================================
# CREAR RANKING
# ============================================================

def crear_ranking(tipo_juego, temporada):

    df = datos.copy()

    if "tipo_juego" in df.columns:
        df = df[
            df["tipo_juego"] == tipo_juego
        ]

    if "temporada" in df.columns:
        df = df[
            df["temporada"] == temporada
        ]

    if df.empty:
        return pd.DataFrame()

    df["puntuacion"] = pd.to_numeric(
        df["puntuacion"],
        errors="coerce"
    ).fillna(0)

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
        by="Puntos",
        ascending=False
    ).reset_index(drop=True)

    ranking["Posición"] = ranking.index + 1

    ranking["Puntos"] = (
        ranking["Puntos"]
        .round()
        .astype(int)
    )

    ranking = ranking[
        [
            "Posición",
            "jugador_id",
            "nombre",
            "Puntos",
            "Partidas"
        ]
    ]

    return ranking


# ============================================================
# FUNCIÓN PARA CREAR ENLACE AL JUGADOR
# ============================================================

def enlace_jugador(jugador_id, nombre):

    parametro = urllib.parse.quote(
        str(jugador_id)
    )

    return (
        f'<a href="/jugador?jugador={parametro}" '
        f'target="_blank">{nombre}</a>'
    )


# ============================================================
# FUNCIÓN PARA MOSTRAR MODALIDAD
# ============================================================

def mostrar_modalidad(tipo_juego):

    st.subheader(
        f"Ranking {tipo_juego}"
    )

    temporadas = [
        "Oct 2025 - Sept 2026",
        "Oct 2026 - Sept 2027"
    ]

    if "temporada" in df_partidas.columns:

        temporadas_bd = (
            df_partidas["temporada"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        for temporada in temporadas_bd:

            if temporada and temporada not in temporadas:
                temporadas.append(temporada)

    pestañas_temporadas = st.tabs(
        temporadas
    )

    for i, temporada in enumerate(temporadas):

        with pestañas_temporadas[i]:

            ranking = crear_ranking(
                tipo_juego,
                temporada
            )

            if ranking.empty:

                st.info(
                    f"No hay partidas de {tipo_juego} "
                    f"para {temporada}."
                )

                continue

            # Crear tabla visual con nombres clicables

            tabla = ranking.copy()

            tabla["Jugador"] = tabla.apply(
                lambda fila: enlace_jugador(
                    fila["jugador_id"],
                    fila["nombre"]
                ),
                axis=1
            )

            tabla = tabla[
                [
                    "Posición",
                    "Jugador",
                    "Puntos",
                    "Partidas"
                ]
            ]

            html_tabla = tabla.to_html(
                index=False,
                escape=False
            )

            st.markdown(
                html_tabla,
                unsafe_allow_html=True
            )


# ============================================================
# TÍTULO
# ============================================================

st.title("🀄 Liga Mahjong Madrid")

st.write(
    "Ranking de jugadores"
)


# ============================================================
# MCR / RIICHI
# ============================================================

tab_mcr, tab_riichi = st.tabs(
    [
        "MCR",
        "RIICHI"
    ]
)


# ============================================================
# MCR
# ============================================================

with tab_mcr:

    mostrar_modalidad("MCR")


# ============================================================
# RIICHI
# ============================================================

with tab_riichi:

    mostrar_modalidad("RIICHI")
