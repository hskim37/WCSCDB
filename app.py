from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
from werkzeug.utils import secure_filename
import cs304dbi as dbi
app = Flask(__name__)

import random
import cs304dbi as dbi
import sqlOperations
import bcrypt

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

from flask_cas import CAS
from flask_cas import login_required
from flask_cas import logout

# CAS(app)

# app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
# app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
# app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
# app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
# app.config['CAS_AFTER_LOGIN'] = 'logged_in'
# the following doesn't work :-(
# app.config['CAS_AFTER_LOGOUT'] = 'after_logout'


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

nameDB = 'wcscdb_db'
# test values for /register
testName = "Wendy Wellesley"
testYear = 2022
testEmail = "wwellesley15@wellesley.edu"

@app.route('/', methods=["GET","POST"])
def index():
    if request.method=="GET":
        if 'userID' in session:
            return render_template('main.html')
        else: # not logged in
            return render_template('login.html')
    else: # POST
        if request.form.get('submit')=="Login":
            try:
                userID = request.form['userID']
                password = request.form['password'] # the user's input as is
                conn = dbi.connect()
                userInfo = sqlOperations.login(conn,userID)
                if userInfo is None:
                    # Same response as wrong password,
                    # so no information about what went wrong
                    flash('Login information incorrect. Try again or register')
                    return redirect(url_for('index'))
                hashed = userInfo['hashed'] # hashed password stored in database
                a = password.encode('utf-8')
                b = hashed.encode('utf-8')
                hashed2 = bcrypt.hashpw(password.encode('utf-8'),hashed.encode('utf-8'))
                hashed2_str = hashed2.decode('utf-8')
                if hashed2_str == hashed:
                    flash('successfully logged in as '+userID)
                    session['userID'] = userID
                    session['logged_in'] = True
                    return redirect(url_for('index'))
                else:
                    flash('Login incorrect. Try again or register')
                    return redirect(url_for('index'))
            except Exception as err:
                flash('form submission error '+str(err))
                return redirect(url_for('index'))
        else: # Register
            return render_template('register.html')

@app.route("/register/", methods=["POST"])
def register():
    try:
        userID = request.form['userID']
        password = request.form['password']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        name = testName
        year = testYear
        email = testEmail
        conn = dbi.connect()
        curs = dbi.cursor(conn)
        try:
            sqlOperations.registerUser(conn,userID,hashed,testName,testYear,testEmail)
        except Exception as err:
            flash('User already registered: {}'.format(repr(err)))
            return redirect(url_for('index'))
        flash('Successfully registered')
        return redirect(url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect(url_for('index'))

@app.route("/profile/", methods=["GET","POST"])
def profile():
    try:
        if 'userID' in session:
            userID = session['userID']
            conn = dbi.connect()
            if request.method=="POST":
                visibility = request.form.get('visibility')
                interests = request.form.get('interests')
                if interests==None:
                    interests = ""
                introduction = request.form.get('introduction')
                if introduction==None:
                    introduction = ""
                career = request.form.get('career')
                if career==None:
                    career = ""
                sqlOperations.updateProfile(conn,userID,visibility,interests,introduction,career)
            # both POST and GET
            profileInfo = sqlOperations.profileInfo(conn,userID)
            if profileInfo['visibility']=='Y':
                visibleY = "checked"
                visibleN = ""
            else:
                visibleY = ""
                visibleN = "checked"
            for key in profileInfo:
                value = profileInfo[key]
                if value==None:
                    profileInfo[key] = ""

            return render_template('profile.html',result=profileInfo,visible=visibleY,invisible=visibleN)

        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(url_for('index'))

@app.route('/logout/')
def logout():
    try:
        if 'userID' in session:
            session.pop('userID')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('index'))
        else:
            flash('You are not logged in. Please log in or register')
            return redirect(url_for('index'))
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(url_for('index'))

@app.route("/network/")
def network():
    try:
        if 'userID' in session:
            conn = dbi.connect()
            profileNetwork = sqlOperations.profileNetwork(conn)
            print(profileNetwork)
            return render_template("network.html", result=profileNetwork) 
        else:
            flash('You are not logged in. Please log in or register')
            return redirect(url_for('index'))
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(url_for('index'))

@app.route("/tips/")
def tips():
    try:
        if 'userID' in session:
            return render_template('tips.html') 
        else:
            flash('You are not logged in. Please log in or register')
            return redirect(url_for('index'))
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(url_for('index'))

if __name__ == '__main__':
    
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
        cnf = dbi.cache_cnf()   # defaults to ~/.my.cnf
        dbi.use(nameDB)
        conn = dbi.connect()
    app.debug = True
    app.run('0.0.0.0',port) 