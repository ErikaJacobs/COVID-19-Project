# Manipulates Johns Hopkins COVID-19 Data Into S3 Bucket, and Creates Dashboard
This project utilized PySpark via DataBricks to import COVID-19 daily reports from the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University. The data was transformed using Spark SQL through PySpark, then the final products were exported to an S3 bucket (Amazon Web Services).

With this newly created data source, a dashboard was created using the Dash library in Python, then deployed through Python Anywhere.

## Methods Used
* ETL

<img src="https://erikajacobs.netlify.app/post/covid-19-sparked-aws-ideas/featured.png" width="500">

## Technologies Used
* Python
* DataBricks
* Amazon Web Services (S3)

## Packages Used
* PySpark
* Boto3
* S3FS
* Dash

# Featured Notebooks, Scripts, Analysis, or Deliverables
* [Python Script - DataBricks Notebook](https://github.com/ErikaJacobs/COVID-19-Project/blob/master/COVID-19%20Databricks%20Notebook.ipynb)
* [Python Script - Dashboard](https://github.com/ErikaJacobs/COVID-19-Project/blob/master/Dashboard/application.py)
* [Coronavirus Dashboard (Deployed)](http://erikajacobs.pythonanywhere.com/)
* [Blog Post - DataBricks, PySpark, AWS, and Data Prep](https://erikajacobs.netlify.app/post/covid-19-sparked-aws-ideas/)
* [Blog Post - Dashboard Creation](https://erikajacobs.netlify.app/post/dash-of-coronavirus-data/)

# Other Repository Contents
* ```coronavirus.png```: Coronavirus Image (Courtesy of CDC PHIL)
* ```stylesheet.css```: Dashboard Style Sheet

# Sources
* [COVID-19 Data Repository - Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19?files=1)
