import cs304dbi as dbi

nameDB = 'wcscdb_db'

def profileInfo(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.userID, user.name, user.classYear, 
        user.email, profile.visibility, profile.interests, 
        profile.introduction, profile.career FROM profile
        INNER JOIN user ON user.userID=profile.userID
        WHERE user.userID=%s;''', [userID])
    return curs.fetchone()

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

def registerUser(conn,userID,hashed,name,year,email):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO
        user (userID,hashed,name,classYear,email) 
        VALUES (%s,%s,%s,%s,%s);
        ''', [userID,hashed,name,year,email])
    conn.commit()
    registerProfile(conn,userID)

def registerProfile(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
    INSERT INTO `profile` 
    (userID) VALUES (%s);
    ''', [userID])
    conn.commit()

def login(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT userID,hashed 
        FROM user WHERE userID=%s
        ''', [userID])
    return curs.fetchone()

def checkDuplicate(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT userID
        FROM user WHERE userID=%s
        ''', [userID])
    return curs.fetchone()

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
def addPost(conn,authorID,content,title,postID,datetime):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        INSERT INTO post
         (postID,authorID,datetime,title,content) 
        VALUES (%s,%s,%s,%s,%s);
        ''', [postID,authorID,datetime,title,content])
    conn.commit()

def getAllPosts(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title FROM post
        INNER JOIN user ON user.userID=post.authorID;
        ''')
    return curs.fetchall()

def searchPostbyAuthor(conn,authorName):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title FROM post
        INNER JOIN user ON user.userID=authorID WHERE user.name like %s;
        ''',['%'+authorName+"%"])
    return curs.fetchall()

    #not yet implemented
def searchPostbyKeyword(conn,keyword):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT user.name,`datetime`,content,title FROM post
        INNER JOIN user ON user.userID=authorID WHERE post.content like %s or post.title like %s;
        ''',['%'+keyword+"%",'%'+keyword+"%"])
    return curs.fetchall()



if __name__ == '__main__':
    dbi.cache_cnf()
    dbi.use(nameDB)
    conn = dbi.connect()