from helpers.mysql import *
from helpers.deletealbum import *
from helpers.logincontroller import *

def deleteuserfn(target,uname=None,uid=None):
    # print(target)
    if current_user.is_authenticated:
        logout_user()
    conn = mysql.connect()
    cur = conn.cursor()
    if not uid:
        cur.execute("select userid from users where username=%s;",uname)
        uid=cur.fetchone()[0]
    cur.execute("update users set propicid=NULL where userid=%s",uid)
    conn.commit()
    cur.execute("select albumid from albums where userid=%s;",uid)
    res=cur.fetchall()
    for alb in res:
        deletealbumfn(alb[0],target,True)
    cur.execute("delete from piclikes where userid=%s;",uid)
    conn.commit()
    cur.execute("delete from albumlikes where userid=%s;",uid)
    conn.commit()
    cur.execute("delete from users where userid=%s;",uid)
    conn.commit()
    cur.close()
    conn.close()
    return {'result':'success'}
