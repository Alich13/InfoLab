import pandas as pd
import streamlit as st

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



def create_filters(df,
                   keys : st.session_state, #possible values in multiselect
                   columns):
    print(keys)
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

def preprocess(df):
        df.fillna("Introuvalble", inplace=True)
        df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y") # convert date columns to datetime
        df["Date Premier Contact"] = df["Date Premier Contact"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime
        df["Date de l'action"] = df["Date de l'action"].map(lambda x : convert_datatime(x) ) # convert date columns to datetime

        pd.to_datetime(df["Date Premier Contact"], format="%d/%m/%Y") # convert date columns to datetime
        	    
        df["Year"] = df["Date Création"].dt.year.astype(int)
        df["Pays"] = df["Financeurs::Pays"].map( lambda x : x.strip().upper() )
        df["Pays"] = df["Pays"].map( lambda x : switch_dict_country[x] if x in switch_dict_country.keys() else x  )

def separate(df,column_to_explode):
    # Normalize: Convert into a separate table

    contract_actors = df[['Numero contrat', column_to_explode]].copy()
    contract_actors[column_to_explode] = contract_actors[column_to_explode].str.split(' // ')
    contract_actors = contract_actors.explode(column_to_explode)
    contract_actors[column_to_explode] = contract_actors[column_to_explode].str.strip()

    
    return contract_actors
        