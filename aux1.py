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


def format_axis(df,col,type)->alt.Axis:
    """
    Format the axis of a chart based on the column and type.
    """
    
    assert(col in df.columns), f"Column '{col}' is not present in the DataFrame."
    assert(~df.empty), "DataFrame is empty."
        
    
    # Dynamically calculate tickCount based on the maximum value of "Nombre"
    max_nombre = df[col].max()

    if max_nombre < 10:
        tick_count = 1
        return alt.Axis(format=type, tickCount=tick_count)
    else:
        return alt.Axis(format=type) # automatically determines tickCount



def separate(df,column_to_explode,sep=" // "):
    # Normalize: Convert into a separate table

    contract_actors = df[['Numero contrat', column_to_explode]].copy()
    contract_actors[column_to_explode] = contract_actors[column_to_explode].str.split(sep)  # Split the column into lists
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


def create_filters(df, 
                   exploded_dfs : list,
                   columns : list )-> dict:
    """
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

            # If the user selects any values, add them to the filters dictionary
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
    """
    Preprocess the DataFrame by cleaning and transforming columns.
    """
        
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].fillna("Introuvable")


    df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y") # convert date columns to datetime
    df["Date Premier Contact"] = df["Date Premier Contact"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime
    df["Date Signature"] = df["Date Signature"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime
    df["Date de l'action"] = df["Date de l'action"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime
    df["Phase"] = df.apply(lambda x : "Abandonné" if x["Action"] in ["Abandonné","Refusé"] else x["Phase"] , axis=1) 
    df["Outil du cadre"] = df.apply(lambda x : "Autres cadres" if x["Outil du cadre"] in ["Introuvable","Autres"] else x["Outil du cadre"] , axis=1) 
    df["Financeurs::Sous-type"] = df.apply(lambda x : "Non spécifié" if x["Financeurs::Sous-type"] in ["Introuvable"] else x["Financeurs::Sous-type"] , axis=1) 
    df["Financeurs::Sous-type"] = df.apply(lambda x : "Etabl public recherche" if x["Financeurs::Sous-type"] in ["Opérateurs de recherche"] else x["Financeurs::Sous-type"] , axis=1) 

        
    pd.to_datetime(df["Date Premier Contact"], format="%d/%m/%Y") # convert date columns to datetime
            
    df["Year"] = df["Date Création"].dt.year.astype(int)
    df["Pays"] = df["Financeurs::Pays"].map( lambda x : x.strip().upper() )
    


def clear_cache_on_new_upload(uploaded_file):
    """
    Clear Streamlit's cache if a new file is uploaded.
    """
    if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file:
        st.cache_data.clear()  # Clear the cache
        st.session_state["last_uploaded_file"] = uploaded_file

# when a function is deterministic (always gives the same result for the same input), and you want Streamlit to remember its result.
@st.cache_data
def plot_grouped_bar(df, group_col, value_col, title="", xlabel=None, ylabel=None,group_function='sum'):
    if group_function not in ['sum', 'mean']:
        raise ValueError("group_function must be either 'sum' or 'mean'")
    if group_function == 'mean':
        grouped_df = df.groupby(group_col)[value_col].mean().reset_index()
    else:  # 'sum'
        grouped_df = df.groupby(group_col)[value_col].sum().reset_index()
    
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
    grouped_df = df.groupby([x_col, stack_col])[value_col].sum().reset_index()

    chart = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X(f"{x_col}:N", title=xlabel or x_col),
        y=alt.Y(f"{value_col}:Q", title=ylabel or value_col, stack='zero'),
        color=alt.Color(f"{stack_col}:N", title=stack_col),
        tooltip=[f"{x_col}:N", f"{stack_col}:N", f"{value_col}:Q"]
    ).properties(
        title=title
    )

    return chart

# when a function is deterministic (always gives the same result for the same input), and you want Streamlit to remember its result.
@st.cache_data
def horizontal_alt_plot(grouped_df, y_axis_col, y_axis_name, x_axis_name):
    """
    Create a horizontal bar chart with all y-axis labels visible.
    
    Args:
        grouped_df: DataFrame with columns [y_axis_col, "Count"]
        y_axis_col: Name of the column for y-axis categories
        y_axis_name: Display name for y-axis
        x_axis_name: Display name for x-axis
    
    Returns:
        Altair chart object
    """
    # Calculate dynamic height based on number of unique values
    num_categories = len(grouped_df)
    chart_height = max(600, num_categories * 35)  # Increased spacing per category
    
    # Create the Altair bar chart
    chart = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X("Count:Q", title=x_axis_name, axis=format_axis(grouped_df,"Count",'d')),
        y=alt.Y(f"{y_axis_col}:N", sort="-x", title=y_axis_name, 
                axis=alt.Axis(
                    labelLimit=0,  # No limit on label length
                    labelOverlap=False,  # Don't allow label overlap
                    labelSeparation=5,  # Minimum separation between labels
                    titlePadding=10  # Add padding for title
                )),
        color=alt.Color(f"{y_axis_col}:N", legend=None)  # Remove legend for simplicity
    ).properties(
        width=1000, 
        height=chart_height,
        autosize=alt.AutoSizeParams(
            type='fit',
            contains='padding'
        )
    ).resolve_scale(
        y='independent'  # Ensure y-axis scaling is independent
    )
    
    return chart

@st.cache_data
def vertical_alt_plot(grouped_df, x_axis_col, y_axis_name="Nombre de contrats"):
    """
    Create a vertical bar chart with all x-axis labels visible.
    
    Args:
        grouped_df: DataFrame with columns [x_axis_col, "Count"]
        x_axis_col: Name of the column for x-axis categories
        y_axis_name: Display name for y-axis
    
    Returns:
        Altair chart object
    """
    # Sort by Count in descending order
    grouped_df = grouped_df.sort_values(by="Count", ascending=False)
    
    # Convert category column to ordered categorical type to preserve sorting
    grouped_df[x_axis_col] = pd.Categorical(
        grouped_df[x_axis_col], categories=grouped_df[x_axis_col], ordered=True
    )
    
    # Calculate dynamic width based on number of unique values
    num_categories = len(grouped_df)
    chart_width = max(800, num_categories * 50)  # Minimum 800px, or 50px per category
    
    # Create the Altair bar chart
    chart = alt.Chart(grouped_df).mark_bar().encode(
        x=alt.X(f"{x_axis_col}:N", sort=None, title="",
                axis=alt.Axis(
                    labelAngle=45,
                    labelLimit=0,  # No limit on label length
                    labelOverlap=False,  # Don't allow label overlap
                    labelSeparation=5,  # Minimum separation between labels
                    titlePadding=10  # Add padding for title
                )),
        y=alt.Y("Count:Q", title=y_axis_name, axis=format_axis(grouped_df,"Count",'d')),
        color=alt.Color(f"{x_axis_col}:N", legend=None)  # Remove legend for simplicity
    ).properties(
        width=chart_width,
        height=600,
        autosize=alt.AutoSizeParams(
            type='fit',
            contains='padding'
        )
    ).resolve_scale(
        x='independent'  # Ensure x-axis scaling is independent
    )
    
    return chart
