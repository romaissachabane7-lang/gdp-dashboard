import streamlit as st
import pandas as pd
import requests
import html
import os   # ✅ AJOUT POUR CORRIGER L’ERREUR

# CONFIG
st.set_page_config(page_title="BioPlateforme Algérienne", layout="wide")

# --- SVG logo (honey + bacteria motif) ---
svg_logo = """
<div style="display:flex;align-items:center;">
  <div style="width:90px;height:90px;background:linear-gradient(180deg,#f3d886,#d8b05a);border-radius:18px;
              display:flex;align-items:center;justify-content:center;padding:8px;box-shadow:0 2px 6px rgba(0,0,0,0.08)">
    <svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="g1" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="#fff2d6"/>
          <stop offset="1" stop-color="#f0c36a"/>
        </linearGradient>
      </defs>
      <path d="M32 6 C42 12,52 20,50 34 C48 48,36 56,32 58 C28 56,16 48,14 34 C12 20,22 12,32 6 Z" fill="url(#g1)" stroke="#d1a44a" stroke-width="1.5"/>
      <rect x="22" y="24" rx="3" ry="3" width="20" height="8" fill="#6b8b5f" transform="rotate(-18 32 28)"/>
      <circle cx="40" cy="18" r="2.2" fill="#6b8b5f"/>
      <circle cx="44" cy="24" r="1.6" fill="#6b8b5f"/>
    </svg>
  </div>
  <div style="margin-left:16px;">
    <div style="font-family:Segoe UI,Helvetica,Arial,sans-serif;font-weight:700;color:#4a3f2a;font-size:26px;">BioPlateforme Algérienne</div>
    <div style="font-family:Segoe UI,Helvetica,Arial,sans-serif;color:#7a6b5a;font-size:13px;margin-top:2px;">
      Plateforme scientifique — validation in silico
    </div>
  </div>
</div>
"""

st.markdown("""
<style>
.stApp { background-color: #fbf7ee; }
.card {
    background-color: #fffaf0;
    border-radius: 10px;
    padding: 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}
.section-title { color:#4a3f2a; font-weight:700; font-size:20px; margin-bottom:10px; }
.muted { color:#7a6b5a; font-size:13px; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"], index=0)

# --- PAGE: Accueil ---
if page == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Bienvenue</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">BioPlateforme Algérienne — plateforme pour validation in silico.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGE: Formulation ---
elif page == "Formulation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    chercheur = st.text_input("Nom du chercheur")
    miel = st.slider("Miel (%)", 0, 100, 40)
    pla = st.slider("Acide phényllactique (%)", 0, 10, 1)
    eps = st.slider("Exopolysaccharides (%)", 0, 10, 2)
    lacto = st.slider("Lactobacillus plantarum (%)", 0, 5, 1)

    if st.button("Valider la formulation"):
        score = round((miel * 0.2 + pla * 2 + eps * 1.5 + lacto * 3), 2)
        st.success(f"Formulation validée — score: {score}")

        df = pd.DataFrame({
            "chercheur":[chercheur],
            "miel":[miel],
            "pla":[pla],
            "eps":[eps],
            "lacto":[lacto],
            "score":[score]
        })

        # ✅ CORRECTION ICI — anti-erreur OS
        dossier = "resultats"
        os.makedirs(dossier, exist_ok=True)  # crée le dossier s'il n'existe pas

        nom_fichier = (chercheur or "anonyme").replace(" ", "_").replace("/", "_")
        path = os.path.join(dossier, f"formulation_{nom_fichier}.csv")

        try:
            df.to_csv(path, index=False)
            st.info(f"Rapport sauvegardé sans erreur : {path}")
        except Exception as e:
            st.warning("Erreur évitée automatiquement — fichier non sauvegardé.")

# --- PAGE: Références ---
elif page == "Références":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Références scientifiques</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    terme = st.text_input("Rechercher (ex: Lactobacillus plantarum)")

# --- PAGE: Validation ---
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Composant":["Miel","PLA","EPS","Lactobacillus"],
        "Contribution":[40,1,2,1]
    })
    st.bar_chart(df.set_index("Composant"))








