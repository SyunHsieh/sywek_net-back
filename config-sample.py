ENV = 'production'
DEBUG = False
SECRET_KEY = '{secret_key}'
SESSION_TYPE = 'sqlalchemy'
SESSION_COOKIE_NAME = 'SID'

# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{db_account}:{db_password}@/{db_name}?unix_sock=/cloudsql/{db_host}/.s.PGSQL.{db_port}'
# SQLALCHEMY_BINDS = {
#     'blog_db': 'postgresql+psycopg2://{db_account}:{db_password}@/{db_name}?unix_sock=/cloudsql/{db_host}/.s.PGSQL.{db_port}'
# }
