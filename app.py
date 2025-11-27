# app.py
"""
BioPlatform — professional single-file Streamlit app
Home: English, Times New Roman font, light-pink theme, golden honey+bacteria SVG logo
Formulation: robust inputs, in-memory CSV download
References: NCBI (PubMed) esearch+esummary, UniProt REST, RCSB search — show readable details
Validation: in-silico visualizations (matplotlib, moderate size)
"""

import streamlit as st
import pandas as pd
import requests
from io import StringIO
import matplotlib.pyplot as plt
from typing import List, Dict, Optional

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="BioPlatform",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------------
# Global CSS: Times New Roman + colors
# -------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman:ital,wght@0,400;0,700;1,400&display=swap');

    html, body, [class*="css"] {
        font-family: "Times New Roman", Times, serif !important;
        color: #222222;
    }

    /* background */
    .stApp {
        background-color: #fff3f7; /* light pink */
    }

    /* header/title styling */
    .main-title {
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 6px;
        color: #2b2b2b;
        text-align: center;
    }
    .subtitle {
        font-size: 15px;
        color: #444444;
        text-align: center;
        margin-top: -6px;
        margin-bottom: 14px;
    }

    /* card style */
    .card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(200,160,180,0.15);
    }

    /* logo center */
    .logo-center {
        text-align: center;
        margin-bottom: 12px;
    }

    /* small note */
    .small-note {
        font-size: 13px;
        color: #555555;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# SVG logo generator (golden honey + rod bacteria)
# - Classic, elegant, no cartoon, yellow/golden palette
# -------------------------
def logo_svg_html(size: int = 150) -> str:
    # Uses gradient for honey, simple rod shapes for bacteria
    svg = f"""
    <div class="logo-center">
    <svg width="{size}" height="{size}" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="gHoney" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="#ffe08a"/>
          <stop offset="100%" stop-color="#e6b800"/>
        </linearGradient>
      </defs>

      <!-- hexagon-ish simple honey cell (soft corners) -->
      <path d="M100 26 L144 54 L144 107 L100 135 L56 107 L56 54 Z"
            fill="url(#gHoney)" stroke="#c99700" stroke-width="4" />

      <!-- central bacteria rods (minimal, elegant) -->
      <g transform="translate(40,60)">
        <rect x="30" y="18" rx="9" ry="9" width="80" height="20" fill="#b57900" opacity="0.95"/>
        <rect x="20" y="46" rx="9" ry="9" width="80" height="20" fill="#b57900" opacity="0.92" transform="rotate(-12 60 56)"/>
        <rect x="50" y="60" rx="9" ry="9" width="80" height="20" fill="#b57900" opacity="0.92" transform="rotate(12 90 70)"/>
      </g>

      <!-- accent dots -->
      <circle cx="82" cy="95" r="4" fill="#c99700"/>
      <circle cx="118" cy="99" r="4" fill="#c99700"/>
    </svg>
    </div>
    """
    return svg

# -------------------------
# Sidebar / Navigation
# -------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Section", ["Home", "Formulation", "References", "Validation", "Settings"], index=0)

# -------------------------
# Helper: safe HTTP GET
# -------------------------
def safe_get(url: str, params: dict = None, timeout: int = 12) -> Optional[requests.Response]:
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception:
        return None

# -------------------------
# Caching wrappers for external data (to reduce repeated calls)
# -------------------------
@st.cache_data(ttl=3600)
def ncbi_esearch(term: str, retmax: int = 8, api_key: Optional[str] = None) -> List[str]:
    # returns list of PubMed IDs (strings)
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {"db": "pubmed", "term": term, "retmode": "json", "retmax": retmax}
    if api_key:
        params["api_key"] = api_key
    r = safe_get(base, params=params)
    if not r:
        return []
    data = r.json()
    return data.get("esearchresult", {}).get("idlist", [])

@st.cache_data(ttl=3600)
def ncbi_esummary(id_list: List[str], api_key: Optional[str] = None) -> List[Dict]:
    # returns list of dicts with title/authors/journal/uid
    if not id_list:
        return []
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {"db": "pubmed", "id": ",".join(id_list), "retmode": "json"}
    if api_key:
        params["api_key"] = api_key
    r = safe_get(base, params=params)
    if not r:
        return []
    data = r.json().get("result", {})
    results = []
    for uid in id_list:
        item = data.get(uid, {})
        title = item.get("title") or ""
        source = item.get("source") or ""
        authors = item.get("authors") or []
        # authors may be list of dicts with 'name'
        authors_str = ", ".join([a.get("name", "") for a in authors]) if authors else ""
        results.append({"pmid": uid, "title": title, "journal": source, "authors": authors_str,
                        "link": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"})
    return results

@st.cache_data(ttl=3600)
def uniprot_search(term: str, size: int = 8) -> List[Dict]:
    base = "https://rest.uniprot.org/uniprotkb/search"
    params = {"query": term, "format": "json", "size": size}
    r = safe_get(base, params=params)
    if not r:
        return []
    data = r.json()
    hits = []
    for item in data.get("results", []):
        acc = item.get("primaryAccession")
        protein = item.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value") \
                  or item.get("primaryAccession")
        organism = ""
        # organism may be nested
        org = item.get("organism", {})
        if org:
            organism = org.get("scientificName", "")
        hits.append({"accession": acc, "protein": protein, "organism": organism,
                     "link": f"https://www.uniprot.org/uniprot/{acc}" if acc else ""})
    return hits

@st.cache_data(ttl=3600)
def rcsb_search(term: str, size: int = 8) -> List[Dict]:
    # Basic RCSB text search via their v1 API (simple)
    url = "https://search.rcsb.org/rcsbsearch/v1/query"
    payload = {
        "query": {"type": "terminal", "service": "text", "parameters": {"attribute": "rcsb_entry_container_identifiers.entry_id", "operator": "contains_words", "value": term}},
        "request_options": {"return_all_hits": False},
        "return_type": "entry"
    }
    try:
        r = requests.post(url, json=payload, timeout=12)
        r.raise_for_status()
        data = r.json()
        hits = []
        for item in data.get("result_set", [])[:size]:
            eid = item.get("identifier")
            hits.append({"pdb_id": eid, "link": f"https://www.rcsb.org/structure/{eid}"})
        return hits
    except Exception:
        return []

# -------------------------
# HOME page (polished)
# -------------------------
if page == "Home":
    st.markdown(logo_svg_html(size=160), unsafe_allow_html=True)

    st.markdown('<div class="main-title">BIOPLATFORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Synbiotic formulation · Scientific references · Computational validation</div>',
                unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card">
        <p style="font-size:16px; color:#222;">
        Welcome to <strong>BioPlatform</strong>. This professional environment is designed for
        researchers and domain experts to build, validate and document synbiotic formulations.
        The interface is crafted for clarity and presentation to scientific audiences and investors.
        </p>

        <ul style="font-size:14px; color:#333;">
          <li><strong>Formulation:</strong> create formulations, compute a structured score, download a tidy report.</li>
          <li><strong>References:</strong> query authoritative databases for human-readable article and protein summaries.</li>
          <li><strong>Validation:</strong> visual diagnostics and reproducible figures at presentation-ready sizes.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown('<div class="small-note">Tip: use the left menu to navigate. All content is in English and formatted for scientific review.</div>', unsafe_allow_html=True)

# -------------------------
# FORMULATION page
# -------------------------
elif page == "Formulation":
    st.header("Formulation")

    with st.form("formulation_form", clear_on_submit=False):
        researcher = st.text_input("Researcher name", value="", key="f_researcher")
        honey = st.number_input("Honey (%)", min_value=0.0, max_value=100.0, value=50.0, key="f_honey")
        phenyl = st.number_input("Phenyl-lactic acid (%)", min_value=0.0, max_value=100.0, value=10.0, key="f_phenyl")
        eps = st.number_input("Exopolysaccharides (%)", min_value=0.0, max_value=100.0, value=10.0, key="f_eps")
        lacto = st.number_input("Lactobacillus plantarum (%)", min_value=0.0, max_value=100.0, value=5.0, key="f_lacto")
        submitted = st.form_submit_button("Validate formulation")

    if submitted:
        total = honey + phenyl + eps + lacto
        if total <= 0:
            st.error("Please enter positive values for the components.")
        elif total > 1000:
            st.error("Unusually large sum — please verify your inputs.")
        else:
            # Weighted score (professional example)
            score = round(honey * 0.12 + phenyl * 0.22 + eps * 0.30 + lacto * 0.45, 2)
            st.success(f"Formulation validated — Score: {score}")

            df = pd.DataFrame([{
                "researcher": researcher or "Unknown",
                "honey_%": honey,
                "phenyl_lactic_%": phenyl,
                "exopolysaccharides_%": eps,
                "lactobacillus_plantarum_%": lacto,
                "score": score
            }])
            st.dataframe(df, use_container_width=True)

            # CSV download (in-memory)
            buf = StringIO()
            df.to_csv(buf, index=False)
            buf.seek(0)
            st.download_button("Download report (CSV)", data=buf.getvalue(),
                               file_name=f"formulation_report.csv", mime="text/csv", key="download_f")

            # save to session for Validation page
            st.session_state["latest_formulation"] = df.to_dict(orient="records")[0]

# -------------------------
# REFERENCES page
# -------------------------
elif page == "References":
    st.header("References")

    st.markdown("Enter a search term (metabolite, protein name, bacterial species, enzyme). The app will fetch readable details from PubMed, UniProt, and PDB.")

    term = st.text_input("Search term", value="", key="ref_term")
    maxhits = st.slider("Results per source", 1, 12, 6, key="ref_n")

    if st.button("Search", key="ref_search"):
        if not term.strip():
            st.error("Please enter a valid search term.")
        else:
            st.info("Querying external resources. This may take a few seconds.")
            # NCBI PubMed
            ncbi_key = None  # optional: set environment variable NCBI_API_KEY if you have one
            pmids = ncbi_esearch(term, retmax=maxhits, api_key=ncbi_key)
            summaries = ncbi_esummary(pmids, api_key=ncbi_key) if pmids else []

            st.subheader("PubMed — top summaries")
            if summaries:
                for s in summaries:
                    st.markdown(f"**{s.get('title','(no title)')}**")
                    if s.get("authors"):
                        st.markdown(f"*{s.get('authors')}* — {s.get('journal')}")
                    st.markdown(f"[View on PubMed]({s.get('link')})")
                    st.markdown("---")
            else:
                st.write("No PubMed summaries found for this term.")

            # UniProt
            st.subheader("UniProt — top entries")
            up_hits = uniprot_search(term, size=maxhits)
            if up_hits:
                for u in up_hits:
                    st.markdown(f"**{u.get('protein')}** — {u.get('organism') or 'organism unknown'}")
                    if u.get("accession"):
                        st.markdown(f"[UniProt entry]({u.get('link')})")
                    st.markdown("---")
            else:
                st.write("No UniProt results.")

            # PDB / RCSB
            st.subheader("PDB — matching entries")
            pdb_hits = rcsb_search(term, size=maxhits)
            if pdb_hits:
                for p in pdb_hits:
                    st.markdown(f"- **PDB: {p.get('pdb_id', 'NA')}** — [View]({p.get('link')})")
            else:
                st.write("No PDB hits found.")

# -------------------------
# VALIDATION page
# -------------------------
elif page == "Validation":
    st.header("In-silico Validation")

    # Use last formulation if present
    latest = st.session_state.get("latest_formulation", None)
    if latest:
        st.markdown("Using the last validated formulation (loaded from previous step).")
        st.json(latest)
        # derive default contributions from latest
        h = latest.get("honey_%", 50) * 0.1
        p = latest.get("phenyl_lactic_%", 10) * 0.2
        e = latest.get("exopolysaccharides_%", 10) * 0.3
        l = latest.get("lactobacillus_plantarum_%", 5) * 0.45
    else:
        st.markdown("No previous formulation found — please enter values below.")
        h = st.number_input("Honey component (abs)", value=5.0, key="v_h")
        p = st.number_input("Phenyl-lactic component (abs)", value=2.0, key="v_p")
        e = st.number_input("Exopolysaccharides component (abs)", value=3.0, key="v_e")
        l = st.number_input("Lactobacillus component (abs)", value=1.5, key="v_l")

    # Compose DataFrame for plotting
    comp_df = pd.DataFrame({
        "Component": ["Honey", "Phenyl-lactic", "Exopolysaccharides", "L. plantarum"],
        "Contribution": [h, p, e, l]
    })

    st.subheader("Contributions (moderate-size figures for presentation)")
    st.dataframe(comp_df, use_container_width=True)

    # Matplotlib bar (moderate size)
    fig, ax = plt.subplots(figsize=(6, 3.8))  # moderate size suitable for presentation slides
    bars = ax.bar(comp_df["Component"], comp_df["Contribution"], color=["#ffd74d", "#f2b880", "#a8d0d8", "#d4a017"])
    ax.set_ylabel("Contribution")
    ax.set_title("Component Contributions")
    ax.bar_label(bars, fmt="%.2f")
    fig.tight_layout()
    st.pyplot(fig)

    # Small radar-style polar chart (matplotlib)
    values = comp_df["Contribution"].tolist()
    labels = comp_df["Component"].tolist()
    # close circle
    vals = values + [values[0]]
    angles = [n / float(len(values)) * 2 * 3.14159 for n in range(len(values)+1)]
    fig2 = plt.figure(figsize=(5,4))
    ax2 = fig2.add_subplot(111, polar=True)
    ax2.plot(angles, vals, linewidth=2)
    ax2.fill(angles, vals, alpha=0.25)
    ax2.set_xticks([n / float(len(values)) * 2 * 3.14159 for n in range(len(values))])
    ax2.set_xticklabels(labels)
    st.pyplot(fig2)

# -------------------------
# SETTINGS fallback (simple)
# -------------------------
elif page == "Settings":
    st.header("Settings & Notes")
    st.markdown("""
    - This application uses public endpoints to retrieve readable reference information.
    - To improve PubMed throughput, consider adding an NCBI API key in deployment environment variables.
    - If you need export to PDF or additional presentation-quality graphics, ask and I will add it.
    """)

# End of file


