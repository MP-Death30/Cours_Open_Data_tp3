"""Module de visualisations avec Plotly."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_meteo_map(df: pd.DataFrame, date_str: str) -> go.Figure:
    """Crée la carte météo interactive (style TP2)."""
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="temperature_max",
        size="temperature_max",
        size_max=15,
        hover_name="original_city_name",
        hover_data={"temperature_max": True, "temperature_min": True, "latitude": False, "longitude": False},
        color_continuous_scale="RdYlBu_r", # Rouge = Chaud, Bleu = Froid
        zoom=4.5,
        center={"lat": 46.603354, "lon": 1.888334},
        title=f"Températures Max le {date_str}",
        mapbox_style="open-street-map"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

def create_line_chart(df: pd.DataFrame, city: str) -> go.Figure:
    """Crée le graphique de prévisions pour une ville."""
    # Trier par date pour avoir une ligne continue
    df_city = df.sort_values('date')
    
    fig = px.line(
        df_city, 
        x='date', 
        y=['temperature_max', 'temperature_min'],
        title=f"Prévisions pour {city}",
        labels={'value': 'Température (°C)', 'date': 'Date', 'variable': 'Type'},
        markers=True
    )
    fig.update_layout(template="plotly_white")
    return fig

def create_histogram(df: pd.DataFrame, x: str, title: str = "") -> go.Figure:
    """Histogramme générique."""
    fig = px.histogram(
        df, x=x, nbins=30,
        title=title,
        template="plotly_white"
    )
    return fig