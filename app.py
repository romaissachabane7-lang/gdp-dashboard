import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# GLOBAL PAGE CONFIGURATION
# ==============================
st.set_page_config(
    page_title="BIOPLATFORM – Synbiotic Development",
    layout="wide",
    page_icon="🧬"
)

# ==============================
# CUSTOM CSS FOR PREMIUM STYLE
# ==============================
st.markdown(
    """
    <style>
        /* Global font */
        html, body, [class*="css"] {
            font-family: "Times New Roman", serif !important;
        }

        /* Title */
        .title-text {
            font-size: 42px;
            font-weight: bold;
            color: #4A4A4A;
            text-align: center;
            margin-top: -30px;
        }

        /* Subtitle */
        .subtitle-text {
            font-size: 22px;
            color: #6A6A6A;
            text-align: center;
            margin-bottom: 20px;
        }

        /* Section titles */
        .section-title {
            font-size: 28px;
            font-weight: bold;
            color: #444;
            margin-top: 30px;
        }

        /* Paragraph */
        .paragraph {
            font-size: 18px;
            color: #333;
            line-height: 1.6;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# SIDEBAR MENU
# ==============================
page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Formulation", "Validation", "References"]
)

# ==============================
# PAGE 1 – HOME
# ==============================
if page == "Home":
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image("assets/logo.png", use_container_width=True)

    st.markdown('<div class="title-text">BIOPLATFORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">Advanced Synbiotic Engineering Platform</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <p class="paragraph">
        Welcome to <b>BIOPLATFORM</b>, a professional environment dedicated to developing
        next-generation synbiotics based on locally isolated <i>Lactobacillus plantarum</i>.
        This platform integrates scientific formulation, predictive validation models, and
        structured documentation for high-quality product development in the animal nutrition sector.
        </p>

        <p class="paragraph">
        The synbiotic developed here combines:
        <ul class="paragraph">
            <li>Probiotic activity</li>
            <li>Prebiotic support</li>
            <li>Anti-heat stress protection</li>
            <li>Natural bio-preservation capability</li>
            <li>Texture and viscosity stabilization</li>
        </ul>
        </p>
        """,
        unsafe_allow_html=True
    )

# ==============================
# PAGE 2 – FORMULATION
# ==============================
if page == "Formulation":
    st.markdown('<div class="section-title">Synbiotic Formulation</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <p class="paragraph">
        This section allows you to configure and review the formulation parameters used during
        the development of the synbiotic product.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.text_input("Probiotic Strain", "Lactobacillus plantarum (Honey isolate)")
    st.text_input("Prebiotic Component", "Inulin / Honey-derived oligosaccharides")
    st.text_input("Functional Additives", "Antioxidants, stabilizing polysaccharides")

# ==============================
# PAGE 3 – VALIDATION
# ==============================
if page == "Validation":
    st.markdown('<div class="section-title">Experimental Validation</div>', unsafe_allow_html=True)

    st.markdown(
        "<p class='paragraph'>Graphical validation of microbial stability, growth and performance.</p>",
        unsafe_allow_html=True
    )

    # Example demo data
    df = pd.DataFrame({
        "Time (h)": [0, 12, 24, 36, 48, 60],
        "Bacterial Growth (CFU/mL)": [1e6, 5e6, 2e7, 5e7, 8e7, 1e8]
    })

    # Medium-size, clean graph
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["Time (h)"], df["Bacterial Growth (CFU/mL)"])
    ax.set_xlabel("Time (hours)", fontfamily="Times New Roman")
    ax.set_ylabel("Growth (CFU/mL)", fontfamily="Times New Roman")
    ax.set_title("Growth Curve", fontfamily="Times New Roman")
    st.pyplot(fig)

# ==============================
# PAGE 4 – REFERENCES
# ==============================
if page == "References":

    st.markdown('<div class="section-title">Scientific References</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <p class="paragraph">
        Below are organized scientific references relevant to synbiotic design,
        <i>Lactobacillus plantarum</i> characterization, and microbial validation methods.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        **Reference 1**  
        National Center for Biotechnology Information (NCBI).  
        Genomic and taxonomic information on *Lactobacillus plantarum*.

        **Reference 2**  
        UniProt Consortium.  
        Protein sequences and functional annotations for *L. plantarum*.

        **Reference 3**  
        Protein Data Bank (PDB).  
        Structural information related to bacterial metabolic proteins.

        **Reference 4**  
        Review literature on synbiotic efficiency, probiotic stability, and prebiotic synergy.
        """
    )




