# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 23:23:20 2021

@author: Chun Yip
"""

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_table as dt
from dash.dependencies import Input, Output


app = dash.Dash(__name__)

#Create a list for areas
boro_species= ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=boroname, spc_common'+\
        '&$group=boroname, spc_common').replace(' ', '%20')
soql_borosp=pd.read_json(boro_species)
boro=soql_borosp['boroname'].unique()

soql_url2 = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=steward, health, count(tree_id)' +\
        '&$group=steward, health').replace(' ', '%20')
soql_trees2 = pd.read_json(soql_url2)     
soql_trees2['%']=(100 * soql_trees2['count_tree_id'] / soql_trees2.groupby('steward')['count_tree_id'].transform('sum')).round(2)
soql_trees2=soql_trees2.dropna()
fig = px.bar(soql_trees2, x='steward', y='%', color='health') #barmode="group")

#Set up the layout
app.layout = html.Div([
    html.Div([
        
        html.Div([
    
            html.Label('Q1: Proportion of Trees Health'),
            
            html.Br(),
            
            html.P('Select Area'),
            
            dcc.Dropdown(
                id='area',
                options=[{'label': i, 'value': i} for i in boro],
                value='Bronx'
            ),
            
            html.Br(),
            
            html.P('Select Species'),
            
            html.Br(),
            
            dcc.Dropdown(id='species'),
            
            html.Br()
            
            ], style={'width': '50%', 'display': 'inline-block'}),
    
        html.Div([
        
            html.Div(id='display-health', 
                     style={'width':'50%', 'textAlign':'left'}),
            
            html.Br(),
            
            html.P('Q2: Are Stewards having an impact on the health of trees?'),
        
            dcc.Graph(id='stewards-impact', figure=fig),
            
            html.Br(),
            
            html.P('There is basically no relationship between stewards and trees health')
    
    ])
])
])

#Question1

@app.callback(
    Output('species', 'options'),
    Input('area', 'value'))
def set_species(selected_area): 
    selected_species=(soql_borosp[soql_borosp['boroname']==selected_area]['spc_common'].dropna()
                      .tolist())
    return [{'label': i, 'value': i} for i in selected_species]

@app.callback(
    Output('display-health', 'children'),
    Input('area', 'value'),
    Input('species', 'value'))
def set_display_children(selected_area, selected_species):
    boro = selected_area
    soql_url1 = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=boroname, spc_common,health,count(tree_id)' +\
        '&$where=boroname=\'{}\'' +\
        '&$group=boroname, spc_common,health').format(boro).replace(' ', '%20')
    soql_trees1 = pd.read_json(soql_url1)
    soql_trees1['%']=(100 * soql_trees1['count_tree_id'] / soql_trees1.groupby('spc_common')['count_tree_id'].transform('sum')).round(2)
    st=soql_trees1[soql_trees1['spc_common']==selected_species]
    st=st.iloc[:,[2,4]]
    data = st.to_dict('rows')
    columns =  [{"name": i, "id": i,} for i in (st.columns)]
    return dt.DataTable(data=data, columns=columns, style_data={'border': '5px solid blue', 'textAlign':'center'}, style_header={ 'border': '5px solid blue', 'textAlign':'center'})
    
if __name__ == '__main__':
    app.run_server(debug=True)