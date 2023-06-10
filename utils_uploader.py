import plotly.express as px
import psycopg2
import streamlit as st

# Set up a function to create a connection
def create_conn():
    conn = psycopg2.connect(**st.secrets['postgres'])
    return conn

# Set up a function to test a connection
def test_conn():
    """Tests connection to the PostgreSQL database."""
    try:
        with psycopg2.connect(database="your_database", user="your_username", password="your_password", host="your_host") as conn:
            st.write("Connection to the database was successful.")
    except psycopg2.Error as e:
        st.write(f"Unable to connect to the database. The error {e} occurred.")

def create_histogram(df, column, title, color_discrete_sequence=None):
    """Create a histogram using Plotly."""
    counts = df[column].value_counts()
    fig = px.histogram(counts, x=counts.index, y=counts.values, nbins=len(counts),
                       labels={'x':column, 'y':'Number of Risks'}, color=counts.index,
                       title=title, color_discrete_sequence=color_discrete_sequence)
    return fig