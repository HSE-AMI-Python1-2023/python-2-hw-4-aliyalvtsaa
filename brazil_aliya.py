import pandas as pd
import json
import dash
import zipfile
import wget
from dash import html, dcc
import plotly.express as px
from urllib.request import urlopen
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

# url = 'https://github.com/Palladain/Deep_Python/raw/main/Homeworks/Homework_1/archive.zip'
# filename = wget.download(url)

# with zipfile.ZipFile(filename, 'r') as zip_ref:
#     zip_ref.extractall('./')
    
# sellers = pd.read_csv('olist_sellers_dataset.csv')
# items = pd.read_csv('olist_order_items_dataset.csv')
# orders = pd.read_csv('olist_orders_dataset.csv')
# customers = pd.read_csv('olist_customers_dataset.csv')
# products = pd.read_csv('olist_products_dataset.csv')
# translation = pd.read_csv('product_category_name_translation.csv')

# sells=pd.merge(sellers, items, on='seller_id', how='inner')
# sells=pd.merge(sells, orders, on='order_id', how='inner')
# sells=pd.merge(sells, customers, on='customer_id', how='inner')
# sells=pd.merge(sells, products, on='product_id', how='inner')	
# sells=pd.merge(sells, translation, on='product_category_name', how='inner')
# sells=sells[['seller_state','price','customer_state','product_category_name_english','order_purchase_timestamp','order_status']]
# df=sells.copy()

df=pd.read_csv('sells.csv')
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()

with urlopen("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson") as response:
    brazil = json.load(response)
for feature in brazil["features"]:
    feature["id"] = feature["properties"]["sigla"]
all_states = [feature["id"] for feature in brazil["features"]]
all_states_df = pd.DataFrame({'id': all_states, 'count': 0})
app = dash.Dash(__name__)

colors = {
    'background': '#ffffff',
    'text': '#000000',
    'plot_background': '#ffffff',
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Анализ продаж и покупок по штатам и статусам',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'fontFamily': 'Courier New, monospace',
            'marginBottom': '20px'
        }
    ),
    html.Div([
        html.Label('Просмотр количества по штатам:', style={'color': colors['text'],'fontFamily': 'Courier New, monospace'}),
        dcc.RadioItems(
            id='map-type-selector',
            options=[
                {'label': 'Продавцы', 'value': 'sellers'},
                {'label': 'Покупатели', 'value': 'customers'},
            ],
            value='sellers',
            style={'color': colors['text'], 'fontFamily': 'Courier New, monospace'}
        ),
        dcc.Graph(id='state-map'),
    ], style={'marginBottom': '20px', 'flex': '100%'}),
        html.Div(
        html.Button('Сбросить выбор штата', 
                    id='reset-state-button', 
                    hidden=True,
                    n_clicks=0,
                    style={
                        'fontSize': '16px',
                        'fontWeight': 'bold', 
                        'color': 'white', 
                        'backgroundColor': '#dc7176', 
                        'padding': '10px 24px',
                        'borderRadius': '12px',
                        'cursor': 'pointer', 
                        'outline': 'none', 
                        'margin': '10px' 
                    }),
        style={'textAlign': 'center', 'margin': '20px'}
    ),
    html.Div([
        html.Div([
            html.Label('Выберите штат продавца:', style={'color': colors['text'],'fontFamily': 'Courier New, monospace'}),
            dcc.Dropdown(
                id='seller-state-dropdown',
                options=[{'label': 'Вся Бразилия', 'value': 'ALL'}] +
                        [{'label': state, 'value': state} for state in df['seller_state'].unique()],
                value='ALL',
                multi=True,
                style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '10px',
                       'fontFamily': 'Courier New, monospace', 'marginRight': '20px'}
            ),
            html.Label('Выберите статус заказа:', style={'color': colors['text'],'fontFamily': 'Courier New, monospace'}),
            dcc.Dropdown(
                id='order-status-dropdown',
                options=[{'label': 'Все', 'value': 'ALL'}] +
                        [{'label': status, 'value': status} for status in df['order_status'].unique()],
                value=['delivered'],
                multi=True,
                style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '20px', 
                       'fontFamily': 'Courier New, monospace','marginRight': '20px'}
            ),
            dcc.DatePickerRange(
                id='seller-date-picker-range',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                style={'color': colors['text'], 'fontFamily': 'Courier New, monospace'}
            ),
            dcc.Graph(id='seller-category-sales-graph', style={'marginBottom': '20px'}),
        ], style={'marginBottom': '20px', 'flex': '50%'}),
        html.Div([
            html.Label('Выберите штат покупателя:', style={'color': colors['text'],'fontFamily': 'Courier New, monospace'}),
            dcc.Dropdown(
                id='customer-state-dropdown',
                options=[{'label': 'Вся Бразилия', 'value': 'ALL'}] +
                        [{'label': state, 'value': state} for state in df['customer_state'].unique()],
                value='ALL',
                multi=True,
                style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '10px', 'fontFamily': 'Courier New, monospace'}
            ),
            html.Label('Выберите статус заказа:', style={'color': colors['text'],'fontFamily': 'Courier New, monospace'}),
            dcc.Dropdown(
                id='customer-order-status-dropdown',
                options=[{'label': 'Все', 'value': 'ALL'}] +
                        [{'label': status, 'value': status} for status in df['order_status'].unique()],
                value=['delivered'],
                multi=True,
                style={'color': colors['text'], 'backgroundColor': colors['background'], 'marginBottom': '20px', 'fontFamily': 'Courier New, monospace'}
            ),
            dcc.DatePickerRange(
                id='customer-date-picker-range',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                style={'color': colors['text'], 'fontFamily': 'Courier New, monospace'}
            ),
            dcc.Graph(id='customer-category-purchases-graph'),
        ], style={'marginBottom': '20px', 'flex': '50%'}),
    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between'}),
    dcc.Store(id='selected-state', storage_type='session'),
])

@app.callback(
    Output('selected-state', 'data'),
    [Input('state-map', 'clickData'), Input('reset-state-button', 'n_clicks')],
    [State('selected-state', 'data')]
)
def set_or_reset_selected_state(clickData, n_clicks, selected_state_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'state-map' and clickData:
        state_id = clickData['points'][0]['location']
        return {'state': state_id}
    elif trigger_id == 'reset-state-button' and n_clicks:
        return {}
    return selected_state_data

@app.callback(
    Output('seller-state-dropdown', 'value'),
    Output('customer-state-dropdown', 'value'),
    [Input('selected-state', 'data')]
)
def update_dropdowns(selected_state_data):
    if selected_state_data and 'state' in selected_state_data:
        selected_state = selected_state_data['state']
        return selected_state, selected_state
    else:
        return 'ALL', 'ALL'

@app.callback(
    Output('state-map', 'figure'),
    [
        Input('map-type-selector', 'value'),
        Input('seller-state-dropdown', 'value'),
        Input('customer-state-dropdown', 'value'),
        Input('order-status-dropdown', 'value'),
        Input('customer-order-status-dropdown', 'value'),
        Input('seller-date-picker-range', 'start_date'),
        Input('seller-date-picker-range', 'end_date'),
        Input('customer-date-picker-range', 'start_date'),
        Input('customer-date-picker-range', 'end_date'),
        Input('selected-state', 'data')
    ]
)
def update_map(map_type, seller_states, customer_states, seller_statuses, customer_statuses, 
               seller_start_date, seller_end_date, customer_start_date, customer_end_date, 
               selected_state_data):
    seller_states = seller_states if isinstance(seller_states, list) else [seller_states]
    customer_states = customer_states if isinstance(customer_states, list) else [customer_states]
    selected_state = selected_state_data.get('state') if selected_state_data else None
    if map_type == 'sellers':
        filtered_data = df if 'ALL' in seller_states else df[df['seller_state'].isin(seller_states)]
        filtered_data = filtered_data if 'ALL' in seller_statuses else filtered_data[filtered_data['order_status'].isin(seller_statuses)]
        filtered_data = filtered_data if not seller_start_date else filtered_data[filtered_data['order_purchase_timestamp'] >= pd.to_datetime(seller_start_date)]
        filtered_data = filtered_data if not seller_end_date else filtered_data[filtered_data['order_purchase_timestamp'] <= pd.to_datetime(seller_end_date)]
        
        map_data = filtered_data.groupby('seller_state').size().reset_index(name='count').rename(columns={'seller_state': 'id'})
        map_data = all_states_df.merge(map_data, on='id', how='left').fillna(0).rename(columns={'count_y':'count'})
        color_column = 'count'  
    else:
        filtered_data = df if 'ALL' in customer_states else df[df['customer_state'].isin(customer_states)]
        filtered_data = filtered_data if 'ALL' in customer_statuses else filtered_data[filtered_data['order_status'].isin(customer_statuses)]
        filtered_data = filtered_data if not customer_start_date else filtered_data[filtered_data['order_purchase_timestamp'] >= pd.to_datetime(customer_start_date)]
        filtered_data = filtered_data if not customer_end_date else filtered_data[filtered_data['order_purchase_timestamp'] <= pd.to_datetime(customer_end_date)]
        
        map_data = filtered_data.groupby('customer_state').size().reset_index(name='count').rename(columns={'customer_state': 'id'})
        map_data = all_states_df.merge(map_data, on='id', how='left').fillna(0).rename(columns={'count_y':'count'})
        color_column = 'count' 
    entity_type = 'продавцов' if map_type == 'sellers' else 'покупателей'
    map_data['hover_info'] = "Штат: " + map_data['id'] + "<br>Количество " + entity_type + ": " + map_data['count'].astype(str)

    if selected_state:
        single_state_data = map_data[map_data['id'] == selected_state]
        fig = px.choropleth(
            single_state_data, 
            geojson=brazil, 
            locations='id',
            color=color_column,
            color_continuous_scale='burgyl',
            custom_data=['hover_info'],
            featureidkey="properties.sigla",
            projection="mercator"
        )
        
        fig.update_traces(hovertemplate='%{customdata[0]}',)
        fig.update_geos(fitbounds="locations", visible=True)
        fig.update_layout(
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white", 
                font_size=16, 
                font_family="Courier New, monospace"))
        annotation_text = f"<b>{single_state_data['hover_info'].iloc[0]}<b>"
        fig.add_annotation(
            x=0.48,
            y=1.18,
            xref="paper",
            yref="paper",
            text=annotation_text, 
            showarrow=False,
            font=dict(
                family='Courier New, monospace',
                size=16,
                color="black"
            ),
            align="left",
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        )
    else:
        fig = px.choropleth(
            map_data, 
            geojson=brazil, 
            locations='id',
            color=color_column,
            color_continuous_scale='burgyl',
            featureidkey="properties.sigla",
            custom_data=['hover_info'],
            projection="mercator"
        )
        fig.update_traces(
            hovertemplate='%{customdata[0]}',)

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white", 
            font_size=16, 
            font_family="Courier New, monospace"
        )
)
    return fig



@app.callback(
    Output('reset-state-button', 'hidden'),
    [Input('selected-state', 'data')]
)
def toggle_reset_button_visibility(selected_state_data):
    if selected_state_data and 'state' in selected_state_data:
        return False
    return True

@app.callback(
    Output('seller-category-sales-graph', 'figure'),
    [
        Input('seller-state-dropdown', 'value'),
        Input('order-status-dropdown', 'value'),
        Input('seller-date-picker-range', 'start_date'),
        Input('seller-date-picker-range', 'end_date')
    ]
)
def update_seller_graph(selected_states, selected_statuses, start_date, end_date):
    selected_states = selected_states if isinstance(selected_states, list) else [selected_states]
    filtered_data = df
    if 'ALL' not in selected_states:
        filtered_data = filtered_data[filtered_data['seller_state'].isin(selected_states)]
    if 'ALL' not in selected_statuses:
        filtered_data = filtered_data[filtered_data['order_status'].isin(selected_statuses)]
    if start_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] <= pd.to_datetime(end_date)]
    
    category_counts = filtered_data['product_category_name_english'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    category_counts = category_counts.sort_values('count', ascending=True)
    
    fig_seller = px.bar(category_counts, y='category', x='count',
                        title='Распределение категорий продаж по штатам',
                        labels={'count': 'Количество продаж', 'category': 'Категория'},
                        color_discrete_sequence=['#c8586c'])
    fig_seller.update_layout(
        font=dict(family="Courier New, monospace", size=13),
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        plot_bgcolor=colors['plot_background'],
        height=1500
    )
    return fig_seller

@app.callback(
    Output('customer-category-purchases-graph', 'figure'),
    [
        Input('customer-state-dropdown', 'value'),
        Input('customer-order-status-dropdown', 'value'),
        Input('customer-date-picker-range', 'start_date'),
        Input('customer-date-picker-range', 'end_date')
    ]
)
def update_customer_graph(selected_states, selected_order_statuses, start_date, end_date):
    filtered_data = df
    selected_states = selected_states if isinstance(selected_states, list) else [selected_states]
    if 'ALL' not in selected_states:
        filtered_data = filtered_data[filtered_data['customer_state'].isin(selected_states)]
    if 'ALL' not in selected_order_statuses:
        filtered_data = filtered_data[filtered_data['order_status'].isin(selected_order_statuses)]
    if start_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered_data = filtered_data[filtered_data['order_purchase_timestamp'] <= pd.to_datetime(end_date)]
    category_counts = filtered_data['product_category_name_english'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    category_counts = category_counts.sort_values('count', ascending=True)
    
    fig_customer = px.bar(category_counts, y='category', x='count',
                          title='Распределение категорий покупок по штатам',
                          labels={'count': 'Количество покупок', 'category': 'Категория'},
                          color_discrete_sequence=['#70284a'])
    fig_customer.update_layout(
        font=dict(family="Courier New, monospace", size=13),
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        plot_bgcolor=colors['plot_background'],
        height=1500  
    )
    return fig_customer

if __name__ == '__main__':
    app.run_server(debug=True) 
