import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LE DESIGN (CSS AVANCÉ & CORRECTIFS) ---
st.markdown("""
    <style>
    /* Fond d'écran global */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* =========================================
       CSS SPÉCIAL CAMÉRA GRAND ANGLE
    ========================================= */
    /* On cible le conteneur de la caméra */
    [data-testid="stCameraInput"] {
        width: 100%;
    }
    
    /* On cible la VIDÉO */
    [data-testid="stCameraInput"] video {
        height: 55vh !important; 
        object-fit: cover !important;
        border-radius: 20px !important;
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    /* On cible le bouton "Prendre la photo" pour qu'il soit VISIBLE */
    [data-testid="stCameraInput"] button {
       color: white !important;
       background: linear-gradient(45deg, #FF416C, #FF4B2B) !important;
       border: none !important;
       border-radius: 25px !important;
       padding: 15px 30px !important;
       font-weight: bold !important;
       margin-top: 15px !important;
       text-transform: uppercase;
       box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    /* ========================================= */


    /* Styles des autres Boutons */
    .stButton>button {
        background: linear-gradient(45deg, #FF416C, #FF4B2B);
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 15px 30px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }

    /* Inputs transparents */
    .stTextInput>div>div, .stTextArea>div>div, .stSelectbox>div>div {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Nettoyage interface */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typographie */
    h1, h2, h3 { text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION CLÉ API ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Réglages techniques")
    if api_key:
        st.success("✅ Clé API connectée")
    else:
        input_key = st.text_input("Clé API", type="password")
        if input_key:
            st.session_state.api_key = input_key
            st.rerun()

# --- FONCTION IA (CERVEAU EXPERT) ---
def analyser_contenu(content, niveau):
    if not api_key:
        return "⛔ Oups ! La clé API est manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # LE NOUVEAU PROMPT PRO
        prompt = f"""
        Tu es un expert en synthèse administrative et juridique. Niveau de détail demandé : {niveau}.
        
        Ta mission est d'analyser ce document et de produire un rapport structuré :
        
        1. 📄 IDENTIFICATION
           - Qui est l'émetteur ?
           - Quelle est la date du document ?
           - De quoi ça parle (résumé en 1 phrase simple) ?

        2. 💰 ANALYSE FINANCIÈRE
           - Y a-t-il un montant à payer ou à recevoir ? 
           - Si OUI : Écris le MONTANT et la DATE LIMITE en GRAS.
           - Si NON : Écris "Aucun mouvement financier".

        3. ✅ ACTIONS REQUISES
           - Liste les actions concrètes à effectuer (To-Do List).
           - Si aucune action : précise "Document à classer".

        4. ⚠️ VIGILANCE (PIÈGES)
           - Signale s'il y a des pénalités, des renouvellements automatiques ou des conditions en petits caractères.

        Ton ton doit être professionnel, rassurant et synthétique.
        """
        
        response = model.generate_content([prompt, content])
        return response.text
    except Exception as e:
        return f"Erreur technique : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("✨ Simplifi Tout")
st.caption("Votre Expert Administratif de Poche")

st.markdown("###") 

# 1. CHOIX DE LA SOURCE
source_image = st.radio(
    "Action :",
    ["📸 Caméra", "🖼️ Galerie", "✍️ Texte"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("###") 

entree = None
type_entree = None

# 2. AFFICHAGE DE L'INPUT
if source_image == "📸 Caméra":
    entree = st.camera_input("Prendre la photo", label_visibility="collapsed")
    type_entree = "img"
elif source_image == "🖼️ Galerie":
    entree = st.file_uploader("Fichier", type=['png', 'jpg'])
    type_entree = "img"
else:
    entree = st.text_area("Copier-coller le texte", height=150)
    type_entree = "txt"

# 3. LE BLOC D'ACTION
if entree:
    st.markdown("###")
    st.markdown("##### 🎚️ Niveau d'expertise")
    niveau_simplification = st.select_slider(
        "Niveau de détail",
        options=["Synthèse Rapide", "Normal", "Analyse Détaillée"],
        label_visibility="collapsed"
    )
    
    st.markdown("###")
    
    if st.button("✨ LANCER L'ANALYSE ✨"):
        with st.spinner("🧐 L'expert analyse votre document..."):
            if type_entree == "img":
                img = Image.open(entree)
                res = analyser_contenu(img, niveau_simplification)
            else:
                res = analyser_contenu(entree, niveau_simplification)
            
            st.markdown("---")
            # Affichage du résultat dans une boîte stylisée
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #FF4B2B;">
                {res}
            </div>
            """, unsafe_allow_html=True)
