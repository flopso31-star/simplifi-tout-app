import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS & DESIGN PRO ---
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

# --- 4. FONCTION DE COMPRESSION (LE CŒUR DU TURBO) ---
def preparer_image(image_file):
    """
    Cette fonction prend l'image brute, la réduit en taille 
    et la renvoie prête pour l'IA.
    """
    image = Image.open(image_file)
    
    # 1. Conversion en RGB (pour éviter les soucis de PNG transparents)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # 2. Redimensionnement (Max 1000px de large)
    # Un document A4 est lisible parfaitement à 1000px, pas besoin de 4000px.
    max_dimension = 1000
    if max(image.size) > max_dimension:
        ratio = max_dimension / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
    return image

# --- 5. CERVEAU IA ---
def analyser(img_traitee):
    if not api_key: return "⚠️ Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """
        Agis comme un assistant personnel efficace.
        Analyse ce document administratif. Sois DIRECT.
        
        1. 📄 C'EST QUOI ? (Nature, Émetteur)
        2. 💰 ARGENT (Montant & Date en GRAS. Si rien : "Rien à payer ✅")
        3. ✅ À FAIRE (Liste d'actions ultra-courte)
        4. ⚠️ ATTENTION (Pièges éventuels)
        """
        return model.generate_content([prompt, img_traitee]).text
    except Exception as e: return f"Erreur : {e}"

# --- 6. INTERFACE ---
icon_url = "https://cdn-icons-png.flaticon.com/512/2991/2991106.png"

st.markdown(f"""
<div class="header-box">
    <img src="{icon_url}" class="logo-icon">
    <h1 class="main-title">Simplifi Tout</h1>
    <p class="sub-title">L'assistant administratif rapide.</p>
</div>
""", unsafe_allow_html=True)

# ZONE RÉSULTAT (VIDE AU DÉBUT)
zone_resultat = st.empty()

# BOUTON
uploaded_file = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# LOGIQUE AUTOMATIQUE
if uploaded_file is not None:
    
    # Notification visuelle immédiate
    st.toast("⚡ Optimisation de l'image pour le réseau...", icon="⚙️")
    
    try:
        # 1. COMPRESSION IMMÉDIATE
        with st.spinner("Traitement rapide..."):
            image_optimisee = preparer_image(uploaded_file)
        
        # 2. ENVOI À L'IA
        with st.spinner("L'IA lit le document..."):
            reponse = analyser(image_optimisee)
        
        # 3. AFFICHAGE RÉSULTAT EN HAUT
        with zone_resultat.container():
            st.markdown(f"""
            <div class="result-box">
                <h3 style="color:#2563EB; margin-top:0;">💡 Analyse Terminée</h3>
                <hr style="border:1px solid #EEE;">
                {reponse}
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
            
    except Exception as e:
        st.error(f"Erreur : {e}")
