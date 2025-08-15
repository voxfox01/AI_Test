from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from .models import (
    db,
    User,
    PropertyCustomer,
    ParkingCustomer,
    Credential,
)
from . import login_manager

bp = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@bp.route('/')
def index():
    properties = PropertyCustomer.query.all()
    return render_template('index.html', properties=properties)


@bp.route('/register_vehicle', methods=['GET', 'POST'])
def register_vehicle():
    if request.method == 'POST':
        prop_id = request.form.get('property_id')
        first = request.form.get('first_name')
        last = request.form.get('last_name')
        unit = request.form.get('unit')
        plate = request.form.get('license_plate')
        departure = datetime.strptime(request.form['departure_date'], '%Y-%m-%d')

        customer = ParkingCustomer(
            Property_ID=prop_id,
            First_Name=first,
            Last_Name=last,
            Unit=unit,
            License_Plate=plate,
            Departure_Date=departure,
        )
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for('main.index'))

    properties = PropertyCustomer.query.all()
    return render_template('register_vehicle.html', properties=properties)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cred = Credential.query.filter_by(Username=username, Current_Flag=True).first()
        if cred and cred.check_password(password):
            login_user(cred.user)
            return redirect(url_for('main.index'))
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
