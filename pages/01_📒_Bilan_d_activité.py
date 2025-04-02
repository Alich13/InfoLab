import pandas as pd
import streamlit as st
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
                          "Acteurs::Type", "Phase", "Montant Global", "Date de l'action"]]
    
    # Calculate duration and aumoins_1_entreprise
    df_use["duree"] = df_use["Date de l'action"] - df_use["Date Premier Contact"]
    df_use["aumoins_1_entreprise"] = df_use["Acteurs::Type"].str.contains("Entreprises", na=False)

    # print table
    st.write("### Data Table")
    st.dataframe(df_use)


    # Filter out rows where Montant Global is 0 or negative
    df_use = df_use[df_use["Montant Global"] > 0]

    # --- Montant Global by aumoins_1_entreprise ---
    st.write("### Montant Global by aumoins_1_entreprise")
    fig, ax = plt.subplots()
    df_use.groupby("aumoins_1_entreprise")["Montant Global"].mean().plot(kind="bar", ax=ax)
    plt.title("Montant Global ")
    plt.xlabel("aumoins une entreprise")
    plt.ylabel("Montant Global")
    st.pyplot(fig)

    # Print average Montant Global for `aumoins_1_entreprise == False`
    mean_montant = df_use[df_use["aumoins_1_entreprise"] == False]["Montant Global"].mean()
    st.write(f"Average Montant Global for non-entreprises: {mean_montant}")

    # --- Durée by aumoins_1_entreprise ---
    st.write("### Durée ")
    fig2, ax2 = plt.subplots()
    df_use.groupby("aumoins_1_entreprise")["duree"].mean().plot(kind="bar", ax=ax2)
    plt.title("Durée by aumoins_1_entreprise")
    plt.xlabel("aumoins une entreprise")
    plt.ylabel("Durée")
    st.pyplot(fig2)

    # Print average Durée for `aumoins_1_entreprise == False`
    mean_duree = df_use[df_use["aumoins_1_entreprise"] == False]["duree"].mean()
    st.write(f"Average Durée for non-entreprises: {mean_duree}")