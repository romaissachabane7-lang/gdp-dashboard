###############################################
#                BIOPLATFORM                 #
#  Professional Synbiotic Formulation Suite   #
###############################################

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import requests

# ---------------- GLOBAL STYLING ----------------

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Times New Roman', serif !important;
}

:root {
    --rose: #f9dfe8;
    --gold: #d4a017;
}

header, .css-18ni7ap, .css-1v0mbdj {
    background-color: var(--rose) !important;
}

.big-title {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    color: #333333;
}

.sub-title {
    font-size: 1.3rem;
    text-align: center;
    color: #666666;
    margin-top: -15px;
}

.logo {
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGO SVG ----------------

honey_bacteria_logo = """
<div class="logo">
<svg width="150" height="150" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="65" fill="#ffd74d" stroke="#d4a017" stroke-width="6"/>
  <ellipse cx="100" cy="100" rx="45" ry="22" fill="#fff6d5" stroke="#d4a017" stroke-width="4"/>
  <circle cx="75" cy="100" r="8" fill="#d4a017"/>
  <circle cx="100" cy="100" r="8" fill="#d4a017"/>
  <circle cx="125" cy="100" r="8" fill="#d4a017"/>
  <path d="M60 60 Q100 20 140 60" stroke="#d4a017" stroke-width="4" fill="none"/>
</svg>
</div>
"""

# ---------------- SIDE MENU ----------------

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Home", "Formulation", "References", "In-Silico Validation"]
)

# ---------------- HOME PAGE ----------------

if page == "Home":
    st.markdown(honey_bacteria_logo, unsafe_allow_html=True)

    st.markdown('<div class="big-title">BIOPLATFORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Advanced Synbiotic Formulation & Scientific Validation Suite</div>',
                unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    ### Welcome  
    Bioplatform is a scientific environment designed for:
    
    - Professional synbiotic formulation  
    - Automatic extraction of scientific references  
    - In-silico validation using analytical graphs  
    - Generation of structured reports  
    """)

    st.info("Use the left-side menu to navigate the platform.")


# ---------------- FORMULATION PAGE ----------------

elif page == "Formulation":
    st.title("Synbiotic Formulation")

    nom = st.text_input("Researcher Name", "YourName")
    miel = st.number_input("Honey (%)", 0, 100, 100)
    acide = st.number_input("Phenyl-Lactic Acid (%)", 0, 100, 10)
    exo = st.number_input("Exopolysaccharides (%)", 0, 100, 10)
    lacto = st.number_input("Lactobacillus plantarum (%)", 0, 100, 5)

    score = round((miel*0.1 + acide*0.2 + exo*0.3 + lacto*0.4), 2)
    st.success(f"Formulation Score: {score}")

    df = pd.DataFrame({
        "Researcher": [nom],
        "Honey (%)": [miel],
        "PLA (%)": [acide],
        "EPS (%)": [exo],
        "L. plantarum (%)": [lacto],
        "Score": [score]
    })

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("Download Formulation Report", csv_buffer.getvalue(),
                       "formulation.csv", "text/csv")


# ---------------- REFERENCES PAGE ----------------

elif page == "References":
    st.title("Scientific Reference Finder")

    query = st.text_input("Enter a metabolite, protein, or bacterial function:")

    if query:
        st.write("Extracting scientific sources...")

        # NCBI
        st.subheader("NCBI Articles")
        st.write(f"https://www.ncbi.nlm.nih.gov/search/all/?term={query.replace(' ', '+')}")

        # UniProt
        st.subheader("UniProt Protein Records")
        st.write(f"https://www.uniprot.org/uniprotkb?query={query.replace(' ', '+')}")

        # PDB
        st.subheader("Protein Data Bank Structures")
        st.write(f"https://www.rcsb.org/search?query={query.replace(' ', '+')}")


# ---------------- IN-SILICO VALIDATION ----------------

elif page == "In-Silico Validation":
    st.title("In-Silico Validation")

    st.write("This section analyzes the formulation using computational simulation.")

    # Exemple de données (tu peux remplacer par tes calculs plus tard)
    x = [0, 1, 2, 3, 4, 5]
    y = [0.5, 1.1, 1.5, 2.2, 2.7, 3.3]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, linewidth=2)
    ax.set_title("Stability Simulation")
    ax.set_xlabel("Time")
    ax.set_ylabel("Performance")

    st.pyplot(fig)


