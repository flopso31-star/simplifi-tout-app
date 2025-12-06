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

# --- 2. CSS MOBILE COMPACT & PROPRE ---
st.markdown("""
    <style>
    /* FOND & ESPACEMENT */
    .stApp { background-color: #F8F9FA; color: #333; }
    
    /* On réduit la marge du haut globalement */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 5rem !important; }

    /* === OPTIMISATION DE L'ESPACE (NOUVEAU) === */
    
    /* 1. On réduit l'espace sous le TITRE */
    .pro-header { margin-bottom: 5px !important; padding-bottom: 5px !important; }
    
    /* 2. On réduit l'espace sous les BOUTONS RADIO (Source) */
    div[data-testid="stRadio"] {
        margin-bottom: -15px !important; /* Remonte le bloc suivant */
    }
    /* On enlève le padding interne des boutons radio */
    div[data-testid="stRadio"] > div {
        gap: 0px !important;
    }

    /* ========================================= */

    /* SWITCH CAMÉRA VISIBLE */
    [data-testid="stCameraInput"] small {
        display: block !important;
        visibility: visible !important;
        font-size: 14px !important;
        background-color: white !important;
        color: #2563EB !important;
        border: 1px solid #2563EB !important;
        padding: 5px !important;
        border-radius: 15px !important;
        margin-bottom: 5px !important; /* Espace réduit */
        text-align: center !important;
        font-weight: bold !important;
    }

    /* CADRE VIDÉO */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 50vh !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 2px solid #E5E7EB;
        margin-bottom: 5px !important; /* Espace réduit */
    }

    /* BOUTON DÉCLENCHEUR */
    [data-testid="stCameraInput"] button {
       font-size: 0 !important;
       background-color: #2563EB !important;
       border: none !important;
       border-radius: 50px !important;
       height: 60px !important;
       width: 100% !important;
       position: relative !important;
    }
    [data-testid="stCameraInput"] button::after {
        content: "📸 PRENDRE LA PHOTO";
        font-size: 16px !important;
        font-weight: bold !important;
        color: white !important;
        position: absolute; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        display: block;
    }

    /* BOUTON ANALYSE */
    .stButton>button {
        background-color: #10B981; 
        color: white !important;
        height: 60px;
        font-size: 20px;
        border-radius: 12px;
        border: none;
        width: 100%;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-top: 10px !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    .pro-header {
        text-align: center; border-bottom: 1px solid #DDD;
    }
    .pro-title { font-size: 22px; font-weight: 800; color: #111; margin: 0; font-family: sans-serif; }
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

# --- 4. CERVEAU IA (MODE CHIRURGICAL) ---
def analyser(contenu):
    if not api_key: return "⛔ Clé manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        config = genai.types.GenerationConfig(temperature=0.1)
        
        prompt = f"""
        ANALYSE VISUELLE ET TEXTUELLE PRÉCISE.
        
        Extrais les infos avec précision chirurgicale (Nom entreprise, logo, etc).
        
        1. 🏢 IDENTITÉ (Obligatoire)
           - CHERCHE PARTOUT (Logo, pied de page).
           - Nom EXACT de l'entreprise/personne.
           - Type de document.

        2. 💰 ARGENT
           - Montant "Total TTC" ou "Net à payer".
           - MONTANT EXACT et DATE ÉCHÉANCE.
           - Sinon: "Aucun montant réclamé".

        3. ✅ ACTIONS (Phrases complètes)
           - Devis : "Vérifier, dater, signer..."
           - Facture : "Payer par virement..."
           - Lettre : Résumé action.

        4. ⚠️ ATTENTION
           - Pénalités ? Renouvellement auto ?
        """
        return model.generate_content([prompt, contenu], generation_config=config).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)

# ZONE RÉSULTAT EN HAUT
resultat_container = st.container()

# Message info plus discret
st.caption("ℹ️ Utilisez 'Select Device' pour la caméra arrière.")

# Menu de choix COMPACT
src = st.radio("Source", ["Caméra", "Galerie", "Texte"], horizontal=True, label_visibility="collapsed")

# --- SUPPRESSION DE L'ESPACE ICI (J'ai enlevé le st.markdown("###")) ---

entree = None
type_input = "txt"

if src == "Caméra":
    entree = st.camera_input("Photo", label_visibility="visible")
    type_input = "img"
elif src == "Galerie":
    entree = st.file_uploader("Fichier", type=['png', 'jpg', 'jpeg'])
    type_input = "img"
else:
    entree = st.text_area("Texte", height=150)
    type_input = "txt"

# Bloc d'action
if entree:
    # J'ai aussi réduit l'espace ici
    st.markdown("") 
    
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Analyse minutieuse..."):
            
            donnee = Image.open(entree) if type_input == "img" else entree
            res = analyser(donnee)
            
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
