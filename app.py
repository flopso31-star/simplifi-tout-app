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

# --- 2. STYLE PRO & NETTOYAGE ---
st.markdown("""
    <style>
    /* POLICE & FOND */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #F8F9FA; color: #333; }
    
    /* SUPPRESSION MARGES */
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    header, footer, #MainMenu { display: none !important; }

    /* HEADER PERSONNALISÉ */
    .header-box {
        text-align: center;
        padding: 20px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .logo-icon { width: 60px; margin-bottom: 10px; }
    .main-title { font-size: 24px; font-weight: 800; color: #111; margin: 0; }
    .sub-title { font-size: 14px; color: #666; margin-top: 5px; }

    /* CUSTOMISATION DU BOUTON UPLOAD */
    [data-testid="stFileUploader"] { width: 100% !important; }
    
    /* On transforme la zone de dépôt en un beau bouton */
    [data-testid="stFileUploader"] section {
        background: linear-gradient(135deg, #2563EB 0%, #10B981 100%) !important;
        padding: 0px !important;
        border-radius: 15px !important;
        border: none !important;
        min-height: 70px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }
    
    /* On cache TOUT le texte par défaut (Drag&Drop etc) */
    [data-testid="stFileUploader"] section > div, 
    [data-testid="stFileUploader"] section span, 
    [data-testid="stFileUploader"] section small {
        display: none !important;
    }

    /* On ajoute NOTRE texte par dessus */
    [data-testid="stFileUploader"] section::after {
        content: "📸 PHOTO  ou  📂 DOCUMENT";
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* On cache la liste de fichiers une fois uploadé */
    [data-testid="stFileUploader"] ul { display: none !important; }

    /* BOITE DE RÉSULTAT */
    .result-box {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin-top: 20px;
        animation: fadeIn 0.5s ease-out;
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

# --- 4. FONCTIONS (Compression + IA) ---
def compresser_image(image):
    # Réduit la taille pour que ça aille vite en 4G
    if image.mode != 'RGB': image = image.convert('RGB')
    max_size = 1500
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image

def analyser(img):
    if not api_key: return "⚠️ Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """
        Agis comme une secrétaire personnelle efficace.
        Analyse ce document pour un particulier. Sois DIRECTE.
        
        1. 📄 C'EST QUOI ? (Nature du document, Émetteur)
        2. 💰 ARGENT (Y a-t-il un paiement ? SI OUI : Montant + Date en GRAS. SI NON : "Rien à payer ✅")
        3. ✅ À FAIRE (Liste d'actions très courtes)
        4. ⚠️ ATTENTION (Seulement s'il y a un piège/pénalité)
        """
        return model.generate_content([prompt, img]).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---

# A. LE HEADER (Logo + Titre + Description)
# Icône Document Pro
icon_url = "https://cdn-icons-png.flaticon.com/512/2991/2991106.png"

st.markdown(f"""
<div class="header-box">
    <img src="{icon_url}" class="logo-icon">
    <h1 class="main-title">Simplifi Tout</h1>
    <p class="sub-title">Scannez vos courriers, comprenez tout de suite.</p>
</div>
""", unsafe_allow_html=True)

# B. ZONE DE RÉSULTAT (L'ASCENSEUR MAGIQUE)
# On crée un espace vide ICI, tout en haut. L'IA écrira dedans plus tard.
zone_resultat = st.empty()

# C. LE BOUTON D'ACTION
uploaded_file = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# D. LOGIQUE AUTOMATIQUE
if uploaded_file is not None:
    # Petit message de chargement non intrusif
    toast = st.toast("📸 Image reçue ! Analyse en cours...", icon="🚀")
    
    try:
        # 1. Traitement Image
        img = Image.open(uploaded_file)
        img_opt = compresser_image(img) # On compresse pour la vitesse
        
        # 2. IA
        reponse = analyser(img_opt)
        
        # 3. AFFICHAGE DANS LA ZONE DU HAUT
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

# E. EXPLICATION (En bas)
if not uploaded_file:
    st.info("👇 Cliquez sur le bouton ci-dessous pour choisir **Caméra** ou **Fichier**.", icon="ℹ️")
