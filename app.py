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

# --- 2. CSS MOBILE OPTIMISÉ ---
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
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
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

# --- 4. CERVEAU IA (MODE CHIRURGICAL) ---
def analyser(contenu):
    if not api_key: return "⛔ Clé manquante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # CONFIGURATION STRICTE : On réduit la créativité pour augmenter la précision
        config = genai.types.GenerationConfig(
            temperature=0.1 # Très bas = Très factuel/précis
        )

        # PROMPT RENFORCÉ
        prompt = f"""
        ANALYSE VISUELLE ET TEXTUELLE PRÉCISE.
        
        Tu dois extraire les informations de ce document avec une précision chirurgicale.
        Ne sois pas vague. Sois explicite.

        1. 🏢 IDENTITÉ DE L'ÉMETTEUR (Obligatoire)
           - CHERCHE PARTOUT : Regarde le logo en haut, le pied de page, ou l'adresse.
           - Écris le NOM EXACT de l'entreprise ou de la personne.
           - Quel est le type de document ? (Devis, Facture, Lettre, Relance...)

        2. 💰 ARGENT ET CHIFFRES
           - Cherche le montant "Total TTC" ou "Net à payer".
           - Écris le MONTANT EXACT et la DATE D'ÉCHÉANCE.
           - S'il n'y a rien à payer, écris explicitement : "Aucun montant réclamé".

        3. ✅ ACTIONS CONCRÈTES (Pas de symboles seuls !)
           - Ne mets pas juste une icône "validé".
           - Si c'est un DEVIS : Écris "Vérifier les détails, dater, signer avec la mention 'Bon pour accord' et renvoyer."
           - Si c'est une FACTURE : Écris "Effectuer le virement sur l'IBAN indiqué avant la date limite."
           - Si c'est une LETTRE : Résume ce qu'on attend de l'utilisateur.

        4. ⚠️ ATTENTION
           - Lis les petits caractères : y a-t-il des pénalités de retard ? Un renouvellement automatique ?
        
        Formate la réponse proprement pour qu'elle soit lisible sur mobile.
        """
        return model.generate_content([prompt, contenu], generation_config=config).text
    except Exception as e: return f"Erreur : {e}"

# --- 5. INTERFACE ---
st.markdown('<div class="pro-header"><h1 class="pro-title">Simplifi Tout</h1></div>', unsafe_allow_html=True)

# ZONE RÉSULTAT EN HAUT
resultat_container = st.container()

st.info("👆 Changez de caméra via 'Select Device' si besoin.", icon="ℹ️")

# Menu de choix
src = st.radio("Source", ["Caméra", "Galerie", "Texte"], horizontal=True, label_visibility="collapsed")
st.markdown("###")

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
    st.markdown("###")
    
    if st.button("LANCER L'ANALYSE"):
        with st.spinner("Lecture minutieuse du document..."):
            
            donnee_a_envoyer = Image.open(entree) if type_input == "img" else entree
            res = analyser(donnee_a_envoyer)
            
            # AFFICHAGE
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
                    <h3 style="text-align:center; color:#2563EB; margin-top:0;">💡 RÉSULTAT DÉTAILLÉ</h3>
                    <hr style="border:1px solid #EEE;">
                    {res}
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
