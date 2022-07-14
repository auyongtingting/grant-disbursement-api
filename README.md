# Grant Disbursement API

A RESTful API that would help your team decide on groups of people who are eligible for various upcoming government grants. These grants are disbursed based on certain criteria - like total household income, age, occupation, etc. The API should be able to build up a list of recipients and which households qualify for it. 

## Deployment 

Step 1: pipenv install gunicorn or pip install gunicorn

Step 2: Download and install Heroku CLI - https://devcenter.heroku.com/articles/heroku-cli

Step 3: Login via CLI
```
heroku login 
```

Step 4: Create application 
```
heroku addons:create heroku-postgresql:hobby-dev --app grant-disbursement-api
```

Step 5: Get URI
```
heroku config --app grant-disbursement-api
```

Step 6: Create Procfile 
```
touch Procfile
```

Step 7: Fill Procfile with the following line
```
web: gunicorn wsgi:app
```

Step 8: Create requirements.txt
```
pip freeze > requirements.txt
```

Step 9: Create runtime.txt 
```
touch runtime.txt
```

Step 10: Fill runtime.txt with the following line
```
python-3.10.5
```

Step 11: Create wsgi.py 
```
touch wsgi.py
```

Step 12: Fill wsgi.py with the following lines of codes 
```
from app import app 

if __name__ == "__main__":
    app.run()
```

Step 13: Deploy wih Git 
```
git init
git add . && git commit -m "Initial Deploy"
heroku git:remote -a grant-disbursement-api
git push heroku main
```

Step 14: Add table to remote database 
```
heroku run python
>>> from app import db 
>>> db.create_all()
>>> exit()
```

Step 15: Visit application 
```
heroku open
```

## Setup remote database

Step 1: Download code source 
Download repository from GitHub and unzip. 

Step 2: Installation of PostgreSQL
Before proceeding on, please ensure that PostgreSQL has been installed on your device. If not, please download from https://www.postgresql.org/download/. 

Step 3: Creation of database 
Proceed to "database" folder and run the following command to create database.
Before creation of database, please ensure database, user, password, host and port matches in "database.py". 
```
cd database
python database.py
```

Step 3: Creation of tables
Proceed to main directory and run the following command to create tables.
Before creation of tables, please ensure SQLALCHEMY_DATABASE_URI matches in "app.py".
```
cd .. 
python
>>> from app import db 
>>> db.create_all()
>>> exit()
```

Step 5: Change the environment mode from "prod" to "dev" 
Proceed to "app.py" file and change environment mode " ENV = 'dev' ".
```
ENV = 'dev' 
```

Step 6: Import csv files to test endpoints 
Proceed to pgAdmin 4 and locate database named 'grant_disbursement'. Subsequently, proceed to the tables to import the csv files respectively. 


## Run application locally

Step 1: Download code source 
Download repository from GitHub and unzip. 

Step 2: Install dependencies
Run the following command to install dependencies.
```
pip install -r requirements.txt
```

Step 3: Run application
Run the application with the following command.
```
flask run
```

Step 4: Explore Swagger
```
Enter "http://127.0.0.1:5000" into browser and you're good to go! 
```

## Assumption(s)
1. With regards to the inputs, values that has been passed through the API endpoints are consistent to what have been shown in the example given.
2. As most of the questions requested fields for the households, household id has been included to better differentiate which housing unit the members belong to. 
3. With regards to question 3, all households will be listed even with households that have no one living in it. 
4. With regards to question 4, specific household refers to the specific housing unit (household id). - NOT housing type
5. With regards to question 5i, qualifying members who are less than 16 years old include those with who are non-students. 