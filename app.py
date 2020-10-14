from flask import Flask, jsonify, request, make_response
from flask_mongoengine import MongoEngine
import json
from mongoengine import DoesNotExist, NotUniqueError
from datetime import datetime, date

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
    # family_size = db.IntField(default=0)


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
        # House.objects.get(house_id=h_id).update(family=family_arr, family_size=len(family_arr))
        return make_response(f"Successfully added family member to House ID: {h_id}", 201)
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


def rm_spouse(fam_list):
    '''
    removes the 'spouse' key from the list of family members
    '''
    for member in fam_list:
        member.pop('spouse', None)


@app.route('/api/del_household/<h_id>', methods=['DELETE'])
def del_household(h_id):
    try:
        House.objects.get(house_id=h_id).delete()
        return make_response(f'House ID: {h_id} deleted successfully', 200)
    except Exception as e:
        print(e)
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

    # House.objects.get(house_id=h_id).update(family=new_family, family_size=len(new_family))
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
    h = House.objects.filter(family__size=int(h_size)).to_json()
    h = json.loads(h)
    # print(h)
    # if h is empty, tell user
    res = {
        'Student Encouragement Bonus': [],
        'Family Togetherness': {},
        'Elder Bonus': {},
        'Baby SunShine Grant': {},
        'YOLO GST Grant': {}
    }

    res['YOLO GST Grant']['house_id'] = [yolo_grant(house, 100000) for house in h]

    for house in h:
        res.get('Student Encouragement Bonus').append(seb(house, 150000))

    return make_response(jsonify(res), 200)
    # return make_response('', 200)


def seb(house, threshold):
    '''
    :return: a dict
    '''
    res = dict()
    family_list = list()
    age_arr = get_age(house['family'])
    total_income = cal_income(house['family'])
    if total_income < threshold:
        for member in age_arr:
            if member['age'] < 16:
                family_list.append({'id': member['id'], 'name': member['name']})
    if family_list:
        res['house_id'] = house['house_id']
        res['family'] = family_list
    return res



def get_age(fam_arr):
    '''
    for every family member. get their age
    return a dict {'name' : ... , 'age': ...}
    '''
    new_arr = list()
    for member in fam_arr:
        # print(f"get_age -> {member}")
        date_obj = datetime.strptime(member['dob'], "%d-%m-%Y")
        # print(member['dob'])
        new_arr.append({
                'id': member['id'],
                'name': member['name'],
                'age': calculate_age(date_obj),
            })
    # print(new_arr)
    return new_arr


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def yolo_grant(h, threshold):
    '''
    retrieve households that qualify for the YOLO GST Grant
    returns the house_id
    '''
    total_income = cal_income(h['family'])
    if total_income < threshold:
        return h['house_id']
    return None


def cal_income(fam_arr):
    '''
    calculate total annual income of the family
    '''
    total_income = 0
    for member in fam_arr:
        total_income += member['annualIncome']
    return total_income


if __name__ == "__main__":
    app.run(debug=True)