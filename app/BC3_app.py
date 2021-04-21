### Business Case 3

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import dash_table
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# importing the 4 datasets
products = pd.read_csv('datasets/products.csv')
departments = pd.read_csv('datasets/departments.csv')
orders = pd.read_csv('datasets/orders.csv')
order_products = pd.read_csv('datasets/order_products.csv')

# renaming a column in 'departments'
departments.columns = ['department_id', 'department_name']
# merging the different datasets in one
product_departments = pd.merge(products, departments, how='left', on='department_id').\
                        drop(["department_id"], axis=1)
order_product_departments = pd.merge(order_products, product_departments, how='left', on='product_id').\
                        drop(["product_id"], axis=1)
df = pd.merge(order_product_departments, orders, how='left', on='order_id')

top_substituition = pd.read_csv('datasets/top_substituition_by_dept.csv')
top_substituition = top_substituition.reset_index().iloc[:,1:]
top_substituition.columns = ['Rule','Antecedent', 'Consequent', 'Support', 'Confidence', 'Lift', 'Department']
department = 'beverages'

recommendation = pd.read_csv('datasets/recommendation.csv')
recommendation.columns = ['Rule', 'Base Product','Recommended']
recommendation_product = 'bread'

############################################ components #####################################################

product_options = []
for i in df['product_name'].unique().tolist():
    product_options.append({'label': i, 'value':  i})

department_options = []
for i in df['department_name'].unique().tolist():
    department_options.append({'label': i, 'value':  i})

recommendation_option = []
for i in recommendation['Base Product'].unique().tolist():
    recommendation_option.append({'label': i, 'value':  i})

dropdown_product_1 = dcc.Dropdown(
        id='product1',
        options=product_options,
        value='fresh fruits'
    )

dropdown_product_2 = dcc.Dropdown(
        id='product2',
        options=product_options,
        value='fresh vegetables'
    )

dropdown_substitute = dcc.Dropdown(
    id='department',
    options=department_options,
    value='beverages'
    )

dropdown_product_recommendation = dcc.Dropdown(
    id='recommendation_product',
    options=recommendation_option,
    value='bread'
    )

dashtable1 = dash_table.DataTable(
        id='table1',
        columns=[{"name": i, "id": i} for i in top_substituition.columns],
        data=top_substituition[top_substituition['Department'] == department].to_dict('records')
    )

dashtable2 = dash_table.DataTable(
        id='table2',
        columns=[{"name": i, "id": i} for i in recommendation.columns],
        data=recommendation[recommendation['Base Product'] == recommendation_product].to_dict('records')
    )


######################################## app itself #######################################################

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

    html.H1('Market Basket Analysis: Instacart'),

    html.H4('Authors: Lorenzo Pigozzi, Nguyen Phuc, Ema Mandura, Xavier Goncalves'),

    html.Br(),
    html.Hr(),
    html.Br(),

    html.H2('Analysis by pair of products'),


    html.Div([
        html.Div([
            html.Label('Select Product 1'),
            dropdown_product_1
        ], style={'width': '50%'}, className='box'),

        html.Br(),

        html.Div([
            html.Label('Select Product 2'),
            dropdown_product_2
        ], style={'width': '50%'}, className='box')

    ], style={'display': 'flex'} ),



    html.Br(),

    html.Div([
        html.Div([
            dcc.Graph(id='graph_1'),
        ], style={'width': '40%'}, className='box'),

        html.Div([
            dcc.Graph(id='graph_3'),
        ], style={'width': '20%'}, className='box'),

        html.Div([
            dcc.Graph(id='graph_2'),
        ], style={'width': '40%'}, className='box'),

    ], style={'display': 'flex'}),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Br(),

    html.H2('Top pair of substitute products by department'),

    html.Label('Select a department'),

    html.Br(),

    dropdown_substitute,

    html.Br(),
    html.Br(),

    dashtable1,

    html.Br(),
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Br(),


    html.H2('Recommendation System: Complementary Products'),

    html.Label('Select a product'),

    dropdown_product_recommendation,

    html.Br(),
    html.Br(),

    dashtable2,

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br()



])

#################################################### callbacks ############################################

@app.callback(
    [Output('graph_1', 'figure'),
     Output('graph_2', 'figure'),
     Output('graph_3', 'figure')
     ],
    [Input('product1', 'value'),
     Input('product2', 'value')
     ]
)

def products_analysis(product1, product2):
    list_of_products = [product1, product2]

    ### plot 1
    df_for_plot = df.groupby(['product_name', 'order_hour_of_day']).size()
    df_for_plot = pd.DataFrame(df_for_plot).reset_index()
    df_for_plot.columns = ['product', 'hour_of_day', 'frequency']
    # manipulating the data with pivot table
    df_for_plot = pd.pivot_table(df_for_plot, values=['frequency'], columns=['product'], index=['hour_of_day'])
    # dropping the multi-index level for the columns
    df_for_plot.columns = df_for_plot.columns.droplevel(0)

    ##plotting##
    data_for_plot = [dict(type='scatter',
                          x=df_for_plot.index,
                          y=df_for_plot[product],
                          name=product)
                     for product in list_of_products
                     ]
    # setting the layout
    plot_1_layout = dict(title=dict(text='Frequency purchases per hour of the day'),
                         xaxis=dict(title='Hour of the day'),
                         yaxis=dict(title='Total Frequency')
                         )
    # displaying the graph
    plot_1 = go.Figure(data=data_for_plot, layout=plot_1_layout)

    ### plot 2
    df_for_plot = df.groupby(['product_name', 'order_dow']).size()
    df_for_plot = pd.DataFrame(df_for_plot).reset_index()
    df_for_plot.columns = ['product', 'order_dow', 'frequency']
    # manipulating the data with pivot table
    df_for_plot = pd.pivot_table(df_for_plot, values=['frequency'], columns=['product'], index=['order_dow'])
    # dropping the multi-index level for the columns
    df_for_plot.columns = df_for_plot.columns.droplevel(0)

    # labels_plot = {}
    ##plotting##
    data_for_plot = [dict(type='scatter',
                          x=df_for_plot.index,
                          y=df_for_plot[product],
                          name=product)
                     for product in list_of_products
                     ]
    # setting the layout
    plot_2_layout = dict(title=dict(text='Frequency purchases per day of the week'),
                         xaxis=dict(title='Day of the week',
                                    tickmode = "array",
                                    ticktext = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
                                                "Friday", "Saturday"],
                                    tickvals = [0, 1, 2, 3, 4, 5, 6, 7]
                                    ),
                         yaxis=dict(title='Total Frequency')
                         )
    # displaying the graph
    plot_2 = go.Figure(data=data_for_plot, layout=plot_2_layout)

    ### plot 3
    top_products = pd.DataFrame(df['product_name'].value_counts()).reset_index()
    top_products.columns = ['product_name', 'value']
    top_products = top_products[top_products['product_name'].isin(list_of_products)]
    plot_3 = px.bar(top_products, y='value', x='product_name', orientation='v',
                    color="product_name", color_discrete_sequence=px.colors.qualitative.Antique,
                    title='Quantity purchased')


    return plot_1, plot_2, plot_3



@app.callback(
    Output('table1', 'data'),
    Input('department', 'value')
)

def get_the_substitute(department):
    table_updated = top_substituition[top_substituition['Department'] == department].to_dict('records')
    return table_updated


@app.callback(
    Output('table2', 'data'),
    Input('recommendation_product', 'value')
)

def get_the_substitute(recommendation_product):
    table_updated2 = recommendation[recommendation['Base Product'] == recommendation_product].to_dict('records')
    return table_updated2


if __name__ == '__main__':
    app.run_server(debug=True)