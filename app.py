##
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import pandas as pd
import boto3
import plotly.graph_objs as go

#%%
# Import Data #
###############

aws_access_key_id = ACCESS_KEY
aws_secret_access_key = SECRET_KEY
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)

def importdf(dftype):
    obj = s3.get_object(Bucket='erikatestbucket', Key='COVID-19/Output/{}.csv'.format(dftype))
    df = pd.read_csv(obj['Body'])
    return df

if 'dfActive' not in dir():
    dfActive = importdf('Active')
    print('Active Table Imported')
if 'dfDeaths' not in dir():
    dfDeaths = importdf('Deaths')
    print('Deaths Table Imported')
if 'dfRecovered' not in dir():
    dfRecovered = importdf('Recovered')
    print('Recovered Table Imported')
if 'dfConfirmed' not in dir():
    dfConfirmed = importdf('Confirmed')
    print('Confirmed Table Imported')
    

#%%
# Configure Dates #
##################

# list items from bucket object

s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
bucket = s3.Bucket('erikatestbucket')
BucketObjects = bucket.objects.filter(Prefix="COVID-19/DailyReports")

# Adding Bucket Item to list to get dates
BucketList = []
for object in BucketObjects:
    BucketList.append(str(object))

#%%
##

# Getting Dates for X axis, and to say when file was last updated.
DateList = []

for object in BucketList:
    if '.csv' and 'DailyReports' in object:
        string = (object)
        filenameind = string.index('DailyReports/')
        csvind = string.index('.csv')
        filename = string[filenameind+13:csvind]
        DateList.append(filename)
    else:
        continue

DateList.sort()

for date in DateList:
    i = DateList.index(date)

    if date[3]=="0":
        DateList[i]=date[:3] + date[(4):]

    if date[0]=='0':
        DateList[i]=DateList[i][1:]


today = DateList[-1]

for date in DateList:
    i = date[:(date.index('-2020'))]
    DateList[DateList.index(date)] = i
    DateList[DateList.index(i)] = (i).replace('-', '/')

x = DateList[-8:]

#%%

##Create Country Dropdown

CountryList = dfActive.Country_Region.unique().tolist()
CountryList.sort()
CountryDrop = []

for i in CountryList:
    CountryDrop.append({'label': '{}'.format(i), 'value': '{}'.format(i)})

##Create US State Dropdown

StateList = dfActive.Province_State[dfActive.Country_Region=="US"].unique().tolist()
#StateList.remove(np.nan)
StateList.remove('Recovered')
StateList.remove('Diamond Princess')
StateList.remove('Grand Princess')
StateList.sort()
StateDrop = []

for i in StateList:
    StateDrop.append({'label': '{}'.format(i), 'value': '{}'.format(i)})

## Data Type Dropdown

datatypes=[
            {'label': 'Total', 'value': 'Confirmed'},
            {'label': 'Deaths', 'value': 'Deaths'}
        ]

## Increase or Decrease Function - For Comments

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


##%%

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
            html.Label("Last Updated On: {}".format(today)),
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
    week = list(range(0, 8))
    week.sort(reverse=True)
    Activey = []
    Deathsy = []
    Recoveredy = []

    for i in week:
        a = dfActive['Active_{}'.format(i)][dfActive.Country_Region == value].sum()
        d = dfDeaths['Deaths_{}'.format(i)][dfDeaths.Country_Region == value].sum()
        r = dfRecovered['Recovered_{}'.format(i)][dfRecovered.Country_Region == value].sum()

        Activey.append(a)
        Deathsy.append(d)
        Recoveredy.append(r)

    Graph1 = go.Bar(x=x, y=Activey, name='Active Cases')
    Graph2 = go.Bar(x=x, y=Recoveredy, name='Recovered')
    Graph3 = go.Bar(x=x, y=Deathsy, name='Deaths')

    data = [Graph1, Graph2, Graph3]
    layout = dict(title="Weekly Breakdown of COVID-19 Cases: {}".format(value),
                  font=dict(color='white'),
                  showlegend=False,
                  barmode='stack',
                  paper_bgcolor = 'rgba(0,0,0,0)',
				  plot_bgcolor = 'rgba(0,0,0,0)',
                  colorway=['#9a3033', '#d66c47', '#e0c553'],
                  textfont=dict(color="White"),
                  colorscale='RdBu')
    fig = dict(data=data, layout=layout)
    return fig

@app.callback(dash.dependencies.Output("Insights Worldwide", "children"),
              [Input("button1", "n_clicks")],
              [State('demo-dropdown', 'value')])

def update_worldwide_notes(n_clicks, value):
    TOTAL1 = "{0:,d}".format(int(dfConfirmed.Confirmed_0[dfConfirmed.Country_Region == value].sum()))
    PERCENT1 = (dfConfirmed.Confirmed_0[dfConfirmed.Country_Region == value].sum()
                - dfConfirmed.Confirmed_7[dfConfirmed.Country_Region == value].sum()) / dfConfirmed.Confirmed_7[
                   dfConfirmed.Country_Region == value].sum() * 100
    PERCENT2 = (dfConfirmed.Confirmed_0[dfConfirmed.Country_Region == value].sum()
                - dfConfirmed.Confirmed_14[dfConfirmed.Country_Region == value].sum()) / dfConfirmed.Confirmed_14[
                   dfConfirmed.Country_Region == value].sum() * 100
    PERCENT3 = (dfConfirmed.Confirmed_0[dfConfirmed.Country_Region == value].sum()
                - dfConfirmed.Confirmed_21[dfConfirmed.Country_Region == value].sum()) / dfConfirmed.Confirmed_21[
                   dfConfirmed.Country_Region == value].sum() * 100
    PERCENT4 = (dfRecovered.Recovered_0[dfRecovered.Country_Region == value].sum()) / (
        dfConfirmed.Confirmed_0[dfConfirmed.Country_Region == value].sum()) * 100
    PERCENT5 = (dfRecovered.Recovered_7[dfRecovered.Country_Region == value].sum()) / (
        dfConfirmed.Confirmed_7[dfConfirmed.Country_Region == value].sum()) * 100
    INCRDECR1 = incrdecr(PERCENT4, PERCENT5)
    PERCENT6 = (dfDeaths.Deaths_0[dfDeaths.Country_Region == value].sum()) / (
        dfConfirmed.Confirmed_0[dfConfirmed.Country_Region == value].sum()) * 100
    PERCENT7 = (dfDeaths.Deaths_7[dfDeaths.Country_Region == value].sum()) / (
        dfConfirmed.Confirmed_7[dfConfirmed.Country_Region == value].sum()) * 100
    INCRDECR2 = incrdecr(PERCENT6, PERCENT7)
    PERCENT8 = (dfActive.Active_0[dfActive.Country_Region == value].sum()) / (
        dfConfirmed.Confirmed_0[dfConfirmed.Country_Region == value].sum()) * 100
    PERCENT9 = (dfActive.Active_7[dfActive.Country_Region == value].sum()) / (
        dfConfirmed.Confirmed_7[dfConfirmed.Country_Region == value].sum()) * 100
    INCRDECR3 = incrdecr(PERCENT8, PERCENT9)

    PERCENT1 = round(PERCENT1, 1)
    PERCENT2 = round(PERCENT2, 1)
    PERCENT3 = round(PERCENT3, 1)
    PERCENT4 = round(PERCENT4, 1)
    PERCENT5 = round(PERCENT5, 1)
    PERCENT6 = round(PERCENT6, 1)
    PERCENT7 = round(PERCENT7, 1)
    PERCENT8 = round(PERCENT8, 1)
    PERCENT9 = round(PERCENT9, 1)

    df = pd.DataFrame(
        {
            "Insights - {}".format(value):
                ["As of {}, there were a total of {} cases of COVID-19 in this location. "
                 "This has increased by {}% since last week, {}% since two weeks ago, and "
                 "{}% since three weeks ago.".format(x[-1], TOTAL1, PERCENT1, PERCENT2, PERCENT3),
                 "{}% of cases have recovered as of {}. This has {} since last week, "
                 "in which {}% of cases have recovered".format(PERCENT4, x[-1], INCRDECR1, PERCENT5),
                 "{}% of cases have died as of {}. This has {} since last week, "
                 "in which {}% of cases had died.".format(PERCENT6, x[-1], INCRDECR2, PERCENT7),
                 "{}% of cases are active as of {}. This has {} since last week, "
                 "in which {}% of cases were actively sick.".format(PERCENT8, x[-1], INCRDECR3, PERCENT9)],
        }
    )
    children = ([html.Tr([html.Th("{} Insights (As of {})".format(value, today), style={"text-align": "center"})])]
                    +
                    [
                        html.Tr(
                            [
                                html.Td(
                                        df.iloc[i]["Insights - {}".format(value)]
                                )
                            ]
                        )
                        for i in range(min(len(df), 10))
                    ])
    return children

@app.callback(
    Output('Coronavirus Chart 2', 'figure'),
    [Input("button2", "n_clicks")],
    state=[State('dropdown2', 'value'), State('dropdown3', 'value')])

def update_graph(n_clicks, value1, value2):
    week = list(range(0, 8))
    week.sort(reverse=True)
    y = []
    Newy = []

    ## Build conditions for value2 (Active, Recovered, Etc.)

    if value2 == 'Confirmed':
        for i in week:
            a = dfConfirmed['Confirmed_{}'.format(i)][dfConfirmed.Province_State == value1].sum()
            n = dfConfirmed['ConfirmedNew_{}'.format(i)][dfConfirmed.Province_State == value1].sum()
            y.append(a)
            Newy.append(n)
    if value2 == 'Deaths':
        for i in week:
            a = dfDeaths['Deaths_{}'.format(i)][dfDeaths.Province_State == value1].sum()
            n = dfDeaths['DeathsNew_{}'.format(i)][dfDeaths.Province_State == value1].sum()
            y.append(a)
            Newy.append(n)

    Graph4 = go.Scatter(x=x, y=Newy, fill='tozeroy', name='New ({})'.format(value2))
    Graph5 = go.Scatter(x=x, y=y, fill='tonexty', name='Total ({})'.format(value2))
    data = [Graph4, Graph5]
    layout = dict(title="{} Cases: New vs Cumulative {} Cases".format(value1, value2),
                  font=dict(color='white'),
                  showlegend=False,
                  paper_bgcolor = 'rgba(0,0,0,0)',
				  plot_bgcolor = 'rgba(0,0,0,0)',
                  colorway = ['#ff7947', '#b63735'])
    fig = dict(data=data, layout=layout)
    return fig

@app.callback(
    Output('Insights State', 'children'),
    [Input("button2", "n_clicks")],
    state=[State('dropdown2', 'value'), State('dropdown3', 'value')])

def update_state_notes(n_clicks, value1, value2):
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
        TOTAL11 = ((dfConfirmed.Confirmed_0[dfConfirmed.Province_State == value1].sum()))
        TOTAL1 = "{0:,d}".format(int(TOTAL11))
        TOTAL22 = ((dfConfirmed.Confirmed_7[dfConfirmed.Province_State == value1].sum()))
        TOTAL2 = "{0:,d}".format(int(TOTAL22))
        TOTAL33 = ((dfConfirmed.ConfirmedNew_0[dfConfirmed.Province_State == value1].sum()))
        TOTAL3 = "{0:,d}".format(int(TOTAL33))
        TOTAL44 = ((dfConfirmed.ConfirmedNew_7[dfConfirmed.Province_State == value1].sum()))
        TOTAL4 = "{0:,d}".format(int(TOTAL44))

        PERCENT1 = round(TOTAL33 / TOTAL11 * 100, 1)
        PERCENT2 = round(TOTAL44 / TOTAL22 * 100, 1)
        PERCENT3 = round((TOTAL11 - TOTAL22) / TOTAL22 * 100, 1)
        PERCENT4 = round((TOTAL33 - TOTAL44) / TOTAL44 * 100, 1)

        INCRDECR1 = incrdecr(TOTAL11, TOTAL22)
        INCRDECR2 = incrdecr(TOTAL33, TOTAL44)
        INCRDECR3 = incrdecr(PERCENT1, PERCENT2)

        AVERAGE = dfConfirmed.iloc[:, 13:20][dfConfirmed.Province_State == value1].sum().sum() / 7
        AVG = "{0:,d}".format(int(AVERAGE))
        DAYAVG = aboveorbelow(TOTAL33, AVERAGE)

    if value2 == 'Deaths':
        value = 'deaths'
        TOTAL11 = ((dfDeaths.Deaths_0[dfDeaths.Province_State == value1].sum()))
        TOTAL1 = "{0:,d}".format(int(TOTAL11))
        TOTAL22 = ((dfDeaths.Deaths_7[dfDeaths.Province_State == value1].sum()))
        TOTAL2 = "{0:,d}".format(int(TOTAL22))
        TOTAL33 = ((dfDeaths.DeathsNew_0[dfDeaths.Province_State == value1].sum()))
        TOTAL3 = "{0:,d}".format(int(TOTAL33))
        TOTAL44 = ((dfDeaths.DeathsNew_7[dfDeaths.Province_State == value1].sum()))
        TOTAL4 = "{0:,d}".format(int(TOTAL44))

        PERCENT1 = round(TOTAL33 / TOTAL11 * 100, 1)
        PERCENT2 = round(TOTAL44 / TOTAL22 * 100, 1)
        PERCENT3 = round((TOTAL11 - TOTAL22) / TOTAL22 * 100, 1)
        PERCENT4 = round((TOTAL33 - TOTAL44) / TOTAL44 * 100, 1)

        INCRDECR1 = incrdecr(TOTAL11, TOTAL22)
        INCRDECR2 = incrdecr(TOTAL33, TOTAL44)
        INCRDECR3 = incrdecr(PERCENT1, PERCENT2)

        AVERAGE = dfDeaths.iloc[:, 13:20][dfDeaths.Province_State == value1].sum().sum() / 7
        AVG = "{0:,d}".format(int(AVERAGE))
        DAYAVG = aboveorbelow(TOTAL33, AVERAGE)

    df = pd.DataFrame(
        {
            "{} Insights - {}".format(value1, value2):
                ["As of {}, there are {} total {} in this state. This has {} by {}% since last week, in which "
                 "there were {} total {}.".format(x[-1], TOTAL1, value, INCRDECR1, PERCENT3, TOTAL2, value),
                 "There were {} new {} on {} in this state. This has {} by {}% since last week, in which "
                 "there were {} new {} on {}.".format(TOTAL3, value, x[-1], INCRDECR2, PERCENT4, TOTAL4, value, x[-8]),
                 "On {}, {}% of {} in this state were new {}. This has {} since last week, in which "
                 "{}% of {} on {} were new {}.".format(x[-1], PERCENT1, value, value, INCRDECR3, PERCENT2,
                                                                     value, x[0], value),
                 "There were an average of {} new {} in this state per day over the past week. In comparison, today is {} average "
                 "for new {} in this state over the past week.".format(AVG, value, DAYAVG, value)]
        }
    )

    children = ([html.Tr([html.Th("{} Insights - {} (As of {})".format(value1, value2, today), style={"text-align": "center"})])]
                    +
                    [
                        html.Tr(
                            [
                                html.Td(
                                        df.iloc[i]["{} Insights - {}".format(value1, value2)]
                                )
                            ]
                        )
                        for i in range(min(len(df), 10))
                    ])
    return children



if __name__ == "__main__":
    app.run_server(debug=True)