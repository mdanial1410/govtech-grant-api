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
    # gender = db.StringField(required=True)
    # maritalStatus = db.StringField(required=True)
    # spouse = db.StringField(required=True)
    # occupationType = db.StringField(required=True)
    # annualIncome = db.StringField(required=True)
    # dob = db.StringField(required=True)


class House(db.Document):
    house_id = db.IntField(required=True, unique=True)
    housingType = db.StringField(required=True)
    family = db.EmbeddedDocumentListField(Family)


@app.route('/api/create_household', methods=['POST'])
def create_household():
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
        return make_response(f"Duplicated House ID detected!\n"
                             f"These were successfully created-> House ID: {h_id}", 400)


@app.route('/api/add_family/<h_id>', methods=['POST'])
def add_family(h_id):
    '''
    check if family member alrdy exists. append if not.
    '''
    content = request.json
    h = House.objects.get(house_id=h_id).to_json()
    h = json.loads(h)
    print(h)
    family = h['family']
    print(f"family = {family}")
    print(f"content = {content['family']}")
    if family:
        count = family[-1].get('id') + 1
    else:
        count = 1
    print(f"count-> {count}")
    for name in content['family']:
        name.update({'id': count})
        family.append(name)
        count += 1
    print(family)
    House.objects.get(house_id=h_id).update(family=family)

    # if family:
    #     for name in content['family']:
    #         family.append(name)
    # print(family)
    # House.objects.get(house_id=h_id).update(family=family)

    # family = [{'name':'boy'}]
    # h = House(house_id=10, housingType="asd", family=family)
    # h.save()
    # House.objects.get(house_id=h_id).update(**content)

    # print(h['family'])
    # print(h.to_json())
    # h.family.append(content['family'])
    # h.save()
    return make_response('', 200)
    # return make_response(f"Added family member in House ID:{h_id} successfully", 201)


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


if __name__ == "__main__":
    app.run(debug=True)