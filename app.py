# app.py
import streamlit as st
import pandas as pd
import requests
import html
import urllib.parse
import numpy as np
import io
import base64
from datetime import datetime

# -------------------------
# CONFIG & STYLE
# -------------------------
st.set_page_config(page_title="BioPlateforme Algérienne — Pro", layout="wide", initial_sidebar_state="auto")

# Palette et style minimal (amélioration UI)
PRIMARY = "#2A9DF4"   # bleu
ACCENT = "#0BA360"    # vert biotech
BG = "#F7F9FC"
CARD_BG = "#FFFFFF"
TEXT = "#0F1724"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"]  {{
    font-family: 'Inter', sans-serif;
    color: {TEXT};
    background: {BG};
}}
.card {{
    background:{CARD_BG};
    padding:18px;
    border-radius:14px;
    box-shadow: 0 6px 18px rgba(16,24,40,0.06);
    margin-bottom:18px;
}}
.section-title {{ font-size:20px; font-weight:700; margin-bottom:6px; color:{PRIMARY} }}
.muted {{ color:#6b7280; font-size:13px }}
.metric-small {{ font-size:12px; color:#374151 }}
.kpi {{ font-size:18px; font-weight:600; color:{PRIMARY} }}
.small-note {{ font-size:12px; color:#6b7280; }}
.table-standard th {{ background:#f3f4f6; }}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION DEFAULTS (formulation)
# -------------------------
if "miel" not in st.session_state:
    st.session_state["miel"] = 40.0
if "pla" not in st.session_state:
    st.session_state["pla"] = 1.0
if "eps" not in st.session_state:
    st.session_state["eps"] = 2.0
if "lacto" not in st.session_state:
    st.session_state["lacto"] = 1.0

# -------------------------
# FONCTIONS : IA LÉGÈRE, VALIDATION, RÉFÉRENCES
# -------------------------
def ai_generate_formulation(miel, pla, eps, lacto):
    """
    Mini modèle (simulé) qui renvoie un score de formulation.
    Garde simple et déterministe — utile pour démonstration.
    """
    X = np.array([miel, pla, eps, lacto], dtype=float)
    W1 = np.array([[0.42, -0.11, 0.07, 0.19],
                   [0.15,  0.33, -0.25, 0.40],
                   [-0.31, 0.21, 0.29, -0.14]])
    b1 = np.array([0.1, -0.05, 0.07])
    hidden = np.maximum(0, W1.dot(X) + b1)
    W2 = np.array([0.28, 0.17, -0.09])
    b2 = 0.12
    score = float(W2.dot(hidden) + b2)
    return max(0, round(score, 3))

def ai_validation(formulation):
    """
    Validation in silico simplifiée :
    - stability (arbitraire pondéré)
    - efficiency
    - global score
    - release profile & probiotic support (qualitatif)
    """
    F = formulation
    stability = round(0.6*F["Miel"] + 1.2*F["PLA"] + 0.9*F["EPS"] + 0.7*F["Lactobacillus"], 2)
    efficiency = round(1.1*F["Miel"] + 0.4*F["PLA"] + 1.3*F["EPS"] + 1.6*F["Lactobacillus"], 2)
    global_score = round((stability + efficiency) / 2, 2)
    release_profile = "Prolongée" if F["PLA"] >= 1 else "Rapide"
    probiotic_support = "Élevé" if F["Lactobacillus"] >= 1 else "Faible"
    # ajout d'un champ ISO-simulé
    iso_like = "Compatible (GMP-like)" if global_score >= 50 else "Nécessite optimisation"
    return {
        "stability": stability,
        "efficiency": efficiency,
        "global_score": global_score,
        "release_profile": release_profile,
        "probiotic_support": probiotic_support,
        "iso_like": iso_like
    }

def get_combined_references(formulation):
    """
    Génère références combinées (placeholders) selon la combinaison.
    Remplace par références réelles pour présentation scientifique.
    """
    refs = []
    if formulation["Miel"] > 0 and formulation["Lactobacillus"] > 0:
        refs.append("Interaction miel–Lactobacillus (FAO/WHO 2022)")
    if formulation["PLA"] > 0 and formulation["EPS"] > 0:
        refs.append("PLA–EPS: Synergie polymère (Nature Materials 2020)")
    if formulation["EPS"] > 0 and formulation["Lactobacillus"] > 0:
        refs.append("EPS produit par Lactobacillus (Applied Microbiology 2021)")
    if formulation["Miel"] >= 30 and formulation["PLA"] < 2:
        refs.append("Effet conservateur du miel (Food Chem 2019)")
    if not refs:
        refs.append("Pas de référence combinée détectée — fournir des références spécifiques.")
    return refs

def format_validation_report(formulation, ai_score, results, refs):
    """
    Retourne un texte markdown résumé prêt à exporter.
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    md = []
    md.append(f"# Fiche de validation — BioPlateforme Algérienne\n\n**Date**: {now}\n")
    md.append("## Formulation (unités relatives)\n")
    df = pd.DataFrame({
        "Composant": ["Miel", "PLA", "EPS", "Lactobacillus"],
        "Concentration (unités relatives)": [formulation["Miel"], formulation["PLA"], formulation["EPS"], formulation["Lactobacillus"]],
        "Unité recommandée": ["% (m/v) ou mg/mL", "mg/mL", "mg/mL", "CFU/mL"],
        "Fonction": ["Conservateur / matrice", "Matériau d'encapsulation", "Polysaccharide exopolysaccharide", "Probiotique"]
    })
    md.append(df.to_markdown(index=False))
    md.append("\n\n## Résultats IA\n")
    md.append(f"- Score IA de formulation: **{ai_score}**\n")
    md.append(f"- Stabilité in silico: **{results['stability']}**\n")
    md.append(f"- Efficacité in silico: **{results['efficiency']}**\n")
    md.append(f"- Score global: **{results['global_score']}**\n")
    md.append(f"- Profil de libération estimé: **{results['release_profile']}**\n")
    md.append(f"- Support probiotique: **{results['probiotic_support']}**\n")
    md.append(f"- Statut ISO-like: **{results['iso_like']}**\n")
    md.append("\n## Références combinées (générées)\n")
    for r in refs:
        md.append(f"- {r}\n")
    md.append("\n---\nCe document est généré automatiquement par BioPlateforme Algérienne — remplacer les références placeholders par des références réelles pour soumission scientifique.")
    return "\n".join(md)

def make_download_button(text, filename, content, mime="text/markdown"):
    st.download_button(label=text, data=content.encode("utf-8"), file_name=filename, mime=mime)

# -------------------------
# SIDEBAR / NAVIGATION
# -------------------------
st.sidebar.title("BioPlateforme Pro")
st.sidebar.markdown("Version améliorée — UI & standards internationaux")
page = st.sidebar.radio("Navigation", ["Accueil", "Recherche", "Formulation", "Validation", "Standards & GMP", "A propos"])

# -------------------------
# PAGE : ACCUEIL
# -------------------------
if page == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">BioPlateforme Algérienne — Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Plateforme Streamlit pour génération de formulations, validation in silico et recherche documentaire.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5,1,1])
    with col1:
        st.markdown("### Vue d'ensemble")
        st.write("Ta plateforme conserve : recherche PubMed / UniProt / PDB, saisie de formulation, validation in silico et génération de références par combinaison.")
        st.write("Améliorations ajoutées : UI professionnelle, standardisation des unités, checklist GMP-like, export de fiche de validation.")
    with col2:
        st.markdown("### KPI rapide")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="kpi">Score IA (exemple)</div>', unsafe_allow_html=True)
        st.write(ai_generate_formulation(st.session_state["miel"], st.session_state["pla"], st.session_state["eps"], st.session_state["lacto"]))
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown("### Conseils rapides")
        st.write("- Utilise des unités cohérentes (mg/mL ou %)") 
        st.write("- Remplace références placeholders par publications réelles")
        st.write("- Prépare un SOP (procédure) pour GMP")

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
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">PubMed — résultats top</div>', unsafe_allow_html=True)
            try:
                entrez_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                params = {"db": "pubmed", "term": terme, "retmax": 6, "retmode": "json"}
                r = requests.get(entrez_url, params=params, timeout=10)
                r.raise_for_status()
                data = r.json()
                ids = data.get("esearchresult", {}).get("idlist", [])
                if ids:
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
                        st.markdown(f"- {display}{extra}", unsafe_allow_html=True)
                else:
                    st.info("Aucun article PubMed trouvé pour ce terme.")
            except Exception as e:
                st.error("Recherche PubMed impossible (vérifiez la connexion).")
            st.markdown('</div>', unsafe_allow_html=True)

            # UniProt
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">UniProt — Top hits</div>', unsafe_allow_html=True)
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
                        st.markdown(f"- <a href='{uniprot_url}' target='_blank' style='color:{PRIMARY};text-decoration:none'><b>{html.escape(display_label)}</b></a> — Accession: `{acc}`", unsafe_allow_html=True)
                else:
                    st.info("Aucun hit UniProt retourné.")
            except Exception as e:
                st.error("Recherche UniProt impossible (temps de réponse ou réseau).")
            st.markdown('</div>', unsafe_allow_html=True)

            # PDB
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">PDB / RCSB</div>', unsafe_allow_html=True)
            try:
                query_encoded = urllib.parse.quote_plus(terme)
                rcsb_link = f"https://www.rcsb.org/search?request={{\"query\":\"{query_encoded}\"}}"
                st.markdown(f"- Effectuer une recherche sur RCSB PDB : <a href='{rcsb_link}' target='_blank' style='color:{PRIMARY};text-decoration:none'>Ouvrir RCSB</a>", unsafe_allow_html=True)
                st.markdown("<div class='small-note'>Astuce : utilisez l'accession UniProt (si trouvée ci-dessus) pour retrouver des structures corrélées.</div>", unsafe_allow_html=True)
            except Exception:
                st.info("Impossible de générer le lien RCSB.")
            st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# PAGE : FORMULATION
# -------------------------
elif page == "Formulation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation — paramètres</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Définis ta formulation ici (valeurs relatives). Utilise des unités cohérentes (voir Standards).</div>', unsafe_allow_html=True)
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
        "Contribution (unités relatives)": [st.session_state["miel"], st.session_state["pla"], st.session_state["eps"], st.session_state["lacto"]],
        "Unité recommandée": ["% (m/v) ou mg/mL", "mg/mL", "mg/mL", "CFU/mL"],
        "Fonction": ["Conservateur / matrice", "Encapsulation", "EPS", "Probiotique"]
    })
    st.table(df_form.set_index("Composant"))

# -------------------------
# PAGE : VALIDATION
# -------------------------
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico — Standardisée</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Résultats dynamiques basés sur la formulation enregistrée.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Récupère formulation
    formulation = {
        "Miel": float(st.session_state.get("miel", 40)),
        "PLA": float(st.session_state.get("pla", 1)),
        "EPS": float(st.session_state.get("eps", 2)),
        "Lactobacillus": float(st.session_state.get("lacto", 1))
    }

    st.markdown("### Formulation utilisée")
    st.write(f"Miel: **{formulation['Miel']}**, PLA: **{formulation['PLA']}**, EPS: **{formulation['EPS']}**, Lactobacillus: **{formulation['Lactobacillus']}**")

    # IA score & validation
    ai_score = ai_generate_formulation(formulation["Miel"], formulation["PLA"], formulation["EPS"], formulation["Lactobacillus"])
    results = ai_validation(formulation)
    refs = get_combined_references(formulation)

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Score IA", ai_score)
    k2.metric("Stabilité in silico", results["stability"])
    k3.metric("Efficacité in silico", results["efficiency"])

    st.markdown("<div class='card'><div class='muted'>Analyse détaillée</div>", unsafe_allow_html=True)
    st.markdown(f"- **Score global** : {results['global_score']}")
    st.markdown(f"- **Profil de libération** : {results['release_profile']}")
    st.markdown(f"- **Support probiotique** : {results['probiotic_support']}")
    st.markdown(f"- **Statut ISO-like** : {results['iso_like']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Graphique standardisé
    df_plot = pd.DataFrame({
        "Composant": ["Miel", "PLA", "EPS", "Lactobacillus"],
        "Contribution": [formulation["Miel"], formulation["PLA"], formulation["EPS"], formulation["Lactobacillus"]]
    }).set_index("Composant")
    st.bar_chart(df_plot)

    # Références combinées
    st.markdown("### Références par combinaison (à remplacer par références réelles)")
    for r in refs:
        st.markdown(f"- {r}")

    # Export fiche de validation
    st.markdown("---")
    st.markdown("### Export / Rapport")
    md = format_validation_report(formulation, ai_score, results, refs)
    make_download_button("Télécharger la fiche de validation (Markdown)", "fiche_validation.md", md)

# -------------------------
# PAGE : STANDARDS & GMP
# -------------------------
elif page == "Standards & GMP":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Standards internationaux & GMP-like</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Checklist et recommandations pour rendre ton procédé industriel-compatible.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Checklist GMP-like (à documenter dans ton SOP)")
    checklist = [
        "SOP pour chaque étape (préparation, encapsulation, séchage, conditionnement)",
        "Contrôle de la température (ex: 4–8 °C pour stockage) et des enregistreurs",
        "Contrôle d'humidité (ex: 30–40%)",
        "Validation des procédés (batch records) et traçabilité",
        "Analyse microbiologique de lot (CFU, contaminants)",
        "Tests de libération in vitro (pH dépendant)",
        "Contrôle des matières premières (pureté, certificates of analysis)",
        "Packaging et étiquetage conformes (lot, date, conditions de stockage)"
    ]
    for c in checklist:
        st.write(f"- {c}")

    st.markdown("### Unités & Table standardisée (exemple)")
    df_units = pd.DataFrame({
        "Composant": ["Miel", "PLA", "EPS", "Lactobacillus"],
        "Unité recommandée": ["% (m/v) ou mg/mL", "mg/mL", "mg/mL", "CFU/mL"],
        "Justification (ex.)": [
            "Concentration active, conservation",
            "Quantité pour encapsulation, influence libération",
            "Quantité EPS pour viscosité & protection",
            "Dose probiotique (viabilité)"
        ]
    })
    st.table(df_units.set_index("Composant"))

    st.markdown("### Conseils pour la standardisation scientifique")
    st.write("- Documente toujours unités et méthode (ex: méthode HPLC, spectrophotométrie, culture plate counts).")
    st.write("- Pour soumission: inclure protocole, validation analytique, et données de stabilité.")
    st.write("- Remplace les références placeholders par articles et normes (ISO / pharmacopeia) pour dossier réglementaire.")

# -------------------------
# PAGE : A PROPOS
# -------------------------
elif page == "A propos":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">À propos</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Informations & crédits</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    **BioPlateforme Algérienne — Version Pro**  
    - Prototype Streamlit amélioré pour présentations investisseurs & dossier scientifique.  
    - Module IA : mini-réseau simulé pour démonstration (remplacer par modèle entraîné pour production).  
    - Références générées automatiquement par combinaison — à remplacer par publications réelles.  
    """)

    st.markdown("### Prochaines étapes recommandées")
    st.write("- Intégrer modèle ML entraîné (ex: scikit-learn / joblib) pour recommandations réelles.")
    st.write("- Ajouter tests in vitro réels et intégrer leurs résultats dans la plateforme.")
    st.write("- Préparer dossier GMP/ISO pour production pilote.")

# -------------------------
# FIN
# -------------------------


