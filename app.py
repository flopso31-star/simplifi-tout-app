import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LE DESIGN (CSS ROBUSTE) ---
st.markdown("""
    <style>
    /* 1. SUPPRESSION DES MARGES */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* 2. FOND D'ÉCRAN PRO */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    /* 3. CSS SPÉCIAL CAMÉRA (ANTI-RÉTRÉCISSEMENT) */
    
    /* On force le bloc global de la caméra à prendre 60% de la hauteur de l'écran */
    [data-testid="stCameraInput"] {
        width: 100% !important;
        min-height: 60vh !important; /* Hauteur minimale forcée */
    }
    
    /* On force la vidéo à remplir ce bloc sans changer de ratio */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 60vh !important; /* Force la hauteur fixe */
        object-fit: cover !important; /* Remplit tout le cadre (zoomé) */
        border-radius: 12px !important;
        border: 1px solid #444;
    }
    
    /* On s'assure que le conteneur interne ne s'écrase pas */
    [data-testid="stCameraInput"] > div {
        height: 60vh !important;
    }
    
    /* Bouton Photo : Visible et Gros */
    [data-testid="stCameraInput"] button {
       color: white !important;
       background-color: #2563EB !important;
       border: none !important;
       border-radius: 8px !important;
       padding: 15px 30px !important;
       font-weight: 600 !important;
       font-size: 16px !important;
       margin-top: 15px !important;
       text-transform: uppercase;
       width: 100%; /* Bouton pleine largeur pour faciliter le clic */
    }

    /* 4. BOUTON ANALYSE */
    .stButton>button {
        background-color: #2563EB;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 15px 0px;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
        margin-top: 20px;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }

    /* 5. Inputs et Cadres */
    .stTextInput>div>div, .stTextArea>div>div, .stSelectbox>div>div {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #41424C;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Titre Custom */
    .pro-header {
        text-align: center;
        margin-bottom: 10px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }
    .pro-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
        margin: 0;
        font-family: sans-serif;
    }
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
    st.header("Paramètres")
    if api_key:
        st.success("Système connecté")
    else:
        input_key = st.text_input("Clé API", type="password")
        if input_key:
            st.session_state.api_key = input_key
            st.rerun()

# --- FONCTION IA ---
def analyser_contenu(content, niveau):
    if not api_key:
        return "⛔ Erreur : Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Agis en tant qu'expert juridique. Niveau : {niveau}.
        Analyse ce document :
        1. IDENTIFICATION (Qui ? Quoi ? Date ?)
        2. FINANCES (Montant dû ? Échéance ? -> EN GRAS)
        3. ACTIONS (Liste à puces des tâches)
        4. PIÈGES (Conditions cachées ?)
        Style : Direct et Pro.
        """
        
        response = model.generate_content([prompt, content])
        return response.text
    except Exception as e:
        return f"Erreur système : {str(e)}"

# --- INTERFACE ---
st.markdown("""
<div class="pro-header">
    <h1 class="pro-title">SIMPLIFI TOUT</h1>
</div>
""", unsafe_allow_html=True)

# Note pour la caméra arrière
st.info("💡 Astuce : Si la caméra est inversée, changez-la via le menu 'Select Device' qui apparaît sur la caméra.", icon="🔄")

source_image = st.radio(
    "Source :",
    ["Caméra", "Galerie", "Texte"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("###") 

entree = None
type_entree = None

if source_image == "Caméra":
    # On force le label collapsed pour gagner de la place
    entree = st.camera_input("Prendre la photo", label_visibility="collapsed")
    type_entree = "img"
elif source_image == "Galerie":
    entree = st.file_uploader("Importer", type=['png', 'jpg', 'pdf'])
    type_entree = "img"
else:
    entree = st.text_area("Texte", height=150)
    type_entree = "txt"

if entree:
    st.markdown("###")
    niveau_simplification = st.select_slider(
        "Niveau d'analyse",
        options=["Synthèse", "Standard", "Détaillé"],
    )
    
    st.markdown("###")
    
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Analyse en cours..."):
            if type_entree == "img":
                img = Image.open(entree)
                res = analyser_contenu(img, niveau_simplification)
            else:
                res = analyser_contenu(entree, niveau_simplification)
            
            st.markdown("---")
            st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 20px; border-radius: 8px; border-left: 4px solid #2563EB; color: #E0E0E0;">
                {res}
            </div>
            """, unsafe_allow_html=True)
