# app.py
import streamlit as st
import pandas as pd
from io import StringIO
import plotly.express as px

# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="Algerian BioPlatform",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# Custom CSS (rose clair)
# -----------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #ffe6f0;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# Function to display a scientific SVG logo (honey drop + bacteria)
# -----------------------
def display_logo():
    svg_logo = """
    <svg width="150" height="150" viewBox="0 0 200 200">
        <!-- Honey drop -->
        <path d="M100 20 C120 50, 130 100, 100 160 C70 100, 80 50, 100 20 Z" fill="#ffcc33" stroke="#b38f00" stroke-width="3"/>
        <!-- Bacteria (Lactobacillus plantarum) -->
        <rect x="85" y="60" width="30" height="60" rx="15" ry="15" fill="#b38f00"/>
        <rect x="70" y="80" width="30" height="60" rx="15" ry="15" fill="#b38f00" transform="rotate(-20 85 110)"/>
        <rect x="100" y="90" width="30" height="60" rx="15" ry="15" fill="#b38f00" transform="rotate(20 115 120)"/>
    </svg>
    """
    st.markdown(f'<div class="logo-container">{svg_logo}</div>', unsafe_allow_html=True)

# -----------------------
# Sidebar navigation
# -----------------------
page = st.sidebar.radio("Navigation", ["Home", "Formulation", "References", "Validation"])

# =======================
# HOME PAGE
# =======================
if page == "Home":
    display_logo()
    st.title("🧪 Algerian BioPlatform - Scientific AI Platform")
    st.markdown("""
    Welcome to the Algerian BioPlatform, a **scientific and professional platform** for biotechnology research.
    
    Features:
    - Product formulation with automated scoring
    - In silico validation with interactive graphs
    - Access to references from NCBI, PDB, and UniProt
    - Professional downloadable reports
    """)
    st.info("Use the sidebar to navigate between Formulation, References, and Validation.")

# =======================
# FORMULATION PAGE
# =======================
elif page == "Formulation":
    st.title("Product Formulation")

    # Inputs
    nom = st.text_input("Researcher Name", "YourName", key="nom_formulation")
    miel = st.number_input("Honey (%)", 0, 100, 100, key="miel_formulation")
    acide = st.number_input("Phenyl lactic acid (%)", 0, 100, 10, key="acide_formulation")
    exopolysaccharides = st.number_input("Exopolysaccharides (%)", 0, 100, 10, key="exopolys_formulation")
    lacto = st.number_input("Lactobacillus plantarum (%)", 0, 100, 5, key="lacto_formulation")

    # Score
    score = round((miel*0.1 + acide*0.2 + exopolysaccharides*0.3 + lacto*0.4), 2)
    st.success(f"Formulation validated — score: {score}")

    # DataFrame
    df = pd.DataFrame({
        "Researcher Name": [nom],
        "Honey (%)": [miel],
        "Phenyl lactic acid (%)": [acide],
        "Exopolysaccharides (%)": [exopolysaccharides],
        "Lactobacillus plantarum (%)": [lacto],
        "Score": [score]
    })

    # CSV download
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    st.download_button(
        "Download report",
        data=csv_buffer.getvalue(),
        file_name="formulation.csv",
        mime="text/csv",
        key="download_formulation"
    )

# =======================
# REFERENCES PAGE
# =======================
elif page == "References":
    st.title("Scientific References")
    st.markdown("Search for metabolites, enzymes, or proteins and get references from NCBI, PDB, and UniProt.")

    query = st.text_input("Enter keyword", key="query_ref")
    if st.button("Search"):
        st.info(f"Searching for: {query}")

        # Dynamic search URLs
        ncbi_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query}"
        pdb_url = f"https://www.rcsb.org/search?q={query}"
        uniprot_url = f"https://www.uniprot.org/uniprot/?query={query}"

        refs_df = pd.DataFrame({
            "Database": ["NCBI PubMed", "PDB", "UniProt"],
            "Link": [ncbi_url, pdb_url, uniprot_url],
            "Description": [
                "Articles and publications",
                "3D protein structures",
                "Protein sequences and annotations"
            ]
        })

        st.dataframe(refs_df, use_container_width=True)
        for i in range(len(refs_df)):
            st.markdown(f"[{refs_df['Database'][i]}]({refs_df['Link'][i]}) : {refs_df['Description'][i]}")

# =======================
# VALIDATION PAGE
# =======================
elif page == "Validation":
    st.title("In silico Validation")
    st.markdown("Automatic visualization of formulation contributions")

    # Validation data
    validation_df = pd.DataFrame({
        "Component": ["Honey", "Phenyl lactic acid", "Exopolysaccharides", "Lactobacillus plantarum"],
        "Contribution": [miel*0.1, acide*0.2, exopolysaccharides*0.3, lacto*0.4]
    })

    st.dataframe(validation_df, use_container_width=True)

    # Plotly bar chart
    fig = px.bar(
        validation_df,
        x="Component",
        y="Contribution",
        text="Contribution",
        title="Component Contribution to Total Score",
        labels={"Contribution":"Score Contribution"},
        color="Contribution",
        color_continuous_scale="Teal"
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(yaxis=dict(range=[0, max(validation_df["Contribution"])*1.2]))
    st.plotly_chart(fig, use_container_width=True)






