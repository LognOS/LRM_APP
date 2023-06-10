
import psycopg2
import pandas as pd
import streamlit as st
from psycopg2 import sql
import datetime
import plotly.express as px
from utils_uploader import create_histogram, create_conn  # Import the function from utils.py


st.set_page_config(layout="wide")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

palettes = {
    "Pastel": px.colors.qualitative.Pastel,
    "D3": px.colors.qualitative.D3,
    "G10": px.colors.qualitative.G10,
    "T10": px.colors.qualitative.T10,
    "Alphabet": px.colors.qualitative.Alphabet,
}

# List the tables in the database connected
st.cache_data(ttl=300)
def get_table_names():
    conn = create_conn()
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """
    df = pd.read_sql(query, conn)
    conn.close()
    # Exclude specific table names
    df = df[~df['table_name'].isin(['pg_stat_statements'])]
    return df['table_name'].tolist()

# Query data from a given table
st.cache_data(ttl=1800)
def query_table(table_name):
    conn = create_conn()
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
    conn.close()
    return df

# Check if session state keys exist or not, otherwise initialize them
if 'df_dict' not in st.session_state:
    st.session_state['df_dict'] = {}
if 'selected_owner' not in st.session_state:
    st.session_state['selected_owner'] = "All"
if 'selected_risk' not in st.session_state:
    st.session_state['selected_risk'] = "All"

if not st.session_state.df_dict:
    # Fetch data only once
    st.session_state.df_dict["risk_main"] = query_table("risk_main")
    st.session_state.df_dict["pre_event_control"] = query_table("pre_event_control")
    st.session_state.df_dict["pos_event_control"] = query_table("pos_event_control")

#Display projects
#project_name = st.selectbox("PROJECT", ["Yanacocha WTP2"])

with st.expander("SELECT"):
# Display dropdown for owner selection
    owners = ["All"] + st.session_state.df_dict["risk_main"]["OWNER"].unique().tolist()
    selected_owner = st.selectbox("OWNER", owners, index=owners.index(st.session_state.selected_owner))


    if selected_owner != st.session_state.selected_owner:
        # If the selected owner has changed, reset the selected risk to 'All'
        st.session_state.selected_owner = selected_owner
        st.session_state.selected_risk = "All"

    # Filter risks based on selected owner
    if st.session_state.selected_owner != "All":
        risks = st.session_state.df_dict["risk_main"][st.session_state.df_dict["risk_main"]["OWNER"] == st.session_state.selected_owner]
    else:
        risks = st.session_state.df_dict["risk_main"]

    # Display dropdown for risk selection
    risks_display = ["All"] + [f'{row["TITLE"]}  [{row["RISK ID"]}]' for _, row in risks.iterrows()]
    st.session_state.selected_risk = st.selectbox("RISK:", risks_display, index=risks_display.index(st.session_state.selected_risk))

# Display relevant dataframes if a risk is selected
if st.session_state.selected_risk != "All":
    risk_id = st.session_state.selected_risk.split("[")[1].split("]")[0].strip()  # Extract the RISK ID from the selection

    pre_event_df = st.session_state.df_dict["pre_event_control"][st.session_state.df_dict["pre_event_control"]["RISK ID"] == risk_id]
    st.dataframe(pre_event_df[["RISK ID", "CONTROL", "DESCRIPTION", "OWNER"]])

    pos_event_df = st.session_state.df_dict["pos_event_control"][st.session_state.df_dict["pos_event_control"]["RISK ID"] == risk_id]
    st.dataframe(pos_event_df[["RISK ID", "CONTROL", "DESCRIPTION", "OWNER"]])

# Create histograms using the imported function
fig_owner = create_histogram(st.session_state.df_dict["risk_main"], "OWNER", "Number of Risks by Owner", color_discrete_sequence=palettes["Pastel"])
st.plotly_chart(fig_owner)

fig_grade = create_histogram(st.session_state.df_dict["risk_main"], "GRADE", "Number of Risks by Grade", color_discrete_sequence=palettes["D3"])
st.plotly_chart(fig_grade)

with st.expander("DB REVIEW"):
    table_names = ["None"]+get_table_names()
    selected_table = st.selectbox("Select table", table_names)
    if selected_table != "None":
        st.dataframe(st.session_state.df_dict[selected_table])