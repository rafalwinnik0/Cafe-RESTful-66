from flask import Flask, jsonify, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
        # dictionary = {}
        # for column in self.__table__.columns:
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/random')
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(random_cafe.to_dict())

@app.route('/all')
def show_all():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafe=[cafe.to_dict() for cafe in cafes])

@app.route('/search')
def search():
    cafe_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=cafe_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})

@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def patch_the_price(cafe_id):
    if cafe_id:
        cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
        new_price = request.args.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify({"success": "Successfully updated the price"})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"})

@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    if request.args.get("api_key") == "TopSecret":
        cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify({"success": "Successfully delete the price"})
        else:
            return jsonify({"Not Found": "Sorry a cafe with that ID was not found in the databse"})
    else:
        return jsonify(error={"Not Found": "Sorry, that's not allowed. Make sure you have the correct api_key."})

if __name__ == '__main__':
    app.run(debug=True)
