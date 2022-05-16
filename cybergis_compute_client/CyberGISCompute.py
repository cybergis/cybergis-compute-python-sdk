"""
This module exposes CyberGISCompute class which creates a CyberGISCompute
object that serves as an entry point to the CyberGISX environment from a Python/Jupyter notebook.
All interactions with the High Performance Computing (HPC) backend are performed using this object.

Example:
        cybergis = CyberGISCompute(url='localhost', port='3030', protocol='HTTP', isJupyter=False)
"""

from .Client import *
from .Job import *
from .UI import *
import base64
import os
from IPython.display import display, Markdown, Javascript


class CyberGISCompute:
    """
    CyberGISCompute class
    An inteface that handles all interactions with the HPC backend
    Attributes:
        client (Client object)      : Initialized using url(str), protocol(str), port(str) and suffix(str)
        jupyterhubApiToken (string) : jupyterhub's REST API token that can be used to authenticate the user
        (https://jhubdocs.readthedocs.io/en/latest/jupyterhub/docs/source/rest.html)
        username (string)           : username
        isJupyter (boolean)         : set to True if you are working in a jupyter environment.
        If you are working in a simple Python environment then set to False
        ui (UI)                     : Serves as entry point to UI functionality
        job (Job)                   : Serves as entry point to access job interactions
        recentDownloadPath (str)    : Gets the most recent download path from globus
        jupyterhubHost (str)        : static variable that stores the path to jupyterhubHost
    """
    # static variable
    jupyterhubHost = None

    job = None

    def __init__(self, url="cgjobsup.cigi.illinois.edu", port=443, protocol='HTTPS', suffix="", isJupyter=True):
        """
        Initializes instance CyberGISCompute using inputs from the client
        Args:
            url (str)               : url that needs to be accessed
            port (str)              : port of the Jupyter or Python interface
            protocol (str)          : Typically HTTP or HTTPS
            suffix (str)            : specify version. For e.g v2
            isJupyter(booleans)     : set to True if you are using Jupyter environment
        Returns:
            (obj)                   : this CyberGISCompute
        """
        self.client = Client(url=url, protocol=protocol, port=port, suffix=suffix)
        self.jupyterhubApiToken = None
        self.username = None
        self.isJupyter = isJupyter
        self.ui = UI(self)
        if isJupyter:
            self.enable_jupyter()
        # job
        self.job = None
        self.recentDownloadPath = None

    def login(self, manualLogin=True):
        """
        Authenticates the client's jupyterhubApiToken and gives them access
        to CyberGISCompute features
        Args:
            manualLogin (boolean) : set to True if env variable and file login modes are not available
        Returns :
            None
        """
        if self.jupyterhubApiToken is not None:
            print('🎯 Logged in as ' + self.username)
            return

        # login via env variable
        envToken = os.getenv('JUPYTERHUB_API_TOKEN')
        if envToken is not None:
            print('💻 Found system token')
            try:
                token = base64.b64encode((self.jupyterhubHost + '@' + envToken).encode('ascii')).decode('utf-8')
                res = self.client.request('GET', '/user', {"jupyterhubApiToken": token})
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
                    res = self.client.request('GET', '/user', {"jupyterhubApiToken": token})
                    self.jupyterhubApiToken = token
                    self.username = res['username']
                    return self.login()
                except:
                    print('❌ Failed to login via token JSON file')
                print('NOTE: if you want to login as another user, please remove this file')
        elif manualLogin:
            if self.isJupyter:
                if (self.jupyterhubHost is not None):
                    import getpass
                    print('📢 Please go to Control Panel -> Token, request a new API token')
                    token = getpass.getpass('enter your API token here')
                    token = base64.b64encode((self.jupyterhubHost + '@' + token).encode('ascii')).decode('utf-8')
                    try:
                        res = self.client.request('GET', '/user', {"jupyterhubApiToken": token})
                        self.jupyterhubApiToken = token
                        self.username = res['username']
                        with open('./cybergis_compute_user.json', 'w') as json_file:
                            json.dump({"token": token}, json_file)
                        return self.login()
                    except:
                        print('❌ Failed to login via user input')
                else:
                    print('❌ You might not be working on a web browser or enabled JavaScript')
            else:
                print('❌ Enable Jupyter using .enable_jupyter() before you login')
        else:
            print('❌ Not logged in. To enable more features, use .login()')

    def create_job(self, maintainer='community_contribution', hpc=None, hpcUsername=None, hpcPassword=None, printJob=True):
        """
        Creates a job object
        Initializes instance CyberGISCompute using inputs from the client
        Args:
            maintainer (str)        : Pre-packaged programs which can be configured and controlled remotely
            and behave as a bridge between user and HPC backends
            hpc(str)                : HPC backend that is being accessed. For e.g 'keeling_community'
            hpcUsername (str)       : username for HPC backend
            hpcPassword (str)       : password for HPC backend
            printJob (str)          : prints the Job infortmation if set to True
        Returns:
            (Job) : The new job instance that was initialized
        """
        self.login()
        return Job(maintainer=maintainer, hpc=hpc, id=None, hpcUsername=hpcUsername, hpcPassword=hpcPassword, client=self.client, isJupyter=self.isJupyter, jupyterhubApiToken=self.jupyterhubApiToken, printJob=printJob)

    def get_job_by_id(self, id=None):
        """
        Returns Job object with the specified id
        Args:
            id(int)                 : Job id
        Returns
            (Job)                   : Job object with the specified id otherwise None
        """
        self.login()
        jobs = self.client.request('GET', '/user/job', {"jupyterhubApiToken": self.jupyterhubApiToken})
        token = None
        for job in jobs['job']:
            if (job['id'] == id):
                token = job['secretToken']
        if (token is None):
            print('❌ job with id ' + id + ' was not found')
        return Job(secretToken=token, client=self.client, id=id, isJupyter=self.isJupyter, jupyterhubApiToken=self.jupyterhubApiToken)

    def get_slurm_usage(self, raw=False):
        """
        prints slurm usage
        Args:
            raw(boolean)            : set to True if you want the raw output
        Returns
            (JSON)                  : Raw output if raw=True otherwise its printed or displayed directly into the interface
        """
        self.login()
        usage = self.client.request('GET', '/user/slurm-usage?format={}'.format(not raw), {"jupyterhubApiToken": self.jupyterhubApiToken})
        if raw:
            return usage
        display(Markdown("Nodes: {}<br>Allocated CPUs: {}<br>Total CPU Time: {}<br>Memory Utilized: {}<br>Total Allocated Memory: {}<br>Total Walltime: {}".format(
            usage['nodes'], usage['cpus'], usage['cpuTime'], usage['memory'], usage['memoryUsage'], usage['walltime'])))

    def list_job(self, raw=False):
        """
        prints a list of jobs that were submitted
        Args:
            raw (boolean)           : set to True if you want the raw output
        Returns
            (JSON)                  : Raw output if raw=True otherwise its printed or displayed into the interface
        """
        self.login()
        if self.jupyterhubApiToken is None:
            print('❌ please login')

        jobs = self.client.request('GET', '/user/job', {"jupyterhubApiToken": self.jupyterhubApiToken})
        if raw:
            return jobs

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

    def list_hpc(self, raw=False):
        """
        prints a list of hpc resources that the server supports
        Args:
            raw (boolean)           : set to True if you want the raw output
        Returns
            (JSON)                  : Raw output if raw=True otherwise its printed
            or displayed directly into the interface
        """
        hpc = self.client.request('GET', '/hpc')['hpc']
        if raw:
            return hpc

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

    def list_container(self, raw=False):
        """
        prints a list of containers that the server supports
        Args:
            raw (boolean)           : set to True if you want the raw output
        Returns
            (JSON)                  : Raw output if raw=True otherwise its printed
            or displayed directly into the interface
        """
        container = self.client.request('GET', '/container')['container']
        if raw:
            return container

        headers = ['container name', 'dockerfile', 'dockerhub']
        data = []

        for i in container:
            data.append([
                i,
                container[i]['dockerfile'],
                container[i]['dockerhub']
            ])

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_git(self, raw=False):
        """
        prints a list of Git projects that the server supports
        Args:
            raw (boolean)           : set to True if you want the raw output
        Returns
            (JSON)                  : Raw output if raw=True otherwise its printed
            or displayed directly into the interface
        """
        git = self.client.request('GET', '/git')['git']
        if raw:
            return git

        headers = ['link', 'name', 'container', 'repository', 'commit']
        data = []

        for i in git:
            data.append([
                'git://' + i,
                git[i]['name'],
                git[i]['container'],
                git[i]['repository'],
                git[i]['commit'] if 'commit' in git[i] else 'NONE',
            ])

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_maintainer(self, raw=False):
        """
        prints a list of maintainers that the server supports
        Args:
            raw (boolean)            : set to True if you want the raw output
        Returns
            (JSON)                  : Raw output if raw=True otherwise its printed
            or displayed directly into the interface
        """
        maintainers = self.client.request('GET', '/maintainer')['maintainer']
        if raw:
            return maintainers

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

    # Integrated functions
    def list_info(self, list_maintainer=False, list_container=False):
        """
        calls list_git, list_hpc, list_job with options to call list_maintainer and list_container
        Args:
            list_maintainer (boolean)    : set to True if you want to call list_maintainer
            list_container (boolean)     : set to True of you want to call list
        Returns
            None
        """
        print('📦 Git repositories:')
        self.list_git()
        print('🖥 HPC endpoints:')
        self.list_hpc()
        if self.is_login():
            print('📮 Submitted jobs:')
            self.list_job()

        if list_container:
            print('🗳 Containers:')
            self.list_container()

        if list_maintainer:
            print('🤖 Maintainers:')
            self.list_maintainer()

    def create_job_by_ui(self, defaultJob="hello_world", defaultDataFolder="./", defaultRemoteResultFolder=None):
        """
        Displays the job submission UI
        Args:
            defaultJob (str)                      : Stores the default job that shows up on the UI
            defaultDataFolder (str)               : Stores the default input folder that shows up on the UI
            defaultRemoteResultFolder (str)       : Stores the default output folder that shows up on the UI
        Returns:
            None
        """
        self.ui.defaultJobName = defaultJob
        self.ui.defaultDataFolder = defaultDataFolder
        if defaultRemoteResultFolder is not None:
            self.ui.defaultRemoteResultFolder = defaultRemoteResultFolder if defaultRemoteResultFolder[0] == '/' else '/' + defaultRemoteResultFolder
        self.ui.render()

    def get_latest_created_job(self):
        """
        Return the current job instance
        Args:
           None
        Returns:
            (JOB)                                 : Latest Job object instance
        """
        return self.job

    # helper functions
    def enable_jupyter(self):
        """
        sets up jupyter environment in jupyterhubHost
        Args:
           None
        Returns:
            None
        """
        self.isJupyter = True
        # get jupyter variable
        url = os.getenv('JUPYTER_INSTANCE_URL')
        if url is not None:
            CyberGISCompute.jupyterhubHost = url.replace('https://', '').replace('http://', '')
        else:
            display(Javascript('IPython.notebook.kernel.execute(`CyberGISCompute.jupyterhubHost = "${window.location.host}"`);'))

    def get_user_jupyter_globus(self):
        """
        Return the current job instance
        Args:
           None
        Returns:
            (JOB)                                 : Latest Job object instance
        """
        return self.client.request('GET', '/user/jupyter-globus', {"jupyterhubApiToken": self.jupyterhubApiToken})

    def is_login(self):
        """
        Checks whether jupyterhubApi token exists or not
        Args:
           None
        Returns:
            (boolean)                             : jupyterhubAPI existence check
        """
        return self.jupyterhubApiToken is not None
