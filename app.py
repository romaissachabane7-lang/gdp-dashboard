{html.escape(source)} {html.escape(pubdate)}" if source or pubdate else ""
                    st.markdown(display + extra, unsafe_allow_html=True)
            else:
                st.info("Aucun article PubMed trouvé pour ce terme.")
        except Exception as e:
            st.error("Recherche PubMed impossible (vérifiez la connexion).")

        # UniProt
        st.markdown("### UniProt — Top hits")
        try:
            uq = "https://rest.uniprot.org/uniprotkb/search"
            params = {"query": terme, "format": "json", "size": 6}
            r2 = requests.get(uq, params=params, timeout=10)
            r2.raise_for_status()
            data = r2.json()
            hits = data.get("results", [])
            if hits:
                for entry in hits:
                    acc = entry.get("primaryAccession")
                    prot_desc = entry.get("proteinDescription", {})
                    rec_name = prot_desc.get("recommendedName", {}).get("fullName", {}).get("value", "") if prot_desc else ""
                    display_label = rec_name or acc
                    uniprot_url = f"https://rest.uniprot.org/uniprotkb/{acc}"
                    st.markdown(f"- <a href='{uniprot_url}' target='_blank' style='color:#0A84FF;text-decoration:none'><b>{html.escape(display_label)}</b></a> — Accession: `{acc}`", unsafe_allow_html=True)
            else:
                st.info("Aucun hit UniProt retourné.")
        except Exception as e:
            st.error("Recherche UniProt impossible (temps de réponse ou réseau).")

        # PDB
        st.markdown("### PDB / RCSB")
        try:
            query_encoded = urllib.parse.quote_plus(terme)
            rcsb_link = f"https://www.rcsb.org/search?request={{\"query\":\"{query_encoded}\"}}"
            st.markdown(f"- Effectuer une recherche sur RCSB PDB : <a href='{rcsb_link}' target='_blank' style='color:#0A84FF;text-decoration:none'>Ouvrir RCSB</a>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:6px' class='muted'>Astuce : utilisez l'accession UniProt (si trouvée ci-dessus) pour retrouver des structures corrélées.</div>", unsafe_allow_html=True)
        except Exception:
            st.info("Impossible de générer le lien RCSB.")

# -------------------------
#  PAGE : VALIDATION
# -------------------------
elif page == "Validation":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation in silico</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Visualisation et score de stabilité</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    df = pd.DataFrame({
        "Composant":["Miel","PLA","EPS","Lactobacillus"],
        "Contribution":[40,1,2,1]
    })
    st.bar_chart(df.set_index("Composant"))


