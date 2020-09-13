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
    ArticlePostFalied = 'Article post failed.'
    ArticlesInfoFetchFailed = "Fetcg articles' info failed."

    ArticleEditFetchFailed = 'Article fetch failed (article not exists or not the owner).'
    ArticleEditDeleteFailed = 'Delete article failed (not article owner or other error).'
    ArticleEditUpdateFailed = 'Update article by article id failed (article not exists or not the article owner).'
    ArticleEditStatusUpdateFailed = 'Update article status failed (article not exists or not the article owner).'
    ArticleGetRecommandFalied = 'Get recommand articles\' failed.'


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
    articlePost = 'article_post'

    articlesInfoSelfFetch = 'articles_info_self_fetch'
    articleEditFetch = 'article_edit_fetch'
    articleEditDelete = 'article_edit_delete'
    articleEditUpdate = 'article_edit_update'
    articleEditStatusUpdate = 'article_edit_status_update'

    articlesGetRecommand = 'articles_get_recommand'


def getResponseBaseDict():
    return _baseResponseDict.copy()


def getResponseMsgString(msgEnum):
    # return "Error" only  when some flag is true
    return msgEnum.value
