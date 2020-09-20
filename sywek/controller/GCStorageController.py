from ..model import GCStorageModel


def downloadBlob(bucketname, blobname):
    """
    return True when download blob successed
    return False when download blob failed
    return format => (flag , blobDict)

    blobDict ={
        'blobname' :,
        'data':,
        'contentType:,
    }
    """

    _flag, _blobDict = GCStorageModel.downloadBlob(bucketname, blobname)

    return (_flag, _blobDict)
