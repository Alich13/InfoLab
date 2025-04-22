
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.styles.stylesheet")
from aux import *


"""
[emoji]: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
"""

# TODO: 
# * Mitigate column names key errors (if the input file changes)
# * Fix warning 
# streamlit run 📊_Dashbord.py



st.title("Tableau de bord") 
st.write("Suivi d'activité globale des labo et aide au développement")

uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])
st.write("----")

# NOTE: "Numero contrat" is the primary key (unique identifier) for the dataframe

# Initialize session state if not set
if "possible_key_dict" not in st.session_state:
    st.session_state.possible_key_dict = {}


if uploaded_file or True: # For testing purposes, set uploaded_file to True
    
    if "df" not in st.session_state:
        st.session_state.df=read_excel("/Users/alichemkhi/Desktop/myProjects/InfoLab/datasym/extraction_contrats.xlsx")#(uploaded_file)
        st.session_state.current_df_filtered = st.session_state.df
    
    df= st.session_state.df 
    
    # guarded by a catch data decorator 
    preprocess(df) 

    # save the original dataframe in session state
    st.session_state["uploaded_file"] = True

    # explode the dataframe in columns where there are multiple values separated by "//"
    # NOTE: "Numero contrat" is the primary key (unique identifier) for the dataframe
    exploded_all_dfs=[contrat_unite,
    contrat_codestructure,
    contrat_acteur,
    contrat_typeacteur] =multi_separate(df,["Intitule structure","Code structure","Acteurs::Dénomination","Acteurs::Type"])

    # set the exploded dataframes in session state first time
    if "current_exploded_dfs" not in st.session_state:
        st.session_state.current_exploded_dfs =exploded_all_dfs


    # Interactive filtering
    st.write("### Filtres ")
    # To create new filters, All we need is current filtered dataframe
    filters=create_filters(df, # TODO: we need to pass the filtered dataframe
                           exploded_dfs=exploded_all_dfs, #st.session_state.current_exploded_dfs,
                           columns=columns)
    print(filters)
    #NOTE: Now that we have the filters, we can apply them to the original dataframe
    df_filtered = df.copy() 
    # Initialize filtered contract-X dataframes
    contrat_unite_filtered = contrat_unite
    contrat_codestructure_filtered = contrat_codestructure
    contrat_acteur_filtered = contrat_acteur
    contrat_typeacteur_filtered = contrat_typeacteur
    # Apply filters to the dataframe
    for column, filter_value in filters.items():
        if isinstance(filter_value, list):
           
            contracts_to_keep= []
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

    
    st.session_state.current_df_filtered = df_filtered
    
    exploded_dfs = [contrat_unite_filtered,
    contrat_codestructure_filtered,
    contrat_acteur_filtered,
    contrat_typeacteur_filtered]= multi_separate(df_filtered,["Intitule structure","Code structure","Acteurs::Dénomination","Acteurs::Type"])

    st.session_state.current_exploded_dfs = exploded_dfs


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
    # ----------------------------------------------------

    occurences = df_filtered.groupby(["Outil du cadre","Phase"]).size().reset_index(name="Count")
    tab1, tab2 = st.tabs(["📊 Bar Chart", "📋 Source Data"])
    with tab1:
        st.write("## Outil du cadre et Phase")
        chart = alt.Chart(occurences).mark_bar().encode(
            x=alt.X("Count:Q", title="Count"),
            y=alt.Y("Outil du cadre:N", sort="-x", title="Outil du cadre"),
            color="Phase:N"
        ).properties(width=800, height=600)
        st.write(chart)
    with tab2:
        st.write("## Source de données ")
        st.dataframe(occurences)  # Display the table


    st.write("---")
    # ----------------------------------------------------

    tab2,tab3,tab4,tab5 = st.tabs(["Acteurs Dénomination","Contacts Structure","Type acteur","Type de contrat"])

    with tab2:
        column_name = "Acteurs::Dénomination"
        new_name="nom_acteur"
        grouped_df = contrat_acteur_filtered[column_name].value_counts().reset_index(name="Count")
        grouped_df.columns = [new_name, "Count"]
        # Sort by Count in descending order
        grouped_df = grouped_df.sort_values(by="Count", ascending=False)
        # Convert category column to ordered categorical type to preserve sorting
        grouped_df[new_name] = pd.Categorical(
            grouped_df[new_name], categories=grouped_df[new_name], ordered=True
        )
        st.write(alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X(new_name, sort=None),
            y='Count',
        ))
        
    with tab3:

        # Group and count occurrences
        grouped_df3 = df_filtered["Contacts Structure"].value_counts().reset_index()
        grouped_df3.columns = ["Contacts Structure", "Count"]

        # Create the Altair bar chart
        chart3 = alt.Chart(grouped_df3).mark_bar().encode(
            x=alt.X("Count:Q", title="Count"),
            y=alt.Y("Contacts Structure:N", sort="-x", title="Contacts Structure"),  # Ensures correct sorting
            color=alt.Color("Contacts Structure:N", legend=None)  # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size

        # Display in Streamlit
        st.write("### Contacts Structure ")
        st.write(chart3)
        

        st.write("---")

    with tab4:

        # Group and count occurrences for "Acteurs::Type"
        grouped_df4 = contrat_typeacteur_filtered["Acteurs::Type"].value_counts().reset_index()
        grouped_df4.columns = ["type", "Count"]
        # Create the Altair bar chart
        chart4 = alt.Chart(grouped_df4).mark_bar().encode(
            x=alt.X("Count:Q", title="Count"),
            y=alt.Y("type:N", sort="-x", title="type"),  # Ensures correct sorting
            color=alt.Color("type:N", legend=None)  # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size

        # Display in Streamlit
        st.write("### Type acteur")
        st.write(chart4)

    with tab5:
        # Group and count occurrences
        grouped_df3 = df_filtered["Type contrat"].value_counts().reset_index()
        grouped_df3.columns = ["Type contrat", "Count"]

        # Create the Altair bar chart
        chart3 = alt.Chart(grouped_df3).mark_bar().encode(
            x=alt.X("Count:Q", title="Count"),
            y=alt.Y("Type contrat:N", sort="-x", title="Type contrat"),  # Ensures correct sorting
            color=alt.Color("Type contrat:N", legend=None)  # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size

        # Display in Streamlit
        st.write("### Type contrat ")
        st.write(chart3)
        

        st.write("---")

    st.write("---")
    # ----------------------------------------------------

    tab6,tab7 = st.tabs(["Financeurs::Soustype ","Financeurs::Soustype & Mantant Global moyen"])


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
            x=alt.X("Count:Q", title="Count"),
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
            x=alt.X("x_axis_col:N",sort="-y", title=x_axis_col),
            y=alt.Y(f"{y_axis_col}:Q", title="Montant Global (€)"),
            color=alt.Color("x_axis_col:N", legend=None),  # 👈 remove legend,
            tooltip=["x_axis_col:N", "Montant Global:Q"]
        )


        st.write("***Les zeros sont exclus !***")
        st.write(montant_chart_financeur_soutype)

    


