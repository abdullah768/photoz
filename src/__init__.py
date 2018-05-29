from flask import Flask
from src.source.helpers.mysql import *
from src.source.helpers.logincontroller import *
from src.source.helpers.configuration import *

from src.source.app import mod
from src.source.api import apimod
app=Flask(__name__)
app.register_blueprint(mod)
app.register_blueprint(apimod,url_prefix="/api")

login_manager.init_app(app)

app.config['SECRET_KEY']= configuration['secretkey']
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = configuration['dbuser']
app.config['MYSQL_DATABASE_PASSWORD'] = configuration['dbpassword']
app.config['MYSQL_DATABASE_DB'] = configuration['db']
app.config['MYSQL_DATABASE_HOST'] = configuration['dbhost']
mysql.init_app(app)

app.config['RESTPLUS_VALIDATE'] = True