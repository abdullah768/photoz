from helpers.mysql import *

def getalbum(aid,owner=False):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select name,description,likes,created,coverid from albums where albumid=%s;",aid)
    tmp = cur.fetchone()
    albumd = {'id': aid, 'cover': tmp[4],'likes': tmp[2], 'description': tmp[1],'name': tmp[0],'created on': tmp[3]}
    if owner:
        cur.execute("select picid,name from pictures where albumid=%s", aid)
    else:
        cur.execute("select picid,name from pictures where albumid=%s and privacy='public';",aid)
    pics = cur.fetchall()
    cur.close()
    conn.close()
    return {'album details':albumd,'pictures':pics}