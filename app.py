import streamlit as st
import pandas as pd
import requests
import html
import os
import urllib.parse

# CONFIG
st.set_page_config(page_title="BioPlateforme Algérienne", layout="wide")

# --- SVG logo ---
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
      <path d="M32 6 C42 12,52 20,50 34 C48 48,36 56,32 58 C28 56,16 48,14 34 C12 20,22 12,32 6 Z"
       fill="url(#g1)" stroke="#d1a44a" stroke-width="1.5"/>
      <rect x="22" y="24" rx="3" ry="3" width="20" height="8"
        fill="#6b8b5f" transform="rotate(-18 32 28)"/>
      <circle cx="40" cy="18" r="2.2" fill="#6b8b5f"/>
      <circle cx="44" cy="24" r="1.6" fill="#6b8b5f"/>
    </svg>
  </div>
  <div style="margin-left:16px;">
    <div style="font-family:Segoe UI,Helvetica,Arial,sans-serif;font-weight:700;color:#4a3f2a;font-size:26px;">
      BioPlateforme Algérienne
    </div>
    <div style="font-family:Segoe UI,Helvetica,Arial,sans-serif;color:#7a6b5a;font-size:13px;margin-top:2px;">
      Plateforme scientifique — validation in silico
    </div>
  </div>
</div>
"""

# --- Global CSS ---
st.markdown(
    """
    <style>
    .stApp { background-color: #fbf7ee; }
    .topbar { padding: 0; margin-bottom: 14px; }
    .card {
        background-color: #fffaf0;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 18px;
    }
    .nav-button { background-color: transparent; border: none; font-weight:600; color: #3b2f1f; padding: 8px 14px; border-radius:6px; }
    .nav-button:hover { background-color: #efe2b3; }
    .section-title { color:#4a3f2a; font-weight:700; font-size:20px; margin-bottom:10px; }
    .muted { color:#7a6b5a; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown("<div class='topbar'></div>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 5])
with col1:
    st.markdown(svg_logo, unsafe_allow_html=True)
with col2:
    st.markdown("""
      <div style="display:flex;align-items:center;justify-content:flex-end;height:90px;">
        <div style="margin-right:18px;"><button class="nav-button">Accueil</button></div>
        <div style="margin-right:18px;"><button class="nav-button">Formulation</button></div>
        <div style="margin-right:18px;"><button class="nav-button">Références</button></div>
        <div style="margin-right:18px;"><button class="nav-button">Validation</button></div>
      </div>
    """, unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"], index=0)

# -------------------------
#  PAGE : ACCUEIL
# -------------------------
if page == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Bienvenue</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">BioPlateforme Algérienne — plateforme professionnelle pour la simulation et la validation in silico de formulations bioactives (miel, métabolites, probiotiques).</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    a, b, c = st.columns([1,1,1])
    with a:
        st.markdown('<div class="card"><div style="font-weight:700;color:#3b2f1f">BioData Explorer</div><div class="muted">Recherches NCBI / PubMed / UniProt</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><div style="font-weight:700;color:#3b2f1f">Formulation Simulator</div><div class="muted">Composer et tester formulations</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="card"><div style="font-weight:700;color:#3b2f1f">In Silico Validator</div><div class="muted">Score & recommandations</div></div>', unsafe_allow_html=True)

# -------------------------
#  PAGE : FORMULATION
# -------------------------
elif page == "Formulation":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Saisissez les paramètres et générez un rapport détaillé, analysé selon des critères scientifiques objectifs.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Inputs principaux ----
    chercheur = st.text_input("Nom du chercheur")
    miel = st.slider("Miel (%)", 0, 100, 40)
    pla = st.slider("Acide phényllactique (%)", 0, 10, 1)
    eps = st.slider("Exopolysaccharides (%)", 0, 10, 2)
    lacto = st.slider("Lactobacillus plantarum (%)", 0, 5, 1)

    # ---- SECTION : métabolites personnalisés dynamiques ----
    st.subheader("Ajouter des métabolites ou composés supplémentaires")

    if "metabolites" not in st.session_state:
        st.session_state.metabolites = []

    if st.button("+ Ajouter un métabolite"):
        st.session_state.metabolites.append({"nom":"","pourcentage":0})

    for i, meta in enumerate(st.session_state.metabolites):
        colA, colB, colC = st.columns([3,1,1])
        with colA:
            meta["nom"] = st.text_input(f"Nom du composé #{i+1}", value=meta["nom"],
                                        placeholder="Ex : Acide férulique, catéchines, peptides, flavonoïdes…")
        with colB:
            meta["pourcentage"] = st.number_input(f"% #{i+1}", value=meta["pourcentage"], min_value=0.0, step=0.1)
        with colC:
            if st.button(f"Supprimer #{i+1}"):
                st.session_state.metabolites.pop(i)
                st.experimental_rerun()

    # ---- Validation & Score ----
    if st.button("Valider la formulation"):

        score = round((miel * 0.2 + pla * 2 + eps * 1.5 + lacto * 3), 2)

        # ajout des métabolites : chaque métabolite compte 1.2
        for meta in st.session_state.metabolites:
            score += meta["pourcentage"] * 1.2

        score = round(score, 2)

        # FONCTION SCORE PREMIUM
        def interpretation_score(score):
            if score < 10:
                return ("Score faible — une optimisation de la composition est recommandée.",
                        "#415A77")  # gris anthracite pro
            elif 10 <= score < 20:
                return ("Score satisfaisant — formulation globalement cohérente et stable.",
                        "#1B263B")  # bleu pétrole
            else:
                return ("Score excellent — formulation scientifiquement robuste et équilibrée.",
                        "#0D1B2A")  # bleu nuit luxe

        message, color = interpretation_score(score)

        # Affichage premium
        st.markdown(f"""
        <div style="
        padding:22px;
        border-radius:12px;
        background-color:{color};
        color:white;
        font-size:18px;
        line-height:1.5;
        box-shadow:0 4px 12px rgba(0,0,0,0.18);
        border:1px solid rgba(255,255,255,0.18);
        ">
        <b>Analyse de stabilité — Résultat</b><br><br>
        <div style="font-size:17px;">{message}</div><br>
        <div style="font-size:20px;font-weight:700;">Score obtenu : {score}</div>
        </div>
        """, unsafe_allow_html=True)

        # ---- Sauvegarde CSV ----
        out_dir = "resultats"
        try:
            os.makedirs(out_dir, exist_ok=True)
            df = pd.DataFrame({
                "chercheur":[chercheur],
                "miel":[miel],
                "pla":[pla],
                "eps":[eps],
                "lacto":[lacto],
                "metabolites":[str(st.session_state.metabolites)],
                "score":[score]
            })
            safe_name = (chercheur or "anonyme").strip().replace(" ", "_").replace("/", "_")
            path = os.path.join(out_dir, f"formulation_{safe_name}.csv")
            df.to_csv(path, index=False)
            st.success("Rapport sauvegardé avec succès.")
            st.info(f"Chemin : {path}")
        except:
            st.error("Erreur lors de la sauvegarde du rapport.")

# -------------------------
#  PAGE : RÉFÉRENCES
# -------------------------
elif page == "Références":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Références scientifiques</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Recherche intégrée : PubMed + UniProt + lien RCSB/PDB</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    terme = st.text_input("Rechercher (ex: Lactobacillus plantarum OR phenyllactic acid OR plantaricin)")

    if terme:
        st.markdown(f"**Résultats pour :** {html.escape(terme)}")

        # PubMed
        st.markdown("### PubMed")
        try:
            esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {"db": "pubmed", "term": terme, "retmax": 5, "retmode": "json"}
            r = requests.get(esearch_url, params=params, timeout=10)
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if ids:
                esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                s = requests.get(esummary_url, params={"db":"pubmed","id":",".join(ids),"retmode":"json"}, timeout=10)
                summaries = s.json().get("result", {})
                for pid in ids:
                    info = summaries.get(pid, {})
                    title = info.get("title") or f"PubMed {pid}"
                    pubdate = info.get("pubdate", "")
                    st.markdown(f"- {html.escape(title)} — {pubdate}")
            else:
                st.info("Aucun article trouvé.")
        except:
            st.error("Erreur PubMed.")

        # UniProt
        st.markdown("### UniProt")
        try:
            uq = "https://rest.uniprot.org/uniprotkb/search"
            params = {"query": terme, "format": "json", "size": 5}
            r2 = requests.get(uq, params=params, timeout=10)
            hits = r2.json().get("results", [])
            if hits:
                for entry in hits:
                    acc = entry.get("primaryAccession")
                    desc = entry.get("proteinDescription", {})
                    name = desc.get("recommendedName", {}).get("fullName", {}).get("value", "")
                    st.markdown(f"- {name} — `{acc}`")
            else:
                st.info("Aucun hit UniProt.")
        except:
            st.error("Erreur UniProt.")

        # PDB / RCSB
        st.markdown("### PDB / RCSB")
        query_encoded = urllib.parse.quote_plus(terme)
        link = f"https://www.rcsb.org/search?request={{\"query\":\"{query_encoded}\"}}"
        st.markdown("- Recherche structures : RCSB (ouvrir dans navigateur)")

# -------------------------
#  PAGE : VALIDATION
# -------------------------
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Visualisation et score de stabilité</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Composant":["Miel","PLA","EPS","Lactobacillus"],
        "Contribution":[40,1,2,1]
    })
    st.bar_chart(df.set_index("Composant"))









