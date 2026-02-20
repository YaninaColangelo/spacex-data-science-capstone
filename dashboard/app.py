import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("data/spacex_launch_dash.csv.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

# --- LAYOUT (Solo componentes visuales) ---
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [{'label': i, 'value': i} for i in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie Chart Container
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Range Slider
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),

    # TASK 4: Scatter Chart Container
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# --- CALLBACKS (Fuera del layout) ---

# TASK 2 Callback
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        df_counts = filtered_df.groupby('class').size().reset_index(name='counts')
        fig = px.pie(df_counts, values='counts', names='class',
                     title=f'Total Success Launches for site {entered_site}')
    return fig

# TASK 4 Callback
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    df_filtered = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(df_filtered, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category",
                         title='Correlation between Payload and Success for all Sites')
    else:
        df_site = df_filtered[df_filtered['Launch Site'] == entered_site]
        fig = px.scatter(df_site, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category",
                         title=f'Correlation for site {entered_site}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)