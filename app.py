from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
from werkzeug.utils import secure_filename
import cs304dbi as dbi
app = Flask(__name__)

import random
import cs304dbi as dbi
import sqlOperations

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

from flask_cas import CAS
from flask_cas import login_required
from flask_cas import logout

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
# app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
# app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
# app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'
# the following doesn't work :-(
# app.config['CAS_AFTER_LOGOUT'] = 'after_logout'


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

nameDB = 'wcscdb_db'
# testUserID for /profile
testUserID = "wwellesley15"

@app.route('/')
def index():
    return render_template('main.html')

@app.route("/register/")
def register():
    return render_template("register.html")

@app.route("/profile/", methods=["GET","POST"])
def profile():
    conn = dbi.connect()

    if request.method=="POST":
        if request.form.get('visible')=="on":
            visibility = 'Y'
        else: # invisible
            visibility = 'N'

        interests = request.form.get('interests')
        if interests==None:
            interests = ""
        
        introduction = request.form.get('introduction')
        if introduction==None:
            introduction = ""

        career = request.form.get('career')
        if career==None:
            career = ""
        sqlOperations.updateProfile(conn,testUserID,visibility,interests,introduction,career)

    profileInfo = sqlOperations.profileInfo(conn,testUserID)
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




        # return render_template('main.html')

@app.route("/network/")
def network():
    return render_template("network.html") 

@app.route("/tips/")
def tips():
    return render_template("interview.html")






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