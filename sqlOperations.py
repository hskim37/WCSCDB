import cs304dbi as dbi

def profileInfo(conn,userID):
    '''Returns profile information for user with specified userID.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.visibility, profile.interests, 
        profile.introduction, profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE user.userID=%s;''', [userID])
    return curs.fetchone()

def postInfo(conn,postID):
    '''Returns post information with specified postID.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title,
        LPAD(postID, 12, '0') as postID, post.authorID FROM post
        INNER JOIN user ON user.userID=post.authorID
        WHERE postID=%s;''', [postID])
    return curs.fetchone()

def updateProfile(conn,userID,visibility,interests,introduction,career):
    '''Updates profile with specified userID and input information.'''
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

def registerUser(conn,userID,hashed,name,year,email):
    '''Registers new user account and calls registerProfile.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO
        user (userID,hashed,name,classYear,email) 
        VALUES (%s,%s,%s,%s,%s);
        ''', [userID,hashed,name,year,email])
    conn.commit()
    registerProfile(conn,userID)

def registerProfile(conn,userID):
    '''Registers profile for new user.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    INSERT INTO `profile` 
    (userID) VALUES (%s);
    ''', [userID])
    conn.commit()

def loginInfo(conn,userID):
    '''Returns login information for account 
    with the specified userID.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT userID,hashed 
        FROM user WHERE userID=%s
        ''', [userID])
    return curs.fetchone()

def checkDuplicate(conn,userID):
    '''Checks if there is a user with the same userID 
    when registering new account.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT userID
        FROM user WHERE userID=%s
        ''', [userID])
    return curs.fetchone()

def profileNetwork(conn):
    '''Returns profile information of all users 
    who have set their profile to be visible.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y';
        ''')
    return curs.fetchall()

# Three search functions for the network page search bar

def searchProfileByName(conn,name):
    '''Returns all profiles with names like the query.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y' and user.name like %s''',['%'+name+"%"]
        )
    return curs.fetchall()

def searchProfileByYear(conn,year):
    '''Returns all profiles with class year equal to the query.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y' and user.classYear = %s''',[year]
        )
    return curs.fetchall()

def searchProfileByInterest(conn,interest):
    '''Returns all profiles with interests like the query.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.interests, profile.introduction, 
        profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE profile.visibility='Y' and profile.interests like %s''',['%'+interest+"%"]
        )
    return curs.fetchall()

def addPost(conn,authorID,content,title,datetime):
    '''Adds post with input information.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post
         (authorID,datetime,title,content) 
        VALUES (%s,%s,%s,%s);
        ''', [authorID,datetime,title,content])
    conn.commit()

def getAllPosts(conn):
    '''Retrieves all posts.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title,
        LPAD(postID, 12, '0') as postID FROM post
        INNER JOIN user ON user.userID=post.authorID;
        ''')
    return curs.fetchall()

def searchPostbyAuthor(conn,authorName):
    '''Searches all posts with author names like the query.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title FROM post
        INNER JOIN user ON user.userID=authorID WHERE user.name like %s;
        ''',['%'+authorName+"%"])
    return curs.fetchall()

def searchPostbyKeyword(conn,keyword):
    '''Searches all posts with keywords like the query.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title FROM post
        INNER JOIN user ON user.userID=authorID WHERE post.content like %s or post.title like %s;
        ''',['%'+keyword+"%",'%'+keyword+"%"])
    return curs.fetchall()

def updatePost(conn,postID,title,content):
    '''Edits post with specified postID and given information.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        UPDATE post
        SET title=%s, content=%s
        WHERE postID=%s;''',[title,content,postID])
    conn.commit()

def deletePost(conn,postID):
    '''Deletes post with specified postID.'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        DELETE from post WHERE postID=%s
    ''',[postID])
    conn.commit()

if __name__ == '__main__':
    dbi.cache_cnf()
    dbi.use('wcscdb_db')
    conn = dbi.connect()