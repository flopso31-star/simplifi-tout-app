import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS (DESIGN LIGHT + FIX TEXTES SÉPARÉS) ---
st.markdown("""
    <style>
    /* 1. APP GLOBALE */
    .stApp {
        background-color: #F8F9FA;
        color: #31333F;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* 2. CIBLAGE DE LA CAMÉRA GLOBAL */
    [data-testid="stCameraInput"] {
        width: 100% !important;
    }

    /* -------------------------------------------------------
       ZONE 1 : LE HAUT (LE LABEL / SWITCH)
       C'est ici qu'on écrit "INVERSER CAM"
    ------------------------------------------------------- */
    [data-testid="stCameraInput"] > label {
        font-size: 0 !important; /* On cache le texte "Prendre la photo" d'origine */
        display: block !important;
        visibility: visible !important;
        margin-bottom: 5px !important;
    }
    
    /* On injecte le nouveau texte "INVERSER CAM" */
    [data-testid="stCameraInput"] > label::after {
        content: "🔄 INVERSER CAM (TOUCHER ICI)";
        font-size: 12px !important;
        font-weight: bold !important;
        color: #2563EB !important; /* Bleu */
        background-color: #DBEAFE; /* Fond bleu très clair */
        padding: 5px 10px !important;
        border-radius: 15px !important;
        display: inline-block !important;
        border: 1px solid #2563EB;
    }
    
    /* On cible le petit texte technique (Select Device) pour le rendre plus gros */
    [data-testid="stCameraInput"] small {
        font-size: 14px !important;
        color: #4B5563 !important;
        opacity: 1 !important;
    }

    /* -------------------------------------------------------
       ZONE 2 : LA VIDÉO (MILIEU)
    ------------------------------------------------------- */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 50vh !important; /* Hauteur fixe */
        object-fit: cover !important;
        border-radius: 15px !important;
        border: 2px solid #E5E7EB;
        margin-bottom: 10px !important;
    }

    /* -------------------------------------------------------
       ZONE 3 : LE DÉCLENCHEUR (BAS)
       C'est ici qu'on écrit "PRENDRE PHOTO"
    ------------------------------------------------------- */
    [data-testid="stCameraInput"] button {
       font-size: 0 !important; /* Cache le texte anglais */
       background-color: #2563EB !important; /* Bleu Pro */
       border: none !important;
       border-radius: 12px !important;
       padding: 0px !important;
       height: 60px !important;
       width: 100% !important;
       margin-top: 5px !important;
    }
    
    /* Le Texte Français sur le bouton du bas */
    [data-testid="stCameraInput"] button::after {
        content: "📸 PRENDRE LA PHOTO";
        font-size: 16px !important;
        font-weight: bold !important;
        color: white !important;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 100%;
    }

    /* 4. RESTE DU DESIGN */
    .stTextInput>div>div, .stTextArea>div>div {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #10B981; /* Vert Validation */
        color: white !important;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        margin-top: 20px;
    }
    #MainMenu, footer, header {visibility: hidden;}
    
    .pro-header {
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 10px;
    }
    .pro-title { font-size: 26px; font-weight: 800; color: #111827; margin: 0; font-family: sans-serif; }
    .pro-subtitle { font-size: 14px; color: #6B7280; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CLÉ API ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

with st.sidebar:
    st.header("⚙️ Paramètres")
    if api_key:
        st.success("✅ Connecté")
    else:
        input_key = st.text_input("Clé API", type="password")
        if input_key:
            st.session_state.api_key = input_key
            st.rerun()

# --- IA ---
def analyser_contenu(content, niveau):
    if not api_key: return "⛔ Clé manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Rôle : Expert administratif. Niveau : {niveau}.
        Analyse ce document en Français :
        1. 📄 DOCUMENT (Nature, Date, Émetteur)
        2. 💰 PAIEMENT (Montant et Date -> EN GRAS. Sinon "Aucun")
        3. ✅ ACTIONS (Liste claire)
        4. ⚠️ VIGILANCE (Pièges)
        """
        response = model.generate_content([prompt, content])
        return response.text
    except Exception as e: return f"Erreur : {str(e)}"

# --- INTERFACE ---
st.markdown("""
<div class="pro-header">
    <h1 class="pro-title">Simplifi Tout</h1>
    <p class="pro-subtitle">Votre assistant administratif</p>
</div>
""", unsafe_allow_html=True)

source_image = st.radio("Source :", ["Caméra", "Galerie", "Texte"], horizontal=True, label_visibility="collapsed")
st.markdown("###")

entree = None
type_entree = None

if source_image == "Caméra":
    # On laisse le label visible car c'est lui qu'on transforme en bouton "Inverser"
    entree = st.camera_input("Prendre la photo", label_visibility="visible")
    type_entree = "img"
    
elif source_image == "Galerie":
    entree = st.file_uploader("Fichier", type=['png', 'jpg', 'pdf'])
    type_entree = "img"
else:
    entree = st.text_area("Texte", height=150)
    type_entree = "txt"

if entree:
    st.markdown("###")
    niveau = st.select_slider("Détails", options=["Synthèse", "Standard", "Détaillé"])
    st.markdown("###")
    
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Analyse en cours..."):
            res = analyser_contenu(Image.open(entree) if type_entree == "img" else entree, niveau)
            st.markdown("---")
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E5E7EB; box-shadow: 0 4px 6px rgba(0,0,0,0.05); color: #374151;">
                {res}
            </div>
            """, unsafe_allow_html=True)
