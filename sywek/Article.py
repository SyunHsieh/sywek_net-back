from .db import articles_table, get_db, post_likes_table, post_comments_table
from datetime import datetime
from sqlalchemy import func, text
from sqlalchemy.orm import load_only
from .DictValidate import validateDict
import re


class Article():
    _articleFormatVersion = "0.1.0"
    _infoQueryStr = 'id', 'author_id', 'header', 'secondHeader', 'headerImage', 'postDT', 'lastEditDT', 'tags', 'likesCount', 'isOpened', 'commentsCount'

    @classmethod
    def searchArticle(cls, searchingStr, searchingTag, searchCount=10, searchOffset=0):
        _sqlBase = "SELECT distinct art.id , art.\"postDT\"  FROM articles_table as art, json_array_elements(art.content) as ctes , json_array_elements(ctes -> 'contentElements') as cts WHERE art.\"isOpened\" = TRUE "
        print(_sqlBase)
        _baseStr = "(cts -> 'content' ->> 'text' LIKE '%{0}%' OR LOWER(art.header) LIKE '%{0}%' OR LOWER(art.\"secondHeader\") LIKE '%{0}%')"
        _baseTagStr = "'{0}' ILIKE ANY(art.tags)"

        _searchingStr = [_baseStr.format(stritem.lower())
                         for stritem in searchingStr if stritem != '']
        _searchingTag = [_baseTagStr.format(
            stritem.lower()) for stritem in searchingTag if stritem != '']
        _concatStr = _searchingStr+_searchingTag
        _conditionStr = ''
        # _sqlBase = ''
        if not len(_concatStr) == 0:
            _conditionStr = _concatStr[0]
            for c in _concatStr[1:]:
                _conditionStr = _conditionStr + ' OR ' + c
            _sqlBase = _sqlBase + 'AND ' + '({0})'.format(_conditionStr)

        _sqlBase = _sqlBase + \
            ' ORDER BY art.\"postDT\" DESC LIMIT {0} OFFSET {1}'.format(
                searchCount, searchOffset)

        _list = articles_table.query.options(load_only(
            'id', 'author_id', 'header', 'secondHeader', 'headerImage', 'postDT', 'lastEditDT', 'tags', 'likesCount', 'isOpened', 'commentsCount')).from_statement(text(_sqlBase))
        print('condition : ', _list)
        _list = _list.all()
        _articles_Info = [cls(loadInfo=True, sqlInstance=item)
                          for item in _list]
        return _articles_Info

    @ classmethod
    def getLatestArticleInfo(cls, articleCount, notInIdList, isOpened=True):
        _articleDataList = articles_table.query.options(load_only(
            'id', 'author_id', 'header', 'secondHeader', 'headerImage', 'postDT', 'lastEditDT', 'tags', 'likesCount', 'isOpened', 'commentsCount')).filter(
                articles_table.id.notin_(notInIdList), articles_table.isOpened == isOpened).order_by(articles_table.postDT.desc()).limit(articleCount)

        _articleList = [cls(loadInfo=True, sqlInstance=articleD)
                        for articleD in _articleDataList]
        return _articleList

    @classmethod
    def getArticleInfoFromIdList(cls, listOfId, isOpened=True):
        _articleDataList = articles_table.query.options(load_only(
            'id', 'author_id', 'header', 'secondHeader', 'headerImage', 'postDT', 'lastEditDT', 'tags', 'likesCount', 'isOpened', 'commentsCount')).filter(articles_table.id.in_(listOfId), articles_table.isOpened == isOpened).all()

        _articleList = [cls(loadInfo=True, sqlInstance=articleD)
                        for articleD in _articleDataList]
        return _articleList

    @classmethod
    def getEmptyArticleJson(cls, author):

        _retInfo = author.getAuthorInfo(author)
        _jsonArticle = {
            'articleFormatVersion': Article._articleFormatVersion,

            'articleInfo': {
                'headerImage': '',
                'header': '',
                'secondHeader': '',
                'tags': [],
                'postDateTime': {
                    'date': '',
                    'time': '',
                    'GMT': 0,
                },
            },



            'sections': [{'contentElements': [{
                'content': {
                    'text': '',
                },
                'contentType': None,
            }, ]}],

        }
        _jsonArticle['authorInfo'] = _retInfo['authorInfo']
        _jsonArticle['readerInfo'] = _retInfo['readerInfo']
        return _jsonArticle

    @classmethod
    def validateContentElement(cls, el):
        _elType = el['contentType']
        _retValidate = True
        if _elType in ('header', 'subTitle', 'text'):
            if not validateDict(el['content'], ['text']):
                return False
            re.sub('(?:\r\n|\r|\n)', '', re.sub(
                '<[^>]*>', '', el['content']['text']))

        elif _elType == 'video':
            if not validateDict(el['content'], ['videoUrl']):
                return False
            if not re.search('https://www.youtube.com/embed/', el['content']['videoUrl']).span() == (0, 30):
                return False
        elif _elType == 'image':
            if not validateDict(el['content'], ['text', 'imageUrl', 'imageCaption']):
                return False
            re.sub('(?:\r\n|\r|\n)', '', re.sub(
                '<[^>]*>', '', el['content']['text']))
            re.sub('(?:\r\n|\r|\n)', '', re.sub(
                '<[^>]*>', '', el['content']['imageCaption']))
            # validation image url data ...
        elif _elType == 'section':
            pass
        elif _elType == 'code':
            if not validateDict(el['content'], ['code', 'title']):
                return False
            re.sub('(?:\r\n|\r|\n)', '', re.sub(
                '<[^>]*>', '', el['content']['title']))
            el['content']['code'] = [
                re.sub('(?:\r\n|\r|\n)', '', codeStr) for codeStr in el['content']['code']]
        else:  # means invalid contentType.
            return False
        return True

    @classmethod
    def loadFromJson(cls, jsonDict, needMsg=False, article=None):
        _flag, _msg = Article.validateArticleJson(jsonDict)

        if not _flag:
            if needMsg:
                return (None, _msg)
            else:
                return None

        _retArticle = None
        if article:
            _retArticle = article
        else:
            _retArticle = cls()
            _retArticle.commentsCount = 0
            _retArticle.likesCount = 0

        _retArticle.headerImage = jsonDict['articleInfo']['headerImage']
        _retArticle.header = jsonDict['articleInfo']['header']
        _retArticle.secondHeader = jsonDict['articleInfo']['secondHeader']
        _retArticle.tags = jsonDict['articleInfo']['tags']

        _retArticle.content = jsonDict['sections']

        if needMsg:
            return (_retArticle, _msg)
        else:
            return _retArticle

    @classmethod
    def validateArticleJson(cls, jsonDict):

        # validate articleInfo

        if(not validateDict(jsonDict, ['articleFormatVersion', {'articleInfo': ['headerImage', 'header', 'secondHeader', 'tags']},
                                       {'sections': [
                                           {'contentElements': ['contentType', 'content']}]}
                                       ])):
            return (False, 'object missing parameter.')

        for sindex, section in enumerate(jsonDict['sections']):
            for eindex, el in enumerate(section['contentElements']):
                if not Article.validateContentElement(el):
                    return (False, 'ContentElement Error in secion: %s , ContentEle:%s . ' % (sindex, eindex))

        # validate contemtElements by contentType:

        return (True, '')

    def __init__(self, articleId=None, loadInfo=False, sqlInstance=None):
        self.isSearchingInDB = False  # is get data form dataabse
        self._articleData = None
        if sqlInstance is None:
            if articleId is not None:
                if loadInfo:
                    self._articleData = articles_table.query.options(load_only(
                        'id', 'author_id', 'header', 'secondHeader', 'headerImage', 'postDT', 'lastEditDT', 'tags', 'likesCount', 'isOpened', 'commentsCount')).filter_by(id=articleId).first()
                else:
                    self._articleData = articles_table.query.filter_by(
                        id=articleId).first()

            if self._articleData is None:  # none means articleId not exist in database or articleId is None
                self._articleData = articles_table()
            else:
                self.isSearchingInDB = True
        else:
            self.isSearchingInDB = True
            self._articleData = sqlInstance
        # if data exist then load
        self.isInfoOnly = loadInfo
        self._mappingParams()

    def _mappingParams(self):
        from .User import User

        self.id = self._articleData.id
        self.author_id = self._articleData.author_id
        self.header = self._articleData.header
        self.secondHeader = self._articleData.secondHeader
        self.headerImage = self._articleData.headerImage
        self.postDT = self._articleData.postDT
        self.tags = self._articleData.tags
        self.likesCount = self._articleData.likesCount
        self.commentsCount = self._articleData.commentsCount
        self.isOpened = self._articleData.isOpened
        self.lastEditDT = self._articleData.lastEditDT
        if self.isInfoOnly:
            self.content = None

        else:
            self.content = self._articleData.content

        self.rs_likes_query = self._articleData.rs_likes_dy
        self.rs_comments_query = self._articleData.rs_comment_dy
        self.author = User(sqlInstance=self._articleData.rs_author)

    def mappingDataToSqlInstance(self):
        if not self.isInfoOnly:
            self._articleData.content = self.content

        self._articleData.lastEditDT = self.lastEditDT
        self._articleData.author_id = self.author_id
        self._articleData.header = self.header
        self._articleData.secondHeader = self.secondHeader
        self._articleData.headerImage = self.headerImage
        self._articleData.tags = self.tags
        self._articleData.likesCount = self.likesCount
        self._articleData.commentsCount = self.commentsCount
        self._articleData.rs_author = self.author._userData
        self._articleData.isOpened = self.isOpened

    def commit(self):
        if not self._validateData():
            return (False, 'Data validate failed')

        _db = get_db()
        self.mappingDataToSqlInstance()
        if self.isSearchingInDB == False:
            _db.session.add(self._articleData)

        _db.session.commit()
        self._mappingParams()
        return (True, 'Successed')

    def searchUserLikeArticle(self, targetUser):
        return self.rs_likes_query.filter_by(user_id=targetUser.id).first()

    def setArticleLike(self, targetUser, likeFlag):
        _ret = {
            'type': 'articleLike',
            'currentStatus': None,
            'msg': 'Failed'
        }
        if not self.isSearchingInDB or not targetUser.isSearchingInDB:
            return _ret
        _lkRow = self.searchUserLikeArticle(targetUser)

        if likeFlag:
            if _lkRow is None:
                _like = post_likes_table(
                    post_id=self.id, user_id=targetUser.id)
                _db = get_db()
                _db.session.add(_like)
                self.likesCount += 1
                self.mappingDataToSqlInstance()
                _db.session.commit()

            _ret['currentStatus'] = True
            _ret['msg'] = 'Successed'
        else:
            if _lkRow is not None:
                _db = get_db()
                _db.session.delete(_lkRow)
                self.likesCount -= 1
                self.mappingDataToSqlInstance()
                _db.session.commit()

            _ret['currentStatus'] = False
            _ret['msg'] = 'Successed'

        return _ret

    def searchArticleComment(self, article, comment):
        pass

    def fetchComments(self, count):
        return self.rs_comments_query.order_by(self.rs_comments_query.commentDT.desc()).limit(count).all()

    def jsonify(self, reader=None):

        # _readerLike = False
        # _readerFollowing = False

        # if reader is not None:
        #     _readerLike = True if self.searchUserLikeArticle(reader) else False
        #     _readerFollowing = True if reader.searchFollow(
        #         self.author) else False
        _retInfo = self.author.getAuthorInfo(reader)
        _jsonArticle = {
            'articleFormatVersion': Article._articleFormatVersion,

            'articleInfo': {
                'headerImage': self.headerImage,
                'header': self.header,
                'secondHeader': self.secondHeader,
                'tags': self.tags,
                'postDateTime': {
                    'date': self.postDT.strftime("%Y-%m-%d"),
                    'time': self.postDT.strftime("%H:%M"),
                    'GMT': 8,
                },

            },


            'sections': self.content,

        }
        _jsonArticle['authorInfo'] = _retInfo['authorInfo']
        _jsonArticle['readerInfo'] = _retInfo['readerInfo']
        return _jsonArticle

    def deleteArticle(self, user):

        if not self.isSearchingInDB:
            return (False, 'Article not exist.')

        _db = get_db()
        _db.session.delete(self._articleData)
        # _deletecommits
        # _deletelikes....
        _db.session.commit()
        return (True, 'Successed')

    def _validateData(self):

        if not self.isInfoOnly:
            for section in self.content:
                for el in section['contentElements']:
                    if not Article.validateContentElement(el):
                        return False
        # if not validateDict(self.,['articleFormatVersion',{'articleInfo':['header','secondHeader','tags']}):

        #     return False
        return True
