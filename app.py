### CODE IDENTIQUE + 2 CORRECTIONS (suppression # et correction delete-error)

import streamlit as st
import pandas as pd
import requests
import html
import os
import urllib.parse

# CONFIG
st.set_page_config(page_title="BioPlateforme Algérienne", layout="wide")

# --- SVG logo ---
svg_logo = """[... inchangé ...]"""

# --- CSS premium (inchangé) ---
st.markdown("""[... inchangé ...]""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<div class='topbar'></div>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 5])
with col1:
    st.markdown(svg_logo, unsafe_allow_html=True)
with col2:
    st.markdown("""[...]""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"], index=0)

# ------------------------- ACCUEIL -------------------------
if page == "Accueil":
    st.markdown("""[...]""", unsafe_allow_html=True)

# ------------------------- FORMULATION -------------------------
elif page == "Formulation":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Saisissez…</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Inputs principaux
    chercheur = st.text_input("Nom du chercheur", placeholder="Prénom Nom — ex : Samir B.")
    miel = st.slider("Miel (%)", 0, 100, 40)
    pla = st.slider("Acide phényllactique (%)", 0, 10, 1)
    eps = st.slider("Exopolysaccharides (%)", 0, 10, 2)
    lacto = st.slider("Lactobacillus plantarum (%)", 0, 5, 1)

    # --- Métabolites dynamiques (CORRIGÉ + sans #) ---
    st.subheader("Ajouter des métabolites ou composés supplémentaires")
    st.markdown("**Instructions :** indiquez le nom du composé scientifique puis son pourcentage.")

    if "metabolites" not in st.session_state:
        st.session_state.metabolites = []   # {id:int, nom:str, pct:float}

    # bouton ajouter
    if st.button("+ Ajouter un métabolite"):
        new_id = max([m["id"] for m in st.session_state.metabolites], default=0) + 1
        st.session_state.metabolites.append({"id": new_id, "nom": "", "pourcentage": 0.0})

    # affichage sans hashtags + suppression sans erreur
    to_delete = None
    new_list = []

    for meta in st.session_state.metabolites:
        m_id = meta["id"]
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            nom = st.text_input(
                "Nom du composé",
                value=meta["nom"],
                key=f"meta_nom_{m_id}",
                placeholder="Acide férulique, Catéchines..."
            )
        with col2:
            pct = st.number_input(
                "%",
                value=float(meta["pourcentage"]),
                min_value=0.0, step=0.1, format="%.2f",
                key=f"meta_pct_{m_id}"
            )
        with col3:
            if st.button("Supprimer", key=f"del_{m_id}"):
                to_delete = m_id

        # reconstruire la liste sans erreur même quand on supprime
        new_list.append({"id": m_id, "nom": nom, "pourcentage": pct})

    # mettre à jour proprement
    if to_delete is not None:
        new_list = [m for m in new_list if m["id"] != to_delete]

    st.session_state.metabolites = new_list

    # --- Validation + Score premium ---
    if st.button("Valider la formulation"):

        score = round((miel * 0.2 + pla * 2 + eps * 1.5 + lacto * 3), 2)

        for m in st.session_state.metabolites:
            score += float(m["pourcentage"]) * 1.2

        score = round(score, 2)

        # interprétation (identique)
        def interpretation_score(score):
            if score < 15:
                return ("Score faible — optimisation recommandée.", "score-poor")
            elif 15 <= score < 30:
                return ("Score satisfaisant — cohérence générale.", "score-good")
            else:
                return ("Score excellent — formulation robuste.", "score-excellent")

        message, css_class = interpretation_score(score)

        st.markdown(
            f"""
            <div class="score-card {css_class}">
                <div class="score-title">Résultat de l'analyse in silico</div>
                <div class="score-value">Score : {score}</div>
                <div class="score-text">{html.escape(message)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # export CSV (identique)
        out_dir = "resultats"
        os.makedirs(out_dir, exist_ok=True)

        base = {
            "chercheur": chercheur or "anonyme",
            "miel": miel, "pla": pla, "eps": eps, "lacto": lacto,
            "score": score
        }

        meta_cols = {}
        for i, m in enumerate(st.session_state.metabolites, start=1):
            meta_cols[f"meta_{i}_nom"] = m["nom"]
            meta_cols[f"meta_{i}_pourcentage"] = m["pourcentage"]

        row = {**base, **meta_cols}
        df = pd.DataFrame([row])

        filename = (chercheur or "anonyme").replace(" ", "_")
        df.to_csv(f"resultats/formulation_{filename}.csv", index=False)

        st.success("Rapport sauvegardé.")

# ------------------------- RÉFÉRENCES (inchangé) -------------------------
elif page == "Références":
    st.markdown("""[...]""", unsafe_allow_html=True)

# ------------------------- VALIDATION (inchangé) -------------------------
elif page == "Validation":
    st.markdown("""[...]""", unsafe_allow_html=True)




