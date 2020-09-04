from .Client import *
from .Job import *
from .JAT import *
import json
import os

class User:
    def __init__(self, destination, user=None, password=None, url="cgjobsup.cigi.illinois.edu", port=3000, isJupyter=False, useFileConstructor = False):
        self.destination = destination
        self.isJupyter = isJupyter

        if useFileConstructor:
            with open(os.path.abspath('job_supervisor_constructor_' + destination + '.json')) as f:
                constructor = json.load(f)
            url = constructor['url']
            port = constructor['port']
            sT = constructor['sT']
            self.client = Client(url, port)
        else:
            self.client = Client(url, port)
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

            sT = out['secretToken']

            with open('job_supervisor_constructor_' + destination + '.json', 'w') as json_file:
                json.dump({
                    "url": url,
                    "port": port,
                    "sT": sT
                }, json_file)

            print('📃 created constructor file [job_supervisor_constructor_' + destination + '.json]')
            print('👉 use [User("' + destination + '", useFileConstructor=True)] to create User interface from constructor file')

            if (password != None):
                print('')
                print('⚠️ delete password from your code/notebook')
                print('👉 use useFileConstructor option to create a safe User interface')

        self.url = url + ':' + str(port)
        self.sT = sT
        self.JAT = JAT()
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