import streamlit as st
import pandas as pd
import requests
import html
import os
import urllib.parse
import uuid

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

# --- Global CSS ---
st.markdown(
    """
    <style>
    .stApp { background-color: #fbf7ee; }
    .topbar { padding: 0; margin-bottom: 14px; }
    .card { background-color: #fffaf0; border-radius: 10px; padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 18px; }
    .nav-button { background-color: transparent; border: none; font-weight:600; color: #3b2f1f; padding: 8px 14px; border-radius:6px; }
    .nav-button:hover { background-color: #efe2b3; }
    .section-title { color:#4a3f2a; font-weight:700; font-size:20px; margin-bottom:10px; }
    .muted { color:#7a6b5a; font-size:13px; }

    .score-card { padding:20px; border-radius:12px; color: #ffffff; box-shadow: 0 6px 20px rgba(13,27,42,0.12); margin-top:12px; border: 1px solid rgba(255,255,255,0.06); max-width: 720px; }
    .score-excellent { background: linear-gradient(180deg, #0D1B2A 0%, #102232 100%); }
    .score-good      { background: linear-gradient(180deg, #1B263B 0%, #243447 100%); }
    .score-poor      { background: linear-gradient(180deg, #415A77 0%, #546E8C 100%); }

    .score-title { font-size:16px; opacity:0.95; margin-bottom:8px; }
    .score-value { font-size:28px; font-weight:700; margin-top:6px; }
    .score-text { font-size:15px; opacity:0.95; margin-top:8px; line-height:1.4; }

    .meta-input { margin-bottom:6px; }
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

# --- Sidebar navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"], index=0)

# -------------------------
#  PAGE : ACCUEIL
# -------------------------
if page == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Bienvenue</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Optimisation de la composition est recommandée pour améliorer stabilité et efficacité.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
#  PAGE : FORMULATION
# -------------------------
elif page == "Formulation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation du produit</div>', unsafe_allow_html=True)

    # Entrées de base
    chercheur = st.text_input("Nom du chercheur")
    miel = st.number_input("Quantité de miel (%)", min_value=0.0, max_value=100.0, value=40.0)
    pla = st.number_input("Quantité de PLA (%)", min_value=0.0, max_value=100.0, value=1.0)
    eps = st.number_input("Quantité d'EPS (%)", min_value=0.0, max_value=100.0, value=2.0)
    lacto = st.number_input("Quantité de Lactobacillus (%)", min_value=0.0, max_value=100.0, value=1.0)

    # Entrées des métabolites
    if 'metabolites' not in st.session_state:
        st.session_state.metabolites = []

    # Affichage et modification des métabolites existants
    to_delete = None
    for meta in st.session_state.metabolites:
        cols = st.columns([3,2,1])
        with cols[0]:
            meta['nom'] = st.text_input("Nom du métabolite", value=meta.get('nom',''), key=f"nom_{meta['id']}")
        with cols[1]:
            meta['pourcentage'] = st.number_input("Pourcentage (%)", value=meta.get('pourcentage',0.0), min_value=0.0, max_value=100.0, key=f"pct_{meta['id']}")
        with cols[2]:
            if st.button("Supprimer", key=f"del_{meta['id']}"):
                to_delete = meta['id']

    # Supprimer en dehors de la boucle
    if to_delete is not None:
        st.session_state.metabolites = [m for m in st.session_state.metabolites if m['id'] != to_delete]
        st.experimental_rerun()

    # Ajouter un nouveau métabolite
    with st.expander("Ajouter un métabolite"):
        new_nom = st.text_input("Nom du métabolite", key="new_meta_nom")
        new_pct = st.number_input("Pourcentage (%)", min_value=0.0, max_value=100.0, key="new_meta_pct")
        if st.button("Ajouter le métabolite", key="add_meta"):
            if new_nom:
                st.session_state.metabolites.append({"id": str(uuid.uuid4()), "nom": new_nom, "pourcentage": new_pct})
                st.success(f"{new_nom} ajouté à la formulation")
                st.experimental_rerun()
            else:
                st.warning("Nom du métabolite requis !")

    # Calcul du score simple
    if st.button("Calculer score"):
        score = int(miel*0.5 + pla*0.2 + eps*0.2 + lacto*0.1)
        def interpretation_score(score):
            if score < 15:
                return ("Score faible — optimisation recommandée.", "#415A77", "score-poor")
            elif 15 <= score < 30:
                return ("Score satisfaisant — tests supplémentaires recommandés.", "#1B263B", "score-good")
            else:
                return ("Score excellent — formulation équilibrée.", "#0D1B2A", "score-excellent")
        message, hex_color, css_class = interpretation_score(score)

        st.markdown(
            f"""
            <div class="score-card {css_class}" style="background-color:{hex_color};">
              <div class="score-title">Résultat de l'analyse in silico</div>
              <div class="score-value">Score : {score}</div>
              <div class="score-text">{html.escape(message)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Sauvegarde CSV
        out_dir = "resultats"
        try:
            os.makedirs(out_dir, exist_ok=True)
            base = {
                "chercheur": chercheur or "anonyme",
                "miel": miel,
                "pla": pla,
                "eps": eps,
                "lacto": lacto,
                "score": score
            }
            meta_cols = {}
            for i, meta in enumerate(st.session_state.metabolites, start=1):
                meta_cols[f"meta_{i}_nom"] = meta.get("nom", "")
                meta_cols[f"meta_{i}_pourcentage"] = meta.get("pourcentage", 0.0)
            row = {**base, **meta_cols}
            df = pd.DataFrame([row])
            safe_name = (chercheur or "anonyme").strip().replace(" ", "_").replace("/", "_")
            path = os.path.join(out_dir, f"formulation_{safe_name}.csv")
            df.to_csv(path, index=False)
            st.success("Rapport sauvegardé avec succès.")
            st.info(f"Chemin : {path}")
        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde du rapport : {e}")

    st.markdown("</div>", unsafe_allow_html=True)

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
        st.markdown("Affichage professionnel — les résultats incluent titre, date et lien direct lorsque disponible.")

        # PubMed
        st.markdown("### PubMed — Top résultats")
        try:
            esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {"db": "pubmed", "term": terme, "retmax": 6, "retmode": "json"}
            r = requests.get(esearch_url, params=params, timeout=10)
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if ids:
                esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                s = requests.get(esummary_url, params={"db":"pubmed","id":",".join(ids),"retmode":"json"}, timeout=10)
                s.raise_for_status()
                summaries = s.json().get("result", {})
                for pid in ids:
                    info = summaries.get(pid, {})
                    title = info.get("title") or f"PubMed {pid}"
                    pubdate = info.get("pubdate", "")
                    source = info.get("source", "")
                    pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
                    display = f"- <b><a href='{pubmed_url}' target='_blank' style='color:#0A84FF;text-decoration:none'>{html.escape(title)}</a></b>"
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
#  PAGE : VALIDATION
# -------------------------
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Visualisation et score de stabilité</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Composant":["Miel","PLA","EPS","Lactobacillus"] + [m["nom"] for m in st.session_state.get("metabolites", [])],
        "Contribution":[40,1,2,1] + [m["pourcentage"] for m in st.session_state.get("metabolites", [])]
    })
    st.bar_chart(df.set_index("Composant"))



