from wtforms import validators,fields as wtfields,Form
from helpers.formhelp import *
from helpers.mysql import *
import datetime
from helpers.picfns import savepic
now=datetime.datetime.now

class addphotoform(Form):
    name=wtfields.StringField(validators=[validators.input_required()])
    description = wtfields.StringField()
    privacy = wtfields.StringField(validators=[validators.input_required(),validators.AnyOf(['private','public','link'])])

class addphotofile(Form):
    photo = wtfields.FileField(validators=[validators.input_required(), imagecheck])

def addphotofn(request, aid,target):

    form = addphotoform(request.form)
    if not form.validate():
        return {'result': tostring(form.errors)}
    formf = addphotofile(request.files)
    if not formf.validate():
        return {'result': tostring(formf.errors)}

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select count from albums where albumid=%s;",aid)
    if (cur.fetchone()[0] >= 1000):
        cur.close()
        conn.close()
        return {'result':'Max album size reached'}
    picname = request.form['name']
    description = request.form['description']
    privacy = request.form['privacy']
    file = request.files['photo']
    fn = file.filename.split(".")
    dt = now().strftime("%Y-%m-%d %H:%M")
    cur.execute("insert into pictures(albumid,name,ext,created,likes,privacy,description) values(%s,%s,%s,%s,0,%s,%s);",
                (aid,picname,fn[1],dt,privacy,description))
    conn.commit()
    cur.execute("select LAST_INSERT_ID()")
    picid = str(cur.fetchone()[0])
    savepic(file, picid,target)
    cur.execute("update albums set count=count+1 where albumid=%s;",aid)
    conn.commit()
    cur.close()
    conn.close()
    return {'result':'success','picid':picid}
