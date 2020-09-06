from flask import request, jsonify, session, g
from ...DictValidate import validateDict
from ...Article import Article
from ...User import User
from ...controller import sessionController
import json
# bp = Blueprint('session', __name__)

routes = []
# @bp.route('/api', methods=['DELETE', 'GET', 'POST'])


def routes_sessionAPI():
    if 'DELETE' == request.method:  # restful->log out

        _flag, _retDict = sessionController.sessionLogout(g.userId)
        session.clear()
        return jsonify(_retDict)
    elif 'GET' == request.method:  # restful->resend user infomations

        _flag, _retDict = sessionController.sessionGetToken(g.userId)
        if _flag == False:
            session.clear()
        return jsonify(_retDict)

    elif 'POST' == request.method:  # restful -> login

        _jsonData = request.get_json()['userData']
        _flag, _retDict, _userId = sessionController.sessionLogin(_jsonData)

        session.clear()
        if _flag:
            session.permanent = True
            session['user_id'] = _userId

        return jsonify(_retDict)


routes.append(dict(
    rule='/session',
    view_func=routes_sessionAPI,
    options=dict(methods=['DELETE', 'GET', 'POST'])
))
