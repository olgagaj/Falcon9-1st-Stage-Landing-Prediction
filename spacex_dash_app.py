# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([dcc.Dropdown(id='site-dropdown',
                                options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                [{'label': i, 'value': i} for i in spacex_df['Launch Site'].unique()],
                                value='ALL',
                                placeholder="Select a Launch Site here",
                                searchable=True)]),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                html.Div(dcc.RangeSlider(id='payload-slider',                
                                min=0, max=10000, step=1000,
                                marks={i: str(i) for i in range(0, 10001, 1000)},
                                value=[min_payload, max_payload])),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value')])
def get_pie_chart(entered_site):
    if entered_site == 'ALL' or entered_site is None:
        data=spacex_df[spacex_df['class'] == 1]
        fig = px.pie(data, values='class', 
        names='Launch Site', 
        title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df.loc[spacex_df['Launch Site'] == entered_site]
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        class_counts['class'] = class_counts['class'].map({1: 'Success', 0: 'Failure'})

        fig = px.pie(class_counts, values='count', names='class', 
                     title=f'Success vs Failure Launches for site {entered_site}')

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id='payload-slider', component_property='value')])
def update_scatter_chart(entered_site,payload_slider):
    low, high = payload_slider
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Payload vs. Success for All Sites')
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Payload vs. Success for {entered_site}')
    return fig


# Run the app
if __name__ == '__main__':
    app.run()