import streamlit as st
import pandas as pd
from streamlit import session_state

# Title of the app
st.title("CSV Viewer App")

# File path input for loading CSV
file_path = "./group_by_for_transpose_table.csv"
df = None


# Load the CSV file if a valid path is provided
if file_path:
    try:
        df = pd.read_csv(file_path)
        st.success("CSV file loaded successfully.")
    except Exception as e:
        st.error(f"Error loading the CSV file: {str(e)}")

display_options = ['Original', 'Transposed']
# Display the DataFrame
if df is not None:

    page = st.radio('Navigate', display_options)

    if page == 'Original':
        st.write("Data from CSV file:")
        st.write(df)
    else:
        df_transposed = df.transpose()
        st.write("Transposed Data:")
        st.dataframe(df_transposed,use_container_width=True)


