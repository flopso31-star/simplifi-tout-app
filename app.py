import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuration de la page
st.set_page_config(page_title="Simplifi Tout", page_icon="✨", layout="centered")

# --- BARRE LATÉRALE (Configuration) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    # On vérifie si la clé est déjà en mémoire pour ne pas la retaper à chaque fois
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    api_key = st.text_input("Clé API Google", value=st.session_state.api_key, type="password")
    
    if api_key:
        st.session_state.api_key = api_key

    st.info("Clé nécessaire (AIza...)")
    st.markdown("---")
    niveau_simplification = st.select_slider(
        "Niveau de simplification",
        options=["Normal", "Explique-moi comme si j'avais 5 ans", "Ultra Bref"]
    )

# --- FONCTION D'INTELLIGENCE ---
def analyser_contenu(content, niveau):
    if not api_key:
        return "⚠️ Il manque la clé API dans le menu de gauche !"
    
    try:
        genai.configure(api_key=api_key)
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
        return f"Oups, une erreur : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("✨ Simplifi Tout")

# On enlève les onglets pour une interface mobile plus directe
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
    # Le composant Caméra direct
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
    # Si c'est une image, on l'affiche pour confirmer
    if type_entree == "image":
        image_a_traiter = Image.open(entree_utilisateur)
        # Pas besoin de bouton supplémentaire pour la caméra, c'est plus fluide
        if st.button("🚀 Analyser maintenant", type="primary", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                resultat = analyser_contenu(image_a_traiter, niveau_simplification)
                st.success("Analyse terminée !")
                st.markdown(resultat)
    
    # Si c'est du texte
    else:
        if st.button("🚀 Analyser le texte", type="primary", use_container_width=True):
            with st.spinner("Lecture en cours..."):
                resultat = analyser_contenu(entree_utilisateur, niveau_simplification)
                st.success("Terminé !")
                st.markdown(resultat)