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

# --- 2. CSS MOBILE (FIX CAMÉRA & BOUTONS) ---
st.markdown("""
    <style>
    /* Fond propre */
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

    /* CADRE VIDÉO STABLE */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: 50vh !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        border: 2px solid #E5E7EB;
        margin-bottom: 10px !important;
    }

    /* BOUTON DÉCLENCHEUR (HACK TEXTE) */
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

    /* RESTE DU DESIGN */
    .stButton>button {
        background-color: #10B981; 
        color: white !important;
        height: 55px;
        font-size: 18px;
        border-radius: 12px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    .stTextInput>div>div, .stTextArea>div>div {
        background-color: white; border: 1px solid #CCC; border-radius: 8px;
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
if "GOOGLE_
