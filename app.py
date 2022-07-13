from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow 
from flask_restx import Api, fields , Resource
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import func, extract, and_
import datetime
from dateutil.relativedelta import *
import json

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

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x != 'query' and x != 'query_class' and x != 'household']:
                data = obj.__getattribute__(field)
                try:
                    if type(data) == datetime.date:
                        fields[field] = data.strftime("%Y-%m-%d")
                    else:
                        json.dumps(data)
                        fields[field] = fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)

class Household(db.Model):
    __tablename__ = 'household'
    household_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    housing_type = db.Column(db.String)

class HouseholdSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Household

household_schema = HouseholdSchema()
households_schema = HouseholdSchema(many=True)

class Family_Household(db.Model):
    __tablename__ = 'occupant'
    uuid = db.Column(db.Integer,primary_key=True,autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.household_id'))
    name = db.Column(db.String)
    gender = db.Column(db.String)
    marital_status = db.Column(db.String)
    spouse = db.Column(db.String, nullable=True)
    occupation_type = db.Column(db.String)
    annual_income = db.Column(db.Integer)
    dob = db.Column(db.Date)
    household = db.relationship('Household', backref='members')

class Family_Household_Schema(ma.Schema):
    class Meta:
        fields = ('uuid', 'household_id', 'name', 'gender', 'marital_status', 'spouse', 'occupation_type', 'annual_income', 'dob')

family_household_schema = Family_Household_Schema()
family_households_schema = Family_Household_Schema(many=True)

model = api.model(
    'Housing Types',{
        'household_id':
            fields.Integer('Enter Housing Unit (Household ID)'),
        'housing_type':
            fields.String('Enter Housing Type (Possible options: Landed, Condominium, HDB)')})
@api.route('/post/create_household')
class post_household(Resource):
    @api.expect(model)
    def post(self):
        housing_type = Household(housing_type=request.json['housing_type'])
        db.session.add(housing_type)
        db.session.commit()
        return {'message':'household has been created and saved into database'}

model = api.model('Family Member to Household',{
    'uuid': fields.Integer('Unique Identification Number for each Member'),
    'household_id': fields.Integer('Enter Housing Unit (Household ID)'),
    'name':fields.String('Enter Name'),
    'gender':fields.String('Enter Gender (Options: Female, Male)'),
    'marital_status':fields.String('Enter Marital Status (Options: Single, Married, Widowed, Divorced/Separated)'),
    'spouse':fields.String('Enter Spouse (Options: Name of the spouse or PK)'),
    'occupation_type':fields.String('Enter Occupation Type (Options: Unemployed, Student, Employed)'),
    'annual_income':fields.Integer('Enter Annual Income'),
    'dob': fields.String('Enter DOB (YYYY-MM-DD)'),
})
@api.route('/post/add_member_to_household')
class post_member_to_household(Resource):
    @api.expect(model)
    def post(self):
        member = Family_Household(
        household_id=request.json['household_id'], name=request.json['name'],gender=request.json['gender'],
        marital_status=request.json['marital_status'],spouse=request.json['spouse'],occupation_type=request.json['occupation_type'],
        annual_income=request.json['annual_income'],dob=request.json['dob'])
        db.session.add(member)
        db.session.commit()
        return {'message':'family member has been added to the household in the database'}

@api.route('/get/list_households')
class get_list_households(Resource):
    def get(self): 
        household = Household.query.all() 
        householdJson = json.loads(json.dumps(household, cls=AlchemyEncoder))
        for index, householdItem in enumerate(householdJson):
            foundMembers = Family_Household.query.filter_by( household_id = householdItem['household_id']).all()
            householdJson[index]['members'] = json.loads(json.dumps(foundMembers, cls=AlchemyEncoder))
        return jsonify(householdJson)

@api.route('/get/specific_household/<int:household_id>')
class get_household_id(Resource):
    def get(self, household_id):
        household = Household.query.filter_by(household_id = household_id).all() 
        householdJson = json.loads(json.dumps(household, cls=AlchemyEncoder))
        for index, householdItem in enumerate(householdJson):
            foundMembers = Family_Household.query.filter_by( household_id = householdItem['household_id']).all()
            householdJson[index]['members'] = json.loads(json.dumps(foundMembers, cls=AlchemyEncoder))
        return jsonify(householdJson)

@api.route('/get/student_encouragement_bonus')
class get_student_encouragement_bonus(Resource):
    def get(self):
        households_sixteen = Family_Household.query.filter(extract('year', func.age(Family_Household.dob))< 16).filter(Family_Household.occupation_type == "Student").all()
        households_sixteenJson = json.loads(json.dumps(households_sixteen, cls=AlchemyEncoder))

        qualified_sixteens = [] 
        for count_household in households_sixteenJson: 
            if count_household['household_id'] not in qualified_sixteens:
                qualified_sixteens.append(count_household['household_id'])

        households_income_200000 = Family_Household.query.with_entities(Family_Household.household_id, func.sum(Family_Household.annual_income)).filter(Family_Household.household_id.in_(qualified_sixteens)).group_by(Family_Household.household_id).having(func.sum(Family_Household.annual_income) < 200000).all()
        households_income_200000Json = json.loads(json.dumps(households_income_200000, cls=AlchemyEncoder))

        qualified_households = [] 
        for count_household in households_income_200000Json: 
            if count_household[0] not in qualified_households:
                qualified_households.append(count_household[0])

        household = Household.query.filter(Household.household_id.in_(qualified_households)).all() 
        householdJson = json.loads(json.dumps(household, cls=AlchemyEncoder))

        for index, householdItem in enumerate(householdJson):
            foundMembers = Family_Household.query.filter(and_(Family_Household.household_id == householdItem['household_id'], extract('year', func.age(Family_Household.dob)) < 16)).all()
            householdJson[index]['members'] = json.loads(json.dumps(foundMembers, cls=AlchemyEncoder))

        return jsonify(householdJson)
@api.route('/get/multigeneration_scheme')
class get_multigeneration_scheme(Resource):
    def get(self):

        households_income_150000 = Family_Household.query.with_entities(Family_Household.household_id, func.sum(Family_Household.annual_income)).group_by(Family_Household.household_id).having(func.sum(Family_Household.annual_income) < 150000).all()
        
        qualified_households = []  
        for count_household in households_income_150000: 
            if count_household[0] not in qualified_households:
                qualified_households.append(count_household[0])

        households_eighteen_ff= Family_Household.query.filter(Family_Household.household_id.in_(qualified_households)).filter((extract('year', func.age(Family_Household.dob)) < 18) | (extract('year', func.age(Family_Household.dob)) > 55)).all()
        households_eighteen_ffJson = json.loads(json.dumps(households_eighteen_ff, cls=AlchemyEncoder))

        final_qualified_households = [] 

        for final_household in households_eighteen_ffJson: 
            if (final_household["household_id"] not in final_qualified_households): 
                final_qualified_households.append(final_household["household_id"])

        household = Household.query.filter(Household.household_id.in_(final_qualified_households)).all()
        householdJson = json.loads(json.dumps(household, cls=AlchemyEncoder))
        
        for index, householdItem in enumerate(householdJson):
            foundMembers = Family_Household.query.filter_by( household_id = householdItem['household_id']).all()
            householdJson[index]['members'] = json.loads(json.dumps(foundMembers, cls=AlchemyEncoder))

        return jsonify(householdJson)

@api.route('/get/elder_bonus')
class get_elder_bonus(Resource):
    def get(self):

        hdb_households = Household.query.filter(Household.housing_type == "HDB").all() 
        hdb_householdsJson = json.loads(json.dumps(hdb_households, cls=AlchemyEncoder))

        hdb_households_arr = [] 
        for hdb_household in hdb_householdsJson: 
            if (hdb_household["household_id"] not in hdb_households_arr):
                hdb_households_arr.append(hdb_household["household_id"])

        hdb_households_ff = Family_Household.query.filter(and_(Family_Household.household_id.in_(hdb_households_arr),extract('year', func.age(Family_Household.dob)) > 55)).all()
        hdb_households_ffJSON = json.loads(json.dumps(hdb_households_ff, cls=AlchemyEncoder))

        final_hdb_households = [] 
        for hdb_households_get_elder_bonus in hdb_households_ffJSON: 
            if (hdb_households_get_elder_bonus["household_id"] not in final_hdb_households):
                final_hdb_households.append(hdb_households_get_elder_bonus["household_id"])

        household = Household.query.filter(Household.household_id.in_(final_hdb_households)).all() 
        householdJson = json.loads(json.dumps(household, cls=AlchemyEncoder))

        for index, householdItem in enumerate(householdJson):
            foundMembers = Family_Household.query.filter(and_(Family_Household.household_id == householdItem['household_id'], extract('year', func.age(Family_Household.dob)) >= 55)).all()
            householdJson[index]['members'] = json.loads(json.dumps(foundMembers, cls=AlchemyEncoder))

        return jsonify(householdJson)

@api.route('/get/baby_sunshine_grant')
class get_baby_sunshine_grant(Resource):
    
    def get(self):
        today = datetime.date.today()
        filter_date = today - relativedelta(months=+8)
        households_baby = Family_Household.query.filter((Family_Household.dob) > filter_date).all()
        households_babyJSON = json.loads(json.dumps(households_baby, cls=AlchemyEncoder))

        qualified_households = [] 
        for household_babyJSON in households_babyJSON:
            if (household_babyJSON["household_id"] not in qualified_households):
                qualified_households.append(household_babyJSON["household_id"])

        households = Household.query.filter(Household.household_id.in_(qualified_households)).all() 
        householdsJson = json.loads(json.dumps(households, cls=AlchemyEncoder))

        for index, householdItem in enumerate(householdsJson):
            foundMembers = Family_Household.query.filter(and_(Family_Household.household_id == householdItem['household_id'],(Family_Household.dob) > filter_date)).all()
            householdsJson[index]['members'] = json.loads(json.dumps(foundMembers, cls=AlchemyEncoder))
        return (householdsJson)

@api.route('/get/yolo_gst_grant')
class get_yolo_gst_grant(Resource):
    def get(self):

        hdb_households = Household.query.filter(Household.housing_type == "HDB").all() 
        hdb_householdsJson = json.loads(json.dumps(hdb_households, cls=AlchemyEncoder))

        hdb_households = [] 
        for hdb_household in hdb_householdsJson: 
            if (hdb_household["household_id"] not in hdb_households):
                hdb_households.append(hdb_household["household_id"])
        
        qualified_households = [] 
        hdb_households2 = Family_Household.query.filter(Household.household_id.in_(hdb_households)).with_entities(Family_Household.household_id, func.sum(Family_Household.annual_income)).group_by(Family_Household.household_id).having(func.sum(Family_Household.annual_income) < 100000).all()
        hdb_households2Json = json.loads(json.dumps(hdb_households2, cls=AlchemyEncoder))
        
        for hdb_household2 in hdb_households2Json:
            if (hdb_household2[0] not in qualified_households):
                qualified_households.append(hdb_household2[0])

        households = Household.query.filter(Household.household_id.in_(qualified_households)).all() 
        householdsJson = json.loads(json.dumps(households, cls=AlchemyEncoder))

        for index, householdItem in enumerate(householdsJson):
            foundMembers = Family_Household.query.filter(Family_Household.household_id == householdItem['household_id']).all()
            householdsJson[index]['members'] = json.loads(json.dumps(foundMembers, cls=AlchemyEncoder))

        return (householdsJson)
