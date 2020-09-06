from enum import Enum

_baseResponseDict = {
    'msg': '',
    'type': '',
}


class Enum_ResponseMsg(Enum):
    # common
    Successed = 'Successed',
    RequestDataInvalid = 'Request data is invalid.'

    # Session enum
    SessionNotFound = 'Session not found.'
    SessionGetTokenFailed = 'Get token by session failed.'

    # Login enum
    NotLogin = 'Not login',
    LoginAccountOrPasswordIsIncorrect = 'Account or password is incorrect',

    # Sign Up enum
    RegisterDataIsInvalid = 'Register data is invalid'
    RegisterAccountAlreadyExists = 'The account already exists'
    RegisterPasswordIsInvalid = 'Register password is invalid'

    RegisterAccountWasFailed = 'Register account was failed.'

    # Articles enum
    ArticlesNotOwner = 'Not article\'s owner'
    ArticleHasInvalidString = 'Article has invalid string'
    ArticleFetchFailed = 'Fetch article failed.'
    ArticleIsPrivate = 'Article is private.'


class Enum_ResponseType(Enum):
    # user
    UserRegister = 'user_register'

    # session
    SessionLogout = 'session_log_out'
    SessionLogIn = 'session_log_in'
    SessionResend = 'session_resend'

    # article
    articlesSearch = 'article_search'
    articleFetch = 'article_fetch'


def getResponseBaseDict():
    return _baseResponseDict.copy()


def getResponseMsgString(msgEnum):
    # return "Error" only  when some flag is true
    return msgEnum.value
