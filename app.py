import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. DESIGN PRO & CLEAN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .stApp { background-color: #F8F9FA; color: #333; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    header, footer, #MainMenu { display: none !important; }

    /* HEADER */
    .header-box {
        text-align: center; padding: 20px; background: white;
        border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .logo-icon { width: 60px; margin-bottom: 10px; }
    .main-title { font-size: 24px; font-weight: 800; color: #111; margin: 0; }
    .sub-title { font-size: 14px; color: #666; margin-top: 5px; }

    /* BOUTON UPLOAD STYLISÉ */
    [data-testid="stFileUploader"] { width: 100% !important; }
    [data-testid="stFileUploader"] section {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
        padding: 0px !important; border-radius: 15px !important; border: none !important;
        min-height: 70px !important; display: flex !important;
        align-items: center !important; justify-content: center !important; cursor: pointer !important;
    }
    /* Cache les textes par défaut */
    [data-testid="stFileUploader"] section > div, 
    [data-testid="stFileUploader"] section span, 
    [data-testid="stFileUploader"] section small { display: none !important; }

    /* Texte perso */
    [data-testid="stFileUploader"] section::after {
        content: "📸 PHOTO  ou  📂 DOCUMENT";
        color: white !important; font-weight: 700 !important; font-size: 16px !important;
    }
    [data-testid="stFileUploader"] ul { display: none !important; }

    /* RÉSULTAT */
    .result-box {
        background: white; padding: 25px; border-radius: 15px;
        border-left: 5px solid #2563EB; box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin-top: 20px; animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
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

# --- 4. COMPRESSION (POUR LA VITESSE) ---
def preparer_image(image_file):
    image = Image.open(image_file)
    if image.mode != 'RGB': image = image.convert('RGB')
    max_dimension = 1000
    if max(image.size) > max_dimension:
        ratio = max_dimension / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image

# --- 5. CERVEAU IA (REMIS À ZÉRO SUR LA VERSION SIMPLE) ---
def analyser(img_traitee):
    if not api_key: return "⚠️ Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # ICI : J'ai remis exactement la version "Monsieur tout le monde"
        prompt = """
        Tu es un assistant personnel bienveillant.
        Ta mission : Lire ce document et l'expliquer le plus simplement possible à quelqu'un qui déteste l'administratif.
        
        Réponds directement avec cette structure :
        
        1. 📄 C'EST QUOI ? (En 1 phrase simple : Qui écrit et pourquoi ?)
        2. 💰 ARGENT (Y a-t-il quelque chose à payer ? Si OUI : Affiche le MONTANT et la DATE LIMITE en TRÈS GRAS et GROS. Si NON : Écris "Rien à payer ✅")
        3. ✅ À FAIRE (Liste ultra-courte des actions. Si rien à faire, dis "Tu peux classer ce document 📂")
        4. ⚠️ ATTENTION (S'il y a un piège ou une pénalité, dis-le clairement. Sinon n'écris rien.)
        
        Ton ton doit être clair, rassurant et direct.
        """
        return model.generate_content([prompt, img_traitee]).text
    except Exception as e: return f"Erreur : {e}"

# --- 6. INTERFACE ---
icon_url = "https://cdn-icons-png.flaticon.com/512/2991/2991106.png"

st.markdown(f"""
<div class="header-box">
    <img src="{icon_url}" class="logo-icon">
    <h1 class="main-title">Simplifi Tout</h1>
    <p class="sub-title">L'administratif devient facile.</p>
</div>
""", unsafe_allow_html=True)

# ZONE RÉSULTAT (VIDE AU DÉBUT, MAIS PLACÉE EN HAUT)
zone_resultat = st.empty()

# BOUTON
uploaded_file = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# LOGIQUE
if uploaded_file is not None:
    
    st.toast("⚡ Traitement rapide...", icon="⚙️")
    
    try:
        # 1. COMPRESSION
        image_optimisee = preparer_image(uploaded_file)
        
        # 2. ENVOI À L'IA
        # J'ai remis le spinner simple
        with st.spinner("Lecture du document..."):
            reponse = analyser(image_optimisee)
        
        # 3. AFFICHAGE RÉSULTAT EN HAUT
        with zone_resultat.container():
            st.markdown(f"""
            <div class="result-box">
                <h3 style="color:#2563EB; margin-top:0;">💡 RÉSULTAT</h3>
                <hr style="border:1px solid #EEE;">
                {reponse}
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
            
    except Exception as e:
        st.error(f"Erreur : {e}")
