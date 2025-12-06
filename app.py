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

# --- 2. DESIGN & LOGO (CSS PREMIUM) ---
st.markdown("""
    <style>
    /* IMPORTATION POLICE MODERNE (Poppins) */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    /* APPLICATION GLOBALE */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background-color: #F3F4F6; /* Gris très doux (Style Apple) */
        color: #1F2937;
    }
    
    /* SUPPRESSION MARGES INUTILES */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }

    /* --- HEADER / LOGO --- */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 30px;
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .logo-img {
        width: 80px;
        height: 80px;
        margin-bottom: 10px;
    }
    
    .app-title {
        font-size: 24px;
        font-weight: 800;
        color: #111827;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .app-subtitle {
        font-size: 14px;
        color: #6B7280;
        margin-top: 5px;
        text-align: center;
    }

    /* --- BOUTON UPLOAD STYLISÉ --- */
    [data-testid="stFileUploader"] {
        width: 100% !important;
    }
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
    }
    /* Cache le contenu par défaut */
    [data-testid="stFileUploader"] section > div, 
    [data-testid="stFileUploader"] section span, 
    [data-testid="stFileUploader"] section small {
        display: none !important;
    }

    /* Le Bouton lui-même */
    [data-testid="stFileUploader"] button {
        visibility: visible !important;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important; /* Dégradé Indigo */
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        width: 100% !important;
        height: 70px !important;
        font-size: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3) !important;
        transition: transform 0.2s !important;
    }
    
    [data-testid="stFileUploader"] button:active {
        transform: scale(0.98) !important;
    }

    [data-testid="stFileUploader"] button::after {
        content: "📸 SCANNER UN DOCUMENT";
        font-size: 16px !important;
        font-weight: 700 !important;
        color: white !important;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stFileUploader"] ul { display: none !important; }

    /* CACHER ÉLÉMENTS DE STREAMLIT */
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

# --- 4. FONCTIONS (Compression & IA) ---
def compresser_image(image):
    if image.mode != 'RGB': image = image.convert('RGB')
    max_size = 1500
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image

def analyser(img_bytes):
    if not api_key: return "⚠️ Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Prompt "Grand Public"
        prompt = """
        Tu es un assistant personnel bienveillant.
        Analyse ce document pour un particulier qui ne comprend pas le jargon.
        
        Ta réponse doit être structurée ainsi :
        
        ### 📄 C'EST QUOI ?
        (En 1 phrase simple : Qui écrit et pourquoi ?)
        
        ### 💰 FAUT-IL PAYER ?
        (Si OUI : Affiche le MONTANT et la DATE LIMITE en GRAS. Si NON : Écris "Rien à payer ✅")
        
        ### ✅ QUE DOIS-JE FAIRE ?
        (Liste ultra-courte des actions : Ranger, Répondre, Payer...)
        
        ### ⚠️ ATTENTION
        (S'il y a un piège ou une pénalité, dis-le clairement. Sinon n'écris rien.)
        """
        return model.generate_content([prompt, img_bytes]).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE UTILISATEUR ---

# HEADER AVEC LOGO (Utilisation d'une icône externe pro)
# Si vous avez votre propre logo sur Github, remplacez l'URL ci-dessous par le lien "Raw" de votre image.
logo_url = "https://cdn-icons-png.flaticon.com/512/9985/9985702.png" # Icône "Document AI" propre

st.markdown(f"""
<div class="header-container">
    <img src="{logo_url}" class="logo-img">
    <h1 class="app-title">Simplifi Tout</h1>
    <p class="app-subtitle">L'administratif, enfin simple.</p>
</div>
""", unsafe_allow_html=True)

# BOUTON D'ACTION
uploaded_file = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# LOGIQUE AUTOMATIQUE
if uploaded_file is not None:
    status = st.status("🚀 Analyse en cours...", expanded=True)
    
    try:
        status.write("Optimisation de l'image...")
        image_originale = Image.open(uploaded_file)
        image_optimisee = compresser_image(image_originale)
        
        status.write("Lecture intelligente...")
        res = analyser(image_optimisee)
        
        status.update(label="✅ Terminé !", state="complete", expanded=False)
        
        # RÉSULTAT STYLE "CARTE"
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background: white;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            border: 1px solid #E5E7EB;
            margin-top: 10px;
            animation: fadeIn 0.6s ease-out;
        ">
            {res}
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons()
        
    except Exception as e:
        status.update(label="❌ Erreur", state="error")
        st.error(f"Erreur technique : {e}")
