from .Client import *
from .JAT import *
import time
from os import system, name
from tabulate import tabulate

class Job:
    def __init__(self, destination, user=None, password=None, id=None, url="cglogger.cigi.illinois.edu", port=3030):
        self.client = Client(url, port)
        self.destination = destination
        self.id = id
        self.url = url + ':' + str(port)
        self.JAT = JAT()
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

    def submit(self, env = {}, payload = {}):
        if self.id != None:
            raise Exception('cannot submit the same job twice')

        manifest = {
            "aT": self.JAT.getAccessToken(),
            "dest": self.destination,
            "env": env,
            "payload": payload
        }

        out = self.client.request('POST', '/supervisor', manifest)

        self.id = out['id']

        print('✅ job registered with ID: ' + str(out['id']))

        return self

    def download(self, dir):
        dir += '/' + self.id + '.zip'
        self.client.download('GET', '/supervisor/download/' + self.id, {
            "aT": self.JAT.getAccessToken()
        }, dir)

    def events(self, liveOutput=False):
        if liveOutput:
            events = []
            isEnd = False
            while (not isEnd):
                out = self.status()['events']
                startPos = len(events)
                headers = ['types', 'message', 'time']

                while (startPos < len(out)):
                    self._clear()
                    o = out[startPos]
                    i = [
                        o['type'],
                        o['message'],
                        o['at']
                    ]
                    events.append(i)
                    print('📮Job ID: ' + self.id)
                    print('📍Destination: ' + self.destination)
                    print('')
                    print(tabulate(events, headers, tablefmt="presto"))
                    startPos += 1

                endEventType = events[len(events)-1][0]
                if (endEventType == 'JOB_ENDED' or endEventType == 'JOB_FAILED'):
                    isEnd = True
                else:
                    time.sleep(1)
        else:
            return self.status()['events']

    def status(self):
        if self.id == None:
            raise Exception('missing job ID, submit/register job first')

        return self.client.request('GET', '/supervisor/' + str(self.id), {
            "aT": self.JAT.getAccessToken()
        })

    def _clear(self):
        # for windows 
        if name == 'nt': 
            _ = system('cls') 
        # for mac and linux(here, os.name is 'posix') 
        else:
            _ = system('clear') 
