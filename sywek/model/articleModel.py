from ..Article import Article
from ..User import User
from datetime import datetime


def searchArticleByUser(searchStr, searchTag, searchCount, searchOffset):
    """
    Return articles' info when match the searchRules
    Return None when not match.
    """

    _ret = Article.searchArticle(
        searchStr, searchTag, searchCount, searchOffset)

    return [{'id': art.id, 'isOpened': art.isOpened,
             'articleHeader': art.header, 'secondHeader': art.secondHeader, 'headerImage': art.headerImage, 'postDT': art.postDT, 'lastEditDT': art.lastEditDT, 'authorInfo': {'authorName': art.author.name, 'authorId': art.author.id}} for art in _ret]


def fetchArticleJsonAndInfo(articleId, userInstance=None):
    """
    Return false when fetch article failed (article not exists which article has articleId)
    Return true when fetch article successed
    Return format => (flag , articleRef)
    articleRef{
        'articleId' : article's id,
        'articleJsonifyFunc' :article parse to json function's address,
        'articleStatus' : boolean > is article publish
    }
    function types:
    type 1. articleId
    type 2. articleId , userInstance : (will check article owner)
    """

    _article = Article(articleId)

    if _article is None or not _article.isSearchingInDB:
        return (False, None)

    # Check article owner is the user
    if not userInstance is None and userInstance.id != _article.author.id:
        return (False, None)

    _articleRef = {
        'articleId': _article.id,
        'articleStatus': _article.isOpened,
        'articleJsonifyFunc': _article.jsonify
    }
    return (True, _articleRef)


def postArticle(article, articleStatus, postUserInstance):
    """
    return true when post article successed
    return false when post article failed or article has invalied data
    return type => (flag , articleId , articleStatus)
    """

    _article = Article.loadFromJson(article, False)

    # create Article instance using loadFromJson failed
    if not _article:
        return (False, None, None)

    _article.author = postUserInstance
    _article.isOpened = articleStatus

    _flag, *_ = _article.commit()

    # commit article falied
    if not _flag:
        return (False, None, None)

    return (True, _article.id, _article.isOpened)


def getEmptyArticleJson(userInstance):
    """
    return emptyArticle
    """
    return Article.getEmptyArticleJson(userInstance)


def fetchUserArticlesInfo(userInstance, count, offset):
    """
    return true when fetch own articles' info successed
    return false when fetch own articles' info failed
    return format=>(flag , articlesInfoList)
    """

    if userInstance is None:
        return (False, None)

    _articlesInfo = [{
        'id': art.id,
        'isOpened': art.isOpened,
        'articleHeader': art.header,
        'headerImage': art.headerImage,
        'postDT': art.postDT,
        'lastEditDT': art.lastEditDT
    } for art in userInstance.getArticlesInfo(count, offset)]

    return (True, _articlesInfo)


def deleteArticle(articleId, userInstance):
    """
    return true when delete article successed.
    return false when delete article failed
    """

    _article = Article(articleId, True)

    # check article exists and the client is article owner
    if _article is None or _article.author.id != userInstance.id:
        return False

    _flag = _article.deleteArticle(userInstance)
    return _flag


def updateArticle(articleId, articleJson, articleStatus, userInstance):
    """
    return ture when update article succesed
    return false when udpate article failed
    return format => (flag , articleInfo)

    articleInfo = {
        'id' :articleId,
        'articleStatus': article.isOpened
    }

    function parameters
    *articleJson : None means update articleStatus only
    """
    _loadInfoFlag = False if articleJson is not None else True
    _article = Article(articleId, _loadInfoFlag)

    # check the article exists and the client isarticle owner
    if not _article or _article.author.id != userInstance.id:
        return (False, None)

    # load article by articleJson and put it in the _article object
    if not _loadInfoFlag:
        _retArticle = Article.loadFromJson(articleJson, False, _article)

        # return None when load article from json failed
        if not _retArticle:
            return (False, None)

    # setArticleStatus and article last-edit-datetime
    _article.isOpened = articleStatus
    _article.lastEditDT = datetime.now()

    _flag, *_ = _article.commit()

    if not _flag:
        return (False, None)

    return (True, {
        'id': _article.id,
        'articleStatus': _article.isOpened
    })


def getRecommandArticlesInfo(maxcount, forceArticleIdList=None):
    """
    return format => (flag , articlesInfo)
    """

    _retArticlesInfo = []

    # get article by id
    if forceArticleIdList is not None:
        _articleList = Article.getArticleInfoFromIdList(
            forceArticleIdList, True)

        for art in _articleList:
            _retArticlesInfo.append(art)

    _restArticleCount = maxcount - len(_retArticlesInfo)

    _articleList = Article.getLatestArticleInfo(
        _restArticleCount, [i.id for i in _retArticlesInfo])

    for art in _articleList:
        _retArticlesInfo.append(art)

    _retArticlesInfo = [{
        'id': art.id,
        'article': art.jsonify()
    } for art in _retArticlesInfo]
    return(True, _retArticlesInfo)
