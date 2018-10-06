from flask import Flask, render_template, flash, request, redirect
from flask import url_for, make_response, jsonify
from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, User
from sqlalchemy import desc
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

# Google client_id
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to database
engine = create_engine('sqlite:///item.db')
Base.metadata.bind = engine

# Create session
DBSession = sessionmaker(bind=engine)
session = DBSession()
Base.metadata.create_all(engine)

# uploads images
UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# specify allowed file extensions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Add new user into database
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:  # noqa: E722
        return None


# send images from directory
@app.route('/upload/full/<filename>')
def send_img(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

# main page


@app.route('/')
@app.route("/hello")
def Hello():
    engine = create_engine('sqlite:///item.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    items = session.query(Item).all()
    return render_template(
        'site.html', items=items, login_session=login_session)


# Create anti-forgery state token
@app.route('/login')
def showlogin():
    state = ''.join(random.choice(
        string.ascii_uppercase+string.digits)for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius:
     150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        return '''<html><h2>Current user not connected.</h2>
        <script>setTimeout(function() {window.location.href = '.';}, 4000);
        </script></html>'''
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = ('''https://accounts.google.com/o/oauth2/revoke?token=%s'''  # NOQA
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return '''<html><h2>Successfully disconnected.</h2>
        <script>setTimeout(function() {window.location.href = '.';},
         4000);</script></html>'''
    else:
        return '''<html><h2>Failed to revoke token for given user.'</h2>
        <script>setTimeout(function() {window.location.href = '.';}, 4000);
        </script></html>'''


# view item with details
@app.route('/viewitem/<id>')
def viewitem(id):
    engine = create_engine('sqlite:///item.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one()
    item.views += 1
    session.add(item)
    session.commit()
    return render_template('view.html', i=item)


# creates new item if logged in
@app.route('/items/new', methods=['GET', 'POST'])
def newitem():
    key = "new"
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        filename = 'default.jpg'
        # checks for file and it's format
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        newitem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category=request.form['category'], img_path=filename,
                       user_id=login_session['gplus_id'],
                       user_email=login_session['email'])
        session.add(newitem)
        session.commit()
        return redirect(url_for('Hello'))
    else:
        return render_template('form.html', key=key)


# edit item if logged in
@app.route('/items/edit/<id>', methods=['GET', 'POST'])
def edititem(id):
    key = "edit"
    engine = create_engine('sqlite:///item.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    edititem = session.query(Item).filter_by(id=id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if edititem.user_email != login_session['email']:
        return "<h1>Acess denied,nice try</h1>"
    if request.method == 'POST':
        filename = edititem.img_path
        # checks for file and it's format
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        edititem.name = request.form['name']
        edititem.description = request.form['description']
        edititem.category = request.form['category']
        edititem.img_path = filename
        session.add(edititem)
        session.commit()
        return redirect(url_for('Hello'))
    else:
        return render_template('form.html', key=key)


# delete item if logged in
@app.route('/items/delete/<id>', methods=['GET', 'POST'])
def deleteitem(id):
    engine = create_engine('sqlite:///item.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if item.user_email != login_session['email']:
        return "<h1>Acess denied,nice try</h1>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('Hello'))
    else:
        return render_template('delete_confirm.html', item=item)


# send specific item details with json format
@app.route('/item/<int:id>/JSON')
def itemJSON(id):
    engine = create_engine('sqlite:///item.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one()
    return jsonify(Item=item.serialize)


# send details of all items in json format
@app.route('/items/JSON')
def itemJSON():
    engine = create_engine('sqlite:///item.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    items = session.query(Item).all()
    return jsonify(Item=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
