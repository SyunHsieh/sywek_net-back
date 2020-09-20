from ..GCStorage import GCStorage
from ..RandomString import RandomSelectString


def uploadBlobFromBase64(
        bucketname,
        blobname,
        base64Str,
        contentType,
        isAutoRename=True,
        renameMaxCount=1):
    """
    This function using to upload file on GCS(google cloud storage) ,
    and rename if parameter <isAutoRename> is true , and blobname was exists.

    return True when upload file successed 
    return False when upload file failed 
    return format => (flag , blobName)
    """

    _storage = GCStorage()
    _flag = _storage.setBucket(bucketname)
    _blobname = blobname

    if not _flag:
        return (False, None)

    _maxRenameCount = 1 if not isAutoRename else renameMaxCount+1
    for i in range(_maxRenameCount):
        _flag = _storage.uploadFromBase64(_blobname, contentType, base64Str)

        if _flag:
            return (True, _blobname)

        # run this code if not upload successed , try rename and upload until maxRenameCount

        _blobname = _blobname.replace('.', '_{}.'.format(
            RandomSelectString("1234567890abcdefghijklmnopqrstuvwxyz", 6)))

    return (False, None)


def copyBlob(bucketname, targetblob, destblob):
    """
    return True when delete blob successed
    return False when selete blob failed
    return format => flag
    """
    _storage = GCStorage()
    _flag = _storage.setBucket(bucketname)

    if not _flag:
        return False
    _flag = _storage.copyBlob(targetblob, destblob)
    return _flag


def renameBlob(bucketname, oldblobname, newblobname):
    """
    return True when delete blob successed
    return False when selete blob failed
    return format => flag
    """
    _storage = GCStorage()
    _flag = _storage.setBucket(bucketname)

    if not _flag:
        return False
    _flag = _storage.renameBlob(oldblobname, newblobname)
    return _flag


def deleteBlob(bucketname, blobname):
    """
    return True when delete blob successed
    return False when selete blob failed
    return format => flag
    """
    _storage = GCStorage()
    _flag = _storage.setBucket(bucketname)

    if not _flag:
        return False

    _flag = _storage.deleteBlob(blobname)

    return _flag


def isBlobExists(bucketname, blobname):
    """
    return true if blob exists
    return false if blob not exists
    """

    _storage = GCStorage()
    _flag = _storage.setBucket(bucketname)

    if not _flag:
        return False

    _flag = _storage.isBlobExists(blobname)
    return _flag


def downloadBlob(bucketname, blobname):
    """
    Return True when download blob successed
    return False when download blob dailed
    return format => (flag , blobDict)
    blobDict ={
        'blobname' :,
        'data':,
        'contentType:,
    }
    """
    _storage = GCStorage()
    _flag = _storage.setBucket(bucketname)

    if not _flag:
        return (False, None)
    _flag, _blobDict = _storage.downloadBlob(blobname)

    if not _flag:
        return(False, None)

    return (True, _blobDict)
