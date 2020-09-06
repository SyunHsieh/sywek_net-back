from ..model import articleModel
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
    _retArticlesInfo = articleModel.searchArticleByUser(
        _searchStr, _searchTag, _searchCount, _searchOffset)
    _retDict['articlesInfo'] = _retArticlesInfo
    _retDict['msg'] = Enum_ResponseMsg.Successed.value

    return(True, _retDict)


def fetchArticleByArticleId(articleId):
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

    _flag, _articleRef = articleModel.fetchArticleJsonAndInfo(_articleId)

    # check article is not private and exists.
    if _flag == False:
        if _articleRef['articleStatus'] == False:
            _retDict['msg'] = Enum_ResponseMsg.ArticleIsPrivate.value
        else:
            _retDict['msg'] = Enum_ResponseMsg.ArticleFetchFailed.value
        return(False, _retDict)

    # jsonify article and append
    _retDict['article'] = _articleRef['articleJsonifyFunc']()
    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    return (True, _retDict)
