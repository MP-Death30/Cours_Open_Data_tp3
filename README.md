# 🌤️ TP3 — Application Météo Interactive & Chatbot IA

Une application Data interactive (disponible en versions **Streamlit** et **Gradio**) permettant d'explorer des données météorologiques enrichies et de dialoguer avec elles via un assistant IA hybride (RAG).

## ✨ Fonctionnalités

* **📊 Dashboard Interactif :** Visualisation des indicateurs clés (KPIs) et explorateur de données.
* **🗺️ Carte Météo :** Carte thermique interactive (Plotly) des températures par ville.
* **📈 Prévisions Détaillées :** Comparaison graphique des températures entre plusieurs villes.
* **🤖 Assistant IA Hybride :** Chatbot intégré pour interroger les données en langage naturel (*"Quelle ville sera la plus chaude ?"*).
    * **Mode Cloud :** Google Gemini 2.0 Flash (Performance).
    * **Mode Local (Fallback) :** Ollama / Mistral (Résilience).
    * **Simulation Temporelle :** L'IA gère les dates futures des prévisions.

## 🛠️ Prérequis

* **Python 3.10+**
* **UV** (Gestionnaire de paquets moderne)
* **Clé API Gemini** (Pour le mode Cloud)
* **Ollama** (Pour le mode Local - optionnel)

## 📦 Installation

### 1. Cloner le projet

``` bash
git clone https://github.com/MP-Death30/Cours_Open_Data_tp3.git
cd tp3-app
```

### 2. Installer les dépendances

``` bash
uv sync

# Ou via pip classique :
# pip install -r requirements.txt
```

### 3. Configurer l'environnement
Créez un fichier `.env` à la racine et ajoutez votre clé API :

``` env
GEMINI_API_KEY="votre_clé_api_ici"
```

### 4. Import des Données
Copiez le fichier Parquet généré par le pipeline TP2 dans le dossier `data/processed/`.

``` text
data/
└── processed/
    └── meteo_enriched_2025XXXX_XXXXXX.parquet
```

## 🚀 Utilisation

Vous avez le choix entre deux interfaces :

### Option A : Interface Streamlit (Recommandé pour Dashboards)

``` bash
uv run streamlit run app_streamlit.py
```
*Accessible sur : `http://localhost:8501`*

### Option B : Interface Gradio (Recommandé pour Démos ML)

``` bash
uv run python app_gradio.py
```
*Accessible sur : `http://127.0.0.1:7860`*

## 📂 Architecture du Projet

``` text
tp3-app/
├── .streamlit/
│   └── config.toml      # Thème personnalisé Streamlit
├── data/
│   └── processed/       # Données météorologiques (Parquet)
├── utils/
│   ├── __init__.py
│   ├── charts.py        # Visualisations Plotly partagées
│   ├── chatbot.py       # Moteur IA (Gemini + Ollama + Context)
│   └── data.py          # Chargement DuckDB & Filtrage
├── app_streamlit.py     # Application Principale (Streamlit)
├── app_gradio.py        # Application Alternative (Gradio)
├── pyproject.toml       # Dépendances (UV)
├── README.md            # Documentation
└── .env                 # Secrets (non versionné)
```

## 🤖 Configuration du Chatbot

Le chatbot utilise une stratégie de **redondance** :

1.  **Tentative Principale :** Connexion à l'API **Gemini** (rapide, nécessite clé API).
2.  **Fallback Automatique :** En cas d'erreur ou de coupure internet, bascule sur **Ollama** en local (`http://localhost:11434`).

Pour activer le mode local, assurez-vous qu'Ollama est lancé :

``` bash
ollama pull mistral
```

## 👤 Auteur

Projet réalisé dans le cadre du module **Open Data & IA**.