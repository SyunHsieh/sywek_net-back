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
    _retData = {
        'type': '',
        'msg': '',
        'articleId': '',

    }
    if g.user is None:
        _retData['msg'] = 'Not log in.'
        return jsonify(_retData)
    # POST-> Create a new article.{article , articleStatus}
    if 'POST' == request.method:
        _retData['type'] += 'edit-article-create'
        _jsonData = request.get_json()
        if not validateDict(_jsonData, ['article', 'articleStatus']):
            _retData['msg'] = 'data invalid.'
            return jsonify(_retData)

        _newArticle, _msg = Article.loadFromJson(
            _jsonData.get('article'), True)
        if _newArticle:
            _newArticle.author = g.user
            _newArticle.isOpened = False if not _jsonData.get(
                'articleStatus') else _jsonData.get('articleStatus')

            _flag, _msg = _newArticle.commit()
            _retData['msg'] = _msg
            if _flag:
                _retData['articleId'] = _newArticle.id
                _retData['articleStatus'] = _newArticle.isOpened
        else:
            _retData['msg'] = _msg

        return jsonify(_retData)
# @bp.route('/edit/api/<articleId>', methods=['GET', 'POST', 'DELETE','PATCH'])


def routes_editArticle(articleId):
    # Must validate article owner is session.user
    # GET-> articleId is -999 then return new article.
    #      else return article by articleId if article exist.

    # DELETE-> Delete article by articleId
    # PUT-> Update all data of the article.
    # PATCH ->  Update article status 'articleStatus'.

    _retData = {
        'type': 'edit-article',
        'msg': '',
        'articleId': -1,
        'articleStatus': False,
    }
    if g.user is None:
        _retData['msg'] = 'Not log in.'
        return jsonify(_retData)

    if 'GET' == request.method:
        _articleId = 0
        try:
            _articleId = int(articleId)
        except ValueError:
            _retData['msg'] = 'Parameters invalid.'
            return jsonify(_retData)

        _retData['articleId'] = _articleId

        # fetch new article with author
        if _articleId == -999:
            _retData['type'] += '-new-article'
            _retData['msg'] = 'Successed'
            _retData['article'] = Article.getEmptyArticleJson(g.user)

        # get exist article.
        else:
            _retData['type'] += '-get-article'
            _article = Article(_articleId)

            if _article.isSearchingInDB:
                if _article.author.id == g.user.id:
                    _retData['msg'] = 'Successed'
                    _retData['articleStatus'] = _article.isOpened
                    _retData['article'] = _article.jsonify(g.user)
                else:
                    _retData['msg'] = 'Not owner.'

            else:
                _retData['msg'] = 'Article not exist.'

        return jsonify(_retData)
    elif 'DELETE' == request.method:
        _retData['type'] += '-delete'
        _articleId = 0
        try:
            _articleId = int(articleId)
        except ValueError:
            _retData['msg'] = 'Parameters invalid.'
            return jsonify(_retData)

        _delArticle = Article(_articleId)
        if _delArticle.id is None:
            _retData['msg'] = 'Article not exist.'
            return jsonify(_retData)
        if _delArticle.author.id != g.user.id:
            _retData['msg'] = 'Not owner.'
            return jsonify(_retData)

        _flag, _msg = _delArticle.deleteArticle(g.user)
        _retData['articleId'] = _delArticle.id
        # _retData['articleStatus'] = _delArticle.isOpened

        if _flag:
            _retData['msg'] = 'Successed'
        else:
            _retData['msg'] = _msg
        return jsonify(_retData)
    elif 'PUT' == request.method:
        _articleId = 0
        try:
            _articleId = int(articleId)
        except ValueError:
            _retData['msg'] = 'Parameters invalid.'
            return jsonify(_retData)

        _retData['type'] += '-update'
        _jsonData = request.get_json()

        _articleJson = _jsonData.get('article')
        _articleStatus = _jsonData.get('articleStatus')
        if not _articleJson:
            _retData['msg'] = 'Data invalid.'
            return jsonify(_retData)

        _article = Article(_articleId)
        if _article.isSearchingInDB:
            _retData['articleId'] = _article.id

            if _article.author.id != g.user.id:
                _retData['msg'] = 'Not owner.'
                return jsonify(_retData)
            else:
                retArticle, _msg = Article.loadFromJson(
                    _articleJson, True, _article)
                _article.isOpened = _articleStatus
                _article.lastEditDT = datetime.now()
                _retData['msg'] = _msg

                if retArticle:

                    _flag, _msg = _article.commit()
                    _retData['articleStatus'] = _article.isOpened
                    _retData['msg'] = _msg
                    if _flag:
                        _retData['msg'] = 'Successed'
        else:
            _retData['msg'] = 'Article not exist.'

        return jsonify(_retData)
    elif 'PATCH' == request.method:
        _articleId = 0
        try:
            _articleId = int(articleId)
        except ValueError:
            _retData['msg'] = 'Parameters invalid.'
            return jsonify(_retData)

        _retData['type'] += '-update-patch'
        _jsonData = request.get_json()

        _articleStatus = _jsonData.get('articleStatus')
        if _articleStatus is None:
            _retData['msg'] = 'Data invalid.'
            return jsonify(_retData)

        _article = Article(_articleId, True)
        if _article.isSearchingInDB:
            _retData['articleId'] = _article.id

            if _article.author.id != g.user.id:
                _retData['msg'] = 'Not owner.'
                return jsonify(_retData)
            else:
                _article.isOpened = _articleStatus
                _article.lastEditDT = datetime.now()

                _flag, _msg = _article.commit()
                _retData['articleStatus'] = _article.isOpened
                _retData['msg'] = _msg
                if _flag:
                    _retData['msg'] = 'Successed'
        else:
            _retData['msg'] = 'Article not exist.'

        return jsonify(_retData)
        # elif _type == 'articleStatus':
        #     _articleStatusJson = _jsonData.get('articleStatue')
        #     if not _articleStatusJson:
        #         _retData['msg'] = 'Data invalid.'
        #         return jsonify(_retData)

        #     _article = Article(_articleId, True)
        #     if _article.isSearchingInDB:
        #         _retData['articleId'] = _article.id
        #         _retData['articleStatus'] = _articleStatusJson

        #         if _article.author.id != g.user.id:
        #             _retData['msg'] = 'Not owner.'
        #             return jsonify(_retData)
        #         else:
        #             _article.isOpened = _articleStatusJson

        #             _flag, _msg = _article.commit()
        #             _retData['msg'] = _msg
        #             if _flag:
        #                 _retData['msg'] = 'Successed'
        #     else:
        #         _retData['msg'] = 'Article not exist.'
# @bp.route('/article/articleInfo', methods=['GET'])


def routes_articlesInfo():
    # isOpened , article-title , article-postDT , article-headerImage , article-id ,
    _retData = {
        'type': 'get-articlesInfo',
        'msg': '',
    }
    _count = 0
    _offset = 0
    try:
        _count = int(request.args['count'])
        _offset = int(request.args['offset'])
    except ValueError:
        _retData['msg'] = 'Parameters invalid.'
        return jsonify(_retData)

    if 'GET' == request.method:
        if not g.user:
            _retData['msg'] = 'Not login.'
        else:
            _retData['articlesInfo'] = [{'id': art.id, 'isOpened': art.isOpened,
                                         'articleHeader': art.header, 'headerImage': art.headerImage, 'postDT': art.postDT, 'lastEditDT': art.lastEditDT} for art in g.user.getArticlesInfo(_count, _offset)]
            _retData['msg'] = 'Successed'

        return jsonify(_retData)


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
        _forceRecommandIdList = [11, 12]
        _retArticlesInfo = []

        _articleList = Article.getArticleInfoFromIdList(_forceRecommandIdList)

        for art in _articleList:
            _retArticlesInfo.append(art)

        # check or filter _articleList...
        _restArticleCount = _maxReturnArticleCount - len(_retArticlesInfo)

        _articleList = Article.getLatestArticleInfo(
            _restArticleCount, [i.id for i in _retArticlesInfo])

        for art in _articleList:
            _retArticlesInfo.append(art)

        _retData['_retArticlesInfo'] = [{'id': art.id, 'article': art.jsonify()}
                                        for art in _retArticlesInfo]
        return jsonify(_retData)

        # _curDatetime = datetime.now()
        # Check is articlesInfo need update.
        # if _recommandArticlesInfo['expireDateTime'] <= _curDatetime:
        #     _recommandArticlesInfo['fetchDateTime'] = dateTime
        #     _recommandArticlesInfo['expireDateTime'] = _recommandArticlesRules['expireRules'](
        #         _curDatetime)


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
