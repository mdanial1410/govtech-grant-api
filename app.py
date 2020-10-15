from flask import Flask, jsonify, request, make_response
from flask_mongoengine import MongoEngine
import json
from mongoengine import DoesNotExist
from functions import *

app = Flask(__name__)

mongo_username = 'user-backend'
mongo_password = "xtqxIQGH35hzWTzt"
db_name = "API"
DB_URI = f"mongodb+srv://{mongo_username}:{mongo_password}@cluster0.ftixi.gcp.mongodb.net/{db_name}?retryWrites=true&w=majority"

app.config['MONGODB_HOST'] = DB_URI

db = MongoEngine()
db.init_app(app)

OCCUPATION = ['Unemployed', 'Student', 'Employed']

class Family(db.EmbeddedDocument):
    id = db.IntField(required=True)
    name = db.StringField(required=True)
    gender = db.StringField(required=True)
    maritalStatus = db.StringField(required=True)
    spouse = db.StringField()
    occupationType = db.StringField(required=True, choices=OCCUPATION)
    annualIncome = db.IntField(required=True)
    dob = db.StringField(required=True)
    # dob has to be in the format 'DD-MM-YYYY'


class House(db.Document):
    house_id = db.IntField(required=True, unique=True)
    housingType = db.StringField(required=True)
    family = db.EmbeddedDocumentListField(Family)


@app.route('/api/create_household', methods=['POST'])
def create_household():
    '''
    create household with no family members initialised
    '''
    content = request.json
    h = House.objects.order_by('-house_id').first()
    if h == None:
        h_id = 1
    else:
        h = json.loads(h.to_json())
        h_id = h.get('house_id') + 1

    h_id_arr = list()
    if isinstance(content, list):
        # creating more than 1 household
        for item in content:
            h = House(house_id=h_id, housingType=item['housingType'])
            h.save()
            h_id_arr.append(h_id)
            h_id += 1
    else:
        # creating just one household
        h = House(house_id=h_id, housingType=content['housingType'])
        h.save()
        h_id_arr.append(h_id)
    return make_response(f"House ID: {h_id_arr} successfully created.", 201)


@app.route('/api/add_family/<h_id>', methods=['POST'])
def add_family(h_id):
    '''
    family member is added only if its not already in the database
    '''
    edited = False
    content = request.json
    h = House.objects.get(house_id=h_id).to_json()
    h = json.loads(h)
    family_arr = h['family']
    if family_arr:
        # family_arr not empty
        count = family_arr[-1].get('id') + 1
    else:
        count = 1

    for new_name in content['family']:
        if not dup_name_check(family_arr, new_name['name']):
            new_name.update({'id': count})
            family_arr.append(new_name)
            count += 1
            edited = True

    if edited:
        House.objects.get(house_id=h_id).update(family=family_arr)
        return make_response(f"Successfully added family member to House ID: {h_id}", 201)
    else:
        return make_response(f"Duplicated entries detected!", 400)


@app.route('/api/list_household', methods=['GET'])
def list_household():
    houses = House.objects.all()
    return make_response(jsonify(houses), 200)


@app.route('/api/show_household/<h_id>', methods=['GET'])
def show_household(h_id):
    try:
        h = House.objects.get(house_id=h_id).to_json()
        h = json.loads(h)
        rm_spouse(h['family'])
        return make_response(jsonify(h), 200)
    except DoesNotExist:
        return make_response(f'House ID: {h_id} does not exist!', 400)


@app.route('/api/del_household/<h_id>', methods=['DELETE'])
def del_household(h_id):
    try:
        House.objects.get(house_id=h_id).delete()
        return make_response(f'House ID: {h_id} deleted successfully', 200)
    except Exception as e:
        print(f'Error >> {e}')
        return make_response(f'Something went wrong trying to delete House ID: {h_id}', 500)


@app.route('/api/del_member/<h_id>/<fam_name>', methods=['DELETE'])
def del_member(h_id, fam_name):
    h = House.objects.get(house_id=h_id).to_json()
    h = json.loads(h)
    family = h['family']
    new_family = family.copy()

    for i in range(len(family)):
        name = family[i].get('name')
        if name == fam_name:
            del new_family[i]
            break

    House.objects.get(house_id=h_id).update(family=new_family)
    return make_response(f'Successfully removed {fam_name}', 200)


@app.route('/api/grant_disbursement/<h_size>', methods=['GET'])
def grant_disbursement(h_size):
    '''
    retrieve only houses that matches with h_size.
    calculate total income and compare with threshold of each grant/scheme.
    return a list of dictionaries with schemes as keys.
    for qualifying family members, return only their names.
    '''
    h = House.objects.filter(family__size=int(h_size))
    if not h:
        return make_response(f'No household of size {h_size}', 400)
    h = json.loads(h.to_json())
    res = {
        'Student Encouragement Bonus': [],
        'Family Togetherness': [],
        'Elder Bonus': [],
        'Baby SunShine Grant': [],
        'YOLO GST Grant': {'house_id': []}
    }

    for house in h:
        res.get('Student Encouragement Bonus').append(seb(house, threshold=150000))
        res.get('Family Togetherness').append(fts(house))
        res.get('Elder Bonus').append(elder_bonus(house))
        res.get('Baby SunShine Grant').append(baby_sunshine_grant(house))
        temp = yolo_grant(house, threshold=100000)
        if temp:
            res.get('YOLO GST Grant')['house_id'].append(temp)
    return make_response(jsonify(res), 200)


if __name__ == "__main__":
    app.run(debug=True)