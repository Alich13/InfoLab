import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt


"""
[emoji]: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
"""
switch_dict_country={
            "FRANCE // FRANCE" :"FRANCE",
            "FRANCE // FRANCE // FRANCE" : "FRANCE",
            "FRANCE //":"FRANCE",
            "FR": "FRANCE"
        }
def preprocess(df):
        df.fillna("Introuvalble", inplace=True)
        df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y") # convert date columns to datetime
        df["Year"] = df["Date Création"].dt.year.astype(int)
        df["Pays"] = df["Financeurs::Pays"].map( lambda x : x.strip().upper() )
        df["Pays"] = df["Pays"].map( lambda x : switch_dict_country[x] if x in switch_dict_country.keys() else x  )
        



df = pd.read_excel("/Users/alichemkhi/Desktop/myProjects/InfoLab/datasym/extraction_contrats.xlsx")
df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y")


df_filtered=df[df["Service"]=="DRV FSI développement"]

# -----------------------Barplot 1
occurences = df_filtered.groupby(["Outil du cadre","Phase"]).size().reset_index(name="Count")
tab1, tab2 = st.tabs(["📊 Bar Chart", "📋 Source Data"])
with tab1:
    st.write("### Category Count Bar Chart")
    chart = alt.Chart(occurences).mark_bar().encode(
        x=alt.X("Outil du cadre:N", sort="-y", title="Outil du cadre"),
        y=alt.Y("Count:Q", title="Count"),
        color="Phase:N"
    ).properties(width=800, height=600)
    st.write(chart)
with tab2:
    st.write("### Source Data")
    st.dataframe(occurences)  # Display the table



# ---------------------- Barplot 2
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
     


