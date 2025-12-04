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

# --- CSS (DESIGN LIGHT + FIX CAMÉRA) ---
st.markdown("""
    <style>
    /* 1. FOND ET STRUCTURE */
    .stApp {
        background-color: #F8F9FA;
        color: #31333F;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
    }

    /* 2. RÉPARATION DU SÉLECTEUR DE CAMÉRA (SWITCH) */
    /* On cible la zone qui contient le choix de la caméra */
    [data-testid="stCameraInput"] > label {
        display: none !important; /* Cache le label inutile "Prendre photo" du haut */
    }
    
    /* On cible la liste déroulante (le vrai switch) */
    [data-testid="stCameraInput"] span {
        font-weight: bold;
        color: #2563EB;
    }
    
    /* On agrandit la zone de clic pour changer de caméra */
    [data-testid="stCameraInput"] small {
        font-size: 14px !important;
        background-color: #E0E7FF;
        color: #2563EB;
        padding: 8px 15px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 10px;
        border: 1px solid #2563EB;
    }

    /* 3. LA VIDÉO */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 45vh !important; /* Un peu moins haut pour laisser la place au switch */
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 2px solid #E0E0E0;
    }
    
    /* 4. LE BOUTON DÉCLENCHEUR (EN BAS) */
    [data-testid="stCameraInput"] button {
       font-size: 0 !important;
       background-color: #2563EB !important;
       border: none !important;
       border-radius: 50px !important;
       padding: 15px !important;
       width: 100% !important;
       margin-top: 5px !important;
    }
    [data-testid="stCameraInput"] button::after {
        content: "📸 PRENDRE LA PHOTO";
        font-size: 16px !important;
        color: white !important;
        display: block;
    }

    /* 5. LE RESTE DU DESIGN (PROPRE) */
    .stTextInput>div>div, .stTextArea>div>div {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #D1D5DB;
    }
    
    .stButton>button {
        background-color: #10B981; /* Vert */
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 15px 0px;
        font-size: 18px;
        font-weight: 700;
        width: 100%;
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
    }
    .stButton>button:hover { background-color: #059669; }

    #MainMenu, footer, header {visibility: hidden;}

    .pro-header {
        text-align: center;
        margin-bottom: 10px;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 10px;
    }
    .pro-title {
        font-size: 26px; font-weight: 800; color: #111827; margin: 0; font-family: sans-serif;
    }
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
        Analyse :
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
    # Le composant caméra standard
    entree = st.camera_input("Photo", label_visibility="collapsed")
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
