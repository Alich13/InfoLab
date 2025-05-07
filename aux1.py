import pandas as pd
import streamlit as st
import altair as alt

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
               "Code structure",
               "Outil du cadre",
               "Type contrat",
               "Acteurs::Dénomination",
               "Acteurs::Type",
               "Year"
               ]#, "Date Création"


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



def separate(df,column_to_explode):
    # Normalize: Convert into a separate table

    contract_actors = df[['Numero contrat', column_to_explode]].copy()
    contract_actors[column_to_explode] = contract_actors[column_to_explode].str.split(' // ')
    contract_actors = contract_actors.explode(column_to_explode)
    contract_actors[column_to_explode] = contract_actors[column_to_explode].str.strip()

    return contract_actors

# when a function is deterministic (always gives the same result for the same input), and you want Streamlit to remember its result.
@st.cache_data
def multi_separate(df,columns_to_explode):
    exploded_dfs = []
    for column in columns_to_explode:
        separated_df = separate(df, column)
        exploded_dfs.append(separated_df)
    return exploded_dfs


def create_filters(df, # NOTE THIS IS THE FILTERED DATAFRAME
                   exploded_dfs : list,
                   columns : list ):
    """
    NOTE: we start from the filtered dataframe so that we get ONLY the values that are present in the filtered dataframe
    and not all the values in the original dataframe
    Create filters for the dataframe based on the columns provided.
    Args:
        df (pd.DataFrame): The dataframe to filter.
        exploded_dfs (list): The exploded dataframes for the columns to filter.
        columns (list): The columns to create filters for.
    Returns:
        dict: A dictionary containing the selected filters for each column.
    """


    # Create a dictionary to store the unique values for each column
    [contrat_unite,
    contrat_codestructure,
    contrat_acteur,
    contrat_typeacteur] = exploded_dfs

    # values to display in the multiselect
    keys={
        "Intitule structure": contrat_unite["Intitule structure"].unique().tolist(),
        "Acteurs::Dénomination": contrat_acteur["Acteurs::Dénomination"].unique().tolist(),
        "Code structure": contrat_codestructure["Code structure"].unique().tolist(),
        "Acteurs::Type": contrat_typeacteur["Acteurs::Type"].unique().tolist()
    } 

    filters = {}
    for column in columns:
        column_to_display = switch_dict_spelling[column] if column in switch_dict_spelling.keys() else column
        if df[column].dtype == 'object':
            unique_values = df[column].unique().tolist()
            if column=="Service":
                selected_values = st.multiselect(column_to_display, unique_values, default="DRV FSI développement")
            elif    column=="Outil du cadre":
                selected_values = st.multiselect(column_to_display, unique_values, default=["CIFRE","CDDP"])
            elif    column=="Intitule structure": #unite
                selected_values = st.multiselect(column_to_display, keys["Intitule structure"],key="")
            elif    column=="Acteurs::Dénomination": 
                selected_values = st.multiselect(column_to_display, keys["Acteurs::Dénomination"],key="")
            elif    column=="Code structure":
                selected_values = st.multiselect(column_to_display, keys["Code structure"],key="")
            elif    column=="Acteurs::Type": 
                selected_values = st.multiselect(column_to_display, keys["Acteurs::Type"],key="")
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


def convert_datatime(date_str):
    try:
        return pd.to_datetime(date_str, format="%d/%m/%Y")
    except ValueError:
        return pd.NaT

# when a function is deterministic (always gives the same result for the same input), and you want Streamlit to remember its result.
@st.cache_data
def preprocess(df):
        
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].fillna("Introuvalble")


        df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y") # convert date columns to datetime
        df["Date Premier Contact"] = df["Date Premier Contact"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime
        df["Date Signature"] = df["Date Signature"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime
        df["Date de l'action"] = df["Date de l'action"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime

        pd.to_datetime(df["Date Premier Contact"], format="%d/%m/%Y") # convert date columns to datetime
        	    
        df["Year"] = df["Date Création"].dt.year.astype(int)
        df["Pays"] = df["Financeurs::Pays"].map( lambda x : x.strip().upper() )

        
# when a function is deterministic (always gives the same result for the same input), and you want Streamlit to remember its result.
@st.cache_data
def plot_grouped_bar(df, group_col, value_col, title="", xlabel=None, ylabel=None):
    grouped_df = df.groupby(group_col)[value_col].mean().reset_index()
    
    chart = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X(f"{group_col}:N", title=xlabel or group_col),
        y=alt.Y(f"{value_col}:Q", title=ylabel or value_col),
        color=alt.Color(f"{group_col}:N"),  # 👈 remove legend
        tooltip=[f"{group_col}:N", f"{value_col}:Q"]
    ).properties(
        title=title
    )

    return chart

# when a function is deterministic (always gives the same result for the same input), and you want Streamlit to remember its result.
@st.cache_data
def stacked_plot_grouped_bar(df, x_col, stack_col, value_col, title="", xlabel=None, ylabel=None):
    # Group by both x_col and stack_col, and compute mean of value_col
    grouped_df = df.groupby([x_col, stack_col])[value_col].mean().reset_index()

    chart = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X(f"{x_col}:N", title=xlabel or x_col),
        y=alt.Y(f"{value_col}:Q", title=ylabel or value_col, stack='zero'),
        color=alt.Color(f"{stack_col}:N", title=stack_col),
        tooltip=[f"{x_col}:N", f"{stack_col}:N", f"{value_col}:Q"]
    ).properties(
        title=title
    )

    return chart
    