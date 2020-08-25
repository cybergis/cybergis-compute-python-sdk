from .Client import *
from .Job import *
from .JAT import *

class User:
    def __init__(self, destination, user=None, password=None, url="cglogger.cigi.illinois.edu", port=3030, isJupyter=False):
        self.client = Client(url, port)
        self.destination = destination
        self.url = url + ':' + str(port)
        self.JAT = JAT()
        self.isJupyter = isJupyter
        if (user == None):
                out = self.client.request('POST', '/guard/secretToken', {
                'destination': destination
            })
        else:
            out = self.client.request('POST', '/guard/secretToken', {
                'destination': destination,
                'user': user,
                'password': password
            })
        self.sT = out['secretToken']
        self.JAT.init('md5', self.sT)

    def job(self, jobID=None):
        if jobID == None:
            return Job(self)
        else:
            return Job(self, jobID)

    def events(self):
        return self.status()['events']

    def status(self):
        return self.client.request('GET', '/supervisor', {
            "aT": self.JAT.getAccessToken()
        })