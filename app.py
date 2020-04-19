from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
from werkzeug.utils import secure_filename
import cs304dbi as dbi
app = Flask(__name__)

import random

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('login.html')

@app.route("/register/")
def register():
    return render_template("register.html")

@app.route("/profile/")
def profileSetup():
    return render_template("profile.html")

@app.route("/main/")
def main(): 
    return render_template("main.html")

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
        dbi.use('wmdb')
        conn = dbi.connect()
    app.debug = True
    app.run('0.0.0.0',port) 