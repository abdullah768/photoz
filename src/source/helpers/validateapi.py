from helpers.mysql import *

def validateapi(requester=None,uname=None,aid=None,pid=None):
    conn = mysql.connect()
    cur = conn.cursor()
    aprivate=False
    pprivate=False
    res={}
    if(pid):
        cur.execute("select albumid,privacy from pictures where picid=%s;",pid)
        if(cur.rowcount==0):
            cur.close()
            conn.close()
            res['msg']= "Picture does not exist"
            return res
        tmp=cur.fetchone()
        aid=tmp[0]
        if tmp[1]=="private":
            pprivate=True

    if(aid):
        cur.execute("select userid,privacy from albums where albumid=%s;",aid)
        if(cur.rowcount==0):
            cur.close()
            conn.close()
            res['msg']= "Album does not exist"
            return res
        tmp=cur.fetchone()
        uid=tmp[0]
        if tmp[1]=="private":
            aprivate=True

    if(uname):
        cur.execute("select userid from users where username=%s;", uname)
        if (cur.rowcount == 0):
            cur.close()
            conn.close()
            res['msg'] = "User does not exist"
            return res
        uid=cur.fetchone()[0]

    rid=None
    if(requester):
        cur.execute("select userid from users where username=%s;", requester)
        rid=cur.fetchone()[0]

    cur.close()
    conn.close()
    res['owner']=False
    res['aid']=aid
    res['msg'] = "success"
    print(rid,uid)
    if rid:
        if rid == uid:
            res['owner'] = True
            return res

    if (aprivate or pprivate) and not res['owner']:
        res['msg']="Unauthorized"
        return res;
    return res
