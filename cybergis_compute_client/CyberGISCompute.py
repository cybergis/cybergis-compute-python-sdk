from .Client import *
from .Job import *
import base64
import os
from IPython.display import Javascript

class CyberGISCompute:
    # static variable
    jupyterhubHost = None

    def __init__(self, url="cgjobsup.cigi.illinois.edu", port=443, isJupyter=True, protocol='HTTPS'):
        self.client = Client(url, port, protocol)
        self.jupyterhubApiToken = None
        self.username = None
        self.isJupyter = isJupyter
        if isJupyter:
            self.enable_jupyter()

    def login(self, manualLogin = True):
        if self.jupyterhubApiToken != None:
            print('🎯 Logged in as ' + self.username)
            return

        # login via env variable
        envToken = os.getenv('JUPYTERHUB_API_TOKEN')
        if envToken != None:
            print('💻 Found system token')
            try:
                token = base64.b64encode((self.jupyterhubHost + '@' + envToken).encode('ascii')).decode('utf-8')
                res = self.client.request('GET', '/user', { "jupyterhubApiToken": token })
                self.jupyterhubApiToken = token
                self.username = res['username']
                return self.login()
            except:
                print('❌ Failed to login via system token')

        # login via file
        if path.exists('./cybergis_compute_user.json'):
            with open(os.path.abspath('cybergis_compute_user.json')) as f:
                user = json.load(f)
                token = user['token']
                print('📃 Found "cybergis_compute_user.json"')
                try:
                    res = self.client.request('GET', '/user', { "jupyterhubApiToken": token })
                    self.jupyterhubApiToken = token
                    self.username = res['username']
                    return self.login()
                except:
                    print('❌ Failed to login via token JSON file')
                print('NOTE: if you want to login as another user, please remove this file')
        elif manualLogin:
            if self.isJupyter:
                if (self.jupyterhubHost != None):
                    import getpass
                    print('📢 Please go to Control Panel -> Token, request a new API token')
                    token = getpass.getpass('enter your API token here')
                    token = base64.b64encode((self.jupyterhubHost + '@' + token).encode('ascii')).decode('utf-8')
                    try:
                        res = self.client.request('GET', '/user', { "jupyterhubApiToken": token })
                        self.jupyterhubApiToken = token
                        self.username = res['username']
                        with open('./cybergis_compute_user.json', 'w') as json_file:
                            json.dump({ "token": token }, json_file)
                        return self.login()
                    except:
                        print('❌ Failed to login via user input')
                else:
                    print('❌ You might not be working on a web browser or enabled JavaScript')
            else:
                print('❌ Enable Jupyter using .enable_jupyter() before you login')
        else:
            print('❌ Not logged in. To enable more features, use .login()')

    def create_job(self, maintainer='community_contribution', hpc=None, hpcUsername=None, hpcPassword=None):
        self.login()
        return Job(maintainer=maintainer, hpc=hpc, id=None, hpcUsername=hpcUsername, hpcPassword=hpcPassword, client=self.client, isJupyter=self.isJupyter, jupyterhubApiToken=self.jupyterhubApiToken)

    def get_job_by_id(self, id=None):
        self.login()
        jobs = self.client.request('GET', '/user/job', { "jupyterhubApiToken": self.jupyterhubApiToken })
        token = None
        for job in jobs['job']:
            if (job['id'] == id):
                token = job['secretToken']
        if (token == None):
            print('❌ job with id ' + id + ' was not found')
        return Job(secretToken=token, client=self.client, id=id, isJupyter=self.isJupyter, jupyterhubApiToken=self.jupyterhubApiToken)

    def list_job(self):
        self.login()
        if self.jupyterhubApiToken == None:
            print('❌ please login')

        jobs = self.client.request('GET', '/user/job', { "jupyterhubApiToken": self.jupyterhubApiToken })

        headers = ['id', 'hpc', 'executableFolder', 'dataFolder', 'resultFolder', 'param', 'slurm', 'userId', 'maintainer', 'createdAt']
        data = []
        for job in jobs['job']:
            data.append([
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
            ])

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_hpc(self):
        hpc = self.client.request('GET', '/hpc')['hpc']
        headers = ['hpc', 'ip', 'port', 'is_community_account']
        data = []

        for i in hpc:
            data.append([
                i,
                hpc[i]['ip'],
                hpc[i]['port'],
                hpc[i]['is_community_account']
            ])

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_container(self):
        hpc = self.client.request('GET', '/container')['container']
        headers = ['container name', 'dockerfile', 'dockerhub']
        data = []

        for i in hpc:
            data.append([
                i,
                hpc[i]['dockerfile'],
                hpc[i]['dockerhub']
            ])

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_git(self):
        git = self.client.request('GET', '/git')['git']
        headers = ['link', 'name', 'container', 'repository', 'commit']
        data = []

        for i in git:
            data.append([
                'git://' + i,
                git[i]['name'],
                git[i]['container'],
                git[i]['repository'],
                git[i]['commit'] if 'commit' in git[i] else 'NONE' ,
            ])

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_maintainer(self):
        maintainers = self.client.request('GET', '/maintainer')['maintainer']
        headers = ['maintainer', 'hpc', 'default_hpc', 'job_pool_capacity', 'executable_folder->from_user', 'executable_folder->must_have']
        data = []

        for i in maintainers:
            maintainer = maintainers[i]

            from_user = 'not specified'
            if 'executable_folder' in maintainer:
                from_user = maintainer['executable_folder']['from_user']

            must_have = 'not specified'
            if 'executable_folder' in maintainer:
                if 'file_config' in maintainer['executable_folder']:
                    if 'must_have' in maintainer['executable_folder']['file_config']:
                        must_have = maintainer['executable_folder']['file_config']['must_have']

            data.append([
                i,
                maintainer['hpc'],
                maintainer['default_hpc'],
                maintainer['job_pool_capacity'],
                from_user,
                must_have
            ])
        
        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))


    def enable_jupyter(self):
        self.isJupyter = True
        # get jupyter variable
        display(Javascript('IPython.notebook.kernel.execute(`CyberGISCompute.jupyterhubHost = "${window.location.host}"`);'))