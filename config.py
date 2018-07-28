from datetime import timedelta

DIALECT = "mysql"
DRIVER = "pymysql"
USERNAME = "root"
PASSWORD = ''
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = ''
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,
																	   DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = True

# SECRET_KET = '\xf4\x7fc^c\x8f\x9f\x90\x03\xfa.\xa4\xbb\xe8\xff\x05e4\xcc0\xce-\xa3\xb0'
PEWMANENT_SESSION_LIFETIME = timedelta(days=7)
