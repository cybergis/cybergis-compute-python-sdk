from .Client import *
from .Job import *
from .JAT import *
import json
import os

class Session:
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

            if os.path.exists('./job_supervisor_constructor_' + destination + '.json'):
                raise Exception('⚠️ session constructor file [job_supervisor_constructor_' + destination + '.json] exists. Please delete it or use "useFileConstructor=True" to recreate session from it.')

            with open('./job_supervisor_constructor_' + destination + '.json', 'w') as json_file:
                json.dump({
                    "url": url,
                    "port": port,
                    "sT": sT
                }, json_file)

            print('📃 created session constructor file [job_supervisor_constructor_' + destination + '.json]')
            print('👉 use [Session("' + destination + '", useFileConstructor=True)] to create Session interface from constructor file')

            if (password != None):
                print('')
                print('⚠️ delete password from your code/notebook')
                print('👉 use useFileConstructor option to create a safe Session interface')

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

    def logs(self):
        return self.status()['logs']

    def status(self):
        return self.client.request('GET', '/supervisor', {
            "aT": self.JAT.getAccessToken()
        })

    def destinations(self):
        dest = self.client.request('GET', '/supervisor/destination', {})['destinations']
        headers = ['name', 'ip', 'port', 'isCommunityAccount', 'useUploadedFile', 'uploadedFileMustHave']
        data = []

        for i in dest.keys():
            d = dest[i]

            uploadedFileMustHave = 'not specified'
            if 'uploadFileConfig' in d:
                if 'mustHave' in d['uploadFileConfig']:
                    uploadedFileMustHave = d['uploadFileConfig']['mustHave']

            data.append([
                i,
                d['ip'],
                d['port'],
                d['isCommunityAccount'],
                d['useUploadedFile'],
                uploadedFileMustHave
            ])

        if self.isJupyter:
            display(HTML(tabulate(data, headers, numalign = 'left', stralign='left', colalign=('left','left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))