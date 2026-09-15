import html
import json
import urllib.request
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   BASE
   ============================================================ */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: #071c14 !important;
}

[data-testid="stAppViewContainer"] {
    min-width: 0 !important;
}

.main {
    background: #071c14 !important;
}

.block-container {
    width: 100% !important;
    max-width: 560px !important;
    padding: 1rem 0.75rem 2rem !important;
    margin: 0 auto !important;
}

#MainMenu,
footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* ============================================================
   TEXTO
   ============================================================ */

body,
p,
label,
span,
div {
    font-family: Arial, Helvetica, sans-serif;
}

body,
p,
label,
span {
    color: #f4e8c6;
}


/* ============================================================
   CABECERA
   ============================================================ */

.cabecera {
    text-align: center;
    margin: 0 auto 22px;
}

.logo-contenedor {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
}

.titulo {
    color: #f6e9c7 !important;
    font-size: clamp(1.35rem, 6vw, 1.75rem);
    font-weight: 900;
    letter-spacing: 1.2px;
    line-height: 1.1;
    margin: 0;
}

.subtitulo {
    color: #bd9140 !important;
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 3px;
    margin-top: 7px;
}


/* ============================================================
   SELECTOR MCR / RIICHI
   ============================================================ */

.selector-juego {
    margin: 0 0 24px;
}

/* Separación */
.selector-juego + div [data-testid="stHorizontalBlock"] {
    gap: 9px !important;
}

/*
   LOS DOS BOTONES
   ------------------------------------------------------------
   El marcador está dentro de la propia columna.
   Así CSS puede localizar directamente el botón correcto.
*/

.mcr-marker,
.mcr-active-marker,
.riichi-marker,
.riichi-active-marker {
    display: none !important;
}


/* ============================================================
   MCR NO SELECCIONADO
   VERDE OSCURO + BORDE AMARILLO
   ============================================================ */

[data-testid="column"]:has(.mcr-marker)
    [data-testid="stButton"] > button {

    background: #102b20 !important;
    background-color: #102b20 !important;
    background-image: none !important;

    border: 2px solid #c5a84d !important;
    border-radius: 12px !important;

    color: #cdbf94 !important;

    box-shadow: none !important;
    opacity: 1 !important;
}


/* Texto MCR apagado */

[data-testid="column"]:has(.mcr-marker)
    [data-testid="stButton"] > button p,

[data-testid="column"]:has(.mcr-marker)
    [data-testid="stButton"] > button span,

[data-testid="column"]:has(.mcr-marker)
    [data-testid="stButton"] > button div {

    color: #cdbf94 !important;
}


/* ============================================================
   MCR SELECCIONADO
   VERDE LUMINOSO + BORDE AMARILLO
   ============================================================ */

[data-testid="column"]:has(.mcr-active-marker)
    [data-testid="stButton"] > button {

    background: #286b49 !important;
    background-color: #286b49 !important;
    background-image: none !important;

    border: 2px solid #f0c84b !important;
    border-radius: 12px !important;

    color: #fff1bd !important;

    box-shadow:
        0 0 0 1px rgba(240, 200, 75, 0.20),
        0 4px 16px rgba(240, 200, 75, 0.20),
        inset 0 1px 0 rgba(255,255,255,0.10) !important;

    opacity: 1 !important;
}


/* Texto MCR activo */

[data-testid="column"]:has(.mcr-active-marker)
    [data-testid="stButton"] > button p,

[data-testid="column"]:has(.mcr-active-marker)
    [data-testid="stButton"] > button span,

[data-testid="column"]:has(.mcr-active-marker)
    [data-testid="stButton"] > button div {

    color: #fff1bd !important;
    font-weight: 900 !important;
}


/* ============================================================
   RIICHI NO SELECCIONADO
   VERDE OSCURO + BORDE AMARILLO
   ============================================================ */

[data-testid="column"]:has(.riichi-marker)
    [data-testid="stButton"] > button {

    background: #102b20 !important;
    background-color: #102b20 !important;
    background-image: none !important;

    border: 2px solid #c5a84d !important;
    border-radius: 12px !important;

    color: #cdbf94 !important;

    box-shadow: none !important;
    opacity: 1 !important;
}


/* Texto RIICHI apagado */

[data-testid="column"]:has(.riichi-marker)
    [data-testid="stButton"] > button p,

[data-testid="column"]:has(.riichi-marker)
    [data-testid="stButton"] > button span,

[data-testid="column"]:has(.riichi-marker)
    [data-testid="stButton"] > button div {

    color: #cdbf94 !important;
}


/* ============================================================
   RIICHI SELECCIONADO
   VERDE LUMINOSO + BORDE AMARILLO
   ============================================================ */

[data-testid="column"]:has(.riichi-active-marker)
    [data-testid="stButton"] > button {

    background: #286b49 !important;
    background-color: #286b49 !important;
    background-image: none !important;

    border: 2px solid #f0c84b !important;
    border-radius: 12px !important;

    color: #fff1bd !important;

    box-shadow:
        0 0 0 1px rgba(240, 200, 75, 0.20),
        0 4px 16px rgba(240, 200, 75, 0.20),
        inset 0 1px 0 rgba(255,255,255,0.10) !important;

    opacity: 1 !important;
}


/* Texto RIICHI activo */

[data-testid="column"]:has(.riichi-active-marker)
    [data-testid="stButton"] > button p,

[data-testid="column"]:has(.riichi-active-marker)
    [data-testid="stButton"] > button span,

[data-testid="column"]:has(.riichi-active-marker)
    [data-testid="stButton"] > button div {

    color: #fff1bd !important;
    font-weight: 900 !important;
}


/* ============================================================
   TAMAÑO DE LOS BOTONES
   ============================================================ */

.selector-juego + div
    [data-testid="stButton"] > button {

    width: 100% !important;

    height: 52px !important;
    min-height: 52px !important;

    padding: 0.2rem 0.4rem !important;

    border-radius: 12px !important;

    font-size: 0.9rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.4px !important;

    transition:
        background-color 0.15s ease,
        border-color 0.15s ease,
        box-shadow 0.15s ease !important;
}


/* ============================================================
   HOVER
   ============================================================ */

[data-testid="column"]:has(.mcr-marker)
    [data-testid="stButton"] > button:hover,

[data-testid="column"]:has(.riichi-marker)
    [data-testid="stButton"] > button:hover {

    background: #173b2b !important;
    background-color: #173b2b !important;

    border-color: #e0bd5c !important;
}


[data-testid="column"]:has(.mcr-active-marker)
    [data-testid="stButton"] > button:hover,

[data-testid="column"]:has(.riichi-active-marker)
    [data-testid="stButton"] > button:hover {

    background: #327c54 !important;
    background-color: #327c54 !important;

    border-color: #ffd968 !important;
}


/* ============================================================
   TÍTULO DEL RANKING
   ============================================================ */

.titulo-ranking {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 2px 9px;
}

.titulo-ranking-texto {
    color: #f5e8c5 !important;
    font-size: 1rem;
    font-weight: 900;
    letter-spacing: 1.5px;
    white-space: nowrap;
}

.linea-dorada {
    height: 1px;

    background: linear-gradient(
        90deg,
        #a98a43,
        rgba(169, 138, 67, 0)
    );

    flex: 1;
}


/* ============================================================
   CABECERA DEL RANKING
   ============================================================ */

.resumen-ranking {
    display: grid;

    grid-template-columns:
        38px
        minmax(0, 1fr)
        70px
        32px;

    align-items: center;

    padding: 0 12px 6px;

    color: #8e815d !important;

    font-size: 0.58rem;
    font-weight: 800;

    letter-spacing: 1px;

    text-transform: uppercase;
}


/* ============================================================
   FILAS DEL RANKING
   ============================================================ */

[data-testid="stHorizontalBlock"]:has(.ranking-marker) {

    position: relative;

    align-items: center !important;

    gap: 6px !important;

    margin: 0 0 7px !important;

    padding: 8px 8px 8px 10px !important;

    min-height: 68px !important;

    background: linear-gradient(
        135deg,
        #123226 0%,
        #102b21 100%
    ) !important;

    border: 1px solid #4e5338 !important;

    border-radius: 13px !important;

    box-shadow:
        0 3px 10px rgba(0, 0, 0, 0.13),
        inset 0 1px 0 rgba(255,255,255,0.025) !important;
}

[data-testid="stHorizontalBlock"]:has(.ranking-marker):hover {
    border-color: #8f783d !important;
}

.ranking-marker {
    display: none !important;
}

.ranking-pos {
    color: #c09a4a !important;

    font-size: 0.95rem;
    font-weight: 900;

    text-align: center;
}

.ranking-name {
    color: #f5e8c5 !important;

    font-size: 0.93rem;
    font-weight: 800;

    line-height: 1.15;

    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.ranking-meta {
    color: #8f967f !important;

    font-size: 0.60rem;
    font-weight: 600;

    margin-top: 4px;

    white-space: nowrap;
}

.ranking-meta span {
    color: #8f967f !important;
}

.ranking-points {
    color: #f0c84b !important;

    font-size: 0.98rem;
    font-weight: 900;

    text-align: right;

    white-space: nowrap;
}

.ranking-points-label {
    color: #8d815d !important;

    font-size: 0.50rem;
    font-weight: 700;

    text-align: right;

    letter-spacing: 0.6px;

    margin-top: 2px;
}


/* ============================================================
   BOTÓN VER JUGADOR
   ============================================================ */

.ranking-ver-button button {

    width: 30px !important;
    min-width: 30px !important;

    height: 30px !important;
    min-height: 30px !important;

    padding: 0 !important;

    border-radius: 50% !important;

    background: #1a4030 !important;

    border: 1px solid #806c3d !important;

    color: #e8c867 !important;

    font-size: 1.05rem !important;
    font-weight: 900 !important;
}

.ranking-ver-button button p {
    color: #e8c867 !important;
    font-size: 1.05rem !important;
    line-height: 1 !important;
}

.ranking-ver-button button:hover {
    background: #e8c867 !important;
    border-color: #e8c867 !important;
}

.ranking-ver-button button:hover p {
    color: #12271d !important;
}


/* ============================================================
   MEDALLA
   ============================================================ */

.medalla {
    color: #e5bd50 !important;
    margin-left: 5px;
}


/* ============================================================
   DETALLE DEL JUGADOR
   ============================================================ */

.volver button {

    height: 42px !important;
    min-height: 42px !important;

    border-radius: 10px !important;

    background: transparent !important;

    border: 1px solid #665b3b !important;

    color: #d7c18b !important;

    font-size: 0.78rem !important;
    font-weight: 700 !important;

    margin-bottom: 12px !important;
}

.volver button p {
    color: #d7c18b !important;
}


.panel-jugador {

    background: linear-gradient(
        145deg,
        #14372a,
        #0f291f
    );

    border: 1px solid #77663a;

    border-radius: 15px;

    padding: 19px 14px 16px;

    margin-bottom: 12px;

    box-shadow:
        0 5px 18px rgba(0, 0, 0, 0.16);
}

.nombre-jugador {

    color: #f5e8c5 !important;

    font-size:
        clamp(1.35rem, 6vw, 1.65rem);

    font-weight: 900;

    text-align: center;

    line-height: 1.1;

    overflow-wrap: anywhere;
}

.posicion-jugador {

    color: #b99445 !important;

    text-align: center;

    font-size: 0.65rem;

    font-weight: 800;

    letter-spacing: 1.4px;

    margin-top: 6px;
}


/* ============================================================
   MÉTRICAS
   ============================================================ */

.metricas [data-testid="stHorizontalBlock"] {
    gap: 7px !important;
}

[data-testid="stMetric"] {

    background: #123226 !important;

    border: 1px solid #514f37 !important;

    border-radius: 11px !important;

    padding: 9px 6px !important;

    min-height: 69px !important;
}

[data-testid="stMetricLabel"] {

    color: #ae914e !important;

    font-size: 0.57rem !important;

    font-weight: 800 !important;

    letter-spacing: 0.6px;
}

[data-testid="stMetricValue"] {

    color: #f4e7c1 !important;

    font-size: 1.18rem !important;

    font-weight: 900 !important;
}


/* ============================================================
   RESULTADOS 1º - 5º
   ============================================================ */

.posiciones-titulo,
.historial-titulo {

    color: #b99445 !important;

    font-size: 0.67rem;

    font-weight: 900;

    letter-spacing: 1.5px;

    margin: 17px 2px 7px;
}

.posiciones [data-testid="stHorizontalBlock"] {
    gap: 5px !important;
}

.posicion-box {

    background: #123226;

    border: 1px solid #514f37;

    border-radius: 9px;

    text-align: center;

    padding: 7px 2px;
}

.posicion-box .numero {

    color: #f5e8c5 !important;

    font-size: 0.95rem;

    font-weight: 900;
}

.posicion-box .texto {

    color: #8f8a75 !important;

    font-size: 0.53rem;

    margin-top: 2px;
}


/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {

    border: 1px solid #4d5039 !important;

    border-radius: 11px !important;

    overflow: hidden !important;
}


/* ============================================================
   MENSAJES
   ============================================================ */

[data-testid="stAlert"] {

    background: #123226 !important;

    border: 1px solid #625b3b !important;

    border-radius: 11px !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {

    text-align: center;

    color: #5f684f !important;

    font-size: 0.55rem;

    letter-spacing: 1.5px;

    margin-top: 24px;
}


/* ============================================================
   MÓVIL
   ============================================================ */

@media (max-width: 500px) {

    .block-container {

        max-width: 100% !important;

        padding:
            0.65rem
            0.55rem
            1.5rem !important;
    }

    .cabecera {
        margin-bottom: 18px;
    }

    .titulo {

        font-size: 1.28rem;

        letter-spacing: 1px;
    }

    .subtitulo {

        font-size: 0.59rem;

        letter-spacing: 2.4px;
    }

    .selector-juego {
        margin-bottom: 19px;
    }

    .selector-juego + div
        [data-testid="stButton"] > button {

        height: 48px !important;

        min-height: 48px !important;

        font-size: 0.82rem !important;
    }

    .resumen-ranking {

        grid-template-columns:
            32px
            minmax(0, 1fr)
            62px
            29px;

        padding:
            0
            9px
            5px;

        font-size: 0.52rem;
    }

    [data-testid="stHorizontalBlock"]:has(.ranking-marker) {

        gap: 5px !important;

        min-height: 62px !important;

        padding: 7px !important;

        border-radius: 12px !important;
    }

    .ranking-pos {
        font-size: 0.87rem;
    }

    .ranking-name {
        font-size: 0.84rem;
    }

    .ranking-meta {

        font-size: 0.54rem;

        margin-top: 3px;
    }

    .ranking-points {
        font-size: 0.88rem;
    }

    .ranking-points-label {
        font-size: 0.44rem;
    }

    .ranking-ver-button button {

        width: 27px !important;

        min-width: 27px !important;

        height: 27px !important;

        min-height: 27px !important;

        font-size: 0.95rem !important;
    }

    .ranking-ver-button button p {
        font-size: 0.95rem !important;
    }

    .nombre-jugador {
        font-size: 1.38rem;
    }

    [data-testid="stMetric"] {

        min-height: 64px !important;

        padding: 8px 4px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.05rem !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.51rem !important;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOGO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


def buscar_logo():

    nombres = [
        "logo_mahjong_madrid.png",
        "logo_mahjong_madrid.PNG",
        "Logo_Mahjong_Madrid.png",
        "Logo Mahjong Madrid.png",
        "logo mahjong madrid.png",
    ]

    for nombre in nombres:

        ruta = BASE_DIR / nombre

        if ruta.exists():
            return ruta

    for ruta in BASE_DIR.iterdir():

        if not ruta.is_file():
            continue

        if ruta.suffix.lower() not in [
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        ]:
            continue

        nombre = (
            ruta.stem
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )

        if (
            "mahjong" in nombre
            and "madrid" in nombre
        ):
            return ruta

    return None


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = (
    "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"
)


def supabase_get(tabla):

    try:

        key = st.secrets["SUPABASE_KEY"]

        url = f"{SUPABASE_URL}/{tabla}"

        request = urllib.request.Request(
            url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(request) as response:

            datos = json.loads(
                response.read().decode("utf-8")
            )

        return pd.DataFrame(datos)

    except Exception as e:

        st.error(
            f"Error conectando con Supabase: {e}"
        )

        return pd.DataFrame()


# ============================================================
# CARGAR TABLAS
# ============================================================

jugadores = supabase_get("jugadores")

partidas = supabase_get("partidas")

resultados = supabase_get(
    "resultados_partidas"
)


if (
    jugadores.empty
    or partidas.empty
    or resultados.empty
):

    st.error(
        "No se han podido cargar los datos de Supabase."
    )

    st.stop()


# ============================================================
# PREPARAR DATOS
# ============================================================

resultados["puntuacion"] = pd.to_numeric(
    resultados["puntuacion"],
    errors="coerce",
)

resultados["posicion"] = pd.to_numeric(
    resultados["posicion"],
    errors="coerce",
)

partidas["tipo_juego"] = (
    partidas["tipo_juego"]
    .astype(str)
    .str.upper()
)


# ============================================================
# UNIR DATOS
# ============================================================

datos = resultados.merge(
    jugadores,
    left_on="jugador_id",
    right_on="id",
    how="left",
)


datos = datos.merge(
    partidas[
        [
            "id",
            "fecha",
            "tipo_juego",
        ]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=(
        "",
        "_partida",
    ),
)


# ============================================================
# CREAR RANKING
# ============================================================

def crear_ranking(tipo):

    df = datos[
        datos["tipo_juego"] == tipo
    ].copy()

    if df.empty:
        return pd.DataFrame()

    ranking = (
        df.groupby(
            [
                "jugador_id",
                "nombre",
            ],
            as_index=False,
        )
        .agg(
            Puntos=(
                "puntuacion",
                "sum",
            ),
            Partidas=(
                "partida_id",
                "nunique",
            ),
            Media=(
                "puntuacion",
                "mean",
            ),
        )
    )

    primeros = (
        df[
            df["posicion"] == 1
        ]
        .groupby("jugador_id")
        .size()
        .rename("Primero")
    )

    ranking = ranking.merge(
        primeros,
        on="jugador_id",
        how="left",
    )

    ranking["Primero"] = (
        ranking["Primero"]
        .fillna(0)
        .astype(int)
    )

    ranking = (
        ranking
        .sort_values(
            by=[
                "Puntos",
                "Primero",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .reset_index(drop=True)
    )

    ranking["Posicion"] = (
        ranking.index + 1
    )

    ranking["Puntos"] = (
        ranking["Puntos"]
        .round()
        .astype(int)
    )

    ranking["Media"] = (
        ranking["Media"]
        .round(1)
    )

    return ranking


# ============================================================
# MOSTRAR RANKING
# ============================================================

def mostrar_ranking(tipo):

    ranking = crear_ranking(tipo)

    if ranking.empty:

        st.info(
            f"No hay partidas de {tipo} todavía."
        )

        return

    st.markdown(
        """
        <div class="resumen-ranking">

            <div>POS.</div>

            <div>JUGADOR</div>

            <div style="text-align:right;">
                PUNTOS
            </div>

            <div></div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    for _, fila in ranking.iterrows():

        jugador_id = int(
            fila["jugador_id"]
        )

        nombre = html.escape(
            str(fila["nombre"])
        )

        posicion = int(
            fila["Posicion"]
        )

        puntos = int(
            fila["Puntos"]
        )

        partidas_jugadas = int(
            fila["Partidas"]
        )

        media = float(
            fila["Media"]
        )

        primero = int(
            fila["Primero"]
        )


        if posicion == 1:

            pos_display = "🥇"

        elif posicion == 2:

            pos_display = "🥈"

        elif posicion == 3:

            pos_display = "🥉"

        else:

            pos_display = str(
                posicion
            )


        medalla = ""

        if primero > 0:

            medalla = (
                f" · 🏆 {primero}"
            )


        st.markdown(
            '<span class="ranking-marker"></span>',
            unsafe_allow_html=True,
        )


        col_pos, col_info, col_points, col_button = (
            st.columns(
                [
                    0.55,
                    3.25,
                    0.95,
                    0.45,
                ],
                gap="small",
            )
        )


        with col_pos:

            st.markdown(
                f"""
                <div class="ranking-pos">
                    {pos_display}
                </div>
                """,
                unsafe_allow_html=True,
            )


        with col_info:

            st.markdown(
                f"""
                <div class="ranking-name">
                    {nombre}
                </div>

                <div class="ranking-meta">

                    {partidas_jugadas}
                    partidas

                    · media
                    {media:.1f}

                    {medalla}

                </div>
                """,
                unsafe_allow_html=True,
            )


        with col_points:

            st.markdown(
                f"""
                <div class="ranking-points">
                    {puntos}
                </div>

                <div class="ranking-points-label">
                    PUNTOS
                </div>
                """,
                unsafe_allow_html=True,
            )


        with col_button:

            st.markdown(
                '<div class="ranking-ver-button">',
                unsafe_allow_html=True,
            )

            if st.button(
                "›",
                key=f"jugador_{tipo}_{jugador_id}",
                help=(
                    f"Ver estadísticas de {nombre}"
                ),
                use_container_width=True,
            ):

                st.session_state[
                    "jugador_seleccionado"
                ] = jugador_id

                st.session_state[
                    "jugador_tipo"
                ] = tipo

                st.rerun()


            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


# ============================================================
# MOSTRAR JUGADOR
# ============================================================

def mostrar_jugador(
    jugador_id,
    tipo,
):

    ranking = crear_ranking(tipo)

    if ranking.empty:
        return


    jugador = ranking[
        ranking["jugador_id"]
        == jugador_id
    ]


    if jugador.empty:
        return


    jugador = jugador.iloc[0]


    nombre = str(
        jugador["nombre"]
    )

    posicion = int(
        jugador["Posicion"]
    )

    puntos = int(
        jugador["Puntos"]
    )

    partidas_jugadas = int(
        jugador["Partidas"]
    )

    media = float(
        jugador["Media"]
    )


    df_jugador = datos[
        (datos["jugador_id"] == jugador_id)
        &
        (datos["tipo_juego"] == tipo)
    ].copy()


    # ========================================================
    # VOLVER
    # ========================================================

    st.markdown(
        '<div class="volver">',
        unsafe_allow_html=True,
    )


    if st.button(
        "←  Volver al ranking",
        key="volver_ranking",
        use_container_width=True,
    ):

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


    # ========================================================
    # CABECERA JUGADOR
    # ========================================================

    st.markdown(
        f"""
        <div class="panel-jugador">

            <div class="nombre-jugador">
                {html.escape(nombre)}
            </div>

            <div class="posicion-jugador">
                RANKING {tipo}
                · POSICIÓN #{posicion}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # MÉTRICAS
    # ========================================================

    st.markdown(
        '<div class="metricas">',
        unsafe_allow_html=True,
    )


    c1, c2, c3 = st.columns(
        3,
        gap="small",
    )


    with c1:

        st.metric(
            "PUNTOS",
            f"{puntos}",
        )


    with c2:

        st.metric(
            "PARTIDAS",
            f"{partidas_jugadas}",
        )


    with c3:

        st.metric(
            "MEDIA",
            f"{media:.1f}",
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


    # ========================================================
    # RESULTADOS
    # ========================================================

    conteo = (
        df_jugador["posicion"]
        .value_counts()
        .to_dict()
    )


    st.markdown(
        '<div class="posiciones-titulo">'
        'RESULTADOS'
        '</div>',
        unsafe_allow_html=True,
    )


    posiciones = [
        ("🥇", 1),
        ("🥈", 2),
        ("🥉", 3),
        ("4º", 4),
        ("5º", 5),
    ]


    cols = st.columns(
        5,
        gap="small",
    )


    for col, (
        texto,
        numero,
    ) in zip(
        cols,
        posiciones,
    ):

        cantidad = int(
            conteo.get(
                numero,
                0,
            )
        )


        with col:

            st.markdown(
                f"""
                <div class="posicion-box">

                    <div class="numero">
                        {cantidad}
                    </div>

                    <div class="texto">
                        {texto}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


    # ========================================================
    # HISTORIAL
    # ========================================================

    st.markdown(
        '<div class="historial-titulo">'
        'HISTORIAL DE PARTIDAS'
        '</div>',
        unsafe_allow_html=True,
    )


    historial = df_jugador[
        [
            "fecha",
            "posicion",
            "puntuacion",
        ]
    ].copy()


    historial = historial.rename(
        columns={
            "fecha": "Fecha",
            "posicion": "Pos.",
            "puntuacion": "Puntos",
        }
    )


    historial = historial.sort_values(
        by="Fecha",
        ascending=False,
    )


    historial["Puntos"] = (
        pd.to_numeric(
            historial["Puntos"],
            errors="coerce",
        )
        .round()
        .astype(int)
    )


    st.dataframe(
        historial,
        use_container_width=True,
        hide_index=True,
        column_config={

            "Fecha":
                st.column_config.DateColumn(
                    "Fecha",
                    format="DD/MM/YYYY",
                ),

            "Pos.":
                st.column_config.NumberColumn(
                    "Pos.",
                    format="%d",
                ),

            "Puntos":
                st.column_config.NumberColumn(
                    "Puntos",
                    format="%d",
                ),
        },
    )


# ============================================================
# SESSION STATE
# ============================================================

if "tipo_juego" not in st.session_state:

    st.session_state[
        "tipo_juego"
    ] = "MCR"


if "jugador_seleccionado" not in st.session_state:

    st.session_state[
        "jugador_seleccionado"
    ] = None


if "jugador_tipo" not in st.session_state:

    st.session_state[
        "jugador_tipo"
    ] = None


# ============================================================
# CABECERA
# ============================================================

logo = buscar_logo()


st.markdown(
    '<div class="cabecera">',
    unsafe_allow_html=True,
)


if logo is not None:

    st.markdown(
        '<div class="logo-contenedor">',
        unsafe_allow_html=True,
    )

    st.image(
        str(logo),
        width=82,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="titulo">
        LIGA MAHJONG MADRID
    </div>

    <div class="subtitulo">
        RANKING OFICIAL
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SELECTOR MCR / RIICHI
# ============================================================

st.markdown(
    '<div class="selector-juego"></div>',
    unsafe_allow_html=True,
)


col_mcr, col_riichi = st.columns(
    2,
    gap="small",
)


# ============================================================
# MCR
# ============================================================

with col_mcr:

    if st.session_state["tipo_juego"] == "MCR":

        st.markdown(
            '<span class="mcr-active-marker"></span>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<span class="mcr-marker"></span>',
            unsafe_allow_html=True,
        )


    if st.button(
        "🀄  MCR",
        key="boton_mcr",
        use_container_width=True,
    ):

        st.session_state[
            "tipo_juego"
        ] = "MCR"

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()


# ============================================================
# RIICHI
# ============================================================

with col_riichi:

    if st.session_state["tipo_juego"] == "RIICHI":

        st.markdown(
            '<span class="riichi-active-marker"></span>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<span class="riichi-marker"></span>',
            unsafe_allow_html=True,
        )


    if st.button(
        "🎴  RIICHI",
        key="boton_riichi",
        use_container_width=True,
    ):

        st.session_state[
            "tipo_juego"
        ] = "RIICHI"

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()


# ============================================================
# RANKING O FICHA
# ============================================================

tipo_actual = (
    st.session_state[
        "tipo_juego"
    ]
)


if (
    st.session_state[
        "jugador_seleccionado"
    ]
    is not None
):

    mostrar_jugador(
        st.session_state[
            "jugador_seleccionado"
        ],
        st.session_state[
            "jugador_tipo"
        ],
    )


else:

    st.markdown(
        f"""
        <div class="titulo-ranking">

            <div class="titulo-ranking-texto">
                RANKING {tipo_actual}
            </div>

            <div class="linea-dorada"></div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    mostrar_ranking(
        tipo_actual
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        LIGA MAHJONG MADRID
    </div>
    """,
    unsafe_allow_html=True,
)
