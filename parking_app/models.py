from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class Type2Mixin:
    """Mixin that provides Type 2 slowly changing dimension fields."""

    Creation_Date = db.Column(db.DateTime, default=datetime.utcnow)
    Modification_Date = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    Current_Flag = db.Column(db.Boolean, default=True)
    Status_ID = db.Column(db.Integer, db.ForeignKey("Status_CD.Status_ID"), default=1)


class StatusCD(db.Model):
    __tablename__ = "Status_CD"

    Status_ID = db.Column(db.Integer, primary_key=True)
    CD_Code = db.Column(db.String(1), unique=True, nullable=False)
    Description = db.Column(db.String(50), nullable=False)


class PropertyCustomer(db.Model, Type2Mixin):
    __tablename__ = "Property_Customers"

    Property_ID = db.Column(db.Integer, primary_key=True)
    Property_Name = db.Column(db.String(128), nullable=False)
    Property_Address = db.Column(db.String(256))
    Property_City = db.Column(db.String(100))
    Property_State = db.Column(db.String(2))
    Property_Zip = db.Column(db.String(10))
    Contact_Number = db.Column(db.String(20))

    users = db.relationship("User", backref="property", lazy=True)
    parking_customers = db.relationship("ParkingCustomer", backref="property", lazy=True)
    security_links = db.relationship(
        "SecurityProperty", backref="property", lazy=True
    )



class SecurityCustomer(db.Model, Type2Mixin):
    __tablename__ = "Security_Customers"

    Security_ID = db.Column(db.Integer, primary_key=True)
    Security_Name = db.Column(db.String(128), nullable=False)
    Security_Address = db.Column(db.String(256))
    Security_City = db.Column(db.String(100))
    Security_State = db.Column(db.String(2))
    Security_Zip = db.Column(db.String(10))

    users = db.relationship("User", backref="security", lazy=True)
    properties = db.relationship("SecurityProperty", backref="security", lazy=True)


class SecurityProperty(db.Model, Type2Mixin):
    __tablename__ = "Security_Properties_dim"

    Security_Property_ID = db.Column(db.Integer, primary_key=True)
    Security_ID = db.Column(
        db.Integer, db.ForeignKey("Security_Customers.Security_ID"), nullable=False
    )
    Property_ID = db.Column(
        db.Integer, db.ForeignKey("Property_Customers.Property_ID"), nullable=False
    )


class User(db.Model, UserMixin, Type2Mixin):
    __tablename__ = "Users"

    User_ID = db.Column(db.Integer, primary_key=True)
    Security_ID = db.Column(db.Integer, db.ForeignKey("Security_Customers.Security_ID"))
    Property_ID = db.Column(db.Integer, db.ForeignKey("Property_Customers.Property_ID"))
    First_Name = db.Column(db.String(50))
    Last_Name = db.Column(db.String(50))
    Role = db.Column(db.String(50), nullable=False)

    credentials = db.relationship("Credential", backref="user", uselist=False)
    monitors = db.relationship("ParkingMonitoring", backref="user", lazy=True)

    def get_id(self) -> str:  # pragma: no cover - simple accessor
        return str(self.User_ID)


class Credential(db.Model, Type2Mixin):
    __tablename__ = "Credentials"

    Credential_ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey("Users.User_ID"), nullable=False)
    Username = db.Column(db.String(80), unique=True, nullable=False)
    Password_Hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        self.Password_Hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.Password_Hash, password)


class ParkingCustomer(db.Model, Type2Mixin):
    __tablename__ = "Parking_Customers"

    Parking_Customer_ID = db.Column(db.Integer, primary_key=True)
    Property_ID = db.Column(
        db.Integer, db.ForeignKey("Property_Customers.Property_ID"), nullable=False
    )
    First_Name = db.Column(db.String(50))
    Last_Name = db.Column(db.String(50))
    Unit = db.Column(db.String(20))
    License_Plate = db.Column(db.String(20), nullable=False)
    Departure_Date = db.Column(db.DateTime, nullable=False)


class ParkingMonitoring(db.Model, Type2Mixin):
    __tablename__ = "Parking_Monitoring"

    Parking_Monitor_ID = db.Column(db.Integer, primary_key=True)
    User_ID = db.Column(db.Integer, db.ForeignKey("Users.User_ID"))
    Property_ID = db.Column(
        db.Integer, db.ForeignKey("Property_Customers.Property_ID"), nullable=False
    )
    License_Plate = db.Column(db.String(20), nullable=False)
    Registered_Flag = db.Column(db.Boolean, default=False)
