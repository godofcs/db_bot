import sqlalchemy
from database.clients import Client
from database.bookings import Booking
from database.tours import Tour
from database.tour_operators import TourOperator
from database.bonus import Bonus
import json
from database import db_session


def create_new_client(name, type, telphone, email, password):
    client = Client()
    client.name = name
    client.type = type
    client.telephone = telphone
    client.email = email
    client.set_password(password)
    session = db_session.create_session()
    session.add(client)
    session.commit()
    session.close()


def see_all_client():
    session = db_session.create_session()
    clients = session.query(Client).all()
    for client in clients:
        print(f"{client.id}, {client.name}, {client.type}, {client.telephone}, {client.email}, {client.bonus}, {client.password}")
    session.close()


def create_new_tour(name, season_price: json, dates, description, place: json, duration, limit, operator):
    tour = Tour()
    tour.name = name
    tour.season_price = season_price
    tour.dates = dates
    tour.description = description
    tour.place = place
    tour.duration = duration
    tour.limit = limit
    tour.id_operator = operator  # TODO посмотреть что мы будем передавать id, или нет (лучше передавать id)
    session = db_session.create_session()
    session.add(tour)
    session.commit()
    session.close()


def see_all_tour():
    session = db_session.create_session()
    tours = session.query(Tour).all()
    for tour in tours:
        print(f"{tour.id}, {tour.name}, {tour.season_price}, {tour.dates}, {tour.description}, {tour.place}, {tour.duration}, {tour.limit}, {tour.id}")
    session.close()


def create_new_tour_operator(name, description, telephone, email, password):
    tour_operator = TourOperator()
    tour_operator.name = name
    tour_operator.description = description
    tour_operator.telephone = telephone
    tour_operator.email = email
    tour_operator.set_password(password)
    session = db_session.create_session()
    session.add(tour_operator)
    session.commit()
    session.close()


def see_all_tour_operator():
    session = db_session.create_session()
    tour_operators = session.query(TourOperator).all()
    for operator in tour_operators:
        print(
            f"{operator.id}, {operator.name}, {operator.description}, {operator.telephone}, {operator.email}, {operator.password}")
    session.close()


def create_new_booking(client_id, tour_id, date, count):
    booking = Booking()
    booking.id_client = client_id
    booking.id_tour = tour_id
    booking.date = date
    booking.count = count
    session = db_session.create_session()
    session.add(booking)
    session.commit()
    session.close()


def see_all_booking():
    session = db_session.create_session()
    bookings = session.query(Booking).all()
    for booking in bookings:
        print(
            f"{booking.id}, {booking.id_client}, {booking.id_tour}, {booking.date}, {booking.count}")
    session.close()


def create_new_bonus(client_id, operator_id, count):
    bonus = Bonus()
    bonus.id_client = client_id
    bonus.id_tour = operator_id
    bonus.count = count
    session = db_session.create_session()
    session.add(bonus)
    session.commit()
    session.close()


def see_all_bonus():
    session = db_session.create_session()
    bonus = session.query(Bonus).all()
    for one_bonus in bonus:
        print(
            f"{one_bonus.id}, {one_bonus.id_client}, {one_bonus.id_tour}, {one_bonus.count}")
    session.close()


def find_tour_operator_by_email(email):
    session = db_session.create_session()
    answer = session.query(TourOperator).filter_by(email=email).first()
    #print(answer.name)
    session.close()
    return answer


def find_client_by_email(email):
    session = db_session.create_session()
    answer = session.query(Client).filter_by(email=email).first()
    #print(answer.name)
    session.close()
    return answer


def auth_tour_operator(email, password):
    session = db_session.create_session()
    answer = session.query(TourOperator).filter_by(email=email).first()
    # print(answer.name)
    session.close()
    if answer.check_password(password):
        return [answer.check_password(password), answer.id]
    return [answer.check_password(password), -1]


def auth_client(email, password):
    session = db_session.create_session()
    answer = session.query(Client).filter_by(email=email).first()
    # print(answer.name)
    session.close()
    if answer.check_password(password):
        return [answer.check_password(password), answer.id]
    return [answer.check_password(password), -1]


def get_all_my_tour(tour_operator_id):
    session = db_session.create_session()
    answer = session.query(Tour).filter_by(id_operator=tour_operator_id).all()
    session.close()
    return answer


def delete_tour(tour):
    session = db_session.create_session()
    all_bookings = session.query(Booking).filter_by(id_tour=tour.id).all()
    for booking in all_bookings:
        session.delete(booking)
        session.commit()
    session.delete(tour)
    session.commit()
    session.close()


def update_tour(tour):
    session = db_session.create_session()
    old_tour = session.query(Tour).filter_by(id=tour.id).first()
    old_tour = tour
    session.merge(old_tour)
    session.commit()
    session.close()


def get_tour_operator_by_id(tour_operator_id):
    session = db_session.create_session()
    tour_operator = session.query(TourOperator).filter_by(id=tour_operator_id).first()
    session.close()
    return tour_operator


def update_tour_operator(tour_operator):
    session = db_session.create_session()
    old_tour_operator = session.query(TourOperator).filter_by(id=tour_operator.id).first()
    old_tour_operator = tour_operator
    session.merge(old_tour_operator)
    session.commit()
    session.close()


def get_all_tour():
    session = db_session.create_session()
    all_tour = session.query(Tour).all()
    session.close()
    return all_tour


def register_client_to_tour(client_id, tour_id, date, kol):
    if not check_bookoing_from_one_tour(tour_id, date, kol):
        return False
    booking = Booking()
    booking.id_client = client_id
    booking.id_tour = tour_id
    booking.date = date
    booking.count = kol
    session = db_session.create_session()
    session.add(booking)
    session.commit()
    session.close()
    return True


def check_bookoing_from_one_tour(tour_id, date, kol):
    session = db_session.create_session()
    all_bookings = session.query(Booking).filter_by(id_tour=tour_id, date=date).all()
    kol_bookings = 0
    for booking in all_bookings:
        kol_bookings += booking.count
    tour = session.query(Tour).filter_by(id=tour_id).first()
    session.close()
    if kol_bookings + kol > tour.limit:
        return False
    return True


def get_client_by_id(client_id):
    session = db_session.create_session()
    client = session.query(Client).filter_by(id=client_id).first()
    session.close()
    return client


def update_client(client):
    session = db_session.create_session()
    old_client = session.query(TourOperator).filter_by(id=client.id).first()
    old_client = client
    session.merge(client)
    session.commit()
    session.close()


def give_bonus_to_tour(tour_operator_id, tour_id, date, count):
    session = db_session.create_session()
    all_bookings = session.query(Booking).filter_by(id_tour=tour_id, date=date).all()
    for boking in all_bookings:
        #TODO проверить, что при пустом поле возвращается None
        bonus = session.query(Bonus).filter_by(id_client=boking.id_client, id_operator=tour_operator_id).first()
        if bonus is None:
            bonus = Bonus()
            bonus.id_client = boking.id_client
            bonus.id_operator = tour_operator_id
            bonus.count = count * boking.count
            session.add(bonus)
            session.commit()
        else:
            bonus.count += count * boking.count
            session.merge(bonus)
            session.commit()
    session.close()


def delete_bookings_tour(tour_id, date):
    session = db_session.create_session()
    bookings = session.query(Booking).filter_by(id_tour=tour_id, date=date).all()
    for boking in bookings:
        session.delete(boking)
        session.commit()
    session.close()


def get_all_my_bonus(client_id):
    session = db_session.create_session()
    bonus = session.query(Bonus).filter_by(id_client=client_id).all()
    res = []
    for bon in bonus:
        res += [[session.query(TourOperator).filter_by(id=bon.id_operator).first().name, str(bon.count)]]
    session.close()
    return res


def get_all_my_bookings(client_id):
    session = db_session.create_session()
    bookings = session.query(Booking).filter_by(id_client=client_id).all()
    res = []
    for booking in bookings:
        res += [[session.query(Tour).filter_by(id=booking.id_tour).first().name, booking]]
    session.close()
    return res


def delete_booking_by_id(booking):
    session = db_session.create_session()
    session.delete(booking)
    session.commit()
    session.close()