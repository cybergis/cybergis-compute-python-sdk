from .Client import *
from .JAT import *
from .Zip import *
import time
import os
import json
from os import system, name
from tabulate import tabulate
from IPython.display import HTML, display, clear_output


class Job:
    """
    Job class

    Args:
        None

    Attributes:
        JAT (obj): Job Access Token associated with this job.
        client (obj): Client that this job requests information from
        maintainer (obj): Maintainer pool that this job is in
        isJupyter (bool): Whether or not this is running in Jupyter
        jupyterhubApiToken (str): API token needed to send requests using the JupyterHub API
        id (str): Id assigned to this job by the client
        hpc (str): HPC that this job will be submitted to
    """
    # static variables
    basicEventTypes = ['JOB_QUEUED', 'JOB_REGISTERED', 'JOB_INIT', 'GLOBUS_TRANSFER_INIT_SUCCESS', 'JOB_ENDED', 'JOB_FAILED']

    def __init__(self, maintainer=None, hpc=None, id=None, secretToken=None, hpcUsername=None, hpcPassword=None, client=None, isJupyter=None, jupyterhubApiToken=None, printJob=True):
        self.JAT = JAT()
        self.client = client
        self.maintainer = maintainer
        self.isJupyter = isJupyter
        self.jupyterhubApiToken = jupyterhubApiToken

        job = None
        if (secretToken is None):
            if maintainer is None:
                raise Exception('maintainer cannot by NoneType')

            req = {'maintainer': maintainer}
            if (hpc is not None):
                req['hpc'] = hpc
            if (jupyterhubApiToken is not None):
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
            job = self.client.request('GET', '/job/get-by-token', {'accessToken': self.JAT.getAccessToken()})
            hpc = job['hpc']

        if (hpcPassword is not None):
            print('⚠️ HPC password input detected, change your code to use .get_job_by_id() instead')
            print('🙅‍♂️ it\'s not safe to distribute code with login credentials')

        self.id = id
        self.hpc = hpc
        if printJob:
            self._print_job(job)

    def submit(self):
        """
        Submits this job to the client, and prints the output
        
        Returns:
            obj: This job
        """
        body = {'accessToken': self.JAT.getAccessToken()}
        if (self.jupyterhubApiToken is not None):
            body['jupyterhubApiToken'] = self.jupyterhubApiToken
        job = self.client.request('POST', '/job/' + self.id + '/submit', body)
        print('✅ job submitted')
        self._print_job(job)
        return self

    def upload_executable_folder(self, folder_path):
        """
        Uploads executable folder to client, sets the path of the executable folder, and displays the status of the job.
        
        Args:
            (str): Path of the executable folder
        
        Returns:
            dict: Results from the folder being uploaded to the client
        """
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
        """
        PUT requests information about this job to the client so it can be submitted to the hpc. Displays information about this job unless
        specified otherwise.
        
        Args:
            executableFolder (str): Path of the executable folder
            dataFolder (str): Path of the data folder
            resultFolder (str): Path of the result folder
            param (dict): Rules for input data
            env (dict): Enviorment variables required by the appliation
            slurm (dict): Slurm input rules
            printJob: If the status of the job should be printed
        """
        body = {'jupyterhubApiToken': self.jupyterhubApiToken}

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

        if (len(list(body)) == 1):
            print('❌ please set at least one parmeter')

        body['accessToken'] = self.JAT.getAccessToken()
        job = self.client.request('PUT', '/job/' + self.id, body)
        if printJob:
            self._print_job(job)

    def events(self, raw=False, liveOutput=True, basic=True, refreshRateInSeconds=10):
        """
        While the job is running, display the events generated by the client
        
        Args:
            raw (bool): If true, return a list of the events generated by status
            liveOutput (bool):
            basic (bool): If true, exclude non-basicEventType events
            RefreshRateInSeconds (int): Number of seconds to wait before refreshing status
        
        Todo:
            Modify function to include liveOutput or remove it from the arguments
        """
        if raw:
            return self.status(raw=True)['events']

        isEnd = False
        while (not isEnd):
            self._clear()
            status = self.status(raw=True)
            out = status['events']
            headers = ['types', 'message', 'time']
            events = []
            for o in out:
                if o['type'] not in self.basicEventTypes and basic:
                    continue

                i = [
                    o['type'],
                    o['message'],
                    o['createdAt']
                ]

                events.append(i)
                isEnd = isEnd or o['type'] == 'JOB_ENDED' or o['type'] == 'JOB_FAILED'

            print('📮 Job ID: ' + self.id)
            if 'slurmId' in status:
                print('🤖 Slurm ID: ' + str(status['slurmId']))
            if len(events) > 0:
                if self.isJupyter:
                    display(HTML(tabulate(events, headers, tablefmt='html')))
                else:
                    print(tabulate(events, headers, tablefmt='presto'))

            if not isEnd:
                time.sleep(refreshRateInSeconds)

    def logs(self, raw=False, liveOutput=True, refreshRateInSeconds=15):
        """
        While the job is running, display the logs generated by the client.
        
        Args:
            raw (bool): If true, return a list of the events generated by status
            liveOutput (bool):
            RefreshRateInSeconds (int): Number of seconds to wait before refreshing status
        
        Returns:
            list: List of logs generated by the client. Only returned if raw is true.
        
        Todo:
            Modify function to include liveOutput or remove it from the arguments
        """
        if raw:
            return self.status(raw=True)['logs']

        logs = []
        isEnd = False
        while (not isEnd):
            self._clear()
            status = self.status(raw=True)
            headers = ['message', 'time']
            logs = []

            for o in status['events']:
                isEnd = isEnd or o['type'] == 'JOB_ENDED' or o['type'] == 'JOB_FAILED'

            for o in status['logs']:
                i = [
                    o['message'],
                    o['createdAt']
                ]
                logs.append(i)

            print('📮 Job ID: ' + self.id)
            if 'slurmId' in status:
                print('🤖 Slurm ID: ' + str(status['slurmId']))
            if len(logs) > 0:
                if self.isJupyter:
                    display(HTML(tabulate(logs, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', "<td style='text-align:left'>")))
                else:
                    print(tabulate(logs, headers, tablefmt='presto'))

            if not isEnd:
                time.sleep(refreshRateInSeconds)

    def status(self, raw=False):
        """
        Displays the status of this job, and returns it if specified.
        
        Args:
            raw (bool): If information about this job should be returned
        
        Returns:
            dict: Infomation about this job returned by the client. This includes the job's 'id', 'hpc', 'executableFolder', 'dataFolder', 'resultFolder', 'param', 'slurm', 'userId', 'maintainer', 'createdAt', and 'events'
        
        Raises:
            Exception: If the 'id' attribute is None
        """
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')

        job = self.client.request('GET', '/job/' + self.id, {
            'accessToken': self.JAT.getAccessToken()
        })

        if raw:
            return job
        self._print_job(job)

    def result_folder_content(self):
        """
        Returns the results from the job
        
        Returns:
            dict: Results from running the job
        
        Throws:
            Exception: If the id is None
        """
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')
        out = self.client.request('GET', '/job/' + self.id + '/result-folder-content', {
            'accessToken': self.JAT.getAccessToken()
        })
        return out

    def download_result_folder(self, localPath=None, remotePath=None, raw=False):
        """
        Downloads the folder with results from the job using Globus
        
        Args:
            localPath (string): Path to the local result folder
            remotePath (string): Path to the remote result folder
            raw (bool): If the function should return the output from the client
        
        Returns:
            dict: Output from the client when downloading the results using globus. Only returned when raw is true.
        
        Raises:
            Exception: If the job ID is None
            Exception: If the key 'resultFolder' is not returned with status
            Exception: If the result folder is formatted improperly
        """
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')

        jobStatus = self.status(raw=True)
        if 'resultFolder' not in jobStatus:
            raise Exception('executable folder is not ready')

        i = jobStatus['resultFolder'].split('://')
        if (len(i) != 2):
            raise Exception('invalid result folder formate provided')

        fileType = i[0]
        fileId = i[1]

        if (fileType == 'globus'):
            status = None
            while status not in ['SUCCEEDED', 'FAILED']:
                self._clear()
                print('⏳ waiting for file to download using Globus')
                out = self.client.request('GET', '/file/result-folder/globus-download', {
                    "accessToken": self.JAT.getAccessToken(),
                    "downloadTo": jobStatus['resultFolder'],
                    "downloadFrom": remotePath
                })
                status = out['status']
                if raw:
                    return out
            # exit loop
            self._clear()
            if status == 'SUCCEEDED':
                print('✅ download success!')
            else:
                print('❌ download fail!')

        if (fileType == 'local'):
            localPath = os.path.join(localPath, fileId)
            localPath = self.client.download('/file/result-folder/direct-download', {
                "accessToken": self.JAT.getAccessToken()
            }, localPath)
            print('file successfully downloaded under: ' + localPath)
            return localPath

    def query_globus_task_status(self):
        """
        Get the status of the result download
        
        Returns:
            dict: Status of the result download
        
        Raises:
            Exception: If the job ID is None
        """
        if self.id is None:
            raise Exception('missing job ID, submit/register job first')
        return self.client.request('GET', '/file/' + self.id + '/globus_task_status', {
            'accessToken': self.JAT.getAccessToken()
        })

    # Integrated functions

    # HACK: back compatability
    def downloadResultFolder(self, dir=None):
        """
        Downloads the result folder and returns information about it
        
        Args:
            (dir): Location to download the files to
        
        Returns:
            dict: Output from the client when downloading the results using globus.
        """
        return self.download_result_folder(dir)

    # Helpers
    def _clear(self):
        """
        Clears output
        """
        if self.isJupyter:
            clear_output(wait=True)
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')

    def _print_job(self, job):
        """
        Displays information about this job
        
        Args:
            job (dict): Information about this job returned by the client
        """
        if job is None:
            return
        headers = ['id', 'slurmId', 'hpc', 'executableFolder', 'dataFolder', 'resultFolder', 'param', 'slurm', 'userId', 'maintainer', 'createdAt']
        data = [[
            job['id'],
            job['slurmId'],
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
