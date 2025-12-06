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

# --- 2. CSS "GROS BOUTON" ---
st.markdown("""
    <style>
    /* FOND */
    .stApp { background-color: #F8F9FA; color: #333; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 5rem !important; }

    /* HEADER COMPACT */
    .pro-header { text-align: center; margin-bottom: 10px; border-bottom: 1px solid #DDD; }
    .pro-title { font-size: 22px; font-weight: 800; color: #111; margin: 0; font-family: sans-serif; }

    /* TRANSFORMATION DU FILE UPLOADER EN BOUTON GÉANT */
    [data-testid="stFileUploader"] {
        width: 100% !important;
    }
    
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        background-color: transparent !important;
        border: none !important;
    }

    /* On cache le petit texte "Drag and drop" */
    [data-testid="stFileUploader"] section > div:first-child {
        display: none !important;
    }

    /* On style le bouton "Browse files" pour qu'il devienne le bouton principal */
    [data-testid="stFileUploader"] button {
        background-color: #2563EB !important; /* Bleu Pro */
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 20px !important;
        width: 100% !important;
        font-size: 0 !important; /* On cache le texte anglais */
        height: 80px !important; /* Bien haut pour être cliquable */
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3) !important;
    }

    /* On écrit le texte Français */
    [data-testid="stFileUploader"] button::after {
        content: "📸 PRENDRE UNE PHOTO (HD)";
        font-size: 18px !important;
        font-weight: bold !important;
        color: white !important;
        display: block;
        margin-top: -2px;
    }
    
    /* Le petit texte sous le bouton une fois la photo prise */
    [data-testid="stFileUploader"] small {
        display: none !important;
    }

    /* BOUTON ANALYSE (VERT) */
    .stButton>button {
        background-color: #10B981; 
        color: white !important;
        height: 60px;
        font-size: 20px;
        border-radius: 12px;
        border: none;
        width: 100%;
        font-weight: bold;
        margin-top: 10px;
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

# --- 4. CERVEAU IA (MODE PRÉCIS) ---
def analyser(contenu):
    if not api_key: return "⛔ Clé manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        config = genai.types.GenerationConfig(temperature=0.1) # Précision max
        
        prompt = f"""
        ANALYSE DE DOCUMENT (HAUTE RÉSOLUTION).
        
        1. 🏢 IDENTITÉ
           - Cherche le NOM de l'entreprise/émetteur (Logo, en-tête).
           - Type de document.

        2. 💰 ARGENT
           - Montant "Total TTC" / "Net à payer".
           - MONTANT EXACT et DATE ÉCHÉANCE.
           - Sinon: "Aucun montant réclamé".

        3. ✅ ACTIONS
           - Que doit faire l'utilisateur concrètement ?

        4. ⚠️ ATTENTION
           - Pénalités ou pièges ?
        """
        return model.generate_content([prompt, contenu], generation_config=config).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)

# ZONE RÉSULTAT EN HAUT
resultat_container = st.container()

# Note explicative
st.caption("ℹ️ Cliquez ci-dessous puis choisissez **'Appareil photo'** ou **'Caméra'** sur votre mobile pour une qualité optimale.")

# BOUTON UNIQUE (Fichier ou Caméra Natif)
fichier = st.file_uploader("Upload", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# Bloc d'action
if fichier:
    st.image(fichier, caption="Image capturée", use_container_width=True) # Affiche la photo pour vérif
    
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Lecture HD en cours..."):
            
            img = Image.open(fichier)
            res = analyser(img)
            
            with resultat_container:
                st.markdown(f"""
                <div style="
                    background-color: #FFFFFF; 
                    padding: 20px; 
                    border-radius: 15px; 
                    border: 3px solid #2563EB; 
                    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2); 
                    color: #333;
                    margin-bottom: 20px;
                ">
                    <h3 style="text-align:center; color:#2563EB; margin-top:0;">💡 RÉSULTAT</h3>
                    <hr style="border:1px solid #EEE;">
                    {res}
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
