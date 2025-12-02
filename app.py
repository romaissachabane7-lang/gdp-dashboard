# app.py
import streamlit as st
import pandas as pd
import requests
import html
import os
import urllib.parse
import numpy as np

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="BioPlateforme Algérienne", layout="wide")

# ---------------------------------------
# Petit style pour rendre l'UI plus propre
# ---------------------------------------
st.markdown("""
<style>
.card { background:#fff;padding:12px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.06);margin-bottom:14px}
.section-title{font-size:20px;font-weight:700}
.muted{color:#6e6e6e;font-size:13px}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION STATE : valeurs par défaut pour la formulation
# -------------------------
if "miel" not in st.session_state:
    st.session_state["miel"] = 40
if "pla" not in st.session_state:
    st.session_state["pla"] = 1
if "eps" not in st.session_state:
    st.session_state["eps"] = 2
if "lacto" not in st.session_state:
    st.session_state["lacto"] = 1

# -------------------------
# MODULE IA AUTOMATISÉ
# -------------------------
def ai_generate_formulation(miel, pla, eps, lacto):
    """
    Mini réseau neuronal simulé pour générer automatiquement
    une formulation optimisée (score simple explicatif).
    """
    X = np.array([miel, pla, eps, lacto], dtype=float)

    # Poids simulés – comme un réseau neuronal entraîné
    W1 = np.array([
        [0.42, -0.11, 0.07, 0.19],
        [0.15,  0.33, -0.25, 0.40],
        [-0.31, 0.21, 0.29, -0.14]
    ])
    b1 = np.array([0.1, -0.05, 0.07])

    hidden = np.maximum(0, W1.dot(X) + b1)  # ReLU

    W2 = np.array([0.28, 0.17, -0.09])
    b2 = 0.12

    # Score final automatisé de formulation
    score = float(W2.dot(hidden) + b2)

    return max(0, round(score, 3))


def ai_validation(formulation_dict):
    """
    Validation in silico dynamique basée sur la formulation.
    Retourne un score de stabilité, un score d’efficacité
    et une note globale.
    """
    F = formulation_dict

    # Normalisation/simplification : on suppose que les quantités sont en pourcentages relatifs
    stability = round(
        0.6 * F["Miel"] + 1.2 * F["PLA"] + 0.9 * F["EPS"] + 0.7 * F["Lactobacillus"],
        2
    )
    efficiency = round(
        1.1 * F["Miel"] + 0.4 * F["PLA"] + 1.3 * F["EPS"] + 1.6 * F["Lactobacillus"],
        2
    )

    global_score = round((stability + efficiency) / 2, 2)

    # Quelques indicateurs dérivés
    release_profile = "Prolongée" if F["PLA"] >= 1 else "Rapide"
    probiotic_support = "Élevé" if F["Lactobacillus"] >= 1 else "Faible"

    return {
        "stability": stability,
        "efficiency": efficiency,
        "global_score": global_score,
        "release_profile": release_profile,
        "probiotic_support": probiotic_support
    }


def get_combined_references(formulation_dict):
    """
    Génère automatiquement des références basées sur
    LA COMBINAISON des composants, pas séparément.
    (Les références ici sont des exemples / placeholders,
    tu peux remplacer par tes références réelles.)
    """
    refs = []

    if formulation_dict["Miel"] > 0 and formulation_dict["Lactobacillus"] > 0:
        refs.append("Interaction synergique miel–Lactobacillus (FAO/WHO 2022)")

    if formulation_dict["PLA"] > 0 and formulation_dict["EPS"] > 0:
        refs.append("Consolidation polymérique PLA–EPS (Nature Materials 2020)")

    if formulation_dict["EPS"] > 0 and formulation_dict["Lactobacillus"] > 0:
        refs.append("Production contrôlée d’EPS par Lactobacillus (Applied Microbiology 2021)")

    if formulation_dict["Miel"] >= 30 and formulation_dict["PLA"] < 2:
        refs.append("Effet conservateur du miel en formulations à faible PLA (Food Chem 2019)")

    if not refs:
        refs.append("Aucune combinaison critique détectée — pas de référence combinée trouvée.")

    return refs

# -------------------------
# UI : barre latérale et navigation entre pages
# -------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil", "Recherche", "Formulation", "Validation", "A propos"])

# -------------------------
# PAGE : ACCUEIL
# -------------------------
if page == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">BioPlateforme Algérienne</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Plateforme Streamlit pour génération de formulations, validation in silico et exploration documentaire.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Résumé rapide")
    st.write("""
    - Cette plateforme recherche dans PubMed / UniProt et propose des liens RCSB.  
    - Elle permet de définir une formulation (Miel, PLA, EPS, Lactobacillus).  
    - Un module IA génère un score de formulation et réalise une validation in silico adaptée à chaque combinaison.  
    """)

# -------------------------
# PAGE : RECHERCHE (PubMed, UniProt, PDB)
# -------------------------
elif page == "Recherche":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recherche documentaire</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">PubMed, UniProt, PDB — saisie d\'un terme</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    terme = st.text_input("Terme de recherche (ex: 'Lactobacillus plantarum EPS')", value="")
    if st.button("Lancer la recherche"):
        if not terme.strip():
            st.warning("Veuillez saisir un terme de recherche.")
        else:
            # PubMed
            st.markdown("### PubMed — résultats top")
            try:
                entrez_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                params = {"db": "pubmed", "term": terme, "retmax": 6, "retmode": "json"}
                r = requests.get(entrez_url, params=params, timeout=10)
                r.raise_for_status()
                data = r.json()
                ids = data.get("esearchresult", {}).get("idlist", [])
                if ids:
                    # fetch summaries
                    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                    params2 = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
                    r2 = requests.get(fetch_url, params=params2, timeout=10)
                    r2.raise_for_status()
                    data2 = r2.json()
                    for pid in ids:
                        doc = data2.get("result", {}).get(pid, {})
                        title = doc.get("title", "Titre non disponible")
                        source = doc.get("source", "")
                        pubdate = doc.get("pubdate", "")
                        display = html.escape(title)
                        extra = f" — {html.escape(source)} {html.escape(pubdate)}" if source or pubdate else ""
                        st.markdown(display + extra, unsafe_allow_html=True)
                else:
                    st.info("Aucun article PubMed trouvé pour ce terme.")
            except Exception as e:
                st.error("Recherche PubMed impossible (vérifiez la connexion).")

            # UniProt
            st.markdown("### UniProt — Top hits")
            try:
                uq = "https://rest.uniprot.org/uniprotkb/search"
                params = {"query": terme, "format": "json", "size": 6}
                r2 = requests.get(uq, params=params, timeout=10)
                r2.raise_for_status()
                data = r2.json()
                hits = data.get("results", [])
                if hits:
                    for entry in hits:
                        acc = entry.get("primaryAccession")
                        prot_desc = entry.get("proteinDescription", {})
                        rec_name = prot_desc.get("recommendedName", {}).get("fullName", {}).get("value", "") if prot_desc else ""
                        display_label = rec_name or acc
                        uniprot_url = f"https://rest.uniprot.org/uniprotkb/{acc}"
                        st.markdown(f"- <a href='{uniprot_url}' target='_blank' style='color:#0A84FF;text-decoration:none'><b>{html.escape(display_label)}</b></a> — Accession: `{acc}`", unsafe_allow_html=True)
                else:
                    st.info("Aucun hit UniProt retourné.")
            except Exception as e:
                st.error("Recherche UniProt impossible (temps de réponse ou réseau).")

            # PDB
            st.markdown("### PDB / RCSB")
            try:
                query_encoded = urllib.parse.quote_plus(terme)
                rcsb_link = f"https://www.rcsb.org/search?request={{\"query\":\"{query_encoded}\"}}"
                st.markdown(f"- Effectuer une recherche sur RCSB PDB : <a href='{rcsb_link}' target='_blank' style='color:#0A84FF;text-decoration:none'>Ouvrir RCSB</a>", unsafe_allow_html=True)
                st.markdown("<div style='margin-top:6px' class='muted'>Astuce : utilisez l'accession UniProt (si trouvée ci-dessus) pour retrouver des structures corrélées.</div>", unsafe_allow_html=True)
            except Exception:
                st.info("Impossible de générer le lien RCSB.")

# -------------------------
# PAGE : FORMULATION (entrée utilisateur)
# -------------------------
elif page == "Formulation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation — paramètres</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Définis ta formulation ici (les valeurs sont relatives).</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        miel_val = st.number_input("Miel (valeur relative)", min_value=0.0, max_value=100.0, value=float(st.session_state["miel"]), step=1.0)
        pla_val = st.number_input("PLA (valeur relative)", min_value=0.0, max_value=100.0, value=float(st.session_state["pla"]), step=0.1)
    with col2:
        eps_val = st.number_input("EPS (valeur relative)", min_value=0.0, max_value=100.0, value=float(st.session_state["eps"]), step=0.1)
        lacto_val = st.number_input("Lactobacillus (valeur relative)", min_value=0.0, max_value=100.0, value=float(st.session_state["lacto"]), step=0.1)

    if st.button("Enregistrer la formulation"):
        st.session_state["miel"] = float(miel_val)
        st.session_state["pla"] = float(pla_val)
        st.session_state["eps"] = float(eps_val)
        st.session_state["lacto"] = float(lacto_val)
        st.success("Formulation enregistrée dans la session. Va à la page Validation pour voir les résultats IA.")

    st.markdown("### Formulation actuelle (session)")
    df_form = pd.DataFrame({
        "Composant": ["Miel", "PLA", "EPS", "Lactobacillus"],
        "Contribution": [st.session_state["miel"], st.session_state["pla"], st.session_state["eps"], st.session_state["lacto"]]
    })
    st.table(df_form.set_index("Composant"))

# -------------------------
# PAGE : VALIDATION (modifiée : IA intégrée)
# -------------------------
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico — IA optimisée</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Visualisation, score de stabilité et validation dynamique liée à la formulation</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Récupère la formulation depuis la session (ou valeurs par défaut)
    miel = st.session_state.get("miel", 40)
    pla = st.session_state.get("pla", 1)
    eps = st.session_state.get("eps", 2)
    lacto = st.session_state.get("lacto", 1)

    st.markdown("### Formulation utilisée pour la validation")
    st.write(f"Miel: **{miel}**, PLA: **{pla}**, EPS: **{eps}**, Lactobacillus: **{lacto}**")

    formulation = {
        "Miel": float(miel),
        "PLA": float(pla),
        "EPS": float(eps),
        "Lactobacillus": float(lacto)
    }

    # ---- IA : score de formulation ----
    ai_score = ai_generate_formulation(miel, pla, eps, lacto)
    st.metric("Score IA de formulation", ai_score)

    # ---- Validation dynamique ----
    results = ai_validation(formulation)
    st.metric("Stabilité in silico", results["stability"])
    st.metric("Efficacité in silico", results["efficiency"])
    st.metric("Score global", results["global_score"])

    st.markdown(f"- Profil de libération estimé : **{results['release_profile']}**")
    st.markdown(f"- Support probiotique estimé : **{results['probiotic_support']}**")

    # ---- Graphique dynamique ----
    df = pd.DataFrame({
        "Composant": ["Miel", "PLA", "EPS", "Lactobacillus"],
        "Contribution": [formulation["Miel"], formulation["PLA"], formulation["EPS"], formulation["Lactobacillus"]]
    })
    st.bar_chart(df.set_index("Composant"))

    # ---- Références automatiques basées sur la combinaison ----
    st.markdown("### Références scientifiques générées automatiquement (par combinaison)")
    refs = get_combined_references(formulation)
    for r in refs:
        st.markdown(f"- {r}")

# -------------------------
# PAGE : A PROPOS
# -------------------------
elif page == "A propos":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">À propos</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Informations & crédits</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    **BioPlateforme Algérienne** — Prototype Streamlit.  
    Module IA : mini réseau neuronal simulé (pour démonstration).  
    Remplace les références placeholder par tes références réelles pour une présentation scientifique.
    """)

# -------------------------
# FIN
# -------------------------


