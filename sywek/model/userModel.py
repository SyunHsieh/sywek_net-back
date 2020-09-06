from ..User import User


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
    _newUser.userImage = _userImage

    _flag, _msg = _newUser.commit()

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
        'name': _user.name
    })
