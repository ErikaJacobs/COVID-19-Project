##
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
from pandasql import sqldf
import requests
from io import StringIO

# Testing if today's file is available
now = (datetime.now())

try:
    url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{now.strftime("%m-%d-%Y")}.csv'
    r = requests.get(url) 
    data = pd.read_csv(StringIO(r.text))
except:
    now = (now - timedelta(days = 1))
    
# Make List of Time Frames
timedeltas = (0, 1, 2, 3, 4, 5, 6, 7, 14, 21)
timeframes = []

for num in timedeltas:
    timeframe = (now - timedelta(days = num)).strftime("%m-%d-%Y")
    timeframes.append(timeframe)

# Loop to import files from Johns Hopkins CSSEGIS GitHub
df = pd.DataFrame() 

for time in range(len(timeframes)):
    url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{timeframes[time]}.csv'
    r = requests.get(url) 
    data = pd.read_csv(StringIO(r.text), sort = False)
    data['Delta'] = timedeltas[time]
    df = df.append(data, sort = False)

# Delete Extraneous Stuff
del data
del timeframe
del num
del time

# SQL Code for Aggregating Tables
pysqldf = lambda q: sqldf(q, globals())

df = pysqldf(
'''SELECT Province_State, Country_Region, Delta,
SUM(Confirmed) as Confirmed, 
SUM(Deaths) as Deaths, 
SUM(Recovered) as Recovered, 
SUM(Active) as Active
FROM df
GROUP BY Delta, Country_Region, Province_State''')

#%%

# Determine How Many Days in Chart
chart_days = 8

# X VALUES
# Getting Dates for X axis, and to say when file was last updated.
today = timeframes[0]

for time in range(len(timeframes)):
    date = timeframes[time]
    date = date[:-5]

    if date[3] == "0":
        date = date[:3] + date[4:]

    if date[0] == '0':
        date = date[1:]
    
    date = date.replace('-', '/')
    
    timeframes[time] = date

del date

x = timeframes[:chart_days]
x = x[::-1]

#%%

# Create Country Dropdown

CountryList = df.Country_Region.unique().tolist()
CountryList.sort()
CountryDrop = []

for country in CountryList:
    CountryDrop.append({'label': f'{country}', 'value': f'{country}'})

del CountryList

# Create US State Dropdown

StateList = df.Province_State[df.Country_Region=="US"].unique().tolist()
StateList = [i for i in StateList if i not in ['Recovered', 'Diamond Princess', 'Grand Princess']]
StateList.sort()
StateDrop = []

for state in StateList:
    StateDrop.append({'label': f'{state}', 'value': f'{state}'})
    
del StateList

# Data Type Dropdown

datatypes=[
            {'label': 'Total', 'value': 'Confirmed'},
            {'label': 'Deaths', 'value': 'Deaths'}
        ]

# Increase or Decrease Function - For Comments

def incrdecr(now, then):
    now = round(now, 1)
    then = round(then, 1)
    if now > then:
        value = 'increased'
    if now < then:
        value = 'decreased'
    if now == then:
        value = 'stayed the same'
    return value

#%%
# Y VALUES

# Get Dictionary of y values - Country Portion

def get_ydict_country_stats(n_clicks, value):
    ydict_stats = {}
    
    y = ['Active', 'Deaths', 'Recovered', 'Confirmed']
    
    for axis in y:
    
        temp = pysqldf(
            f'''SELECT Delta, SUM({axis}) as col
            FROM df
            WHERE Country_Region = '{value}'
            GROUP BY Delta
            ORDER BY Delta desc''')
        
        ydict_stats[f'{axis}'] = dict(zip(temp.Delta, temp.col))
        
    return ydict_stats

def get_ydict_country_plot(n_clicks, value):
    ydict_plot = {}
    
    y = ['Active', 'Deaths', 'Recovered', 'Confirmed']
    
    for axis in y:
    
        temp = pysqldf(
            f'''SELECT SUM({axis}) as col
            FROM df
            WHERE Country_Region = '{value}'
            GROUP BY Delta
            ORDER BY Delta desc''')
        
        ydict_plot[f'{axis}'] = temp['col'].to_list()
        ydict_plot[f'{axis}'] = ydict_plot[f'{axis}'][-chart_days:]
        
    return ydict_plot
    
def get_ydict_state_stats(n_clicks, value1, value2):
    ydict_stats = {}
    
    y = ['Active', 'Deaths', 'Recovered', 'Confirmed']
    
    for axis in y:
    
        temp = pysqldf(
            f'''SELECT Delta, SUM({axis}) as col
            FROM df
            WHERE Province_State = '{value1}'
            GROUP BY Delta
            ORDER BY Delta desc''')
        
        ydict_stats[f'{axis}'] = dict(zip(temp.Delta, temp.col))

    return ydict_stats

def get_ydict_state_plot(n_clicks, value1, value2):
    ydict_plot = {}

    y = ['Active', 'Deaths', 'Recovered', 'Confirmed']
    
    for axis in y:
    
        temp = pysqldf(
            f'''SELECT SUM({axis}) as col
            FROM df
            WHERE Province_State = '{value1}'
            GROUP BY Delta
            ORDER BY Delta desc''')
        
        ydict_plot[f'{axis}'] = temp['col'].to_list()
        ydict_plot[f'{axis}'] = ydict_plot[f'{axis}'][-chart_days:]
        
    return ydict_plot

#%%

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    
    html.Div([
        html.H2("Coronavirus Dashboard: A Deeper Dive"),
        html.Img(src="/assets/coronavirus.png")
        ], className="banner"),
    
    
    html.Div([

        html.Div([
            html.H3("By Country/Region", style={'text-align': 'center'}),
            dcc.Graph(id="Coronavirus Chart 1", style={'text-align': 'center'})
            ], className="six columns"),



        html.Div([
            html.H3("By State (US)", style={'text-align': 'center'}),
            dcc.Graph(id="Coronavirus Chart 2", style={'text-align': 'center'})
            ], className="six columns")
        
        ], className="row"),

    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='demo-dropdown',
                    options=CountryDrop,
                    value='US',
                    style = {"margin-left": "10px"}
                    )], className='six columns'),
                ], className='six columns'),

        html.Div([
            dcc.Dropdown(
                id='dropdown2',
                options=StateDrop,
                value='Arizona'
                )], className='three columns'),
        html.Div([
            dcc.Dropdown(
                id='dropdown3',
                options=datatypes,
                value='Confirmed'
                )], className='three columns'),
             ], className='row'),
     html.Br(),
     html.Div([
        html.Div([
            html.Button(id="button1", n_clicks=0, children="Submit",
                        style={"margin-left": "20px",
                               'color': 'white'}
                        ),
                ], className='six columns'),
        html.Div([
            html.Button(id="button2", n_clicks=0, children="Submit",
                        style={'display': 'inline-block',
                                'width': '48 %',
                                'text-align': "center",
                                'float': 'center',
                                'margin': 'auto',
                                'display': 'block',
                                'float': 'center',
                                'color': 'white'
                                }
                        ),
                ], className ='six columns')
         ], className='CenterButtons'),
    html.Br(),
    html.Br(),
    html.Div([
        html.Div([
            html.Div(
                [
                    html.Div([
                        html.Table(id = "Insights Worldwide"
                        )],
                        style={"height": "300px", "overflowY": "scroll", "margin-left": "20px"},
                    ),
                ], className='six columns',
                style={"height": "100%"}, ),
            html.Div(
                [
                    html.Div([
                        html.Table(id="Insights State"
                                )],
                        style={"height": "300px", "overflowY": "scroll"},
                    ),
                ], className='six columns',
                style={"height": "100%"}, ),
                ], className='twelve columns'),
        ], className='row'),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div([
        html.Div([
            html.Label("Dashboard Created By Erika Jacobs"),
            html.Label(f"Last Updated On: {today}"),
            html.Label("Data Source: Coronavirus COVID-19 "
                       "Global Cases by the Center for Systems Science and Engineering "
                       "at Johns Hopkins University"),
            html.A("Data Source via GitHub", href="https://github.com/CSSEGISandData/COVID-19?files=1"),
            html.Label("Coronavirus Picture Courtesy of CDC PHIL")
                  ], className='footer')
            ], className='row')
], className='background')

@app.callback(dash.dependencies.Output("Coronavirus Chart 1", "figure"),
              [Input("button1", "n_clicks")],
              [State('demo-dropdown', 'value')])

def update_fig(n_clicks, value):

    ydict_plot = get_ydict_country_plot(n_clicks, value)

    Graph1 = go.Bar(x=x, y=ydict_plot['Active'], name='Active Cases')
    Graph2 = go.Bar(x=x, y=ydict_plot['Recovered'], name='Recovered')
    Graph3 = go.Bar(x=x, y=ydict_plot['Deaths'], name='Deaths')

    data = [Graph1, Graph2, Graph3]
    layout = dict(title = f"Weekly Breakdown of COVID-19 Cases: {value}",
                  font = dict(color='white'),
                  showlegend = False,
                  barmode = 'stack',
                  paper_bgcolor = 'rgba(0,0,0,0)',
				  plot_bgcolor = 'rgba(0,0,0,0)',
                  colorway = ['#9a3033', '#d66c47', '#e0c553'],
                  textfont = dict(color="White"),
                  colorscale = 'RdBu')
    fig = dict(data = data, layout = layout)
    return fig

@app.callback(dash.dependencies.Output("Insights Worldwide", "children"),
              [Input("button1", "n_clicks")],
              [State('demo-dropdown', 'value')])

def update_worldwide_notes(n_clicks, value):
    
    ydict_stats = get_ydict_country_stats(n_clicks, value)
    
    TOTAL1 = "{0:,d}".format(int(ydict_stats['Confirmed'][0]))
    PERCENT1 = (ydict_stats['Confirmed'][0] - ydict_stats['Confirmed'][7]) / ydict_stats['Confirmed'][7] * 100
    PERCENT2 = (ydict_stats['Confirmed'][0] - ydict_stats['Confirmed'][14]) / ydict_stats['Confirmed'][14] * 100
    PERCENT3 = (ydict_stats['Confirmed'][0] - ydict_stats['Confirmed'][21]) / ydict_stats['Confirmed'][21] * 100
    PERCENT4 = ydict_stats['Recovered'][0] / ydict_stats['Confirmed'][0] * 100
    PERCENT5 = ydict_stats['Recovered'][7] / ydict_stats['Confirmed'][7] * 100
    INCRDECR1 = incrdecr(PERCENT4, PERCENT5)
    PERCENT6 = ydict_stats['Deaths'][0] / ydict_stats['Confirmed'][0] * 100
    PERCENT7 = ydict_stats['Deaths'][7] / ydict_stats['Confirmed'][7] * 100
    INCRDECR2 = incrdecr(PERCENT6, PERCENT7)
    PERCENT8 = ydict_stats['Active'][0] / ydict_stats['Confirmed'][0] * 100
    PERCENT9 = ydict_stats['Active'][7] / ydict_stats['Confirmed'][7] * 100
    INCRDECR3 = incrdecr(PERCENT8, PERCENT9)
    
    pc = [PERCENT1, PERCENT2, PERCENT3, PERCENT4, PERCENT5, PERCENT6,
              PERCENT7, PERCENT8, PERCENT9]
    
    for percent in range(len(pc)):
        pc[percent] = round(pc[percent], 1)

    dfstats = pd.DataFrame(
        {
            f"Insights - {value}":
                [f"As of {x[-1]}, there were a total of {TOTAL1} cases of COVID-19 in this location. "
                 f"This has increased by {pc[0]}% since last week, {pc[1]}% since two weeks ago, and "
                 f"{pc[2]}% since three weeks ago.",
                 f"{pc[5]}% of cases have died as of {x[-1]}. This has {INCRDECR2} since last week, "
                 f"in which {pc[6]}% of cases had died.",
                 f"{pc[7]}% of cases are active as of {x[-1]}. This has {INCRDECR3} since last week, "
                 f"in which {pc[8]}% of cases were actively sick."],
        }
    )
    children = ([html.Tr([html.Th(f"{value} Insights (As of {today})", style={"text-align": "center"})])]
                    +
                    [
                        html.Tr(
                            [
                                html.Td(
                                        dfstats.iloc[i][f"Insights - {value}"]
                                )
                            ]
                        )
                        for i in range(min(len(dfstats), 10))
                    ])
    return children

@app.callback(
    Output('Coronavirus Chart 2', 'figure'),
    [Input("button2", "n_clicks")],
    state=[State('dropdown2', 'value'), State('dropdown3', 'value')])

def update_graph(n_clicks, value1, value2):
    
    ydict_plot = get_ydict_state_plot(n_clicks, value1, value2)
    
    ## Build conditions for value2 (Active, Recovered, Etc.)
    Graph4 = go.Scatter(x=x, 
                        y=ydict_plot[f'{value2}'], 
                        fill = 'tozeroy', 
                        name = 'New ({value2})')
    data = [Graph4]
    layout = dict(title = f"{value1} Cases: New vs Cumulative {value2} Cases",
                  font = dict(color='white'),
                  showlegend = False,
                  paper_bgcolor = 'rgba(0,0,0,0)',
				  plot_bgcolor = 'rgba(0,0,0,0)',
                  colorway = ['#b63735'])
    fig = dict(data = data, layout = layout)
    
    return fig

@app.callback(
    Output('Insights State', 'children'),
    [Input("button2", "n_clicks")],
    state=[State('dropdown2', 'value'), State('dropdown3', 'value')])

def update_state_notes(n_clicks, value1, value2):
    
    ydict_stats = get_ydict_state_stats(n_clicks, value1, value2)
    
    def aboveorbelow(day, week):
        if day > week:
            value = 'above'
        if day < week:
            value = 'below'
        if day == week:
            value = 'approximately'
        return value

    if value2 == 'Confirmed':
        value = 'confirmed cases'
    else:
        value = 'deaths'
        
    TOTAL11 = int(ydict_stats[f'{value2}'][0])
    TOTAL22 = int(ydict_stats[f'{value2}'][7])
    TOTAL1 = "{0:,d}".format(TOTAL11)
    TOTAL2 = "{0:,d}".format(TOTAL22)

    PERCENT3 = round((TOTAL11 - TOTAL22) / TOTAL22 * 100, 1)
    INCRDECR1 = incrdecr(TOTAL11, TOTAL22)

    # Calculate Average
    avg_list = []
    for i in range(7):
        avg_list.append(ydict_stats[f'{value2}'][i])
        
    AVERAGE = sum(avg_list)/len(avg_list)
    AVG = "{0:,d}".format(int(AVERAGE))

    dfstats = pd.DataFrame(
        {
            f"{value1} Insights - {value2}":
                [f"As of {x[-1]}, there are {TOTAL1} total {value} in this state. This has {INCRDECR1} by {PERCENT3}% since last week, in which "
                 f"there were {TOTAL2} total {value}.",
                 f"The average number of {value} in this state over the past week was approximately {AVG} {value}."]
        }
    )

    children = ([html.Tr([html.Th(f"{value1} Insights - {value2} (As of {today})", style={"text-align": "center"})])]
                    +
                    [
                        html.Tr(
                            [
                                html.Td(
                                        dfstats.iloc[i][f"{value1} Insights - {value2}"]
                                )
                            ]
                        )
                        for i in range(min(len(dfstats), 10))
                    ])
    return children

if __name__ == "__main__":
    app.run_server()

#%%