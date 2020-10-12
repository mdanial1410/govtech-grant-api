from flask import Flask, jsonify, request, make_response
from flask_mongoengine import MongoEngine


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
        }
}
'''

class Family(db.EmbeddedDocument):
    name = db.StringField()
    # gender = db.StringField()

class House(db.Document):
    house_id = db.IntField(required=True, unique=True)
    housingType = db.StringField(required=True)
    family = db.EmbeddedDocumentListField(Family)

    # def to_json(self):
    #     return {
    #         "house_id": self.house_id,
    #         "housingType": self.housingType,
    #         "family_members": self.family
    #     }

@app.route('/api/create_household', methods=['POST'])
def create_household():
    h_id = list()
    content = request.json
    if isinstance(content, list):
        for item in content:
            h = House(house_id=item['house_id'], housingType=item['housingType'])
            h.save()
            h_id.append(h.house_id)
    else:
        h = House(house_id=content['house_id'], housingType=content['housingType'])
        h.save()
        h_id.append(h.house_id)
    return make_response("House ID: {} successfully created.".format(h_id), 201)


@app.route('/api/add_family/<h_id>', methods=['POST'])
def add_family(h_id):
    content = request.json
    # House.objects.get(house_id=h_id).update(**content)
    h = House.objects.get(house_id=h_id)
    print(h.to_json())
    return make_response("Added family member successfully", 201)

@app.route('/api/list_household', methods=['GET'])
def list_household():
    houses = House.objects()
    return make_response(jsonify(houses), 200)

@app.route('/api/show_household/<h_id>', methods=['GET'])
def show_household(h_id):
    houses = []
    for house in House.objects:
        houses.append(house)
    return make_response(jsonify(houses), 200)


if __name__ == "__main__":
    app.run(debug=True)