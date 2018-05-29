from flask import request,Blueprint
from os import path,mkdir
from flask_restplus import Api,Resource,reqparse
from helpers.picfns import *
from helpers.signup import *
from helpers.login import *
from helpers.getuser import *
from helpers.updateuser import *
from helpers.deleteuser import *
from helpers.addalbum import *
from helpers.getalbum import *
from helpers.deletealbum import *
from helpers.editalbum import *
from helpers.addphoto import *
from helpers.deletephoto import *
from helpers.editphoto import *

from helpers.validateapi import *
from helpers.verifyapikey import *
from helpers.photozparsers import *
from helpers.configuration import *

APP_ROOT= path.dirname(path.abspath(__file__))
target = path.join(path.dirname(APP_ROOT), 'images/')
if not path.isdir(target):
    mkdir(target)

authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

apimod=Blueprint('api',__name__)

api = Api(apimod,authorizations=authorizations)

@api.route("/api/login")
class loginapi(Resource):

    @api.doc(responses={'200': 'success', '401': 'Unauthorized'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def get(self):
        '''
        Check if api key is valid
        Returns username if valid
        '''
        res = verifykey(request)
        if (res['result'] == "valid"):
            return res, 200
        return res, 401

    @api.doc(responses={'200': 'success', '401': 'Unauthorized'})
    @api.expect(loginapi)
    def post(self):
        '''
        Login to get an api key
        Returns id,username and api key valid for 100 minutes
        '''
        s = Serializer(configuration['secretkey'])
        res = loginfn(request)
        if (res['result'] == "success"):
            res['apiKey'] = s.dumps(res['username'])
            return res, 200
        return res, 401


@api.route("/api/users")
class usersapi(Resource):

    @api.expect(getusersapi, validate=True)
    def get(self):
        '''
        Get list of users filtered by username substring and gender
        Returns a list with userid and username of satisfied users
        '''
        username = ""
        if 'username' in request.args:
            username = request.args['username']
        gender = ""
        if 'gender' in request.args:
            gender = request.args['gender']
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("select userid,username from users where username like %s  and gender like %s",
                    ("%" + username + "%", gender + "%"))
        res = cur.fetchall()
        userlist = []
        for r in res:
            tmp = {'userid': r[0], 'username': r[1]}
            userlist.append(tmp)
        cur.close()
        conn.close()
        return {'users': userlist}

    @api.expect(createuserapi)
    @api.doc(responses={'201': 'created', '400': 'Bad Request'})
    def post(self):
        '''
        Create a new user
        Returns id and username of the created user
        '''
        res = signupfn(request, target)
        if (res['result'] == "success"):
            return res, 201
        return res, 400


@api.route("/api/users/<uname>")
class userdetapi(Resource):

    @api.doc(responses={'200': 'success', '404': 'Not found'})
    def get(self, uname):
        '''
        Gets details of a username
        Returns userdetails(name,userid,gender,username) and profilepic(b64encoded) and list of albums(albumid,name)
        '''
        res = getuserfn(uname)
        if (res['result'] != "success"):
            return res, 404
        res.pop("type", None)
        tmp = []
        for x in res['albums']:
            tmp.append({'albumid': x[0], 'name': x[1]})
        res['albums'] = tmp
        res['profilepic'] = getthumbnail(res['profilepic']['id'], target)
        return res, 200

    @api.expect(userupdateapi)
    @api.doc(security='apiKey')
    @api.doc(responses={'200': 'success', '401': 'Unauthorized', '400': 'Bad request'})
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def put(self, uname):
        '''
        Update user details
        '''
        ver = verifykey(request)
        if (ver['result'] == 'valid'):
            if (uname != ver['user']):
                return {'result': 'Unauthorized'}, 401
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute("select userid from users where username=%s;", ver['user'])
            res = updatefn(request, str(cur.fetchone()[0]), target)
            cur.close()
            conn.close()
            if (res['result'] == "success"):
                return res, 200
            else:
                return res, 400
        else:
            return ver, 401

    @api.doc(security='apiKey')
    @api.doc(responses={'200': 'success', '401': 'Unauthorized'})
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def delete(self, uname):
        '''
        Delete a user
        '''
        ver = verifykey(request)
        if (ver['result'] == 'valid'):
            if (uname != ver['user']):
                return {'result': 'Unauthorized'}, 401
            return deleteuserfn(target, uname=uname), 200
        else:
            return ver, 401


@api.route("/api/photos")
class photosapi(Resource):

    @api.expect(addphotoapi)
    @api.doc(responses={'201': 'Added', '401': 'Unauthorized', '400': 'Bad request'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def post(self):
        '''
        Add a photo to an album
        Returns the picid of the added image
        '''
        res = verifykey(request)
        if (res['result'] == "valid"):
            val = validateapi(requester=res['user'], aid=request.form['albumid'])
            if (val['msg'] != "success"):
                return {'result': val['msg']}, 400
            if not val['owner']:
                return {'result': 'Unauthorized'}, 401
            res = addphotofn(request, request.form['albumid'], target)
            if (res['result'] == "success"):
                return res, 201
            else:
                return res, 400
        return res, 401


@api.route("/api/photos/<pid>")
class photoapi(Resource):

    @api.doc(responses={'200': 'Success', '404': 'Not found'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def get(self, pid):
        '''
        Gets details of a photo
        Returns id,name,description,likes(int),created on(Date),image(b64encoded) of the photo
        Need api key for private photo
        '''
        res = verifykey(request)
        if res['result'] != "valid":
            res = validateapi(pid=pid)
        else:
            res = validateapi(requester=res['user'], pid=pid)

        if res['msg'] != "success":
            return res['msg'], 404

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("select name,description,likes,created from pictures where picid=%s;", pid)
        tmp = cur.fetchone()
        cur.close()
        conn.close()
        return {'result': 'success', 'id': pid, 'name': tmp[0], 'description': tmp[1], 'likes': tmp[2],
                'created on': tmp[3], 'image': getthumbnail(pid, target)}, 200

    @api.expect(editphotoapi)
    @api.doc(responses={'200': 'Success', '401': 'Unauthorized', '400': 'Bad request'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def put(self, pid):
        '''
        Update photo details
        '''
        res = verifykey(request)
        if (res['result'] == "valid"):
            val = validateapi(requester=res['user'], pid=pid)
            if (val['msg'] != "success"):
                return {'result': val['msg']}, 400
            if not val['owner']:
                return {'result': 'Unauthorized'}, 401
            # print("editing")
            res = editphotofn(request, pid)
            if (res['result'] != "success"):
                return res, 400
            return {'result': 'success'}, 200
        return res, 401

    @api.doc(responses={'200': 'Success', '401': 'Unauthorized', '400': 'Bad request'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def delete(self, pid):
        '''
        Delete a photo
        '''
        res = verifykey(request)
        if (res['result'] == "valid"):
            val = validateapi(requester=res['user'], pid=pid)
            if (val['msg'] != "success"):
                return {'result': val['msg']}, 400
            if not val['owner']:
                return {'result': 'Unauthorized'}, 401
            res = deletephotofn(pid, val['aid'], target)
            return res, 200
        return res, 401


@api.route("/albums")
class albumsapi(Resource):

    @api.expect(addalbumapi)
    @api.doc(responses={'201': 'Albumadded', '401': 'Unauthorized', '400': 'Bad request'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def post(self):
        '''
        Add an album
        Returns albumid of created album
        '''
        res = verifykey(request)
        if (res['result'] == "valid"):
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute("select userid from users where username=%s;", res['user'])
            res = addalbumfn(request, cur.fetchone()[0], target)
            cur.close()
            conn.close()
            if (res['result'] == "success"):
                return res, 201
            else:
                return res, 400
        return res, 401


@api.route("/api/albums/<aid>")
class albumapi(Resource):

    @api.doc(responses={'200': 'Success', '404': 'Not found'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def get(self, aid):
        '''
        Gets details of aln album
        Returns name,description,likes(int),created(date),coverid and thumbnails(b64encoded) of images in it.
        Need api key for private album
        '''
        res = verifykey(request)
        if res['result'] != "valid":
            res = validateapi(aid=aid)
        else:
            res = validateapi(requester=res['user'], aid=aid)

        if res['msg'] != "success":
            return res['msg'], 404
        res = getalbum(aid, owner=res['owner'])
        tmp = []
        for pic in (res['pictures']):
            tmp.append({'thumbnail': getthumbnail(pic[0], target), 'name': pic[1]})
        res['pictures'] = tmp
        return res, 200

    @api.expect(editalbumapi)
    @api.doc(responses={'200': 'Success', '401': 'Unauthorized', '400': 'Bad request'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def put(self, aid):
        '''
        Update Album details
        '''
        res = verifykey(request)
        if (res['result'] == "valid"):
            val = validateapi(requester=res['user'], aid=aid)
            if (val['msg'] != "success"):
                return {'result': val['msg']}, 400
            if not val['owner']:
                return {'result': 'Unauthorized'}, 401
            res = editalbumfn(request, aid)
            if (res['result'] != "success"):
                return res, 400
            return {'result': 'success'}, 200
        return res, 401

    @api.doc(responses={'200': 'Success', '401': 'Unauthorized', '400': 'Bad request'})
    @api.doc(security='apiKey')
    @api.header('X-API-KEY', 'type:apiKey', required=True)
    def delete(self, aid):
        '''
        Delete an Album
        '''
        res = verifykey(request)
        if (res['result'] == "valid"):
            val = validateapi(requester=res['user'], aid=aid)
            if (val['msg']) != "success":
                return {'result': val['msg']}, 400
            if not val['owner']:
                return {'result': 'Unauthorized'}, 401
            res = deletealbumfn(aid, target)
            return res, 200
        return res, 401