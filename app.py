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

# --- DESIGN "LIGHT MODE" & CORRECTIF CAMÉRA ---
st.markdown("""
    <style>
    /* 1. FOND D'ÉCRAN CLAIR (Style Bancaire/Pro) */
    .stApp {
        background-color: #F8F9FA; /* Gris très très clair */
        color: #31333F; /* Gris foncé pour le texte */
    }

    /* 2. CORRECTION CAMÉRA (Le bouton ne gêne plus) */
    [data-testid="stCameraInput"] {
        width: 100% !important;
    }
    
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 50vh !important; /* Hauteur fixe */
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 2px solid #E0E0E0; /* Bordure claire */
        margin-bottom: 10px !important; /* Espace SOUS la vidéo */
    }
    
    /* Bouton Photo : SOUS la vidéo et en Français via CSS propre */
    [data-testid="stCameraInput"] button {
       font-size: 0 !important; /* On cache le texte anglais */
       background-color: #2563EB !important; /* Bleu Pro */
       border: none !important;
       border-radius: 50px !important; /* Bien arrondi */
       padding: 20px !important;
       width: 100% !important;
       margin-top: 5px !important;
    }
    
    /* On réécrit le texte en Français proprement */
    [data-testid="stCameraInput"] button::after {
        content: "📸 PRENDRE LA PHOTO";
        font-size: 16px !important;
        color: white !important;
        display: block;
    }

    /* 3. INPUTS ET CADRES (Sur fond blanc) */
    .stTextInput>div>div, .stTextArea>div>div, .stSelectbox>div>div {
        background-color: #FFFFFF; /* Fond blanc */
        color: #31333F;
        border-radius: 8px;
        border: 1px solid #D1D5DB; /* Bordure grise */
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* 4. TRADUCTION BOUTON GALERIE (BROWSE FILES) */
    [data-testid="stFileUploader"] button {
        font-size: 0 !important;
        background-color: #2563EB !important;
        border: none;
        border-radius: 8px;
        width: 100%;
        height: 50px;
    }
    [data-testid="stFileUploader"] button::after {
        content: "📂 CHOISIR UN FICHIER";
        font-size: 16px;
        color: white;
        display: block;
    }
    /* Cache le petit texte drag & drop */
    [data-testid="stFileUploader"] section > div:first-child span { display: none; }
    [data-testid="stFileUploader"] section > div:first-child small { display: none; }


    /* 5. BOUTON D'ANALYSE */
    .stButton>button {
        background-color: #10B981; /* Vert "Validation" pour différencier */
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 15px 0px;
        font-size: 18px;
        font-weight: 700;
        width: 100%;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
    }
    .stButton>button:hover {
        background-color: #059669;
    }

    /* Nettoyage */
    .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; }
    #MainMenu, footer, header {visibility: hidden;}

    /* Header Pro */
    .pro-header {
        text-align: center;
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 2px solid #E5E7EB;
    }
    .pro-title {
        font-size: 26px;
        font-weight: 800;
        color: #111827; /* Noir profond */
        margin: 0;
        font-family: sans-serif;
        letter-spacing: -0.5px;
    }
    .pro-subtitle {
        font-size: 14px;
        color: #6B7280; /* Gris moyen */
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
    st.header("⚙️ Paramètres")
    if api_key:
        st.success("✅ Système connecté")
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
        Rôle : Expert administratif. Niveau : {niveau}.
        Langue : Français.
        
        Analyse le document :
        1. 📄 DOCUMENT (Nature, Date, Émetteur)
        2. 💰 PAIEMENT (Montant et Date limite -> EN GRAS. Sinon "Aucun")
        3. ✅ À FAIRE (Liste d'actions claires)
        4. ⚠️ ATTENTION (Conditions pièges)
        """
        
        response = model.generate_content([prompt, content])
        return response.text
    except Exception as e:
        return f"Erreur : {str(e)}"

# --- INTERFACE ---
st.markdown("""
<div class="pro-header">
    <h1 class="pro-title">Simplifi Tout</h1>
    <p class="pro-subtitle">L'administratif devient facile</p>
</div>
""", unsafe_allow_html=True)

# Menu Source
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
    entree = st.camera_input("Photo", label_visibility="collapsed")
    type_entree = "img"
elif source_image == "Galerie":
    entree = st.file_uploader("Fichier", type=['png', 'jpg', 'pdf'])
    type_entree = "img"
else:
    entree = st.text_area("Collez votre texte ici", height=150)
    type_entree = "txt"

if entree:
    st.markdown("###")
    niveau_simplification = st.select_slider(
        "Niveau de détail",
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
            # Résultat sur fond Blanc avec bordure bleue (Style Papier)
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #E5E7EB; box-shadow: 0 4px 6px rgba(0,0,0,0.05); color: #374151;">
                {res}
            </div>
            """, unsafe_allow_html=True)
