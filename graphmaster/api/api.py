import os
import sys
import flask
import flask_sqlalchemy
import flask_praetorian
import flask_cors
from flask_mail import Mail, Message

db = flask_sqlalchemy.SQLAlchemy()
guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()


# A generic user model that might be used by an app powered by flask-praetorian
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    roles = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, server_default='true')

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []
    
    @property
    def identity(self):
        return self.id

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    def is_valid(self):
        return self.is_active


# Initialize flask app for the example
app = flask.Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'top secret'
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# mail config. Set gmail username+password in seperate env-file .env
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ['GMAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['GMAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = ('Graphmaster', app.config['MAIL_USERNAME'])
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail= Mail(app)

try:  
    os.environ["GMAIL_PASSWORD"]
    os.environ["GMAIL_USERNAME"]
except KeyError: 
   print("Please set the environment variable GMAIL_PASSWORD and USERNAME")
   sys.exit(1)

# Initialize the flask-praetorian instance for the app
guard.init_app(app, User)

# Initialize local database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.getcwd(), 'database.db')}"
db.init_app(app)

# Initializes CORS so that the api_tool can talk to the app
cors.init_app(app)

# Add default users
with app.app_context():
    db.create_all()
    if db.session.query(User).filter_by(username='Erik').count() < 1:
        db.session.add(User(
            username='Erik',
            # Important to hash the created password
            password=guard.hash_password('strongpassword'),
            roles='admin'
        ))
    db.session.commit()


# Set up routes
@app.route('/api/')
def home():
    return {"Hello": "World"}, 200


@app.route("/api/mailme")
def index():
    msg = Message("Hello",
                recipients=["erik.karlsson97@outlook.com"])
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)
    return "Sent"


@app.route('/api/login', methods=['POST'])
def login():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.
    .. example::
       $ curl http://localhost:5000/api/login -X POST \
         -d '{"username":"admin","password":"strongpassword"}'
    """
    req = flask.request.get_json(force=True)
    
    username = req.get('username', None)
    password = req.get('password', None)
    user = guard.authenticate(username, password)
    ret = {'access_token': guard.encode_jwt_token(user)}
    return ret, 200


@app.route('/api/refresh', methods=['POST'])
def refresh():
    """
    Refreshes an existing JWT by creating a new one that is a copy of the old
    except that it has a refrehsed access expiration.
    .. example::
       $ curl http://localhost:5000/api/refresh -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    print("refresh request")
    old_token = guard.read_token_from_header()
    new_token = guard.refresh_jwt_token(old_token)
    ret = {'access_token': new_token}
    return ret, 200


@app.route('/api/protected')
@flask_praetorian.auth_required
def protected():
    """
    A protected endpoint. The auth_required decorator will require a header
    containing a valid JWT
    .. example::
       $ curl http://localhost:5000/api/protected -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    return {'message': f'protected endpoint (allowed user {flask_praetorian.current_user().username})'}


@app.route('/api/disable_user', methods=['POST'])
@flask_praetorian.auth_required
@flask_praetorian.roles_required('admin')
def disable_user():
    """
    Disables a user in the data store
    .. example::
        $ curl http://localhost:5000/disable_user -X POST \
          -H "Authorization: Bearer <your_token>" \
          -d '{"username":"Walter"}'
    """
    req = flask.request.get_json(force=True)
    usr = User.query.filter_by(username=req.get('username', None)).one()
    usr.is_active = False
    db.session.commit()
    return flask.jsonify(message='disabled user {}'.format(usr.username))


@app.route('/api/register', methods=['POST'])
def register():
    """
    Registers a new user by parsing a POST request containing new user info and
    dispatching an email with a registration token

    .. example::
       $ curl http://localhost:5000/register -X POST \
         -d '{
           "username":"Brandt", \
           "password":"herlifewasinyourhands" \
           "email":"brandt@biglebowski.com"
         }'
    """
    req = flask.request.get_json(force=True)[0]
    username = req.get('username', None)
    email = req.get('email', None)
    password = req.get('password', None)
    new_user = User(
        username=username,
        password=guard.hash_password(password),
        is_active=False
    )
    db.session.add(new_user)
    db.session.commit()
    guard.send_registration_email(email, user=new_user, confirmation_sender= ('Graphmaster', 'bot@graphmaster.io'), confirmation_uri='http://localhost:5000/finalize' )
    ret = {'message': 'successfully sent registration email to user {}'.format(
        new_user.username
    )}
    return ret, 201


@app.route('/api/finalize')
def finalize():
    """
    Finalizes a user registration with the token that they were issued in their
    registration email.

    .. example::
       $ curl http://localhost:5000/api/finalize -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    registration_token = guard.read_token_from_header()
    user = guard.get_user_from_registration_token(registration_token)
    # perform 'activation' of user here...like setting 'active' or something
    user.is_active = True
    db.session.commit()

    ret = {'access_token': guard.encode_jwt_token(user)}
    return ret, 200



# Run the api
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
