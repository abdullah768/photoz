from helpers.validate import *
from helpers.mysql import *

def getuserfn(uname,owner=False):
    val=validate(uname)
    if(val['msg']):
        return {'result':val['msg']}
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select username,fname,lname,propicid,userid,gender from users where username=%s;",uname)
    details = cur.fetchone()
    userd = {'username': details[0], 'name': details[1] + " " + details[2],'gender':details[5],'userid':details[4]}
    picd={'id':details[3]}
    uid=str(details[4])
    type = {'type': 'user', 'loggedin': val['loggedin'],'owner':val['owner'], 'name': details[0]}
    if val['owner']:
        cur.execute("select coverid,name,albumid from albums where userid=%s;",uid)
    else:
        cur.execute("select coverid,name,albumid from albums where userid=%s and privacy='public';", uid)
    albums = cur.fetchall()
    cur.close()
    conn.close()
    return {'result':'success','userdetails':userd,'profilepic':picd,'type':type,'albums':albums}