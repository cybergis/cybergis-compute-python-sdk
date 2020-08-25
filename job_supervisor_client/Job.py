from .Client import *
from .JAT import *
from .Zip import *
import time
import zipfile
import os
import mmap
from os import system, name
from tabulate import tabulate
from IPython.display import clear_output
from IPython.display import HTML, display

class Job:
    def __init__(self, user, jobID=None):
        self.client = user.client
        self.destination = user.destination
        self.id = jobID
        self.url = user.url
        self.JAT = user.JAT
        self.file = None
        self.isJupyter = user.isJupyter
        self.sT = user.sT

    def submit(self, env = {}, payload = {}):
        if self.id != None:
            raise Exception('cannot submit the same job twice')

        manifest = {
            "aT": self.JAT.getAccessToken(),
            "dest": self.destination,
            "env": env,
            "payload": payload
        }

        if (self.file != None):
            manifest['file'] = self.file

        out = self.client.request('POST', '/supervisor', manifest)

        self.id = out['id']

        print('✅ job registered with ID: ' + str(out['id']))

        return self

    def upload(self, model_dir):
        model_dir = '/' + model_dir.strip('/')

        if self.destination.lower() == "summa":
            for root, dirs, files in os.walk(model_dir):
                for f in files:
                    with open(os.path.join(root, f), 'rb') as i:
                        s = mmap.mmap(i.fileno(), 0, access=mmap.ACCESS_READ)
                        if s.find(model_dir.encode('utf-8')) != -1:
                            fin = open(os.path.join(root, f), "rt")
                            #read file contents to string
                            data = fin.read()
                            #replace all occurrences of the required string
                            data = data.replace(model_dir, '<BASEDIR>')
                            #close the input file
                            fin.close()
                            #open the input file in write mode
                            fin = open(os.path.join(root, f), "wt")
                            #overrite the input file with the resulting data
                            fin.write(data)
                            #close the file
                            fin.close()

        zip = Zip()
        for root, dirs, files in os.walk(model_dir):
            for d in dirs:
                p = os.path.join(root.replace(model_dir, self.destination.lower()), d)
                zip.mkdir(p)

            for f in files:
                with open(os.path.join(root, f), 'rb') as i:
                    p = os.path.join(root.replace(model_dir, self.destination.lower()), f)
                    zip.append(p, i.read())

        response = self.client.upload('/supervisor/upload', {
            "aT": self.JAT.getAccessToken()
        }, zip.read())

        self.file = response['file']
        return response

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
                    if self.isJupyter:
                        display(HTML(tabulate(events, headers, tablefmt='html')))
                    else:
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
        if self.isJupyter:
            clear_output(wait=True)
        # for windows 
        if name == 'nt': 
            _ = system('cls') 
        # for mac and linux(here, os.name is 'posix') 
        else:
            _ = system('clear') 
