import flask
import flask_praetorian
import flask_cors
from flask_mail import Mail, Message

from .model import User, db, influx_db

guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()
app = flask.Flask(__name__)
app.debug = True
app.config.from_object("api.config")
mail = Mail(app)

# Initialize the flask-praetorian instance for the app
guard.init_app(app, User)

# Initialize local database
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
    req = flask.request.get_json(force=True)
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
    guard.send_registration_email(email, user=new_user, confirmation_sender=(
        'Graphmaster', 'bot@graphmaster.io'), confirmation_uri='http://localhost:3000/finalize')
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


# Error handling
jsonify = flask.jsonify
g = flask.g


@app.errorhandler(400)
@app.errorhandler(422)
def bad_request(err):
    try:
        headers = err.data.get('headers', None)
        messages = err.data.get('messages', [err.description])
    except AttributeError:
        headers = None
        messages = [err.description]
    body = jsonify(
        error='BAD_REQUEST' if err.code == 400 else 'UNPROCESSABLE_ENTITY',
        messages=messages
    )
    if headers:
        return body, err.code, headers
    else:
        return body, err.code


@app.errorhandler(403)
def not_found(err):
    return jsonify(error='FORBIDDEN', messages=[err.description]), 403


@app.errorhandler(404)
def not_found(err):
    return jsonify(error='NOT_FOUND', messages=[err.description]), 404


@app.errorhandler(405)
def method_not_allowed(err):
    return jsonify(error='METHOD_NOT_ALLOWED', messages=[err.description]), 405


@app.errorhandler(500)
def internal_server_error(err):
    if g.sentry_event_id:
        messages = [
            ('An unknown error has occured. Please try again. '
             'If the problem persists, please contact support with your error '
             'event identifier at hand. Your error event identifier is ') +
            g.sentry_event_id
        ]
    else:
        messages = ['An unknown error has occured. Please try again.']
    return jsonify(
        error='INTERNAL_SERVER_ERROR',
        messages=messages
    ), 500


# Run the api
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
