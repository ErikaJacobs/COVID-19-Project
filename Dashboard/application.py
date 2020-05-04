##
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
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
    if date[0]=='0':
        DateList[DateList.index(date)]=date[1:]
    else:
        continue

today = DateList[-1]

for date in DateList:
    i = date[:(date.index('-2020'))]
    DateList[DateList.index(date)] = i
    DateList[DateList.index(i)] = (i).replace('-', '/')

print(DateList)
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
            {'label': 'Active', 'value': 'Active'},
            {'label': 'Recovered', 'value': 'Recovered'},
            {'label': 'Deaths', 'value': 'Deaths'}
        ]


##%%

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    
    html.Div([
        html.H2("Coronavirus Dashboard"),
        html.Img(src="/assets/coronavirus.png")
        ], className="banner"),
    
    
    html.Div([

        html.Div([
            html.H3("Graph 1"),
            dcc.Graph(id="Coronavirus Chart 1")
            ], className="six columns"),



        html.Div([
            html.H3("Graph 2"),
            dcc.Graph(id="Coronavirus Chart 2")
            ], className="six columns")
        
        ], className="row"),

    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='demo-dropdown',
                    options=CountryDrop,
                    value='US'
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
                value='Active')
                ], className='three columns'),
             ], className='row'),

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
])

@app.callback(dash.dependencies.Output("Coronavirus Chart 1", "figure"),
              [dash.dependencies.Input('demo-dropdown', 'value')])

def update_fig(value):
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
    layout = dict(title="Coronavirus Chart 1", showlegend=False, barmode='stack')
    fig = dict(data=data, layout=layout)
    return fig

@app.callback(
    Output('Coronavirus Chart 2', 'figure'),
    [Input('dropdown2', 'value'), Input('dropdown3', 'value')])

def update_graph(value1, value2):
    week = list(range(0, 8))
    week.sort(reverse=True)
    y = []
    Newy = []

## Build conditions for value2 (Active, Recovered, Etc.)
    if value2 == 'Active':
        for i in week:
            a = dfActive['Active_{}'.format(i)][dfActive.Province_State == value1].sum()
            n = dfActive['ActiveNew_{}'.format(i)][dfActive.Province_State == value1].sum()
            y.append(a)
            Newy.append(n)
    if value2 == 'Confirmed':
        for i in week:
            a = dfConfirmed['Confirmed_{}'.format(i)][dfConfirmed.Province_State == value1].sum()
            n = dfConfirmed['ConfirmedNew_{}'.format(i)][dfConfirmed.Province_State == value1].sum()
            y.append(a)
            Newy.append(n)
    if value2 == 'Deaths':
        for i in week:
            a = dfDeaths['Deaths_{}'.format(i)][dfDeaths.Province_State == value1].sum()
            n = dfDeaths['Deaths_{}'.format(i)][dfDeaths.Province_State == value1].sum()
            y.append(a)
            Newy.append(n)
    if value2 == 'Recovered':
        for i in week:
            a = dfRecovered['Recovered_{}'.format(i)][dfRecovered.Province_State == value1].sum()
            n = dfRecovered['Recovered_{}'.format(i)][dfRecovered.Province_State == value1].sum()
            y.append(a)
            Newy.append(n)

    Graph4 = go.Scatter(x=x, y=Newy, fill='tozeroy', name='New ({})'.format(value2))
    Graph5 = go.Scatter(x=x, y=y, fill='tonexty', name='Total ({})'.format(value2))
    data = [Graph4, Graph5]
    layout = dict(title="Coronavirus Chart 2", showlegend=True)
    fig = dict(data=data, layout=layout)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)