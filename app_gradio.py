"""Application Gradio - Météo & IA."""
import gradio as gr
import pandas as pd
from pathlib import Path

# Import des modules locaux
from utils.data import load_data
from utils.charts import create_meteo_map, create_line_chart, create_histogram
from utils.chatbot import DataChatbot

# --- Chargement des données ---
DATA_DIR = Path("data/processed")
files = sorted(DATA_DIR.glob("*.parquet"), key=lambda x: x.stat().st_mtime, reverse=True)

if not files:
    raise FileNotFoundError("Aucun fichier de données trouvé dans `data/processed/`.")

df = load_data(files[0])

# Initialisation globale du chatbot (pour cet exemple simple)
chatbot_engine = DataChatbot(df)

# --- Fonctions de rappel (Callbacks) ---

def get_kpi_markdown(city_filter=None):
    """Génère le texte Markdown pour les KPIs."""
    subset = df
    if city_filter:
        subset = df[df['original_city_name'].isin(city_filter)]
    
    nb_villes = subset['original_city_name'].nunique()
    temp_moy = subset['temperature_max'].mean()
    temp_max = subset['temperature_max'].max()
    nb_rows = len(subset)
    
    return f"""
    ### 📊 Indicateurs Clés
    | Villes | Temp. Moyenne | Temp. Max | Enregistrements |
    | :---: | :---: | :---: | :---: |
    | **{nb_villes}** | **{temp_moy:.1f}°C** | **{temp_max:.1f}°C** | **{nb_rows}** |
    """

def update_map(date_str):
    """Met à jour la carte selon la date sélectionnée."""
    # Convertir la date string (ex: '2025-12-17') en format compatible
    try:
        target_date = pd.to_datetime(date_str)
        df_map = df[df['date'] == target_date]
        
        if df_map.empty:
            return None
            
        fig = create_meteo_map(df_map, target_date.strftime("%d/%m/%Y"))
        return fig
    except Exception as e:
        print(f"Erreur update_map: {e}")
        return None

def update_city_chart(cities):
    """Met à jour le graphique des prévisions pour les villes sélectionnées."""
    if not cities:
        return None
    
    # Pour Gradio, on va combiner les courbes sur un seul graphique si possible
    # ou juste prendre la première ville pour simplifier l'affichage
    # Ici, on filtre le dataframe pour toutes les villes sélectionnées
    df_cities = df[df['original_city_name'].isin(cities)].sort_values('date')
    
    # On utilise Plotly Express pour faire un graphique multi-lignes
    import plotly.express as px
    fig = px.line(
        df_cities, 
        x='date', 
        y='temperature_max', 
        color='original_city_name',
        title="Comparaison des Températures Max",
        markers=True
    )
    fig.update_layout(template="plotly_white")
    return fig

def filter_dataframe(cities):
    """Filtre le tableau de données."""
    if not cities:
        return df.head(100)
    return df[df['original_city_name'].isin(cities)]

def chat_response(message, history):
    """Wrapper pour le chatbot."""
    return chatbot_engine.chat(message)

# --- Interface Utilisateur (Gradio Blocks) ---

# Préparation des options pour les filtres
available_cities = sorted(df['original_city_name'].unique().tolist()) if 'original_city_name' in df.columns else []
available_dates = sorted(df['date'].unique())
date_str_list = [pd.to_datetime(d).strftime("%Y-%m-%d") for d in available_dates]

with gr.Blocks(title="Météo Data Explorer", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🌤️ Météo Data & IA Explorer (Gradio Edition)")
    
    with gr.Tabs():
        
        # --- ONGLET 1 : Dashboard ---
        with gr.TabItem("📊 Dashboard"):
            
            # KPIs
            kpi_output = gr.Markdown(get_kpi_markdown())
            
            gr.Markdown("---")
            
            with gr.Row():
                # Contrôles
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ Filtres")
                    date_selector = gr.Dropdown(
                        choices=date_str_list, 
                        value=date_str_list[0] if date_str_list else None,
                        label="📅 Date de prévision"
                    )
                    city_selector = gr.Dropdown(
                        choices=available_cities,
                        value=["Avignon"] if "Avignon" in available_cities else None,
                        multiselect=True,
                        label="🏙️ Sélectionner des villes"
                    )
                
                # Carte
                with gr.Column(scale=3):
                    map_output = gr.Plot(label="Carte des Températures")
            
            gr.Markdown("---")
            
            # Graphique Courbe
            chart_output = gr.Plot(label="Prévisions Détaillées")
            
            # Événements (Interactivité)
            # 1. Changer la date met à jour la carte
            date_selector.change(
                fn=update_map,
                inputs=date_selector,
                outputs=map_output
            )
            
            # 2. Changer les villes met à jour le graphique et les KPIs
            city_selector.change(
                fn=update_city_chart,
                inputs=city_selector,
                outputs=chart_output
            ).then(
                fn=get_kpi_markdown,
                inputs=city_selector,
                outputs=kpi_output
            )
            
            # Chargement initial
            app.load(fn=update_map, inputs=date_selector, outputs=map_output)
            app.load(fn=update_city_chart, inputs=city_selector, outputs=chart_output)

        # --- ONGLET 2 : Données ---
        with gr.TabItem("🗃️ Données"):
            gr.Markdown("### Explorateur de données brutes")
            data_filter = gr.Dropdown(choices=available_cities, multiselect=True, label="Filtrer par ville")
            data_output = gr.Dataframe(value=df.head(100), interactive=False)
            
            data_filter.change(fn=filter_dataframe, inputs=data_filter, outputs=data_output)

        # --- ONGLET 3 : Chatbot ---
        with gr.TabItem("🤖 Assistant IA"):
            gr.ChatInterface(
                fn=chat_response,
                examples=["Quelle est la ville la plus chaude ?", "Quelle est la moyenne des températures ?", "Affiche les données pour Paris"],
                title="Assistant Météo",
                description="Posez vos questions sur les données météo."
            )

# Lancement de l'application
if __name__ == "__main__":
    app.launch()