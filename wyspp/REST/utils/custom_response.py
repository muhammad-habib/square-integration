import json

class CustomResponse():
    def __init__(self, success, data=None):
        self.success = success
        self.data = data

    def toJSON(self):
        return self.__dict__
