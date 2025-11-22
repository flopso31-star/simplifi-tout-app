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

# --- LE DESIGN (CSS AVANCÉ) ---
st.markdown("""
    <style>
    /* Fond d'écran global */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* =========================================
       NOUVEAU : CSS SPÉCIAL CAMÉRA GRAND ANGLE
    ========================================= */
    /* On cible le conteneur de la caméra Streamlit */
    [data-testid="stCameraInput"] {
        width: 100%; /* Prend toute la largeur */
    }
    
    /* On cible spécifiquement l'élément VIDÉO à l'intérieur */
    [data-testid="stCameraInput"] video {
        /* On force une hauteur de 55% de l'écran du téléphone */
        height: 55vh !important; 
        /* On s'assure que l'image remplit bien le cadre sans être déformée */
        object-fit: cover !important;
        border-radius: 20px !important;
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
   /* On cible le bouton "Prendre la photo" SOUS la vidéo */
    [data-testid="stCameraInput"] button {
       color: white !important;  /* Texte blanc */
       background: linear-gradient(45deg, #FF416C, #FF4B2B) !important; /* Fond coloré */
       border: none !important;
       border-radius: 25px !important;
       padding: 15px 30px !important;
       font-weight: bold !important;
       margin-top: 15px !important;
       text-transform: uppercase; /* Met le texte en majuscules pour être bien lisible */
       box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    /* ========================================= */


    /* Styles des autres Boutons (Lancer l'analyse) */
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
    
    /* Cacher éléments inutiles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Centrer les titres */
    h1, h2, h3 { text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION CLÉ API ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

# --- BARRE LATÉRALE (Clé uniquement) ---
with st.sidebar:
    st.header("⚙️ Réglages techniques")
    if api_key:
        st.success("✅ Clé API connectée")
    else:
        input_key = st.text_input("Clé API", type="password")
        if input_key:
            st.session_state.api_key = input_key
            st.rerun()

# --- FONCTION IA ---
def analyser_contenu(content, niveau):
    if not api_key:
        return "⛔ Oups ! La clé API est manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"Tu es un assistant expert. Niveau de simplification demandé : {niveau}. Résume ce document, dis s'il y a un paiement (en GRAS), et liste les actions à faire. Sois joli et utilise des émojis."
        response = model.generate_content([prompt, content])
        return response.text
    except Exception as e:
        return f"Erreur: {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("✨ Simplifi Tout")
st.caption("Votre assistant administratif personnel")

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

# 2. AFFICHAGE DE L'INPUT (Caméra agrandie par CSS)
if source_image == "📸 Caméra":
    # Le label est caché pour gagner de la place
    entree = st.camera_input("Prendre la photo", label_visibility="collapsed")
    type_entree = "img"
elif source_image == "🖼️ Galerie":
    entree = st.file_uploader("Fichier", type=['png', 'jpg'])
    type_entree = "img"
else:
    entree = st.text_area("Texte à analyser", height=150)
    type_entree = "txt"

# 3. LE BLOC D'ACTION
if entree:
    st.markdown("###")
    st.markdown("##### 🎚️ Niveau de détail")
    niveau_simplification = st.select_slider(
        "Niveau de détail",
        options=["Enfant (5 ans)", "Normal", "Expert"],
        label_visibility="collapsed"
    )
    
    st.markdown("###")
    
    if st.button("✨ LANCER L'ANALYSE ✨"):
        with st.spinner("🧠 Analyse en cours..."):
            if type_entree == "img":
                img = Image.open(entree)
                res = analyser_contenu(img, niveau_simplification)
            else:
                res = analyser_contenu(entree, niveau_simplification)
            
            st.markdown("---")
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #FF4B2B;">
                {res}
            </div>
            """, unsafe_allow_html=True)

