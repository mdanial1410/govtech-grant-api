from flask import Flask, jsonify, request, make_response
from flask_mongoengine import MongoEngine
import json
from bson.objectid import ObjectId
from mongoengine import DoesNotExist, NotUniqueError, ObjectIdField

app = Flask(__name__)

mongo_password = "Danial1410"
db_name = "API"
DB_URI = "mongodb+srv://danial:{}@cluster0.ftixi.gcp." \
         "mongodb.net/{}?retryWrites=true&w=majority".format(mongo_password, db_name)

app.config['MONGODB_HOST'] = DB_URI

db = MongoEngine()
db.init_app(app)

'''
Data Struc:
{
houseType : "landed/condo" ,
family: [
            {family member 1 ('name': "..." , "gender": "..." , and so on},
            {family member 2},
            ...
        ]
}
'''

class Family(db.EmbeddedDocument):
    id = db.IntField()
    name = db.StringField(required=True)
    gender = db.StringField(required=True)
    maritalStatus = db.StringField(required=True)
    spouse = db.StringField()
    occupationType = db.StringField(required=True)
    annualIncome = db.IntField(required=True)
    dob = db.StringField(required=True)


class House(db.Document):
    house_id = db.IntField(required=True, unique=True)
    housingType = db.StringField(required=True)
    family = db.EmbeddedDocumentListField(Family)


@app.route('/api/create_household', methods=['POST'])
def create_household():
    '''
    create household with no family members initialised
    '''
    h_id = list()
    content = request.json
    try:
        if isinstance(content, list):
            for item in content:
                h = House(house_id=item['house_id'], housingType=item['housingType'])
                h.save()
                h_id.append(h.house_id)
        else:
            h = House(house_id=content['house_id'], housingType=content['housingType'])
            h.save()
            h_id.append(h.house_id)
        return make_response(f"House ID: {h_id} successfully created.", 201)
    except NotUniqueError:
        return make_response(f"Duplicated House ID detected!\n", 400)


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
        return make_response(f"Successfully added family member in House ID:{h_id}", 201)
    else:
        return make_response(f"Duplicated entries detected!", 400)


def dup_name_check(family_arr, new_name):
    '''
    checks for duplicate name in the family array
    :return: boolean
    '''
    for member in family_arr:
        if member.get('name') == new_name:
            return True
    return False


@app.route('/api/list_household', methods=['GET'])
def list_household():
    houses = House.objects()
    return make_response(jsonify(houses), 200)


@app.route('/api/show_household/<h_id>', methods=['GET'])
def show_household(h_id):
    try:
        house = House.objects.get(house_id=h_id)
        return make_response(jsonify(house), 200)
    except DoesNotExist:
        return make_response(f'House ID: {h_id} does not exist!', 400)


@app.route('/api/del_household/<h_id>', methods=['DELETE'])
def del_household(h_id):
    try:
        House.objects.get(house_id=h_id).delete()
        return make_response(f'House ID: {h_id} deleted successfully', 200)
    except Exception:
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
    return make_response('', 200)


@app.route('/api/show_household/<grant>', methods=['GET']) <<<???
def grant_disbursement(grant):


if __name__ == "__main__":
    app.run(debug=True)