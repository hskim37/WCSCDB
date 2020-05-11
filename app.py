from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
from werkzeug.utils import secure_filename
from datetime import datetime
import cs304dbi as dbi
app = Flask(__name__)

from threading import Lock
lock = Lock()

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
from flask_cas import logout

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'
# the following doesn't work :-(
# app.config['CAS_AFTER_LOGOUT'] = 'after_logout'


# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

nameDB = 'wcscdb_db'

'''Login route for CAS.'''
@app.route('/logged_in/')
def logged_in():
    flash('Wellesley credentials successfully verified')
    if '_CAS_TOKEN' in session:
        token = session['_CAS_TOKEN']
    if 'CAS_ATTRIBUTES' in session:
        attribs = session['CAS_ATTRIBUTES']
        # print('CAS_attributes: ')
        # for k in attribs:
        #     print('\t',k,' => ',attribs[k])
    if 'CAS_USERNAME' in session:
        is_logged_in = True
        username = session['CAS_USERNAME']
        conn = dbi.connect()
        if sqlOperations.checkDuplicate(conn,username)!=None:
            flash('You already have a registered account on WCSCDB.')
            return redirect(url_for('index'))
        # print(('CAS_USERNAME is: ',username))
    else:
        is_logged_in = False
        username = None
        print('CAS_USERNAME is not in the session')
    return render_template('register.html',
                           cas_attributes = session.get('CAS_ATTRIBUTES'))

'''URL for main page. 
User will see the login form only if they are not logged in.'''
@app.route('/', methods=["GET","POST"])
def index():
    if request.method=="GET":
        if 'userID' in session:
            return render_template('main.html')
        else: # not logged in
            return render_template('login.html')
    else: # POST - Login form
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

'''URL for registering new account, 
after users have been verified as a Wellesley student.'''
@app.route("/register/", methods=["POST"])
def register():
    try:
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        if password!=confirmPassword:
            flash('Passwords do not match. Try again.')
            return redirect(url_for('logged_in'))
        name = request.form['name']
        year = request.form['year']
        email = request.form['email']
        userID = request.form['userID']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        conn = dbi.connect()
        curs = dbi.cursor(conn)
        lock.acquire()
        try:
            sqlOperations.registerUser(conn,userID,hashed,name,year,email)
        except Exception as err:
            lock.release()
            flash('User already registered: {}'.format(repr(err)))
            return redirect(url_for('index'))
        lock.release()
        flash('Successfully registered')
        return redirect(url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect(url_for('index'))

'''URL for viewing and editing user's personal profile.'''
@app.route("/profile/", methods=["GET","POST"])
def profile():
    try:
        if 'userID' in session:
            userID = session['userID']
            conn = dbi.connect()
            if request.method=="POST":
                visibility = request.form.get('visibility')
                interests = request.form.get('interests', "")
                introduction = request.form.get('introduction', "")
                career = request.form.get('career', "")
                sqlOperations.updateProfile(conn,userID,visibility,interests,introduction,career)
                flash("Suceessfully updated your profile.")
            # both POST and GET
            profileInfo = sqlOperations.profileInfo(conn,userID)
            if profileInfo['visibility']=='Y':
                visibleY = "checked"
                visibleN = ""
            else:
                visibleY = ""
                visibleN = "checked"
            for key in profileInfo:
                if profileInfo[key]==None:
                    profileInfo[key] = ""
            return render_template('profile.html',result=profileInfo,visible=visibleY,invisible=visibleN)

        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(url_for('index'))

'''URL for logout.
Logs out of WCSCDB account, not CAS.'''
@app.route('/log_out/')
def log_out():
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

'''URL for network page.'''
@app.route("/network/", methods=["GET","POST"])
def network():
    if request.method =='GET':
        try:
            if 'userID' in session:
                conn = dbi.connect()
                profileNetwork = sqlOperations.profileNetwork(conn)
                return render_template("network.html", result=profileNetwork) 
            else:
                flash('You are not logged in. Please log in or register')
                return redirect(url_for('index'))
        except Exception as err:
            flash('some kind of error '+str(err))
            return redirect(url_for('index'))
    else: 
        try:
            conn = dbi.connect()
            form_data = request.form
            searchType = form_data['kind']
            searchWord = form_data['keyword']
            if searchType =='name':
                profileNetwork = sqlOperations.searchProfileByName(conn,searchWord) 
            elif searchType == "year":
                profileNetwork = sqlOperations.searchProfileByYear(conn,searchWord)
            elif searchType == 'interest':
                profileNetwork = sqlOperations.searchProfileByInterest(conn,searchWord)
            return render_template("network.html", result=profileNetwork) 
        except Exception as err:
            flash('some kind of error '+str(err))
            return redirect(url_for('network'))
                    
'''URL for viewing posts on tips.'''
@app.route("/tips/",methods=["GET","POST"])
def tips():
    if 'userID' in session:
        if request.method=='GET':
            try:
                conn = dbi.connect()
                posts = sqlOperations.getAllPosts(conn)
                return render_template('tips.html',posts=posts) 
            except Exception as err:
                flash('some kind of error '+str(err))
                return redirect(url_for('index'))
        else: # POST
            try:
                form_data = request.form
                conn = dbi.connect()
                if form_data['kind'] =='author':
                    authorName = form_data['searchWord']
                    posts = sqlOperations.searchPostbyAuthor(conn,authorName)
                    return render_template('tips.html',posts=posts)
                else: # keyword
                    keyword = form_data['searchWord']
                    posts = sqlOperations.searchPostbyKeyword(conn,keyword) 
                    return render_template('tips.html',posts=posts)
            except Exception as err:
                flash('Error: {}'.format(repr(err)))
                return redirect(url_for('tips'))  
    else:
        flash('You are not logged in. Please log in or register')
        return redirect(url_for('index'))

'''URL for writing posts on tips.'''
@app.route("/write/",methods=["GET","POST"])
def write():
    if 'userID' in session:
        if request.method == 'GET':
            return render_template("write.html")
        else: # POST
            userID = session['userID']
            form_data = request.form
            conn = dbi.connect()
            title = form_data.get('postTitle',"")
            content = form_data.get('postContent',"")
            timeNow = datetime.now() 
            authorID = userID
            # lock.acquire()
            try:
                sqlOperations.addPost(conn,authorID,content,title,timeNow)
                # lock.release()
                flash('Successfully submitted your post!')
            except Exception as err:
                # lock.release()
                flash('Some kind of post submission error: {}'.format(repr(err)))
            return redirect(url_for('tips'))
    else:
        flash('You are not logged in. Please log in or register')
        return redirect(url_for('index'))

'''URL for viewing individual post on tips.'''
@app.route("/tip/<postID>", methods=['GET','POST'])
def tip(postID):
    if 'userID' in session:
        if request.method=='GET':
            try:
                conn = dbi.connect()
                postInfo = sqlOperations.postInfo(conn,postID)
                return render_template("tip.html",result = postInfo)
            except Exception as error:
                flash('Error: {}'.format(repr(error)))
                return redirect(url_for('tips'))  
        else: # POST
            form_data = request.form
            if form_data.get('submit')=="Delete":
                try:
                    conn = dbi.connect()
                    sqlOperations.deletePost(conn,postID)
                    flash('Your post was successfully deleted.')
                except Exception as error:
                    flash('Error: {}'.format(repr(error)))
                return redirect(url_for('tips')) 
            elif form_data.get('submit')=="Edit":
                conn = dbi.connect()
                postInfo = sqlOperations.postInfo(conn,postID)
                return render_template('edit.html',result=postInfo)
            else: # Submit from Edit
                conn = dbi.connect()
                try:
                    title = form_data.get('postTitle',"")
                    content = form_data.get('postContent',"")
                    sqlOperations.updatePost(conn,postID,title,content)
                    flash("Successfully edited your post.")
                except Exception as error:
                    flash('Error: {}'.format(repr(error)))
                postInfo = sqlOperations.postInfo(conn,postID)
                return render_template('tip.html',result=postInfo)
    else:
        flash('You are not logged in. Please log in or register')
        return redirect(url_for('index'))


'''URL for profiles on network, visible to other users.'''
@app.route("/profile/<userID>")
def alumnusPage(userID):
    conn = dbi.connect()
    profileInfo = sqlOperations.profileInfo(conn,userID)
    return render_template("alumnus.html",result = profileInfo)

if __name__ == '__main__':
    
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        print(sys.argv[1])
        port = int(sys.argv[1])
        
        assert(port>1024)
        if not(1943 <= port <= 1950):
            print('For CAS, choose a port from 1943 to 1950')
            sys.exit()
    else:
        port = os.getuid()
        cnf = dbi.cache_cnf()   # defaults to ~/.my.cnf
        dbi.use(nameDB)
        conn = dbi.connect()
    app.debug = True
    app.run('0.0.0.0',port) 