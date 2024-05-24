import json

from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta


def getBaseData(batMax, batterieEffDropdownList):
    url = "https://iten-web.ch/batteriespeicher/api/data_as_json.php"
    main_data = pd.read_json(url)
    main_data.to_csv('dok/mainData.csv', index=False)

    # Generate Additional Data
    main_data = main_data[pd.to_numeric(main_data['PVErtrag'], errors='coerce').notnull()]
    main_data = main_data.astype(
        {"Datum": "string", "PVErtrag": "Int64", "Netz": "Int32", "Bezug": "Int32", "Einspeisung": "Int32",
         "Verbrauch": "Int32"})
    main_data.insert(1, "10 kWh Linie", 10000, False)
    main_data.insert(1, "Produktion", main_data['Netz'] > 0, False)
    main_data.insert(1, "Sum Erzeugung", main_data['Einspeisung'].cumsum(), False)
    main_data.insert(1, "Sum Verbrauch", main_data['Verbrauch'].cumsum(), False)
    realDatetime = pd.to_datetime(main_data['Datum'])
    main_data.insert(1, "realDatum", realDatetime, False)
    realDate = pd.to_datetime(main_data['Datum'])
    main_data.insert(1, "realDatumOnlyDate", pd.to_datetime(main_data['realDatum']).dt.date, False)
    main_data.insert(1, "batData", generateBatData(main_data, batMax[0], batterieEffDropdownList[-3] / 100), False)

    return main_data


def getBatteryData():
    batCaption = []
    batMax = []
    batPrice = []

    url = "https://iten-web.ch/batteriespeicher/api/batteries"
    batdata = pd.read_json(url)
    batdata.to_csv('dok/batData.csv', index=False)

    batData = batdata['response']
    for data in batData:
        batCaption.append(data['caption'])
        batMax.append(data['max'])
        batPrice.append(data['price'])
    return batCaption, batMax, batPrice


    batData = batdata['response']
    for data in batData:
        data = eval(data)

        batCaption.append(data['caption'])
        batMax.append(data['max'])
        batPrice.append(data['price'])
    return batCaption, batMax, batPrice

def grossVerbraucher2(json_data):
    fig = go.Figure()
    #tozeroy
    #tonexty
    fig.add_trace(go.Scatter(name="PV-Ertrag", x=json_data['Datum'], y=json_data['PVErtrag'], fill='tonexty', mode= 'none'))  # fill down to xaxis
    fig.add_trace(go.Scatter(name="Verbrauch", x=json_data['Datum'], y=json_data['Verbrauch'], fill='tozeroy', mode= 'none'))
    fig.add_trace(go.Scatter(name="Batterie Auslastung", x=json_data['Datum'], y=json_data['batData'], fill='tozeroy', mode= 'none'))# fill to trace0 y
    fig.add_trace(go.Scatter(name="10 kWh Linie", x=json_data['Datum'], y=json_data['10 kWh Linie']))
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ))
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))

    return fig

def überproduktion(json_data):
    color = ['red', 'blue']
    legend = ['Tage mit Überproduktion', 'Tage ohne Überproduktion']
    fig = px.pie(json_data.groupby(by=["Produktion"]).count(), values='PVErtrag', names=legend, color= color)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_layout(margin_pad=0)
    fig.update_layout(height=400)
    fig.update_traces(textinfo='value')
    return fig

def batterie(json_data, threshold):
    x = json_data.groupby(by='realDatumOnlyDate').max()
    y = x.groupby(by='batData').count()['Datum']
    numOfFullDays = 0
    if threshold in y:
        numOfFullDays = y[threshold]

    numRestDays = y.sum() - numOfFullDays
    color = ['red','blue']
    legend = ['Tage mit Vollauslastung', 'Tage ohne Vollauslastung']
    fig = px.pie(values=[numOfFullDays, numRestDays], names= legend, color=color)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_layout(margin_pad=0)
    fig.update_layout(legend_traceorder="reversed")
    fig.update_layout(height=400)
    fig.update_traces(textinfo='value')
    return fig

def PVErzeugung_Verbrauch2(json_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Erzeugung", x=json_data['Datum'], y=json_data['Sum Erzeugung'], fill='tozeroy', mode='none'))
    fig.add_trace(go.Scatter(name="Verbrauch", x=json_data['Datum'], y=json_data['Sum Verbrauch'], fill='tozeroy', mode='none'))
    #fig = px.area(json_data, x='Datum', y=['Sum Erzeugung', 'Sum Verbrauch'])
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ))
    fig.update_layout(height=400)
    return fig

def generateCenterTable1(json_data, StrVerg, StrPr, BatPrice):
    gesEn, Verg, Einsp, FinErf, Ansch, Amort = generateCenterData(json_data, StrVerg, StrPr, BatPrice)

    text = round(gesEn,1),' kWh'
    row1 = html.Tr([
        html.Td("gesparte Energie", className = 'tableText'),
        html.Td(text, className = 'tableNum')
    ])

    text = round(Verg,1),' CHF'
    row2 = html.Tr([
        html.Td("Vergütung", className = 'tableText'),
        html.Td(text, className = 'tableNum')
    ])

    text = round(Einsp,1),' CHF'
    row3 = html.Tr([
        html.Td("Einsparung", className = 'tableText'),
        html.Td(text, className = 'tableNumSec')
    ])

    text = round(FinErf,1),' CHF'
    row4 = html.Tr([
        html.Td("Finanzieller Erfolg", className = 'tableText'),
        html.Td(text, className = 'tableNumLast')
    ])

    table_body = [html.Tbody([row1, row2, row3, row4])]
    return table_body

def generateCenterTable2(json_data, StrVerg, StrPr, BatPrice):
    gesEn, Verg, Einsp, FinErf, Ansch, Amort = generateCenterData(json_data, StrVerg, StrPr, BatPrice)

    if Amort < 10:
        col = 'greenyellow'
    else:
        col = 'crimson'
    print(col)

    text = round(Ansch,1), ' CHF'
    row5 = html.Tr([
        html.Td("Anschaffung", className = 'tableText'),
        html.Td(text, className = 'tableNum')
    ])

    text = round(Amort,1), ' Jahre'
    row6 = html.Tr([
        html.Td("Amortisation", className = 'tableText'),
        html.Td(html.Div(text, className = 'tableNumAmort', style={'backgroundColor': col}))
    ])

    #background-color: greenyellow;
    #background-color: crimson;

    table_body = [html.Tbody([row5, row6])]
    return table_body



def getCutOffDate(date):
    index = [idx for idx, s in enumerate(dateDropdownList) if date in s]
    return numDateDropdownList[index[0]]

def getBatLimit(bat):
    index = [idx for idx, s in enumerate(batterieDropdownList) if bat in s]
    return batMax[index[0]]

def getBatPrice(bat):
    index = [idx for idx, s in enumerate(batterieDropdownList) if bat in s]
    return batPrice[index[0]]

def generateBatData(json_data, batLimit, batEff):
    #json_data.insert(1, "batteryNoCap", json_data['Netz'].cumsum(), False)
    lastVal = 0
    batData = []
    for val in json_data['Netz']:
        if val <0:
            curr = (lastVal + val*-1 * batEff) * 0.01
        else:
            curr = (lastVal + val * -1) * 0.01

        if curr > batLimit:
            curr = batLimit
        elif curr < 0:
            curr = 0
        lastVal = curr
        batData.append(np.round(curr, 2))
    #print(batData)
    return batData

def generateCenterData(json_data, StrVerg, StrPr, BatPrice):
    #TODO Berechnung aus BatData
    gesEn = 1136 #kWh

    Verg = gesEn * StrVerg *-1

    Einsp = gesEn * StrPr

    FinErf = Verg + Einsp

    Ansch = BatPrice

    Amort = Ansch / FinErf

    return gesEn, Verg, Einsp, FinErf, Ansch, Amort


#Generate Data
batCaption, batMax, batPrice = getBatteryData()

#Date Dropdown mit Woche
#dateDropdownList = ["alle Daten", "letzte Woche", "letzter Monat", "letztes Jahr"]
#numDateDropdownList = [datetime(1999, 1, 1), datetime.today() - timedelta(days=7), datetime.today() - timedelta(days=30), datetime.today() - timedelta(days=365)]

#Date Dropdown ohne Woche
#dateDropdownList = ["alle Daten",  "letzter Monat", "letztes Jahr"]
#numDateDropdownList = [datetime(1999, 1, 1), datetime.today() - timedelta(days=30), datetime.today() - timedelta(days=365)]

#Date Dropdown mit Halbjahr
dateDropdownList = ["alle Daten", "letzte Woche", "letzter Monat", "letztes Halbjahr", "letztes Jahr"]
numDateDropdownList = [datetime(1999, 1, 1), datetime.today() - timedelta(days=7), datetime.today() - timedelta(days=30), datetime.today() - timedelta(days=180), datetime.today() - timedelta(days=365)]

batterieDropdownList = batCaption
batterieEffDropdownList = list(range(0, 101, 5))
strPrDropdownList = np.arange(0.05, 2.5, 0.05).round(2)
strVerDropdownList = np.arange(0.05, 2.5, 0.05).round(2)

main_data = getBaseData(batMax, batterieEffDropdownList)

#Create App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.css.append_css({'external_url': '/assets/styling.css'})

app.layout = html.Div(
    ################################################################
    # First Row
    ################################################################
    style={'backgroundColor': 'lightblue', 'min-height': '100vh', 'padding': '20px'},
    children=[
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        className='row1Div',
                        style={'minWidth': '480px'},
                        children=[
                            dbc.Row([
                                html.Div("Batteriespeicher", className='mainTitle'),
                                html.Div("Wirtschaftlichkeitsberechnung", className='subTitle'),
                            ])
                        ]
                    ),
                    xs=4, sm=4, md=4, lg=4, xl=4, xxl=4
                ),
                dbc.Col(
                    html.Div(
                        className='row1Div',
                        children=[
                            dbc.Row([
                                dbc.Col(html.Div([
                                    html.Div('Zeitraum', className='DDtext'),
                                    dcc.Dropdown(dateDropdownList, dateDropdownList[0], id='zeitraum-dropdown', clearable=False, className='row1DD')
                                ], className='ddbig'), className='row1Col', width=12, lg=3),
                                dbc.Col(html.Div([
                                    html.Div('Batterie', className='DDtext'),
                                    dcc.Dropdown(batterieDropdownList, batterieDropdownList[0], id='Batterie-dropdown', clearable=False, className='row1DD')
                                ], className='ddbig'), className='row1Col', width=12, lg=3),
                                dbc.Col(html.Div([
                                    html.Div('Batterie Effizienz in [%]', className='DDtext'),
                                    dcc.Dropdown(batterieEffDropdownList, batterieEffDropdownList[-3], id='batEff-dropdown', clearable=False, className='row1DD')
                                ], className='ddbig'), className='row1Col', width=12, lg=3),
                                dbc.Col(html.Div([
                                    html.Div('Strompreis', className='DDtext'),
                                    dcc.Dropdown(strPrDropdownList, strPrDropdownList[16], id='StrPr-dropdown', clearable=False, className='row1DD' )
                                ], className='ddsmall'), className='row1Col', width=12, lg=1),
                                dbc.Col(html.Div([
                                    html.Div('Stromvergütung', className='DDtext'),
                                    dcc.Dropdown(strVerDropdownList, strVerDropdownList[3], id='StrVerg-dropdown', clearable=False, className='row1DD' )
                                ], className='ddsmall'), className='row1Col', width=12, lg=1),
                            ])
                        ]
                    ),
                    xs=12, sm=12, md=12, lg=12, xl=12, xxl=8,
                )
            ]
        ),
    ################################################################
    # Second Row
    ################################################################
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        className='row2Div',
                        style={'minWidth': '525px'},
                        children=[
                            dbc.Row([
                                dbc.Col(html.Div([
                                    html.Div('Tage mit Überproduktion', className='graphText'),
                                    dcc.Graph(id="üprod", figure=überproduktion(main_data), className='row2pie')
                                ], className= 'pieDiv')),
                                dbc.Col(html.Div([
                                    html.Div('Batterie Auslastung', className='graphText'),
                                    dcc.Graph(id="bat", figure=batterie(main_data, batMax[0]), className='row2pie'),
                                ], className= 'pieDiv'))
                            ])
                        ]
                    ),
                    xs=12, sm=12, md=12, lg=12, xl=8, xxl=4,
                ),

                dbc.Col(
                    html.Div(
                        className='row2Div',
                        style={
                            'minWidth': '250px'},
                        children=[
                            dbc.Row([
                                dbc.Col(html.Div([
                                    dbc.Table(generateCenterTable1(main_data, strVerDropdownList[3], strPrDropdownList[16], getBatPrice(batterieDropdownList[0])), id='topTab', className='topTab'),
                                    dbc.Table(generateCenterTable2(main_data, strVerDropdownList[3], strPrDropdownList[16], getBatPrice(batterieDropdownList[0])), id='botTab')
                                ])),
                            ])
                        ]
                    ),
                    xs=12, sm=12, md=12, lg=12, xl=4, xxl=2,
                ),

                dbc.Col(
                    html.Div(
                        className='row2Div',
                        style={
                            'minWidth': '525px'},
                        children=[
                            dbc.Row([
                                dbc.Col(html.Div([
                                    html.Div('PV-Erzeugung und Verbrauch', className='graphText'),
                                    dcc.Graph(id="pve", figure=PVErzeugung_Verbrauch2(main_data),className='row2graph')
                                ])),
                            ])
                        ]
                    ),
                    xs=12, sm=12, md=12, lg=12, xl=12, xxl=6,
                )
            ]
        ),
    ################################################################
    # Third Row
    ################################################################
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        style={
                            'backgroundColor': 'white',
                            'borderRadius': '10px',
                            'padding': '20px',
                            'marginBottom': '20px',
                            'minWidth': '300px'
                        },
                        children=[
                            dbc.Row([
                                dbc.Col(html.Div([
                                    html.H4('Grossverbraucher und Batterie-Auslastung', className='graphText'),
                                    dcc.Graph(id="grossV", figure=grossVerbraucher2(main_data))
                                ])),

                            ])
                        ]
                    ),
                    xs=12, sm=12, md=12, lg=12, xl=12, xxl=12,
                )
            ]
        )
    ]
)

@callback(
    Output("grossV", "figure"),
    Output("bat", "figure"),
    Output("topTab", "children"),
    Output("botTab", "children"),
    Input("zeitraum-dropdown","value"),
    Input("Batterie-dropdown","value"),
    Input("batEff-dropdown","value"),
    Input("StrPr-dropdown","value"),
    Input("StrVerg-dropdown","value")
    )
def update_graphs_withBattery(date, batType, batEff, StrPr, StrVerg):
    print(date, batType, batEff, StrPr, StrVerg)

    newBatData = generateBatData(main_data, getBatLimit(batType), batEff)
    main_data.drop("batData", axis=1, inplace=True)
    main_data.insert(1, "batData", newBatData, False)

    mask = (main_data['realDatum'] > getCutOffDate(date))
    json_data = main_data[mask]


    figureGV = grossVerbraucher2(json_data)
    figureGV.update_layout()

    figureBat = batterie(json_data, getBatLimit(batType))
    figureBat.update_layout()

    topTable = generateCenterTable1(json_data, StrVerg, StrPr, getBatPrice(batType))
    botTable = generateCenterTable2(json_data, StrVerg, StrPr, getBatPrice(batType))

    return figureGV, figureBat, topTable, botTable



@callback(
    Output("pve", "figure"),
    Output("üprod", "figure"),
    Input("zeitraum-dropdown","value"),
)
def update_graphs_noBattery(date):
    mask = (main_data['realDatum'] > getCutOffDate(date))
    json_data = main_data[mask]

    figurePVE = PVErzeugung_Verbrauch2(json_data)
    figurePVE.update_layout()

    figureÜber = überproduktion(json_data)
    figureÜber.update_layout()

    return figurePVE, figureÜber



if __name__ == '__main__':
    app.run_server(debug=False)



'''
app.layout = html.Div([
    ################################################################
    #First Row
    ################################################################
    dbc.Row([
        dbc.Col([
            dcc.Markdown(tileMarkdown)
        ], width=3, id= 'mainCompTitle'),

        dbc.Col([
            html.H4('Zeitraum'),
            dcc.Dropdown(dateDropdownList, dateDropdownList[0], id='zeitraum-dropdown', clearable=False)
        ], width=2, id= 'mainCompDDZeit'),

        dbc.Col([
            html.H4('Batterie'),
            dcc.Dropdown(batterieDropdownList, batterieDropdownList[0], id='Batterie-dropdown', clearable=False)
        ], width=2, id= 'mainCompDDBat'),

        dbc.Col([
            html.H4('Batterie Effizienz in [%]'),
            dcc.Dropdown(batterieEffDropdownList, batterieEffDropdownList[-3], id='batEff-dropdown', clearable=False)
        ], width=2, id= 'mainCompDDBatEff'),

        dbc.Col([
            html.H4('Strompreis'),
            dcc.Dropdown(strPrDropdownList, strPrDropdownList[16], id='StrPr-dropdown', clearable=False)
        ], width=1, id= 'mainCompDDStrPr'),

        dbc.Col([
            html.H4('Stromvergütung'),
            dcc.Dropdown(strVerDropdownList, strVerDropdownList[3], id='StrVerg-dropdown', clearable=False)
        ], id= 'mainCompDDStrV'),
    ]),

    ################################################################
    # Second Row
    ################################################################
    dbc.Row([
        dbc.Col([
            html.H4('Tage mit Überproduktion', style={'textAlign': 'center'}),
            dcc.Graph(id="üprod", figure=überproduktion(main_data))
        ], width=2, id= 'mainCompPie1'),

        dbc.Col([
            html.H4('Batterie', style={'textAlign': 'center'}),
            dcc.Graph(id="bat", figure=batterie(main_data, batMax[0])),
        ],align="center", width=2, id= 'mainCompPie2'),

        dbc.Col([
            dbc.Table(generateCenterTable(main_data, strVerDropdownList[3], strPrDropdownList[16], getBatPrice(batterieDropdownList[0])), id='tab')
        ],align="center", id= 'mainCompTable'),

        dbc.Col([
            html.H4('PV-Erzeugung und Verbrauch', style={'textAlign': 'center'}),
            dcc.Graph(id="pve", figure=PVErzeugung_Verbrauch2(main_data))
        ], width=6, id= 'mainCompPV')
    ]),

    ################################################################
    # Third Row
    ################################################################
    dbc.Row([
        html.H4('Grossverbraucher und Batterie-Auslastung', style={'textAlign': 'center'}),
        dcc.Graph(id="grossV", figure=grossVerbraucher2(main_data))
    ], id= 'mainCompGross'),
], style={'backgroundColor':'white'})
'''