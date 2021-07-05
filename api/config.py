#!/usr/bin/env python
import os
import sys

#auth
SECRET_KEY = os.environ['SECRET_KEY']
JWT_ACCESS_LIFESPAN = {'hours': 24}
JWT_REFRESH_LIFESPAN = {'minutes': 30}

#db
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getcwd(), 'database.db')}"

INFLUXDB_DATABASE = 'test'
INFLUXDB_HOST = '0.0.0.0'

# mail Set gmail username+password in seperate env-file .env
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = os.environ['GMAIL_USERNAME']
MAIL_PASSWORD = os.environ['GMAIL_PASSWORD']
MAIL_DEFAULT_SENDER = (
    'Graphmaster', MAIL_USERNAME)
MAIL_USE_TLS = False
MAIL_USE_SSL = True

try:
    os.environ["GMAIL_PASSWORD"]
    os.environ["GMAIL_USERNAME"]
except KeyError:
    print("Please set the environment variable GMAIL_PASSWORD and USERNAME")
    sys.exit(1)

