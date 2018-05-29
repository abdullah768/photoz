from helpers.mysql import *
from helpers.picfns import deletepic

def deletealbumfn(aid,target,userdel=False):
    # print(target)
    conn = mysql.connect()
    cur = conn.cursor()
    if( not userdel):
        cur.execute("select albumid from users,pictures where users.propicid=pictures.picid and pictures.albumid=%s;",aid)
        if (cur.rowcount != 0):
            cur.close()
            conn.close()
            return {'result':"Profile picture album can not be deleted"}

    cur.execute("delete from albumlikes where albumid=%s;",aid)
    conn.commit()
    cur.execute("select picid,ext from pictures where albumid=%s;",aid)
    reslt = cur.fetchall()
    print(reslt)

    cur.execute("update pictures set albumid=NULL where albumid=%s",aid)
    conn.commit()
    for res in reslt:
        cur.execute("delete from piclikes where picid=%s", res[0])
        conn.commit()
        picname = "p" + str(res[0]) + "." + str(res[1])
        destination = "/".join([target, picname])
        deletepic(destination)

    cur.execute("delete from albums where albumid=%s;",aid)
    conn.commit()
    query = "delete from pictures where albumid is NULL;"
    print(query)
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    return {'result':'success'}