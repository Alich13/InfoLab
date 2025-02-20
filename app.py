import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


"""
[emoji]: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

"""

# streamlit run app.py

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
        if df[column].dtype == 'object':
            unique_values = df[column].unique().tolist()
            if column=="Service":
                selected_values = st.multiselect(f"Filter {column}", unique_values, default="DRV FSI développement")
            else:
                selected_values = st.multiselect(f"Filter {column}", unique_values)

            if selected_values:
                filters[column] = selected_values
        elif df[column].dtype in ['int64', 'float64']:
            min_value = df[column].min()
            max_value = df[column].max()
            selected_range = st.slider(f"Filter {column}", min_value, max_value, (min_value, max_value))
            if selected_range != (min_value, max_value):
                filters[column] = selected_range
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            min_date = df[column].min()
            max_date = df[column].max()
            selected_date_range = st.date_input(f"Filter {column}", [min_date.date(), max_date.date()], min_value=min_date.date(), max_value=max_date.date())
            selected_date_range = [pd.to_datetime(date) for date in selected_date_range]
            if selected_date_range != [min_date, max_date]:
                filters[column] = selected_date_range
    return filters

def generate_diplay_message(occurences):
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




#my_data = pd.read_csv('/Users/alichemkhi/Downloads/jobs_to_delete_tabs.tsv',names=['id','code','name','mail',"start-end","date",'nan'], sep='	')
st.title("InfoLab Dashboard") 


uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])

if uploaded_file:
    
    df=read_excel(uploaded_file)


    # Interactive filtering
    st.write("### Filter Data")
    columns = ["Createur",
               "Service",
               "Intitule structure",
               "Outil du cadre",
               "Action",
               "Type contrat",
               "Acteurs::Dénomination",
               ]#, "Date Création"
    
    
    
    df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y") # convert date columns to datetime
    df_filtered = df
    

    filters=create_filters(df,columns)

    for column, filter_value in filters.items():
        if isinstance(filter_value, list):
            df_filtered = df_filtered[df_filtered[column].isin(filter_value)]
        else:
            df_filtered = df_filtered[(df_filtered[column] >= filter_value[0]) & (df_filtered[column] <= filter_value[1])]

    st.write("### Preview of Data", df_filtered)
    st.write("Raw dataset", df_filtered.shape[0])

    if ( "Outil du cadre" in filters.keys() ) and ("CIFRE" in filters["Outil du cadre"] or "CDDP" in filters["Outil du cadre"]):
        df_filtered=df_filtered[df_filtered["Outil du cadre"].isin(["CDDP","CIFRE"])]
        occurences = df_filtered.groupby(["Outil du cadre","Phase"]).agg({"Phase": "count"})
        st.write(occurences)
        message =generate_diplay_message(occurences)
        st.write(message)


        


    # add a pie chart of the filtered data countries 
    #st.write("### Pie chart of the filtered data")
    #fig, ax = plt.subplots()
    #df_filtered['Financeurs::Pays'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
    #st.pyplot(fig)

    # plot occ evolution over time 
    #st.write("### Occurences evolution over time")
    #occurences = df_filtered.groupby("Date Création").size()
    #fig, ax = plt.subplots()
    #occurences.plot(kind="bar", ax=ax)
    #plt.xticks(rotation=45)
    # plot the bar chart in jupyther
    #st.pyplot(fig)
    


    


