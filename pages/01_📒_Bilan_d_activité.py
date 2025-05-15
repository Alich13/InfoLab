import pandas as pd
import streamlit as st

import altair as alt
from aux1 import *

import matplotlib.pyplot as plt

st.header("Bilan d'activité")
"""
Outil de bilan d'activité générale \n
Pour les analyses ci-dessous on a uniquement les contrats « en gestion » et « archivé »
"""

st.title("Tableau de bord") 
st.write("Suivi d'activité globale des labo et aide au développement")

# NOTE: "Numero contrat" is the primary key (unique identifier) for the dataframe



if "uploaded_file" in st.session_state and st.session_state["uploaded_file"]: # For testing purposes, set uploaded_file to True
    
    df= st.session_state.get("df", "Not set") # already processed
    # Filter data based on 'Service' and 'Phase'
    st.write("***Filters appliqués***") 
    st.write("* Service : DRV FSI développement")
    st.write("* Phase : en gestion, archivé")
    st.write("----")

    # add a date filter
    min_value = df["Year"].min()  
    max_value = df["Year"].max()        
    selected_range = st.slider("Année", min_value, max_value, (2021, max_value))
    
    filters=create_filters(df, # TODO: we need to pass the filtered dataframe
                           exploded_dfs=st.session_state.current_exploded_dfs, #st.session_state.current_exploded_dfs,
                           columns=["Intitule structure","Code structure"])
    print("Applied filters - bilan  =" ,filters)

    
    [contrat_unite,
    contrat_codestructure,
    contrat_acteur,
    contrat_typeacteur]=st.session_state.current_exploded_dfs
    
    # Filter 
    df_use = df[(df["Service"] == "DRV FSI développement") & 
                     (df["Phase"].isin(["en gestion", "archivé"]))  & (df["Year"] >= selected_range[0] ) & (df["Year"] <= selected_range[1] ) ].copy()

    for column, filter_value in filters.items():

        if column == "Intitule structure":
            filtered_items = contrat_unite[contrat_unite[column].isin(filter_value)]
            contracts_to_keep = filtered_items["Numero contrat"].unique()
            df_use = df_use[df_use["Numero contrat"].isin(filtered_items["Numero contrat"])]
        elif column == "Code structure":
            filtered_items = contrat_codestructure[contrat_codestructure[column].isin(filter_value)]
            contracts_to_keep = filtered_items["Numero contrat"].unique()
            df_use = df_use[df_use["Numero contrat"].isin(filtered_items["Numero contrat"])]
        else :    
            raise KeyError(" something wrong ")





    # Prepare data for use
    df_use = df_use[["Numero contrat", "Date Création", "Date Premier Contact", "Type projet","Intitule structure","Code structure",
                          "Acteurs::Type", "Phase", "Montant Global", "Date de l'action","Acteurs::Sous-type",'Financeurs::Type',
       'Financeurs::Sous-type', 'Financeurs::Classe',"Date Signature"]]
    
    # Calculate duration and aumoins_1_entreprise
    df_use["duree"] = (df_use["Date Signature"] - df_use["Date Premier Contact"]).dt.days
    # if duree is none, set it to -1
    df_use["duree"] = df_use["duree"].fillna(-1)
    # make sure duree is int
    df_use["duree"] = df_use["duree"].astype(int)
    df_use["aumoins_1_entreprise"] = df_use["Acteurs::Type"].str.contains("Entreprises", na=False)
    df_use["aumoins_1_entreprise"] = df_use["aumoins_1_entreprise"].replace({True: "Au moins 1 entreprise", False: "Pas d'entreprise"})

    # display table
    st.write("### Data Table")
    st.dataframe(df_use)
    st.write("----") # -----------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------#
    # ##################################### PLOTS 1 ##########################################################
    # ----------------------------------------------------------------------------------------------------------#
    
    #----------------------------------------------------------------------------
    # Montant Global by aumoins_1_entreprise 
    st.write("***Montant Global (€)***")
    df_montant_plot = df_use[df_use["Montant Global"] > 0]  # Filter out rows where Montant Global is 0 or negative
    chart_montant=plot_grouped_bar(df_montant_plot, "aumoins_1_entreprise", "Montant Global", title="", xlabel=None, ylabel=None)
    st.altair_chart(chart_montant, use_container_width=True)


    #----------------------------------------------------------------------------
    # Durée by aumoins_1_entreprise 
    st.write("***Durée (Jours)***")
    # Checkbox to filter out negative durations
    filter_negatives = st.checkbox("Filtrer les durées negatives", value=False)
    # Apply the filter if checkbox is checked
    if filter_negatives:
        filtered_df = df_use[df_use["duree"] >= 0]
        chart=plot_grouped_bar(filtered_df, "aumoins_1_entreprise", "duree", title="", xlabel=None, ylabel=None)    
    else:
        filtered_df = df_use
        chart=plot_grouped_bar(filtered_df, "aumoins_1_entreprise", "duree", title="", xlabel=None, ylabel=None)
   
    
    tab1, tab2 = st.tabs(["📊 Bar Chart", "📋 Source Data"])
    with tab1:
        st.altair_chart(chart, use_container_width=True)
    with tab2:
        st.write("## Source de données ")
        st.dataframe(filtered_df)  # Display the table
    
    
   
    st.write("---") #-----------------------------------------------------



    # ----------------------------------------------------------------------------------------------------------#
    # montant by Acteurs::Sous-type 

    sigle=separate(df_use,column_to_explode = 'Acteurs::Sous-type')
    sigle_merged=sigle.merge(df_use, left_on="Numero contrat", right_on="Numero contrat", how="left")
    sigle_merged = sigle_merged.rename(columns={'Acteurs::Sous-type_x': 'soustype'})
    # Filter out rows where Montant Global is 0 or negative
    df_montant_plot = sigle_merged[sigle_merged["Montant Global"] > 0]

    grouped_df = df_montant_plot.groupby("soustype")["Montant Global"].mean().reset_index()
    grouped_df = grouped_df.sort_values(by="Montant Global", ascending=False)

    montant_chart_acteur_soutype = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X("soustype:N",sort="-y", title="Acteurs::Sous-type"),
        y=alt.Y("Montant Global:Q", title="Montant Global (€)"),
        color=alt.Color("soustype:N", legend=None),  # 👈 remove legend,
        tooltip=["soustype:N", "Montant Global:Q"]
    ).properties(
        title="montant global moyen"
    )
    
    # ----------------------------------------------------
    # montant by Financeurs::Sous-type
    x_axis_col = "Financeurs::Sous-type"
    y_axis_col = "Montant Global"
    sigle=separate(df_use,column_to_explode = x_axis_col)
    sigle_merged=sigle.merge(df_use, left_on="Numero contrat", right_on="Numero contrat", how="left")
    sigle_merged = sigle_merged.rename(columns={f"{x_axis_col}_x": 'x_axis_col'})
    
    # Filter out rows where Montant Global is 0 or negative
    df_montant_plot = sigle_merged[sigle_merged["Montant Global"] > 0]

    grouped_df = df_montant_plot.groupby("x_axis_col")[y_axis_col].mean().reset_index()
    grouped_df = grouped_df.sort_values(by=y_axis_col, ascending=False)

    montant_chart_financeur_soutype = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X("x_axis_col:N",sort="-y", title=x_axis_col),
        y=alt.Y(f"{y_axis_col}:Q", title="Montant Global (€)"),
        color=alt.Color("x_axis_col:N", legend=None),  # 👈 remove legend,
        tooltip=["x_axis_col:N", "Montant Global:Q"]
    ).properties(
        title="montant global moyen"
    )

    # stacked bar chart - too complicated and not informative - comment it for now
    # chart_stacked=stacked_plot_grouped_bar(sigle_merged,  "aumoins_1_entreprise", "soustype", "duree", title=" Durée moyenne par type de financeur ", xlabel=None, ylabel=None)


    # Display the charts
    st.write("***Pour la moyenne montant global , Les contrats sans montant spécifié ne sont pas pris en compte ! .***")

    tab1, tab2 = st.tabs(["Financeur soustype", "Acteur soustype"])
    with tab1:
        st.altair_chart(montant_chart_financeur_soutype, use_container_width=True)
        #st.altair_chart(chart_stacked, use_container_width=True) 

    with tab2:
        st.altair_chart(montant_chart_acteur_soutype, use_container_width=True)

else:

    st.write("***Merci de télécharger un fichier dans la page Dashbord ! .***")
    st.write("----")


    
    






