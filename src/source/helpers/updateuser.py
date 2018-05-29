from wtforms import validators,fields as wtfields,Form
from helpers.formhelp import *
from helpers.mysql import *
from helpers.picfns import savepic
from werkzeug.security import generate_password_hash

class updateuserform(Form):
    email = wtfields.StringField(validators=[validators.optional(),validators.Email()])
    fname = wtfields.StringField()
    lname = wtfields.StringField()
    password=wtfields.PasswordField(validators=[validators.EqualTo('rpassword')])
    rpassword = wtfields.StringField()
    gender = wtfields.StringField(validators=[validators.optional(),validators.AnyOf(['none','male','female','other'])])

class updateuserfile(Form):
    prophoto = wtfields.FileField(validators=[imagecheck])

def updatefn(request,uid,target):
    err = ""
    print(request.form)
    form=updateuserform(request.form)
    if not form.validate():
        return {'result':tostring(form.errors)}
    if 'prophoto' in request.files:
        if(request.files['prophoto'].filename!=""):
            formf=updateuserfile(request.files)
            if not formf.validate():
                return {'result':tostring(formf.errors)}
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select email,fname,lname,gender from users where userid=%s;",uid)
    tmp = cur.fetchone()
    prev = {'email': tmp[0], 'fname': tmp[1], 'lname': tmp[2], 'gender': tmp[3]}

    email=""
    if 'email' in request.form:
        email = request.form['email']
    if email=="":
        email=prev['email']

    fname=""
    if 'fname' in request.form :
        fname = request.form['fname']

    if fname=="":
        fname=prev['fname']

    lname=""
    if 'lname' in request.form :
        lname = request.form['lname']
    if lname=="":
        lname=prev['lname']

    password=""
    if 'password' in request.form:
        password = request.form['password']

    gender=""
    if 'gender' in request.form:
        gender = request.form['gender']
    if(gender==""):
        gender=prev['gender']

    cur.execute("select userid from users where email=%s;",email)
    tmp = cur.fetchone()
    if (tmp):
        if (str(tmp[0]) != uid):
            err += "Email already Exists!\n"

    if (err != ""):
        cur.close()
        conn.close()
        return {'result':err};

    else:
        cur.execute("update users set email=%s ,fname=%s ,lname=%s ,gender=%s where userid= %s;",(email,fname,lname,gender,uid))
        conn.commit()
        if ('prophoto' in request.files):
            file = request.files['prophoto']
            if (file.filename != ""):
                fn = file.filename.split(".")
                cur.execute("select propicid from users where userid=%s;",uid)
                oldid = str(cur.fetchone()[0])
                print(oldid)
                cur.execute("update pictures set ext=%s where picid=%s ;",(fn[1],oldid))
                conn.commit()
                savepic(file, oldid,target)

        if (password != ""):
            cur.execute("update users set password=%s where userid=%s;",(generate_password_hash(password),uid))
            conn.commit()
    cur.close()
    conn.close()
    return {'result':'success'}