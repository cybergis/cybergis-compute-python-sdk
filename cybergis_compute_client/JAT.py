from base64 import b64decode, b64encode
from datetime import datetime
from json import dumps, loads
import hashlib


class JAT:
    """
    Job Access Token (JAT) class
    Attributes:
        accessTokenCache (dict): All cached access tokens with the date submitted as keys
        id (str): Unique identifier for the job assigned by the client
        secretToken (str): Token to generate JAT signature provided by the client
        algorithm (str): Algorithm used to hash the signature
    """
    def __init__(self):
        self.accessTokenCache = {}
        self.id = None
        self.secretToken = None
        self.algorithm = None

    def init(self, algorithm, id, secretToken):
        """
        Initializes instance data with data from the client
        Args:
            accessTokenCache (dict): All cached access tokens with the dates submitted as keys
            id (str): Unique identifier for the job (assigned by the client)
            secretToken (str): Token to generate JAT signature (provided by the client)
            algorithm (str): Algorithm used to hash the signature
        Returns:
            (obj): this JAT
        """
        if (algorithm not in hashlib.algorithms_available):
            raise Exception('encryption algorithm not supported by hashlib library')
        self.id = id
        self.secretToken = secretToken
        self.algorithm = algorithm
        return self

    def hash(self, payload):
        """
        Constructs a compact access token with the given payload
        Args:
            payload (str): payload to be hashed
        Returns:
            (str) hashed payload
        """
        self._checkInit()
        h = hashlib.new(self.algorithm)
        h.update(self.secretToken.encode('utf_8') + self.id.encode('utf_8') + payload.encode('utf_8'))
        return h.hexdigest()

    def getDate(self):
        """
        Returns the current date (year, month, day, hour)
        Args:
            none
        Returns:
            (str): The current date
        """
        return int(datetime.utcnow().strftime("%Y%m%d%H"))

    def getAccessToken(self):
        """
        Returns the access token signaure of this job, and adds it to the cache if it is not already there
        
        Returns:
            (str): Access token signature, in the form of 4 Base64-URL strings separated by dots
        """
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
        """
        Returns decoded information from the access token in the form of a dictionary
        Args:
            accessToken (str): The job's access token, in the form of 4 Base64-URL strings separated by dots
        Returns:
            (dict): Algorithm, payload (both encoded and decoded), id, and the hash associated with a job's secret token, id, and payload.
        """
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
        """
        Encodes a dictionary into a Base64-URL
        Args:
            target (dict): the dictionary to be encoded
        Returns:
            (str): the Base64-URL encoded target
        """
        return b64encode(dumps(target, separators=(',', ':')).encode('ascii')).decode('ascii')

    def _decodeDict(self, target):
        """
        Decodes a Base64_URL into a dictionary
        Args:
            target (str): Base64-URL to be decoded into a text dictionary
        Returns:
            (dict): Dictionary decoded from the passed target
        """
        return loads(b64decode(target.encode('ascii')).decode('ascii'))

    def _encodeString(self, target):
        """
        Encodes a string into a Base64_URL string
        Args:
            target (str): Text string to be encoded into a Base64-URL string
        Returns:
            (str): The Base64-URL encoded target
        """
        return b64encode(target.encode('ascii')).decode('ascii')

    def _decodeString(self, target):
        """
        Decodes a Base64_URL string
        Args:
            target (str): The Base64-URL encoded target
        Returns:
            (str): String decoded from the passed target
        """
        return b64decode(target.encode('ascii')).decode('ascii')

    def _checkInit(self):
        """
        Checks that the init function has succesfully assigned algorithm and secretToken to a non-None value
        Raises:
            Exception: If 'algorithm' or 'secretToken' is None
        """
        if (self.algorithm is None or self.secretToken is None):
            raise Exception("please init object before getting accessToken")

    def _clearCache(self):
        """
        Deletes every element in accessTokenCache
        """
        date = self.getDate()
        keys = list(self.accessTokenCache.keys())
        for i in keys:
            if (int(i) < date):
                del self.accessTokenCache[i]
