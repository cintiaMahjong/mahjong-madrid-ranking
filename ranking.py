import streamlit as st
import pandas as pd
import urllib.request
import json
from pathlib import Path


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Liga Mahjong Madrid",
    page_icon="🀄",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# TEMPORADAS
# =========================================================

TEMPORADA_1 = "Oct 2025 - Sept 2026"
TEMPORADA_2 = "Oct 2026 - Sept 2027"


# =========================================================
# CSS
# =========================================================

css = """
<style>
.stApp {
    background-color: #0b2118;
}

[data-testid="stHeader"] {
    background-color: transparent;
}

[data-testid="stMainBlockContainer"] {
    max-width: 680px;
    padding-left: 10px;
    padding-right: 10px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.titulo {
    text-align: center;
    color: #f5e8c5;
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-top: 5px;
}

.subtitulo {
    text-align: center;
    color: #b89445;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 15px;
}

.ranking-titulo {
    color: #f5e8c5;
    font-size: 19px;
    font-weight: 900;
    margin-top: 15px;
    margin-bottom: 10px;
}

.ranking-cabecera {
    color: #91845d;
    font-size: 10px;
    font-weight: 800;
    display: grid;
    grid-template-columns: 45px 1fr 70px;
    padding: 0 10px 6px 10px;
}

.ranking-card {
    background-color: #143225;
    border: 1px solid #4f5539;
    border-radius: 11px;
    padding: 10px;
    margin-bottom: 5px;
}

.ranking-fila {
    display: grid;
    grid-template-columns: 45px 1fr 70px;
    align-items: center;
}

.ranking-posicion {
    color: #b89445;
    font-size: 17px;
    font-weight: 900;
}

.ranking-nombre {
    color: #f5e8c5;
    font-size: 15px;
    font-weight: 800;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.ranking-puntos {
    color: #f0c84b;
    font-size: 16px;
    font-weight: 900;
    text-align: right;
}

.ranking-info {
    color: #918b75;
    font-size: 10px;
    margin-left: 45px;
    margin-top: 4px;
}

.ficha {
    background-color: #102a20;
    border: 1px solid #79683a;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 15px;
}

.ficha-nombre {
    color: #f5e8c5;
    font-size: 23px;
    font-weight: 900;
}

.ficha-posicion {
    color: #b89445;
    font-size: 10px;
    font-weight: 800;
    margin-top: 5px;
}

.seccion {
    color: #b89445;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-top: 18px;
    margin-bottom: 8px;
}

div[data-testid="stButton"] button {
    background-color: #143225 !important;
    color: #f5e8c5 !important;
    border: 1px solid #806a35 !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}

div[data-testid="stButton"] button:hover {
    border-color: #d1ae52 !important;
    color: #fff0bd !important;
}

@media (max-width: 500px) {
    [data-testid="stMainBlockContainer"] {
        padding-left: 7px;
        padding-right: 7px;
    }

    .titulo {
        font-size: 21px;
    }

    .ranking-cabecera,
    .ranking-fila {
        grid-template-columns: 38px 1fr 65px;
    }

    .ranking-nombre {
        font-size: 14px;
    }

    .ranking-puntos {
        font-size: 15px;
    }

    .ranking-info {
        margin-left: 38px;
    }
}
</style>
"""

st.markdown(css, unsafe_allow_html=True)


# =========================================================
# LOGO
# =========================================================

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

    return None


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = "https://gauqwlrsmxynqcokblaw.supabase.co/rest/v1"


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

        st.error(f"Error conectando con Supabase: {e}")

        return pd.DataFrame()


# =========================================================
# CARGAR TABLAS
# =========================================================

jugadores = supabase_get("jugadores")
partidas = supabase_get("partidas")
resultados = supabase_get("resultados_partidas")


if jugadores.empty:

    st.error("No se han podido cargar los jugadores.")
    st.stop()


if partidas.empty:

    st.error("No se han podido cargar las partidas.")
    st.stop()


if resultados.empty:

    st.error("No se han podido cargar los resultados.")
    st.stop()


# =========================================================
# PREPARAR DATOS
# =========================================================

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
    .str.strip()
)

partidas["temporada"] = (
    partidas["temporada"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# =========================================================
# UNIR TABLAS
# =========================================================

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
            "tipo_juego",
            "temporada"
        ]
    ],
    left_on="partida_id",
    right_on="id",
    how="left",
    suffixes=("", "_partida")
)


# =========================================================
# CREAR RANKING
# =========================================================

def crear_ranking(tipo, temporada):

    filtro = (
        (datos["tipo_juego"] == tipo)
        &
        (datos["temporada"] == temporada)
    )

    df = datos[filtro].copy()

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
    )

    ranking = ranking.reset_index(drop=True)

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


# =========================================================
# MOSTRAR RANKING
# =========================================================

def mostrar_ranking(tipo, temporada):

    ranking = crear_ranking(
        tipo,
        temporada
    )

    if ranking.empty:

        st.info(
            f"No hay partidas de {tipo} en {temporada}."
        )

        return

    st.markdown(
        f'<div class="ranking-titulo">RANKING {tipo}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="ranking-cabecera">'
        '<div>POS.</div>'
        '<div>JUGADOR</div>'
        '<div style="text-align:right;">PUNTOS</div>'
        '</div>',
        unsafe_allow_html=True
    )

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

        if posicion == 1:
            puesto = "🥇"

        elif posicion == 2:
            puesto = "🥈"

        elif posicion == 3:
            puesto = "🥉"

        else:
            puesto = str(posicion)

        tarjeta = (
            '<div class="ranking-card">'
            '<div class="ranking-fila">'
            f'<div class="ranking-posicion">{puesto}</div>'
            f'<div class="ranking-nombre">{nombre}</div>'
            f'<div class="ranking-puntos">{puntos}</div>'
            '</div>'
            '<div class="ranking-info">'
            f'{partidas_jugadas} partidas'
            f' · media {media:.1f}'
            f' · 🥇 {primero}'
            '</div>'
            '</div>'
        )

        st.markdown(
            tarjeta,
            unsafe_allow_html=True
        )

        if st.button(
            f"Ver {nombre}",
            key=f"jugador_{tipo}_{temporada}_{jugador_id}",
            use_container_width=True
        ):

            st.session_state[
                "jugador_seleccionado"
            ] = jugador_id

            st.session_state[
                "jugador_tipo"
            ] = tipo

            st.session_state[
                "jugador_temporada"
            ] = temporada

            st.rerun()


# =========================================================
# MOSTRAR JUGADOR
# =========================================================

def mostrar_jugador(
    jugador_id,
    tipo,
    temporada
):

    ranking = crear_ranking(
        tipo,
        temporada
    )

    jugador = ranking[
        ranking["jugador_id"] == jugador_id
    ]

    if jugador.empty:

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()

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
        &
        (datos["temporada"] == temporada)
    ].copy()

    if st.button(
        "← Volver al ranking",
        key="volver_ranking",
        use_container_width=True
    ):

        st.session_state[
            "jugador_seleccionado"
        ] = None

        st.rerun()

    ficha = (
        '<div class="ficha">'
        f'<div class="ficha-nombre">{nombre}</div>'
        f'<div class="ficha-posicion">'
        f'RANKING {tipo} · POSICIÓN #{posicion}'
        '</div>'
        '</div>'
    )

    st.markdown(
        ficha,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "PUNTOS",
            puntos
        )

    with col2:

        st.metric(
            "PARTIDAS",
            partidas_jugadas
        )

    with col3:

        st.metric(
            "MEDIA",
            f"{media:.1f}"
        )

    st.markdown(
        '<div class="seccion">RESULTADOS</div>',
        unsafe_allow_html=True
    )

    conteo = (
        df_jugador["posicion"]
        .value_counts()
        .to_dict()
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    posiciones = [
        ("🥇", 1),
        ("🥈", 2),
        ("🥉", 3),
        ("4º", 4),
        ("5º", 5)
    ]

    columnas = [
        c1,
        c2,
        c3,
        c4,
        c5
    ]

    for columna, dato in zip(
        columnas,
        posiciones
    ):

        texto, numero = dato

        cantidad = int(
            conteo.get(
                numero,
                0
            )
        )

        with columna:

            st.metric(
                texto,
                cantidad
            )

    st.markdown(
        '<div class="seccion">'
        'HISTORIAL DE PARTIDAS'
        '</div>',
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
            "posicion": "Posición",
            "puntuacion": "Puntos"
        }
    )
```
