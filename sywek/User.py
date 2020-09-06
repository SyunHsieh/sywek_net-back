from .db import user_info_table, get_db, follows_table, articles_table
from datetime import datetime
import hashlib
from sqlalchemy.orm import load_only
import random
import re


class User():
    @classmethod
    def getUserByAccount(cls, account):
        _user = user_info_table.query.filter_by(account=account).first()

        if _user is None:
            return None
        else:
            return User(sqlInstance=_user)

    @classmethod
    def IsAccountExist(cls, account):
        if user_info_table.query.filter_by(account=account).first() is None:
            return False
        else:
            return True

    def __init__(self, userId=None, loadInfo=False, sqlInstance=None):
        self.isSearchingInDB = False  # is get data form dataabse
        self._userData = None

        if sqlInstance is None:  # not from instance then load data from sql_table.
            if userId is not None:
                if loadInfo:
                    self._userData = user_info_table.query.options(load_only(
                        'id', 'name', 'socialInfo', 'followersCount', 'userImage')).filter_by(id=userId).first()
                else:
                    self._userData = user_info_table.query.filter_by(
                        id=userId).first()

            if self._userData is None:  # none means userId not exist in database or userId is None
                self._userData = user_info_table()
            else:
                self.isSearchingInDB = True
        else:
            self.isSearchingInDB = True
            self._userData = sqlInstance
        # if data exist then load

        self.isInfoOnly = loadInfo
        self._mappingParams()

    def _mappingParams(self):

        self.id = self._userData.id
        self.name = self._userData.name
        self.userImage = self._userData.userImage
        self.socialInfo = self._userData.socialInfo
        self.followersCount = self._userData.followersCount

        if self.isInfoOnly:
            self.account = None
            self.passwordHash = None
            self.salt = None
            self.createDT = None
            self.verifyAccount = None
        else:
            self.account = self._userData.account
            self.passwordHash = self._userData.passwordHash
            self.salt = self._userData.salt
            self.createDT = self._userData.createDT
            self.verifyAccount = self._userData.verifyAccount
        self.rs_posts_query = self._userData.rs_posts_dy
        self.rs_likes_query = self._userData.rs_likes_dy
        self.rs_comments_query = self._userData.rs_comments_dy
        self.rs_follows_query = self._userData.rs_follows_dy

    def mappingDataToSqlInstance(self):
        if not self.isInfoOnly:
            self._userData.account = self.account
            self._userData.passwordHash = self.passwordHash
            self._userData.salt = self.salt
            self._userData.verifyAccount = self.verifyAccount

        self._userData.name = self.name
        self._userData.socialInfo = self.socialInfo
        self._userData.userImage = self.userImage
        self._userData.followersCount = self.followersCount

    def commit(self):
        if not self._validateData():
            return (False, 'Data validate failed')
        if User.IsAccountExist(self.account):
            return (False, 'Account is exist.')

        _db = get_db()
        self.mappingDataToSqlInstance()

        if self.isSearchingInDB == False:
            _db.session.add(self._userData)

        _db.session.commit()
        self._mappingParams()
        return (True, 'Successed')

    def setPasswordHashAndSalt(self, password):
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,32}', password):
            return False

        def _getSalt():
            sample_letters = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:ZXCVBNM<>?`1234567890-=qwertyuiop[]asdfghjkl;zxcvbnm,./'
            result_str = ''.join((random.choice(sample_letters)
                                  for i in range(32)))
            return result_str

        self.salt = _getSalt()
        sha512 = hashlib.sha512((password+self.salt).encode('utf-8'))
        self.passwordHash = sha512.hexdigest()
        return True

    def getArticlesInfo(self, count=1, offset=0):
        from .Article import Article
        if count <= 0:
            return None

        _articles = self.rs_posts_query.options(
            load_only('id', 'author_id', 'header', 'secondHeader', 'headerImage', 'postDT', 'tags', 'likesCount', 'commentsCount'))\
            .order_by(articles_table.postDT.desc()).limit(count).offset(offset).all()
        if _articles is not None:
            return [Article(loadInfo=True, sqlInstance=row) for row in _articles]
        else:
            return None

    def searchLike(self, article):
        return self.rs_likes_query.filter_by(post_id=article.id).first()

    def searchFollow(self, targetUser):
        return self.rs_follows_query.filter_by(followUser_id=targetUser.id).first()

    def validatePassword(self, password):
        return self.passwordHash == hashlib.sha512((password+self.salt).encode('utf-8')).hexdigest()

    def setFollower(self, targetFollower, followFlag):
        _ret = {
            'type': 'follower',
            'currentStatus': None,
            'msg': 'Failed'
        }
        if not self.isSearchingInDB or not targetFollower.isSearchingInDB:
            return _ret

        _db = get_db()
        _fwRow = self.searchFollow(targetFollower)
        if followFlag:
            if _fwRow is None:
                _follow = follows_table(
                    user_id=self.id, followUser_id=targetFollower.id)
                _db.session.add(_follow)
                targetFollower.followersCount += 1
                targetFollower.mappingDataToSqlInstance()
                _db.session.commit()

            _ret['currentStatus'] = True
            _ret['msg'] = 'Successed'
        else:
            if _fwRow is not None:
                _db.session.delete(_fwRow)
                targetFollower.followersCount -= 1
                targetFollower.mappingDataToSqlInstance()
                _db.session.commit()

            _ret['currentStatus'] = False
            _ret['msg'] = 'Successed'

        return _ret

    def _validateData(self):
        # account rules
        # password rules
        # salt rules
        # socialmedia rules
        # image rules
        # name rules
        # return flase or true
        if not self.isInfoOnly:
            if not re.fullmatch(r'^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$', self.account) or \
                    len(self.passwordHash) != 128 or len(self.salt) != 32:
                return False

        if not re.fullmatch(r'[a-z0-9A-Z ]{3,64}', self.name):
            return False

        return True

    @classmethod
    def verifyData(cls, account, password, name):
        if not re.fullmatch(r'^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z]+$', account):
            return False
        if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,32}', password):
            return False
        if not re.fullmatch(r'[a-z0-9A-Z ]{3,64}', name):
            return False
        return True
