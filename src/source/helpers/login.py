from wtforms import validators,fields as wtfields,Form
from helpers.formhelp import *
from helpers.mysql import *
from werkzeug.security import check_password_hash

class loginform(Form):
    username=wtfields.StringField(validators=[validators.input_required()])
    password=wtfields.PasswordField(validators=[validators.input_required()])

def loginfn(request):
    form=loginform(request.form)
    if not form.validate():
        return {'result': tostring(form.errors)}
    conn = mysql.connect()
    cur = conn.cursor()
    username = request.form['username']
    password = request.form['password']
    cur.execute("select password from users where username=%s;",username)
    if (cur.rowcount == 0):
        cur.close()
        conn.close()
        return {'result':"Username does not Exist!\n"}
    realpass = cur.fetchone()[0]
    if not check_password_hash(realpass, password):
        cur.close()
        conn.close()
        return {'result':"Incorrect username or password"}
    else:
        cur.execute("select userid from users where username=%s;",username)
        iid = str(cur.fetchone()[0]).encode("utf-8").decode("utf-8")
        cur.close()
        conn.close()
        return {'result':'success','id':iid,'username':username}
