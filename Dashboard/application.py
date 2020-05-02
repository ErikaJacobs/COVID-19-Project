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

aws_access_key_id = 'ACCESS_KEY'
aws_secret_access_key = 'SECRET_KEY'
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
today = DateList[-1]
x = DateList[-7:]


#%%
# CREATING GRAPH #
##################



##
y = [1, 2, 3, 4, 5, 6, 7]

# Graph 2
trace_close = go.Scatter(x=x,
                         y=y,
                         name='Close',
                         line=dict(color="#f44242"))

data = [trace_close]
layout = dict(title="Coronavirus Chart 2", showlegend = False)
fig2 = dict(data=data, layout=layout)

#%%

##Create Country Dropdown




#%%

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
            dcc.Graph(id="Coronavirus Chart 2", figure=fig2)
            ], className="six columns")
        
        ], className="row"),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='demo-dropdown',
                options=[
                    {'label': 'US', 'value': 'US'},
                    {'label': 'Canada', 'value': 'Canada'},
                    {'label': 'Italy', 'value': 'Italy'}
                ],
                value='US'
                )], className='three columns'),
            ], className='row'),

    html.Div([
        html.Div([
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

    x = ['4/23', '4/24', '4/25', '4/26', '4/27', '4/28', '4/29', '4/30']

    Graph1 = go.Bar(x=x, y=Activey, name='Active Cases')
    Graph2 = go.Bar(x=x, y=Recoveredy, name='Recovered')
    Graph3 = go.Bar(x=x, y=Deathsy, name='Deaths')

    data = [Graph1, Graph2, Graph3]
    layout = dict(title="Coronavirus Chart 1", showlegend=False, barmode='stack')
    fig = dict(data=data, layout=layout)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)