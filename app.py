import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


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
            if column=="Year":
                selected_range = st.slider(f"Filter {column}", min_value, max_value, (2020, max_value))
            else :
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

columns = ["Contact princpal DR&I",
               "Service",
               "Intitule structure",
               "Outil du cadre",
               "Action",
               "Type contrat",
               "Acteurs::Dénomination",
               "Year"
               ]#, "Date Création"


#my_data = pd.read_csv('/Users/alichemkhi/Downloads/jobs_to_delete_tabs.tsv',names=['id','code','name','mail',"start-end","date",'nan'], sep='	')
st.title("InfoLab Dashboard") 


uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])

if uploaded_file:
    
    df=read_excel(uploaded_file)
    df["Date Création"] = pd.to_datetime(df["Date Création"], format="%d/%m/%Y") # convert date columns to datetime
    df["Year"] = df["Date Création"].dt.year.astype(int)

    
    # Interactive filtering
    st.write("### Filter Data")
    
    
    df_filtered = df
    df_filtered.fillna("introuvalble", inplace=True)

    

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
        
        # display 
        #message =generate_display_message(occurences)
        #st.write(message)


        # ------------------------------------Piechart
        switch_dict={
            "FRANCE // FRANCE" :"FRANCE",
            "FRANCE // FRANCE // FRANCE" : "FRANCE",
            "FRANCE //":"FRANCE",
            "FR": "FRANCE"
        }
        df_filtered["Pays"]=df_filtered["Financeurs::Pays"].map( lambda x : x.strip().upper() )
        df_filtered["Pays"]=df_filtered["Pays"].map( lambda x : switch_dict[x] if x in switch_dict.keys() else x  )


        grouped_df = df_filtered["Pays"].value_counts().reset_index()
        grouped_df.columns = ["Pays", "Count"]  # Rename columns

        fig = px.pie(grouped_df, names="Pays", values="Count", 
                    title="Distribution par pays", 
                    hole=0.4,  # Makes it a donut chart (set to 0 for a full pie)
                    color_discrete_sequence=px.colors.qualitative.Set2)

        # Display in Streamlit
        st.write("### Category Count Bar Plot")
        st.plotly_chart(fig)

        # ------------------------------------BAR PLOTS
        # Contact princpal DR&I
        grouped_df = df_filtered["Contact princpal DR&I"].value_counts().reset_index()
        grouped_df.columns = ["Contact princpal DR&I", "Count"]  # Rename columns
        
        fig = px.bar(grouped_df, y="Contact princpal DR&I", x="Count", 
                    title="Category Count",
                    text_auto=True, 
                    color="Contact princpal DR&I",
                    orientation="h")

        fig.update_layout(
            showlegend=False,
            width=1000,  # Set width of the plot
            height=600   # Set height of the plot
        )

        # ------------------------------------BAR PLOTS
        # Contact Intitule structure
        # Check for NaN and replace with 'Unavailable'
        df_filtered["Intitule structure"].fillna("Unavailable", inplace=True)

        # Create the grouped DataFrame for "Intitule structure"
        grouped_df2 = df_filtered["Intitule structure"].value_counts().reset_index()
        grouped_df2.columns = ["Intitule structure", "Count"]  # Rename columns

        # Create the bar plot for "Intitule structure"
        fig2 = px.bar(grouped_df2, y="Intitule structure", x="Count", 
                    title="Intitule structure Count",
                    text_auto=True, 
                    color="Intitule structure",
                    orientation="h")
        
        fig2.update_layout(
            showlegend=False,
            width=2000,  # Set width of the plot
            height=600,   # Set height of the plot
            yaxis=dict(
            tickfont=dict(size=8)  # Set the font size for y-axis labels
            )
        )

        
        # ------------------------------------BAR PLOTS
        # Contact Type contrat
        df_filtered["Type contrat"].fillna("Unavailable", inplace=True)

        # Create the grouped DataFrame for "Type contrat"
        grouped_df3 = df_filtered["Type contrat"].value_counts().reset_index()
        grouped_df3.columns = ["Type contrat", "Count"]  # Rename columns

        fig3 = px.bar(grouped_df3, y="Type contrat", x="Count", 
                    title="Type contrat Count",
                    text_auto=True, 
                    color="Type contrat",
                    orientation="h")

        fig3.update_layout(
            showlegend=False,
            width=2000,  # Set width of the plot
            height=600,   # Set height of the plot
        )

        # ------------------------------------TABS
        tab = st.radio("Select a Plot", ("Contact principal DR&I", "Intitule structure", "Type contrat"))

        if tab == "Contact principal DR&I":
            st.write("### Contact principal DR&I Count Bar Plot")
            st.plotly_chart(fig)

        elif tab == "Intitule structure":
            st.write("### Intitule structure Count Bar Plot")
            st.plotly_chart(fig2, use_container_width=True)

        elif tab == "Type contrat":
            st.write("### Type contrat Count Bar Plot")
            st.plotly_chart(fig3, use_container_width=True)

        


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
    


    


