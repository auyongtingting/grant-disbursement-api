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

