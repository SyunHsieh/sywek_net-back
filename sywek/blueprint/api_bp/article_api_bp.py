from flask import request, jsonify, g
from ...Article import Article
from ...User import User
from ...DictValidate import validateDict
from datetime import datetime, timedelta
from ...controller import articleController
import re
routes = []

# @bp.route('/article', methods=['GET', 'POST'])
# _recommandArticleRules: {
#     'rules': '',
#     'expireRules': lambda dt:  dt.replace(hour=23, minute=59, second=59),
#     'forceRecommandArticlesNo': [11, 12],
#     'fetchArticleCount' = 5
# }
# _recommandArticlesInfo: {
#     'fetchDateTime': datetime.now(),
#     'expireDateTime': datetime.now(),
#     'recommandRules': None,
#     'articleInfos': None
# }


def routes_serachingArticlesInfo():

    if 'GET' == request.method:

        _searchStr = request.args.get('searchStr')
        _searchTag = request.args.get('searchTag')
        _searchCount = request.args.get('searchCount')
        _searchOffset = request.args.get('searchOffset')

        _flag, _retDict = articleController.searchArticle(
            _searchStr, _searchTag, _searchCount, _searchOffset)
        return jsonify(_retDict)


def routes_article(articleId):
    if 'GET' == request.method:
        _flag, _retDict = articleController.fetchArticleByArticleId(articleId)
        return jsonify(_retDict)
# '/edit/api , methods=['POST']


def routes_postArticle():
    if 'POST' == request.method:
        _articleData = request.get_json()
        _flag, _retDict = articleController.postArticle(_articleData, g.userId)
        return jsonify(_retDict)


# @bp.route('/edit/api/<articleId>', methods=['GET', 'POST', 'DELETE','PATCH'])


def routes_editArticle(articleId):
    # Must validate article owner is session.user
    # GET-> articleId is -999 then return new article.
    #      else return article by articleId if article exist.

    # DELETE-> Delete article by articleId
    # PUT-> Update all data of the article.
    # PATCH ->  Update article status 'articleStatus'.

    if 'GET' == request.method:

        _flag, _retDict = articleController.fetchEditArticle(
            articleId, g.userId)
        return jsonify(_retDict)

    elif 'DELETE' == request.method:
        _flag, _retDict = articleController.deleteArticle(articleId, g.userId)
        return jsonify(_retDict)
    elif 'PUT' == request.method:
        _jsonData = request.get_json()
        _flag, _retDict = articleController.updateArticle(
            articleId, _jsonData, g.userId)
        return jsonify(_retDict)
    elif 'PATCH' == request.method:
        _articleStatus = request.get_json().get('articleStatus')
        _flag, _retDict = articleController.udpateArticleStatus(
            articleId, _articleStatus, g.userId)
        return jsonify(_retDict)

# @bp.route('/article/articleInfo', methods=['GET'])


def routes_articlesInfo():

    if 'GET' == request.method:

        _flag, _retDict = articleController.fetchEditArticlesInfo(
            request.args['count'], request.args['offset'], g.userId)
        return jsonify(_retDict)


def routes_getRecommandArticlesInfo():
    # Fetch articles-info with recommand article list
    # Store recommand-articleInfo in memory (avoid server repeated access to the sqlDB when request)
    # Set expire datetime and recommand-article-rule , if rule changes or data is in expired then re-fetch the recommand articles
    _retData = {
        'msg': 'Successed',
        'type': 'get-RecommandArticlesInfo',
        'articlesInfo': None
    }
    _maxReturnArticleCount = 5
    if 'GET' == request.method:
        _fetchRules = {'forceRecommandIdList': [11, 12]}
        _retArticlesInfo = []
        _flag, _retDict = articleController.getRecommandArticlesInfo(
            _maxReturnArticleCount, _fetchRules)
        return jsonify(_retDict)


routes.append(dict(
    rule='/article/<articleId>',
    view_func=routes_article,
    options=dict(methods=['GET'])
))
routes.append(dict(
    rule='/article/edit/<articleId>',
    view_func=routes_editArticle,
    options=dict(methods=['GET', 'POST', 'DELETE', 'PATCH', 'PUT'])
))
routes.append(dict(
    rule='/article/articlesInfo',
    view_func=routes_articlesInfo,
    options=dict(methods=['GET'])
))
routes.append(dict(
    rule='/article/edit',
    view_func=routes_postArticle,
    options=dict(methods=['POST'])
))
routes.append(dict(
    rule='/article/recommandArticlesInfo',
    view_func=routes_getRecommandArticlesInfo,
    options=dict(methods=['GET'])
))
routes.append(dict(
    rule='/articles',
    view_func=routes_serachingArticlesInfo,
    options=dict(methods=['GET'])
))
