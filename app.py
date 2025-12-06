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

# --- 2. CSS "INVISIBLE & AUTOMATIQUE" ---
st.markdown("""
    <style>
    /* FOND */
    .stApp { background-color: #F8F9FA; color: #333; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

    /* HEADER */
    .pro-header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #DDD; }
    .pro-title { font-size: 26px; font-weight: 800; color: #111; margin: 0; font-family: sans-serif; }

    /* --- LE GROS NETTOYAGE DU BOUTON UPLOAD --- */
    
    /* On cible le composant File Uploader */
    [data-testid="stFileUploader"] {
        width: 100% !important;
    }
    
    /* On cache TOUS les petits textes parasites (Limit, Drag&Drop...) */
    [data-testid="stFileUploader"] section > div:first-child span { display: none !important; }
    [data-testid="stFileUploader"] section > div:first-child small { display: none !important; }
    [data-testid="stFileUploader"] section > div:first-child div { display: none !important; }

    /* On transforme le bouton "Browse files" en GROS BOUTON UNIQUE */
    [data-testid="stFileUploader"] button {
        background-color: #2563EB !important; /* Bleu Pro */
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        width: 100% !important;
        height: 70px !important; /* Hauteur confortable */
        font-size: 0 !important; /* On cache le texte anglais */
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* On écrit le texte Français par-dessus */
    [data-testid="stFileUploader"] button::after {
        content: "📸 PRENDRE UNE PHOTO (HD)";
        font-size: 18px !important;
        font-weight: bold !important;
        color: white !important;
        display: block !important;
    }
    
    /* Une fois le fichier chargé, on cache la liste moche du fichier */
    [data-testid="stFileUploader"] ul {
        display: none !important;
    }

    /* CACHER ÉLÉMENTS INUTILES */
    #MainMenu, footer, header {visibility: hidden;}
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

# --- 4. CERVEAU IA (RAPIDE ET EFFICACE) ---
def analyser(contenu):
    if not api_key: return "⛔ Problème de clé API."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Tu es un assistant personnel. Analyse ce document pour un particulier.
        
        Réponds directement :
        1. 📄 C'EST QUOI ? (Type de courrier, Émetteur)
        2. 💰 ARGENT (Y a-t-il un montant à payer ? OUI/NON. Si OUI : Combien et Quand ?)
        3. ✅ À FAIRE (Liste simple des actions)
        4. ⚠️ ATTENTION (Seulement s'il y a un piège)
        """
        return model.generate_content([prompt, contenu]).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)

st.info("💡 Cliquez ci-dessous puis choisissez **'Appareil photo'**.", icon="📸")

# BOUTON UNIQUE (Le trigger)
uploaded_file = st.file_uploader("Upload", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# --- LOGIQUE AUTOMATIQUE (Dès que la photo est là, on lance) ---
if uploaded_file is not None:
    
    # 1. On affiche un message d'attente immédiatement
    with st.spinner("🚀 Photo reçue ! Analyse intelligente en cours..."):
        
        # 2. On traite l'image
        image = Image.open(uploaded_file)
        
        # 3. On appelle l'IA
        resultat = analyser(image)
        
        # 4. On affiche le résultat TOUT EN HAUT (Ascenseur magique)
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background-color: #FFFFFF; 
            padding: 25px; 
            border-radius: 15px; 
            border: 3px solid #2563EB; 
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2); 
            color: #333;
            animation: fadeIn 0.5s;
        ">
            <h3 style="text-align:center; color:#2563EB; margin-top:0;">💡 RÉSULTAT</h3>
            <hr style="border:1px solid #EEE;">
            {resultat}
        </div>
        """, unsafe_allow_html=True)
        
        # 5. On affiche l'image en petit en dessous pour rappel
        with st.expander("Voir la photo envoyée"):
            st.image(image, use_container_width=True)

        st.balloons()
