import cs304dbi as dbi

'''Returns profile information for user with specified userID.'''
def profileInfo(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.visibility, profile.interests, 
        profile.introduction, profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE user.userID=%s;''', [userID])
    return curs.fetchone()

'''Returns post information with specified postID.'''
# fix this
def postInfo(conn,postID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT * FROM post
        WHERE postID=%s;''', [postID])
    return curs.fetchone()

'''Updates profile with specified userID and input information.'''
def updateProfile(conn,userID,visibility,interests,introduction,career):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    UPDATE profile
    SET
        visibility = %s,
        interests = %s,
        introduction = %s,
        career = %s
    WHERE
        userID = %s
    ''', [visibility,interests,introduction,career,userID])
    conn.commit()

'''Registers new user account and calls registerProfile.'''
def registerUser(conn,userID,hashed,name,year,email):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO
        user (userID,hashed,name,classYear,email) 
        VALUES (%s,%s,%s,%s,%s);
        ''', [userID,hashed,name,year,email])
    conn.commit()
    registerProfile(conn,userID)

'''Registers profile for new user.'''
def registerProfile(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    INSERT INTO `profile` 
    (userID) VALUES (%s);
    ''', [userID])
    conn.commit()

'''Returns login information for account 
with the specified userID.'''
def login(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT userID,hashed 
        FROM user WHERE userID=%s
        ''', [userID])
    return curs.fetchone()

'''Checks if there is a user with the same userID 
when registering new account.'''
def checkDuplicate(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT userID
        FROM user WHERE userID=%s
        ''', [userID])
    return curs.fetchone()

'''Returns profile information of all users 
who have set their profile to be visible.'''
def profileNetwork(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y';
        ''')
    return curs.fetchall()

#three search functions for the network page search bar
'''Returns all profiles with names like the query.'''
def searchProfileByName(conn,name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y' and user.name like %s''',['%'+name+"%"]
        )
    return curs.fetchall()

'''Returns all profiles with class year equal to the query.'''
def searchProfileByYear(conn,year):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y' and user.classYear = %s''',[year]
        )
    return curs.fetchall()

'''Returns all profiles with interests like the query.'''
def searchProfileByInterest(conn,interest):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y' and profile.interests like %s''',['%'+interest+"%"]
        )
    return curs.fetchall()

#add post
'''Adds post with input information.'''
def addPost(conn,authorID,content,title,datetime):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post
         (authorID,datetime,title,content) 
        VALUES (%s,%s,%s,%s);
        ''', [authorID,datetime,title,content])
    conn.commit()

'''Retrieves all posts.'''
def getAllPosts(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title,postID FROM post
        INNER JOIN user ON user.userID=post.authorID;
        ''')
    return curs.fetchall()

'''Searches all posts with author names like the query.'''
def searchPostbyAuthor(conn,authorName):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title FROM post
        INNER JOIN user ON user.userID=authorID WHERE user.name like %s;
        ''',['%'+authorName+"%"])
    return curs.fetchall()

#not yet implemented
'''Searches all posts with keywords like the query.'''
def searchPostbyKeyword(conn,keyword):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title FROM post
        INNER JOIN user ON user.userID=authorID WHERE post.content like %s or post.title like %s;
        ''',['%'+keyword+"%",'%'+keyword+"%"])
    return curs.fetchall()



if __name__ == '__main__':
    dbi.cache_cnf()
    dbi.use('wcscdb_db')
    conn = dbi.connect()