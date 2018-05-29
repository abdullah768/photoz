from helpers.mysql import *
from helpers.picfns import deletepic

def deletephotofn(pid, aid,target):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select coverid from albums where coverid=%s;",pid)
    if (cur.rowcount != 0):
        cur.close()
        conn.close()
        return {'result':"Cover picture can not be deleted"}

    cur.execute("delete from piclikes where picid=%s;", pid)
    conn.commit()
    cur.execute("select ext from pictures where picid=%s;",pid)
    picname = "p" + pid + "." + cur.fetchone()[0]
    destination = "/".join([target, picname])
    deletepic(destination)
    cur.execute("delete from pictures where picid=%s;",pid)
    conn.commit()
    cur.execute("update albums set count=count-1 where albumid=%s;",aid)
    conn.commit()
    cur.close()
    conn.close()
    return {'result':'success'}