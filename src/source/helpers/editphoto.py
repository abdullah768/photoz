from wtforms import validators,fields as wtfields,Form
from helpers.formhelp import *
from helpers.mysql import *
import datetime
now=datetime.datetime.now

class editphotoform(Form):
    name=wtfields.StringField()
    description = wtfields.StringField()
    privacy = wtfields.StringField(validators=[validators.optional(),validators.AnyOf(['private','public','link'])])

def editphotofn(request, pid):
    form = editphotoform(request.form)
    if not form.validate():
        return {'result': tostring(form.errors)}
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select name,privacy,description from pictures where picid=%s", pid)
    tmp = cur.fetchone()

    picname = ""
    if 'name' in request.form:
        picname = request.form['name']
    if picname == "":
        picname = tmp[0]

    description=""
    if 'description' in request.form:
        description = request.form['description']
    else:
        description=tmp[2]
    privacy = ""
    if 'privacy' in request.form:
        privacy = request.form['privacy']
    if privacy == "":
        privacy = tmp[1]

    cur.execute("update pictures set name=%s ,description=%s ,privacy=%s where picid=%s ;",(picname,description,privacy,pid))
    conn.commit()
    cur.close()
    conn.close()
    return {'result':'success'}