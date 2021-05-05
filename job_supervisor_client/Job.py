from .Client import *
from .JAT import *
from .Zip import *
import time
import os
import mmap
from os import system, name, path
from tabulate import tabulate
from IPython.display import HTML, display, clear_output


class Job:
    def __init__(self, hpc=None, maintainer=None, id=None, user=None, password=None, url="cgjobsup.cigi.illinois.edu", port=443, isJupyter=False, protocol='HTTPS'):
        self.protocol = protocol
        self.JAT = JAT()
        self.client = Client(url, port)
        self.url = url + ':' + str(port)
        self.hpc = hpc
        self.maintainer = maintainer
        self.file = None            

        if id != None:
            if path.exists('./job_constructor_' + id + '.json'):
                with open(os.path.abspath('job_constructor_' + id + '.json')) as f:
                    constructor = json.load(f)
                url = constructor['url']
                port = constructor['port']
                sT = constructor['sT']
            else:
                raise Exception('jobID provided but constructor file [job_constructor_' + id + '.json] not found')
        else:
            if maintainer == None:
                raise Exception('maintainer cannot by NoneType')

            if (user is None):
                out = self.client.request('POST', '/auth/job', {
                    'dest': maintainer if hpc == None else maintainer + '@' + hpc
                }, protocol=protocol)
            else:
                out = self.client.request('POST', '/auth/job', {
                    'dest': maintainer if hpc == None else maintainer + '@' + hpc,
                    'user': user,
                    'password': password
                }, protocol=protocol)

            sT = out['sT']
            id = out['id']
            with open('./job_constructor_' + id + '.json', 'w') as json_file:
                json.dump({
                    "url": url,
                    "port": port,
                    "sT": sT,
                    "id": id
                }, json_file)
            print('📃 created constructor file [job_constructor_' + id + '.json]')

        if (password is not None):
            print('')
            print('⚠️ password input detected, change your code to use Job(id="' + id + '") instead')
            print('🙅‍♂️ it\'s not safe to distribute code with login credentials')
            print('📃 share constructor file [job_constructor_' + id + '.json] instead')

        self.sT = sT
        self.id = id
        self.JAT.init('md5', self.sT)

    def submit(self, env={}, app={}):
        manifest = {
            "aT": self.JAT.getAccessToken(),
            "env": env,
            "app": app
        }

        if (self.file is not None):
            manifest['file'] = self.file

        self.client.request('POST', '/job', manifest, self.protocol)
        print('✅ job submitted')
        return self

    def upload(self, file_path):
        file_path = os.path.abspath(file_path)

        zip = Zip()
        for root, dirs, files in os.walk(file_path, followlinks=True):
            for f in files:
                with open(os.path.join(root, f), 'rb') as i:
                    p = os.path.join(root.replace(file_path, ''), f)
                    zip.append(p, i.read())

        response = self.client.upload('/job/upload', {
            "aT": self.JAT.getAccessToken()
        }, zip.read(), self.protocol)
        self.file = response['file']
        return response

    def download(self, target_path):
        if self.id is not None:
            raise Exception('missing job ID, submit/register job first')

        target_path += '/' + self.id
        target_path = self.client.download('GET', '/job/download', {
            "aT": self.JAT.getAccessToken()
        }, target_path, self.protocol)
        print('file successfully downloaded under: ' + target_path)
        return target_path

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
                    print('💻HPC: ' + self.hpc)
                    print('🤖Maintainer: ' + self.maintainer)
                    print('')
                    if self.isJupyter:
                        display(HTML(tabulate(events, headers, tablefmt='html')))
                    else:
                        print(tabulate(events, headers, tablefmt="presto"))
                    startPos += 1

                endEventType = events[len(events) - 1][0]
                if (endEventType == 'JOB_ENDED' or endEventType == 'JOB_FAILED'):
                    isEnd = True
                else:
                    time.sleep(1)
        else:
            return self.status()['events']

    def logs(self, liveOutput=False):
        if liveOutput:
            logs = []
            isEnd = False
            while (not isEnd):
                status = self.status()
                startPos = len(logs)
                headers = ['message', 'time']

                while (startPos < len(status['logs'])):
                    self._clear()
                    o = status['logs'][startPos]
                    i = [
                        o['message'],
                        o['at']
                    ]
                    logs.append(i)
                    print('📮Job ID: ' + self.id)
                    print('💻HPC: ' + self.hpc)
                    print('🤖Maintainer: ' + self.maintainer)
                    print('')
                    if self.isJupyter:
                        display(HTML(tabulate(logs, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
                    else:
                        print(tabulate(logs, headers, tablefmt="presto"))
                    startPos += 1

                endEventType = status['events'][len(status['events']) - 1]['type']
                if (endEventType == 'JOB_ENDED' or endEventType == 'JOB_FAILED'):
                    isEnd = True
                else:
                    time.sleep(1)
        else:
            return self.status()['logs']

    def status(self):
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')

        return self.client.request('GET', '/job/status', {
            "aT": self.JAT.getAccessToken()
        }, self.protocol)

    def _clear(self):
        if self.isJupyter:
            clear_output(wait=True)
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')
