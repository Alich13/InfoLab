import pandas as pd
import streamlit as st

import altair as alt
from aux import *

import matplotlib.pyplot as plt

st.header("Bilan d'activité")
"""
Outil de bilan de l’activité plus générale
NB : pour le traitement "bilan" se concentrait que sur les dossiers en phase « en gestion » et « archivé »
"""

st.title("Tableau de bord") 
st.write("Suivi d'activité globale des labo et aide au développement")

uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])
st.write("----")

# NOTE: "Numero contrat" is the primary key (unique identifier) for the dataframe

# Initialize session state if not set
if "possible_key_dict" not in st.session_state:
    st.session_state.possible_key_dict = {}


if uploaded_file or True: # For testing purposes, set uploaded_file to True
    
    df=read_excel("/Users/alichemkhi/Desktop/myProjects/InfoLab/datasym/extraction_contrats.xlsx")#(uploaded_file)

    preprocess(df)

    # Filter data based on 'Service' and 'Phase'
    df_filtered = df[(df["Service"] == "DRV FSI développement") & 
                     (df["Phase"].isin(["en gestion", "archivé"]))]

    # Prepare data for use
    df_use = df_filtered[["Numero contrat", "Date Création", "Date Premier Contact", 
                          "Acteurs::Type", "Phase", "Montant Global", "Date de l'action","Acteurs::Sigle"]]
    
    # Calculate duration and aumoins_1_entreprise
    df_use["duree"] = (df_use["Date de l'action"] - df_use["Date Premier Contact"]).dt.days
    df_use["aumoins_1_entreprise"] = df_use["Acteurs::Type"].str.contains("Entreprises", na=False)

    # print table
    st.write("### Data Table")
    st.dataframe(df_use)


    # Filter out rows where Montant Global is 0 or negative
    df_montant_plot = df_use[df_use["Montant Global"] > 0]

    # --- Montant Global by aumoins_1_entreprise ---
    st.write("### Montant Global by aumoins_1_entreprise")
    montant_chart = alt.Chart(df_use.groupby("aumoins_1_entreprise")["Montant Global"].mean().reset_index()).mark_bar().encode(
        x=alt.X("aumoins_1_entreprise:N", title="aumoins_1_entreprise"),
        y=alt.Y("Montant Global:Q", title="Montant Global (€)"),
        color="aumoins_1_entreprise:N",
        tooltip=["aumoins_1_entreprise:N", "Montant Global:Q"]
    ).properties(
        title="Montant Global by aumoins_1_entreprise"
    )
    
    st.altair_chart(montant_chart, use_container_width=True)


    # --- Durée by aumoins_1_entreprise ---
    st.write("### Durée by aumoins_1_entreprise")
    duree_chart = alt.Chart(df_use.groupby("aumoins_1_entreprise")["duree"].mean().reset_index()).mark_bar().encode(
        x=alt.X("aumoins_1_entreprise:N", title="aumoins_1_entreprise"),
        y=alt.Y("duree:Q", title="Durée (days)"),
        color="aumoins_1_entreprise:N",
        tooltip=["aumoins_1_entreprise:N", "duree:Q"]
    ).properties(
        title="Durée by aumoins_1_entreprise"
    )

    st.altair_chart(duree_chart, use_container_width=True)



     # --- montant by sigle ---
    sigle=separate(df_use,column_to_explode = 'Acteurs::Sigle')
    sigle_merged=sigle.merge(df_use, left_on="Acteurs::Sigle", right_on="Acteurs::Sigle", how="left")
    sigle_merged = sigle_merged.rename(columns={'Acteurs::Sigle': 'Sigle'})
    # Filter out rows where Montant Global is 0 or negative
    df_montant_plot = sigle_merged[sigle_merged["Montant Global"] > 0]

    # --- Montant Global by aumoins_1_entreprise ---
    # TODO add a top k param
    st.write("### Montant Global by aumoins_1_entreprise")
    grouped_df = df_montant_plot.groupby("Sigle")["Montant Global"].mean().reset_index()
    print(grouped_df)
    grouped_df = grouped_df.sort_values(by="Montant Global", ascending=False)[0:20]
    print(grouped_df)
    montant_chart = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X("Sigle:N",sort="-y", title="Acteurs::Sigle"),
        y=alt.Y("Montant Global:Q", title="Montant Global (€)"),
        color="Sigle:N",
        tooltip=["Sigle:N", "Montant Global:Q"]
    ).properties(
        title="Top 20 sigle par montant global moyen"
    )
    
    st.altair_chart(montant_chart, use_container_width=True)



