"""Module de chargement et préparation des données."""
import duckdb
import pandas as pd
from pathlib import Path
import streamlit as st

@st.cache_data
def load_data(filepath: str | Path) -> pd.DataFrame:
    """
    Charge les données depuis un fichier Parquet.
    Utilise DuckDB pour des performances optimales.
    """
    try:
        con = duckdb.connect()
        # On lit le parquet via DuckDB et on convertit en Pandas
        df = con.execute(f"SELECT * FROM read_parquet('{filepath}')").df()
        con.close()
        
        # Conversion explicite des dates si nécessaire
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

def filter_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Applique des filtres au DataFrame."""
    df_filtered = df.copy()
    
    for col, value in filters.items():
        if not value: # Si la liste est vide, on ignore
            continue
        if col not in df_filtered.columns:
            continue
        if isinstance(value, list):
            df_filtered = df_filtered[df_filtered[col].isin(value)]
        else:
            df_filtered = df_filtered[df_filtered[col] == value]
    
    return df_filtered