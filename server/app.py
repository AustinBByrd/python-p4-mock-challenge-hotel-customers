#!/usr/bin/env python3

from models import db, Hotel, HotelCustomer, Customer
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Mock Code challenge</h1>'

class HotelList(Resource):
    def get(self):
        hotels = Hotel.query.all()
        hotel_list = [hotel.to_dict(only=('id', 'name')) for hotel in hotels]
        return hotel_list, 200
    
class HotelResource(Resource):
    def get(self, id):
        hotel = Hotel.query.get(id)
        if hotel is None:
            return {"error": "Hotel not found"}, 404
        
        hotel_data = hotel.to_dict(only=('id', 'name'))
        hotel_data['hotel_customers'] = [
            {
                "id": hc.id,
                "rating": hc.rating,
                "hotel_id": hc.hotel_id,
                "customer_id": hc.customer_id,
                "customer": {
                    "id": hc.customer.id,
                    "first_name": hc.customer.first_name,
                    "last_name": hc.customer.last_name
                }
            } for hc in hotel.hotel_ratings
        ]
        return hotel_data, 200

    def delete(self, id):
        hotel = Hotel.query.get(id)
        if hotel is None:
            return {"error": "Hotel not found"}, 404
        
        db.session.delete(hotel)
        db.session.commit()

        return '', 204 

class CustomerList(Resource):
    def get(self):
        customers = Customer.query.all()
        customer_list = [customer.to_dict(only=('id', 'first_name', 'last_name')) for customer in customers]
        return customer_list, 200

class HotelCustomerResource(Resource):
    def post(self):
        data = request.get_json()
        rating = data.get('rating')
        hotel_id = data.get('hotel_id')
        customer_id = data.get('customer_id')

        if not all([rating is not None, hotel_id, customer_id]):
            return {"errors": ["validation errors"]}, 400
        
        if not 1 <= rating <= 5:
            return {"errors": ["validation errors"]}, 400
        
        try:
            hotel = Hotel.query.get(hotel_id)
            customer = Customer.query.get(customer_id)
            if not hotel or not customer:
                return {"errors": ["validation errors"]}, 400
            
            hotel_customer = HotelCustomer(rating=rating, hotel_id=hotel_id, customer_id=customer_id)
            db.session.add(hotel_customer)
            db.session.commit()

            response_data = hotel_customer.to_dict(only=('id', 'rating', 'hotel_id', 'customer_id'))
            response_data['hotel'] = hotel_customer.hotel.to_dict(only=('id', 'name'))
            response_data['customer'] = hotel_customer.customer.to_dict(only=('id', 'first_name', 'last_name'))

            return response_data, 201


        except Exception as e:
            print(f"Error: {e}")
            return {"errors": ["validation errors"]}, 500

api.add_resource(HotelList, '/hotels')
api.add_resource(HotelResource, '/hotels/<int:id>')
api.add_resource(CustomerList, '/customers')
api.add_resource(HotelCustomerResource, '/hotel_customers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
