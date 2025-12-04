import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIG ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS MOBILE-FIRST ROBUSTE ---
st.markdown("""
    <style>
    /* 1. FOND PROPRE */
    .stApp {
        background-color: #F8F9FA;
        color: #333;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* 2. RÉPARATION DU SÉLECTEUR DE CAMÉRA (SWITCH) */
    /* On force l'affichage de la zone de sélection */
    [data-testid="stCameraInput"] small {
        display: block !important;
        visibility: visible !important;
        font-size: 16px !important; /* Gros texte */
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        border: 2px solid #2563EB !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
        text-align: center !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }

    /* 3. CADRE VIDÉO */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 50vh !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 2px solid #E5E7EB;
        margin-bottom: 15px !important; /* Espace sous la vidéo */
    }

    /* 4. LE BOUTON "PRENDRE PHOTO" (Bas) */
    [data-testid="stCameraInput"] button {
       /* TECHNIQUE INFAILLIBLE POUR REMPLACER LE TEXTE */
       font-size: 0 !important; /* Réduit le texte anglais à 0 pixel */
       
       background-color: #2563EB !important;
       border: none !important;
       border-radius: 12px !important;
       height: 60px !important;
       width: 100% !important;
       position: relative !important;
    }
    
    /* On réécrit le texte par dessus */
    [data-testid="stCameraInput"] button::after {
        content: "📸 PRENDRE LA PHOTO";
        font-size: 18px !important; /* On remet une taille normale ici */
        font-weight: bold !important;
        color: white !important;
        
        /* Centrage parfait */
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        display: block;
        width: 100%;
    }

    /* 5. RESTE DU DESIGN */
    .stButton>button {
        background-color: #10B981; 
        color: white !important;
        height: 60px;
        font-size: 18px;
        border-radius: 12px;
        border: none;
        width: 100%;
    }
    .stTextInput>div>div, .stTextArea>div>div {
        background-color: white; border: 1px solid #CCC; border-radius: 8px;
    }
    #MainMenu, footer, header {visibility: hidden;}
    
    .pro-header {
        text-align: center; margin-bottom: 15px; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px;
    }
    .pro-title { font-size: 26px; font-weight: 800; color: #111827; margin: 0; font-family: sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

with st.sidebar:
    st.header("⚙️ Paramètres")
    if api_key: st.success("Connecté")
    else:
        k = st.text_input("Clé API", type="password")
        if k:
            st.session_state.api_key = k
            st.rerun()

def analyser(contenu, niveau):
    if not api_key: return "⛔ Clé manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Expert administratif (Français). Niveau
