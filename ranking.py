import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import os
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
   MAHJONG MADRID - DISEÑO RESPONSIVE
   Esta sección controla la presentación. La lógica y cálculos
   del ranking permanecen sin cambios.
========================================================= */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

.stApp { background: #ffffff; }

.block-container {
    width: 100% !important;
    max-width: 1080px !important;
    padding: 1.2rem 1.2rem 2.5rem 1.2rem !important;
    box-sizing: border-box !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] .main,
[data-testid="stAppViewContainer"] .block-container {
    max-width: 100% !important;
    overflow-x: hidden !important;
}

h1, h2, h3 { color: #151515 !important; }
h1 { font-size: 2rem !important; line-height: 1.08 !important; font-weight: 800 !important; margin-bottom: .15rem !important; }
h2 { font-size: 1.4rem !important; line-height: 1.15 !important; }
h3 { font-size: 1.1rem !important; }

.stButton > button {
    width: 100% !important;
    min-height: 40px !important;
    height: auto !important;
    border-radius: 8px !important;
    border: 1px solid #d6d6d6 !important;
    background: #ffffff !important;
    color: #151515 !important;
    font-size: .9rem !important;
    font-weight: 600 !important;
    line-height: 1.15 !important;
    padding: 6px 8px !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    box-shadow: none !important;
}
.stButton > button:hover { border-color: #b40000 !important; color: #b40000 !important; }

.stTabs [data-baseweb="tab-list"] { width: 100% !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    justify-content: center !important;
    font-size: .95rem !important;
    font-weight: 700 !important;
    min-height: 46px !important;
    padding: 6px 8px !important;
}

/* Selector de orden */
div[role="radiogroup"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
    width: 100% !important;
}
div[role="radiogroup"] label {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    border: 1px solid #d8d8d8 !important;
    border-radius: 8px !important;
    padding: 7px 9px !important;
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
.main-header-subtitle { color: #777777; font-size: .9rem; line-height: 1.2; margin-top: 2px; }

/* Ranking escritorio */
.ranking-box {
    width: 100%;
    border: 1px solid #dedede;
    border-radius: 10px;
    overflow: hidden;
    background: #ffffff;
    box-sizing: border-box;
}
.ranking-header {
    display: grid;
    grid-template-columns: .60fr 3.00fr .95fr .75fr .75fr 1.00fr .80fr .80fr 1.00fr;
    gap: 5px;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    background: #b90000;
    color: #ffffff;
    padding: 11px 9px;
    font-weight: 800;
    font-size: .78rem;
    line-height: 1.05;
}
.ranking-header > div { min-width: 0; }
.ranking-header > div:not(:nth-child(2)) { text-align: center; }
.ranking-position { text-align: center; font-weight: 800; font-size: .92rem; }
.ranking-value { text-align: center; font-weight: 700; font-size: .86rem; white-space: nowrap; }

/* Ficha */
.player-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #111111;
    margin: 8px 0 12px 0;
    overflow-wrap: anywhere;
}
.match-header {
    background: #f2f7f3;
    color: #17612e;
    border-left: 4px solid #17612e;
    padding: 9px 12px;
    border-radius: 7px;
    margin-top: 13px;
    margin-bottom: 5px;
    font-weight: 700;
    overflow-wrap: anywhere;
}
.match-col-header { font-size: .76rem; color: #666666; font-weight: 700; padding: 4px 5px; }
.match-cell { background: #ffffff; border-bottom: 1px solid #eeeeee; padding: 7px 5px; font-size: .88rem; overflow-wrap: anywhere; }
.match-cell-selected { background: #fff8d9; border-bottom: 1px solid #eadf9c; padding: 7px 5px; font-weight: 700; font-size: .88rem; overflow-wrap: anywhere; }

/* Métricas */
[data-testid="stMetric"] { border: 1px solid #e1e1e1 !important; border-radius: 9px !important; padding: 9px !important; background: #fafafa !important; min-width: 0 !important; }
[data-testid="stMetricLabel"] { font-size: .72rem !important; }
[data-testid="stMetricValue"] { font-size: 1.25rem !important; }

[data-testid="stHorizontalBlock"] { width: 100% !important; max-width: 100% !important; min-width: 0 !important; }
[data-testid="column"] { min-width: 0 !important; }

/* Cada fila móvil se encierra en un contenedor propio.
   Esto evita que Streamlit apile las columnas en vertical. */
[class*="st-key-mobile-row-"] [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
}
[class*="st-key-mobile-row-"] [data-testid="column"] {
    min-width: 0 !important;
    overflow: hidden !important;
}

/* Móvil */
@media (max-width: 700px) {
    .block-container { max-width: 100% !important; padding: .55rem .45rem 1.5rem .45rem !important; }
    h1 { font-size: 1.42rem !important; }
    h2 { font-size: 1.18rem !important; }
    h3 { font-size: 1.02rem !important; }
    .main-header { gap: 10px; margin-bottom: 6px; }
    .main-header-logo { width: 58px; min-width: 58px; }
    .main-header-subtitle { font-size: .76rem; }
    .stTabs [data-baseweb="tab"] { font-size: .82rem !important; min-height: 42px !important; padding: 5px 4px !important; }
    div[role="radiogroup"] { gap: 4px !important; }
    div[role="radiogroup"] label { padding: 6px 4px !important; font-size: .72rem !important; }

    .mobile-ranking-header {
        display: grid;
        grid-template-columns: .55fr 3.15fr .90fr;
        gap: 4px;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
        background: #b90000;
        color: #ffffff;
        border-radius: 8px 8px 0 0;
        padding: 10px 7px;
        font-size: .70rem;
        line-height: 1;
        font-weight: 800;
    }
    .mobile-ranking-header > div { min-width: 0; }
    .mobile-ranking-header > div:first-child,
    .mobile-ranking-header > div:last-child { text-align: center; }
    .mobile-ranking-header > div:nth-child(2) { text-align: left; }

    .mobile-ranking-row {
        display: grid;
        grid-template-columns: .55fr 3.15fr .90fr;
        gap: 4px;
        align-items: center;
        width: 100%;
        min-height: 46px;
        box-sizing: border-box;
        padding: 2px 5px;
        border: 1px solid #e1e1e1;
        border-top: 0;
        background: #ffffff;
    }
    .mobile-position { text-align: center; font-size: .98rem; line-height: 1; font-weight: 800; }
    .mobile-name-button { min-width: 0 !important; width: 100% !important; }
    .mobile-name-button .stButton > button,
    .mobile-name-button button {
        width: 100% !important;
        min-height: 42px !important;
        height: auto !important;
        border: 0 !important;
        background: transparent !important;
        color: #111111 !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 4px 2px !important;
        margin: 0 !important;
        font-size: .82rem !important;
        line-height: 1 !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .mobile-name-button .stButton > button:hover,
    .mobile-name-button button:hover { color: #b40000 !important; }
    .mobile-main-value { text-align: right; padding-right: 2px; font-size: .82rem; line-height: 1; font-weight: 800; white-space: nowrap; }

    [data-testid="stMetric"] { padding: 6px 5px !important; }
    [data-testid="stMetricLabel"] { font-size: .64rem !important; }
    [data-testid="stMetricValue"] { font-size: 1rem !important; }
    .stButton > button { min-height: 40px !important; font-size: .86rem !important; padding: 5px 6px !important; }
    .match-cell, .match-cell-selected { font-size: .82rem; padding: 6px 4px; }
}

@media (max-width: 380px) {
    .block-container { padding-left: .3rem !important; padding-right: .3rem !important; }
    .main-header-logo { width: 50px; min-width: 50px; }
    h1 { font-size: 1.28rem !important; }
    .mobile-ranking-header, .mobile-ranking-row { grid-template-columns: .50fr 3.20fr .85fr; }
    .mobile-name-button .stButton > button, .mobile-name-button button { font-size: .80rem !important; }
    .mobile-main-value { font-size: .78rem; }
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

    criterio = st.radio(
        "Ordenar ranking por:",
        ["📈 Winrate", "🏆 Puntos", "🎯 Media posición"],
        index=0,
        horizontal=True,
        key=f"criterio_{tipo_juego}_{temporada}"
    )

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
        f'<div style="font-size:.95rem;font-weight:800;margin:8px 0 7px 2px;">Ranking por {nombre_valor}</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # MÓVIL: POSICIÓN | JUGADOR | VALOR
    # =====================================================
    if es_dispositivo_movil():
        st.markdown(
            f'''<div class="mobile-ranking-header">
                <div>POS.</div>
                <div>JUGADOR</div>
                <div>{nombre_valor.upper()}</div>
            </div>''',
            unsafe_allow_html=True
        )

        for _, fila in ranking.iterrows():
            posicion = int(fila["Posición"])
            jugador_id = fila["jugador_id"]
            nombre = str(fila["nombre_jugador"]).strip()

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

            # Contenedor propio para que estas 3 columnas permanezcan
            # siempre en una sola línea también en teléfonos.
            with st.container(key=f"mobile-row-{tipo_juego}-{temporada}-{jugador_id}"):
                c1, c2, c3 = st.columns(
                    [0.55, 3.15, 0.90],
                    gap="small"
                )

                with c1:
                    st.markdown(
                        f'''<div class="mobile-position" style="min-height:46px;display:flex;align-items:center;justify-content:center;border-bottom:1px solid #e1e1e1;">{simbolo}</div>''',
                        unsafe_allow_html=True
                    )

                with c2:
                    st.markdown('<div class="mobile-name-button">', unsafe_allow_html=True)
                    if st.button(
                        nombre[:15],
                        key=f"mobile_{tipo_juego}_{temporada}_{jugador_id}",
                        use_container_width=True
                    ):
                        st.session_state.jugador_seleccionado = str(jugador_id)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                with c3:
                    st.markdown(
                        f'''<div class="mobile-main-value" style="min-height:46px;display:flex;align-items:center;justify-content:flex-end;border-bottom:1px solid #e1e1e1;">{valor}</div>''',
                        unsafe_allow_html=True
                    )

        return

    # =====================================================
    # ESCRITORIO: TABLA COMPLETA
    # =====================================================
    st.markdown('<div class="ranking-box">', unsafe_allow_html=True)

    st.markdown('''
    <div class="ranking-header">
        <div>Pos.</div>
        <div>Jugador</div>
        <div>Puntos</div>
        <div>Part.</div>
        <div>Gan.</div>
        <div>Winrate</div>
        <div>Media</div>
        <div>Máx.</div>
        <div>Media pos.</div>
    </div>
    ''', unsafe_allow_html=True)

    for _, fila in ranking.iterrows():
        posicion = int(fila["Posición"])
        jugador_id = fila["jugador_id"]
        nombre = str(fila["nombre_jugador"]).strip()
        puntos = int(fila["Puntos"])
        partidas = int(fila["Partidas"])
        ganadas = int(fila["Ganadas"])
        winrate = float(fila["Winrate"])
        media = float(fila["Media"])
        maxima = int(fila["PuntuacionMaxima"])
        media_pos = float(fila["MediaPosicion"])

        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(
            [0.60, 3.00, 0.95, 0.75, 0.75, 1.00, 0.80, 0.80, 1.00],
            gap="small"
        )

        with c1:
            st.markdown(
                f'<div class="ranking-position">{posicion}</div>',
                unsafe_allow_html=True
            )

        with c2:
            if st.button(
                nombre,
                key=f"pc_{tipo_juego}_{temporada}_{jugador_id}",
                use_container_width=True
            ):
                st.session_state.jugador_seleccionado = str(jugador_id)
                st.rerun()

        with c3:
            st.markdown(f'<div class="ranking-value">{puntos}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="ranking-value">{partidas}</div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="ranking-value">{ganadas}</div>', unsafe_allow_html=True)
        with c6:
            st.markdown(f'<div class="ranking-value">{winrate:.1f}%</div>', unsafe_allow_html=True)
        with c7:
            st.markdown(f'<div class="ranking-value">{media:.1f}</div>', unsafe_allow_html=True)
        with c8:
            st.markdown(f'<div class="ranking-value">{maxima}</div>', unsafe_allow_html=True)
        with c9:
            st.markdown(f'<div class="ranking-value">{media_pos:.2f}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

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
