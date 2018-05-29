from flask_login import current_user, login_user, LoginManager,UserMixin,logout_user
from helpers.mysql import mysql

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, username):
        self.username = username
        self.id = id

@login_manager.user_loader
def load_user(id):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select username from users where userid=%s;",id)
    un=cur.fetchone()[0]
    cur.close()
    conn.close()
    return User(id,un)
