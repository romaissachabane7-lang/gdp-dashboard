import streamlit as st
import pandas as pd
from io import StringIO

# Navigation entre les pages
page = st.sidebar.radio("Navigation", ["Accueil", "Formulation", "Références", "Validation"])

if page == "Accueil":
    st.title("Accueil")
    st.write("Bienvenue sur la BioPlateforme Algérienne")
elif page == "Formulation":
    st.title("Formulation")
    
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
elif page == "Références":
    st.title("Références")
    st.write("Liste des références scientifiques")
elif page == "Validation":
    st.title("Validation")
    st.write("Section validation")
import streamlit as st
import pandas as pd
from io import StringIO
streamlit==1.29.0
pandas==2.1.0




