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
