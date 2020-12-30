# Processes Johns Hopkins University COVID-19 Data to Create a Dashboard
Data was extracted from the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University using Python. With this newly created data source, a dashboard was created using the Dash library in Python, then deployed through Heroku.

This project previously utilized PySpark via DataBricks to import COVID-19 daily reports. The data was transformed using Spark SQL through PySpark, then the final products were exported to an S3 bucket (Amazon Web Services). Historic project files are still available to view.

## Methods Used
* ETL

Previous Data Flow Diagram:

<img src="https://erikajacobs.netlify.app/post/covid-19-sparked-aws-ideas/featured.png" width="450">

## Technologies Used
* Python
* DataBricks
* Amazon Web Services (S3)
* Heroku

## Packages Used
* Pandas
* Requests
* PySpark
* Boto3
* S3FS
* Dash

# Featured Notebooks, Scripts, Analysis, or Deliverables
* [```app.py```](app.py) - Dashboard Script
* [Coronavirus Dashboard (Deployed)](https://covid-19-jacobs.herokuapp.com/)

# Other Repository Contents
* assets
  * [```coronavirus.png```](/assets/coronavirus.png) - Coronavirus image (Courtesy of CDC PHIL)
  * [```stylesheet.css```](/assets/stylesheet.css) - CSS Stylesheet for dashboard
* history
  * [```COVID-19_Databricks.ipynb```](/history/COVID-19_Databricks.ipynb) - Original ETL data transformation using PySpark and Spark SQL to export to S3
  * [```app_v1.py```](/history/app_v1.py) - Original Dash app that imported data from S3 to create dashboard
* [```Procfile```](Procfile) - Configures Heroku application server
* [```requirements.txt```](requirements.txt) - Sets Python package requirements for Heroky dyno
* [```runtime.txt```](runtime.txt) - Sets Python version in Heroku to Python 3.8.7

# Sources
* [COVID-19 Data Repository - Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19?files=1)
* [Heroku Hosting](https://austinlasseter.medium.com/how-to-deploy-a-simple-plotly-dash-app-to-heroku-622a2216eb73)
