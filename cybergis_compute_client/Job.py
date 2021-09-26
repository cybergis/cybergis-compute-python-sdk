from .Client import *
from .JAT import *
from .Zip import *
import time
import os
import mmap
import json
from os import system, name, path
from tabulate import tabulate
from IPython.display import HTML, display, clear_output


class Job:
    def __init__(self, maintainer=None, hpc=None, id=None, secretToken=None, hpcUsername=None, hpcPassword=None, client=None, isJupyter=None, jupyterhubApiToken=None, printJob=True):
        self.JAT = JAT()
        self.client = client
        self.maintainer = maintainer
        self.isJupyter = isJupyter
        self.jupyterhubApiToken = jupyterhubApiToken

        job = None
        if (secretToken == None):
            if maintainer == None:
                raise Exception('maintainer cannot by NoneType')

            req = { 'maintainer': maintainer }
            if (hpc != None):
                req['hpc'] = hpc
            if (jupyterhubApiToken != None):
                req['jupyterhubApiToken'] = jupyterhubApiToken

            if (hpcUsername is None):
                job = self.client.request('POST', '/job', req)
            else:
                req['user'] = hpcUsername
                req['password'] = hpcPassword
                job = self.client.request('POST', '/job', req)

            hpc = job['hpc']
            secretToken = job['secretToken']
            id = job['id']
            self.JAT.init('md5', id, secretToken)
        else:
            self.JAT.init('md5', id, secretToken)
            job = self.client.request('GET', '/job/get-by-token', { 'accessToken': self.JAT.getAccessToken() })
            hpc = job['hpc']

        if (hpcPassword is not None):
            print('⚠️ HPC password input detected, change your code to use .get_job_by_id() instead')
            print('🙅‍♂️ it\'s not safe to distribute code with login credentials')

        self.id = id
        self.hpc = hpc
        if printJob:
            self._print_job(job)

    def submit(self):
        try:
            body = { 'accessToken': self.JAT.getAccessToken() }
            if (self.jupyterhubApiToken != None):
                body['jupyterhubApiToken'] = self.jupyterhubApiToken
            job = self.client.request('POST', '/job/' + self.id + '/submit', body)
            print('✅ job submitted')
        except:
            print('❌ job already submitted or in queue')
            job = self.client.request('GET', '/job', { 'accessToken': self.JAT.getAccessToken() })

        self._print_job(job)
        return self

    def upload_executable_folder(self, folder_path):
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
        self.set(executableFolder=response['file'], printJob=True)
        return response

    def set(self, executableFolder=None, dataFolder=None, resultFolder=None, param=None, env=None, slurm=None, printJob=True):
        body = {}
        
        if executableFolder:
            body['executableFolder'] = executableFolder
        if dataFolder:
            body['dataFolder'] = dataFolder
        if resultFolder:
            body['resultFolder'] = resultFolder
        if param:
            body['param'] = param
        if env:
            body['env'] = env
        if slurm:
            body['slurm'] = slurm

        if (body == {}):
            print('❌ please set at least one parmeter')

        body['accessToken'] = self.JAT.getAccessToken()
        job = self.client.request('PUT', '/job/' + self.id, body)
        if printJob:
            self._print_job(job)

    def events(self, liveOutput=True, refreshRateInSeconds = 10):
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
                isEnd =  isEnd or o['type'] == 'JOB_ENDED' or o['type'] == 'JOB_FAILED'
                print('📮 Job ID: ' + self.id)
                print('🖥 HPC: ' + self.hpc)
                if self.isJupyter:
                    display(HTML(tabulate(events, headers, tablefmt='html')))
                else:
                    print(tabulate(events, headers, tablefmt='presto'))
                startPos += 1

            if not isEnd:
                time.sleep(refreshRateInSeconds)

    def logs(self, liveOutput=True, refreshRateInSeconds = 15):
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
                print('🖥 HPC: ' + self.hpc)
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
                time.sleep(refreshRateInSeconds)

    def status(self):
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')

        return self.client.request('GET', '/job/' + self.id, {
            'accessToken': self.JAT.getAccessToken()
        })

    def get_statistic(self, raw=False):
        statistic = self.client.request('GET', '/statistic/job/' + self.id, { 
            'jupyterhubApiToken': self.jupyterhubApiToken,
            'accessToken': self.JAT.getAccessToken()
        })
        if raw:
            return statistic

        headers = ['Job Runtime in Hours']
        data = [[
            statistic['runtime_in_seconds'] / (60 * 60) if statistic['runtime_in_seconds'] != None else 'job not finished'
        ]]

    def download_result_folder(self, dir=None):
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')

        jobStatus = self.status()

        if 'resultFolder' not in jobStatus:
            raise Exception('executable folder is not ready')

        i = jobStatus['resultFolder'].split('://')
        if (len(i) != 2):
            raise Exception('invalid result folder formate provided')

        fileType = i[0]
        fileId = i[1]

        if (fileType == 'globus'):
            return self.client.request('GET', '/file', {
                'accessToken': self.JAT.getAccessToken(),
                "fileUrl": jobStatus['resultFolder']
            })

        if (fileType == 'local'):
            dir = os.path.join(dir, fileId)
            dir = self.client.download('GET', '/file', {
                "accessToken": self.JAT.getAccessToken(),
                "fileUrl": jobStatus['resultFolder']
            }, dir)
            print('file successfully downloaded under: ' + dir)
            return dir

    def query_globus_task_status(self):
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')

        return self.client.request('GET', '/file/' + self.id + '/globus_task_status', {
            'accessToken': self.JAT.getAccessToken()
        })

    # Integrated functions

    # HACK: back compatability
    def downloadResultFolder(self, dir=None):
        return self.download_result_folder(dir)

    # Helpers
    def _clear(self):
        if self.isJupyter:
            clear_output(wait=True)
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')

    def _print_job(self, job):
        if job == None:
            return
        headers = ['id', 'hpc', 'executableFolder', 'dataFolder', 'resultFolder', 'param', 'slurm', 'userId', 'maintainer', 'createdAt']
        data = [[
            job['id'],
            job['hpc'],
            job['executableFolder'],
            job['dataFolder'],
            job['resultFolder'],
            json.dumps(job['param']),
            json.dumps(job['slurm']),
            job['userId'],
            job['maintainer'],
            job['createdAt'],
        ]]

        if self.isJupyter:
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))
