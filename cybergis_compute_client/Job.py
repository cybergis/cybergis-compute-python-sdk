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
    def __init__(self, maintainer=None, hpc=None, id=None, user=None, password=None, client=None, isJupyter=None):
        self.JAT = JAT()
        self.client = client
        self.maintainer = maintainer
        self.isJupyter = isJupyter

        if id != None:
            if path.exists('./job_constructor_' + id + '.json'):
                with open(os.path.abspath('job_constructor_' + id + '.json')) as f:
                    constructor = json.load(f)
                id = constructor['id']
                sT = constructor['secretToken']
                hpc = constructor['hpc']
            else:
                raise Exception('jobID provided but constructor file [job_constructor_' + id + '.json] not found')
        else:
            if maintainer == None:
                raise Exception('maintainer cannot by NoneType')

            req = {
                'maintainer': maintainer
            }
            if (hpc != None):
                req['hpc'] = hpc

            if (user is None):
                out = self.client.request('POST', '/job', req)
            else:
                req['user'] = user
                req['password'] = password
                out = self.client.request('POST', '/job', req)

            hpc = out['hpc']
            sT = out['secretToken']
            id = out['id']
            with open('./job_constructor_' + id + '.json', 'w') as json_file:
                json.dump({ 'secretToken': sT, 'id': id, 'hpc': hpc }, json_file)
            print('📃 created constructor file [job_constructor_' + id + '.json]')

        if (password is not None):
            print('⚠️ password input detected, change your code to use Job(id='' + id + '') instead')
            print('🙅‍♂️ it\'s not safe to distribute code with login credentials')
            print('📃 share constructor file [job_constructor_' + id + '.json] instead')

        self.id = id
        self.hpc = hpc
        self.JAT.init('md5', id, sT)
        self.body = {
            'param': {},
            'env': {},
            'slurm': {},
            'executableFolder': None
        }

    def submit(self):
        self.client.request('PUT', '/job/' + self.id, self.getBodyForRequest())
        job = self.client.request('POST', '/job/' + self.id + '/submit', {
            'accessToken': self.JAT.getAccessToken()
        })
        print('✅ job submitted')
        return self

    def uploadExecutableFolder(self, folder_path):
        folder_path = os.path.abspath(folder_path)

        zip = Zip()
        for root, dirs, files in os.walk(folder_path, followlinks=True):
            for f in files:
                with open(os.path.join(root, f), 'rb') as i:
                    p = os.path.join(root.replace(folder_path, ''), f)
                    zip.append(p, i.read())

        response = self.client.upload('/file', {
            'accessToken': self.JAT.getAccessToken()
        }, zip.read())
        self.body['executableFolder'] = response['file']
        return response

    def set(self, executableFolder=None, param=None, env=None, slurm=None):
        if executableFolder:
            self.body['executableFolder'] = executableFolder
        if param:
            self.body['param'] = param
        if env:
            self.body['env'] = env
        if slurm:
            self.body['slurm'] = slurm
        print(self.body)

    def download(self, target_path):
        if self.id is not None:
            raise Exception('missing job ID, submit/register job first')

        target_path += '/' + self.id
        target_path = self.client.download('GET', '/job/' + self.id + '/download', {
            'accessToken': self.JAT.getAccessToken()
        }, target_path)
        print('file successfully downloaded under: ' + target_path)
        return target_path

    def events(self, liveOutput=False):
        if not liveOutput:
            return self.status()['events']

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
                    o['createdAt']
                ]
                events.append(i)
                isEnd =  o['type'] == 'JOB_ENDED' or o['type'] == 'JOB_FAILED'
                print('📮 Job ID: ' + self.id)
                print('💻 HPC: ' + self.hpc)
                print('🤖 Maintainer: ' + self.maintainer)
                if self.isJupyter:
                    display(HTML(tabulate(events, headers, tablefmt='html')))
                else:
                    print(tabulate(events, headers, tablefmt='presto'))
                startPos += 1

            if not isEnd:
                time.sleep(3)

    def logs(self, liveOutput=False):
        if not liveOutput:
            return self.status()['logs']

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
                    o['createdAt']
                ]
                logs.append(i)
                print('📮 Job ID: ' + self.id)
                print('💻 HPC: ' + self.hpc)
                print('🤖 Maintainer: ' + self.maintainer)
                if self.isJupyter:
                    display(HTML(tabulate(logs, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', "<td style='text-align:left'>")))
                else:
                    print(tabulate(logs, headers, tablefmt='presto'))
                startPos += 1

            i = 0
            while (i < len(status['events'])):
                eventType = status['events'][i]['type']
                isEnd = eventType == 'JOB_ENDED' or eventType == 'JOB_FAILED'
                if isEnd:
                    break
                i += 1

            if isEnd:
                time.sleep(3)

    def status(self):
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')

        return self.client.request('GET', '/job/' + self.id, {
            'accessToken': self.JAT.getAccessToken()
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

    def getBodyForRequest(self):
        body = {}
        body['accessToken'] = self.JAT.getAccessToken()
        for i in self.body:
            if self.body[i] != None:
                body[i] = self.body[i]
        return body