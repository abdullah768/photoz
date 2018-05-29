from flask_restplus import reqparse
from werkzeug.datastructures import FileStorage

loginapi=reqparse.RequestParser()
loginapi.add_argument('username', location='form', type=str, required=True)
loginapi.add_argument('password', location='form', type=str, required=True)

createuserapi=reqparse.RequestParser()
createuserapi.add_argument('username', location='form', type=str, required=True)
createuserapi.add_argument('email', location='form', type=str, required=True)
createuserapi.add_argument('fname', location='form', type=str, required=True)
createuserapi.add_argument('lname', location='form', type=str, required=True)
createuserapi.add_argument('password', location='form', type=str, required=True)
createuserapi.add_argument('rpassword', location='form', type=str, required=True)
createuserapi.add_argument('gender', location='form', type=str, required=True,choices=['male','female','other'])
createuserapi.add_argument('prophoto', location='files', type=FileStorage, required=True, help='should have a valid image extension')

getusersapi=reqparse.RequestParser()
getusersapi.add_argument('username', location='args', type=str)
getusersapi.add_argument('gender', location='args', type='str',choices=['male','female','other'])

userupdateapi=reqparse.RequestParser()
userupdateapi.add_argument('email', location='form', type=str)
userupdateapi.add_argument('fname', location='form', type=str)
userupdateapi.add_argument('lname', location='form', type=str)
userupdateapi.add_argument('password', location='form', type=str)
userupdateapi.add_argument('rpassword', location='form', type=str)
userupdateapi.add_argument('gender', location='form', type=str,choices=['male','female','other'])
userupdateapi.add_argument('prophoto', location='files', type=FileStorage,help='should have a valid image extension')

addphotoapi=reqparse.RequestParser()
addphotoapi.add_argument('name', location='form', type=str, required=True)
addphotoapi.add_argument('description', location='form', type=str)
addphotoapi.add_argument('privacy', location='form', type=str, required=True,choices=['private','public','link'])
addphotoapi.add_argument('photo', location='files', type=FileStorage, required=True,help='should have a valid image extension')
addphotoapi.add_argument('albumid', location='form', type=int, required=True,)

editphotoapi=reqparse.RequestParser()
editphotoapi.add_argument('name', location='form', type=str)
editphotoapi.add_argument('description', location='form', type=str)
editphotoapi.add_argument('privacy', location='form', type=str,choices=['public','private','link'])

addalbumapi=reqparse.RequestParser()
addalbumapi.add_argument('name', location='form', type=str, required=True)
addalbumapi.add_argument('description', location='form', type=str,required=True)
addalbumapi.add_argument('privacy', location='form', type=str, required=True,choices=['public','private','link'])
addalbumapi.add_argument('photo', location='files', type=FileStorage, required=True,help='should have a valid image extension')

editalbumapi=reqparse.RequestParser()
editalbumapi.add_argument('name', location='form', type=str)
editalbumapi.add_argument('description', location='form', type=str)
editalbumapi.add_argument('privacy', location='form', type=str, choices=['private', 'public', 'link'])
