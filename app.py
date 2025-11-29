import streamlit as st
import pandas as pd
import requests
import html
import os
import urllib.parse

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
      <path d="M32 6 C42 12,52 20,50 34 C48 48,36 56,32 58 C28 56,16 48,14 34 C12 20,22 12,32 6 Z" 
            fill="url(#g1)" stroke="#d1a44a" stroke-width="1.5"/>
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

# --- GLOBAL CSS ---
st.markdown("""
<style>
.stApp { background-color: #fbf7ee; }
.card { background-color: #fffaf0; border-radius: 10px; padding: 18px;
        box-shadow:0 1px 4px rgba(0,0,0,0.06); margin-bottom:18px; }
.section-title { color:#4a3f2a; font-weight:700; font-size:20px; margin-bottom:10px; }
.muted { color:#7a6b5a; font-size:13px; }

/* SCORE PREMIUM */
.score-box {
    padding: 18px;
    border-radius: 12px;
    font-size: 20px;
    font-weight: bold;
    color: white;
    margin-top: 12px;
}
.good-score {
    background: linear-gradient(90deg, #2ecc71, #27ae60);
}
.medium-score {
    background: linear-gradient(90deg, #f1c40f, #f39c12);
}
.bad-score {
    background: linear-gradient(90deg, #e74c3c, #c0392b);
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col1, col2 = st.columns([2,5])
with col1:
    st.markdown(svg_logo, unsafe_allow_html=True)

# --- SIDEBAR NAV ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"], index=0)

# ============================================================
#  PAGE : ACCUEIL
# ============================================================
if page == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Bienvenue</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">BioPlateforme Algérienne — plateforme professionnelle pour la simulation et la validation in silico.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#  PAGE : FORMULATION
# ============================================================
elif page == "Formulation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Saisissez les paramètres et validez pour générer le score.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    chercheur = st.text_input("Nom du chercheur")

    # --- SLIDERS CLASSIQUES ---
    miel = st.slider("Miel (%)", 0, 100, 40)
    pla = st.slider("Acide phényllactique (%)", 0, 10, 1)
    eps = st.slider("Exopolysaccharides (%)", 0, 10, 2)
    lacto = st.slider("Lactobacillus plantarum (%)", 0, 5, 1)

    # --- AJOUT DYNAMIQUE DE MÉTABOLITES ---
    st.subheader("➕ Ajouter des métabolites personnalisés")

    if "meta_count" not in st.session_state:
        st.session_state.meta_count = 0

    if st.button("Ajouter un métabolite"):
        st.session_state.meta_count += 1

    custom_metabolites = {}

    for i in range(st.session_state.meta_count):
        colA, colB = st.columns([2,1])
        name = colA.text_input(f"Nom du métabolite {i+1}", key=f"name_{i}")
        value = colB.number_input(f"% {i+1}", 0, 100, 0, key=f"value_{i}")
        custom_metabolites[name] = value

    # --- VALIDATION ---
    if st.button("Valider la formulation"):
        
        # SCORE
        score = miel*0.2 + pla*2 + eps*1.5 + lacto*3

        for name, val in custom_metabolites.items():
            score += val * 0.5

        score = round(score, 2)

        # --- INTERPRÉTATION VISUELLE PREMIUM ---
        if score >= 30:
            css_class = "good-score"
            msg = "Score excellent — formulation optimale"
        elif score >= 15:
            css_class = "medium-score"
            msg = "Score moyen — formulation équilibrée"
        else:
            css_class = "bad-score"
            msg = "Score faible — reformulation nécessaire"

        st.markdown(
            f'<div class="score-box {css_class}">Score : {score}<br>{msg}</div>',
            unsafe_allow_html=True
        )

        # --- EXPORT CSV ---
        os.makedirs("resultats", exist_ok=True)

        df = {
            "chercheur": [chercheur],
            "miel": [miel],
            "pla": [pla],
            "eps": [eps],
            "lacto": [lacto],
            "score": [score]
        }

        # ajouter métabolites
        for k, v in custom_metabolites.items():
            df[k] = [v]

        df = pd.DataFrame(df)

        safe_name = (chercheur or "anonyme").replace(" ", "_").replace("/", "_")
        path = f"resultats/formulation_{safe_name}.csv"
        df.to_csv(path, index=False)

        st.success("Rapport sauvegardé.")
        st.info(f"Chemin : {path}")


# ============================================================
#  PAGE : RÉFÉRENCES
# ============================================================
elif page == "Références":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Références scientifiques</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    terme = st.text_input("Rechercher (ex: Lactobacillus plantarum)")

    if terme:
        st.markdown(f"**Résultats pour :** {terme}")

        # PUBMED
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
                    date = info.get("pubdate", "")
                    st.markdown(f"- {title} — {date}")
            else:
                st.info("Aucun article trouvé.")
        except:
            st.error("Erreur PubMed.")

        # UNIPROT
        st.markdown("### UniProt")
        try:
            uq = "https://rest.uniprot.org/uniprotkb/search"
            params = {"query": terme, "format": "json", "size": 5}
            r2 = requests.get(uq, params=params, timeout=10)
            hits = r2.json().get("results", [])
            for entry in hits:
                acc = entry.get("primaryAccession")
                name = entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "")
                st.markdown(f"- {name} — `{acc}`")
        except:
            st.error("Erreur UniProt")

# ============================================================
#  PAGE : VALIDATION
# ============================================================
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Composant":["Miel","PLA","EPS","Lactobacillus"],
        "Contribution":[40,1,2,1]
    })

    st.bar_chart(df.set_index("Composant"))








