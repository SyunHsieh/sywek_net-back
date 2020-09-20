def base64DataSplit(base64DataWithInfo):
    """
        return (flag , dataDict)
        dataDict ={
            'contentType':,
            'data':base 64 data as string
        }
    """
    try:
        _tempDataList = base64DataWithInfo.split(',')
        _contentType = _tempDataList[0].split(';')[0].split(':')[1]
        _base64Data = _tempDataList[1]
        # _fileExtension = _contentType.split('/')[1]
        return (True, {
            'contentType': _contentType,
                'data': _base64Data
                })
    except Exception as e:
        return (False, None)
