import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.styles.stylesheet")
from aux1 import *


"""
[emoji]: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
"""

# TODO: 
# check if the column names are in the dataframe
# streamlit run 📊_Dashbord.py

st.title("Tableau de bord") 
st.write("Suivi d'activité globale des labo et aide au développement")


uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])
st.write("----")


if uploaded_file or ("uploaded_file" in st.session_state and st.session_state["uploaded_file"]) : 
    
    # Clear cache if a new file is uploaded
    clear_cache_on_new_upload(uploaded_file)

    if "df" not in st.session_state:
        df=read_excel(uploaded_file)#(uploaded_file)
        preprocess(df) 
        st.session_state.df=df
        st.session_state.current_df_filtered = st.session_state.df
        # save the original dataframe in session state
        st.session_state["uploaded_file"] = True

    df= st.session_state.df 

    # explode the dataframe in columns where there are multiple values separated by "//"
    # NOTE: "Numero contrat" is the primary key (unique identifier) for the dataframe
    col_to_split = ["Intitule structure","Code structure","Acteurs::Dénomination","Acteurs::Type","Acteurs::Sous-type"]
    exploded_all_dfs=[contrat_unite,
    contrat_codestructure,
    contrat_acteur,
    contrat_typeacteur,
    contrat_soustypeacteur] =multi_separate(df,col_to_split)

    # set the exploded dataframes in session state first time
    if "current_exploded_dfs" not in st.session_state:
        st.session_state.current_exploded_dfs =exploded_all_dfs


    # Interactive filtering
    st.write("### Filtres ")
    # Create a list of columns to filter
    # The exploded dataframes are used to display the filters values for the exploded columns (ones with multiple values separated by //)
    filters=create_filters(df, 
                           exploded_dfs=exploded_all_dfs, 
                           columns=columns)
    print("Applied filters =" ,filters) # printed to the console for debugging

    #Now that we have the filters, we can apply them to the original dataframe
    df_filtered = df.copy() 
    # Apply filters to the dataframe
    for column, filter_value in filters.items():
        if isinstance(filter_value, list):
            if column == "Intitule structure":
                filtered_items = contrat_unite[contrat_unite[column].isin(filter_value)]
                contracts_to_keep = filtered_items["Numero contrat"].unique()
                df_filtered = df_filtered[df_filtered["Numero contrat"].isin(filtered_items["Numero contrat"])]
            elif column == "Acteurs::Dénomination":
                filtered_items = contrat_acteur[contrat_acteur[column].isin(filter_value)]
                contracts_to_keep = filtered_items["Numero contrat"].unique()
                df_filtered = df_filtered[df_filtered["Numero contrat"].isin(filtered_items["Numero contrat"])]
            elif column == "Acteurs::Type":
                filtered_items = contrat_typeacteur[contrat_typeacteur[column].isin(filter_value)]
                contracts_to_keep = filtered_items["Numero contrat"].unique()
                df_filtered = df_filtered[df_filtered["Numero contrat"].isin(filtered_items["Numero contrat"])]
            elif column == "Code structure":
                filtered_items = contrat_codestructure[contrat_codestructure[column].isin(filter_value)]
                contracts_to_keep = filtered_items["Numero contrat"].unique()
                df_filtered = df_filtered[df_filtered["Numero contrat"].isin(filtered_items["Numero contrat"])]
            elif column == "Acteurs::Sous-type":
                filtered_items = contrat_soustypeacteur[contrat_soustypeacteur[column].isin(filter_value)]
                contracts_to_keep = filtered_items["Numero contrat"].unique()
                df_filtered = df_filtered[df_filtered["Numero contrat"].isin(filtered_items["Numero contrat"])]
            else :    
                df_filtered = df_filtered[df_filtered[column].isin(filter_value)]

        else: 
            # datetime filtering
            df_filtered = df_filtered[(df_filtered[column] >= filter_value[0]) & (df_filtered[column] <= filter_value[1])]

    # Save the filtered dataframe in session state
    st.session_state.current_df_filtered = df_filtered

    exploded_filtered_dfs = [contrat_unite_filtered,
    contrat_codestructure_filtered,
    contrat_acteur_filtered,
    contrat_typeacteur_filtered,
    contrat_soustypeacteur_filtered]= multi_separate(df_filtered,col_to_split)
    contrat_RS_filtered=separate(df_filtered,"Contacts Structure",sep=",") # RS = responsable structure



    # ----------------------------------------------------------------------------------------------------------#
    # ##################################### DISPLAY TABLES #####################################################
    # ----------------------------------------------------------------------------------------------------------#


    tab0_1, tab0_2 ,tab0_3= st.tabs(["Tous les contrats", "contrats par dénomination","contrats par type acteur"])
    with tab0_1:
        st.write("### Aperçu general", df_filtered)
        st.write("Nombre de lignes", df_filtered.shape[0])
    with tab0_2:
        st.write("### Aperçu general", contrat_acteur_filtered)
        st.write("Nombre de lignes", contrat_acteur_filtered.shape[0])
    with tab0_3:
        st.write("### Aperçu general", contrat_typeacteur_filtered)
        st.write("Nombre de lignes", contrat_typeacteur_filtered.shape[0])

    
    st.write("---")

    # ----------------------------------------------------------------------------------------------------------#
    # ##################################### PLOTS ##########################################################
    # ----------------------------------------------------------------------------------------------------------#

    occurences_1 = df_filtered.groupby(["Type contrat","Phase"]).size().reset_index(name="Nombre")
    occurences_2 = df_filtered.groupby(["Outil du cadre","Phase"]).size().reset_index(name="Nombre")
    occurences_3 = df_filtered.groupby(["Contact princpal DR&I","Phase"]).size().reset_index(name="Nombre")
    tab1, tab2 ,tab3 = st.tabs(["Type contrat","📊 Outil du cadre ","contact principale DRI  "])
    
    with tab1:
        # Stacked bars with properly positioned labels
        chart = alt.Chart(occurences_1).mark_bar().encode(
            x=alt.X("Nombre:Q", title="Nombre", axis=format_axis(occurences_1,"Nombre",'d')), 
            y=alt.Y("Type contrat:N", sort="-x", title="Type contrat"),
            color=alt.Color("Phase:N")
        ).properties(width=800, height=600)

        st.write(chart)
        st.write("### Données", occurences_1)

    with tab2:
        st.write("## Outil du cadre et Phase")
        chart = alt.Chart(occurences_2).mark_bar().encode(
            x=alt.X("Nombre:Q", title="Nombre",axis=format_axis(occurences_2,"Nombre",'d')),
            y=alt.Y("Outil du cadre:N", sort="-x", title="Outil du cadre"),
            color="Phase:N",
        ).properties(width=800, height=600)

        st.write(chart)
        st.write("### Données", occurences_2)

    with tab3:
        
        # Stacked bars with properly positioned labels
        chart = alt.Chart(occurences_3).mark_bar().encode(
            x=alt.X("Nombre:Q", title="Nombre", axis=format_axis(occurences_3,"Nombre",'d')), 
            y=alt.Y("Contact princpal DR&I:N", sort="-x", title="Contact principal DR&I"),
            color=alt.Color("Phase:N")
        ).properties(width=800, height=600)

        st.write(chart)
        st.write("### Données", occurences_3)


    st.write("---") # -----------------------------------------------------------------------------------------

    tab2,tab3,tab4,tab5 = st.tabs(["Acteurs Dénomination","Contacts Structure","Type acteur","Sous type acteur"])

    with tab2:  # COUNT - VERTICAL
        column_name = "Acteurs::Dénomination"
        new_name = "nom_acteur"
        y_axis_name = "Nombre de contrats"

        # group and count occurrences
        grouped_df = contrat_acteur_filtered[column_name].value_counts().reset_index(name="Count")
        grouped_df.columns = [new_name, "Count"]
        
        # Use the vertical plot function from aux1.py
        chart = vertical_alt_plot(grouped_df, new_name, y_axis_name)
        st.write(chart)

    with tab3: # COUNT - HORIZONTAL

        y_axis_original_col = "Contacts Structure"
        y_axis_name = "Contacts Structure"
        x_axis_name = "Nombre de contrats"

        # Group and count occurrences
        grouped_df3 = contrat_RS_filtered[y_axis_original_col].value_counts().reset_index()
        grouped_df3.columns = [y_axis_name, "Count"]
        
        # Use the horizontal plot function from aux1.py
        chart = horizontal_alt_plot(grouped_df3, y_axis_name, y_axis_name, x_axis_name)
        st.write(chart)

    with tab4: # COUNT - HORIZONTAL

        y_axis_original_col = "Acteurs::Type"
        y_axis_name = "type"
        x_axis_name = "Nombre de contrats"

        # Group and count occurrences for "Acteurs::Type"
        grouped_df4 = contrat_typeacteur_filtered[y_axis_original_col].value_counts().reset_index()
        grouped_df4.columns = [y_axis_name, "Count"] 
        
        # Use the horizontal plot function from aux1.py
        chart = horizontal_alt_plot(grouped_df4, y_axis_name, y_axis_name, x_axis_name)
        st.write(chart)

    with tab5: # COUNT - VERTICAL

        column_name = "Acteurs::Sous-type"
        new_name = "soustype-acteur"
        y_axis_name = "Nombre de contrats"

        # group and count occurrences
        grouped_df4 = contrat_soustypeacteur_filtered[column_name].value_counts().reset_index(name="Count")
        grouped_df4.columns = [new_name, "Count"]

        grouped_df4.loc[grouped_df4[new_name] == "null", new_name] = "non applicable"  # le champs n'a pas été rentrer dans infolab 
        
        # Use the vertical plot function from aux1.py
        chart = vertical_alt_plot(grouped_df4, new_name, y_axis_name)
        st.write(chart)
        

    st.write("---") # -----------------------------------------------------------------------------------------

    tab7, = st.tabs(["Financeurs soustype & Somme Montant Global"])  # Unpack the single tab

    with tab7:
        # montant by Financeurs::Sous-type
        x_axis_col = "Financeurs::Sous-type"
        y_axis_col = "Montant Global"
        sigle=separate(df_filtered,column_to_explode = x_axis_col)
        sigle_merged=sigle.merge(df_filtered, left_on="Numero contrat", right_on="Numero contrat", how="left")
        sigle_merged = sigle_merged.rename(columns={f"{x_axis_col}_x": 'x_axis_col'})
        
        # Filter out rows where Montant Global is 0 or negative
        df_montant_plot = sigle_merged[sigle_merged["Montant Global"] > 0]

        grouped_df = df_montant_plot.groupby("x_axis_col")[y_axis_col].sum().reset_index()
        grouped_df = grouped_df.sort_values(by=y_axis_col, ascending=False)

        montant_chart_financeur_soutype = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X("x_axis_col:N",sort="-y", title=x_axis_col , axis=alt.Axis(labelAngle=45)),
            y=alt.Y(f"{y_axis_col}:Q", title="Somme des Montants Globaux (€)",axis=format_axis(grouped_df,y_axis_col,'d')),
            color=alt.Color("x_axis_col:N", legend=None),  # 👈 remove legend,
            tooltip=["x_axis_col:N", "Montant Global:Q"]
        )

        st.write("Les contrats sans montant spécifié ne sont pas pris en compte.")
        st.write(montant_chart_financeur_soutype)




