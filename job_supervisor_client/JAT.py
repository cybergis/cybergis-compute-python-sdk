from base64 import b64decode, b64encode
from datetime import datetime
from json import dumps, loads
import hashlib

class JAT:
    def __init__(self):
        self.accessTokenCache = {}
        self.secretToken = None
        self.algorithm = None

    def init(self, algorithm, secretToken):
        if (algorithm not in hashlib.algorithms_available):
            raise Exception('encryption algorithm not supported by hashlib library')
        self.secretToken = secretToken
        self.algorithm = algorithm
        return self

    def hash(self, payload):
        h = hashlib.new(self.algorithm)
        h.update(self.secretToken.encode('utf_8') + payload.encode('utf_8'))
        return h.hexdigest()

    def getDate(self):
        return int(datetime.utcnow().strftime("%Y%m%d%H"))

    def getAccessToken(self):
        self._checkInit()
        date = self.getDate()
        accessToken = None

        if (date not in self.accessTokenCache):
            payload = self._encodeDict({
                "date": date
            })
            alg = self._encodeString(self.algorithm)
            h = self.hash(payload)
            accessToken = alg + '.' + payload + '.' + h
            self.accessTokenCache[date] = accessToken
            self._clearCache()
        else:
            accessToken = self.accessTokenCache[date]

        return accessToken

    def parseAccessToken(self, accessToken):
        aT = accessToken.split('.')
        if (len(aT) != 3):
            raise Exception('invalid accessToken')

        return {
            "alg": self._decodeString(aT[0]),
            "payload": {
                "encoded": aT[1],
                "decoded": self._decodeDict(aT[1])
            },
            "hash": aT[2]
        }

    def _encodeDict(self, target):
        return b64encode(dumps(target, separators=(',', ':')).encode('ascii')).decode('ascii')

    def _decodeDict(self, target):
        return loads(b64decode(target.encode('ascii')).decode('ascii'))

    def _encodeString(self, target):
            return b64encode(target.encode('ascii')).decode('ascii')

    def _decodeString(self, target):
        return b64decode(target.encode('ascii')).decode('ascii')
        
    def _checkInit(self):
        if (self.algorithm == None or self.secretToken == None):
            raise Exception("please init object before getting accessToken")

    def _clearCache(self):
        date = self.getDate()
        keys = list(self.accessTokenCache.keys())
        for i in keys:
            if (int(i) < date):
                del self.accessTokenCache[i]
