from flask import Blueprint, request, jsonify
from ...article.testArticle import fetch_article
from ...Article import Article
from flask_cors import cross_origin,CORS
from ...User import User
bp = Blueprint('article', __name__)

@bp.route('',methods=['GET','POST'])
def routes_article():
    if 'POST' == request.method:
        _article = Article()
        _article.loadFromJson(request.get_json().get('article'))
        _article.commit()
        return 'Successed'

@bp.route('/<articleId>', methods=['GET', 'DELETE'])
def routes_register(articleId):
    
    _article = Article(int(articleId))
    if 'GET' == request.method:
        if _article.isSearchingInDB:
            return jsonify(_article.jsonify(User(3,loadInfo=True)))#test
        else:
            return 'None'

        # return jsonify(fetch_article())



@bp.route('/test')
def routes_articleTest():
    return 'test article'
