import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


#my_data = pd.read_csv('/Users/alichemkhi/Downloads/jobs_to_delete_tabs.tsv',names=['id','code','name','mail',"start-end","date",'nan'], sep='	')
st.title("InfoLab Dashboard") 

uploaded_file = st.file_uploader("Upload your Excel/CSV/TSV file", type=["xlsx","csv","tsv"])

if uploaded_file:
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

    st.write("### Preview of Data", df.head())
    st.write("Raw dataset ", df.shape[0])

    # Interactive filtering
    st.write("### Filter Data")
    columns = ["Createur", "Date Création", "Service"]

    # convert date columns to datetime
    df["Date Création"]=pd.to_datetime(df["Date Création"], format="%d/%m/%Y")



    df_filtered = df
    filters = {}

    for column in columns:

        if df[column].dtype == 'object':
            unique_values = df[column].unique().tolist()
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
            selected_date_range = st.date_input(f"Filter {column}", [min_date, max_date], min_value=min_date, max_value=max_date)
            if selected_date_range != [min_date, max_date]:
                filters[column] = selected_date_range

    for column, filter_value in filters.items():
        if isinstance(filter_value, list):
            df_filtered = df_filtered[df_filtered[column].isin(filter_value)]
        else:
            df_filtered = df_filtered[(df_filtered[column] >= filter_value[0]) & (df_filtered[column] <= filter_value[1])]

    st.write("Raw dataset", df_filtered.shape[0])



    

    

