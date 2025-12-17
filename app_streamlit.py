"""Application Streamlit - Météo & IA."""
import streamlit as st
import pandas as pd
from pathlib import Path

# Import des modules locaux
from utils.data import load_data, filter_data
from utils.charts import create_meteo_map, create_line_chart, create_histogram
from utils.chatbot import DataChatbot

# --- Configuration ---
st.set_page_config(
    page_title="Météo Data Explorer",
    page_icon="🌤️",
    layout="wide"
)

# --- Chargement des données ---
DATA_DIR = Path("data/processed")
files = sorted(DATA_DIR.glob("*.parquet"), key=lambda x: x.stat().st_mtime, reverse=True)

if not files:
    st.error("⚠️ Aucun fichier de données trouvé dans `data/processed/`. Veuillez copier le fichier du TP2.")
    st.stop()

# Chargement du fichier le plus récent
df = load_data(files[0])

# --- Sidebar : Filtres & Options ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Sélecteur de date pour la carte
    if 'date' in df.columns:
        dates = sorted(df['date'].unique())
        selected_date = st.select_slider(
            "📅 Date de prévision",
            options=dates,
            format_func=lambda x: pd.to_datetime(x).strftime("%d/%m/%Y")
        )
    
    st.markdown("---")
    
    # Filtre par ville
    cities = sorted(df['original_city_name'].unique()) if 'original_city_name' in df.columns else []
    selected_cities = st.multiselect("🏙️ Filtrer par ville", options=cities, default=["Avignon"] if "Avignon" in cities else [])
    
    filters = {}
    if selected_cities:
        filters['original_city_name'] = selected_cities

# Application des filtres
df_filtered = filter_data(df, filters)

# --- Contenu Principal ---
st.title("🌤️ Météo Data & IA Explorer")

# Création des onglets
tab_viz, tab_data, tab_chat = st.tabs(["📊 Visualisations", "🗃️ Données Brutes", "🤖 Assistant IA"])

# --- ONGLET 1 : VISUALISATIONS ---
with tab_viz:
    # 1. KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Villes suivies", df['original_city_name'].nunique())
    with col2: st.metric("Température Moy.", f"{df_filtered['temperature_max'].mean():.1f}°C")
    with col3: st.metric("Température Max", f"{df_filtered['temperature_max'].max():.1f}°C")
    with col4: st.metric("Enregistrements", len(df_filtered))

    st.markdown("---")

    # 2. Carte Interactive (Basée sur la date sélectionnée dans la sidebar)
    st.subheader(f"🗺️ Carte des températures ({pd.to_datetime(selected_date).strftime('%d/%m/%Y')})")
    
    # On filtre le DF global sur la date choisie pour la carte
    df_map = df[df['date'] == selected_date]
    if not df_map.empty:
        fig_map = create_meteo_map(df_map, pd.to_datetime(selected_date).strftime("%d/%m/%Y"))
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Pas de données pour cette date.")

    # 3. Graphiques par ville (Basés sur le filtre villes)
    if selected_cities:
        st.markdown("---")
        st.subheader("📈 Prévisions détaillées")
        cols = st.columns(min(len(selected_cities), 2)) # Affichage sur 2 colonnes max
        
        for idx, city in enumerate(selected_cities):
            # On prend les données complètes de la ville (toutes dates)
            df_city = df[df['original_city_name'] == city]
            fig = create_line_chart(df_city, city)
            
            with cols[idx % 2]:
                st.plotly_chart(fig, use_container_width=True)

# --- ONGLET 2 : DONNÉES ---
with tab_data:
    st.subheader("Explorateur de données")
    st.dataframe(df_filtered, use_container_width=True)

# --- ONGLET 3 : CHATBOT ---
with tab_chat:
    st.subheader("🤖 Discutez avec vos données météo")
    
    # Initialisation de la session
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = DataChatbot(df) # On passe le DF complet à l'IA
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Je connais toutes les prévisions. Posez-moi une question (ex: 'Quelle ville sera la plus chaude demain ?')"}]

    # Affichage de l'historique
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de saisie
    if prompt := st.chat_input("Votre question..."):
        # Message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Réponse IA
        with st.chat_message("assistant"):
            with st.spinner("Analyse des données en cours..."):
                response = st.session_state.chatbot.chat(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Bouton reset
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.chatbot.reset()
        st.session_state.messages = []
        st.rerun()