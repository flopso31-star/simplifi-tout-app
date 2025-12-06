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

# --- 2. CSS MOBILE (CLEAN & VISIBLE) ---
st.markdown("""
    <style>
    /* FOND & ESPACEMENT */
    .stApp { background-color: #F8F9FA; color: #333; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

    /* SWITCH CAMÉRA VISIBLE */
    [data-testid="stCameraInput"] small {
        display: block !important;
        visibility: visible !important;
        font-size: 14px !important;
        background-color: white !important;
        color: #2563EB !important;
        border: 1px solid #2563EB !important;
        padding: 8px !important;
        border-radius: 20px !important;
        margin-bottom: 5px !important;
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
        margin-bottom: 10px !important;
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

    /* BOUTON ANALYSE (VERT) */
    .stButton>button {
        background-color: #10B981; 
        color: white !important;
        height: 60px;
        font-size: 20px; /* Plus gros */
        border-radius: 12px;
        border: none;
        width: 100%;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* CACHER ÉLÉMENTS INUTILES */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* TITRE */
    .pro-header {
        text-align: center; margin-bottom: 10px; border-bottom: 2px solid #DDD; padding-bottom: 10px;
    }
    .pro-title { font-size: 24px; font-weight: 800; color: #111; margin: 0; font-family: sans-serif; }
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

# --- 4. CERVEAU IA (PROMPT UNIVERSEL) ---
def analyser(contenu):
    if not api_key: return "⛔ Clé manquante. Vérifiez les paramètres."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # PROMPT SIMPLIFIÉ "Monsieur et Madame tout le monde"
        prompt = f"""
        Tu es un assistant personnel bienveillant.
        Ta mission : Lire ce document et l'expliquer le plus simplement possible à quelqu'un qui déteste l'administratif.
        
        Réponds directement (sans phrases d'intro) avec cette structure :
        
        1. 📄 C'EST QUOI ? (En 1 phrase simple : Qui écrit et pourquoi ?)
        2. 💰 ARGENT (Y a-t-il quelque chose à payer ? Si OUI : Affiche le MONTANT et la DATE LIMITE en TRÈS GRAS et GROS. Si NON : Écris "Rien à payer ✅")
        3. ✅ À FAIRE (Liste les actions. Si rien à faire, dis "Tu peux classer ce document 📂")
        4. ⚠️ ATTENTION (S'il y a un piège ou une pénalité, dis-le clairement. Sinon n'écris rien.)
        
        Ton ton doit être clair, rassurant et direct.
        """
        return model.generate_content([prompt, contenu]).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)

# --- ASTUCE UX : ON CRÉE LA ZONE DE RÉSULTAT ICI, TOUT EN HAUT ---
resultat_container = st.container()
# ---------------------------------------------------------------

st.info("👆 Changez de caméra via 'Select Device' si besoin.", icon="ℹ️")

# Menu de choix
src = st.radio("Source", ["Caméra", "Galerie", "Texte"], horizontal=True, label_visibility="collapsed")
st.markdown("###")

entree = None
type_input = "txt"

# Logique d'affichage
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
    # PLUS DE SLIDER ! On va droit au but.
    st.markdown("###")
    
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Lecture du document en cours..."):
            
            # Préparation
            donnee_a_envoyer = Image.open(entree) if type_input == "img" else entree
            
            # Analyse
            res = analyser(donnee_a_envoyer)
            
            # --- AFFICHAGE MAGIQUE EN HAUT DE PAGE ---
            with resultat_container:
                st.markdown(f"""
                <div style="
                    background-color: #FFFFFF; 
                    padding: 25px; 
                    border-radius: 15px; 
                    border: 3px solid #2563EB; 
                    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2); 
                    color: #333;
                    margin-bottom: 20px;
                    animation: fadeIn 0.5s;
                ">
                    <h3 style="text-align:center; color:#2563EB; margin-top:0;">💡 RÉSULTAT</h3>
                    <hr style="border:1px solid #EEE;">
                    {res}
                </div>
                """, unsafe_allow_html=True)
                
                # Petit message de succès pour confirmer que ça a marché
                st.balloons()

