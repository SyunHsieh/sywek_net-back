from ..model import userModel
from ..DictValidate import validateDict
from ..Response import getResponseBaseDict, getResponseMsgString, Enum_ResponseMsg, Enum_ResponseType


def createAccount(registerData):
    _retDict = getResponseBaseDict()

    _retDict['type'] = Enum_ResponseType.UserRegister.value

    # Verify register data.
    if not validateDict(registerData, ['account', 'name', {'socialInfo': ['facebook', 'github', 'instagram', 'twitter']}, 'password', 'userImage']) or \
            not userModel.verifyRegisterData(registerData['account'], registerData['password'], registerData['name']):
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict, None)

    #  Check register account is not exists.
    if userModel.isAccountExists(registerData['account']):
        _retDict['msg'] = Enum_ResponseMsg.RegisterAccountAlreadyExists.value
        return (False, _retDict, None)

    # Create account
    _flag, _userId = userModel.createUser(
        registerData['account'], registerData['password'], registerData['name'], registerData['socialInfo'], registerData['userImage'])

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.RegisterAccountWasFailed.value
        return (False, _retDict, None)

    # Successed
    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    return (True, _retDict, _userId)


def setFollower(userId, targetFollowerId, followStatus):
    """
    return True when set follower successed 
    retrun False when set follower failed

    return format =>(flag , retDict)
    retDict['targetFollowerId]= target id
    retDict['currentStatus'] = is followed? type of bool
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.UserSetFollower.value
    _targetFollowerId = 0
    # verify function parameters
    try:
        _targetFollowerId = int(targetFollowerId)
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (True, _retDict)
    _retDict['targetFollowerId'] = _targetFollowerId

    # check user exists and was login.
    if userId is None:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return(False, _retDict)
    _flag, _user = userModel.getUser(userId)
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        return (False, _retDict)

    # set follower
    _flag, _curStatus = userModel.setFollower(
        _user, _targetFollowerId, followStatus)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.UserSetFollowerFailed.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['currentStatus'] = _curStatus
    return (True, _retDict)


def getAuthorInfo(userId, targetAuthorId):
    """
    return true when get authorInfo successed 
    return false when get authorInfo failed 
    return format =>(flag , retDict)
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.UserGetAuthorInfo.value

    _targetAuthorId = 0
    # verify function parameters
    try:
        _targetAuthorId = int(targetAuthorId)
    except ValueError:
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    # get user
    _flag, _reader = userModel.getUser(userId)

    _flag, _userInfoDict = userModel.getTargetUserInfo(
        _reader, _targetAuthorId)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.UserGetAuthorInfoFailed.value
        return (False, _retDict)

    _retDict['userInfo'] = _userInfoDict
    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    return (True, _retDict)


def getUserProfile(userId):
    """
    retrun True when get user profile successed
    return Flase when get user profile failed


    return format =>(flag , retDict)
    retDict['userProfile']
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.UserProfileGet.value

    # check was login
    _flag, _user = userModel.getUser(userId)
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return (False, _retDict)

    # get Profile
    _flag, _userProfileDict = userModel.getUserProfile(_user)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.UserProfileGetFailed.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['userProfile'] = _userProfileDict
    return(True, _retDict)


def udpateUserProfile(userId, userProfileData):
    """
        return true when update user-profile successed
        return false when udpate user-profile failed

        return format =>(falg , retDict)
    """

    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.UserProfileUpdate.value
    _profileData = {

    }
    # verify function parmeters
    if not validateDict(userProfileData, ['userImage', {'socialInfo': ['facebook', 'github', 'instagram', 'twitter']}]):
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict)

    # check was login
    _flag, _user = userModel.getUser(userId)
    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return (False, _retDict)

    # update Profile
    _flag = userModel.updateUserProfile(
        _user, userProfileData)

    if not _flag:
        _retDict['msg'] = Enum_ResponseMsg.UserProfileUpdateFailed.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    return(True, _retDict)
