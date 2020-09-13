from flask import request, jsonify, session, g
from ...DictValidate import validateDict
from ...User import User
from ...controller import userController
# bp = Blueprint('user', __name__)

routes = []
# @bp.route('/api', methods=['POST', 'DELETE', 'GET'])


def routes_userAPI():

    # restful->Create user.
    if 'POST' == request.method:
        _jsonData = request.get_json()['userData']
        _flag, _retDict, _userId = userController.createAccount(_jsonData)

        return jsonify(_retDict)
    elif 'DELETE' == request.method:  # restful->Delete user
        # should check session.user not null
        return 'Falied'


# post-method delete-method
def routes_setUserFollow(targetUserId):
    pass


routes.append(dict(
    rule='/user',
    view_func=routes_userAPI,
    options=dict(methods=['POST', 'DELETE', 'GET'])
))

routes.append(dict(
    rule='/user/follow/<userId>',
    view_func=routes_setUserFollow,
    options=dict(methods=['POST', 'DELETE'])
))


# @ bp.before_app_request


def load_logged_in_user():
    user_id = session.get('user_id')
    g.userId = user_id
    # if user_id is None:
    #     g.user = None
    # else:
    #     g.user = User(user_id, loadInfo=True)
