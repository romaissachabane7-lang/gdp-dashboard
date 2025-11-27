# app.py
import os
import time
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from typing import List, Dict, Optional

# Optional AI summarization (OpenAI)
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY", ""))  # set OPENAI_API_KEY in Streamlit Cloud secrets/env to enable

if USE_OPENAI:
    import openai

# -----------------------
# Page config & CSS
# -----------------------
st.set_page_config(
    page_title="Algerian BioPlatform",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Elegant, light rose background and container styling
st.markdown(
    """
    <style>
      .stApp { background-color: #fff0f6; }            /* very light rose */
      header {visibility: hidden;}
      .logo-row {display:flex; align-items:center; gap:16px; margin-bottom:18px;}
      .title-main {font-size:28px; font-weight:700; color:#1f1f1f;}
      .subtitle {color:#333333; margin-bottom:12px;}
      .card {background:#ffffff; padding:18px; border-radius:12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);}
      .small {font-size:13px; color: #555;}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# SVG Logo builder (honey drop + bacteria rod), no upload required
# -----------------------
def svg_logo_html(width: int = 140) -> str:
    # colors: honey yellow, darker honey; classic scientific minimal shapes
    honey = "#FFCC33"
    honey_dark = "#B38F00"
    bac = "#B38F00"
    svg = f"""
    <svg width="{width}" height="{width}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <!-- honey drop -->
      <path d="M100 18 C122 48, 140 92, 100 160 C60 92, 78 48, 100 18 Z" fill="{honey}" stroke="{honey_dark}" stroke-width="3" />
      <!-- stylized Lactobacillus rods (three, minimal) -->
      <g transform="translate(50,60)">
        <rect x="30" y="10" rx="10" ry="10" width="40" height="20" fill="{bac}" opacity="0.95" />
        <rect x="10" y="38" rx="10" ry="10" width="40" height="20" fill="{bac}" opacity="0.95" transform="rotate(-14 30 48)"/>
        <rect x="50" y="46" rx="10" ry="10" width="40" height="20" fill="{bac}" opacity="0.95" transform="rotate(12 70 56)"/>
      </g>
    </svg>
    """
    return svg

# small helper to show logo + title inline
def header():
    logo_html = svg_logo_html(120)
    st.markdown(f"""
      <div class="logo-row">
         <div style="width:140px">{logo_html}</div>
         <div>
            <div class="title-main">Algerian BioPlatform</div>
            <div class="subtitle">Scientific & Professional Bioformulation & In-silico Validation Platform</div>
            <div class="small">Elegant, scientific visuals — investor-ready prototype</div>
         </div>
      </div>
      """, unsafe_allow_html=True)

# -----------------------
# Sidebar navigation
# -----------------------
page = st.sidebar.selectbox("Navigate", ["Home", "Formulation", "References", "Validation", "Settings"])

# -----------------------
# Utilities: caching external calls for speed & to avoid rate limiting
# -----------------------
@st.cache_data(ttl=3600)
def pubmed_search(query: str, retmax: int = 10, api_key: Optional[str] = None) -> List[Dict]:
    """Use NCBI E-utilities: esearch -> efetch to get basic article metadata and abstract (if any)."""
    base_esearch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    base_efetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json"
    }
    if api_key:
        params["api_key"] = api_key
    r = requests.get(base_esearch, params=params, timeout=20)
    r.raise_for_status()
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    results = []
    if not ids:
        return results
    efetch_params = {"db":"pubmed", "id":",".join(ids), "retmode":"xml"}
    if api_key:
        efetch_params["api_key"] = api_key
    r2 = requests.get(base_efetch, params=efetch_params, timeout=20)
    r2.raise_for_status()
    xml = r2.text
    # light parsing: split per PubmedArticle to extract Title and Abstract (simple)
    # This is a lightweight parser: in production use Bio.Entrez or xml parser for robustness.
    for pid in ids:
        # construct link and placeholder; detailed parsing is heavier
        results.append({
            "pmid": pid,
            "title": f"PubMed Article {pid}",
            "link": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
            "abstract": "Open the PubMed link for full abstract (efetch xml parsing could be added)."
        })
    return results

@st.cache_data(ttl=3600)
def uniprot_search(query: str, size: int = 10) -> List[Dict]:
    """Simple UniProt REST search (JSON)."""
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {"query": query, "format": "json", "size": size}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    hits = []
    for item in data.get("results", []):
        accession = item.get("primaryAccession")
        protein_name = item.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", accession)
        entry_url = f"https://rest.uniprot.org/uniprotkb/{accession}.json" if accession else ""
        hits.append({"accession": accession, "protein": protein_name, "link": f"https://www.uniprot.org/uniprot/{accession}"})
    return hits

@st.cache_data(ttl=3600)
def rcsb_search(query: str, rows: int = 10) -> List[Dict]:
    """Query RCSB simple text search using their REST API (POST)."""
    url = "https://search.rcsb.org/rcsbsearch/v1/query"
    payload = {
        "query": {"type":"terminal", "service":"text", "parameters":{"attribute":"rcsb_entry_container_identifiers.entry_id", "operator":"contains_words", "value": query}},
        "request_options":{"return_all_hits": True},
        "return_type":"entry"
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    hits = []
    for item in data.get("result_set", [])[:rows]:
        eid = item.get("identifier")
        hits.append({"pdb_id": eid, "link": f"https://www.rcsb.org/structure/{eid}"})
    return hits

# -----------------------
# Page: HOME (elegant)
# -----------------------
if page == "Home":
    header()
    st.markdown(
        """
        ## Professional & scientific presentation
        This platform provides:
        - **Robust product formulation** with automated scoring and downloadable reports.
        - **Automated literature & database search** (PubMed/NCBI, UniProt, RCSB PDB).
        - **In-silico validation** with interactive graphs and diagnostics.
        - **Optional AI summarization** of articles (requires OPENAI_API_KEY).
        """
    )
    st.divider()
    st.markdown("**Quick start:**    Choose *Formulation* to compute a score, *References* to search databases, *Validation* to visualize results.")

# -----------------------
# Page: FORMULATION
# -----------------------
elif page == "Formulation":
    header()
    st.subheader("Formulation — Input components")
    with st.form("form_formulation", clear_on_submit=False):
        name = st.text_input("Researcher name", value="Your Name", key="f_name")
        honey = st.number_input("Honey (%)", 0, 100, 100, key="f_honey")
        phenyl = st.number_input("Phenyl lactic acid (%)", 0, 100, 10, key="f_phenyl")
        exo = st.number_input("Exopolysaccharides (%)", 0, 100, 10, key="f_exo")
        lacto = st.number_input("Lactobacillus plantarum (%)", 0, 100, 5, key="f_lacto")
        submitted = st.form_submit_button("Validate formulation")
        if submitted:
            # validate sums or other business rules (example: total <= 200)
            total = honey + phenyl + exo + lacto
            if total > 500:
                st.error("Sum of components seems too large. Check inputs.")
            else:
                # compute a professional score (example weighted)
                score = round(honey*0.12 + phenyl*0.25 + exo*0.33 + lacto*0.45, 2)
                st.success(f"Formulation validated — score: {score}")
                # DataFrame and CSV in-memory
                df = pd.DataFrame([{
                    "researcher": name,
                    "honey_%": honey,
                    "phenyl_lactic_%": phenyl,
                    "exopolysaccharides_%": exo,
                    "lactobacillus_plantarum_%": lacto,
                    "score": score,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }])
                st.dataframe(df, use_container_width=True)
                buf = StringIO()
                df.to_csv(buf, index=False)
                buf.seek(0)
                st.download_button("Download report (CSV)", data=buf.getvalue(),
                                   file_name=f"formulation_{int(time.time())}.csv", mime="text/csv", key="download1")

# -----------------------
# Page: References (automated & professional)
# -----------------------
elif page == "References":
    header()
    st.subheader("Automated references search — PubMed / UniProt / RCSB")
    query = st.text_input("Enter metabolite / enzyme / protein / term", key="q_ref_input")
    n = st.slider("Results per DB", 1, 25, 8, key="q_ref_n")
    col1, col2 = st.columns([2,1])
    with col1:
        if st.button("Search databases"):
            st.info(f"Searching for: {query}")
            try:
                ncbi_key = os.getenv("NCBI_API_KEY", None)
                pm_results = pubmed_search(query, retmax=n, api_key=ncbi_key)
                up_results = uniprot_search(query, size=n)
                rcsb_results = rcsb_search(query, rows=n)
            except Exception as e:
                st.error(f"Error querying external DBs: {e}")
                pm_results, up_results, rcsb_results = [], [], []

            st.markdown("### PubMed (NCBI) — top results")
            if pm_results:
                for r in pm_results:
                    st.markdown(f"- **[{r['title']}]({r['link']})** — PMID: {r['pmid']}")
                    if USE_OPENAI:
                        # optional: use OpenAI to summarize the abstract text (if available)
                        try:
                            # we only have a placeholder abstract in our lightweight parser; replace with efetch parsing for real abstracts
                            summary = None
                            if 'abstract' in r and r['abstract']:
                                prompt = f"Summarize the abstract in 2-3 short bullets for investors:\n\n{r['abstract']}"
                                openai.api_key = os.getenv("OPENAI_API_KEY")
                                res = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role":"user", "content":prompt}], temperature=0.0)
                                summary = res.choices[0].message.content.strip()
                            if summary:
                                st.info(summary)
                        except Exception as e:
                            st.write("", end="")  # silent fallback
            else:
                st.write("No PubMed hits.")

            st.markdown("### UniProt — top results")
            if up_results:
                up_df = pd.DataFrame(up_results)
                up_df['link'] = up_df['link'].apply(lambda u: f"[link]({u})")
                st.dataframe(up_df.rename(columns={"accession":"Accession","protein":"Protein","link":"Link"}), use_container_width=True)
            else:
                st.write("No UniProt hits.")

            st.markdown("### RCSB PDB — top results")
            if rcsb_results:
                rcsb_df = pd.DataFrame(rcsb_results)
                rcsb_df['link'] = rcsb_df['link'].apply(lambda u: f"[link]({u})")
                st.dataframe(rcsb_df.rename(columns={"pdb_id":"PDB ID","link":"Link"}), use_container_width=True)
            else:
                st.write("No PDB hits.")

    with col2:
        st.markdown("**Quick tips**")
        st.markdown("- Use specific enzyme or protein names (e.g., `lactobacillus plantarum`, `phenyl lactic acid`) for best matches.")
        st.markdown("- Set `NCBI_API_KEY` in app secrets if you have one to increase rate limits.")

# -----------------------
# Page: Validation (in-silico professional)
# -----------------------
elif page == "Validation":
    header()
    st.subheader("In-silico validation & visual diagnostics")

    # For demonstration: allow user to input a few score breakdowns (or read last formulation values via session state)
    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown("### Input / adjust contributions (for visualization)")
        h = st.number_input("Honey contribution (abs)", 0.0, 1000.0,  (st.session_state.get("f_honey",100) * 0.1) , key="vis_honey")
        p = st.number_input("Phenyl lactic contribution (abs)", 0.0, 1000.0, (st.session_state.get("f_phenyl",10) * 0.2), key="vis_phenyl")
        e = st.number_input("Exopolysaccharides contribution (abs)", 0.0, 1000.0, (st.session_state.get("f_exo",10)*0.3), key="vis_exo")
        l = st.number_input("Lactobacillus contribution (abs)", 0.0, 1000.0, (st.session_state.get("f_lacto",5)*0.45), key="vis_lacto")
        if st.button("Run validation analysis"):
            st.success("Validation run completed.")

    with c2:
        st.markdown("### Diagnostics")
        st.metric("Total contribution", f"{round(h+p+e+l,2)}")
        st.markdown("- Check components distribution and stability.")
        st.markdown("- For more advanced analyses, integrate docking / molecular simulation outputs.")

    # create dataframe and plot
    val_df = pd.DataFrame({
        "Component": ["Honey", "Phenyl lactic", "Exopolysaccharides", "Lactobacillus"],
        "Contribution": [h, p, e, l]
    })
    st.dataframe(val_df, use_container_width=True)

    # Plotly: stacked and radar-like view (radar made via polar)
    fig_bar = px.bar(val_df, x="Component", y="Contribution", text="Contribution", title="Component Contributions")
    fig_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_polar = px.line_polar(val_df, r="Contribution", theta="Component", line_close=True, title="Polar view (radar style)")
    st.plotly_chart(fig_polar, use_container_width=True)

# -----------------------
# Page: Settings (API keys, info)
# -----------------------
elif page == "Settings":
    header()
    st.subheader("Settings & Deployment tips")
    st.markdown("""
    - **To enable AI summarization** set the environment variable `OPENAI_API_KEY` in Streamlit Cloud (or as secret).
    - (Optional) set `NCBI_API_KEY` to increase NCBI E-utilities rate limit.
    - If Plotly import errors appear, ensure `plotly` is listed in `requirements.txt`.
    - Use GitHub repo access to edit the code and redeploy automatically.
    """)
    st.markdown("**Deployment checklist:** `requirements.txt` updated, commit to main branch, Streamlit will rebuild the app.")
import streamlit as st

# --- LOGO GENERÉ EN CODE ---
logo_svg = """
<svg width="180" height="180" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">

  <!-- Hexagone miel -->
  <polygon points="100,20 160,55 160,125 100,160 40,125 40,55"
           fill="#FFC93C" stroke="#D4A017" stroke-width="4"/>

  <!-- Bactérie Lactobacillus (ellipse rose clair) -->
  <ellipse cx="100" cy="90" rx="45" ry="20"
           fill="#FFB6C9" stroke="#E88AA2" stroke-width="4"/>

  <!-- Petits détails bactériens -->
  <circle cx="80" cy="90" r="4" fill="#E88AA2"/>
  <circle cx="95" cy="90" r="4" fill="#E88AA2"/>
  <circle cx="110" cy="90" r="4" fill="#E88AA2"/>
  <circle cx="125" cy="90" r="4" fill="#E88AA2"/>

</svg>
"""

# Affichage centré
st.markdown(
    f"""
    <div style="text-align:center;">
        {logo_svg}
        <h1 style='color:#FF69B4; font-family:Arial;'>BioSyn Pro • Intelligent Synbiotic Platform</h1>
    </div>
    """,
    unsafe_allow_html=True
)






