# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# -----------------------
# Configuration de la page
# -----------------------
st.set_page_config(
    page_title="BioPlateforme Algérienne",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# Navigation
# -----------------------
page = st.sidebar.radio("Navigation", ["Accueil", "Formulation", "Références", "Validation"])

# =======================
# PAGE ACCUEIL
# =======================
if page == "Accueil":
    st.title("🧪 BioPlateforme Algérienne")
    st.markdown("""
    Bienvenue sur la plateforme scientifique automatisée.
    
    Cette plateforme permet :
    - La formulation de produits
    - La génération automatique de scores
    - La validation e-SILICO avec graphiques
    - L’accès aux références NCBI, PubMed et PDB
    """)

# =======================
# PAGE FORMULATION
# =======================
elif page == "Formulation":
    st.title("Formulation du produit")

    # Inputs utilisateur avec clés uniques
    nom = st.text_input("Nom du chercheur", "VotreNom", key="nom_formulation")
    miel = st.number_input("Miel (%)", 0, 100, 100, key="miel_formulation")
    acide = st.number_input("Acide phényllactique (%)", 0, 100, 10, key="acide_formulation")
    exopolysaccharides = st.number_input("Exopolysaccharides (%)", 0, 100, 10, key="exopolys_formulation")
    lacto = st.number_input("Lactobacillus plantarum (%)", 0, 100, 5, key="lacto_formulation")

    # Calcul du score
    score = round((miel*0.1 + acide*0.2 + exopolysaccharides*0.3 + lacto*0.4), 2)
    st.success(f"Formulation validée — score: {score}")

    # Création du DataFrame
    df = pd.DataFrame({
        "Nom du chercheur": [nom],
        "Miel (%)": [miel],
        "Acide phényllactique (%)": [acide],
        "Exopolysaccharides (%)": [exopolysaccharides],
        "Lactobacillus plantarum (%)": [lacto],
        "Score": [score]
    })

    # Générer CSV en mémoire pour téléchargement
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="Télécharger le rapport",
        data=csv_data,
        file_name="formulation.csv",
        mime="text/csv",
        key="download_formulation"
    )

# =======================
# PAGE REFERENCES
# =======================
elif page == "Références":
    st.title("Références scientifiques")

    # Exemple : tableau automatique des références
    refs_data = {
        "Source": ["NCBI", "PubMed", "PDB"],
        "Lien": [
            "https://www.ncbi.nlm.nih.gov",
            "https://pubmed.ncbi.nlm.nih.gov",
            "https://www.rcsb.org"
        ],
        "Description": [
            "Base de données génétiques et biologiques",
            "Articles scientifiques biomédicaux",
            "Structures 3D de protéines et macromolécules"
        ]
    }

    refs_df = pd.DataFrame(refs_data)
    st.dataframe(refs_df, use_container_width=True)

    # Liens cliquables
    for i in range(len(refs_df)):
        st.markdown(f"[{refs_df['Source'][i]}]({refs_df['Lien'][i]}) : {refs_df['Description'][i]}")

# =======================
# PAGE VALIDATION IN SILICO
# =======================
elif page == "Validation":
    st.title("Validation e-SILICO")

    st.markdown("Validation automatique et visualisation graphique des formulations")

    # Exemple graphique interactif
    # Ici on simule des valeurs pour montrer les performances
    validation_df = pd.DataFrame({
        "Paramètre": ["Miel", "Acide", "Exopolysaccharides", "Lactobacillus plantarum"],
        "Valeur (%)": [100, 10, 10, 5],
        "Score contribution": [miel*0.1, acide*0.2, exopolysaccharides*0.3, lacto*0.4]
    })

    st.dataframe(validation_df, use_container_width=True)

    fig = px.bar(
        validation_df,
        x="Paramètre",
        y="Score contribution",
        text="Score contribution",
        title="Contribution des composants au score total",
        labels={"Score contribution":"Contribution au score"}
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_color="teal")
    fig.update_layout(yaxis=dict(range=[0, max(validation_df["Score contribution"])*1.2]))
    st.plotly_chart(fig, use_container_width=True)





