from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from .models import db, User, Property, Vehicle
from . import login_manager

bp = Blueprint('main', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@bp.route('/')
def index():
    properties = Property.query.all()
    return render_template('index.html', properties=properties)


@bp.route('/register_vehicle', methods=['GET', 'POST'])
@login_required
def register_vehicle():
    if request.method == 'POST':
        plate = request.form['license_plate']
        apartment = request.form.get('apartment')
        prop_id = request.form.get('property_id')
        is_guest = request.form.get('is_guest') == 'on'
        vehicle = Vehicle(
            license_plate=plate,
            apartment=apartment,
            property_id=prop_id,
            user_id=request.form.get('user_id'),
            is_guest=is_guest,
        )
        db.session.add(vehicle)
        db.session.commit()
        return redirect(url_for('main.index'))

    properties = Property.query.all()
    return render_template('register_vehicle.html', properties=properties)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user)
            return redirect(url_for('main.index'))
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
