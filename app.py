from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
from flask_restx import Api, fields , Resource
from sqlalchemy.ext.declarative import DeclarativeMeta


app = Flask(__name__)

ENV = 'prod'

if ENV =='dev': 
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:root@localhost:5432/grant_disbursement'
else: 
    app.debug=False
    app.config['SQLALCHEMY_DATABASE_URI']='postgres://aotccantdkhwom:e0ee040a0d97f9cc97acc9caac0f2e11cbbf9857000898fbf665908561d26cdd@ec2-3-219-229-143.compute-1.amazonaws.com:5432/d74v0oq1fb30tv'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(
    title= 'Government Grant Disbursement API', 
    default ='API Endpoints', 
    default_label='', 
    description='A RESTful API that would help your team decide on groups of people who are eligible for various upcoming government grants. These grants are disbursed based on certain criteria - like total household income, age, occupation, etc. The API should be able to build up a list of recipients and which households qualify for it. For ease of definition, a household is defined by all the people living inside 1 physical housing unit.'
    )
api.init_app(app)

class Household(db.Model):
    __tablename__ = 'household'
    household_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    housing_type = db.Column(db.String)

class HouseholdSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Household

household_schema = HouseholdSchema()
households_schema = HouseholdSchema(many=True)

model = api.model('Housing Types',{
    'housing_type':fields.String('Enter Housing Type')
})

@api.route('/post/housing_type')
class post_housing_type(Resource):
    @api.expect(model)
    def post(self):
        housing_type = Household(housing_type=request.json['housing_type'])
        db.session.add(housing_type)
        db.session.commit()
        return {'message':'household has been created and saved into database'}
