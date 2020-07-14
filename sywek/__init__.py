from flask import Flask, redirect, url_for, session, jsonify,request
# from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import os


def Create_app(test_config=None, renew_database=False):

    def _registerBP(flaskApp):
        from .blueprint.article.article_bp import bp as articleBP
        # CORS(articleBP, resources={r"/*": {"origins": "*"}})#enable cors with blueprint
        flaskApp.register_blueprint(articleBP, url_prefix='/article')

    app = Flask(__name__, instance_relative_config=True)

    # append flask cors

    #app.config['CORS_HEADERS'] = 'Content-Type'
 
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    app.config.from_object('config')
    if test_config is None:
        # Loading instance config
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Loding test config.
        app.config.from_mapping(test_config)

    # Ensure dic are exists
    try:
        os.makedirs(app.instance_path)
    except:
        pass

    @app.route('/')
    def routes_index():
        return 'default'
        #return redirect(url_for('blog.routes_blogIndex')) #this was not good  redirect 3 times.#################



    @app.route('/test/<postId>',methods=['GET','POST'])
    def routes_apitetst(postId):
        print(request.get_json())
        return 'id'+postId
    _registerBP(app)

    import sywek.db as sywekDb
    sywekDb.init_app(app)
    sywekDb.init_db(app)

    # import flaskr.db as flaskDB

    # flaskDB.createBlogDB_APP(app)
    # flaskDB.init_db(app)

    # from flask_sqlalchemy import SQLAlchemy
    # db = SQLAlchemy(app)
    # session = Session(app)

    # session.app.session_interface.db.drop_all()
    # session.app.session_interface.db.create_all()

    #from flask_talisman import Talisman
    # Talisman(app)
    return app
