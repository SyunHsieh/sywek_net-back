# from flask import Blueprint, request, jsonify, session, g
# from ..DictValidate import validateDict
# from ..User import User
# import json
# bp = Blueprint('user', __name__)


# @bp.route('/api', methods=['POST', 'DELETE', 'GET'])
# def routes_userAPI():

#     # restful->Create user.
#     if 'POST' == request.method:
#         _jsonData = request.get_json()['userData']
#         if not validateDict(_jsonData, ['account', 'name', {'socialInfo': ['facebook', 'github', 'instagram', 'twitter']}, 'password', 'userImage']):
#             return jsonify({'msg': 'data is invalid.'})

#         if User.IsAccountExist(_jsonData['account']):
#             return jsonify({'msg': 'account "%s" is exist.' % (_jsonData['account'])})
#         _newUser = User()
#         _newUser.account = _jsonData['account']
#         if not _newUser.setPasswordHashAndSalt(_jsonData['password']):
#             return jsonify({'msg': 'invalid password.'})

#         _newUser.socialInfo = _jsonData['socialInfo']
#         _newUser.jsonImage = _jsonData['userImage']
#         _newUser.name = _jsonData['name']

#         _flag, _msg = _newUser.commit()

#         if _flag:
#             session['user_id'] = _newUser.id

#         return jsonify({'msg': _msg})
#     elif 'DELETE' == request.method:  # restful->Delete user
#         # should check session.user not null
#         return 'Falied'
#     # elif 'GET' == request.method:  # restful->login or logout
#     #     _jsonData = json.loads(request.args['userData'])
#     #     # logout
#     #     if g.user is not None:
#     #         session.clear()
#     #         return jsonify({'msg': 'Successed'})

#     #     if not validateDict(_jsonData, ['account', 'password']):
#     #         return jsonify({'msg': 'data is invalid.'})

#     #     # get user by account
#     #     _user = User.getUserByAccount(_jsonData['account'])
#     #     if _user is None or _user.validatePassword(_jsonData['password']) == False:
#     #         return jsonify({'msg': 'account or password is incorrect'})

#     #     session.clear()
#     #     session.permanent = True
#     #     session['user_id'] = _user.id

#     #     return jsonify({'msg': 'Successed', 'token': {'name': _user.name}})


# @ bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#     if user_id is None:
#         g.user = None
#     else:
#         g.user = User(user_id)
