from wtforms import validators,fields as wtfields,Form
from helpers.formhelp import *
from helpers.mysql import *
import datetime
from helpers.picfns import savepic
from werkzeug.security import generate_password_hash

now=datetime.datetime.now

class createuserform(Form):
    username=wtfields.StringField(validators=[validators.input_required()])
    email = wtfields.StringField(validators=[validators.input_required(),validators.Email()])
    fname = wtfields.StringField(validators=[validators.input_required()])
    lname = wtfields.StringField(validators=[validators.input_required()])
    password=wtfields.PasswordField(validators=[validators.input_required(),validators.EqualTo('rpassword')])
    rpassword = wtfields.StringField(validators=[validators.input_required()])
    gender = wtfields.StringField(validators=[validators.input_required(),validators.AnyOf(['male','female','other'])])

class createuserfile(Form):
    prophoto = wtfields.FileField(validators=[validators.input_required(), imagecheck])

def signupfn(request,target):
    err = ""
    form=createuserform(request.form)
    formf=createuserfile(request.files)
    if not form.validate():
        return {'result':tostring(form.errors)}
    if not formf.validate():
        return {'result':tostring(formf.errors)}

    username = request.form['username']
    email = request.form['email']
    fname = request.form['fname']
    lname = request.form['lname']
    password = request.form['password']
    gender = request.form['gender']
    print(username)
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select username from users where username= %s ;",username)
    if (cur.rowcount != 0):
        err += "Username already Exists!\n"
    cur.execute("select username from users where email= %s ;",email)
    if (cur.rowcount != 0):
        err += "Email already Exists!\n"

    if (err == ""):
        file = request.files['prophoto']
        fn = file.filename.split(".")
        dt = now().strftime("%Y-%m-%d %H:%M")

        cur.execute("select max(userid) from users;")
        uid = cur.fetchone()[0]
        if uid:
            uid += 1
        else:
            uid = 1

        cur.execute("select max(albumid) from albums;")
        aid = cur.fetchone()[0]
        if aid:
            aid += 1
        else:
            aid = 1

        cur.execute("select max(picid) from pictures;")
        pid = cur.fetchone()[0]
        if pid:
            pid += 1
        else:
            pid = 1

        cur.execute("insert into albums (albumid,userid,name,coverid,created,likes,privacy,description,count) values(" \
                    +"%s,NULL,'Profile Picture',NULL,%s,0,'public','Profile Picture',1);",(aid,dt))
        conn.commit()

        cur.execute("insert into pictures(picid,albumid,name,ext,created,likes,privacy,description) values("\
                    +"%s,%s,'Profile Picture',%s,%s,0,'public','Profile Picture');",(pid,aid,fn[1],dt))
        conn.commit()

        savepic(file, pid,target)

        print(pid)
        cur.execute("insert into users(userid,username,email,fname,lname,password,gender,propicid) values("\
                    +"%s,%s,%s,%s,%s,%s,%s,%s);",(uid,username,email,fname,lname,generate_password_hash(password),gender,pid))
        conn.commit()

        cur.execute("update albums set userid=%s, coverid=%s where albumid=%s;",(uid,pid,aid))
        conn.commit()
        cur.close()
        conn.close()
        return {'result':'success','username':username,'id':uid}
    else:
        cur.close()
        conn.close()
        return {'result':err}
