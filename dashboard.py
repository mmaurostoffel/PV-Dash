from dash import Dash, dcc, html, Input, Output, callback
import numpy as np
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

from fetchData import getBaseData, getBatteryData, generateBatData
from generateDiagramms import grossVerbraucher2, überproduktion, batterie, PVErzeugung_Verbrauch2, generateCenterTable1, \
    generateCenterTable2


def getCutOffDate(date):
    index = [idx for idx, s in enumerate(dateDropdownList) if date in s]
    return numDateDropdownList[index[0]]

def getBatLimit(bat):
    index = [idx for idx, s in enumerate(batterieDropdownList) if bat in s]
    return batMax[index[0]]

def getBatPrice(bat):
    index = [idx for idx, s in enumerate(batterieDropdownList) if bat in s]
    return batPrice[index[0]]


#Generate Battery Data (fetchData)
batCaption, batMax, batPrice = getBatteryData()

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
                                    dbc.Table(
                                        generateCenterTable1(main_data, strVerDropdownList[3], strPrDropdownList[16], getBatPrice(batterieDropdownList[0])), id='topTab', className='topTab'),
                                    dbc.Table(
                                        generateCenterTable2(main_data, strVerDropdownList[3], strPrDropdownList[16], getBatPrice(batterieDropdownList[0])), id='botTab')
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
                                    dcc.Graph(id="pve", figure=PVErzeugung_Verbrauch2(main_data), className='row2graph')
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