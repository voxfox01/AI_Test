# Parking Monitor

This repository contains a sample Flask application that demonstrates a basic parking management system for rental properties. It allows guests or residents to register vehicles and provides simple dashboards for property managers and security staff.

## Requirements

- Python 3.10+
- MySQL server

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the MySQL URI in `parking_app/__init__.py` to match your database credentials.

## Running the Application

```bash
python run.py
```

Open `http://localhost:5000` in your browser.

This is a minimal starter project. It can be extended with authentication, camera-based license plate recognition, and more sophisticated dashboards.
