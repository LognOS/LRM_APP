import plotly.express as px
import plotly.graph_objects as go
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


st.cache_data()
def create_histogram(df, column, title, color, bins=None):
    # Create a histogram
    fig = px.histogram(df, 
                       x=column,
                       nbins=bins)  # Here we use the 'bins' variable

    # Set the color of all bars to be the same
    fig.update_traces(marker=dict(color=color))

    # Rotate the x-axis labels if they are too long
    fig.update_layout(
        xaxis=dict(tickangle=45),  # rotate the x-axis labels 45 degrees
        yaxis_title="Count",
        autosize=False,  # disable autosizing
        width=500,  # set figure width
        height=450,  # set figure height
        margin=dict(t=10,l=20, r=20, b=120),  # adjust margins to make room for x-axis labels
    )
    return fig

st.cache_data()
def heat_mapper(df, title):
    """
    This function takes a DataFrame as input and returns a plotly heatmap figure.
    The DataFrame should contain 'GRADE', 'OWNER' and 'RISK' columns.
    """
    
    # Create a function to truncate the risk text
    def truncate_text(text):
        return ' '.join(text.split()[:5])

    # Truncate the risk text and then group the DataFrame by 'GRADE' and 'OWNER',
    # concatenating the risks with line breaks
    df['RISK'] = df['TITLE'].apply(truncate_text)
    text = df.groupby(['GRADE', 'OWN. FUNC'])['TITLE'].apply(lambda x: '<br>'.join(x)).reset_index()

    # Create a pivot table from the DataFrame for the number of risks
    pivot = df.pivot_table(index='GRADE', columns='OWN. FUNC', aggfunc='size', fill_value=0)

    # Create a pivot table for the hover text
    hover_text = text.pivot(index='GRADE', columns='OWN. FUNC', values='TITLE').fillna('')

    # Create the heatmap figure
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        text=hover_text.values,  # add the hover text
        hoverongaps=False,
        hoverinfo='text',
        colorscale='RdYlGn_r',
        ),
        layout = go.Layout(height=400, width=600)) #Here we set the height to 600

    # Add annotations (the number of risks in each square)
    annotations = []
    for i, row in enumerate(pivot.values):
        for j, value in enumerate(row):
            annotations.append(go.layout.Annotation(
                x=pivot.columns[j], y=pivot.index[i], text=str(value),
                showarrow=False, font=dict(size=14, color='#333333')))

    fig.update_layout(annotations=annotations,
                      title_text="",
                      margin=dict(t=10))

    # Return the figure
    return fig