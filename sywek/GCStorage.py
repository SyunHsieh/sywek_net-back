from google.cloud import storage
from io import BytesIO, FileIO
import base64


class GCStorage():

    def __init__(self, storageKeyJson=None):

        _jsonKey = './sywek-net-web-key.json' if storageKeyJson is None else storageKeyJson
        self.storageClient = storage.Client.from_service_account_json(_jsonKey)

        if not self.storageClient:
            self = None

    def setBucket(self, bucketName):

        self.bucket = self.storageClient.get_bucket(bucketName)

        if self.bucket:
            return True
        else:
            return False

    def isBlobExists(self, blobName):
        _blob = self.bucket.blob(blobName)
        if _blob.exists():
            return True
        return False

    def deleteBlob(self, blobName):
        _blob = self.bucket.blob(blobName)
        if _blob.exists():
            _blob.delete()
            return True

        return False

    def uploadFromBase64(self, blobName, contentType, base64DataString):
        # create bytesIO
        try:

            _bytesIO = BytesIO()
            # check blob is not exists
            _blob = self.bucket.blob(blobName)
            if _blob.exists():
                # return false when blob was exists
                return False

            _b64dataBytes = base64.b64decode(base64DataString)

            # write base64Data in bytesIO
            _bytesIO.write(_b64dataBytes)
            _bytesIO.seek(0)

            _blob.content_type = contentType
            _blob.upload_from_file(_bytesIO)
            return True
        except Exception as e:
            return False

    def renameBlob(self, oldblobname, newblobname):
        try:
            _blob = self.bucket.blob(blobname)
            if not _blob.exists():
                return False
            _newblob = self.bucket.rename_blob(_blob, newblobname)
            if not _newblob:
                return False
            return True
        except Exception as e:
            return False

    def copyBlob(self, targetBlob, destBlob):
        try:
            _blob = self.bucket.blob(targetBlob)
            if not _blob.exists():
                return False

            _newblob = self.bucket.copy_blob(_blob, self.bucket, destBlob)
            if not _newblob:
                return False
            return True
        except Exception as e:
            return False

    def downloadBlob(self, blobname):
        """
        return (flag , dataDict)
        dataDict={
            'data' :'',
            'contentType':'',
            'blobname':blobName
        }
        """
        try:
            _blob = self.bucket.blob(blobname)
            if not _blob.exists():
                return (False, None)

            _data = _blob.download_as_bytes()
            _contentType = _blob.content_type

            if _data:
                return (True, {'data': BytesIO(_data), 'contentType': _contentType})
            else:
                return (False, None)
        except Exception as e:
            return (False, None)
