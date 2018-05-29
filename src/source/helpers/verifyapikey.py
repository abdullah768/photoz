from helpers.mysql import *
from itsdangerous import (URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired)
from helpers.configuration import *

def verifykey(request):
    if 'X-API-KEY' in request.headers:
        key = request.headers['X-API-KEY']
    else:
        return {'result': 'No Api Key sent'}
    s = Serializer(configuration['secretkey'])
    try:
        res = s.loads(key, max_age=6000)
        conn=mysql.connect()
        cur=conn.cursor()
        cur.execute("select userid from users where username=%s",res)
        rc=cur.rowcount
        cur.close()
        conn.close()
        if rc==0:
            return {'result':'User deleted'}
    except SignatureExpired:
        return {'result': 'Expired'}
    except BadSignature:
        return {'result': 'Invalid'}
    return {'result': 'valid', 'user': res}
