import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt


"""
[emoji]: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
"""

# TODO: 
# * Mitigate column names key errors (if the input file changes)
# * Fix warning 
# streamlit run app.py


switch_dict_spelling={
            "Intitule structure" : "Unité",
            "Contact princpal DR&I" : "Contact principal DR&I",
            "Year" : "Année",
            "Type contrat" : "Type de contrat",
            "Acteurs::Dénomination" :"Dénomination d'acteurs",
            "Acteurs::Type" : "Type d'acteurs"
        }

columns = ["Contact princpal DR&I",
               "Service",
               "Intitule structure",
               "Outil du cadre",
               "Action",
               "Type contrat",
               "Acteurs::Dénomination",
               "Acteurs::Type",
               "Year"
               ]#, "Date Création"


switch_dict_country={
            "FRANCE // FRANCE" :"FRANCE",
            "FRANCE // FRANCE // FRANCE" : "FRANCE",
            "FRANCE //":"FRANCE",
            "FR": "FRANCE"
        }



def read_excel(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e_csv:
        try:
            df = pd.read_csv(uploaded_file, sep='\t')
        except Exception as e_tsv:
            try:
                df = pd.read_excel(uploaded_file)
            except Exception as e_xlsx:
                st.error("The file format is not supported or the file is corrupted.")
                st.stop()

    return df



def create_filters(df,column):
    filters = {}
    for column in columns:
        column_to_display = switch_dict_spelling[column] if column in switch_dict_spelling.keys() else column
        if df[column].dtype == 'object':
            unique_values = df[column].unique().tolist()
            if column=="Service":
                selected_values = st.multiselect(column_to_display, unique_values, default="DRV FSI développement")
            else:
                selected_values = st.multiselect(column_to_display, unique_values)

            if selected_values:
                filters[column] = selected_values
        elif df[column].dtype in ['int64', 'float64']:
            min_value = df[column].min()
            max_value = df[column].max()
            if column=="Year":
                selected_range = st.slider(column_to_display, min_value, max_value, (2020, max_value))
            else :
                selected_range = st.slider(column_to_display, min_value, max_value, (min_value, max_value))

            if selected_range != (min_value, max_value):
                filters[column] = selected_range
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            min_date = df[column].min()
            max_date = df[column].max()
            selected_date_range = st.date_input(column_to_display, [min_date.date(), max_date.date()], min_value=min_date.date(), max_value=max_date.date())
            selected_date_range = [pd.to_datetime(date) for date in selected_date_range]
            if selected_date_range != [min_date, max_date]:
                filters[column] = selected_date_range
    return filters

def generate_display_message(occurences):
# 		       Phase
# Outil du cadre	        Phase	
# CDDP	en gestion	        12
#       en négociation	    6
# CIFRE	archivé	            61
#       en gestion	        272
#       en négociation	    91
#       en préparation	    25

    # get all the possible lo levl values 
    lowLevelVar=occurences.columns[0]
    possible_status=list(set([ x[1] for x in occurences[lowLevelVar].index]))
    display_dict={}
    # iterate through a dataframe
    for index, row in occurences.iterrows():
        highLevel=index[0]
        lowLevel =index[1]
        if highLevel not in display_dict:
            display_dict[highLevel]=[0]*len(possible_status) # initialize the count list
            lowLevelIndex=possible_status.index(lowLevel)
            assert lowLevelIndex>=0 and lowLevelIndex<len(possible_status)
            display_dict[highLevel][lowLevelIndex]=int(row[lowLevelVar])
        else : 
            lowLevelIndex=possible_status.index(lowLevel)
            assert lowLevelIndex>=0 and lowLevelIndex<len(possible_status)
            display_dict[highLevel][lowLevelIndex]=int(row[lowLevelVar])
        
        # display the results
        message=""
        for k,v in display_dict.items():
            message+=f"{k} \n"
            for i,e in enumerate(v):
                message+=f"\t{possible_status[i]} : {e} \n"
                
        message
    return message

def preprocess(df):
        df.fillna("Introuvalble", inplace=True)
        df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y") # convert date columns to datetime
        df["Year"] = df["Date Création"].dt.year.astype(int)
        df["Pays"] = df["Financeurs::Pays"].map( lambda x : x.strip().upper() )
        df["Pays"] = df["Pays"].map( lambda x : switch_dict_country[x] if x in switch_dict_country.keys() else x  )
        



st.title("InfoLab Dashboard") 
uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])
st.write("----")



if uploaded_file:
    
    df=read_excel(uploaded_file)
    preprocess(df)

    # Interactive filtering
    st.write("### Filtres ")
    df_filtered = df

    filters=create_filters(df,columns)
    for column, filter_value in filters.items():
        if isinstance(filter_value, list):
            df_filtered = df_filtered[df_filtered[column].isin(filter_value)]
        else:
            df_filtered = df_filtered[(df_filtered[column] >= filter_value[0]) & (df_filtered[column] <= filter_value[1])]

    st.write("### Preview of Data", df_filtered)
    st.write("Raw dataset", df_filtered.shape[0])

    
    st.write("---")
    # ----------------------------------------------------

    occurences = df_filtered.groupby(["Outil du cadre","Phase"]).size().reset_index(name="Count")
    tab1, tab2 = st.tabs(["📊 Bar Chart", "📋 Source Data"])
    with tab1:
        st.write("### Category Count Bar Chart")
        chart = alt.Chart(occurences).mark_bar().encode(
            x=alt.X("Count:Q", title="Count"),
            y=alt.Y("Outil du cadre:N", sort="-x", title="Outil du cadre"),
            color="Phase:N"
        ).properties(width=800, height=600)
        st.write(chart)
    with tab2:
        st.write("### Source Data")
        st.dataframe(occurences)  # Display the table


    st.write("---")
    # ----------------------------------------------------

    tab3, tab4,tab5 = st.tabs(["Contact principal", "Unité","Type de contrat"])

    with tab3:
        grouped_df = df_filtered["Contact princpal DR&I"].value_counts().reset_index(name="Count")
        # Sort by Count in descending order
        grouped_df = grouped_df.sort_values(by="Count", ascending=False)
        # Convert category column to ordered categorical type to preserve sorting
        grouped_df["Contact princpal DR&I"] = pd.Categorical(
            grouped_df["Contact princpal DR&I"], categories=grouped_df["Contact princpal DR&I"], ordered=True
        )
        st.write(alt.Chart(grouped_df).mark_bar().encode(
            x=alt.X('Contact princpal DR&I', sort=None),
            y='Count',
        ))

    with tab4:

        # Group and count occurrences for "Acteurs::Type"
        grouped_df4 = df_filtered["Acteurs::Type"].value_counts().reset_index()
        grouped_df4.columns = ["type", "Count"]
        # Create the Altair bar chart
        chart4 = alt.Chart(grouped_df4).mark_bar().encode(
            x=alt.X("Count:Q", title="Count"),
            y=alt.Y("type:N", sort="-x", title="type acteur"),  # Ensures correct sorting
            color=alt.Color("type:N", legend=None)  # Remove legend for simplicity
        ).properties(width=1000, height=600)  # Adjust plot size

        # Display in Streamlit
        st.write("### Acteurs Type Count Bar Chart")
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
        st.write("### Type Contrat Count Bar Chart")
        st.write(chart3)
        

        st.write("---")
    # ----------------------------------------------------

    # Pie chart by country 
    grouped_df = df_filtered["Pays"].value_counts().reset_index()
    grouped_df.columns = ["Pays", "Count"]  # Rename columns

    fig = px.pie(grouped_df, names="Pays", values="Count", 
                title="Distribution par pays", 
                hole=0.4,  # Makes it a donut chart (set to 0 for a full pie)
                color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig)

    


