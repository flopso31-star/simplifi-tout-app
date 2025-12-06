import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS "FANTÔME" (La solution radicale) ---
st.markdown("""
    <style>
    /* POLICE & FOND */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background-color: #F3F4F6; color: #1F2937; }
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* HEADER */
    .header-container {
        display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;
        background: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .logo-img { width: 80px; height: 80px; margin-bottom: 10px; }
    .app-title { font-size: 24px; font-weight: 800; color: #111; margin: 0; }
    .app-subtitle { font-size: 14px; color: #666; margin-top: 5px; text-align: center; }

    /* --- LE HACK SUPRÊME POUR LE BOUTON --- */

    /* 1. On cible la zone de dépôt principale */
    [data-testid="stFileUploader"] section {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 40px 0px !important; /* Donne la hauteur au bouton */
        cursor: pointer !important;
        
        /* ICI LA MAGIE : On rend tout le texte natif INVISIBLE */
        color: transparent !important;
        font-size: 0px !important;
    }

    /* 2. On cible TOUS les enfants possibles (span, small, div, svg) et on les force à être invisibles */
    [data-testid="stFileUploader"] section * {
        color: transparent !important;
        font-size: 0px !important;
        fill: transparent !important; /* Pour les icônes SVG */
        border: none !important;
        background-color: transparent !important;
    }
    
    /* 3. On cache spécifiquement le bouton "Browse files" par sécurité */
    [data-testid="stFileUploader"] button {
        display: none !important;
    }

    /* 4. ON ÉCRIT NOTRE PROPRE TEXTE PAR DESSUS */
    /* On utilise ::after sur la section elle-même */
    [data-testid="stFileUploader"] section::after {
        content: "📸 PRENDRE UNE PHOTO / GALERIE";
        
        /* On remet la couleur et la taille visible */
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        
        /* On centre parfaitement le texte */
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        white-space: nowrap; /* Empêche le texte de se couper */
        pointer-events: none; /* Le clic passe au travers pour activer l'upload */
    }

    /* Cacher éléments parasites */
    [data-testid="stFileUploader"] ul { display: none !important; }
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
    <p class="app-subtitle">Touchez le bouton violet ci-dessous</p>
</div>
""", unsafe_allow_html=True)

# BOUTON D'ACTION (Label vide)
uploaded_file = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")

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
    
