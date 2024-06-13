from dash import Dash, dcc, html, Input, Output, callback, State
import numpy as np
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

from fetchData import getBaseData, getBatteryData, generateBatData
from generateDiagramms import grossVerbraucher, batterieAnalyse, PVErzeugung_Verbrauch, generateCenterTable1, generateCenterTable2


def getCutOffDate(date):
    '''
    Get datetime Object from numDateDropdownList according to date (String) Input
    '''
    index = [idx for idx, s in enumerate(dateDropdownList) if date in s]
    return numDateDropdownList[index[0]]

def getBatLimit(bat):
    '''
    Get numerical bat Capacity from batMax List according to bat (BatteryName) Input
    '''
    index = [idx for idx, s in enumerate(batterieDropdownList) if bat in s]
    return batMax[index[0]]

def getBatPrice(bat):
    '''
    Get numerical bat Price from batMax List according to bat (BatteryName) Input
    '''
    index = [idx for idx, s in enumerate(batterieDropdownList) if bat in s]
    return batPrice[index[0]]


#Generate Battery Data (fetchData)
batCaption, batMax, batPrice = getBatteryData()

#Generate Dropdown Lists
dateDropdownList = ["alle Daten", "letzte Woche", "letzter Monat", "letztes Halbjahr", "letztes Jahr"]
numDateDropdownList = [datetime(1999, 1, 1), datetime.today() - timedelta(days=7), datetime.today() - timedelta(days=30), datetime.today() - timedelta(days=180), datetime.today() - timedelta(days=365)]
batterieDropdownList = batCaption
batterieEffDropdownList = list(range(0, 101, 5))
strPrDropdownList = np.arange(0.05, 2.5, 0.05).round(2)
strVerDropdownList = np.arange(0.05, 2.5, 0.05).round(2)

#Get Main Data according to default Dropdown selection
main_data = getBaseData(batMax, batterieEffDropdownList)


#Create App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.css.append_css({'external_url': '/assets/styling.css'})

modalString1 = "Das Dashboard wurde im Rahmen des Moduls und «Dashboard Design» an der FHGR erstellt. Die Autoren sind Mauro Stoffel und Marc-Alexander Iten."
modalString2 = "Sämtliche verwendete Daten wurden durch das Monitoring System von Herr Itens Photovoltaik Anlage aufgezeichnet und über eine selbst entwicklete API zur Verfügung gestellt."

modalButton = html.Div(
    [
        dbc.Button("Impressum und Quellen", id="open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Impressum und Quellen")),
                dbc.ModalBody([html.Div(modalString1), html.Div(modalString2)]),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)


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
                                html.Div("Wirtschaftlichkeitsberechnung", className='subTitle')
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
                                ], className='ddbig'), className='row1Col', width=12, lg=6),
                                dbc.Col(html.Div([
                                    html.Div('Batterie', className='DDtext'),
                                    dcc.Dropdown(batterieDropdownList, batterieDropdownList[0], id='Batterie-dropdown', clearable=False, className='row1DD')
                                ], className='ddbig'), className='row1Col', width=12, lg=6),
                            ]),
                            dbc.Row([
                                dbc.Col(html.Div([
                                    html.Div('Batterie Effizienz in [%]', className='DDtext'),
                                    dcc.Dropdown(batterieEffDropdownList, batterieEffDropdownList[-3],
                                                 id='batEff-dropdown', clearable=False, className='row1DD')
                                ], className='ddbig'), className='row1Col', width=12, lg=6),
                                dbc.Col(html.Div([
                                    html.Div('Strompreis', className='DDtext'),
                                    dcc.Dropdown(strPrDropdownList, strPrDropdownList[16], id='StrPr-dropdown',
                                                 clearable=False, className='row1DD')
                                ], className='ddsmall'), className='row1Col', width=12, lg=3),
                                dbc.Col(html.Div([
                                    html.Div('Stromvergütung', className='DDtext'),
                                    dcc.Dropdown(strVerDropdownList, strVerDropdownList[14], id='StrVerg-dropdown',
                                                 clearable=False, className='row1DD')
                                ], className='ddsmall'), className='row1Col', width=12, lg=3),
                            ]),
                        ]
                    ),
                    xs=12, sm=12, md=12, lg=12, xl=12, xxl=7,
                ),
                dbc.Col(
                    html.Div(
                        className='row1Div',
                        children=[
                            modalButton
                        ]
                    ), align="center",
                    xs=12, sm=12, md=12, lg=12, xl=12, xxl=1,
                )
            ]
        ),
    ################################################################
    # Second Row
    ################################################################
        dcc.Tabs([
            dcc.Tab(label='Übersicht und Ammortisationsrechnung', className='tab_style', selected_className='tab_style--selected', children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                className='row2Div',
                                style={'minWidth': '525px'},
                                children=[
                                    dbc.Row([
                                        dbc.Col(html.Div([
                                            html.Div('Batterieanalyse', className='graphText'),
                                            dcc.Graph(id="bat", figure=batterieAnalyse(main_data, batMax[0]), className='row2bat')
                                        ], className= 'batDiv')),
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
                                                generateCenterTable1(main_data, strVerDropdownList[14], strPrDropdownList[16], getBatPrice(batterieDropdownList[0]), batterieEffDropdownList[-3], batMax[0]), id='topTab', className='topTab'),
                                            dbc.Table(
                                                generateCenterTable2(main_data, strVerDropdownList[14], strPrDropdownList[16], getBatPrice(batterieDropdownList[0]), batterieEffDropdownList[-3], batMax[0]), id='botTab')
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
                                            dcc.Graph(id="pve", figure=PVErzeugung_Verbrauch(main_data), className='row2graph')
                                        ])),
                                    ])
                                ]
                            ),
                            xs=12, sm=12, md=12, lg=12, xl=12, xxl=6,
                        )
                    ]
                )]),
        ################################################################
        # Third Row
        ################################################################
            dcc.Tab(label='Batterie Simulation', className='tab_style', selected_className='tab_style--selected', children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                className='row3Div',
                                style={'minWidth': '300px'},
                                children=[
                                    dbc.Row([
                                        dbc.Col(html.Div([
                                            html.H4('Grossverbraucher und Batterie-Auslastung', className='graphText'),
                                            dcc.Graph(id="grossV", figure=grossVerbraucher(main_data))
                                        ])),

                                    ])
                                ]
                            ),
                            xs=12, sm=12, md=12, lg=12, xl=12, xxl=12,
                        )
                    ]
                )])])
    ]
)


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"),
     Input("close", "n_clicks")],
    [State("modal", "is_open")],
    )
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

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

    figureGV = grossVerbraucher(json_data)
    figureGV.update_layout()

    figureBat = batterieAnalyse(json_data,  getBatLimit(batType))
    figureBat.update_layout()

    topTable = generateCenterTable1(json_data, StrVerg, StrPr, getBatPrice(batType), batEff, getBatLimit(batType))
    botTable = generateCenterTable2(json_data, StrVerg, StrPr, getBatPrice(batType), batEff, getBatLimit(batType))

    return figureGV, figureBat, topTable, botTable



@callback(
    Output("pve", "figure"),
    Input("zeitraum-dropdown","value"),
)
def update_graphs_noBattery(date):
    mask = (main_data['realDatum'] > getCutOffDate(date))
    json_data = main_data[mask]

    figurePVE = PVErzeugung_Verbrauch(json_data)
    figurePVE.update_layout()

    return figurePVE



if __name__ == '__main__':
    app.run_server(debug=False)