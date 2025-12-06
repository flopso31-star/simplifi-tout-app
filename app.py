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

# --- 2. CSS "GROS BOUTON" ---
st.markdown("""
    <style>
    /* FOND */
    .stApp { background-color: #F8F9FA; color: #333; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

    /* HEADER */
    .pro-header { text-align: center; margin-bottom: 15px; border-bottom: 1px solid #DDD; }
    .pro-title { font-size: 26px; font-weight: 800; color: #111; margin: 0; font-family: sans-serif; }

    /* NETTOYAGE INTERFACE */
    header, footer, #MainMenu { visibility: hidden !important; }
    
    /* BOUTON UPLOAD CUSTOMISÉ */
    [data-testid="stFileUploader"] { width: 100% !important; }
    [data-testid="stFileUploader"] section { padding: 0 !important; background: transparent !important; border: none !important; }
    [data-testid="stFileUploader"] section > div, 
    [data-testid="stFileUploader"] section span, 
    [data-testid="stFileUploader"] section small { display: none !important; }

    [data-testid="stFileUploader"] button {
        visibility: visible !important;
        background: linear-gradient(90deg, #2563EB, #10B981) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        width: 100% !important;
        height: 80px !important;
        font-size: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
    }

    [data-testid="stFileUploader"] button::after {
        content: "📸 PHOTO  |  📂 GALERIE";
        font-size: 18px !important;
        font-weight: bold !important;
        color: white !important;
    }
    
    [data-testid="stFileUploader"] ul { display: none !important; }
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

# --- 4. FONCTION DE COMPRESSION (LE SECRET DE LA VITESSE) ---
def compresser_image(image):
    # Convertir en RGB si nécessaire
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Redimensionner si l'image est géante (plus de 1500px)
    max_size = 1500
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    return image

# --- 5. CERVEAU IA ---
def analyser(img_bytes):
    if not api_key: return "⚠️ Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """
        Tu es un assistant personnel. Sois DIRECT et CLAIR.
        Analyse ce document :
        1. 📄 C'EST QUOI ? (Type, Émetteur)
        2. 💰 PAIEMENT (Montant & Date limite en TRÈS GRAS. Sinon "Rien à payer ✅")
        3. ✅ À FAIRE (Liste simple)
        4. ⚠️ ATTENTION (Pièges éventuels)
        """
        return model.generate_content([prompt, img_bytes]).text
    except Exception as e: return f"Erreur : {e}"

# --- 6. INTERFACE ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)

st.info("💡 L'application compresse automatiquement vos photos pour aller plus vite.", icon="⚡")

# BOUTON
uploaded_file = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# LOGIQUE
if uploaded_file is not None:
    # On utilise un "status" pour montrer à l'utilisateur que ça avance
    status = st.status("🚀 Traitement en cours...", expanded=True)
    
    try:
        # ÉTAPE 1 : Chargement
        status.write("📥 Réception de l'image...")
        image_originale = Image.open(uploaded_file)
        
        # ÉTAPE 2 : Compression (C'est là qu'on gagne du temps)
        status.write("⚙️ Optimisation pour le réseau...")
        image_optimisee = compresser_image(image_originale)
        
        # ÉTAPE 3 : Envoi à l'IA
        status.write("🧠 Analyse par l'IA...")
        res = analyser(image_optimisee)
        
        status.update(label="✅ Terminé !", state="complete", expanded=False)
        
        # RÉSULTAT
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background:white; padding:20px; border-radius:15px; 
            border:3px solid #2563EB; box-shadow:0 10px 25px rgba(37,99,235,0.2); 
            margin-top:10px; animation: fadeIn 0.5s;">
            <h3 style="text-align:center; color:#2563EB; margin:0;">💡 RÉSULTAT</h3>
            <hr style="border:1px solid #EEE;">
            {res}
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        status.update(label="❌ Erreur", state="error")
        st.error(f"Erreur : {e}")
