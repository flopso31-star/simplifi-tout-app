import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Simplifi Tout",
    page_icon="📄", # Fini les étoiles, place au dossier
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LE DESIGN "CORPORATE" (CSS) ---
st.markdown("""
    <style>
    /* 1. SUPPRESSION DES MARGES DU HAUT (Logo trop bas) */
    .block-container {
        padding-top: 1rem !important; /* On remonte tout vers le haut */
        padding-bottom: 1rem !important;
    }

    /* 2. FOND D'ÉCRAN PRO (Gris Anthracite / Bleu Nuit) */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    /* 3. CSS SPÉCIAL CAMÉRA (Grand format) */
    [data-testid="stCameraInput"] { width: 100%; }
    
    [data-testid="stCameraInput"] video {
        height: 50vh !important; 
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 1px solid #333;
    }
    
    /* Bouton Photo : Sobre et Visible */
    [data-testid="stCameraInput"] button {
       color: white !important;
       background-color: #2563EB !important; /* Bleu "Tech" */
       border: none !important;
       border-radius: 8px !important; /* Coins moins ronds, plus carrés */
       padding: 12px 25px !important;
       font-weight: 600 !important;
       margin-top: 10px !important;
       text-transform: uppercase;
    }

    /* 4. BOUTON PRINCIPAL (ANALYSE) */
    .stButton>button {
        background-color: #2563EB;
        color: white !important;
        border: none;
        border-radius: 8px; /* Look plus sérieux */
        padding: 15px 0px;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.5px;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #1D4ED8; /* Bleu plus foncé au survol */
    }

    /* 5. Inputs et Cadres */
    .stTextInput>div>div, .stTextArea>div>div, .stSelectbox>div>div {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #41424C;
    }
    
    /* Nettoyage interface */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Titre Custom */
    .pro-header {
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #333;
    }
    .pro-title {
        font-size: 26px;
        font-weight: 700;
        color: white;
        margin: 0;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .pro-subtitle {
        font-size: 14px;
        color: #A0A0A0;
        margin-top: 5px;
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

# --- FONCTION IA (PROMPT STRICT) ---
def analyser_contenu(content, niveau):
    if not api_key:
        return "⛔ Erreur : Clé API manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Agis en tant qu'expert juridique et administratif. Niveau d'analyse : {niveau}.
        
        Analyse le document fourni et produis une synthèse formelle :
        
        1. IDENTIFICATION DU DOCUMENT
           - Émetteur / Destinataire
           - Date et Objet
           
        2. SYNTHÈSE FINANCIÈRE (CRITIQUE)
           - Y a-t-il un montant dû ? Si OUI : Affiche le MONTANT et l'ÉCHÉANCE en GRAS.
           - Si NON : Indique "Aucune action financière requise".

        3. ACTIONS À ENTREPRENDRE
           - Liste numérotée des démarches à effectuer.
           
        4. POINTS DE VIGILANCE
           - Clauses particulières, pénalités ou délais stricts.

        Ton style doit être direct, neutre et professionnel. Pas de familiarités.
        """
        
        response = model.generate_content([prompt, content])
        return response.text
    except Exception as e:
        return f"Erreur système : {str(e)}"

# --- INTERFACE PRINCIPALE (HEADER CUSTOM) ---
st.markdown("""
<div class="pro-header">
    <h1 class="pro-title">SIMPLIFI TOUT</h1>
    <p class="pro-subtitle">Analyseur de documents administratifs</p>
</div>
""", unsafe_allow_html=True)

# 1. CHOIX DE LA SOURCE
source_image = st.radio(
    "Source :",
    ["Caméra", "Galerie", "Texte"], # Texte simple, sans émojis
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("###") 

entree = None
type_entree = None

# 2. AFFICHAGE DE L'INPUT
if source_image == "Caméra":
    entree = st.camera_input("Prendre la photo", label_visibility="collapsed")
    type_entree = "img"
elif source_image == "Galerie":
    entree = st.file_uploader("Importer un fichier", type=['png', 'jpg', 'pdf'])
    type_entree = "img"
else:
    entree = st.text_area("Saisir le texte", height=150)
    type_entree = "txt"

# 3. LE BLOC D'ACTION
if entree:
    st.markdown("###")
    # Slider plus discret
    niveau_simplification = st.select_slider(
        "Profondeur d'analyse",
        options=["Synthèse", "Standard", "Détaillé"],
        label_visibility="visible" 
    )
    
    st.markdown("###")
    
    # Bouton sobre
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Traitement en cours..."):
            if type_entree == "img":
                img = Image.open(entree)
                res = analyser_contenu(img, niveau_simplification)
            else:
                res = analyser_contenu(entree, niveau_simplification)
            
            st.markdown("---")
            # Résultat sobre (Gris foncé sur fond noir)
            st.markdown(f"""
            <div style="background-color: #1E1E1E; padding: 20px; border-radius: 8px; border-left: 4px solid #2563EB; color: #E0E0E0;">
                {res}
            </div>
            """, unsafe_allow_html=True)
