"""Module chatbot pour interroger les données."""
import pandas as pd
from litellm import completion
import os
import datetime
import streamlit as st

class DataChatbot:
    """Chatbot hybride (Cloud + Local) pour interroger les données."""
    
    def __init__(self, df: pd.DataFrame, 
                 primary_model: str = "gemini/gemini-2.5-flash-lite",
                 fallback_model: str = "ollama/mistral"):
        self.df = df
        self.primary_model = primary_model
        self.fallback_model = fallback_model # Modèle local (ex: mistral, llama3)
        self.context = self._build_context()
        self.history = []
    
    def _build_context(self) -> str:
        """Construit le contexte avec la date réelle du système."""
        
        # 1. Préparation des données brutes
        if len(self.df) > 1000:
            data_str = self.df.head(1000).to_string(index=False)
            warning = "(Données partielles : 1000 premières lignes)"
        else:
            data_str = self.df.to_string(index=False)
            warning = "(Données complètes)"
            
        # 2. Date réelle du système (Dynamique)
        today_str = datetime.datetime.now().strftime("%d/%m/%Y")

        return f"""
        Tu es un expert météorologue.
        
        CONTEXTE TEMPOREL :
        Nous sommes le {today_str} (Date du jour).
        
        DONNÉES DISPONIBLES {warning} :
        {data_str}
        
        TES MISSIONS :
        1. Réponds aux questions en utilisant UNIQUEMENT ce tableau.
        2. Si on te demande "demain", calcule la date par rapport à aujourd'hui ({today_str}).
        3. IMPORTANT : Si les dates du tableau sont dans le futur par rapport à aujourd'hui, considère-les comme des prévisions fiables à long terme. Ne refuse pas de répondre.
        4. Si les dates sont dans le passé, considère-les comme de l'historique.
        """
    
    def chat(self, user_message: str) -> str:
        messages = [{"role": "system", "content": self.context}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_message})
        
        try:
            # 1. Tentative avec le modèle principal (Gemini)
            response = completion(
                model=self.primary_model,
                messages=messages,
                api_key=os.environ.get("GEMINI_API_KEY")
            )
            assistant_message = response.choices[0].message.content
            
        except Exception as e:
            # 2. FALLBACK sur Ollama en cas d'erreur (Quota, Connexion...)
            print(f"⚠️ Erreur Gemini ({str(e)}). Bascule sur Ollama ({self.fallback_model})...")
            
            # Notification discrète dans l'interface
            st.toast(f"Mode hors-ligne activé : Utilisation de {self.fallback_model}", icon="🛟")
            
            try:
                # Configuration pour Ollama local (port standard 11434)
                response = completion(
                    model=self.fallback_model,
                    messages=messages,
                    api_base="http://localhost:11434"
                )
                assistant_message = response.choices[0].message.content
            except Exception as e_local:
                return f"❌ Erreur totale (Cloud & Local) : {str(e_local)}. Vérifiez qu'Ollama est bien lancé."

        # Mise à jour de l'historique
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})
        if len(self.history) > 20:
            self.history = self.history[-20:]
        
        return assistant_message
    
    def reset(self):
        self.history = []