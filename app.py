import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS MOBILE (FIX CAMÉRA & BOUTONS) ---
st.markdown("""
    <style>
    /* Fond propre */
    .stApp { background-color: #F8F9FA; color: #333; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

    /* SWITCH CAMÉRA VISIBLE */
    [data-testid="stCameraInput"] small {
        display: block !important;
        visibility: visible !important;
        font-size: 14px !important;
        background-color: white !important;
        color: #2563EB !important;
        border: 1px solid #2563EB !important;
        padding: 8px !important;
        border-radius: 20px !important;
        margin-bottom: 5px !important;
        text-align: center !important;
        font-weight: bold !important;
    }

    /* CADRE VIDÉO STABLE */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 50vh !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 2px solid #E5E7EB;
        margin-bottom: 10px !important;
    }

    /* BOUTON DÉCLENCHEUR (HACK TEXTE) */
    [data-testid="stCameraInput"] button {
       font-size: 0 !important;
       background-color: #2563EB !important;
       border: none !important;
       border-radius: 50px !important;
       height: 60px !important;
       width: 100% !important;
       position: relative !important;
    }
    [data-testid="stCameraInput"] button::after {
        content: "📸 PRENDRE LA PHOTO";
        font-size: 16px !important;
        font-weight: bold !important;
        color: white !important;
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        display: block;
    }

    /* RESTE DU DESIGN */
    .stButton>button {
        background-color: #10B981; 
        color: white !important;
        height: 55px;
        font-size: 18px;
        border-radius: 12px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    .stTextInput>div>div, .stTextArea>div>div {
        background-color: white; border: 1px solid #CCC; border-radius: 8px;
    }
    #MainMenu, footer, header {visibility: hidden;}
    
    .pro-header {
        text-align: center; margin-bottom: 10px; border-bottom: 2px solid #DDD; padding-bottom: 10px;
    }
    .pro-title { font-size: 24px; font-weight: 800; color: #111; margin: 0; font-family: sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CLÉ API ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

with st.sidebar:
    st.header("⚙️ Paramètres")
    if api_key: st.success("✅ Connecté")
    else:
        k = st.text_input("Clé API", type="password")
        if k:
            st.session_state.api_key = k
            st.rerun()

# --- 4. CERVEAU IA ---
def analyser(contenu, niveau):
    if not api_key: return "⛔ Clé manquante. Vérifiez les paramètres."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Expert administratif. Niveau {niveau}.
        Analyse ce document :
        1. 📄 DOC (Type, Date)
        2. 💰 PAIEMENT (Montant/Date en GRAS ou "Aucun")
        3. ✅ ACTIONS (Liste claire)
        4. ⚠️ PIÈGES"""
        return model.generate_content([prompt, contenu]).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)
st.info("👆 Pour changer de caméra, touchez le texte 'Select Device' au-dessus de l'image.", icon="ℹ️")

# Menu de choix
src = st.radio("Source", ["Caméra", "Galerie", "Texte"], horizontal=True, label_visibility="collapsed")
st.markdown("###")

entree = None
type_input = "txt" # Par défaut c'est du texte

# Logique d'affichage
if src == "Caméra":
    entree = st.camera_input("Photo", label_visibility="visible")
    type_input = "img"
elif src == "Galerie":
    # J'ai retiré 'pdf' pour éviter le crash de la ligne 125
    entree = st.file_uploader("Fichier", type=['png', 'jpg', 'jpeg'])
    type_input = "img"
else:
    entree = st.text_area("Texte", height=150)
    type_input = "txt"

# Bloc d'action (C'est ici qu'on corrige l'erreur)
if entree:
    st.markdown("###")
    niv = st.select_slider("Détail", options=["Synthèse", "Standard", "Complet"])
    st.markdown("###")
    
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Analyse en cours..."):
            
            # --- CORRECTION DE LA LIGNE 125 ---
            # On prépare la donnée proprement avant de l'envoyer
            donnee_a_envoyer = None
            
            if type_input == "img":
                # Si c'est une image, on l'ouvre avec PIL
                donnee_a_envoyer = Image.open(entree)
            else:
                # Si c'est du texte, on l'envoie tel quel
                donnee_a_envoyer = entree
            
            # On envoie à l'IA
            res = analyser(donnee_a_envoyer, niv)
            
            # Affichage
            st.markdown("---")
            st.markdown(f'<div style="background:white;padding:20px;border-radius:12px;border:1px solid #EEE;box-shadow:0 2px 5px rgba(0,0,0,0.05);color:#333;">{res}</div>', unsafe_allow_html=True)
