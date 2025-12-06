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

# --- 2. DESIGN & LOGO (CSS SÉCURISÉ) ---
st.markdown("""
    <style>
    /* POLICE MODERNE */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .stApp { background-color: #F3F4F6; color: #1F2937; }
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* HEADER */
    .header-container {
        display: flex; flex-direction: column; align-items: center;
        margin-bottom: 20px; background: white; padding: 20px;
        border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .logo-img { width: 80px; height: 80px; margin-bottom: 10px; }
    .app-title { font-size: 24px; font-weight: 800; color: #111; margin: 0; }
    .app-subtitle { font-size: 14px; color: #666; margin-top: 5px; text-align: center; }

    /* --- BOUTON UPLOAD (CORRECTION) --- */
    
    /* On cible la zone de dépôt (le rectangle en pointillés) */
    [data-testid="stFileUploader"] section {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        padding: 30px 0px !important; /* Donne de la hauteur */
        border-radius: 20px !important;
        border: none !important;
        cursor: pointer !important;
    }

    /* On change la couleur des textes à l'intérieur pour qu'ils soient lisibles sur le fond bleu */
    [data-testid="stFileUploader"] section span {
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    
    [data-testid="stFileUploader"] section small {
        color: rgba(255,255,255,0.8) !important;
        font-size: 12px !important;
    }
    
    /* On cache le bouton "Browse files" standard car on rend toute la zone cliquable */
    [data-testid="stFileUploader"] button {
        display: none !important;
    }

    /* Icône de trombone qu'on remplace ou cache si besoin */
    [data-testid="stFileUploader"] svg {
        fill: white !important;
    }

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

# --- 4. FONCTIONS ---
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
        prompt = """
        Tu es un assistant personnel bienveillant.
        Analyse ce document pour un particulier.
        
        ### 📄 C'EST QUOI ?
        (En 1 phrase simple : Qui écrit et pourquoi ?)
        
        ### 💰 FAUT-IL PAYER ?
        (Si OUI : Affiche le MONTANT et la DATE LIMITE en GRAS. Si NON : Écris "Rien à payer ✅")
        
        ### ✅ QUE DOIS-JE FAIRE ?
        (Liste ultra-courte des actions)
        
        ### ⚠️ ATTENTION
        (S'il y a un piège ou une pénalité, dis-le clairement.)
        """
        return model.generate_content([prompt, img_bytes]).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
logo_url = "https://cdn-icons-png.flaticon.com/512/9985/9985702.png"

st.markdown(f"""
<div class="header-container">
    <img src="{logo_url}" class="logo-img">
    <h1 class="app-title">Simplifi Tout</h1>
    <p class="app-subtitle">Touchez la zone bleue ci-dessous</p>
</div>
""", unsafe_allow_html=True)

# BOUTON D'ACTION (Avec un label visible cette fois pour la sécurité)
uploaded_file = st.file_uploader("Prendre une photo ou choisir un fichier", type=['png', 'jpg', 'jpeg'])

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
        
        # RÉSULTAT
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background: white; padding: 25px; border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #E5E7EB; margin-top: 10px;
        ">
            {res}
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
        
    except Exception as e:
        status.update(label="❌ Erreur", state="error")
        st.error(f"Erreur : {e}")
