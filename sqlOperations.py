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
        VALUES (%s,%s,%s,%s,%s)
        ''', [userID,hashed,name,year,email])
    conn.commit()

def login(conn,userID):
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        SELECT userID,hashed 
        FROM user WHERE userID=%s
        ''', [userID])
    return curs.fetchone()

if __name__ == '__main__':
    dbi.cache_cnf()
    dbi.use(nameDB)
    conn = dbi.connect()