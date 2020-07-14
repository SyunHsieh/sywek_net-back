def validateDict(obj , keys):
            if type(obj) is not dict:
                return False
            for i in keys:
                if(type(i) is dict):
                    for key,values in i.items():
                        if(not obj.get(key)):
                            return False
                        if type(obj[key]) is list:
                            for j in obj.get(key):
                                if(not validateDict(j,values)):
                                    return False
                        else:
                            if(not validateDict(obj[key],values)):
                                return False

                else:
                    if not obj.get(i):
                        return False
            return True
        