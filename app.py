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

# --- CSS général ---
st.markdown(
    """
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

    .score-card {
      padding:20px;
      border-radius:12px;
      color: #ffffff;
      box-shadow: 0 6px 20px rgba(13,27,42,0.12);
      margin-top:12px;
    }
    .score-excellent { background: linear-gradient(180deg, #0D1B2A 0%, #102232 100%); }
    .score-good      { background: linear-gradient(180deg, #1B263B 0%, #243447 100%); }
    .score-poor      { background: linear-gradient(180deg, #415A77 0%, #546E8C 100%); }
    .score-value { font-size:28px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"])

# -------------------------
# ACCUEIL
# -------------------------
if page == "Accueil":
    st.markdown(svg_logo, unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="section-title">Bienvenue</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Plateforme professionnelle pour la validation in silico.</div></div>', unsafe_allow_html=True)


# -------------------------
# FORMULATION — FIX #1 & FIX #2
# -------------------------
elif page == "Formulation":

    st.markdown('<div class="card"><div class="section-title">Formulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Composez et validez la formulation.</div></div>', unsafe_allow_html=True)

    chercheur = st.text_input("Nom du chercheur")
    miel = st.slider("Miel (%)", 0, 100, 40)
    pla = st.slider("Acide phényllactique (%)", 0, 10, 1)
    eps = st.slider("Exopolysaccharides (%)", 0, 10, 2)
    lacto = st.slider("L. plantarum (%)", 0, 5, 1)

    # --- DYNAMIC METABOLITES ---
    st.subheader("Métabolites supplémentaires")

    if "metabolites" not in st.session_state:
        st.session_state.metabolites = []  # format: [{id, nom, pourcentage}]

    # Add metabolite
    if st.button("➕ Ajouter un métabolite"):
        new_id = 1 if not st.session_state.metabolites else max(m["id"] for m in st.session_state.metabolites) + 1
        st.session_state.metabolites.append({"id": new_id, "nom": "", "pourcentage": 0.0})

    # Safe deletion process
    delete_id = None

    # Render metabolites
    for i, meta in enumerate(st.session_state.metabolites):

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            nom = st.text_input(
                "Nom du composé", 
                value=meta["nom"],
                key=f"meta_nom_{meta['id']}"
            )
        with col2:
            pct = st.number_input(
                "%", 
                value=float(meta["pourcentage"]),
                min_value=0.0,
                step=0.1,
                format="%.2f",
                key=f"meta_pct_{meta['id']}"
            )
        with col3:
            if st.button("Supprimer", key=f"del_{meta['id']}"):
                delete_id = meta["id"]

        # update local state
        meta["nom"] = nom
        meta["pourcentage"] = pct

    # DELETE WITHOUT ERROR (FIX #1)
    if delete_id is not None:
        st.session_state.metabolites = [
            m for m in st.session_state.metabolites if m["id"] != delete_id
        ]
        st.rerun()

    # --- VALIDATION ---
    if st.button("Valider la formulation"):

        score = miel * 0.2 + pla * 2 + eps * 1.5 + lacto * 3

        for m in st.session_state.metabolites:
            score += m["pourcentage"] * 1.2

        score = round(score, 2)

        # interpretation
        if score < 15:
            c = "score-poor"
            msg = "Score faible — formulation instable ou incomplète."
        elif score < 30:
            c = "score-good"
            msg = "Score satisfaisant — formulation scientifiquement cohérente."
        else:
            c = "score-excellent"
            msg = "Score excellent — formulation robuste et bien équilibrée."

        st.markdown(
            f"""
            <div class="score-card {c}">
                <div class="score-value">{score}</div>
                <div>{msg}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # SAVE CSV
        out = {
            "chercheur": chercheur,
            "miel": miel,
            "pla": pla,
            "eps": eps,
            "lacto": lacto,
            "score": score
        }

        for i, m in enumerate(st.session_state.metabolites, start=1):
            out[f"meta_{i}_nom"] = m["nom"]
            out[f"meta_{i}_pct"] = m["pourcentage"]

        df = pd.DataFrame([out])
        os.makedirs("resultats", exist_ok=True)
        path = f"resultats/formulation_{chercheur.replace(' ','_')}.csv"
        df.to_csv(path, index=False)
        st.success(f"Rapport enregistré : {path}")


# -------------------------
# RÉFÉRENCES (inchangé)
# -------------------------
elif page == "Références":
    st.markdown('<div class="card"><div class="section-title">Références scientifiques</div>', unsafe_allow_html=True)
    terme = st.text_input("Rechercher dans PubMed / UniProt")

    if terme:
        st.markdown(f"**Résultats pour :** {terme}")

        # PubMed
        try:
            r = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={"db": "pubmed", "term": terme, "retmode": "json", "retmax": 5}
            )
            ids = r.json()["esearchresult"]["idlist"]

            if ids:
                s = requests.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                    params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
                )
                data = s.json()["result"]
                for pid in ids:
                    info = data[pid]
                    st.markdown(f"- **[{info['title']}](https://pubmed.ncbi.nlm.nih.gov/{pid}/)**")
            else:
                st.info("Aucun article trouvé.")
        except:
            st.error("Erreur PubMed.")

        # UniProt
        try:
            r = requests.get(
                "https://rest.uniprot.org/uniprotkb/search",
                params={"query": terme, "format": "json", "size": 5}
            )
            for entry in r.json().get("results", []):
                acc = entry["primaryAccession"]
                st.markdown(f"- **[{acc}](https://www.uniprot.org/uniprotkb/{acc})**")
        except:
            st.error("Erreur UniProt.")


# -------------------------
# VALIDATION (inchangé)
# -------------------------
elif page == "Validation":
    st.markdown('<div class="card"><div class="section-title">Visualisation</div>', unsafe_allow_html=True)
    df = pd.DataFrame({
        "Composant": ["Miel", "PLA", "EPS", "Lacto"],
        "Contribution": [40, 1, 2, 1]
    })
    st.bar_chart(df.set_index("Composant"))










