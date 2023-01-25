"""
This module exposes CyberGISCompute class which creates a CyberGISCompute
object that serves as an entry point to the CyberGISX environment from a Python/Jupyter notebook.
All interactions with the High Performance Computing (HPC) backend are performed using this object.

Example:
        cybergis = CyberGISCompute(url='localhost', port='3030', protocol='HTTP', isJupyter=False)
"""

from .Client import Client  # noqa
from .Job import Job  # noqa
from .UI import UI  # noqa
from .MarkdownTable import MarkdownTable  # noqa
import json
import base64
import os
import getpass
from IPython.display import display, Markdown, Javascript


class CyberGISCompute:
    """CyberGISCompute class
    An inteface that handles all interactions with the HPC backend

    Args:
        url (str): url that needs to be accessed
        port (str): port of the Jupyter or Python interface
        protocol (str): Typically HTTP or HTTPS
        suffix (str): specify version. For e.g v2
        isJupyter(bool): set to True if you are using Jupyter environment

    Attributes:
        client (Client object): Initialized using url(str), protocol(str), port(str) and suffix(str)
        jupyterhubApiToken (string): jupyterhub's REST API token that can be used to authenticate the user
        username (string): username
        isJupyter (bool): set to True if you are working in a jupyter environment else set it to False
        ui (UI): Serves as entry point to UI functionality
        job (Job): Serves as entry point to access job interactions
        recentDownloadPath (str): Gets the most recent download path from globus
        jupyterhubHost (str): static variable that stores the path to jupyterhubHost
    """
    # static variable
    jupyterhubHost = None

    job = None

    def __init__(self, url="cgjobsup.cigi.illinois.edu", port=443, protocol='HTTPS', suffix="", isJupyter=True):
        """
        Initializes instance CyberGISCompute using inputs from the client

        Args:
            url (str): url that needs to be accessed
            port (str): port of the Jupyter or Python interface
            protocol (str): Typically HTTP or HTTPS
            suffix (str): specify version. For e.g v2
            isJupyter(bool): set to True if you are using Jupyter environment

        Returns:
            CyberGISCompute: this CyberGISCompute
        """
        self.client = Client(url=url, protocol=protocol,
                             port=port, suffix=suffix)
        self.jupyterhubApiToken = None
        self.username = None
        self.isJupyter = isJupyter
        self.ui = UI(self)
        if isJupyter:
            self.enable_jupyter()
        # job
        self.job = None
        self.recentDownloadPath = None

    def encrypt_token(self, token):
        """
        Encrypts the token using host variable.

        Args:
            token (str): User/Environment provided token.
        """
        self.jupyterhubApiToken = base64.b64encode(
            (self.jupyterhubHost + '@' + token).encode('ascii')).decode('utf-8')

    def get_jupyterhubHost(self):
        """
        Gets the jupyterhub host(str) from the user.
        """
        if (self.jupyterhubHost is None):
            print(
                "Please copy the JupyterHub url along with port. E.g http://127.0.0.1:8081")
            self.jupyterhubHost = input('Enter your jupyterhubHost here: ')

    def set_username(self):
        """
        Authenticates the token(str) and saves the username(str).
        """
        res = self.client.request(
            'GET', '/user', {"jupyterhubApiToken": self.jupyterhubApiToken})
        self.username = res['username']

    def save_token(self):
        """
        Writes token(str) to json file.
        """
        with open('./cybergis_compute_user.json', 'w') as json_file:
            json.dump({"token": self.jupyterhubApiToken}, json_file)

    def login_token(self):
        """
        Saves username(str) and token(str).
        """
        try:
            self.set_username()
            self.save_token()
            return self.login()
        except:
            print('❌ Failed to login via system token')

    def host_token_login(self, token):
        """
        Gets the host(str), encrypts the token(str) and calls login.

        Args:
            token (str): User/Environment provided token.
        """
        self.get_jupyterhubHost()
        self.encrypt_token(token)
        return self.login_token()

    def login_manual(self):
        """
        Asks for token and host from user and calls login_token function.
        """
        if self.isJupyter:
            print('📢 Please go to Control Panel -> Token, request a new API token')
            token = getpass.getpass('Enter your API token here')
            try:
                return self.host_token_login(token)
            except:
                print('❌ Failed to login via user input')
        else:
            print('❌ Enable Jupyter using .enable_jupyter() before you login')

    def login_json(self):
        """
        Checks for json file and calls login_token function.
        """
        try:
            with open(os.path.abspath('cybergis_compute_user.json')) as f:
                user = json.load(f)
                token = user['token']
            print('📃 Found "cybergis_compute_user.json! NOTE: if you want to login as another user, please remove this file')
            self.jupyterhubApiToken = token
            self.set_username()
            self.save_token()
            return self.login()
        except:
            # print('❌ Failed to login via token JSON file, trying environment variable...')
            envToken = os.getenv('JUPYTERHUB_API_TOKEN')
            if envToken is not None:
                return self.host_token_login(envToken)

    def login(self, manualLogin=False, manualHost=None, verbose=True):
        """
        Authenticates the client's jupyterhubApiToken and gives them access
        to CyberGISCompute features

        Args:
            manualLogin (bool): set to True if env variable and  file login modes are not available

        Todo:
            Document exceptions/errors raised.
        """
        if manualHost is not None:
            self.jupyterhubHost = manualHost
        # login via env variable
        if self.jupyterhubApiToken is not None:
            if self.username is None:
                self.set_username()
            if verbose:
                print('🎯 Logged in as ' + self.username)
            return
        # manual login
        if manualLogin:
            return self.login_manual()
        # login via json file
        elif os.path.exists('./cybergis_compute_user.json'):
            return self.login_json()
        else:
            envToken = os.getenv('JUPYTERHUB_API_TOKEN')
            if envToken is not None:
                return self.host_token_login(envToken)
            print('❌ Not logged in. To enable more features, use .login()')

    def create_job(self, maintainer='community_contribution', hpc=None, hpcUsername=None, hpcPassword=None, verbose=True):
        """
        Creates a job object
        Initializes instance CyberGISCompute using inputs from the client

        Args:
            maintainer (str): Pre-packaged programs which can be configured and controlled remotely
            and behave as a bridge between user and HPC backends
            hpc(str): HPC backend that is being accessed. For e.g 'keeling_community'
            hpcUsername (str): username for HPC backend
            hpcPassword (str): password for HPC backend
            printJob (str): prints the Job infortmation if set to True

        Returns:
            Job: The new job instance that was initialized
        """
        self.login()
        return Job(maintainer=maintainer, hpc=hpc, id=None, hpcUsername=hpcUsername, hpcPassword=hpcPassword, client=self.client, isJupyter=self.isJupyter, jupyterhubApiToken=self.jupyterhubApiToken, printJob=verbose)

    def get_job_by_id(self, id=None, verbose=True):
        """
        Returns Job object with the specified id

        Args:
            id (int): Job id

        Returns:
            Job: Job object with the specified id otherwise None
        """
        self.login(verbose=False)
        return Job(client=self.client, id=id, isJupyter=self.isJupyter, jupyterhubApiToken=self.jupyterhubApiToken, printJob=verbose)

    def get_slurm_usage(self, raw=False):
        """
        Prints slurm usage

        Args:
            raw(bool): set to True if you want the raw output

        Returns:
            JSON: Raw output if raw=True otherwise its printed
            or displayed directly into the interface
        """
        self.login()
        usage = self.client.request('GET', '/user/slurm-usage?format={}'.format(
            not raw), {"jupyterhubApiToken": self.jupyterhubApiToken})
        if raw:
            return usage
        display(
            Markdown(
                "Nodes: {}<br>Allocated CPUs: {}<br>Total CPU Time: {}<br>Memory Utilized: {}<br>Total Allocated Memory: {}<br>Total Walltime: {}".format(usage['nodes'], usage['cpus'], usage['cpuTime'], usage['memory'], usage['memoryUsage'], usage['walltime'])))

    def list_job(self, raw=False):
        """
        Prints a list of jobs that were submitted

        Args:
            raw (bool): set to True if you want the raw output

        Returns:
            JSON: Raw output if raw=True otherwise its printed
            or displayed into the interface
        """
        self.login()
        if self.jupyterhubApiToken is None:
            print('❌ please login')

        jobs = self.client.request(
            'GET', '/user/job', {
                "jupyterhubApiToken": self.jupyterhubApiToken})
        if raw:
            return jobs

        headers = ['id', 'hpc', 'remoteExecutableFolder', 'remoteDataFolder',
                   'remoteResultFolder', 'param', 'slurm', 'userId', 'maintainer', 'createdAt']
        data = []
        for job in jobs['job']:
            to_append = [
                job['id'],
                job['hpc'],
                job['remoteExecutableFolder']["id"] if (
                    job['remoteExecutableFolder'] is not None and "id" in job['remoteExecutableFolder']) else None,
                job['remoteDataFolder']["id"] if (
                    job['remoteDataFolder'] is not None and "id" in job['remoteDataFolder']) else None,
                job['remoteResultFolder']["id"] if (
                    job['remoteResultFolder'] is not None and "id" in job['remoteResultFolder']) else None,
                json.dumps(job['param']),
                json.dumps(job['slurm']),
                job['userId'],
                job['maintainer'],
                job['createdAt']
            ]
            data.append(to_append)

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(Markdown(MarkdownTable.render(data, headers)))
        else:
            print(MarkdownTable.render(data, headers))

    def list_hpc(self, raw=False):
        """
        Prints a list of hpc resources that the server supports

        Args:
            raw (bool): set to True if you want the raw output

        Returns:
            JSON: Raw output if raw=True otherwise its printed
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
            display(Markdown(MarkdownTable.render(data, headers)))
        else:
            print(MarkdownTable.render(data, headers))

    def list_container(self, raw=False):
        """
        Prints a list of containers that the server supports

        Args:
            raw (bool): set to True if you want the raw output

        Returns:
            JSON: Raw output if raw=True otherwise its
            printed or displayed directly into the interface
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
            display(Markdown(MarkdownTable.render(data, headers)))
        else:
            print(MarkdownTable.render(data, headers))

    def list_jupyter_host(self, raw=False):
        """
        Prints a list of jupyter hosts that the server supports

        Args:
            raw (bool): set to True if you want the raw output

        Returns:
            JSON: Raw output if raw=True otherwise its
            printed or displayed directly into the interface
        """
        try:
            hosts = self.client.request('GET', '/whitelist')['whitelist']
            if raw:
                return hosts

            headers = ['jupyter_host', 'description']
            data = []

            for i in hosts:
                data.append([
                    i,
                    hosts[i],
                ])

            if self.isJupyter:
                if len(data) == 0:
                    print('empty')
                    return
                display(Markdown(MarkdownTable.render(data, headers)))
            else:
                print(MarkdownTable.render(data, headers))
        except:
            print("The server " + self.client.url + " doesn't have this route")

    def list_git(self, raw=False):
        """
        Prints a list of Git projects that the server supports

        Args:
            raw (bool): set to True if you want the raw output

        Returns:
            JSON: Raw output if raw=True otherwise its
            printed or displayed directly into the interface
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
            display(Markdown(MarkdownTable.render(data, headers)))
        else:
            print(MarkdownTable.render(data, headers))

    def list_maintainer(self, raw=False):
        """
        prints a list of maintainers that the server supports

        Args:
            raw (bool): set to True if you want the raw output

        Returns:
            JSON: Raw output if raw=True otherwise its printed
            or displayed directly into the interface
        """
        maintainers = self.client.request('GET', '/maintainer')['maintainer']
        if raw:
            return maintainers

        headers = [
            'maintainer', 'hpc', 'default_hpc',
            'job_pool_capacity', 'executable_folder->from_user',
            'executable_folder->must_have']
        data = []

        for i in maintainers:
            maintainer = maintainers[i]

            from_user = 'not specified'
            if 'executable_folder' in maintainer:
                from_user = maintainer['executable_folder']['from_user']

            must_have = 'not specified'
            if 'executable_folder' in maintainer:
                if 'file_config' in maintainer['executable_folder']:
                    if 'must_have' in maintainer[
                        'executable_folder'][
                            'file_config']:
                        must_have = maintainer[
                            'executable_folder'][
                                'file_config'][
                                    'must_have']

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
            display(Markdown(MarkdownTable.render(data, headers)))
        else:
            print(MarkdownTable.render(data, headers))

    # Integrated functions
    def list_info(self, list_maintainer=False, list_container=False):
        """
        Calls :meth:`cybergis_compute_client.CyberGISCompute.CyberGISCompute.list_git`, :meth:`cybergis_compute_client.CyberGISCompute.CyberGISCompute.list_hpc`, :meth:`cybergis_compute_client.CyberGISCompute.CyberGISCompute.list_job` with options to call
        :meth:`cybergis_compute_client.CyberGISCompute.CyberGISCompute.list_maintainer` and :meth:`cybergis_compute_client.CyberGISCompute.CyberGISCompute.list_container`.

        Args:
            list_maintainer (bool): set to True if you want to
                call list_maintainer
            list_container (bool): set to True of you want to
                call list
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

    def create_job_by_ui(
        self,
            input_params=None,
            defaultJob="hello_world",
            defaultDataFolder="./",
            defaultRemoteResultFolder=None):
        """
        Displays the job submission UI.

        Args:
            defaultJob (str): Stores the default job that shows up on the UI
            defaultDataFolder (str): Stores the default input folder that shows up on the UI
            defaultRemoteResultFolder (str): Stores the default output folder that shows up on the UI
        """
        self.show_ui(input_params, defaultJob, defaultDataFolder, defaultRemoteResultFolder)

    def show_ui(self, input_params=None, defaultJob="hello_world", defaultDataFolder="./", defaultRemoteResultFolder=None, jupyterhubApiToken=None):
        """
        Displays the job submission UI

        Args:
            defaultJob (str): Stores the default job that shows up on the UI
            defaultDataFolder (str): Stores the default input folder that shows up on the UI
            defaultRemoteResultFolder (str): Stores the default output folder that shows up on the UI

        Returns:
            None
        """
        if (jupyterhubApiToken is not None):
            self.jupyterhubApiToken = jupyterhubApiToken
        self.ui.defaultJobName = defaultJob
        self.ui.defaultDataFolder = defaultDataFolder
        df = defaultRemoteResultFolder
        self.ui.input_params = input_params
        if df is not None:
            self.ui.defaultRemoteResultFolder = df if df[0] == '/' else '/' + df
        self.ui.render()

    def get_latest_created_job(self):
        """
        Return the current job instance

        Returns:
            Job: Latest Job object instance
        """
        return self.job

    # helper functions
    def enable_jupyter(self):
        """
        Sets up jupyter environment in jupyterhubHost
        """
        self.isJupyter = True
        # get jupyter variable
        url = os.getenv('JUPYTER_INSTANCE_URL')
        if url is not None:
            CyberGISCompute.jupyterhubHost = url.replace(
                'https://', '').replace(
                    'http://', '')
        else:
            display(Javascript(
                'IPython.notebook.kernel.execute(''`CyberGISCompute.jupyterhubHost = "${window.location.host}"`);'))

    def get_user_jupyter_globus(self):
        """
        Return the current job instance

        Returns:
             Job: Latest Job object instance
        """
        return self.client.request(
            'GET', '/user/jupyter-globus', {
                "jupyterhubApiToken": self.jupyterhubApiToken})

    def is_login(self):
        """
        Checks whether jupyterhubApi token exists or not

        Returns:
            bool: jupyterhubAPI existence check
        """
        return self.jupyterhubApiToken is not None
