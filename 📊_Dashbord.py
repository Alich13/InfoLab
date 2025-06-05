
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
# * Mitigate column names key errors (if the input file changes)
# check if the column names are in the dataframe
# streamlit run 📊_Dashbord.py

st.title("Tableau de bord") 
st.write("Suivi d'activité globale des labo et aide au développement")


uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])
st.write("----")


if uploaded_file or ("uploaded_file" in st.session_state and st.session_state["uploaded_file"]) : 
    
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
    exploded_all_dfs=[contrat_unite,
    contrat_codestructure,
    contrat_acteur,
    contrat_typeacteur] =multi_separate(df,["Intitule structure","Code structure","Acteurs::Dénomination","Acteurs::Type"])

    # set the exploded dataframes in session state first time
    # TODO :  this is not needed for now , but we might need it for automatic filtering mult-selection
    if "current_exploded_dfs" not in st.session_state:
        st.session_state.current_exploded_dfs =exploded_all_dfs


    # Interactive filtering
    st.write("### Filtres ")

    # Create a list of columns to filter
    # the exploded dataframes are used to display the filters values for the exploded columns (ones with multiple values separated by //)
    filters=create_filters(df, # TODO: we need to pass the filtered dataframe
                           exploded_dfs=exploded_all_dfs, #st.session_state.current_exploded_dfs,
                           columns=columns)
    print("Applied filters =" ,filters)

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
            else :    
                df_filtered = df_filtered[df_filtered[column].isin(filter_value)]

        else:
            df_filtered = df_filtered[(df_filtered[column] >= filter_value[0]) & (df_filtered[column] <= filter_value[1])]


    # Save the filtered dataframe in session state    
    st.session_state.current_df_filtered = df_filtered

    exploded_filtered_dfs = [contrat_unite_filtered,
    contrat_codestructure_filtered,
    contrat_acteur_filtered,
    contrat_typeacteur_filtered]= multi_separate(df_filtered,["Intitule structure","Code structure","Acteurs::Dénomination","Acteurs::Type"])

    st.session_state.current_exploded_dfs = exploded_filtered_dfs


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
    tab1, tab2 = st.tabs(["Type contrat","📊 Outil du cadre "])
    with tab1:
        # Stacked bars with properly positioned labels
        chart = alt.Chart(occurences_1).mark_bar().encode(
            x=alt.X("Nombre:Q", title="Nombre"),  # or "zero"
            y=alt.Y("Type contrat:N", sort="-x", title="Type contrat"),
            color=alt.Color("Phase:N")
        ).properties(width=800, height=600)

        st.write(chart)
        st.write("### Données", occurences_1)



    with tab2:
        st.write("## Outil du cadre et Phase")
        chart = alt.Chart(occurences_2).mark_bar().encode(
            x=alt.X("Nombre:Q", title="Nombre"),
            y=alt.Y("Outil du cadre:N", sort="-x", title="Outil du cadre"),
            color="Phase:N",
            
        ).properties(width=800, height=600)

        st.write(chart)
        st.write("### Données", occurences_2)


    st.write("---") # -----------------------------------------------------------------------------------------

    tab2,tab3,tab4,tab5 = st.tabs(["Acteurs Dénomination","Contacts Structure","Type acteur","Type de contrat"])

    with tab2:  # COUNT - VERTICAL
        column_name = "Acteurs::Dénomination"
        new_name="nom_acteur"
        y_axis_name = "Nombre de contrats"

        # group and count occurrences
        grouped_df = contrat_acteur_filtered[column_name].value_counts().reset_index(name="Count")
        grouped_df.columns = [new_name, "Count"]
        # Sort by Count in descending order
        grouped_df = grouped_df.sort_values(by="Count", ascending=False)
        # Convert category column to ordered categorical type to preserve sorting
        grouped_df[new_name] = pd.Categorical(
            grouped_df[new_name], categories=grouped_df[new_name], ordered=True
        )
        bar=alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X(new_name, sort=None , axis=alt.Axis(labelAngle=45)),
            y=alt.Y('Count:Q', sort="-x", title=y_axis_name , axis=alt.Axis(format='d')),
            color=alt.Color(new_name, legend=None)  # Remove legend for simplicity
        )
        st.write(bar)

    with tab3: # COUNT - HORIZONTAL

        y_axis_col = "Contacts Structure"
        y_axis_name = "Contacts Structure"
        x_axis_name = "Nombre de contrats"


        # Group and count occurrences
        grouped_df3 = df_filtered[y_axis_col].value_counts().reset_index()
        grouped_df3.columns = [y_axis_col, "Count"]
        # Create the Altair bar chart
        chart = alt.Chart(grouped_df3).mark_bar().encode(
            x=alt.X("Count:Q", title="Nombre de contrats",axis=alt.Axis(format='d')),
            y=alt.Y(f"{y_axis_col}:N", sort="-x", title=y_axis_name),  # Ensures correct sorting
            color=alt.Color(f"{y_axis_col}:N", legend=None)  # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size

        st.write(chart)

    with tab4: # COUNT - HORIZONTAL

        y_axis_col = "Acteurs::Type"
        y_axis_name = "type"
        x_axis_name = "Nombre de contrats"

        # Group and count occurrences for "Acteurs::Type"
        grouped_df4 = contrat_typeacteur_filtered["Acteurs::Type"].value_counts().reset_index()
        grouped_df4.columns = [y_axis_name, "Count"] 
        # Create the Altair bar chart
        chart = alt.Chart(grouped_df4).mark_bar().encode(
            x=alt.X("Count:Q", title=x_axis_name),
            y=alt.Y(f"{y_axis_name}:N", sort="-x", title="type"),  # Ensures correct sorting
            color=alt.Color(f"{y_axis_name}:N", legend=None)       # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size

        st.write(chart)

    with tab5: # COUNT - HORIZONTAL
        
        y_axis_col = "Type contrat"
        y_axis_name = "Type contrat"
        x_axis_name = "Nombre de contrats"
        # Group and count occurrences
        grouped_df3 = df_filtered[y_axis_col].value_counts().reset_index()
        grouped_df3.columns = [y_axis_col, "Count"]

        # Create the Altair bar chart
        chart = alt.Chart(grouped_df3).mark_bar().encode(
            x=alt.X("Count:Q", title=y_axis_name),
            y=alt.Y(f"{y_axis_col}:N", sort="-x", title=x_axis_name),  # Ensures correct sorting
            color=alt.Color(f"{y_axis_col}:N", legend=None)  # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size

        st.write(chart)



    st.write("---") # -----------------------------------------------------------------------------------------

    tab6,tab7 = st.tabs(["Financeurs::Soustype ","Financeurs::Soustype & Montant Global moyen"])


    with tab6:

        # montant by Financeurs::Sous-type
        x_axis_col = "Financeurs::Sous-type"
        sigle=separate(df_filtered,column_to_explode = x_axis_col)
        sigle_merged=sigle.merge(df_filtered, left_on="Numero contrat", right_on="Numero contrat", how="left")
        sigle_merged = sigle_merged.rename(columns={f"{x_axis_col}_x": 'x_axis_col'})
        
        
        # Group and count occurrences
        grouped_df3 = sigle_merged['x_axis_col'].value_counts().reset_index()
        grouped_df3.columns = ['x_axis_col', "Count"]

        # Create the Altair bar chart
        chart3 = alt.Chart(grouped_df3).mark_bar().encode(
            x=alt.X("Count:Q", title="Nombre de contrats"),
            y=alt.Y("x_axis_col:N", sort="-x", title=x_axis_col),  # Ensures correct sorting
            color=alt.Color("x_axis_col:N", legend=None)  # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size


        st.write(chart3)
    

    with tab7:
        # montant by Financeurs::Sous-type
        x_axis_col = "Financeurs::Sous-type"
        y_axis_col = "Montant Global"
        sigle=separate(df_filtered,column_to_explode = x_axis_col)
        sigle_merged=sigle.merge(df_filtered, left_on="Numero contrat", right_on="Numero contrat", how="left")
        sigle_merged = sigle_merged.rename(columns={f"{x_axis_col}_x": 'x_axis_col'})
        
        # Filter out rows where Montant Global is 0 or negative
        df_montant_plot = sigle_merged[sigle_merged["Montant Global"] > 0]

        grouped_df = df_montant_plot.groupby("x_axis_col")[y_axis_col].mean().reset_index()
        grouped_df = grouped_df.sort_values(by=y_axis_col, ascending=False)

        montant_chart_financeur_soutype = alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X("x_axis_col:N",sort="-y", title=x_axis_col , axis=alt.Axis(labelAngle=45)),
            y=alt.Y(f"{y_axis_col}:Q", title="Montant Global (€)"),
            color=alt.Color("x_axis_col:N", legend=None),  # 👈 remove legend,
            tooltip=["x_axis_col:N", "Montant Global:Q"]
        )


        st.write("Les contrats sans montant spécifié ne sont pas pris en compte.")
        st.write(montant_chart_financeur_soutype)

    


