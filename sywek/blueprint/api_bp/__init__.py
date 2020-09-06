from flask import Blueprint, g, session
from .article_api_bp import routes as article_routes
from .session_api_bp import routes as session_routes
from .user_api_bp import load_logged_in_user, routes as user_routes

bp = Blueprint('api', __name__)

routes = (article_routes+session_routes+user_routes)


def tear_down_function(e=None):
    print('teardown!!!!!!')
    g.db.session.close()
    close_db()


for r in routes:
    bp.add_url_rule(
        r['rule'],
        r.get('endpoint', None),
        view_func=r['view_func'],
        **r.get('options', {})
    )
bp.before_app_request(load_logged_in_user)
# bp.teardown_app_request(tear_down_function)
