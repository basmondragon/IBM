# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Extract unique launch sites for dropdown
launch_sites = [{"label": "All Sites", "value": "All Sites"}] + [
    {"label": site, "value": site} for site in spacex_df["Launch Site"].unique()
]

# Create a Dash application
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        # Title
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # Dropdown for Launch Site selection
        dcc.Dropdown(
            id="site-dropdown",
            options=launch_sites,
            placeholder="Select a Launch Site Here",
            value="All Sites",
            searchable=True,
        ),
        html.Br(),
        # Pie chart for success launches
        dcc.Graph(id="success-pie-chart"),
        html.Br(),
        # Payload range slider
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={i: f"{i}" for i in range(0, 10001, 1000)},
            value=[min_payload, max_payload],
        ),
        # Scatter chart for payload vs. success
        dcc.Graph(id="success-payload-scatter-chart"),
    ]
)


# Callback for pie chart
@app.callback(Output("success-pie-chart", "figure"), Input("site-dropdown", "value"))
def update_pie_chart(launch_site):
    if launch_site == "All Sites":
        # Aggregate success rate by launch site
        site_success = spacex_df.groupby("Launch Site")["class"].mean().reset_index()
        fig = px.pie(
            site_success,
            values="class",
            names="Launch Site",
            title="Total Success Launches by Site",
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df["Launch Site"] == launch_site]
        fig = px.pie(
            filtered_df,
            names="class",
            title=f"Total Success Launches for {launch_site}",
        )
    return fig


# Callback for scatter chart
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def update_scatter_chart(launch_site, payload_range):
    low, high = payload_range
    mask = (spacex_df["Payload Mass (kg)"] >= low) & (
        spacex_df["Payload Mass (kg)"] <= high
    )
    filtered_df = spacex_df.loc[mask]

    if launch_site != "All Sites":
        filtered_df = filtered_df[filtered_df["Launch Site"] == launch_site]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site"],
        title=f"Payload vs. Success for {launch_site}",
    )
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
