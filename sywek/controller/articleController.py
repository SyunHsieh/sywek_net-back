from ..model import articleModel, userModel
from ..DictValidate import validateDict
from ..Response import getResponseBaseDict, getResponseMsgString, Enum_ResponseMsg, Enum_ResponseType
import re


def searchArticle(searchStr, searchTag, searchCount, searchOffset):
    """
    Return false when search articles failed.
    Returm True when search articles successed.

    return => (flag , retDict)
    """

    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articlesSearch.value
    # declare searchRule in _retDict
    _retDict['searchRule'] = {}

    _searchStr = ''
    _searchTag = ''
    _searchCount = 10
    _searchOffset = 0
    # Verify searchRules parameters
    try:
        _searchStr = [re.sub(r'[=<*/]', '', item)
                      for item in searchStr.split(' ')]
        _searchTag = [re.sub(r'[=<*/]', '', item)
                      for item in searchTag.split(' ')]
        _searchCount = int(searchCount)
        _searchOffset = int(searchOffset)
    except Exception:
        _retDict['searchRule']['searchStr'] = searchStr
        _retDict['searchRule']['searchTag'] = searchTag
        _retDict['searchRule']['searchCount'] = searchCount
        _retDict['searchRule']['searchOffset'] = searchOffset
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    # append search infomation in searchRules
    _retDict['searchRule']['searchStr'] = _searchStr
    _retDict['searchRule']['searchTag'] = _searchTag
    _retDict['searchRule']['searchCount'] = _searchCount
    _retDict['searchRule']['searchOffset'] = _searchOffset

    # Search articles' info
    _retArticlesInfo = articleModel.searchArticle(
        _searchStr, _searchTag, _searchCount, _searchOffset)
    _retDict['articlesInfo'] = _retArticlesInfo
    _retDict['msg'] = Enum_ResponseMsg.Successed.value

    return(True, _retDict)


def fetchArticleByArticleId(articleId, userId):
    """
    Return True when fetch successed 
    Return False when fetch article failed (article not found or other error)
    return format => (flag , retDict)
    """

    # Declare retDict and set type
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articleFetch.value

    _articleId = 0
    # verify parameters
    try:
        _articleId = int(articleId)
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    _flag, _articleRef = articleModel.fetchArticleJsonAndInfo(
        _articleId)

    # check article is not private and exists.
    if _flag == False:
        if _articleRef['articleStatus'] == False:
            _retDict['msg'] = Enum_ResponseMsg.ArticleIsPrivate.value
        else:
            _retDict['msg'] = Enum_ResponseMsg.ArticleFetchFailed.value
        return(False, _retDict)

    # jsonify article and append
    _flag, _user = userModel.getUser(userId)
    _retDict['article'] = _articleRef['articleJsonifyFunc'](_user)
    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    return (True, _retDict)


def postArticle(articleData, postUserId):
    """
    post article and set article-status(true means airticle is publish ,false) 
    return truple (flag ,retDict)
    #retDict['articleId'] = article id
    #retDict['articleStatus'] = BOOLEAN article is opened
    """

    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articlePost.value

    _postUserId = 0

    # verify parameters
    try:
        _postUserId = int(postUserId)
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    # verify articleData
    if not validateDict(articleData, ['article', 'articleStatus']):
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    # check user exists and was login.
    if _postUserId is None:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return(False, _retDict)

    _flag, _user = userModel.getUser(_postUserId)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        return (False, _retDict)

    # post article
    _flag, _articleId, _articleStatus = articleModel.postArticle(
        articleData['article'], articleData['articleStatus'], _user)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.ArticlePostFalied.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['articleId'] = _articleId
    _retDict['articleStatus'] = _articleStatus
    return (True, _retDict)


def fetchEditArticle(articleId, userId):
    """
    articleId equals to -999 then return new-edit-article
    return true when fetch eidt-article with articleId successed
    return false when fetch edit-article with articleId failed
    return type =>(flag , retDict)
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articleFetch.value

    # verify function parameters
    _articleId = 0

    try:
        _articleId = int(articleId)
    except Exception:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return(False, _retDict)

    # check user exists and was login.
    if userId is None:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return(False, _retDict)

    _flag, _user = userModel.getUser(userId)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        return (False, _retDict)

    # fetch new article
    if _articleId == -999:
        _retDict['article'] = articleModel.getEmptyArticleJson(_user)
        _retDict['articleId'] = _articleId
        _retDict['msg'] = Enum_ResponseMsg.Successed.value
        return(True, _retDict)

    # fetch exists article by article id
    _flag, _articleRef = articleModel.fetchArticleJsonAndInfo(
        _articleId, _user)

    # flag is False when article not exists or the article's owner not the user.
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.ArticleEditFetchFailed.value
        return (False, _retDict)

    # append article data in _retDict and set message
    _retDict['article'] = _articleRef['articleJsonifyFunc'](_user)
    _retDict['articleStatus'] = _articleRef['articleStatus']
    _retDict['articleId'] = _articleRef['articleId']
    _retDict['msg'] = Enum_ResponseMsg.Successed.value

    return (True, _retDict)


def fetchArticlesInfo(count, offset, userId, isCheckLogin=True, isPublishOnly=False):
    """
    return articles' info 
    return True when fetch successed
    return False when fetch failed
    return format => (flag , retDict)

    retDict['articlesInfo'] = the fetch articles' info
    retDict['fetchRules']['count'] = the fetch count 
    retDict['fetchRules']['offset'] = the fetcg articles' offset

    parameters:
    count : Fetch articles' info count
    offset : Fetch articles' info offset 
    userId : articles' author id
    isCheckOwner : True : will check user as userId are those articles owner 
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articlesInfoSelfFetch.value

    _count = 0
    _offset = 0

    # verify function parameters
    try:
        _count = int(count)
        _offset = int(offset)
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return(False, _retDict)

    if _offset < 0 or _count <= 0:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return(False, _retDict)

    _retDict['fetchRules'] = {
        'count': _count,
        'offset': _offset
    }

    # check user exists and was login.
    if userId is None:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return(False, _retDict)

    _flag, _user = userModel.getUser(userId)

    if not _flag:
        if isCheckLogin:
            _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        else:
            _retDict['msg'] = Enum_ResponseMsg.ArticlesInfoFetchFailed.value
        return (False, _retDict)

    # Fetch user's articles info by count offset and userInstance
    _flag, _articlesInfo = articleModel.fetchUserArticlesInfo(
        _user, _count, _offset, isPublishOnly)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.ArticlesInfoFetchFailed.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['articlesInfo'] = _articlesInfo
    return (True, _retDict)


def deleteArticle(articleId, userId):
    """
    return True when delete article successed
    return False when delete article failed(article not exists or not article owner)
    retrun format => (flag , retDict)
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articleEditDelete.value

    _articleId = 0

    # verify function parameters
    try:
        _articleId = int(articleId)
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    _retDict['articleId'] = _articleId

    # check user exists and was login.
    if userId is None:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return(False, _retDict)
    _flag, _user = userModel.getUser(userId)
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        return (False, _retDict)

    # delete article
    _flag = articleModel.deleteArticle(_articleId, _user)

    # delete article failed ,its means article not exists or not the article owner.
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.ArticleEditDeleteFailed.value
        return(False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    return (True, _retDict)


def updateArticle(articleId, articleData, userId):
    """
    update the article which article id is articleId
    return True when update article successed
    return False when udpate article failed (not article owner or article not exists)
    return format => (flag , retDict)
    retDict['articleId'] = articleId
    retDict['articleStatus] = the article status
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articleEditUpdate.value

    _articleId = 0
    _articleStauts = False
    # verify function parameters
    if not validateDict(articleData, ['article', 'articleStatus']):
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    try:
        _articleId = int(articleId)
        _articleStauts = bool(articleData['articleStatus'])
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    _retDict['articleId'] = _articleId

    # check user exists and was login.
    if userId is None:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return(False, _retDict)
    _flag, _user = userModel.getUser(userId)
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        return (False, _retDict)

    # update article
    _flag, _articleInfo = articleModel.updateArticle(
        _articleId, articleData['article'], articleData['articleStatus'], _user)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.ArticleEditUpdateFailed.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['articleStatus'] = _articleInfo['articleStatus']
    return (True, _retDict)


def udpateArticleStatus(articleId, articleStatus, userId):
    """
    return True when update article-status successed
    retrun False when update article-status failed (article not exists or not the article owner)
    return format =>(flag , retDict)

    retDict['articleId'] = article id
    retDict['articleStatus] = article status
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articleEditStatusUpdate.value

    _articleId = 0
    _articleStatus = False
    # verify function parameters
    try:
        _articleId = int(articleId)
        _articleStatus = bool(articleStatus)
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    _retDict['articleId'] = _articleId

    # check user exists and was login.
    if userId is None:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return(False, _retDict)
    _flag, _user = userModel.getUser(userId)
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        return (False, _retDict)

    # update article
    _flag, _articleInfo = articleModel.updateArticle(
        _articleId, None, articleStatus=_articleStatus, userInstance=_user)

    # return false means update the article failed
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.ArticleEditStatusUpdateFailed.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['articleId'] = _articleInfo['id']
    _retDict['articleStatus'] = _articleInfo['articleStatus']
    return (True, _retDict)


def getRecommandArticlesInfo(maxcount, fetchRules=None):
    """
    return ture when get recommand article successed
    return False when get recommand article failed
    return format =>(flag , retDict)

    retDict['_retArticlesInfo'] = Recommand articles' info

    parameters:
    fetchRules:{
        forceRecommandIdList : type of int list 
        ...
    }
    """
    _varifyString = ['forceRecommandIdList']

    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.articlesGetRecommand.value

    # verify function parameters
    if maxcount <= 0 or not validateDict(fetchRules, _varifyString):
        _retDict['msg'] = Enum_ResponseMsg.ArticleGetRecommandFalied.value
        return (False, _retDict)

    _flag, _recommandArticleList = articleModel.getRecommandArticlesInfo(
        maxcount, fetchRules['forceRecommandIdList'])

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.ArticleGetRecommandFalied.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['_retArticlesInfo'] = _recommandArticleList
    return (True, _retDict)
