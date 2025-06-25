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
# NOTE: "Numero contrat" is the primary key (unique identifier) for the dataframe
st.title("Tableau de bord") 
st.write("Suivi d'activité globale des labo et aide au développement")


if "uploaded_file" in st.session_state and st.session_state["uploaded_file"]: 
    
    df= st.session_state.get("df", "Not set") # already processed
    # Filter data based on 'Service' and 'Phase'
    st.write("***Filters appliqués***") 
    st.write("* Service : DRV FSI développement")
    st.write("* Phase : en gestion, archivé")
    st.write("----")

    # Add a date filter
    min_value = df["Year"].min()  
    max_value = df["Year"].max()        
    selected_range = st.slider("Année", min_value, max_value, (2021, max_value))
    
    filters=create_filters(df, # TODO: we need to pass the filtered dataframe
                           exploded_dfs=st.session_state.current_exploded_dfs, #st.session_state.current_exploded_dfs,
                           columns=["Intitule structure","Code structure"])
    print("Applied filters (bilan)  =" ,filters) # debug 

    
    [contrat_unite,
    contrat_codestructure,
    contrat_acteur,
    contrat_typeacteur]=st.session_state.current_exploded_dfs
    
    # Default filters  
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


    #-------------------------------------------------
    # Prepare data for use
    #-------------------------------------------------

    df_use = df_use[["Numero contrat", "Date Création", "Date Premier Contact", "Type projet","Intitule structure","Code structure",
                          "Acteurs::Type", "Phase", "Montant Gestion UPMC", "Date de l'action","Acteurs::Sous-type",'Financeurs::Type',
       'Financeurs::Sous-type', 'Financeurs::Classe',"Date Signature"]]
    
    df_use['Montant Gestion UPMC'] = df['Montant Gestion UPMC'].str.replace(',', '.', regex=False).astype(float)
    # Calculate duration and aumoins_1_entreprise
    df_use["duree"] = (df_use["Date Signature"] - df_use["Date Premier Contact"]).dt.days
    # if duree is none, set it to -1
    df_use["duree"] = df_use["duree"].fillna(-1)
    # make sure duree is int
    df_use["duree"] = df_use["duree"].astype(int)
    df_use["type_acteur_plot"] = df_use.apply(
        lambda x: "entreprise" if "Entreprises" in str(x["Acteurs::Type"]) else "autres", axis=1
    )
    df_use["type_acteur_plot"] = df_use.apply(
        lambda x: "Commission européenne" if "Commission européenne" in str(x["Acteurs::Sous-type"])  else x["type_acteur_plot"], axis=1
    )

    df_use["Financeurs::Sous-type"] = df_use["Financeurs::Sous-type"].str.replace("Agences", "ANR", regex=False) 



    # display table
    st.write("### Data Table")
    st.dataframe(df_use)
    st.write("----") # -----------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------#
    # ##################################### PLOTS 1 ##########################################################
    # ----------------------------------------------------------------------------------------------------------#
    
    #----------------------------------------------------------------------------
    # Montant Gestion UPMC by type_acteur_plot 
    st.write("***Somme Montants Globaux (€)***")
    df_montant_plot = df_use[df_use["Montant Gestion UPMC"] > 0]  # Filter out rows where Montant Gestion UPMC is 0 or negative
    chart_montant=plot_grouped_bar(df_montant_plot, "type_acteur_plot", "Montant Gestion UPMC", title="", xlabel=None, ylabel=None)
    st.altair_chart(chart_montant, use_container_width=True)


    #----------------------------------------------------------------------------
    # Durée by type_acteur_plot 
    st.write("***Durée (Jours)***")
    # Checkbox to filter out negative durations
    filter_negatives = st.checkbox("Filtrer les durées negatives", value=False)
    # Apply the filter if checkbox is checked
    if filter_negatives:
        filtered_df = df_use[df_use["duree"] >= 0]
        chart=plot_grouped_bar(filtered_df, "type_acteur_plot", "duree", title="", xlabel=None, ylabel=None,group_function='mean')    
    else:
        filtered_df = df_use
        chart=plot_grouped_bar(filtered_df, "type_acteur_plot", "duree", title="", xlabel=None, ylabel=None,group_function='mean')
   
    
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
    # Filter out rows where Montant Gestion UPMC is 0 or negative
    df_montant_plot = sigle_merged[sigle_merged["Montant Gestion UPMC"] > 0]

    grouped_df = df_montant_plot.groupby("soustype")["Montant Gestion UPMC"].mean().reset_index()
    grouped_df = grouped_df.sort_values(by="Montant Gestion UPMC", ascending=False)

    montant_chart_acteur_soutype = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X("soustype:N",sort="-y", title="Acteurs::Sous-type"),
        y=alt.Y("Montant Gestion UPMC:Q", title="Montant Gestion SU (€)"),
        color=alt.Color("soustype:N", legend=None),  # 👈 remove legend,
        tooltip=["soustype:N", "Montant Gestion UPMC:Q"]
    ).properties(
        title="Montant Gestion SU moyen"
    )
    
    # ----------------------------------------------------
    # montant by Financeurs::Sous-type
    x_axis_col = "Financeurs::Sous-type"
    y_axis_col = "Montant Gestion UPMC"
    sigle=separate(df_use,column_to_explode = x_axis_col)
    sigle_merged=sigle.merge(df_use, left_on="Numero contrat", right_on="Numero contrat", how="left")
    sigle_merged = sigle_merged.rename(columns={f"{x_axis_col}_x": 'x_axis_col'})
    
    # Filter out rows where Montant Gestion UPMC is 0 or negative
    df_montant_plot = sigle_merged[sigle_merged["Montant Gestion UPMC"] > 0]

    grouped_df = df_montant_plot.groupby("x_axis_col")[y_axis_col].sum().reset_index()
    grouped_df = grouped_df.sort_values(by=y_axis_col, ascending=False)

    montant_chart_financeur_soutype = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X("x_axis_col:N",sort="-y", title=x_axis_col),
        y=alt.Y(f"{y_axis_col}:Q", title="Montant Gestion SU (€)"),
        color=alt.Color("x_axis_col:N", legend=None),  # 👈 remove legend,
        tooltip=["x_axis_col:N", "Montant Gestion UPMC:Q"]
    ).properties(
        title="Montant Gestion SU "
    )

    # Display the charts
    st.write("***Pour la somme Montant Gestion SU , Les contrats sans montant spécifié ne sont pas pris en compte ! .***")

    tab1,= st.tabs(["Financeur soustype"])
    with tab1:
        st.altair_chart(montant_chart_financeur_soutype, use_container_width=True)
        #st.altair_chart(chart_stacked, use_container_width=True) 
else:
    st.write("***Merci de télécharger un fichier dans la page Dashbord ! .***")







