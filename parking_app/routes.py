from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user

from .models import (
    db,
    User,
    PropertyCustomer,
    ParkingCustomer,
    SecurityCustomer,
    SecurityProperty,
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


@bp.route('/signup/property', methods=['GET', 'POST'])
def signup_property():
    if request.method == 'POST':
        name = request.form['property_name']
        address = request.form['property_address']
        city = request.form['property_city']
        state = request.form['property_state']
        zip_code = request.form['property_zip']
        contact = request.form['contact_number']
        username = request.form['username']
        password = request.form['password']

        prop = PropertyCustomer(
            Property_Name=name,
            Property_Address=address,
            Property_City=city,
            Property_State=state,
            Property_Zip=zip_code,
            Contact_Number=contact,
        )
        db.session.add(prop)
        db.session.flush()

        user = User(Role='property_owner', Property_ID=prop.Property_ID)
        db.session.add(user)
        db.session.flush()

        cred = Credential(User_ID=user.User_ID, Username=username)
        cred.set_password(password)
        db.session.add(cred)
        db.session.commit()

        login_user(user)
        return redirect(url_for('main.owner_dashboard'))

    return render_template('signup_property.html')


@bp.route('/signup/security', methods=['GET', 'POST'])
def signup_security():
    if request.method == 'POST':
        name = request.form['security_name']
        address = request.form['security_address']
        city = request.form['security_city']
        state = request.form['security_state']
        zip_code = request.form['security_zip']
        username = request.form['username']
        password = request.form['password']

        sec = SecurityCustomer(
            Security_Name=name,
            Security_Address=address,
            Security_City=city,
            Security_State=state,
            Security_Zip=zip_code,
        )
        db.session.add(sec)
        db.session.flush()

        user = User(Role='security_admin', Security_ID=sec.Security_ID)
        db.session.add(user)
        db.session.flush()

        cred = Credential(User_ID=user.User_ID, Username=username)
        cred.set_password(password)
        db.session.add(cred)
        db.session.commit()

        login_user(user)
        return redirect(url_for('main.security_dashboard'))

    return render_template('signup_security.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cred = Credential.query.filter_by(Username=username, Current_Flag=True).first()
        if cred and cred.check_password(password):
            login_user(cred.user)
            if cred.user.Role == 'property_owner':
                return redirect(url_for('main.owner_dashboard'))
            if cred.user.Role in ['security_admin', 'security_guard']:
                return redirect(url_for('main.security_dashboard'))
            return redirect(url_for('main.index'))
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/owner_dashboard', methods=['GET', 'POST'])
@login_required
def owner_dashboard():
    if current_user.Role != 'property_owner':
        return redirect(url_for('main.index'))

    property_obj = current_user.property
    security_companies = SecurityCustomer.query.all()
    assigned = SecurityProperty.query.filter_by(
        Property_ID=property_obj.Property_ID, Current_Flag=True
    ).all()

    if request.method == 'POST':
        security_id = request.form.get('security_id')
        if security_id:
            existing = SecurityProperty.query.filter_by(
                Property_ID=property_obj.Property_ID,
                Security_ID=security_id,
                Current_Flag=True,
            ).first()
            if not existing:
                link = SecurityProperty(
                    Property_ID=property_obj.Property_ID, Security_ID=security_id
                )
                db.session.add(link)
                db.session.commit()
            return redirect(url_for('main.owner_dashboard'))

    reg_count = ParkingCustomer.query.filter_by(
        Property_ID=property_obj.Property_ID
    ).count()

    return render_template(
        'owner_dashboard.html',
        property=property_obj,
        security_companies=security_companies,
        assigned=assigned,
        registered_count=reg_count,
    )


@bp.route('/security_dashboard', methods=['GET', 'POST'])
@login_required
def security_dashboard():
    if current_user.Role not in ['security_admin', 'security_guard']:
        return redirect(url_for('main.index'))

    security_obj = current_user.security
    properties = [
        link.property for link in security_obj.properties if link.Current_Flag
    ]
    employees = User.query.filter_by(
        Security_ID=security_obj.Security_ID, Current_Flag=True
    ).all()

    if request.method == 'POST' and current_user.Role == 'security_admin':
        first = request.form['first_name']
        last = request.form['last_name']
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        new_user = User(
            First_Name=first,
            Last_Name=last,
            Role=role,
            Security_ID=security_obj.Security_ID,
        )
        db.session.add(new_user)
        db.session.flush()

        cred = Credential(User_ID=new_user.User_ID, Username=username)
        cred.set_password(password)
        db.session.add(cred)
        db.session.commit()
        return redirect(url_for('main.security_dashboard'))

    return render_template(
        'security_dashboard.html',
        security=security_obj,
        properties=properties,
        employees=employees,
    )


@bp.route('/remove_employee/<int:user_id>', methods=['POST'])
@login_required
def remove_employee(user_id):
    if current_user.Role != 'security_admin':
        return redirect(url_for('main.security_dashboard'))

    user = User.query.filter_by(
        User_ID=user_id,
        Security_ID=current_user.Security_ID,
        Current_Flag=True,
    ).first()
    if user:
        user.Current_Flag = False
        if user.credentials:
            user.credentials.Current_Flag = False
        db.session.commit()
    return redirect(url_for('main.security_dashboard'))
