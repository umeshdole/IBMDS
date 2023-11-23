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

site_options = [{'label': 'All Sites', 'value': 'ALL'}]
for launch_site in spacex_df["Launch Site"].unique():
    site_options.append({'label':launch_site, 'value':launch_site})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                             options = site_options,
                                             value = 'ALL',
                                             placeholder = 'Select a Launch Site here',
                                             searchable = True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0:'0',
                                                       2000:'2000',
                                                       4000:'4000',
                                                       6000:'6000',
                                                       8000:'8000',
                                                       10000:'10000'},
                                                value=[min_payload, max_payload]),
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart',component_property='figure'),
              Input(component_id='site-dropdown',component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df[spacex_df['Launch Site']==entered_site].groupby('class').size().reset_index(name='class count')
    if entered_site=='ALL':
        fig = px.pie(spacex_df, values='class', names='Launch Site', title='Total Successful Launches By Site')
        return fig
    else:
        fig = px.pie(filtered_df, values='class count', names='class', title='Total Successful Launches for '+entered_site)
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart',component_property='figure'),
              [Input(component_id='site-dropdown',component_property='value'),
               Input(component_id='payload-slider',component_property='value')])
def get_scatter_plot(entered_site,payload_range):
    low, high = payload_range
    window = (spacex_df['Payload Mass (kg)']>low) & (spacex_df['Payload Mass (kg)']<high)
    filtered_df = spacex_df[window]
    if entered_site=='ALL':
        fig = px.scatter(filtered_df,
                         x=filtered_df['Payload Mass (kg)'], y=filtered_df['class'],
                         color='Booster Version Category',
                         title='Correlation between Success and Payload for all sites')
        return fig
    else:
        filtered_df = filtered_df[filtered_df['Launch Site']==entered_site]
        fig = px.scatter(filtered_df,
                         x=filtered_df['Payload Mass (kg)'], y=filtered_df['class'],
                         color='Booster Version Category',
                         title=f'Success by Payload size for {entered_site}')
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
