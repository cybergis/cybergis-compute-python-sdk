from .Client import *
from .Job import *
import base64
import os
from IPython.display import Javascript
from IPython.display import display, Markdown
import ipywidgets as widgets

class CyberGISCompute:
    # static variable
    jupyterhubHost = None

    job = None

    def __init__(self, url="cgjobsup.cigi.illinois.edu", port=443, protocol='HTTPS', suffix="", isJupyter=True):
        self.client = Client(url=url, protocol=protocol, port=port, suffix=suffix)
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

    def create_job(self, maintainer='community_contribution', hpc=None, hpcUsername=None, hpcPassword=None, printJob=True):
        self.login()
        return Job(maintainer=maintainer, hpc=hpc, id=None, hpcUsername=hpcUsername, hpcPassword=hpcPassword, client=self.client, isJupyter=self.isJupyter, jupyterhubApiToken=self.jupyterhubApiToken, printJob=printJob)

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

    def get_statistic(self, raw=False):
        statistic = self.client.request('GET', '/statistic', { "jupyterhubApiToken": self.jupyterhubApiToken })
        if raw:
            return statistic

        headers = ['HPC Type', 'Total Runtime in Hours']
        data = []
        for key in statistic['runtime_in_seconds']:
            data.append([key, statistic['runtime_in_seconds'][key] / (60 * 60)])

        if self.isJupyter:
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_job(self, raw=False):
        self.login()
        if self.jupyterhubApiToken == None:
            print('❌ please login')

        jobs = self.client.request('GET', '/user/job', { "jupyterhubApiToken": self.jupyterhubApiToken })
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
                git[i]['commit'] if 'commit' in git[i] else 'NONE' ,
            ])

        if self.isJupyter:
            if len(data) == 0:
                print('empty')
                return
            display(HTML(tabulate(data, headers, numalign='left', stralign='left', colalign=('left', 'left'), tablefmt='html').replace('<td>', '<td style="text-align:left">').replace('<th>', '<th style="text-align:left">')))
        else:
            print(tabulate(data, headers, tablefmt="presto"))

    def list_maintainer(self, raw=False):
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
    def list_info(self, list_maintainer = False, list_container = False):
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

    def create_job_by_UI(self):
        if not self.isJupyter:
            print('❌ Enable Jupyter using .enable_jupyter() before you use the UI option')

        self.job = None

        style = {'description_width': '120px'}
        # main dropdown
        repo_opts = ['git://' + i for i in self.list_git(raw=True)]
        hpc_opts = [i for i in self.list_hpc(raw=True)]
        repo = widgets.Dropdown(options=repo_opts, value=repo_opts[0],description='📦 Git Repository:', style=style)
        hpc = widgets.Dropdown(options=hpc_opts, value=hpc_opts[0],description='🖥 HPC Endpoint:', style=style)
        display(repo, hpc)
        # slurm
        display(Markdown('#### Slurm Options:'), Markdown('Click checkboxs to enable option and overwrite default config value. All configs are optional. Please refer to [Slurm official documentation](https://slurm.schedmd.com/sbatch.html)'))
        show_slurm_button = widgets.Button(description="Show Slurm Options")
        hide_slurm_button = widgets.Button(description="Hide Slurm Options")
        slurm_output = widgets.Output()
        slurm_button_output = widgets.Output()

        with slurm_button_output:
            display(show_slurm_button)
        display(slurm_button_output, slurm_output)

        def on_click_hide_slurm_options(change):
            slurm_output.clear_output()
            with slurm_button_output:
                display(show_slurm_button)
        hide_slurm_button.on_click(on_click_hide_slurm_options)

        # general opts
        # partition
        partition_cbox = widgets.Checkbox(description='Partition*: ', value=False)
        partition = widgets.Text(value='')
        partition_hbox = widgets.HBox([partition_cbox, partition])
        # total gpu
        total_gpu_cbox = widgets.Checkbox(description='Total GPU per job: ', value=False)
        total_gpu = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        total_gpu_hbox = widgets.HBox([total_gpu_cbox, total_gpu])
        # task opts
        # num_of_task
        num_of_task_cbox = widgets.Checkbox(description='Number of tasks: ', value=False)
        num_of_task = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        num_of_task_hbox = widgets.HBox([num_of_task_cbox, num_of_task])
        # cpu_per_task
        cpu_per_task_cbox = widgets.Checkbox(description='Number of CPU per task: ', value=False)
        cpu_per_task = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        cpu_per_task_hbox = widgets.HBox([cpu_per_task_cbox, cpu_per_task])
        # gpu_per_task
        gpus_per_task_cbox = widgets.Checkbox(description='Number of GPU per task: ', value=False)
        gpus_per_task = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        gpus_per_task_hbox = widgets.HBox([gpus_per_task_cbox, gpus_per_task])
        # email to
        email_to = widgets.Text(value='example@illinois.edu', style=style)
        # email to opts
        email_to_fail = widgets.Checkbox(description='FAIL', value=False)
        email_to_end = widgets.Checkbox(description='END', value=False)
        email_to_begin = widgets.Checkbox(description='BEGIN', value=False)
        email_to_opt_hbox = widgets.HBox([widgets.Label('Email to '), email_to, widgets.Label('When job: ', style={'width': '100px'}), email_to_fail, email_to_end, email_to_begin], width="300px")

        def on_click_show_slurm_options(change):
            slurm_button_output.clear_output()
            with slurm_output:
                display(hide_slurm_button)
                display(Markdown('**General Slurm Options:**'))
                display(partition_hbox)
                display(total_gpu_hbox)
                display(Markdown('**Task Options:**'))
                display(num_of_task_hbox)
                display(cpu_per_task_hbox)
                display(gpus_per_task_hbox)
                display(Markdown('**Email Options:**'))
                display(email_to_opt_hbox)
        show_slurm_button.on_click(on_click_show_slurm_options)

        # globus
        globus_output = widgets.Output()

        display(Markdown('#### Globus File Upload/Download:'), globus_output)

        is_globus_jupyter = True
        globus_jupyter_upload_cbox = widgets.Checkbox(description='Upload from Jupyter working directory', value=False)
        globus_jupyter_upload_path = widgets.Text(value='', description='file path')
        globus_jupyter_upload_hbox = widgets.HBox([globus_jupyter_upload_cbox, globus_jupyter_upload_path])
        globus_jupyter_download_cbox = widgets.Checkbox(description='Download to Jupyter working directory', value=False)

        # Markdown('Upload data using Globus SFTP. [share your Globus folder](https://docs.globus.org/how-to/share-files/) with apadmana@illinois.edu before job submission')
        # upload
        globus_upload_cbox = widgets.Checkbox(description='Upload data from: ', value=False)
        globus_upload_endpoint = widgets.Text(value='', description='endpoint')
        globus_upload_path = widgets.Text(value='', description='file path')
        globus_upload_hbox = widgets.HBox([globus_upload_cbox, globus_upload_endpoint, globus_upload_path])

        # download
        globus_download_cbox = widgets.Checkbox(description='Download result to: ', value=False)
        globus_download_endpoint = widgets.Text(value='', description='endpoint')
        globus_download_path = widgets.Text(value='', description='file path')
        globus_download_hbox = widgets.HBox([globus_download_cbox, globus_download_endpoint, globus_download_path])

        use_custom_globus_button = widgets.Button(description="Custom Globus Settings")
        use_jupyter_globus_button = widgets.Button(description="Jupyter Globus Settings")
        use_custom_globus_button_hbox = widgets.HBox([widgets.Label('Want to use your own Globus endpoint?'), use_custom_globus_button])
        use_jupyter_globus_button_hbox = widgets.HBox([widgets.Label('Want to use Jupyter Globus endpoint?'), use_jupyter_globus_button])

        def on_click_use_custom_globus_button(change):
            is_globus_jupyter = False
            globus_output.clear_output()
            with globus_output:
                display(globus_upload_hbox, globus_download_hbox, use_jupyter_globus_button_hbox)
        use_custom_globus_button.on_click(on_click_use_custom_globus_button)

        def on_click_use_jupyter_globus_button(change):
            is_globus_jupyter = True
            globus_output.clear_output()
            with globus_output:
                display(globus_jupyter_upload_hbox, globus_jupyter_download_cbox, use_custom_globus_button_hbox)
        use_jupyter_globus_button.on_click(on_click_use_jupyter_globus_button)

        with globus_output:
            display(globus_jupyter_upload_hbox, globus_jupyter_download_cbox, use_custom_globus_button_hbox)

        # outputs
        submit_output = widgets.Output()
        init_output = widgets.Output()
        job_output = widgets.Output()
        event_output = widgets.Output()
        log_output = widgets.Output()
        download_output = widgets.Output()
        display(submit_output, init_output, job_output, event_output, log_output, download_output)

        # submit btn
        submit_button = widgets.Button(description="Submit Job")
        with submit_output:
            display(submit_button)

        def submit_on_click(change):
            if self.job != None:
                return

            submit_output.clear_output()

            d = {
                'repo': repo.value,
                'hpc': hpc.value,
                'partition': {
                    'partition': partition.value,
                    'is_partition': partition_cbox.value
                },
                'total_gpu': {
                    'total_gpu': total_gpu.value,
                    'is_total_gpu': total_gpu_cbox.value
                },
                'num_of_task': {
                    'num_of_task': num_of_task.value,
                    'is_num_of_task': num_of_task_cbox.value
                },
                'cpu_per_task': {
                    'cpu_per_task': cpu_per_task.value,
                    'is_cpu_per_task': cpu_per_task_cbox.value
                },
                'gpus_per_task': {
                    'gpus_per_task': gpus_per_task.value,
                    'is_gpus_per_task': gpus_per_task_cbox.value
                },
                'email_to': {
                    'email_to': email_to.value,
                    'fail': email_to_fail.value,
                    'end': email_to_end.value,
                    'begin': email_to_begin.value
                },
                'globus': {
                    'custom_download': {
                        'globus_download_endpoint': globus_download_endpoint.value,
                        'globus_download_path': globus_download_path.value,
                        'is_globus_download': globus_download_cbox.value
                    },
                    'custom_upload': {
                        'globus_upload_endpoint': globus_upload_endpoint.value,
                        'globus_upload_path': globus_upload_path.value,
                        'is_globus_upload': globus_upload_cbox.value
                    },
                    'jupyter_download': {
                        'is_globus_download': globus_jupyter_download_cbox.value
                    },
                    'jupyter_upload': {
                        'globus_upload_path': globus_jupyter_upload_path.value,
                        'is_globus_upload': globus_jupyter_upload_cbox.value
                    }
                }
            }

            is_globus_download = d['globus']['custom_download']['is_globus_download'] or d['globus']['jupyter_download']['is_globus_download']
            is_globus = d['globus']['custom_upload']['is_globus_upload'] or d['globus']['jupyter_upload']['is_globus_upload'] or is_globus_download

            with init_output:
                self.job = self.create_job(hpc=d['hpc'], printJob=False)
            self.job.set(executableFolder=d['repo'], printJob=False)

            # slurm
            slurm_settings = {}
            if d['partition']['is_partition']:
                slurm_settings['partition'] = d['partition']['partition']
            if d['total_gpu']['is_total_gpu']:
                slurm_settings['gpus'] = d['total_gpu']['total_gpu']
            if d['num_of_task']['is_num_of_task']:
                slurm_settings['num_of_task'] = d['num_of_task']['num_of_task']
            if d['cpu_per_task']['is_cpu_per_task']:
                slurm_settings['cpu_per_task'] = d['cpu_per_task']['cpu_per_task']
            if d['gpus_per_task']['is_gpus_per_task']:
                slurm_settings['gpus_per_task'] = d['gpus_per_task']['gpus_per_task']
            if d['email_to']['fail'] or d['email_to']['end'] or d['email_to']['begin']:
                slurm_settings['mail_user'] = [d['email_to']['email_to']]
                slurm_settings['mail_type'] = []
                if d['email_to']['fail']:
                    slurm_settings['mail_type'].append('FAIL')
                if d['email_to']['end']:
                    slurm_settings['mail_type'].append('END')
                if d['email_to']['begin']:
                    slurm_settings['mail_type'].append('BEGIN')

            if slurm_settings != {}:
                self.job.set(slurm=slurm_settings, printJob=False)

            if is_globus_jupyter and is_globus:
                jupyter_globus = self.get_user_jupyter_globus()

                if d['globus']['jupyter_download']['is_globus_download']:
                    filepath = 'globus_download_' + self.job.id
                    self.job.set(resultFolder='globus://' + jupyter_globus['endpoint'] + ':' + path.join(jupyter_globus['root_path'], filepath), printJob=False)

                if d['globus']['jupyter_upload']['is_globus_upload']:
                    filepath = d['globus']['upload']['globus_upload_path'].strip('/')
                    self.job.set(dataFolder='globus://' + jupyter_globus['endpoint'] + ':' + path.join(jupyter_globus['root_path'], filepath), printJob=False)

            else:
                if d['globus']['custom_download']['is_globus_download']:
                    self.job.set(resultFolder='globus://' + d['globus']['download']['globus_download_endpoint'] + ':' + d['globus']['download']['globus_download_path'], printJob=False)

                if d['globus']['custom_upload']['is_globus_upload']:
                    self.job.set(dataFolder='globus://' + d['globus']['upload']['globus_upload_endpoint'] + ':' + d['globus']['upload']['globus_upload_path'], printJob=False)

            with job_output:
                self.job.submit()
            with event_output:
                self.job.events()
            with log_output:
                self.job.logs()
            with download_output:
                if is_globus_download:
                    download_button = widgets.Button(description="Globus Download")
                    display(download_button)
                else:
                    download_dir = widgets.Text(value='./', description='Download to:')
                    download_button = widgets.Button(description="Local Download")
                    display(download_dir, download_button)

                def download_on_click(change):
                    if is_globus_download:
                        self.job.downloadResultFolder()
                        display(Markdown('your data is being downloaded using Globus in background, please wait patiently...'))
                    else:
                        self.job.downloadResultFolder(download_dir.value)
                download_button.on_click(download_on_click)
            print('⚠️ use .get_latest_created_job() to retrive job object')

        submit_button.on_click(submit_on_click)
        return

    def get_latest_created_job(self):
        return self.job

    # helper functions
    def enable_jupyter(self):
        self.isJupyter = True
        # get jupyter variable
        display(Javascript('IPython.notebook.kernel.execute(`CyberGISCompute.jupyterhubHost = "${window.location.host}"`);'))

    def get_user_jupyter_globus(self):
        return self.client.request('GET', '/user/jupyter-globus', { "jupyterhubApiToken": self.jupyterhubApiToken })

    def is_login(self):
        return self.jupyterhubApiToken != None