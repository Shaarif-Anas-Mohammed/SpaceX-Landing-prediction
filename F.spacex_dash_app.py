import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                   options=[
                                    {'label': 'All Sites', 'value': 'ALL'},
                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                    ],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                
                                html.P("Payload range (Kg):"),
                                # Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min = 0, max = 10000, step = 1000,
                                                value = [min_payload, max_payload]),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])
                                

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
            Output(component_id='success-pie-chart', component_property='figure'),
            Input(component_id='site-dropdown', component_property='value')
            )
def get_pie_chart(selected_site):
    selected_df = spacex_df
    if selected_site == 'ALL':
        fig = px.pie(selected_df, values='class', 
            names='Launch Site', 
            title='Pie chart of all the launches of SpaceX')
                                        
    else:
        selected_df = spacex_df[spacex_df['Launch Site'] == selected_site].groupby(['Launch Site', 'class']). \
        size().reset_index(name='class count')
        title = f"Total Success Launches for site {selected_site}"
        fig = px.pie(selected_df,values='class count', names='class', title=title)
       
                                    
    return fig

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
    Input(component_id="payload-slider", component_property="value")] )

def get_scatter_plot(selected_site, slider_range):
    low, high = slider_range
    slide = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)
    dropdown_scatter=spacex_df[slide]
    if selected_site == 'ALL':
        fig = px.scatter(spacex_df, 
        x = 'Payload Mass (kg)', 
        y = 'class', 
        title='Correlation between Payload and Launch success in All sites',
        color = "Booster Version Category")                                
                                        
    else:
        site_df = spacex_df[ spacex_df['Launch Site'] == selected_site]
        fig = px.scatter(site_df, 
        x = 'Payload Mass (kg)', 
        y = 'class', 
        title='Correlation between Payload and Launch success ' + selected_site,
        color = "Booster Version Category")
                                    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()