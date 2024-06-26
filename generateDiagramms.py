from dash import html
from plotly import graph_objects as go, express as px
import pandas as pd
from scipy import signal


def grossVerbraucher(json_data):
    '''
    Generate the big diagramm at the bottom of the page
    '''
    fig = go.Figure()
    #tozeroy
    #tonexty
    fig.add_trace(go.Scatter(name="PV-Ertrag", x=json_data['Datum'], y=signal.savgol_filter(json_data['PVErtrag'],53,3), fill='tonexty', mode= 'none',))  # fill down to xaxis
    fig.add_trace(go.Scatter(name="Verbrauch", x=json_data['Datum'], y=signal.savgol_filter(json_data['Verbrauch'],53,3), fill='tozeroy', mode= 'none'))
    fig.add_trace(go.Scatter(name="Batterie Auslastung", x=json_data['Datum'], y=signal.savgol_filter(json_data['batData'], 53, 3), fill='tozeroy', mode= 'none'))# fill to trace0 y
    fig.add_trace(go.Scatter(name="10 kWh Linie", x=json_data['Datum'], y=json_data['10 kWh Linie']))
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=20)
    ))
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    fig.update_layout(xaxis_title="Datum", yaxis_title="Erträge & Verbäuche [kWh]")
    fig.update_layout(height=600)
    fig.update_xaxes(title_font_size=20)
    fig.update_yaxes(title_font_size=20)
    fig.update_xaxes(tickfont_size=20)
    fig.update_yaxes(tickfont_size=20)
    return fig


def batterieAnalyse(json_data, threshold):
    '''
    Generate the first pie Chart for the power consumption diagram.
    '''
    tempData = json_data.groupby(by=["Produktion"])['Datum'].count()

    x = json_data.groupby(by='realDatumOnlyDate').max()
    y = x.groupby(by='batData').count()['Datum']
    bAll = y.sum()

    if tempData[tempData > threshold].empty:
        üTrue = 0
        üFalse = bAll
    else:
        üFalse = tempData.iloc[0]
        üTrue = tempData.iloc[1]
        üAll = üTrue + üFalse
        üTrue = round(üTrue/üAll * bAll, 0)
        üFalse = round(üFalse/üAll * bAll, 0)

    bTrue = 0
    if threshold in y:
        bTrue = y[threshold]

    bFalse = bAll - bTrue
    bTrue = round(bTrue, 0)
    bFalse = round(bFalse, 0)



    colors = {'Wahr': 'rgba(0,0,255,0.3)',
              'Falsch': 'rgba(255,0,0,0.3)'}
    x = ['Tage mit<br>Überproduktion', 'Tage mit voller<br>Batterieauslastung']
    fig = go.Figure(data=[
        go.Bar(name='Wahr', x=x, y=[üTrue, bTrue], marker_color=colors['Wahr']),
        go.Bar(name='Falsch', x=x, y=[üFalse, bFalse], marker_color=colors['Falsch']),
    ])
    fig.update_layout(barmode='stack')
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font = dict(size=20)
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_layout(margin_pad=0)
    fig.update_layout(height=500)
    fig.update_layout(yaxis_title='Tage')
    fig.update_yaxes(title_font_size=20)
    fig.update_xaxes(tickfont_size=20)
    fig.update_yaxes(tickfont_size=15)
    return fig


def PVErzeugung_Verbrauch(json_data):
    '''
    Generate the area Plot for the PV-Ertrag and Verbrauch
    '''
    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Erzeugung", x=json_data['Datum'], y=json_data['Sum Erzeugung'], fill='tozeroy', mode='none'))
    fig.add_trace(go.Scatter(name="Verbrauch", x=json_data['Datum'], y=json_data['Sum Verbrauch'], fill='tonexty', mode='none'))
    #fig = px.area(json_data, x='Datum', y=['Sum Erzeugung', 'Sum Verbrauch'])
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=20)
    ))
    #fig.update_layout(height=400)
    fig.update_layout(xaxis_title="Datum", yaxis_title="Erträge & Verbäuche [kWh]")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_layout(margin_pad=0)
    fig.update_layout(height=500)
    fig.update_xaxes(title_font_size=20)
    fig.update_yaxes(title_font_size=20)
    fig.update_xaxes(tickfont_size=15)
    fig.update_yaxes(tickfont_size=15)
    return fig


def generateCenterTable1(json_data, StrVerg, StrPr, BatPrice, batEff, batLimit):
    '''
    Generate the first part of the center table (gesparte Energie, Verguetung, Einsparung, Finanzieller Erfolg)
    '''
    gesEn, Verg, Einsp, FinErf, Ansch, Amort = generateCenterData(json_data, StrVerg, StrPr, BatPrice, batEff, batLimit)

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


def generateCenterTable2(json_data, StrVerg, StrPr, BatPrice, batEff, batLimit):
    '''
    Generate the second part of the center table (Anschaffungskosten und Amortisation)
    '''
    gesEn, Verg, Einsp, FinErf, Ansch, Amort = generateCenterData(json_data, StrVerg, StrPr, BatPrice, batEff, batLimit)

    if Amort < 10:
        col = 'rgba(0,200,0,1)'
    else:
        col = 'rgba(255,0,0,1)'

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

    table_body = [html.Tbody([row5, row6])]
    return table_body

def generateCenterGauge(json_data, StrVerg, StrPr, BatPrice, batEff, batLimit):
    '''
    Generate the diagramm below the center Table
    '''

    gesEn, Verg, Einsp, FinErf, Ansch, Amort = generateCenterData(json_data, StrVerg, StrPr, BatPrice, batEff, batLimit)

    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=Amort,
        number={'suffix':" J"},
        mode="gauge+number+delta",
        title={'text': "Amortisation",
               'font': {'size': 30, 'weight': 'bold'},
               },
        delta={'reference': 10,
               'decreasing': {'color': 'rgba(0,200,0,1)'},
               'increasing': {'color': 'rgba(255,0,0,1)'},
               'suffix': ' J'
               },
        gauge={'bar': {'color': "gray"},
               'axis': {'range': [None, 20]},
               'steps': [
                   {'range': [0, 10], 'color': "rgba(0,200,0,0.3)"},
                   {'range': [10, 20], 'color': "rgba(255,0,0,0.3)"}]
               }))
    fig.update_layout(height=250)
    fig.update_layout(margin=dict(l=0, r=0, b=0))
    fig.update_layout(margin_pad=0)
    fig.update_yaxes(title_font_size=20)
    fig.update_yaxes(tickfont_size=20)
    return fig

def generateCenterData(json_data, StrVerg, StrPr, BatPrice, batEff, batLimit):
    '''
    Calculate the Data for the center table
    '''

    #fetch Data from API
    url = 'https://iten-web.ch/batteriespeicher/api/batteries/'+str(batLimit)+'/'+str(batEff)
    batData = pd.read_json(url)
    gesEn = batData.iloc[0, 0] / 1000
    losEn = batData.iloc[1, 0] / 1000

    Verg = losEn * StrVerg *-1

    Einsp = gesEn * StrPr

    FinErf = Verg + Einsp

    Ansch = BatPrice

    Amort = Ansch / FinErf / 365 * batData.iloc[2, 0]

    return gesEn, Verg, Einsp, FinErf, Ansch, Amort
