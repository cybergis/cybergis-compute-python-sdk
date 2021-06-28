from base64 import b64decode, b64encode
from datetime import datetime
from json import dumps, loads
import hashlib


class JAT:
    def __init__(self):
        self.accessTokenCache = {}
        self.id = None
        self.secretToken = None
        self.algorithm = None

    def init(self, algorithm, id, secretToken):
        if (algorithm not in hashlib.algorithms_available):
            raise Exception('encryption algorithm not supported by hashlib library')
        self.id = id
        self.secretToken = secretToken
        self.algorithm = algorithm
        return self

    def hash(self, payload):
        self._checkInit()
        h = hashlib.new(self.algorithm)
        h.update(self.secretToken.encode('utf_8') + self.id.encode('utf_8') + payload.encode('utf_8'))
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
            id = self._encodeString(self.id)
            accessToken = alg + '.' + payload + '.' + id + '.' + h
            self.accessTokenCache[date] = accessToken
            self._clearCache()
        else:
            accessToken = self.accessTokenCache[date]

        return accessToken

    def parseAccessToken(self, accessToken):
        aT = accessToken.split('.')
        if (len(aT) != 4):
            raise Exception('invalid accessToken')

        return {
            "alg": self._decodeString(aT[0]),
            "payload": {
                "encoded": aT[1],
                "decoded": self._decodeDict(aT[1])
            },
            "id": self._decodeString(aT[2]),
            "hash": aT[3]
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
        if (self.algorithm is None or self.secretToken is None):
            raise Exception("please init object before getting accessToken")

    def _clearCache(self):
        date = self.getDate()
        keys = list(self.accessTokenCache.keys())
        for i in keys:
            if (int(i) < date):
                del self.accessTokenCache[i]
