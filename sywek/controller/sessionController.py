from ..model import userModel
from ..DictValidate import validateDict
from ..Response import getResponseBaseDict, getResponseMsgString, Enum_ResponseMsg, Enum_ResponseType


def sessionLogout(userId):
    """
    return tuple (flag , MsgDict)
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.SessionLogout.value

    # !!should add something like : 1. logout history and store in database.
    #
    #

    if(userId is None):
        _retDict['msg'] = Enum_ResponseMsg.NotLogin.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    return (True, _retDict)


def sessionLogin(loginData):
    """
    Return tuple (flag , msgDict , UserId)
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.SessionLogIn.value

    # verify login data
    if not validateDict(loginData, ['account', 'password']):
        _retDict['msg'] = Enum_ResponseMsg.RequestDataInvalid.value
        return (False, _retDict, None)

    # Login
    _flag, _userInfo = userModel.loginUser(
        loginData['account'], loginData['password'])
    if _flag == False:
        _retDict['msg'] = Enum_ResponseMsg.LoginAccountOrPasswordIsIncorrect.value
        return (False, _retDict, None)

    # !!Should add login-history and store in database.

    # Login successed
    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['token'] = {
        'name': _userInfo['name'],
        'userImage': _userInfo['userImage']
    }
    return (True, _retDict, _userInfo['id'])


def sessionGetToken(userId):
    """
    Return false when user not found or has no session
    Return True when user find by userId
    return =>(flag , msgDict)
    """
    _retDict = getResponseBaseDict()
    _retDict['type'] = Enum_ResponseType.SessionResend.value

    # check userId is not None , None means user request has no session.
    if userId is None:
        _retDict['msg'] = Enum_ResponseMsg.SessionNotFound.value
        return (False, _retDict)

    # get user info by userId
    _flag, _userInfo = userModel.loginUser(userId)

    if _flag == False:
        _retDict['msg'] = Enum_ResponseMsg.SessionGetTokenFailed.value
        return (False, _retDict)

    _retDict['msg'] = Enum_ResponseMsg.Successed.value
    _retDict['token'] = {
        'name': _userInfo['name'],
        'userImage': _userInfo['userImage']
    }
    return (True, _retDict)
