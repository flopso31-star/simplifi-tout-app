import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS "SPEED PRO" ---
st.markdown("""
    <style>
    /* IMPORT POLICE */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .stApp { background-color: #F3F4F6; color: #1F2937; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; }

    /* HEADER */
    .header-container {
        display: flex; flex-direction: column; align-items: center;
        margin-bottom: 20px; background: white; padding: 20px;
        border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .logo-img { width: 70px; height: 70px; margin-bottom: 10px; }
    .app-title { font-size: 22px; font-weight: 800; color: #111; margin: 0; }
    
    /* --- CUSTOMISATION DE LA CAMÉRA LIVE (INSTANTANÉE) --- */
    
    /* 1. Le Conteneur Vidéo */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 60vh !important; /* On force une grande hauteur */
        object-fit: cover !important;
        border-radius: 20px !important;
        border: 4px solid white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px !important; /* Espace avant le bouton */
    }

    /* 2. Le Bouton Déclencheur */
    [data-testid="stCameraInput"] button {
        visibility: visible !important;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important; /* Bouton Pilule */
        width: 100% !important;
        height: 70px !important;
        font-size: 0px !important; /* Cache le texte anglais */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3) !important;
    }
    
    /* 3. Texte Français sur le bouton */
    [data-testid="stCameraInput"] button::after {
        content: "⚡ PRENDRE LA PHOTO";
        font-size: 18px !important;
        font-weight: 800 !important;
        color: white !important;
        letter-spacing: 1px;
    }

    /* 4. Le Sélecteur de Caméra (Switch) */
    [data-testid="stCameraInput"] small {
        display: block !important;
        visibility: visible !important;
        background: white !important;
        color: #4F46E5 !important;
        padding: 8px 15px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        text-align: center !important;
        border: 1px solid #E5E7EB !important;
        margin-bottom: 10px !important;
    }

    /* CACHER ÉLÉMENTS INUTILES */
    header, footer, #MainMenu { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CLÉ API ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

with st.sidebar:
    if not api_key:
        k = st.text_input("Clé API", type="password")
        if k: st.session_state.api_key = k; st.rerun()

# --- 4. CERVEAU IA ---
def analyser(img_bytes):
    if not api_key: return "⚠️ Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """
        Tu es un assistant personnel. Analyse ce document.
        Sois DIRECT.
        
        ### 📄 C'EST QUOI ?
        (Type de courrier, Émetteur)
        
        ### 💰 FAUT-IL PAYER ?
        (Si OUI : Affiche le MONTANT et la DATE LIMITE en GRAS. Si NON : Écris "Rien à payer ✅")
        
        ### ✅ QUE DOIS-JE FAIRE ?
        (Liste des actions)
        
        ### ⚠️ ATTENTION
        (Pièges éventuels)
        """
        return model.generate_content([prompt, img_bytes]).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
logo_url = "https://cdn-icons-png.flaticon.com/512/9985/9985702.png"

st.markdown(f"""
<div class="header-container">
    <img src="{logo_url}" class="logo-img">
    <h1 class="app-title">Simplifi Tout</h1>
</div>
""", unsafe_allow_html=True)

# NOTE D'AIDE
st.caption("ℹ️ Pour la caméra arrière, touchez **'Select Device'** juste au-dessus de l'image.")

# CAMÉRA LIVE (Le secret de la vitesse)
photo_prise = st.camera_input(" ", label_visibility="hidden")

# AUTOMATISME
if photo_prise:
    # Pas de spinner bloquant, ça va trop vite pour ça
    
    # 1. Analyse directe
    res = analyser(photo_prise)
    
    # 2. Résultat
    st.markdown("---")
    st.markdown(f"""
    <div style="
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #E5E7EB; margin-top: 10px;
        animation: fadeIn 0.5s;
    ">
        {res}
    </div>
    """, unsafe_allow_html=True)
