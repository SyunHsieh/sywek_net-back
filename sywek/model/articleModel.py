from ..Article import Article
from ..User import User
from datetime import datetime
from ..RandomString import RandomSelectString
from ..base64DataSplit import base64DataSplit
from ..model import GCStorageModel


def _uploadArticlesImageOnGCS(articleInstance, bucketname):
    """
    return True when full image upload successed
    return Flase when image upload failed 
    return format => (flag , uploadedBlobList )
    """
    _retBlobList = []
    _bucketName = bucketname
    _rnadomSelSample = '1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'
    _articleLayerOnePrefix = _articleImageBlobPrefix = 'image/article/' + \
        RandomSelectString(_rnadomSelSample, 6)
    _prefixStrCount = 6
    _rerandomPrefixCount = 0
    while GCStorageModel.isBlobExists(_bucketName, _articleLayerOnePrefix):
        # get new blob prefix
        _articleLayerOnePrefix = _articleImageBlobPrefix = 'image/article/' + \
            RandomSelectString(_rnadomSelSample, _prefixStrCount)
        _rerandomPrefixCount = _rerandomPrefixCount+1
        if _rerandomPrefixCount == 3:
            _rerandomPrefixCount = 0
            _prefixStrCount = _prefixStrCount + 1

    _articleImageBlobPrefix = _articleLayerOnePrefix+'/'+RandomSelectString(
        "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm", 3)+'_'

    # upload article-header-image
    # split base64str
    if articleInstance.headerImage.startswith('image/article'):
        # copy
        _fileExtension = articleInstance.headerImage.split('.')[1]
        _blobname = _articleImageBlobPrefix + \
            'header.'+_fileExtension
        _flag = GCStorageModel.copyBlob(
            _bucketName, articleInstance.headerImage, _blobname)
        if not _flag:
            return (False, _retBlobList)
        articleInstance.headerImage = _blobname
    else:
        _flag, _dataDict = base64DataSplit(articleInstance.headerImage)

        if not _flag:
            return (False, _retBlobList)

        _fileExtension = _dataDict['contentType'].split('/')[1]
        _blobname = _articleImageBlobPrefix+'header.'+_fileExtension
        _uploadImageFlag, _retBlobName = GCStorageModel.uploadBlobFromBase64(
            _bucketName, _blobname, _dataDict['data'], _dataDict['contentType'], True, 2)

        if not _uploadImageFlag:
            return (False, _retBlobList)

        # append newbloblist and oldbloblist
        _retBlobList.append(_retBlobName)
        articleInstance.headerImage = _retBlobName

    for sectionIndex, section in enumerate(articleInstance.content):
        for contentEleIndex, contentEle in enumerate(section['contentElements']):
            if contentEle['contentType'] == 'image':
                # split base64str
                # check url
                if contentEle['content']['imageUrl'].startswith('image/article'):
                    _fileExtension = contentEle['content']['imageUrl'].split('.')[
                        1]
                    _blobname = _articleImageBlobPrefix + \
                        '{}_{}.'.format(
                            sectionIndex, contentEleIndex)+_fileExtension
                    _flag = GCStorageModel.copyBlob(
                        _bucketName, contentEle['content']['imageUrl'], _blobname)
                    if not _flag:
                        return (False, _retBlobList)
                    # append newbloblist and oldbloblist
                    _retBlobList.append(_blobname)
                    contentEle['content']['imageUrl'] = _blobname

                else:
                    _flag, _dataDict = base64DataSplit(
                        contentEle['content']['imageUrl'])

                    if not _flag:
                        return (False, _retBlobList)

                    _fileExtension = _dataDict['contentType'].split('/')[1]
                    _blobname = _articleImageBlobPrefix + \
                        '{}_{}.'.format(
                            sectionIndex, contentEleIndex)+_fileExtension
                    _uploadImageFlag, _retBlobName = GCStorageModel.uploadBlobFromBase64(
                        _bucketName, _blobname, _dataDict['data'], _dataDict['contentType'], True, 2)
                    if not _uploadImageFlag:
                        return (False, _retBlobList)
                    # append newbloblist and oldbloblist
                    _retBlobList.append(_retBlobName)
                    contentEle['content']['imageUrl'] = _retBlobName

    return (True, _retBlobList)


def searchArticle(searchStr, searchTag, searchCount, searchOffset):
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
    # upload article's images
    _flag, _newBlobList = _uploadArticlesImageOnGCS(
        _article, 'sywek_net_bucket')

    if not _flag:
        for blob in _newBlobList:
            GCStorageModel.deleteBlob('sywek_net_bucket', blob)
            return (False, None, None)

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


def fetchUserArticlesInfo(userInstance, count, offset, isPublishOnly=False):
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
    } for art in userInstance.getArticlesInfo(count, offset, isPublishOnly)]

    return (True, _articlesInfo)


def deleteArticle(articleId, userInstance):
    """
    return true when delete article successed.
    return false when delete article failed
    """
    _bucketName = 'sywek_net_bucket'
    _article = Article(articleId)

    # check article exists and the client is article owner
    if _article is None or _article.author.id != userInstance.id:
        return False

    # collect old article blob
    _oldArticlesBlobList = []

    _oldArticlesBlobList.append(_article.headerImage)

    for section in _article.content:
        for contentEle in section['contentElements']:
            if contentEle['contentType'] == 'image':
                _oldArticlesBlobList.append(
                    contentEle['content']['imageUrl'])

    _flag = _article.deleteArticle(userInstance)
    if _flag:
        for blob in _oldArticlesBlobList:
            GCStorageModel.deleteBlob(_bucketName, blob)
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
    _bucketName = 'sywek_net_bucket'
    _loadInfoFlag = False if articleJson is not None else True
    _article = Article(articleId, _loadInfoFlag)

    # collect old article blob
    _oldArticlesBlobList = []
    if not _loadInfoFlag:
        _oldArticlesBlobList.append(_article.headerImage)

        for section in _article.content:
            for contentEle in section['contentElements']:
                if contentEle['contentType'] == 'image':
                    _oldArticlesBlobList.append(
                        contentEle['content']['imageUrl'])

    # check the article exists and the client isarticle owner
    if not _article or _article.author.id != userInstance.id:
        return (False, None)

    # setArticleStatus and article last-edit-datetime
    _article.isOpened = articleStatus
    _article.lastEditDT = datetime.now()

    # load article by articleJson and put it in the _article object
    if not _loadInfoFlag:
        _retArticle = Article.loadFromJson(articleJson, False, _article)

        # return None when load article from json failed
        if not _retArticle:
            return (False, None)

        # upload new article on GCS
        _flag, _retBlobList = _uploadArticlesImageOnGCS(
            _retArticle, _bucketName)

        if not _flag:
            # delete uploaded blob and return
            for blob in _retBlobList:
                GCStorageModel.deleteBlob(_bucketName, blob)
                return (False, None)

    _flag, *_ = _article.commit()

    if not _flag:
        return (False, None)

    for blob in _oldArticlesBlobList:
        GCStorageModel.deleteBlob(_bucketName, blob)
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
