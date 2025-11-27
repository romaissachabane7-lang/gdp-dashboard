"""
Prototype Bioplatforme avec interface Streamlit + simulation sensorielle
-----------------------------------------------------------------------
- Formulation dynamique avec validation
- Visualisation des lectures capteurs (Flask)
- Références PubMed / UniProt / PDB avec cache pour fluidité
- Score calculé automatiquement
- CSV sauvegarde
"""

import streamlit as st
import pandas as pd
import requests
import html
import os
import urllib.parse
from flask import Flask, jsonify, request, render_template_string, send_file
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import threading
import csv
import io
import random

# ------------------- Streamlit CONFIG -------------------
st.set_page_config(page_title="BioPlateforme Algérienne", layout="wide")

# -- CSS et logo --
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

st.markdown("""
<style>
.stApp { background-color: #fbf7ee; }
.card { background-color: #fffaf0; border-radius: 10px; padding: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin-bottom: 18px;}
.section-title { color:#4a3f2a; font-weight:700; font-size:20px; margin-bottom:10px; }
.muted { color:#7a6b5a; font-size:13px; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Accueil", "Formulation", "Références", "Validation"], index=0)

# ------------------ PAGE: Accueil ------------------
if page == "Accueil":
    st.markdown(svg_logo, unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="section-title">Bienvenue</div><div class="muted">Plateforme algérienne de simulation, validation et exploration scientifique des formulations biotechnologiques — miel, métabolites, probiotiques.</div></div>', unsafe_allow_html=True)

# ------------------ PAGE: Formulation ------------------
elif page == "Formulation":
    st.markdown('<div class="card"><div class="section-title">Formulation</div><div class="muted">Saisissez les paramètres et validez pour générer un rapport.</div></div>', unsafe_allow_html=True)

    chercheur = st.text_input("Nom du chercheur")
    miel = st.slider("Miel (%)", 0, 100, 40)
    pla = st.slider("Acide phényllactique (%)", 0, 10, 1)
    eps = st.slider("Exopolysaccharides (%)", 0, 10, 2)
    lacto = st.slider("Lactobacillus plantarum (%)", 0, 5, 1)

    if st.button("Valider la formulation"):
        score = round((miel * 0.2 + pla * 2 + eps * 1.5 + lacto * 3), 2)
        st.session_state.last_formulation = {"chercheur": chercheur, "miel": miel, "pla": pla, "eps": eps, "lacto": lacto, "score": score}

        os.makedirs("resultats", exist_ok=True)
        df = pd.DataFrame([st.session_state.last_formulation])
        safe_name = (chercheur or "anonyme").strip().replace(" ", "_").replace("/", "_")
        path = f"resultats/formulation_{safe_name}.csv"
        df.to_csv(path, index=False)
        st.success(f"Formulation validée — score: {score}")
        st.info(f"Rapport sauvegardé: {path}")

# ------------------ PAGE: Références ------------------
elif page == "Références":
    st.markdown('<div class="card"><div class="section-title">Références scientifiques</div><div class="muted">Recherche intégrée : PubMed + UniProt + PDB</div></div>', unsafe_allow_html=True)
    terme = st.text_input("Rechercher (ex: Lactobacillus plantarum OR phenyllactic acid OR plantaricin)")
    st.caption("Exemples : phenyllactic acid, plantaricin, Lactobacillus plantarum metabolite")

    @st.cache_data
    def cached_pubmed(query):
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        r = requests.get(url, params={"db":"pubmed","term":query,"retmax":5,"retmode":"json"}, timeout=10)
        return r.json()

    @st.cache_data
    def cached_uniprot(query):
        url = "https://rest.uniprot.org/uniprotkb/search"
        r = requests.get(url, params={"query":query,"format":"json","size":5}, timeout=10)
        return r.json()

    if terme:
        st.markdown(f"**Résultats pour :** {html.escape(terme)}")

        # PubMed
        try:
            ids = cached_pubmed(terme).get("esearchresult", {}).get("idlist", [])
            if ids:
                summaries = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", params={"db":"pubmed","id":",".join(ids),"retmode":"json"}, timeout=10).json().get("result", {})
                for pid in ids:
                    info = summaries.get(pid,{})
                    title = info.get("title") or f"PubMed {pid}"
                    pubdate = info.get("pubdate","")
                    st.markdown(f"- [{html.escape(title)}](https://pubmed.ncbi.nlm.nih.gov/{pid}/) — {pubdate}")
            else: st.info("Aucun article PubMed trouvé.")
        except: st.error("Recherche PubMed impossible.")

        # UniProt
        try:
            hits = cached_uniprot(terme).get("results", [])
            if hits:
                for entry in hits:
                    acc = entry.get("primaryAccession")
                    prot_desc = entry.get("proteinDescription", {})
                    rec_name = prot_desc.get("recommendedName",{}).get("fullName",{}).get("value","") if prot_desc else ""
                    if not rec_name:
                        alt = prot_desc.get("alternativeNames",[])
                        if alt: rec_name = alt[0].get("fullName",{}).get("value","")
                    display_label = rec_name or acc
                    st.markdown(f"- [{display_label}](https://rest.uniprot.org/uniprotkb/{acc}) — UniProt Accession: `{acc}`")
            else: st.info("Aucun hit UniProt.")
        except: st.error("Recherche UniProt impossible.")

        # PDB
        try:
            query_encoded = urllib.parse.quote_plus(terme)
            rcsb_link = f"https://www.rcsb.org/search?request={{\"query\":\"{query_encoded}\"}}"
            st.markdown(f"- [RCSB search]({rcsb_link})")
        except: st.info("Impossible de générer le lien RCSB.")

# ------------------ PAGE: Validation ------------------
elif page == "Validation":
    st.markdown('<div class="card"><div class="section-title">Validation in silico</div><div class="muted">Visualisation et score de stabilité</div></div>', unsafe_allow_html=True)

    if "last_formulation" not in st.session_state:
        st.warning("Aucune formulation validée. Va d'abord dans la page Formulation.")
    else:
        data = st.session_state.last_formulation
        df = pd.DataFrame({"Composant":["Miel","PLA","EPS","Lactobacillus"],"Contribution":[data["miel"],data["pla"],data["eps"],data["lacto"]]})
        st.bar_chart(df.set_index("Composant"))
        st.success(f"Score final calculé : {data['score']}")






