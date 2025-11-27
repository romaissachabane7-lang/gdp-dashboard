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

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fbf7ee; }
    .topbar { padding: 0; margin-bottom: 14px; }
    .card { background-color: #fffaf0; border-radius: 10px; padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 18px; }
    .nav-button { background-color: transparent; border: none; font-weight:600; color: #3b2f1f; padding: 8px 14px; border-radius:6px; }
    .nav-button:hover { background-color: #efe2b3; }
    .section-title { color:#4a3f2a; font-weight:700; font-size:20px; margin-bottom:10px; }
    .muted { color:#7a6b5a; font-size:13px; }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<div class='topbar'></div>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 5])
with col1:
    st.markdown(svg_logo, unsafe_allow_html=True)
with col2:
    st.markdown("""
      <div style="display:flex;align-items:center;justify-content:flex-end;height:90px;">
        <div style="margin-right:18px;"><button class="nav-button" onclick="">Accueil</button></div>
        <div style="margin-right:18px;"><button class="nav-button" onclick="">Formulation</button></div>
        <div style="margin-right:18px;"><button class="nav-button" onclick="">Références</button></div>
        <div style="margin-right:18px;"><button class="nav-button" onclick="">Validation</button></div>
      </div>
    """, unsafe_allow_html=True)

# --- Sidebar navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"], index=0)

# --- Stockage session des valeurs de formulation ---
if 'formulation' not in st.session_state:
    st.session_state['formulation'] = {'miel':40,'pla':1,'eps':2,'lacto':1}

# --- PAGE: Accueil ---
if page == "Accueil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Bienvenue</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">BioPlateforme Algérienne — simulation et validation in silico de formulations bioactives.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    a, b, c = st.columns([1,1,1])
    with a:
        st.markdown('<div class="card"><div style="font-weight:700;color:#3b2f1f">BioData Explorer</div><div class="muted">NCBI / PubMed / UniProt</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><div style="font-weight:700;color:#3b2f1f">Formulation Simulator</div><div class="muted">Composer et tester formulations</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="card"><div style="font-weight:700;color:#3b2f1f">In Silico Validator</div><div class="muted">Score & recommandations</div></div>', unsafe_allow_html=True)

# --- PAGE: Formulation ---
elif page == "Formulation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Formulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Saisissez les paramètres et validez pour générer un rapport.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    chercheur = st.text_input("Nom du chercheur")
    miel = st.slider("Miel (%)", 0, 100, st.session_state['formulation']['miel'])
    pla = st.slider("Acide phényllactique (%)", 0, 10, st.session_state['formulation']['pla'])
    eps = st.slider("Exopolysaccharides (%)", 0, 10, st.session_state['formulation']['eps'])
    lacto = st.slider("Lactobacillus plantarum (%)", 0, 5, st.session_state['formulation']['lacto'])

    if st.button("Valider la formulation"):
        # sauvegarder dans session_state
        st.session_state['formulation'] = {'miel':miel,'pla':pla,'eps':eps,'lacto':lacto}
        score = round((miel*0.2 + pla*2 + eps*1.5 + lacto*3),2)

        # Préparer le dossier
        out_dir = "resultats"
        os.makedirs(out_dir, exist_ok=True)
        df = pd.DataFrame({
            "chercheur":[chercheur],
            "miel":[miel],
            "pla":[pla],
            "eps":[eps],
            "lacto":[lacto],
            "score":[score]
        })
        safe_name = (chercheur or "anonyme").strip().replace(" ","_").replace("/","_")
        path = os.path.join(out_dir,f"formulation_{safe_name}.csv")
        df.to_csv(path,index=False)
        st.success(f"Formulation validée — score: {score}")
        st.info(f"Rapport sauvegardé: {path}")

# --- PAGE: Références ---
elif page == "Références":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Références scientifiques</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Recherche intégrée : PubMed + UniProt + PDB</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    terme = st.text_input("Rechercher (ex: Lactobacillus plantarum OR phenyllactic acid)")
    if terme:
        st.markdown(f"**Résultats pour :** {html.escape(terme)}")
        # PubMed
        st.markdown("### PubMed")
        try:
            params = {"db":"pubmed","term":terme,"retmax":5,"retmode":"json"}
            r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",params=params,timeout=5)
            r.raise_for_status()
            ids = r.json().get("esearchresult",{}).get("idlist",[])
            if ids:
                s = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                                 params={"db":"pubmed","id":",".join(ids),"retmode":"json"},timeout=5)
                s.raise_for_status()
                summaries = s.json().get("result",{})
                for pid in ids:
                    info = summaries.get(pid,{})
                    title = info.get("title",f"PubMed {pid}")
                    pubdate = info.get("pubdate","")
                    st.markdown(f"- [{html.escape(title)}](https://pubmed.ncbi.nlm.nih.gov/{pid}/) — {pubdate}")
            else:
                st.info("Aucun article PubMed trouvé.")
        except:
            st.error("Recherche PubMed impossible.")

        # UniProt
        st.markdown("### UniProt")
        try:
            r2 = requests.get("https://rest.uniprot.org/uniprotkb/search",
                              params={"query":terme,"format":"json","size":5},timeout=5)
            r2.raise_for_status()
            hits = r2.json().get("results",[])
            if hits:
                for entry in hits:
                    acc = entry.get("primaryAccession")
                    prot_desc = entry.get("proteinDescription",{})
                    rec_name = prot_desc.get("recommendedName",{}).get("fullName",{}).get("value","")
                    if not rec_name:
                        alt = prot_desc.get("alternativeNames",[])
                        if alt: rec_name = alt[0].get("fullName",{}).get("value","")
                    label = rec_name or acc
                    st.markdown(f"- [{label}](https://rest.uniprot.org/uniprotkb/{acc}) — Accession: `{acc}`")
            else:
                st.info("Aucun hit UniProt trouvé.")
        except:
            st.error("Recherche UniProt impossible.")

        # PDB / RCSB
        st.markdown("### PDB / RCSB")
        try:
            query_encoded = urllib.parse.quote_plus(terme)
            rcsb_link = f"https://www.rcsb.org/search?request={{\"query\":\"{query_encoded}\"}}"
            st.markdown(f"- [Recherche RCSB]({rcsb_link})")
        except:
            st.info("Impossible de générer le lien RCSB.")

# --- PAGE: Validation ---
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Visualisation des contributions réelles saisies dans la Formulation</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # utiliser session_state pour refléter la formulation réelle
    f = st.session_state['formulation']
    df = pd.DataFrame({
        "Composant":["Miel","PLA","EPS","Lactobacillus"],
        "Contribution":[f['miel'],f['pla'],f['eps'],f['lacto']]
    })
    st.bar_chart(df.set_index("Composant"))






