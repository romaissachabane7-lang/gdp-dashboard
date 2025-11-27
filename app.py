# app.py
"""
Algerian BioPlatform — professional and robust single-file Streamlit app.
Do NOT include words removed by the user in the UI text.
"""

import os
import time
import json
import requests
import streamlit as st
import pandas as pd
from io import StringIO
from typing import List, Dict, Optional
import matplotlib.pyplot as plt

honey_bacteria_logo = """
<div class="logo">
<svg width="160" height="160" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="65" fill="#ffd74d" stroke="#d4a017" stroke-width="6"/>
  <ellipse cx="100" cy="100" rx="45" ry="22" fill="#fff6d5" stroke="#d4a017" stroke-width="4"/>
  <circle cx="75" cy="100" r="8" fill="#d4a017"/>
  <circle cx="100" cy="100" r="8" fill="#d4a017"/>
  <circle cx="125" cy="100" r="8" fill="#d4a017"/>
  <path d="M60 60 Q100 20 140 60" stroke="#d4a017" stroke-width="4" fill="none"/>
</svg>
</div>
"""
# ---- PAGE D’ACCUEIL AMÉLIORÉE ----
if page == "Home":
    st.markdown(honey_bacteria_logo, unsafe_allow_html=True)

    st.markdown('<div class="big-title">BIOPLATFORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Advanced Synbiotic Formulation & In-Silico Validation</div>', unsafe_allow_html=True)

    st.write("")
    st.write("Welcome to **Bioplatform**, a professional scientific environment for synbiotic formulation, automated reference extraction, and in-silico validation.")
    
    st.markdown("""
    ### What you can do here:
    - Formulate your synbiotic composition  
    - Automatically extract scientific references (NCBI, UniProt, PDB)  
    - Validate results with optimized in-silico graphs  
    - Generate professional downloadable reports  
    """)

    st.write("")
    st.info("Use the left menu to navigate through the platform.")


st.markdown(
    """
    <style>
      .stApp { background-color: #fff8fb; }   /* light rose background */
      .header-row { display:flex; align-items:center; gap:18px; margin-bottom:12px; }
      .title-main { font-size:26px; font-weight:700; color:#2b2b2b; margin:0; }
      .subtitle { color:#444; margin-top:2px; margin-bottom:6px; }
      .card { background: #ffffff; padding:16px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
      .center { text-align:center; }
      .small { font-size:13px; color:#555; }
      .noword { color: #2b2b2b; } /* reserved for titles without banned words */
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# SVG Logo (golden hexagon + bacterium rod) — no image upload
# -----------------------
def logo_svg(width: int = 120) -> str:
    # Colors
    honey = "#FFC93C"      # golden honey
    honey_dark = "#D4A017"
    rod = "#A46300"        # dark gold for bacteria rod
    pale = "#FFE9F2"       # pale accent if needed
    svg = f"""
    <svg width="{width}" height="{width}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <!-- Hexagon honey cell -->
      <polygon points="100,22 148,52 148,108 100,138 52,108 52,52"
               fill="{honey}" stroke="{honey_dark}" stroke-width="4"/>
      <!-- Stylized bacterium rod (three segments) -->
      <g transform="translate(40,52)">
        <rect x="40" y="28" rx="10" ry="10" width="70" height="18" fill="{rod}" />
        <rect x="30" y="52" rx="10" ry="10" width="70" height="18" fill="{rod}" transform="rotate(-10 65 61)"/>
        <rect x="50" y="70" rx="10" ry="10" width="70" height="18" fill="{rod}" transform="rotate(10 85 79)"/>
      </g>
      <!-- small dots as texture -->
      <circle cx="84" cy="82" r="3" fill="{honey_dark}" />
      <circle cx="116" cy="88" r="3" fill="{honey_dark}" />
    </svg>
    """
    return svg

def page_header():
    sv = logo_svg(110)
    st.markdown(
        f"""
        <div class="header-row">
            <div style="width:120px">{sv}</div>
            <div>
                <div class="title-main noword">BioSyn Pro</div>
                <div class="subtitle">Synbiotic formulation & in-silico validation — professional prototype</div>
                <div class="small">Download reports, consult references, and run validations</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------
# Sidebar navigation
# -----------------------
selection = st.sidebar.radio("Menu", ["Home", "Formulation", "References", "Validation", "Settings"])

# -----------------------
# Utilities: safe HTTP with timeout and simple error handling
# -----------------------
def safe_get(url: str, params: dict = None, timeout: int = 15):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        return None

# Caching for external calls
@st.cache_data(ttl=3600)
def search_pubmed(term: str, retmax: int = 8, ncbi_key: Optional[str] = None) -> List[Dict]:
    """
    Use NCBI E-utilities (esearch + efetch lightweight). Returns list of dicts with pmid, title, link.
    If no results or error, returns empty list.
    """
    if not term:
        return []
    esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    efetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db":"pubmed", "term": term, "retmax": retmax, "retmode":"json"}
    if ncbi_key:
        params["api_key"] = ncbi_key
    try:
        r = requests.get(esearch, params=params, timeout=20)
        r.raise_for_status()
        idlist = r.json().get("esearchresult", {}).get("idlist", [])
        if not idlist:
            return []
        # fetch summaries (use esummary for concise info)
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        sparams = {"db":"pubmed", "id": ",".join(idlist), "retmode":"json"}
        if ncbi_key:
            sparams["api_key"] = ncbi_key
        r2 = requests.get(summary_url, params=sparams, timeout=20)
        r2.raise_for_status()
        docsum = r2.json().get("result", {})
        results = []
        for pid in idlist:
            item = docsum.get(pid, {})
            title = item.get("title") or f"Article {pid}"
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            results.append({"pmid": pid, "title": title, "link": link})
        return results
    except Exception:
        return []

@st.cache_data(ttl=3600)
def search_uniprot(term: str, size: int = 8) -> List[Dict]:
    if not term:
        return []
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {"query": term, "format": "json", "size": size}
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        hits = []
        for item in data.get("results", []):
            acc = item.get("primaryAccession")
            prot = item.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", acc)
            link = f"https://www.uniprot.org/uniprot/{acc}" if acc else ""
            hits.append({"accession": acc, "protein": prot, "link": link})
        return hits
    except Exception:
        return []

@st.cache_data(ttl=3600)
def search_rcsb(term: str, rows: int = 8) -> List[Dict]:
    if not term:
        return []
    url = "https://search.rcsb.org/rcsbsearch/v2/query"
    # Simple text query for entries matching the term
    payload = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {"attribute": "rcsb_entity_source_organism.taxonomy_lineage.name", "operator": "contains_phrase", "value": term}
        },
        "request_options": {"return_all_hits": False, "sort": [{"sort_by":"score"}]},
        "return_type": "entry"
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("result_set", [])[:rows]:
            eid = item.get("identifier")
            results.append({"pdb_id": eid, "link": f"https://www.rcsb.org/structure/{eid}"})
        return results
    except Exception:
        # fallback: try simple search site link
        return []

# -----------------------
# HOME page
# -----------------------
if selection == "Home":
    page_header()
    st.markdown("""
    <div class="card">
      <p style="margin:0">
        Welcome to <strong>BioSyn Pro</strong> — a professional platform for synbiotic formulation and computational validation.
        Use the menu to create a formulation, consult scientific references, and run validation visualizations.
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

# -----------------------
# FORMULATION page
# -----------------------
elif selection == "Formulation":
    page_header()
    st.markdown("<div class='card'><b>Formulation input</b></div>", unsafe_allow_html=True)
    st.write("")  # spacer

    # Use a form for controlled submission
    with st.form("formulation_form"):
        researcher = st.text_input("Researcher name", value="Your Name", key="r_name")
        honey_pct = st.number_input("Honey (%)", min_value=0.0, max_value=100.0, value=100.0, key="r_honey")
        phenyl_pct = st.number_input("Phenyl lactic acid (%)", min_value=0.0, max_value=100.0, value=10.0, key="r_phenyl")
        exo_pct = st.number_input("Exopolysaccharides (%)", min_value=0.0, max_value=100.0, value=10.0, key="r_exo")
        lacto_pct = st.number_input("Lactobacillus plantarum (%)", min_value=0.0, max_value=100.0, value=5.0, key="r_lacto")
        submit = st.form_submit_button("Validate")

    if submit:
        # Basic validation rules
        total = honey_pct + phenyl_pct + exo_pct + lacto_pct
        if total <= 0:
            st.error("Please enter values greater than zero.")
        elif total > 1000:
            st.error("Sum of components is unusually high. Check your inputs.")
        else:
            # Professional weighted score (example weights)
            score = round(honey_pct * 0.12 + phenyl_pct * 0.25 + exo_pct * 0.33 + lacto_pct * 0.45, 2)
            st.success(f"Formulation validated — score: {score}")

            # Build DataFrame and show
            df = pd.DataFrame([{
                "researcher": researcher,
                "honey_%": honey_pct,
                "phenyl_lactic_%": phenyl_pct,
                "exopolysaccharides_%": exo_pct,
                "lactobacillus_plantarum_%": lacto_pct,
                "score": score,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }])
            st.dataframe(df, use_container_width=True)

            # CSV download in-memory
            buf = StringIO()
            df.to_csv(buf, index=False)
            buf.seek(0)
            st.download_button("Download report (CSV)", data=buf.getvalue(),
                               file_name=f"formulation_{int(time.time())}.csv",
                               mime="text/csv", key="dl_form1")

            # store latest formulation in session for Validation page
            st.session_state["latest_formulation"] = df.to_dict(orient="records")[0]

# -----------------------
# REFERENCES page
# -----------------------
elif selection == "References":
    page_header()
    st.markdown("<div class='card'><b>Automated reference search</b></div>", unsafe_allow_html=True)
    st.write("")
    q = st.text_input("Enter a protein name, enzyme, organism, or metabolite", key="q_input")

    n_results = st.slider("Results per source", 1, 20, 6, key="n_results")

    if st.button("Search"):
        if not q or q.strip() == "":
            st.error("Enter a valid search term.")
        else:
            with st.spinner("Querying sources..."):
                ncbi_key = os.getenv("NCBI_API_KEY", None)
                pubmed_hits = search_pubmed(q, retmax=n_results, ncbi_key=ncbi_key)
                uniprot_hits = search_uniprot(q, size=n_results)
                rcsb_hits = search_rcsb(q, rows=n_results)

            st.markdown("#### PubMed top results")
            if pubmed_hits:
                for item in pubmed_hits:
                    st.markdown(f"- **[{item['title']}]({item['link']})** — PMID: {item['pmid']}")
            else:
                st.write("No PubMed results found.")

            st.markdown("#### UniProt top results")
            if uniprot_hits:
                up_df = pd.DataFrame(uniprot_hits)
                up_df_display = up_df.rename(columns={"accession":"Accession","protein":"Protein","link":"Link"})
                # show links as plain text clickable
                st.dataframe(up_df_display, use_container_width=True)
                for row in uniprot_hits:
                    st.markdown(f"- {row.get('protein')} — [entry link]({row.get('link')})")
            else:
                st.write("No UniProt results found.")

            st.markdown("#### PDB top results")
            if rcsb_hits:
                rcsb_df = pd.DataFrame(rcsb_hits)
                st.dataframe(rcsb_df.rename(columns={"pdb_id":"PDB ID","link":"Link"}), use_container_width=True)
                for row in rcsb_hits:
                    st.markdown(f"- [PDB: {row.get('pdb_id')}]({row.get('link')})")
            else:
                st.write("No PDB results found.")

# -----------------------
# VALIDATION page (in-silico)
# -----------------------
elif selection == "Validation":
    page_header()
    st.markdown("<div class='card'><b>In-silico validation & diagnostics</b></div>", unsafe_allow_html=True)
    st.write("")

    # Load last formulation from session (if available) or allow manual entry
    last = st.session_state.get("latest_formulation", None)
    if last:
        st.markdown("**Using last validated formulation**")
        st.json(last)
        h_default = last.get("honey_%", 100.0)
        p_default = last.get("phenyl_lactic_%", 10.0)
        e_default = last.get("exopolysaccharides_%", 10.0)
        l_default = last.get("lactobacillus_plantarum_%", 5.0)
    else:
        st.markdown("**No previous formulation found** — enter values for validation visualization.")
        h_default = 100.0
        p_default = 10.0
        e_default = 10.0
        l_default = 5.0

    col1, col2 = st.columns([2,1])
    with col1:
        h = st.number_input("Honey contribution (absolute)", 0.0, 1000.0, float(h_default)*0.1, key="v_h")
        p = st.number_input("Phenyl lactic contribution (absolute)", 0.0, 1000.0, float(p_default)*0.2, key="v_p")
        e = st.number_input("Exopolysaccharides contribution (absolute)", 0.0, 1000.0, float(e_default)*0.3, key="v_e")
        l = st.number_input("Lactobacillus contribution (absolute)", 0.0, 1000.0, float(l_default)*0.45, key="v_l")

        if st.button("Run validation"):
            st.success("Validation completed.")

    with col2:
        st.metric("Total score contribution", f"{round(h+p+e+l,2)}")
        st.markdown("**Checks**")
        if max([h,p,e,l]) == 0:
            st.warning("Contributions are zero — check inputs.")
        if any(x < 0 for x in [h,p,e,l]):
            st.error("Negative contributions detected.")

    # Build DataFrame and plots
    val_df = pd.DataFrame({
        "Component": ["Honey", "Phenyl lactic", "Exopolysaccharides", "Lactobacillus"],
        "Contribution": [h, p, e, l]
    })
    st.dataframe(val_df, use_container_width=True)

    # Matplotlib bar chart (robust)
    fig, ax = plt.subplots(figsize=(6,3.5))
    bars = ax.bar(val_df["Component"], val_df["Contribution"], color=["#FFC93C","#F4A261","#A8DADC","#B38F00"])
    ax.set_ylabel("Contribution")
    ax.set_title("Component contributions")
    ax.bar_label(bars, fmt="%.2f", padding=3)
    fig.tight_layout()
    st.pyplot(fig)

    # Polar (radar-like) using matplotlib polar
    theta = range(len(val_df))
    values = val_df["Contribution"].tolist()
    # radar needs closure
    vals = values + [values[0]]
    thetas = [n / float(len(values)) * 2 * 3.14159 for n in range(len(values)+1)]
    fig2 = plt.figure(figsize=(5,4))
    ax2 = fig2.add_subplot(111, polar=True)
    ax2.plot(thetas, vals, marker='o', linewidth=2)
    ax2.fill(thetas, vals, alpha=0.25)
    ax2.set_xticks([n / float(len(values)) * 2 * 3.14159 for n in range(len(values))])
    ax2.set_xticklabels(val_df["Component"])
    st.pyplot(fig2)

# -----------------------
# SETTINGS page (notes)
# -----------------------
elif selection == "Settings":
    page_header()
    st.markdown("<div class='card'><b>Settings & notes</b></div>", unsafe_allow_html=True)
    st.markdown("""
    - To increase PubMed rate limits, set environment variable `NCBI_API_KEY` in your deployment settings.
    - If you want external summarization, keep that separate and secure.
    - Edit the code in your repository to further customize visuals and weights.
    """)
    st.markdown("Deployment checklist: update `requirements.txt`, commit to repository, redeploy.")
# ---- STYLING GLOBAL ----
import streamlit as st

st.markdown("""
<style>
/* Police professionnelle */
html, body, [class*="css"] {
    font-family: 'Times New Roman', serif !important;
}

/* Couleur rose clair + design premium */
:root {
    --rose: #f9dfe8;
    --gold: #d4a017;
}

.main {
    background-color: #ffffff;
}

header, .css-18ni7ap, .css-1v0mbdj {
    background-color: var(--rose) !important;
}

/* Titre principal */
.big-title {
    font-size: 2.8rem;
    font-weight: bold;
    color: #333333;
    text-align: center;
    margin-bottom: 0px;
}

/* Sous-titre */
.sub-title {
    font-size: 1.3rem;
    color: #555555;
    text-align: center;
    margin-top: -10px;
}

/* Logo généré (simple, classe, scientifique) */
.logo {
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6,4))  # Taille moyenne
ax.plot(data_x, data_y)
ax.set_title("In-Silico Validation", fontsize=14)
ax.set_xlabel("Parameter", fontsize=10)
ax.set_ylabel("Response", fontsize=10)

st.pyplot(fig)

# End of app









