from flask import Blueprint, render_template, request,send_from_directory,redirect,url_for
from os import path,mkdir

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
now=datetime.datetime.now

mod=Blueprint('site',__name__)

APP_ROOT= path.dirname(path.abspath(__file__))
target = path.join(path.dirname(APP_ROOT), 'images/')
if not path.isdir(target):
    mkdir(target)
# print(target)
@mod.route("/")
def main():
    if(current_user.is_authenticated):
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("select username from users where userid=%s;",current_user.id)
        details=cur.fetchone()
        cur.close()
        conn.close()
        return redirect("/user/"+details[0])
    else:
        return render_template('index.html')

@mod.route("/viewimage/<iname>")
def viewimage(iname):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select ext from pictures where picid=%s;",iname)
    filename="p"+iname+"."+cur.fetchone()[0]
    cur.close()
    conn.close()
    return send_from_directory("images", filename)

@mod.route("/users")
def userlist():
    type={}
    type['loggedin']=False
    if current_user.is_authenticated:
        type['loggedin']=True
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select username,propicid from users")
    pics=cur.fetchall()
    cur.close()
    conn.close()
    return render_template("users.html",pics=pics,type=type)

@mod.route('/signup', methods=['POST'])
def signup():
    return signupfn(request,target)['result']

@mod.route('/login', methods=['POST'])
def login():
    res=loginfn(request)
    if(res['result']=="success"):
        print(res)
        login_user(User(res['id'],res['username']))
    return res['result']

@mod.route("/user/<uname>")
def user(uname):
    res=getuserfn(uname)
    if(res['result']!="success"):
        return render_template("error.html",error=res['result'])
    return render_template('view.html',albumd={} ,userd=res['userdetails'],type=res['type'],picd=res['profilepic'],pics=res['albums'])

@mod.route('/settings')
def settings():
    if current_user.is_authenticated:
        return render_template("settings.html",det={})
    return redirect('/')

@mod.route('/update', methods=['post'])
def update():
    if current_user.is_authenticated:
        res=updatefn(request,current_user.id,target)
        if(res['result']=="success"):
            return redirect("/")
        return render_template("error.html",error=res['result'])
    return render_template("error.html",error="Unauthorized")

@mod.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect('/')

@mod.route("/delete")
def deleteuser():
    if current_user.is_authenticated:
        deleteuserfn(target,uid=current_user.id)
        return redirect("/")
    return render_template("error.html",error="Unauthorized")

@mod.route("/user/<uname>/addalbum")
def addalbum(uname):
    val=validate(uname);
    if(val['msg']):
        return render_template("error.html",error=val['msg'])
    if( not val['owner']):
        return render_template("error.html", error="Unauthorized")
    det={'uname':uname,'type':'album','func':'add','loggedin':True}
    return render_template("add.html",det=det)

@mod.route("/user/<uname>/addalbumproc", methods=['POST'])
def addalbumproc(uname):
    val=validate(uname);
    if(val['msg']):
        return render_template("error.html",error=val['msg'])
    if( not val['owner']):
        return render_template("error.html", error="Unauthorized")
    res=addalbumfn(request, current_user.id,target)
    if res['result']!="success":
        return render_template("error.html",error=res['result'])
    return redirect("/user/"+uname+"/album/"+res['Album Id'])

@mod.route("/user/<uname>/album/<aid>")
def album(uname,aid):
    val=validate(uname,aid);
    if(val['msg']):
        return render_template("error.html",error=val['msg'])
    conn = mysql.connect()
    cur = conn.cursor()
    like="like"
    if(val['loggedin']):
        cur.execute("select userid from albumlikes where userid= %s and albumid=%s;",(current_user.id,aid))
        if(cur.rowcount!=0):
            like="UnLike"
    res=getalbum(aid,val['owner'])
    userd={'username':uname}
    albumd={'id':aid,'cover':res['album details']['cover']}
    picd={'id':res['album details']['cover']}
    type={'loggedin':val['loggedin'],'likes':res['album details']['likes'],'description':res['album details']['description'],
          'type':'album','name':res['album details']['name'],'owner':val['owner'],'date':res['album details']['created on'],'like':like}
    cur.close()
    conn.close()
    return render_template("view.html",userd=userd,albumd=albumd,picd=picd,type=type,pics=res['pictures'])

@mod.route("/user/<uname>/album/<aid>/deletealbum")
def deletealbum(uname,aid):

    val=validate(uname,aid)
    if(val['msg']):
        return render_template("error.html,",error=val['msg'])

    if(val['owner']):
        res=deletealbumfn(aid,target)
        if(res['result']!="success"):
            return render_template("error.html,", error=res['result'])
        return redirect("/user/"+uname)
    return render_template("error.html,",error="Unauthorized")

@mod.route("/user/<uname>/album/<aid>/editalbum")
def editalbum(uname,aid):
    val=validate(uname,aid)
    if(val['msg']):
        return render_template("error.html",error=val['msg'])

    if(val['owner']):
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("select name,description,privacy,coverid from albums where albumid=%s;",aid)
        tmp=cur.fetchone()
        det = {'uname': uname, 'aid': aid, 'type': 'album', 'func': 'edit','loggedin':val['loggedin'],'name':tmp[0],'description':tmp[1],'privacy':tmp[2],'pid':tmp[3]}
        print(det)
        cur.close()
        conn.close()
        return render_template("add.html", det=det)
    return render_template("error.html",error="Unauthorized")

@mod.route("/user/<uname>/album/<aid>/editalbumproc", methods=['POST'])
def editalbumproc(uname,aid):
    val=validate(uname,aid)
    if(val['msg']):
        return render_template("error.html", error=val['msg'])
    if( not val['owner']):
        return render_template("error.html", error="Unauthorized")
    res=editalbumfn(request,aid)
    if res['result']!="success":
        return render_template("error.html",error=res['result'])
    return redirect("/user/"+uname+"/album/"+aid)

@mod.route("/user/<uname>/album/<aid>/albumlike")
def albumlike(uname,aid):
    val=validate(uname,aid);
    if(val['msg']):
        return render_template("error.html",error=val['msg'])
    if( not val['loggedin']):
        return render_template("error.html",error="Unauthorized")
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select * from albumlikes where albumid=%s and userid=%s;",(aid,current_user.id))
    if(cur.rowcount==0):
        cur.execute("insert into albumlikes values(%s,%s);",(aid,current_user.id))
        cur.execute("update albums set likes=likes+1 where albumid=%s;",aid)
    else:
        cur.execute("delete from albumlikes where albumid=%s and userid=%s",(aid,current_user.id))
        cur.execute("update albums set likes=likes-1 where albumid=%s;",aid)
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/user/"+uname+"/album/"+aid)

@mod.route("/user/<uname>/album/<aid>/addphoto")
def addphoto(uname,aid):
    val=validate(uname,aid);
    if(val['msg']):
        return render_template("error.html",error=val['msg'])
    if( not val['owner']):
        return render_template("error.html",error="Unauthorized")
    det={'uname':uname,'aid':aid,'type':'photo','func':'add','loggedin':True}
    return render_template("add.html",det=det)

@mod.route("/user/<uname>/album/<aid>/addphotoproc", methods=['POST'])
def addphotoproc(uname,aid):
    val=validate(uname,aid);
    if(val['msg']):
        return render_template("error.html",error=val['msg'])
    if( not val['owner']):
        return render_template("error.html",error="Unauthorized")
    res=addphotofn(request, aid,target)
    if(res['result']=="success"):
        return redirect("/user/"+uname+"/album/"+aid)
    return render_template("error.html",error=res['result'])

@mod.route("/user/<uname>/album/<aid>/photo/<pid>")
def photo(uname,aid,pid):
    val=validate(uname,aid,pid);
    if(val['msg']):
        return render_template("error.html",error=val['msg'])
    conn = mysql.connect()
    cur = conn.cursor()
    like="like"
    if(val['loggedin']):
        cur.execute("select userid from piclikes where userid=%s and picid=%s;",(current_user.id,pid))
        if(cur.rowcount!=0):
            like="UnLike"
    cur.execute("select name,description,likes,created from pictures where picid=%s;",pid)
    tmp=cur.fetchone()
    cur.close()
    conn.close()
    userd={'username':uname}
    albumd={'id':aid}
    picd={'id':pid,'name':tmp[0]}
    type={'loggedin':val['loggedin'],'likes':tmp[2],'description':tmp[1],'type':'pic','name':tmp[0],'owner':val['owner'],'date':tmp[3],'like':like}

    return render_template("view.html",userd=userd,albumd=albumd,picd=picd,type=type)

@mod.route("/user/<uname>/album/<aid>/photo/<pid>/piclike")
def piclike(uname,aid,pid):
    val=validate(uname,aid,pid);
    if (val['msg']):
        return render_template("error.html", error=val['msg'])
    if (not val['loggedin']):
        return render_template("error.html", error="Unauthorized")
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select * from piclikes where picid=%s and userid=%s",(pid,current_user.id))
    if(cur.rowcount==0):
        cur.execute("insert into piclikes values(%s,%s);",(pid,current_user.id))
        conn.commit()
        cur.execute("update pictures set likes=likes+1 where picid=%s;",pid)
        conn.commit()
    else:
        cur.execute("delete from piclikes where picid=%s and userid=%s;",(pid,current_user.id))
        conn.commit()
        cur.execute("update pictures set likes=likes-1 where picid=%s;",pid)
        conn.commit()
    cur.close()
    conn.close()
    return redirect("/user/"+uname+"/album/"+aid+"/photo/"+pid)

@mod.route("/user/<uname>/album/<aid>/photo/<pid>/deletephoto")
def deletephoto(uname,aid,pid):

    val=validate(uname,aid)
    if(val['msg']):
        return render_template("error.html,",error=val['msg'])

    if(val['owner']):
        res=deletephotofn(pid,aid,target)
        if(res['result']!="success"):
            return render_template("error.html", error=res['result'])
        return redirect("/user/"+uname+"/album/"+aid)
    return render_template("error.html,",error="Unauthorized")

@mod.route("/user/<uname>/album/<aid>/photo/<pid>/editphoto")
def editphoto(uname,aid,pid):
    val=validate(uname,aid,pid)
    if(val['msg']):
        return render_template("error.html", error=val['msg'])
    if( not val['owner']):
        return render_template("error.html", error="Unauthorized")

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select name,description,privacy from pictures where picid=%s;",pid)
    tmp=cur.fetchone()
    cur.close()
    conn.close()
    det = {'uname': uname, 'aid': aid, 'type': 'photo', 'func': 'edit','loggedin':True,'name':tmp[0],'description':tmp[1],'privacy':tmp[2],'pid':pid}
    return render_template("add.html", det=det)

@mod.route("/user/<uname>/album/<aid>/photo/<pid>/editphotoproc", methods=['POST'])
def editphotoproc(uname,aid,pid):
    val=validate(uname,aid,pid)
    if(val['msg']):
        return render_template("error.html", error=val['msg'])
    if( not val['owner']):
        return render_template("error.html", error="Unauthorized")
    res=editphotofn(request,pid)
    if res['result']!="success":
        return render_template("error.html",error=res['result'])
    return redirect("/user/"+uname+"/album/"+aid+"/photo/"+pid)
