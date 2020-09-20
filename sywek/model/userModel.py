from ..User import User
from . import GCStorageModel
from ..base64DataSplit import base64DataSplit


def isAccountExists(_account):
    """
    Return false when _account not exists.
    Return true when _account is already exists.
    """
    return User.IsAccountExist(_account)


def verifyRegisterData(_account, _password, _name):
    """
    Return false when register data was invalid.
    Return true when retgister data was valid.
    """
    return User.verifyData(_account, _password, _name)


def createUser(_account, _password, _name, _socialMediaInfo, _userImage):
    """
    Return flag and userId
    retrun true,userId when create account successed
    return false,None when create account falied.
    """
    _newUser = User()

    if not _newUser.setPasswordHashAndSalt(_password):
        return False

    _newUser.account = _account
    _newUser.name = _name
    _newUser.socialInfo = _socialMediaInfo

    # upload image on GCS using GCStorageModel
    _bucketName = 'sywek_net_bucket'
    _flag, _dataDict = base64DataSplit(_userImage)
    # check split data successed
    if not _flag:
        return False

    _fileExtension = _dataDict['contentType'].split('/')[1]

    _blobname = 'image/user/{}.{}'.format(
        _name.replace(' ', '_'), _fileExtension)

    _uploadImageFlag, _retBlobName = GCStorageModel.uploadBlobFromBase64(
        _bucketName, _blobname, _dataDict['data'], _dataDict['contentType'], True, 2)

    if not _uploadImageFlag:
        return False

    _newUser.userImage = _retBlobName

    _flag, _msg = _newUser.commit()

    if not _flag:
        # if create user failed then delete the uploaded image
        GCStorageModel.deleteBlob(_bucketName, _retBlobName)
    return (_flag, _newUser.id)


def loginUser(*args):
    """
    parameters 1. :_account , _password,
    paraneters 2. :_userId,

    Return false when login failed , that means user not found or account,password not matched.
    Return true when login successed.

    return=> (flag , userInfo)
    """
    _user = None

    if len(args) == 1 and isinstance(*args, int):
        _user = User(*args, loadInfo=True)
        if _user is None:
            return(False, None)
    elif len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], str):
        _account, _password, *_ = args
    # Get user by account.
        _user = User.getUserByAccount(_account)
    else:
        raise Exception("parameter error")

    # Check _user not none (account exists) and password is match.
    # Check password rule : AddSalt(_password) equal _user.passwordHash
        if(_user is None or _user.validatePassword(_password) == False):
            return(False, None)

    return(True, {
        'id': _user.id,
        'name': _user.name,
        'userImage': _user.userImage
    })


def getUser(userId):
    """
    return true when user searching in sqlDB
    return false user not exists
    return type (flag , userInstance)
    """
    if userId is None:
        return (False, None)
    _user = User(userId, True)

    if _user is None:
        return (False, None)

    return (True, _user)


def setFollower(user, targetUserId, followStatus):
    """
    return true when set follower successed
    retrun false when set follower failed(Target user not exists)
    return format =>(flag , currnetStatus)
    """

    _targetUser = User(targetUserId, True)

    if _targetUser is None:
        return (False, None)

    _flag, _curStatus = user.setFollower(_targetUser, followStatus)
    return (_flag, _curStatus)


def getTargetUserInfo(user, targetUserId):
    """
    return True when get target user info successed.
    return False when get target user info failed (maybe target user not exists).
    return format => (flag , userInfoDict)
    userInfoDict:{
        'authorInfo' : {
            'authorId' : author id,
            'authorName' : author name,
            'authorPicture' : author image 
            'links' :author social media links
        },
        'readerInfo':{
            'isFollowing' : is user followed the (target) user

        }
    }
    """
    _targetUser = User(targetUserId, True)

    if _targetUser is None:
        return (False, None)

    return (True, _targetUser.getAuthorInfo(user))


def getUserProfile(user):
    """
        return Ture when successed
        return False when failed

        return format => (flag , userProfileict)
    userProfileict = {
        'id' : ,
        'name':,
        'socialInfo':,
        'userImage':
    }
    """
    if not user:
        return (False, None)

    _userProfileDict = {

    }
    _userProfileDict['id'] = user.id
    _userProfileDict['name'] = user.name
    _userProfileDict['socialInfo'] = user.socialInfo
    _userProfileDict['userImage'] = user.userImage

    return(True, _userProfileDict)


def updateUserProfile(user, userProfileData):
    """

    """

    if not user:
        return False

    # upload image
    # upload image on GCS using GCStorageModel
    _oldUserImage = user.userImage
    _bucketName = 'sywek_net_bucket'
    _flag, _dataDict = base64DataSplit(userProfileData["userImage"])
    # check split data successed
    if not _flag:
        return False

    _fileExtension = _dataDict['contentType'].split('/')[1]

    _blobname = 'image/user/{}.{}'.format(
        user.name.replace(' ', '_'), _fileExtension)

    _uploadImageFlag, _retBlobName = GCStorageModel.uploadBlobFromBase64(
        _bucketName, _blobname, _dataDict['data'], _dataDict['contentType'], True, 2)

    if not _uploadImageFlag:
        return False
    # udpate user and commit it
    user.socialInfo = userProfileData["socialInfo"]
    user.userImage = _retBlobName

    _flag, *_ = user.commit()

    if not _flag:
        # if update profile failed then delete new header image
        GCStorageModel.deleteBlob(_bucketName, _blobname)
        return False
    # delete old image when successed
    GCStorageModel.deleteBlob(_bucketName, _oldUserImage)
    return True
