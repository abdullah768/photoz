from helpers.mysql import *
from helpers.logincontroller import *

def validate(uname,aid=None,pid=None):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select userid from users where username=%s ;",uname)
    res={'msg':None,'loggedin':False,'owner':False}
    if(cur.rowcount==0):
        res['msg']="User does not exist"
        cur.close()
        conn.close()
        return res
    uid=str(cur.fetchone()[0])
    aprivacy=None
    pprivacy=None
    if(aid):
        cur.execute("select userid,privacy from albums where albumid=%s ;",aid)
        if(cur.rowcount==0):
            res['msg']="Album does not exist"
            cur.close()
            conn.close()
            return res
        xyz=cur.fetchone()
        auid=str(xyz[0])
        aprivacy=xyz[1]
        if(uid != auid):
            res['msg']= "User does not own the album"
            cur.close()
            conn.close()
            return res

    if(pid):
        cur.execute("select albumid,privacy from pictures where picid=%s;",pid)
        if(cur.rowcount==0):
            cur.close()
            conn.close()
            res['msg']= "Picture does not exist"
            return res
        xyz=cur.fetchone()
        paid=str(xyz[0])
        pprivacy=xyz[1]
        if(aid != paid):
            res['msg']="Picture is not preset in the album"
            cur.close()
            conn.close()
            return res

    if(current_user.is_authenticated):
        res['loggedin']=True
        if(current_user.id==uid):
            res['owner']=True
    if(res['owner']==False and (aprivacy=="private" or pprivacy=="private")):
        res['msg']="Access Denied"
    cur.close()
    conn.close()
    return res