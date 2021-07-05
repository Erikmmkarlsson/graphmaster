#!/usr/bin/env python
import os
import sys

INFLUXDB_DATABASE = 'test'
INFLUXDB_HOST = '0.0.0.0'

SECRET_KEY = os.urandom(24)
JWT_ACCESS_LIFESPAN = {'hours': 24}
JWT_REFRESH_LIFESPAN = {'days': 30}
SQLALCHEMY_TRACK_MODIFICATIONS = False

# mail config. Set gmail username+password in seperate env-file .env
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


SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getcwd(), 'database.db')}"
