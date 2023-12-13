from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hotel(db.Model, SerializerMixin):
    __tablename__ = 'hotels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    customers = db.relationship('Customer', secondary='hotel_customers', back_populates='hotels')

    def __repr__(self):
        return f'<Hotel {self.name}>'


class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    hotels = db.relationship('Hotel', secondary='hotel_customers', back_populates='customers')


    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name}>'


class HotelCustomer(db.Model, SerializerMixin):
    __tablename__ = 'hotel_customers'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    hotel = db.relationship('Hotel', backref=db.backref('hotel_ratings', cascade='all, delete-orphan'))
    customer = db.relationship('Customer', backref=db.backref('customer_ratings', cascade='all, delete-orphan'))

    @validates('rating')
    def validate_rating(self, key, rating):
        if not (1 <= rating <= 5):
            raise ValueError(f"Rating must be between 1 and 5, got {rating}")
        return rating

    def __repr__(self):
        return f'<HotelCustomer ★{self.rating}>'
def get_hotel_data(hotel_id):
    hotel = Hotel.query.get(hotel_id)
    if hotel:
        return hotel.to_dict(rules=('-customers',))
    return None

def get_customer_data(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        return customer.to_dict(rules=('-hotels',))
    return None

def get_hotel_customer_data(hotel_customer_id):
    hotel_customer = HotelCustomer.query.get(hotel_customer_id)
    if hotel_customer:
        return hotel_customer.to_dict()
    return None