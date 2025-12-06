import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIG ---
st.set_page_config(page_title="Simplifi Tout", page_icon="📄", layout="centered", initial_sidebar_state="collapsed")

# --- CSS BULLDOZER ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; color: #333; }
    .block-container { padding-top: 1rem !important; }

    /* CACHER LE HEADER ET FOOTER */
    header, footer, #MainMenu { visibility: hidden !important; }

    /* === LE GROS BOUTON PHOTO (NETTOYAGE COMPLET) === */
    
    /* 1. On cible la zone de dépôt */
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        background-color: transparent !important;
        border: none !important;
    }

    /* 2. ON REND TOUT LE TEXTE INVISIBLE DANS CETTE ZONE */
    [data-testid="stFileUploader"] section > div, 
    [data-testid="stFileUploader"] section span, 
    [data-testid="stFileUploader"] section small {
        color: transparent !important; /* Texte invisible */
        font-size: 0px !important;     /* Taille zéro */
    }

    /* 3. ON NE GARDE QUE LE BOUTON ET ON LE CUSTOMISE */
    [data-testid="stFileUploader"] button {
        visibility: visible !important; /* Lui, on le voit */
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important; /* Très rond */
        width: 100% !important;
        height: 80px !important;
        font-size: 0px !important; /* On cache le texte "Browse files" */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: -30px !important; /* Remonte pour couvrir le vide */
    }

    /* 4. ON ÉCRIT LE NOUVEAU TEXTE PAR DESSUS */
    [data-testid="stFileUploader"] button::after {
        content: "📸 PRENDRE UNE PHOTO (HD)";
        font-size: 18px !important;
        font-weight: bold !important;
        color: white !important;
        visibility: visible !important;
    }
    
    /* 5. Une fois le fichier chargé, on cache la liste moche */
    [data-testid="stFileUploader"] ul { display: none !important; }
    
    /* HEADER TITRE */
    .pro-header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #DDD; }
    .pro-title { font-size: 26px; font-weight: 800; color: #111; margin: 0; font-family: sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- CLÉ API ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

with st.sidebar:
    if not api_key:
        k = st.text_input("Clé API", type="password")
        if k: st.session_state.api_key = k; st.rerun()

# --- IA ---
def analyser(img):
    if not api_key: return "⚠️ Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """Assistant perso. Analyse pour un particulier :
        1. 📄 C'EST QUOI ? (Type, Émetteur)
        2. 💰 ARGENT (Montant & Date limite en GRAS. Sinon "Rien à payer")
        3. ✅ À FAIRE (Liste actions simples)
        4. ⚠️ ATTENTION (Pièges éventuels)"""
        return model.generate_content([prompt, img]).text
    except Exception as e: return f"Erreur : {e}"

# --- APP ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)

# LE DÉCLENCHEUR
uploaded_file = st.file_uploader(" ", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# --- AUTO-START (Dès qu'il y a un fichier, ça part) ---
if uploaded_file:
    # Petit message visuel pour dire "J'ai compris"
    st.toast("📸 Photo reçue ! Analyse en cours...", icon="🚀")
    
    with st.spinner("Le cerveau de l'IA réfléchit..."):
        try:
            image = Image.open(uploaded_file)
            res = analyser(image)
            
            # AFFICHAGE DU RÉSULTAT EN HAUT
            st.markdown(f"""
            <div style="background:white; padding:20px; border-radius:15px; border:3px solid #2563EB; box-shadow:0 10px 25px rgba(37,99,235,0.2); margin-top:20px; animation: fadeIn 0.5s;">
                <h3 style="text-align:center; color:#2563EB; margin:0;">💡 RÉSULTAT</h3>
                <hr style="border:1px solid #EEE;">
                {res}
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
            
        except Exception as e:
            st.error("Erreur de lecture de l'image. Réessayez.")
