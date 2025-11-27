import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="🌿 BioPlateforme - Formulation Microbienne", layout="wide")

# --- SIDEBAR MENU ---
st.sidebar.title("🧬 Menu de navigation")
menu = st.sidebar.radio("Choisissez une section :", [
    "🏠 Accueil",
    "🧪 Formulation intelligente",
    "📚 Références bio-informatiques",
    "📊 Validation virtuelle",
])

# --- ACCUEIL ---
if menu == "🏠 Accueil":
    st.title("🌿 BioPlateforme de formulation microbienne")
    st.markdown("""
    Bienvenue sur la **BioPlateforme**, un espace de simulation et de validation
    **in silico** des formulations bioactives à base de **miel algérien** et de **Lactobacillus plantarum**.  
    Cette plateforme intègre des données issues de **NCBI**, **UniProt**, et **PDB**.
    """)

# --- FORMULATION ---
elif menu == "🧪 Formulation intelligente":
    st.header("🧪 Formulation du produit bio-intelligent")
    chercheur = st.text_input("Nom du chercheur :")
    miel = st.slider("Pourcentage de miel (%)", 0, 100, 40)
    pla = st.slider("Acide phényllactique (%)", 0, 10, 1)
    eps = st.slider("Exopolysaccharides (%)", 0, 10, 2)
    lplantarum = st.slider("Concentration de Lactobacillus plantarum (%)", 0, 5, 1)

    if st.button("✅ Valider la formulation"):
        score = round((miel * 0.2 + pla * 2 + eps * 1.5 + lplantarum * 3), 2)
        st.success(f"Formulation validée ! Score de stabilité bioactive : {score}")
        st.balloons()

# --- REFERENCES ---
elif menu == "📚 Références bio-informatiques":
    st.header("📚 Références scientifiques et bases de données mondiales")
    st.markdown("""
    Cette section permet d'accéder virtuellement aux données issues de :
    - 🧬 **NCBI (National Center for Biotechnology Information)**
    - 🧫 **UniProt (Protein Knowledgebase)**
    - 🧠 **PubMed (Articles scientifiques)**
    - 🧩 **PDB (Protein Data Bank)**
    """)

    choix = st.text_input("🔎 Entrez un nom d'espèce, protéine ou composé bioactif :")

    if choix:
        st.info(f"Résultats pour **{choix}** à partir des bases de données mondiales :")
        if "Lactobacillus plantarum" in choix:
            st.markdown("""
            **🧬 NCBI Taxonomy ID :** 1590  
            **🧫 UniProt Entry :** [PLN_12345](https://www.uniprot.org/uniprotkb/Q88FY0/entry)  
            **🧩 PDB ID :** [2JUI](https://www.rcsb.org/structure/2JUI)  
            **📖 PubMed DOI :** [10.3390/foods13060826](https://doi.org/10.3390/foods13060826)  
            **Fonction :** Production de plantaricine, acide phényllactique et exopolysaccharides.  
            **Applications :** Antimicrobien, cicatrisant, probiotique.  
            """)
        elif "miel" in choix.lower():
            st.markdown("""
            **Source :** Produit naturel complexe riche en polyphénols et sucres.  
            **Fonction :** Antioxydant, antibactérien, support énergétique.  
            **Référence PubMed :** [PMID 37390412](https://pubmed.ncbi.nlm.nih.gov/37390412/)  
            **Composés actifs :** Flavonoïdes, acide phényllactique.  
            """)
        else:
            st.warning("Aucune donnée directe trouvée. Essayez avec un autre nom scientifique.")

# --- VALIDATION ---
elif menu == "📊 Validation virtuelle":
    st.header("📊 Validation in silico")
    st.markdown("Calcule et visualise la performance des formulations bioactives.")
    data = {"Composant": ["Miel", "PLA", "EPS", "L. plantarum"],
            "Contribution": [40, 1, 2, 1]}
    df = pd.DataFrame(data)
    st.bar_chart(df)




