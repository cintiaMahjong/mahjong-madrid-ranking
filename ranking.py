import streamlit as st
import pandas as pd
import urllib.request
import json
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS - DISEÑO MOBILE FIRST
# ============================================================

st.markdown("""
<style>

/* ============================================================
   RESET / FONDO
   ============================================================ */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: #0b2118 !important;
}

[data-testid="stAppViewContainer"] {
    min-width: 0 !important;
}

.main {
    background: #0b2118 !important;
}

.block-container {
    max-width: 680px !important;
    padding-top: 1rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    padding-bottom: 2rem !important;
}


/* ============================================================
   OCULTAR ELEMENTOS INNECESARIOS
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

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
span {
    color: #f5e8c5;
}


/* ============================================================
   CABECERA
   ============================================================ */

.cabecera {
    text-align: center;
    margin-bottom: 14px;
}

.logo-contenedor {
    display: flex;
    justify-content: center;
    margin-bottom: 4px;
}

.titulo {
    color: #f5e8c5 !important;
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: 1.5px;
    line-height: 1.1;
    margin: 0;
}

.subtitulo {
    color: #b89445 !important;
    font-size: 0.72rem;
    letter-spacing: 2px;
    margin-top: 5px;
}


/* ============================================================
   SELECTOR MCR / RIICHI
   ============================================================ */

.selector-juego {
    margin-top: 18px;
    margin-bottom: 20px;
}

[data-testid="column"]:has(.selector-marker) [data-testid="stButton"] > button {
    height: 62px !important;
    min-height: 62px !important;
    border-radius: 13px !important;
    font-size: 1.12rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.5px !important;
    padding: 0.3rem 0.4rem !important;
    box-shadow: none !important;
}

/* Marcadores invisibles. Evitamos divs abiertos/cerrados alrededor de
   st.button porque Streamlit puede renderizarlos como texto visible. */
.selector-marker {
    display: none !important;
}

/* INACTIVO: verde oscuro + borde amarillo */
[data-testid="column"]:has(.selector-marker-normal) [data-testid="stButton"] > button {
    background: #123125 !important;
    background-color: #123125 !important;
    background-image: none !important;
    border: 2px solid #c5a84d !important;
    color: #e6d9ad !important;
    box-shadow: none !important;
}

[data-testid="column"]:has(.selector-marker-normal) [data-testid="stButton"] > button p,
[data-testid="column"]:has(.selector-marker-normal) [data-testid="stButton"] > button span,
[data-testid="column"]:has(.selector-marker-normal) [data-testid="stButton"] > button div {
    color: #e6d9ad !important;
    font-weight: 900 !important;
}

/* ACTIVO: verde luminoso + borde amarillo */
[data-testid="column"]:has(.selector-marker-activo) [data-testid="stButton"] > button {
    background: #286b49 !important;
    background-color: #286b49 !important;
    background-image: none !important;
    border: 2px solid #f0c84b !important;
    color: #fff1bd !important;
    box-shadow: 0 0 14px rgba(240,200,75,0.22), inset 0 1px 0 rgba(255,255,255,0.10) !important;
}

[data-testid="column"]:has(.selector-marker-activo) [data-testid="stButton"] > button p,
[data-testid="column"]:has(.selector-marker-activo) [data-testid="stButton"] > button span,
[data-testid="column"]:has(.selector-marker-activo) [data-testid="stButton"] > button div {
    color: #fff1bd !important;
    font-weight: 900 !important;
}

[data-testid="column"]:has(.selector-marker) [data-testid="stButton"] > button:hover {
    transform: none !important;
}


/* ============================================================
   TÍTULO RANKING
   ============================================================ */

.titulo-ranking {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 8px;
    margin-bottom: 10px;
}

.titulo-ranking-texto {
    color: #f5e8c5 !important;
    font-size: 1.15rem;
    font-weight: 900;
    letter-spacing: 1px;
}

.linea-dorada {
    height: 1px;
    background: #806a35;
    flex: 1;
    margin-left: 12px;
}


/* ============================================================
   CABECERA PEQUEÑA DEL RANKING
   ============================================================ */

.resumen-ranking {
    display: grid;
    grid-template-columns: 48px 1fr 82px;
    align-items: center;
    padding: 7px 12px;
    margin-bottom: 6px;

    color: #9d8c5a !important;

    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}


/* ============================================================
   TARJETAS DE JUGADORES
   ============================================================ */

.tarjeta-jugador {
    margin-bottom: 8px;
}

.tarjeta-jugador div[data-testid="stButton"] > button {
    width: 100% !important;
    min-height: 66px !important;
    height: auto !important;

    background: #143225 !important;
    background-color: #143225 !important;

    border: 1px solid #635a38 !important;
    border-radius: 12px !important;

    padding: 8px 12px !important;

    text-align: left !important;

    box-shadow: none !important;
}


/* Hover */

.tarjeta-jugador div[data-testid="stButton"] > button:hover {
    background: #1a4230 !important;
    background-color: #1a4230 !important;
    border-color: #a48a45 !important;
}


/* Texto */

.tarjeta-jugador div[data-testid="stButton"] > button p {
    color: #f5e8c5 !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
}


/* ============================================================
   INFORMACIÓN DENTRO DE CADA JUGADOR
   ============================================================ */

.fila-jugador {
    display: grid;
    grid-template-columns: 43px 1fr 75px;
    align-items: center;

    width: 100%;

    margin-top: -54px;
    margin-bottom: 8px;

    padding-left: 13px;
    padding-right: 13px;

    pointer-events: none;
}

.posicion {
    color: #b89445 !important;
    font-size: 1rem;
    font-weight: 900;
}

.nombre {
    color: #f5e8c5 !important;
    font-size: 1rem;
    font-weight: 800;

    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.puntos {
    color: #f0c84b !important;
    font-size: 1.05rem;
    font-weight: 900;
    text-align: right;
}


/* ============================================================
   SEGUNDA LÍNEA
   ============================================================ */

.info-jugador {
    display: flex;
    align-items: center;
    justify-content: flex-start;

    margin-left: 56px;
    margin-top: -5px;
    margin-bottom: 9px;

    color: #9f987e !important;

    font-size: 0.68rem;
    font-weight: 600;
}

.info-jugador span {
    color: #9f987e !important;
}


/* ============================================================
   MEDALLA
   ============================================================ */

.medalla {
    color: #e6c25c !important;
    margin-left: 7px;
}


/* ============================================================
   PANEL DEL JUGADOR
   ============================================================ */

.panel-jugador {
    background: #102a20;
    border: 1px solid #79683a;
    border-radius: 15px;

    padding: 18px 14px;

    margin-top: 12px;
    margin-bottom: 18px;
}

.nombre-jugador {
    color: #f5e8c5 !important;
    font-size: 1.65rem;
    font-weight: 900;
    text-align: center;
    line-height: 1.1;
}

.posicion-jugador {
    color: #b89445 !important;
    text-align: center;

    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.2px;

    margin-top: 5px;
    margin-bottom: 18px;
}


/* ============================================================
   MÉTRICAS DEL JUGADOR
   ============================================================ */

[data-testid="stMetric"] {
    background: #173629 !important;

    border: 1px solid #645a38 !important;
    border-radius: 11px !important;

    padding: 9px !important;

    min-height: 72px !important;
}

[data-testid="stMetricLabel"] {
    color: #b89445 !important;
    font-size: 0.66rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #f5e8c5 !important;
    font-size: 1.35rem !important;
    font-weight: 900 !important;
}


/* ============================================================
   POSICIONES 1-5
   ============================================================ */

.posiciones-titulo {
    color: #b89445 !important;
    font-size: 0.75rem;
    font-weight: 900;
    letter-spacing: 1px;
    margin-top: 18px;
    margin-bottom: 8px;
}

.posiciones {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 5px;
}

.posicion-box {
    background: #173629;
    border: 1px solid #625a3c;
    border-radius: 8px;

    text-align: center;

    padding: 7px 2px;
}

.posicion-box .numero {
    color: #f5e8c5 !important;
    font-size: 1rem;
    font-weight: 900;
}

.posicion-box .texto {
    color: #a69a7a !important;
    font-size: 0.6rem;
}


/* ============================================================
   HISTORIAL
   ============================================================ */

.historial-titulo {
    color: #b89445 !important;
    font-size: 0.8rem;
    font-weight: 900;
    letter-spacing: 1px;

    margin-top: 20px;
    margin-bottom: 8px;
}


/* ============================================================
   BOTÓN VOLVER
   ============================================================ */

.volver div[data-testid="stButton"] > button {
    height: 46px !important;

    background: transparent !important;
    background-color: transparent !important;

    border: 1px solid #79683a !important;

    color: #d6c28c !important;

    border-radius: 10px !important;

    font-size: 0.85rem !important;
    font-weight: 700 !important;
}

.volver div[data-testid="stButton"] > button p {
    color: #d6c28c !important;
}


/* ============================================================
   MENSAJES
   ============================================================ */

[data-testid="stAlert"] {
    background: #173629 !important;
    border: 1px solid #79683a !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    text-align: center;

    color: #766d50 !important;

    font-size: 0.62rem;

    letter-spacing: 1px;

    margin-top: 25px;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 500px) {

    .block-container {
        padding-top: 0.65rem !important;
        padding-left: 0.55rem !important;
        padding-right: 0.55rem !important;
    }

    .titulo {
        font-size: 1.45rem;
    }

    .selector-juego div[data-testid="stButton"] > button {
        height: 58px !important;
        min-height: 58px !important;
        font-size: 1rem !important;
    }

    .resumen-ranking {
        grid-template-columns: 42px 1fr 75px;
        font-size: 0.62rem;
    }

    .fila-jugador {
        grid-template-columns: 38px 1fr 70px;
        padding-left: 10px;
        padding-right: 10px;
    }

    .nombre {
        font-size: 0.92rem;
    }

    .puntos {
        font-size: 0.95rem;
    }

    .info-jugador {
        margin-left: 48px;
        font-size: 0.63rem;
    }

    [data-testid="stMetric"] {
        min-height: 68px !important;
        padding: 7px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }

    .panel-jugador {
        padding: 15px 10px;
    }

}

</style>
""", unsafe_allow_html=True)


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
        "logo mahjong madrid.png"
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
            ".webp"
        ]:
            continue

        nombre = (
            ruta.stem.lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )

        if "mahjong" in nombre and "madrid" in nombre:
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
                "Content-Type": "application/json"
            }
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
resultados = supabase_get("resultados_partidas")


if jugadores.empty or partidas.empty or resultados.empty:

    st.error(
        "No se han podido cargar los datos de Supabase."
    )

    st.stop()


# ============================================================
# PREPARAR DATOS
# ============================================================

resultados["puntuacion"] = pd.to_numeric(
    resultados["puntuacion"],
    errors="coerce"
)

resultados["posicion"] = pd.to_numeric(
    resultados["posicion"],
    errors="coerce"
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
    how="left"
)

datos = datos.merge(
    partidas[
        [
            "id",
            "fecha",
            "tipo_juego"
        ]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
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
                "nombre"
            ],
            as_index=False
        )
        .agg(
            Puntos=("puntuacion", "sum"),
            Partidas=("partida_id", "nunique"),
            Media=("puntuacion", "mean")
        )
    )

    primeros = (
        df[df["posicion"] == 1]
        .groupby("jugador_id")
        .size()
        .rename("Primero")
    )

    ranking = ranking.merge(
        primeros,
        on="jugador_id",
        how="left"
    )

    ranking["Primero"] = (
        ranking["Primero"]
        .fillna(0)
        .astype(int)
    )

    ranking = ranking.sort_values(
        by=[
            "Puntos",
            "Primero"
        ],
        ascending=[
            False,
            False
        ]
    ).reset_index(drop=True)

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

    # -----------------------------------------------
    # Cabecera pequeña
    # -----------------------------------------------

    st.markdown(
        """
        <div class="resumen-ranking">
            <div>POS.</div>
            <div>JUGADOR</div>
            <div style="text-align:right;">
                PUNTOS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------
    # Jugadores
    # -----------------------------------------------

    for _, fila in ranking.iterrows():

        jugador_id = int(
            fila["jugador_id"]
        )

        nombre = str(
            fila["nombre"]
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

        # Botón

        st.markdown(
            '<div class="tarjeta-jugador">',
            unsafe_allow_html=True
        )

        if st.button(
            nombre,
            key=f"jugador_{tipo}_{jugador_id}",
            use_container_width=True
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
            unsafe_allow_html=True
        )

        # Información visual sobre el botón

        medalla = ""

        if primero > 0:
            medalla = (
                f'<span class="medalla">🥇 {primero}</span>'
            )

        st.markdown(
            f"""
            <div class="fila-jugador">

                <div class="posicion">
                    {posicion}
                </div>

                <div class="nombre">
                    {nombre}
                </div>

                <div class="puntos">
                    {puntos}
                </div>

            </div>

            <div class="info-jugador">
                {partidas_jugadas} partidas
                &nbsp;·&nbsp;
                media {media:.1f}
                {medalla}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# MOSTRAR JUGADOR
# ============================================================

def mostrar_jugador(
    jugador_id,
    tipo
):

    ranking = crear_ranking(tipo)

    if ranking.empty:
        return

    jugador = ranking[
        ranking["jugador_id"] == jugador_id
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
    # BOTÓN VOLVER
    # ========================================================

    st.markdown(
        '<div class="volver">',
        unsafe_allow_html=True
    )

    if st.button(
        "← Volver al ranking",
        key="volver_ranking",
        use_container_width=True
    ):

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # ========================================================
    # CABECERA JUGADOR
    # ========================================================

    st.markdown(
        f"""
        <div class="panel-jugador">

            <div class="nombre-jugador">
                {nombre}
            </div>

            <div class="posicion-jugador">
                RANKING {tipo}
                · POSICIÓN #{posicion}
            </div>

        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # MÉTRICAS
    # ========================================================

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "PUNTOS",
            f"{puntos}"
        )

    with c2:

        st.metric(
            "PARTIDAS",
            f"{partidas_jugadas}"
        )

    with c3:

        st.metric(
            "MEDIA",
            f"{media:.1f}"
        )


    # ========================================================
    # POSICIONES
    # ========================================================

    conteo = (
        df_jugador["posicion"]
        .value_counts()
        .to_dict()
    )

    st.markdown(
        """
        <div class="posiciones-titulo">
            RESULTADOS
        </div>

        <div class="posiciones">
        """,
        unsafe_allow_html=True
    )

    posiciones = [
        ("🥇", 1),
        ("🥈", 2),
        ("🥉", 3),
        ("4º", 4),
        ("5º", 5)
    ]

    for texto, numero in posiciones:

        cantidad = int(
            conteo.get(numero, 0)
        )

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
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # ========================================================
    # HISTORIAL
    # ========================================================

    st.markdown(
        """
        <div class="historial-titulo">
            HISTORIAL DE PARTIDAS
        </div>
        """,
        unsafe_allow_html=True
    )

    historial = df_jugador[
        [
            "fecha",
            "posicion",
            "puntuacion"
        ]
    ].copy()

    historial = historial.rename(
        columns={
            "fecha": "Fecha",
            "posicion": "Pos.",
            "puntuacion": "Puntos"
        }
    )

    historial = historial.sort_values(
        by="Fecha",
        ascending=False
    )

    historial["Puntos"] = (
        pd.to_numeric(
            historial["Puntos"],
            errors="coerce"
        )
        .round()
        .astype(int)
    )

    st.dataframe(
        historial,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fecha": st.column_config.DateColumn(
                "Fecha",
                format="DD/MM/YYYY"
            ),
            "Pos.": st.column_config.NumberColumn(
                "Pos.",
                format="%d"
            ),
            "Puntos": st.column_config.NumberColumn(
                "Puntos",
                format="%d"
            )
        }
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
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
    unsafe_allow_html=True
)


if logo is not None:

    st.image(
        str(logo),
        width=85
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
    unsafe_allow_html=True
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# SELECTOR MCR / RIICHI
# ============================================================

col_mcr, col_riichi = st.columns(
    2,
    gap="small"
)


# ------------------------------------------------------------
# MCR
# ------------------------------------------------------------

with col_mcr:
    if st.session_state["tipo_juego"] == "MCR":
        st.markdown(
            '<span class="selector-marker selector-marker-activo"></span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="selector-marker selector-marker-normal"></span>',
            unsafe_allow_html=True
        )

    if st.button(
        "🀄  MCR",
        key="boton_mcr",
        use_container_width=True
    ):
        st.session_state[
            "tipo_juego"
        ] = "MCR"

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()


# ------------------------------------------------------------
# RIICHI
# ------------------------------------------------------------

with col_riichi:
    if st.session_state["tipo_juego"] == "RIICHI":
        st.markdown(
            '<span class="selector-marker selector-marker-activo"></span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="selector-marker selector-marker-normal"></span>',
            unsafe_allow_html=True
        )

    if st.button(
        "🎴  RIICHI",
        key="boton_riichi",
        use_container_width=True
    ):
        st.session_state[
            "tipo_juego"
        ] = "RIICHI"

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()


# ============================================================
# RANKING O FICHA DEL JUGADOR
# ============================================================

tipo_actual = st.session_state[
    "tipo_juego"
]


if st.session_state[
    "jugador_seleccionado"
] is not None:

    mostrar_jugador(
        st.session_state[
            "jugador_seleccionado"
        ],
        st.session_state[
            "jugador_tipo"
        ]
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
        unsafe_allow_html=True
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
    unsafe_allow_html=True
)
