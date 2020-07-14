from .db import articles_table, get_db , post_likes_table , post_comments_table
from datetime import datetime
from sqlalchemy.orm import load_only
from .DictValidate import validateDict
import re


class Article():
    @classmethod
    def validateContentElement(cls,el):
        _elType = el['contentType']
        _retValidate = True
        if _elType in ('header','subTitle','text'):
            if not validateDict(el['content'],['text']):
                return False
            re.sub('(?:\r\n|\r|\n)','',re.sub('<[^>]*>','',el['content']['text']))
             
        elif _elType == 'video':
            if not validateDict(el['content'],['videoUrl']):
                return False
            if not re.search('https://www.youtube.com/embed/',el['content']['videoUrl']).span() == (0,30):
                return False
        elif _elType == 'image':
            if not validateDict(el['content'],['text','imageUrl','imageCaption']):
                return False
            re.sub('(?:\r\n|\r|\n)','',re.sub('<[^>]*>','',el['content']['text']))
            re.sub('(?:\r\n|\r|\n)','',re.sub('<[^>]*>','',el['content']['imageCaption']))
            #validation image url data ...
        elif _elType == 'section':
            pass
        else:#means invalid contentType.
            return False
        return True
    
    @classmethod
    def loadFromJson(cls,jsonDict,needMsg = False):
        _flag , _msg = Article.validateArticleJson(jsonDict)

        if not _flag:
            if needMsg:
                return (None,_msg)
            else:
                return None
                
        _retArticle = cls()
        _retArticle.header = jsonDict['articleInfo']['header']
        _retArticle.secondHeader = jsonDict['articleInfo']['secondHeader']
        _retArticle.tags = jsonDict['articleInfo']['tags']

        _retArticle.content = jsonDict['sections']
        _retArticle.commentsCount = 0
        _retArticle.likesCount = 0

        if needMsg:
            return (_retArticle,_msg)
        else:
            return _retArticle
    @classmethod
    def validateArticleJson(cls,jsonDict):

        #validate articleInfo

        if(not validateDict(jsonDict,['articleFormatVersion',{'articleInfo':['header','secondHeader','tags']},\
            {'sections':[{'contentElements':['contentType','content']}]}\
                ])):
            return (False,'object missing parameter.')
        
        for sindex,section in enumerate(jsonDict['sections']):
            for eindex,el in enumerate(section['contentElements']):
                if not Article.validateContentElement(el):
                    return (False,'ContentElement Error in secion: %s , ContentEle:%s . '%(sindex,eindex))
                    
        #validate contemtElements by contentType:
        
        return (True,'')
    def __init__(self, articleId=None, loadInfo=False, sqlInstance=None):
        self.isSearchingInDB = False  # is get data form dataabse
        self._articleData = None
        if sqlInstance is None:
            if articleId is not None:
                if loadInfo:
                    self._articleData = articles_table.query.options(load_only('id', 'author_id', 'header', 'secondHeader', 'headerImage', 'postDT', 'tags', 'likesCount', 'commentsCount')).filter_by(id=articleId).first()
                else:
                    self._articleData = articles_table.query.filter_by(id=articleId).first()

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
        
        if self.isInfoOnly:
            self.content = None
            self.lastEditDT = None
        else:
            self.content = self._articleData.content
            self.lastEditDT = self._articleData.lastEditDT

        self.rs_likes_query = self._articleData.rs_likes_dy
        self.rs_comments_query = self._articleData.rs_comment_dy
        self.author = User(sqlInstance=self._articleData.rs_author)
    def mappingDataToSqlInstance(self):
        if not self.isInfoOnly:
            self._articleData.content = self.content
            
        self._articleData.lastEditDT = datetime.now()
        self._articleData.author_id = self.author_id
        self._articleData.header = self.header
        self._articleData.secondHeader = self.secondHeader
        self._articleData.headerImage = self.headerImage
        self._articleData.tags = self.tags
        self._articleData.likesCount = self.likesCount
        self._articleData.commentsCount = self.commentsCount
        self._articleData.rs_author = self.author._userData

    def commit(self):
        if not self._validateData():
            return (False , 'Data validate failed')

        _db = get_db()
        self.mappingDataToSqlInstance()
        if self.isSearchingInDB == False:
            _db.session.add(self._articleData)

        _db.session.commit()
        return (True,'')
    def searchUserLikeArticle(self, targetUser):
        return self.rs_likes_query.filter_by(user_id = targetUser.id).first()


    def setArticleLike(self,targetUser,likeFlag):
        _ret = {
            'type':'articleLike',
            'currentStatus':None,
            'msg':'Failed'
        }
        if not self.isSearchingInDB or  not targetUser.isSearchingInDB:
            return _ret
        _lkRow = self.searchUserLikeArticle(targetUser)

        if likeFlag:
            if _lkRow is None:
                _like = post_likes_table(post_id = self.id,user_id = targetUser.id)
                _db = get_db()
                _db.session.add(_like)
                self.likesCount+=1
                self.mappingDataToSqlInstance()
                _db.session.commit()
            
            _ret['currentStatus'] = True
            _ret['msg'] = 'Successed'
        else:
            if _lkRow is not None:
                _db = get_db()
                _db.session.delete(_lkRow)
                self.likesCount-=1
                self.mappingDataToSqlInstance()
                _db.session.commit()

            _ret['currentStatus'] = False
            _ret['msg'] = 'Successed'

        return _ret
    def searchArticleComment(self,article,comment):
        pass

    def fetchComments(self, count):
        return self.rs_comments_query.order_by(self.rs_comments_query.commentDT.desc()).limit(count).all()

    def jsonify(self, reader=None):

        _readerLike = False

        if reader is not None:
            _readerLike = True if self.searchUserLikeArticle(reader) else False

        _jsonArticle = {
            'articleFormatVersion': "0.1.0",

            'articleInfo': {
                'header': self.header,
                'secondHeader': self.secondHeader,
                'tags': self.tags,
                'postDateTime': {
                    'date': self.postDT.strftime("%Y-%m-%d %H:%M"),
                    'time': self.postDT.strftime("%H:%M"),
                    'GMT': 8,
                },
            },

            'authorInfo': {
                'authorName': self.author.name,
                'authorPicture': self.author.userImage,
                'links': self.author.socialInfo,
            },
            'readerInfo': {
                'isFollowing': _readerLike,
                'isSaveArticle': False,
            },

            'sections': self.content,

        }

        return _jsonArticle
     
    
    def _validateData(self):

        if not self.isInfoOnly:
            for section in self.content:
                for el in section['contentElements']:
                    if not Article.validateContentElement(el):
                        return False
        # if not validateDict(self.,['articleFormatVersion',{'articleInfo':['header','secondHeader','tags']}):
              
        #     return False
        return True
    
