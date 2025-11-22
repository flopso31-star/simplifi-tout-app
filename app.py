import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuration de la page
st.set_page_config(page_title="Simplifi Tout", page_icon="✨", layout="centered")

# --- GESTION INTELLIGENTE DE LA CLÉ API ---
api_key = None

# 1. D'abord, on regarde dans le coffre-fort du Cloud (Secrets)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

# 2. Sinon, on regarde dans la mémoire de session (si l'utilisateur l'a déjà rentrée)
elif "api_key" in st.session_state:
    api_key = st.session_state.api_key

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Si la clé a été trouvée automatiquement
    if api_key:
        st.success("✅ Clé API connectée !")
        st.caption("Mode : Sécurisé Cloud")
    else:
        # Sinon, on affiche le champ pour la rentrer manuellement
        input_key = st.text_input("Entrez votre clé API (AIza...)", type="password")
        if input_key:
            st.session_state.api_key = input_key
            api_key = input_key
            st.rerun() # On recharge la page pour valider

    st.markdown("---")
    niveau_simplification = st.select_slider(
        "Niveau de simplification",
        options=["Normal", "Explique-moi comme si j'avais 5 ans", "Ultra Bref"]
    )

# --- FONCTION D'INTELLIGENCE ---
def analyser_contenu(content, niveau):
    if not api_key:
        return "⛔ ERREUR : Impossible de trouver une clé API. Vérifiez les Secrets ou entrez-la manuellement."
    
    try:
        genai.configure(api_key=api_key)
        # On utilise le modèle Flash qui est rapide et gratuit
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt_systeme = f"""
        Tu es l'intelligence 'Simplifi Tout'.
        Niveau : {niveau}
        
        Tâche :
        1. Résume ce document en 2 phrases claires.
        2. Y a-t-il quelque chose à payer ou une date limite ? (Si oui, mets-le en GRAS).
        3. Liste les actions à faire sous forme de "To-Do List".
        
        Réponse courte, directe et avec des émojis.
        """
        
        response = model.generate_content([prompt_systeme, content])
        return response.text

    except Exception as e:
        return f"Oups, une erreur technique : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("✨ Simplifi Tout")
st.markdown("### 📸 Scanner un document")

# Choix de la méthode
source_image = st.radio(
    "Source :",
    ["Prendre une photo (Caméra)", "Importer depuis la Galerie", "Coller du Texte"],
    horizontal=True,
    label_visibility="collapsed" 
)

entree_utilisateur = None
type_entree = None

if source_image == "Prendre une photo (Caméra)":
    entree_utilisateur = st.camera_input("Cadrez le document", label_visibility="collapsed")
    type_entree = "image"

elif source_image == "Importer depuis la Galerie":
    entree_utilisateur = st.file_uploader("Choisir une image", type=['png', 'jpg', 'jpeg'])
    type_entree = "image"

elif source_image == "Coller du Texte":
    entree_utilisateur = st.text_area("Collez le texte ici", height=150)
    type_entree = "text"

# --- BOUTON D'ACTION ---
if entree_utilisateur:
    if type_entree == "image":
        image_a_traiter = Image.open(entree_utilisateur)
        if st.button("🚀 Analyser maintenant", type="primary", use_container_width=True):
            with st.spinner("Le cerveau de l'IA s'active..."):
                resultat = analyser_contenu(image_a_traiter, niveau_simplification)
                if "ERREUR" in resultat:
                    st.error(resultat)
                else:
                    st.success("Analyse terminée !")
                    st.markdown(resultat)
    
    else: # Texte
        if st.button("🚀 Analyser le texte", type="primary", use_container_width=True):
            with st.spinner("Lecture en cours..."):
                resultat = analyser_contenu(entree_utilisateur, niveau_simplification)
                st.markdown(resultat)