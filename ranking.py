import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import os
import html
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
st.markdown("""
<style>
/* =========================================================
   MAHJONG MADRID - DISEÑO LIMPIO Y RESPONSIVE
   Escritorio y móvil se diseñan por separado mediante media queries.
========================================================= */
* { box-sizing: border-box; }

[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

.stApp { background: #ffffff; }

.block-container {
    width: 100% !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 1.25rem 1.25rem 2.5rem !important;
}

[data-testid="stAppViewContainer"] .main,
[data-testid="stAppViewContainer"] .block-container {
    overflow-x: hidden !important;
}

h1, h2, h3 { color: #151515 !important; }
h1 { font-size: 2rem !important; font-weight: 800 !important; line-height: 1.1 !important; }
h2 { font-size: 1.4rem !important; }
h3 { font-size: 1.1rem !important; }

/* Botones normales: compactos en escritorio */
.stButton > button {
    width: 100% !important;
    min-height: 40px !important;
    height: auto !important;
    padding: 6px 9px !important;
    border-radius: 8px !important;
    border: 1px solid #d6d6d6 !important;
    background: #ffffff !important;
    color: #151515 !important;
    font-size: .90rem !important;
    font-weight: 600 !important;
    line-height: 1.1 !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    border-color: #b40000 !important;
    color: #b40000 !important;
}

/* Pestañas */
.stTabs [data-baseweb="tab-list"] {
    width: 100% !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    justify-content: center !important;
    min-height: 46px !important;
    padding: 6px 8px !important;
    font-size: .95rem !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #14532d !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: #14532d !important;
}

/* Selector de ordenación */
div[role="radiogroup"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
    width: 100% !important;
}
div[role="radiogroup"] label {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    padding: 7px 8px !important;
    border: 1px solid #d8d8d8 !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    text-align: center !important;
    font-size: .82rem !important;
}

/* Cabecera */
.main-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
}
.main-header-logo { width: 78px; min-width: 78px; }
.main-header-title { min-width: 0; }
.main-header-subtitle {
    color: #777777;
    font-size: .90rem;
    line-height: 1.2;
    margin-top: 2px;
}

/* =========================================================
   RANKING ESCRITORIO
========================================================= */
.ranking-box {
    width: 100%;
    border: 1px solid #dedede;
    border-radius: 9px;
    overflow: hidden;
    background: #ffffff;
}
.ranking-header,
.ranking-row {
    display: grid;
    grid-template-columns: 52px minmax(170px, 1fr) 82px 58px 58px 82px 68px 68px 82px;
    column-gap: 5px;
    align-items: center;
    width: 100%;
    padding-left: 9px;
    padding-right: 9px;
}
.ranking-header {
    min-height: 48px;
    background: #14532d;
    color: #ffffff;
    font-size: .76rem;
    font-weight: 800;
}
.ranking-row {
    min-height: 50px;
    border-top: 1px solid #e5e5e5;
    background: #ffffff;
    font-size: .86rem;
}
.ranking-row:nth-child(odd) { background: #fff9df; }
.ranking-cell { min-width: 0; }
.ranking-position { text-align: center; font-weight: 800; }
.ranking-value { text-align: center; font-weight: 700; white-space: nowrap; }
.ranking-player-link {
    display: block;
    width: 100%;
    color: #111111;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
    font-weight: 600;
}
.ranking-player-link:hover { color: #b40000; }

/* =========================================================
   FICHA / HISTORIAL
========================================================= */
.player-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #111111;
    margin: 8px 0 12px;
    overflow-wrap: anywhere;
}
.match-header {
    background: #f2f7f3;
    color: #17612e;
    border-left: 4px solid #17612e;
    padding: 9px 12px;
    border-radius: 7px;
    margin: 13px 0 5px;
    font-weight: 700;
}
.match-col-header {
    font-size: .76rem;
    color: #666666;
    font-weight: 700;
    padding: 4px 5px;
}
.match-cell {
    background: #ffffff;
    border-bottom: 1px solid #eeeeee;
    padding: 7px 5px;
    font-size: .88rem;
}
.match-cell-selected {
    background: #fff8d9;
    border-bottom: 1px solid #eadf9c;
    padding: 7px 5px;
    font-weight: 700;
    font-size: .88rem;
}

[data-testid="stMetric"] {
    border: 1px solid #e1e1e1 !important;
    border-radius: 9px !important;
    padding: 9px !important;
    background: #fafafa !important;
    min-width: 0 !important;
}
[data-testid="stMetricLabel"] { font-size: .72rem !important; }
[data-testid="stMetricValue"] { font-size: 1.25rem !important; }

/* =========================================================
   RANKING MÓVIL: HTML PURO, SIN st.button NI st.columns
   Esto es deliberado: evita que Streamlit apile o agrande botones.
========================================================= */
.mobile-ranking {
    width: 100%;
    max-width: 100%;
    border: 1px solid #dedede;
    border-radius: 8px;
    overflow: hidden;
}
.mobile-ranking-header,
.mobile-ranking-row {
    display: grid;
    grid-template-columns: 38px minmax(0, 1fr) 74px;
    width: 100%;
    align-items: center;
}
.mobile-ranking-header {
    min-height: 43px;
    padding: 0 7px;
    background: #14532d;
    color: #ffffff;
    font-size: .70rem;
    font-weight: 800;
}
.mobile-ranking-row {
    min-height: 44px;
    padding: 0 7px;
    border-top: 1px solid #e5e5e5;
    background: #ffffff;
    text-decoration: none !important;
}
.mobile-ranking-row:nth-child(odd) { background: #fff9df; }
.mobile-pos { text-align: center; font-size: .90rem; font-weight: 800; }
.mobile-name {
    min-width: 0;
    padding: 0 5px;
    color: #111111;
    font-size: .82rem;
    font-weight: 600;
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.mobile-value {
    text-align: right;
    padding-right: 1px;
    color: #111111;
    font-size: .80rem;
    font-weight: 800;
    white-space: nowrap;
}
.mobile-ranking-row:hover .mobile-name { color: #b40000; }

@media (max-width: 700px) {
    .block-container {
        width: 100% !important;
        max-width: 100% !important;
        padding: .55rem .45rem 1.4rem !important;
    }

    h1 { font-size: 1.35rem !important; }
    h2 { font-size: 1.15rem !important; }
    h3 { font-size: 1rem !important; }

    .main-header { gap: 9px; margin-bottom: 5px; }
    .main-header-logo { width: 54px; min-width: 54px; }
    .main-header-subtitle { font-size: .72rem; }

    .stTabs [data-baseweb="tab"] {
        min-height: 40px !important;
        padding: 4px 3px !important;
        font-size: .78rem !important;
    }

    div[role="radiogroup"] {
        gap: 3px !important;
    }
    div[role="radiogroup"] label {
        padding: 6px 3px !important;
        font-size: .68rem !important;
        line-height: 1 !important;
    }

    /* Los botones normales de otras pantallas sí se mantienen usables,
       pero NO intervienen en el ranking móvil. */
    .stButton > button {
        min-height: 38px !important;
        padding: 5px 7px !important;
        font-size: .82rem !important;
    }

    .mobile-ranking-header,
    .mobile-ranking-row {
        grid-template-columns: 36px minmax(0, 1fr) 72px;
    }
    .mobile-ranking-header {
        min-height: 40px;
        font-size: .66rem;
    }
    .mobile-ranking-row {
        min-height: 43px;
    }
    .mobile-pos { font-size: .86rem; }
    .mobile-name { font-size: .78rem; padding: 0 4px; }
    .mobile-value { font-size: .76rem; }

    [data-testid="stMetric"] { padding: 6px 5px !important; }
    [data-testid="stMetricLabel"] { font-size: .62rem !important; }
    [data-testid="stMetricValue"] { font-size: .98rem !important; }

    .match-cell, .match-cell-selected {
        font-size: .80rem;
        padding: 6px 4px;
    }
}

@media (max-width: 380px) {
    .block-container { padding-left: .28rem !important; padding-right: .28rem !important; }
    .main-header-logo { width: 48px; min-width: 48px; }
    h1 { font-size: 1.22rem !important; }
    .mobile-ranking-header,
    .mobile-ranking-row { grid-template-columns: 34px minmax(0, 1fr) 68px; }
    .mobile-name { font-size: .75rem; }
    .mobile-value { font-size: .73rem; }
}
</style>
""", unsafe_allow_html=True)
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
@st.cache_data(ttl=60)
def cargar_datos():
    jugadores = supabase_get("jugadores", {"select": "*"})
    partidas = supabase_get("partidas", {"select": "*"})
    resultados = supabase_get("resultados_partidas", {"select": "*"})
    return (
        pd.DataFrame(jugadores),
        pd.DataFrame(partidas),
        pd.DataFrame(resultados)
    )
try:
    df_jugadores, df_partidas, df_resultados = cargar_datos()
except Exception as e:
    st.error("No se han podido cargar los datos de Supabase.")
    st.exception(e)
    st.stop()
datos = df_resultados.copy()
if not df_partidas.empty:
    columnas_partidas = [
        c for c in [
            "id", "fecha", "tipo_juego", "temporada",
            "nombre", "nombre_partida"
        ] if c in df_partidas.columns
    ]
    if "id" in columnas_partidas:
        partidas_merge = df_partidas[columnas_partidas].copy()
        partidas_merge = partidas_merge.rename(columns={"id": "partida_id"})
        datos = datos.merge(partidas_merge, on="partida_id", how="left")
if not df_jugadores.empty:
    columnas_jugadores = [
        c for c in ["id", "nombre", "name"]
        if c in df_jugadores.columns
    ]
    if "id" in columnas_jugadores:
        jugadores_merge = df_jugadores[columnas_jugadores].copy()
        if "nombre" not in jugadores_merge.columns and "name" in jugadores_merge.columns:
            jugadores_merge["nombre"] = jugadores_merge["name"]
        if "nombre" in jugadores_merge.columns:
            jugadores_merge = jugadores_merge[["id", "nombre"]]
            jugadores_merge = jugadores_merge.rename(columns={
                "id": "jugador_id",
                "nombre": "nombre_jugador"
            })
            datos = datos.merge(jugadores_merge, on="jugador_id", how="left")
if "puntuacion" in datos.columns:
    datos["puntuacion"] = pd.to_numeric(
        datos["puntuacion"], errors="coerce"
    ).fillna(0)
else:
    datos["puntuacion"] = 0
if "posicion" in datos.columns:
    datos["posicion"] = pd.to_numeric(
        datos["posicion"], errors="coerce"
    )
else:
    datos["posicion"] = pd.NA
if "tipo_juego" not in datos.columns:
    datos["tipo_juego"] = ""
if "temporada" not in datos.columns:
    datos["temporada"] = ""
datos["tipo_juego"] = datos["tipo_juego"].fillna("").astype(str).str.strip().str.upper()
datos["temporada"] = datos["temporada"].fillna("").astype(str).str.strip()
if "nombre_jugador" not in datos.columns:
    datos["nombre_jugador"] = "Jugador"
else:
    datos["nombre_jugador"] = datos["nombre_jugador"].fillna("Jugador").astype(str)
if "jugador_id" not in datos.columns:
    datos["jugador_id"] = ""
if "jugador_seleccionado" not in st.session_state:
    st.session_state.jugador_seleccionado = None
# En móvil el nombre es un enlace HTML, no un botón de Streamlit.
# Así la fila nunca se apila ni crece de tamaño.
if "jugador_id" in st.query_params:
    st.session_state.jugador_seleccionado = str(st.query_params["jugador_id"])
def ordenar_temporada(valor):
    try:
        for parte in str(valor).split():
            if parte.isdigit():
                return int(parte)
        return 9999
    except Exception:
        return 9999
def obtener_temporadas():
    if "temporada" not in df_partidas.columns:
        return []
    temporadas = (
        df_partidas["temporada"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )
    return sorted(temporadas, key=ordenar_temporada)
def crear_ranking(tipo_juego, temporada):
    df = datos.copy()
    df = df[
        (df["tipo_juego"] == tipo_juego) &
        (df["temporada"] == temporada)
    ].copy()
    if df.empty:
        return pd.DataFrame()
    df = df.drop_duplicates(subset=["partida_id", "jugador_id"]).copy()
    df["puntuacion"] = pd.to_numeric(
        df["puntuacion"], errors="coerce"
    ).fillna(0)
    df["posicion"] = pd.to_numeric(
        df["posicion"], errors="coerce"
    )
    ranking = (
        df.groupby(["jugador_id", "nombre_jugador"], as_index=False)
        .agg(
            Puntos=("puntuacion", "sum"),
            Partidas=("partida_id", "nunique"),
            Media=("puntuacion", "mean"),
            PuntuacionMaxima=("puntuacion", "max")
        )
    )
    ganadas = (
        df[df["posicion"] == 1]
        .groupby("jugador_id")["partida_id"]
        .nunique()
        .reset_index(name="Ganadas")
    )
    ranking = ranking.merge(ganadas, on="jugador_id", how="left")
    ranking["Ganadas"] = ranking["Ganadas"].fillna(0).astype(int)
    ranking["Winrate"] = (
        ranking["Ganadas"] / ranking["Partidas"] * 100
    ).fillna(0).round(1)
    posiciones = (
        df.groupby("jugador_id")
        .agg(SumaPosiciones=("posicion", "sum"))
        .reset_index()
    )
    ranking = ranking.merge(posiciones, on="jugador_id", how="left")
    ranking["MediaPosicion"] = (
        ranking["SumaPosiciones"] / ranking["Partidas"]
    ).round(2)
    ranking["Puntos"] = ranking["Puntos"].round().astype(int)
    ranking["Media"] = ranking["Media"].round(1)
    ranking["PuntuacionMaxima"] = ranking["PuntuacionMaxima"].round().astype(int)
    ranking["MediaPosicion"] = ranking["MediaPosicion"].fillna(0).round(2)
    ranking = ranking.sort_values(
        "Puntos", ascending=False, kind="mergesort"
    ).reset_index(drop=True)
    ranking["Posición"] = ranking.index + 1
    return ranking[[
        "Posición", "jugador_id", "nombre_jugador", "Puntos",
        "Partidas", "Ganadas", "Winrate", "Media",
        "PuntuacionMaxima", "MediaPosicion"
    ]]
def es_dispositivo_movil():
    try:
        user_agent = st.context.headers.get("User-Agent", "").lower()
    except Exception:
        user_agent = ""
    return any(x in user_agent for x in [
        "android", "iphone", "ipad", "ipod", "mobile"
    ])
def mostrar_indicadores(jugador_id, tipo_juego, temporada):
    ranking = crear_ranking(tipo_juego, temporada)
    if ranking.empty:
        st.info("No hay datos para esta temporada.")
        return
    fila_jugador = ranking[
        ranking["jugador_id"].astype(str) == str(jugador_id)
    ]
    if fila_jugador.empty:
        st.info(f"Este jugador no tiene partidas de {tipo_juego} en esta temporada.")
        return
    fila = fila_jugador.iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Puntos", int(fila["Puntos"]))
    with c2:
        st.metric("Partidas", int(fila["Partidas"]))
    with c3:
        st.metric("Posición", int(fila["Posición"]))
    c4, c5, c6 = st.columns(3)
    with c4:
        st.metric("WINRATE", f"{float(fila['Winrate']):.1f}%")
    with c5:
        st.metric("Ganadas", int(fila["Ganadas"]))
    with c6:
        st.metric("Media posición", f"{float(fila['MediaPosicion']):.2f}")
    c7, c8 = st.columns(2)
    with c7:
        st.metric("Puntuación media", f"{float(fila['Media']):.1f}")
    with c8:
        st.metric("Puntuación máxima", int(fila["PuntuacionMaxima"]))
def mostrar_distribucion_posiciones(jugador_id, tipo_juego, temporada):
    df = datos[
        (datos["jugador_id"].astype(str) == str(jugador_id)) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()
    if df.empty:
        return
    df = df.drop_duplicates(subset=["partida_id", "jugador_id"])
    df["posicion"] = pd.to_numeric(df["posicion"], errors="coerce")
    valores = [int((df["posicion"] == i).sum()) for i in range(1, 6)]
    st.subheader("📊 Posiciones")
    tabla = pd.DataFrame({
        "🥇 1ª": [valores[0]],
        "🥈 2ª": [valores[1]],
        "🥉 3ª": [valores[2]],
        "4ª": [valores[3]],
        "5ª": [valores[4]]
    })
    st.table(tabla)
def mostrar_historial(jugador_id, tipo_juego, temporada):
    jugador_id_texto = str(jugador_id)
    datos_jugador = datos[
        (datos["jugador_id"].astype(str) == jugador_id_texto) &
        (datos["tipo_juego"] == tipo_juego) &
        (datos["temporada"] == temporada)
    ].copy()
    if datos_jugador.empty:
        st.info(f"Este jugador no tiene partidas de {tipo_juego} en esta temporada.")
        return
    ids_partidas = datos_jugador["partida_id"].dropna().unique()
    partidas_jugador = datos[
        datos["partida_id"].isin(ids_partidas)
    ].copy()
    partidas_jugador = partidas_jugador[
        (partidas_jugador["tipo_juego"] == tipo_juego) &
        (partidas_jugador["temporada"] == temporada)
    ].copy()
    if partidas_jugador.empty:
        st.info("No hay historial.")
        return
    partidas_info = (
        partidas_jugador[["partida_id", "fecha"]]
        .drop_duplicates()
        .copy()
    )
    partidas_info["fecha_orden"] = pd.to_datetime(
        partidas_info["fecha"], errors="coerce"
    )
    partidas_info = partidas_info.sort_values(
        "fecha_orden", ascending=False
    )
    for _, partida in partidas_info.iterrows():
        partida_id = partida["partida_id"]
        datos_partida = partidas_jugador[
            partidas_jugador["partida_id"] == partida_id
        ].copy()
        if datos_partida.empty:
            continue
        datos_partida = datos_partida.sort_values(
            "posicion", ascending=True, na_position="last"
        )
        try:
            fecha_formateada = pd.to_datetime(partida["fecha"]).strftime("%d/%m/%Y")
        except Exception:
            fecha_formateada = str(partida["fecha"])
        nombre_partida = ""
        if "nombre_partida" in datos_partida.columns:
            valores = datos_partida["nombre_partida"].dropna()
            if not valores.empty:
                nombre_partida = str(valores.iloc[0]).strip()
        if not nombre_partida and "nombre" in datos_partida.columns:
            valores = datos_partida["nombre"].dropna()
            if not valores.empty:
                nombre_partida = str(valores.iloc[0]).strip()
        titulo = (
            f"{fecha_formateada} · {nombre_partida}"
            if nombre_partida else fecha_formateada
        )
        st.markdown(
            f'<div class="match-header">{titulo}</div>',
            unsafe_allow_html=True
        )
        h1, h2, h3 = st.columns([3, 1, 1])
        with h1:
            st.markdown('<div class="match-col-header">JUGADOR</div>', unsafe_allow_html=True)
        with h2:
            st.markdown('<div class="match-col-header">PUNTOS</div>', unsafe_allow_html=True)
        with h3:
            st.markdown('<div class="match-col-header">POS.</div>', unsafe_allow_html=True)
        for _, fila in datos_partida.iterrows():
            nombre = str(fila.get("nombre_jugador", "Jugador"))
            try:
                puntuacion = int(round(float(fila.get("puntuacion", 0))))
            except Exception:
                puntuacion = 0
            try:
                posicion = int(float(fila.get("posicion", "")))
            except Exception:
                posicion = ""
            seleccionado = str(fila["jugador_id"]) == jugador_id_texto
            clase = "match-cell-selected" if seleccionado else "match-cell"
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f'<div class="{clase}">{nombre}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="{clase}" style="text-align:center">{puntuacion}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="{clase}" style="text-align:center">{posicion}</div>', unsafe_allow_html=True)
def mostrar_ficha(jugador_id):
    cab1, cab2 = st.columns([3, 1])
    with cab1:
        st.title("🀄 Ficha del jugador")
    with cab2:
        if st.button("← Volver", key="volver_arriba", use_container_width=True):
            st.session_state.jugador_seleccionado = None
            st.query_params.clear()
            st.rerun()
    jugador_id_texto = str(jugador_id)
    nombre_jugador = "Jugador"
    if not df_jugadores.empty and "id" in df_jugadores.columns:
        encontrados = df_jugadores[
            df_jugadores["id"].astype(str) == jugador_id_texto
        ]
        if not encontrados.empty:
            if "nombre" in encontrados.columns:
                nombre_jugador = str(encontrados.iloc[0]["nombre"])
            elif "name" in encontrados.columns:
                nombre_jugador = str(encontrados.iloc[0]["name"])
    if nombre_jugador == "Jugador":
        encontrados = datos[
            datos["jugador_id"].astype(str) == jugador_id_texto
        ]
        if encontrados.empty:
            st.error("No se ha encontrado el jugador.")
            return
        nombre_jugador = str(encontrados.iloc[0]["nombre_jugador"])
    st.markdown(
        f'<div class="player-title">{nombre_jugador}</div>',
        unsafe_allow_html=True
    )
    temporadas_ficha = obtener_temporadas()
    if not temporadas_ficha:
        st.warning("No se han encontrado temporadas en la tabla de partidas.")
        return
    tab_mcr, tab_riichi = st.tabs(["🀄 MCR", "🀄 RIICHI"])
    with tab_mcr:
        tabs = st.tabs(temporadas_ficha)
        for temporada, tab in zip(temporadas_ficha, tabs):
            with tab:
                st.subheader(temporada)
                mostrar_indicadores(jugador_id, "MCR", temporada)
                st.divider()
                mostrar_distribucion_posiciones(jugador_id, "MCR", temporada)
                st.divider()
                st.subheader("📋 Historial")
                mostrar_historial(jugador_id, "MCR", temporada)
    with tab_riichi:
        tabs = st.tabs(temporadas_ficha)
        for temporada, tab in zip(temporadas_ficha, tabs):
            with tab:
                st.subheader(temporada)
                mostrar_indicadores(jugador_id, "RIICHI", temporada)
                st.divider()
                mostrar_distribucion_posiciones(jugador_id, "RIICHI", temporada)
                st.divider()
                st.subheader("📋 Historial")
                mostrar_historial(jugador_id, "RIICHI", temporada)
    st.divider()
    if st.button("← Volver al ranking", key="volver_abajo", use_container_width=True):
        st.session_state.jugador_seleccionado = None
        st.query_params.clear()
        st.rerun()
def limpiar_criterio(criterio):
    return (
        criterio.replace("📈 ", "")
        .replace("🏆 ", "")
        .replace("🎯 ", "")
    )
def mostrar_ranking(tipo_juego, temporada):
    ranking = crear_ranking(tipo_juego, temporada)
    if ranking.empty:
        st.info(f"No hay datos de {tipo_juego} para {temporada}.")
        return

    total_jugadores = len(ranking)

criterio = st.radio( 
    "Ordenar ranking por:", 
    ["📈 Winrate", "🏆 Puntos", "🎯 Media posición"], 
    index=0, 
    horizontal=True, 
    key=f"criterio_{tipo_juego}_{temporada}" 
)

if criterio == "📈 Winrate":

    if criterio == "📈 Winrate":
        columna_orden = "Winrate"
        ascendente = False
    elif criterio == "🏆 Puntos":
        columna_orden = "Puntos"
        ascendente = False
    else:
        columna_orden = "MediaPosicion"
        ascendente = True

    ranking = ranking.sort_values(
        columna_orden,
        ascending=ascendente,
        kind="mergesort"
    ).reset_index(drop=True)
    ranking["Posición"] = ranking.index + 1

    nombre_valor = limpiar_criterio(criterio)

    st.markdown(
        f'<div style="font-size:.92rem;font-weight:800;margin:8px 0 7px 2px;">Ranking por {nombre_valor}</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # MÓVIL: TABLA HTML COMPLETA EN UNA SOLA FILA POR JUGADOR
    # No usamos st.button ni st.columns aquí.
    # =====================================================
    if es_dispositivo_movil():
        filas_html = [
            f'''<div class="mobile-ranking-header">
                    <div style="text-align:center;">POS.</div>
                    <div>JUGADOR</div>
                    <div style="text-align:right;">{nombre_valor.upper()}</div>
                </div>'''
        ]

        for _, fila in ranking.iterrows():
            posicion = int(fila["Posición"])
            jugador_id = str(fila["jugador_id"])
            nombre = html.escape(str(fila["nombre_jugador"]).strip()[:15])

            if columna_orden == "Winrate":
                valor = f"{float(fila['Winrate']):.1f}%"
            elif columna_orden == "Puntos":
                valor = f"{int(fila['Puntos'])}"
            else:
                valor = f"{float(fila['MediaPosicion']):.2f}"

            if posicion == 1:
                simbolo = "🥇"
            elif posicion == 2:
                simbolo = "🥈"
            elif posicion == 3:
                simbolo = "🥉"
            else:
                simbolo = str(posicion)

            # El ID se codifica para que cualquier UUID/valor especial sea seguro en la URL.
            jugador_url = urllib.parse.quote(jugador_id, safe="")

            filas_html.append(
                f'''<a class="mobile-ranking-row" href="?jugador_id={jugador_url}">
                        <div class="mobile-pos">{simbolo}</div>
                        <div class="mobile-name">{nombre}</div>
                        <div class="mobile-value">{valor}</div>
                    </a>'''
            )

        st.markdown(
            '<div class="mobile-ranking">' + ''.join(filas_html) + '</div>',
            unsafe_allow_html=True
        )
        return

    # =====================================================
    # ESCRITORIO: TABLA COMPLETA
    # =====================================================
    filas_html = [
        '''<div class="ranking-header">
            <div style="text-align:center;">Pos.</div>
            <div>Jugador</div>
            <div style="text-align:center;">Puntos</div>
            <div style="text-align:center;">Part.</div>
            <div style="text-align:center;">Gan.</div>
            <div style="text-align:center;">Winrate</div>
            <div style="text-align:center;">Media</div>
            <div style="text-align:center;">Máx.</div>
            <div style="text-align:center;">Media pos.</div>
        </div>'''
    ]

    for _, fila in ranking.iterrows():
        posicion = int(fila["Posición"])
        jugador_id = str(fila["jugador_id"])
        nombre = html.escape(str(fila["nombre_jugador"]).strip())
        puntos = int(fila["Puntos"])
        partidas = int(fila["Partidas"])
        ganadas = int(fila["Ganadas"])
        winrate = float(fila["Winrate"])
        media = float(fila["Media"])
        maxima = int(fila["PuntuacionMaxima"])
        media_pos = float(fila["MediaPosicion"])
        jugador_url = urllib.parse.quote(jugador_id, safe="")

        filas_html.append(
            f'''<div class="ranking-row">
                <div class="ranking-cell ranking-position">{posicion}</div>
                <div class="ranking-cell">
                    <a class="ranking-player-link" href="?jugador_id={jugador_url}">{nombre}</a>
                </div>
                <div class="ranking-cell ranking-value">{puntos}</div>
                <div class="ranking-cell ranking-value">{partidas}</div>
                <div class="ranking-cell ranking-value">{ganadas}</div>
                <div class="ranking-cell ranking-value">{winrate:.1f}%</div>
                <div class="ranking-cell ranking-value">{media:.1f}</div>
                <div class="ranking-cell ranking-value">{maxima}</div>
                <div class="ranking-cell ranking-value">{media_pos:.2f}</div>
            </div>'''
        )

    st.markdown(
        '<div class="ranking-box">' + ''.join(filas_html) + '</div>',
        unsafe_allow_html=True
    )

if st.session_state.jugador_seleccionado is not None:
    mostrar_ficha(st.session_state.jugador_seleccionado)
    st.stop()
if os.path.exists(RUTA_LOGO):
    import base64
    with open(RUTA_LOGO, "rb") as archivo_logo:
        logo_base64 = base64.b64encode(archivo_logo.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width:100%;height:auto;display:block;">'
else:
    logo_html = '<div style="font-size:2.2rem;text-align:center;">🀄</div>'

st.markdown(
    f'''<div class="main-header">
        <div class="main-header-logo">{logo_html}</div>
        <div class="main-header-title">
            <div style="font-size:2rem;line-height:1.08;font-weight:800;color:#151515;">Liga Mahjong Madrid</div>
            <div class="main-header-subtitle">Ranking de jugadores · MCR y RIICHI</div>
        </div>
    </div>''',
    unsafe_allow_html=True
)
temporadas = obtener_temporadas()
if not temporadas:
    st.warning("No se han encontrado temporadas en la tabla de partidas.")
    st.stop()
tab_mcr, tab_riichi = st.tabs(["🀄 MCR", "🀄 RIICHI"])
with tab_mcr:
    tabs_mcr = st.tabs(temporadas)
    for temporada, tab_temporada in zip(temporadas, tabs_mcr):
        with tab_temporada:
            st.subheader(temporada)
            mostrar_ranking("MCR", temporada)
with tab_riichi:
    tabs_riichi = st.tabs(temporadas)
    for temporada, tab_temporada in zip(temporadas, tabs_riichi):
        with tab_temporada:
            st.subheader(temporada)
            mostrar_ranking("RIICHI", temporada)
