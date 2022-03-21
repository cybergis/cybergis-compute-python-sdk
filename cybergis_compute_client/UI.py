import os
import math
import ipywidgets as widgets
from ipyfilechooser import FileChooser
from IPython.display import Markdown, display, clear_output

class UI:
    def __init__(self, compute, defaultJobName="hello_world", defaultDataFolder="./", defaultRemoteResultFolder=None):
        self.compute = compute
        self.style = {'description_width': 'auto'}
        self.layout = widgets.Layout(width='60%')
        self.jobs = None
        self.hpcs = None
        self.defaultJobName = defaultJobName
        if defaultRemoteResultFolder != None:
            self.defaultRemoteResultFolder = defaultRemoteResultFolder if defaultRemoteResultFolder[0] == '/' else '/' + defaultRemoteResultFolder
        self.defaultDataFolder = defaultDataFolder
        # slurm configs
        self.slurm_configs = ['num_of_node', 'num_of_task', 'time', 'cpu_per_task', 'memory_per_cpu', 'memory_per_gpu', 'memory', 'gpus', 'gpus_per_node', 'gpus_per_socket', 'gpus_per_task', 'partition']
        self.slurm_integer_configs = ['num_of_node', 'num_of_task', 'time', 'cpu_per_task', 'memory_per_cpu', 'memory_per_gpu', 'memory', 'gpus', 'gpus_per_node', 'gpus_per_socket', 'gpus_per_task']
        self.slurm_integer_storage_unit_config = ['memory_per_cpu', 'memory_per_gpu', 'memory']
        self.slurm_integer_time_unit_config = ['time']
        self.slurm_integer_none_unit_config = ['cpu_per_task', 'num_of_node', 'num_of_task', 'gpus', 'gpus_per_node', 'gpus_per_socket', 'gpus_per_task']
        self.slurm_string_option_configs = ['partition']
        self.globus_filename = None
        self.jupyter_globus = None

    def render(self):
        self.init()
        self.renderCompoenets()
        divider = Markdown('***')
        # render main UI
        # 1. job template
        job_config = widgets.Output()
        with job_config:
            display(Markdown('# Welcome to CyberGIS-Compute'))
            display(Markdown('Some description about CyberGIS-Compute'))
            display(divider)
            display(self.jobTemplate['output'])
            display(self.description['output'])
            display(self.computingResource['output'])
            display(self.slurm['output'])
            display(self.param['output'])
            display(self.uploadData['output'])
            display(self.email['output'])
            display(self.submit['output'])
        
        # 2. job status
        job_status = widgets.Output()
        with job_status:
            display(self.resultStatus['output'])
            display(divider)
            display(Markdown('## 📋 job events (live refresh)'))
            display(self.resultEvents['output'])
            display(divider)
            display(Markdown('## 📋 job logs'))
            display(self.resultLogs['output'])

        # 3. download
        download = widgets.Output()
        with download:
            display(self.download['output'])

        # assemble into tabs
        self.tab = widgets.Tab(children=[
            job_config,
            job_status,
            download
        ])
        self.tab.set_title(0, 'Job Configuration')
        self.tab.set_title(1, 'Your Job Status')
        self.tab.set_title(2, 'Download Job Result')
        display(self.tab)

    def renderCompoenets(self):
        self.renderJobTemplate()
        self.renderDescription()
        self.renderComputingResource()
        self.renderSlurm()
        self.renderEmail()
        self.renderSubmit()
        self.renderParam()
        self.renderUploadData()
        self.renderResultStatus()
        self.renderResultEvents()
        self.renderResultLogs()
        self.renderDownload()

    # components
    def renderJobTemplate(self):
        if self.jobTemplate['output'] == None:
            self.jobTemplate['output'] = widgets.Output()
        # create components
        self.jobTemplate['dropdown'] = widgets.Dropdown(options=[i for i in self.jobs], value=self.jobName, description='📦 Job Templates:', style=self.style, layout=self.layout)
        self.jobTemplate['dropdown'].observe(self.onJobDropdownChange())
        with self.jobTemplate['output']:
            display(self.jobTemplate['dropdown'])

    def renderDescription(self):
        if self.description['output'] == None:
                self.description['output'] = widgets.Output()
        self.description['job_description'] = Markdown('**' + self.jobName + ' Job Description:** ' + self.job['description'])
        self.description['computing_resource_description'] = Markdown('**' + self.hpcName + ' HPC Description**: ' + self.hpc['description'])
        self.description['estimated_runtime'] = Markdown('**Estimated Runtime:** ' + self.job['estimated_runtime'])
        with self.description['output']:
            display(self.description['job_description'], self.description['computing_resource_description'], self.description['estimated_runtime'])

    def renderComputingResource(self):
        if self.computingResource['output'] == None:
            self.computingResource['output'] = widgets.Output()
        # create components
        self.computingResource['dropdown'] = widgets.Dropdown(options=[i for i in self.job['supported_hpc']], value=self.hpcName, description='🖥 Computing Recourse:', style=self.style, layout=self.layout)
        self.computingResource['accordion'] = widgets.Accordion(children=( self.computingResource['dropdown'], ), selected_index=None)
        self.computingResource['accordion'].set_title(0, 'Computing Resource')
        self.computingResource['dropdown'].observe(self.onComputingResourceDropdownChange())
        with self.computingResource['output']:
            display(self.computingResource['accordion'])

    def renderEmail(self):
        if self.email['output'] == None:
            self.email['output'] = widgets.Output()
        # create components
        self.email['checkbox'] = widgets.Checkbox(description='receive email on job status? ', value=False, style=self.style)
        self.email['text'] = widgets.Text(value='example@illinois.edu', style=self.style)
        self.email['hbox'] = widgets.HBox([self.email['checkbox'], self.email['text']])
        with self.email['output']:
            display(self.email['hbox'])

    def renderSlurm(self):
        if self.slurm['output'] == None:
            self.slurm['output'] = widgets.Output()
        # check if necessary to render
        if self.job['slurm_input_rules'] == {}:
            return
        # create components
        self.slurm['description'] = widgets.Label(value='All configs are optional. Please refer to Slurm official documentation at 🔗 https://slurm.schedmd.com/sbatch.html')
        # settings
        for i in self.slurm_configs:
            if i not in self.job['slurm_input_rules']:
                self.slurm[i] = None
                continue

            config = self.job['slurm_input_rules'][i]

            if i in self.slurm_integer_configs:
                default_val = config['default_value']
                max_val = config['max']
                min_val = config['min']
                step_val = config['step']
                unit = config['unit']
                description = i + ' (' + unit + ')' if unit != 'None' else i
                self.slurm[i] = widgets.IntSlider(
                    value=default_val,
                    min=min_val,
                    max=max_val,
                    step=step_val,
                    disabled=False,
                    continuous_update=False,
                    orientation='horizontal',
                    readout=True,
                    readout_format='d',
                    description=description,
                    style=self.style, layout=self.layout
                )

            if i in self.slurm_string_option_configs:
                default_val = config['default_value']
                options = config['options']
                self.slurm[i] = widgets.Dropdown(
                    options=options,
                    value=default_val,
                    description=i,
                    style=self.style
                )

        w = []
        for i in self.slurm_configs:
            if self.slurm[i] != None:
                w.append(self.slurm[i])
        self.slurm['vbox'] = widgets.VBox(w)

        # settings end
        self.slurm['accordion'] = widgets.Accordion(children=( widgets.VBox(children=(self.slurm['description'], self.slurm['vbox'])), ), selected_index=None)
        self.slurm['accordion'].set_title(0, 'Slurm Computing Configurations')
        with self.slurm['output']:
            display(self.slurm['accordion'])

    def renderUploadData(self):
        if self.uploadData['output'] == None:
            self.uploadData['output'] = widgets.Output()
        # check if necessary to render
        if not self.job['require_upload_data']: return
        # render all
        self.uploadData['selector'] = FileChooser(self.defaultDataFolder, select_default=True if self.defaultDataFolder != './' else False)
        self.uploadData['selector'].show_only_dirs = True
        self.uploadData['selector'].title = 'Job requires upload data. Please select a folder to upload'
        # settings end
        self.uploadData['accordion'] = widgets.Accordion(children=( self.uploadData['selector'], ), selected_index=None)
        self.uploadData['accordion'].set_title(0, 'Upload Data')
        with self.uploadData['output']:
            display(self.uploadData['accordion'])

    def renderParam(self):
        if self.param['output'] == None:
            self.param['output'] = widgets.Output()
        # check if necessary to render
        if self.job['param_rules'] == {}:
            return
        # clear config
        for i in self.param:
            if i != 'output':
                self.param[i] = None

        # render param
        for i in self.job['param_rules']:
            config = self.job['param_rules'][i]

            if config['type'] == 'integer':
                default_val = config['default_value']
                max_val = config['max']
                min_val = config['min']
                step_val = config['step']
                description = i
                self.param[i] = widgets.IntSlider(
                    value=default_val,
                    min=min_val,
                    max=max_val,
                    step=step_val,
                    disabled=False,
                    continuous_update=False,
                    orientation='horizontal',
                    readout=True,
                    readout_format='d',
                    description=description,
                    style=self.style, layout=self.layout
                )

            if config['type'] == 'string_option':
                default_val = config['default_value']
                options = config['options']
                self.param[i] = widgets.Dropdown(
                    options=options,
                    value=default_val,
                    description=i,
                    style=self.style
                )

            if config['type'] == 'string_input':
                default_val = config['default_value']
                self.param[i] = widgets.Text(description=i, value=default_val, style=self.style)

        # render all
        self.param['vbox'] = widgets.VBox([self.param[i] for i in self.job['param_rules']])
        # settings end
        self.param['accordion'] = widgets.Accordion(children=( self.param['vbox'], ), selected_index=None)
        self.param['accordion'].set_title(0, 'Input Parameters')
        with self.param['output']:
            display(self.param['accordion'])

    def renderSubmit(self):
        if self.submit['output'] == None:
            self.submit['output'] = widgets.Output()
        if self.submit['alert_output'] == None:
            self.submit['alert_output'] = widgets.Output()
        # create components
        if self.submitted:
            self.submit['button'] = widgets.Button(description="Job Submitted ✅", disabled=True)
        else:
            self.submit['button'] = widgets.Button(description="Submit Job")
        self.submit['button'].on_click(self.onSubmitButtonClick())
        
        with self.submit['output']:
            display(self.submit['alert_output'])
            display(self.submit['button'])

    def renderDownload(self):
        if self.download['output'] == None:
            self.download['output'] = widgets.Output()
        if self.download['alert_output'] == None:
            self.download['alert_output'] = widgets.Output()
        if self.download['result_output'] == None:
            self.download['result_output'] = widgets.Output()
        # create components
        if self.jobFinished:
            result_folder_content = self.compute.job.result_folder_content()
            # push default value to front
            try:
                result_folder_content.insert(0, result_folder_content.pop(result_folder_content.index(self.defaultRemoteResultFolder)))
            except: result_folder_content
            self.download['dropdown'] = widgets.Dropdown(options=result_folder_content, value=result_folder_content[0], description='select file/folder')
            self.download['button'] = widgets.Button(description="Download")
            self.download['button'].on_click(self.onDownloadButtonClick())
        else:
            self.download['button'] = widgets.Button(description="Download", disabled=True)
        
        with self.download['output']:
            if self.jobFinished:
                display(Markdown('# ☁️ Download Job Output Files'))
                display(self.download['alert_output'])
                display(self.download['result_output'])
                display(self.download['dropdown'])
            else:
                display(Markdown('# ⏳ Waiting for Job to Finish...'))
            display(self.download['button'])

    def renderResultStatus(self):
        if self.resultStatus['output'] == None:
            self.resultStatus['output'] = widgets.Output()
        
        if not self.submitted:
            with self.resultStatus['output']:
                display(Markdown('# 😴 No Job to Work On'))
                display(Markdown('you need to submit your job first'))
            return

        with self.resultStatus['output']:
            display(Markdown('# ✌️ Your Job is Here!'))
            self.compute.job.status()
        return

    def renderResultEvents(self):
        if self.resultEvents['output'] == None:
            self.resultEvents['output'] = widgets.Output()
        
        if not self.submitted: return

        with self.resultEvents['output']:
            self.compute.job.events()
        return

    def renderResultLogs(self):
        if self.resultLogs['output'] == None:
            self.resultLogs['output'] = widgets.Output()

        if not self.submitted: return
        with self.resultLogs['output']:
            self.compute.job.logs()
            self.tab.set_title(1, '✅ Your Job Status')
            self.tab.set_title(2, '✅ Download Job Result')
            display(Markdown('***'))
            display(Markdown('## ✅ your job completed'))
            self.jobFinished = True
            self.rerender(['download'])
        return

    # events
    def onDownloadButtonClick(self):
        def on_click(change):
            if self.downloading:
                self.download['alert_output'].clear_output(wait=True)
                with self.download['alert_output']:
                    display(Markdown('⚠️ download process is running in background...'))
                    return

            with self.download['result_output']:
                self.download['alert_output'].clear_output(wait=True)
                self.downloading = True
                self.compute.job.download_result_folder(remotePath=self.download['dropdown'].value)
                print('please check your data at your root folder under "' + self.globus_filename + '"')
                self.compute.recentDownloadPath = os.path.join(self.jupyter_globus['container_home_path'], self.globus_filename)
                self.downloading = False
        return on_click

    def onSubmitButtonClick(self):
        def on_click(change):
            if self.submitted: return
            with self.submit['alert_output']: clear_output(wait=True)

            self.compute.login()
            dataFolder = None
            self.jupyter_globus = self.compute.get_user_jupyter_globus()
            if self.job['require_upload_data']:
                dataFolder = self.uploadData['selector'].selected
                if dataFolder == None:
                    with self.submit['alert_output']:
                        display(Markdown('⚠️ please select a folder before upload...'))
                        return
                else:
                    dataFolder = dataFolder.replace(self.jupyter_globus['container_home_path'].strip('/'), '')
                    dataFolder = 'globus://' + self.jupyter_globus['endpoint'] + ':' + os.path.join(self.jupyter_globus['root_path'], dataFolder.strip('/'))

            data = self.get_data()
            self.compute.job = self.compute.create_job(hpc=data['computing_resource'], printJob=False)
            # slurm
            slurm = data['slurm']
            if data['email'] != None:
                slurm['mail_user'] = [data['email']]
                slurm['mail_type'] = ['FAIL', 'END', 'BEGIN']
            # param
            param = data['param']
            # download
            self.globus_filename = 'globus_download_' + self.compute.job.id
            resultFolder = 'globus://' + self.jupyter_globus['endpoint'] + ':' + os.path.join(self.jupyter_globus['root_path'], self.globus_filename)

            # submit
            self.compute.job.set(executableFolder='git://' + data['job_template'], dataFolder=dataFolder, resultFolder=resultFolder, printJob=False, param=param, slurm=slurm)
            self.compute.job.submit()
            self.tab.selected_index = 1
            self.submitted = True
            self.tab.set_title(1, '⏳ Your Job Status')
            self.rerender(['resultStatus', 'resultEvents', 'resultLogs', 'submit'])
        return on_click

    def onJobDropdownChange(self):
        def on_change(change):
            if change['type'] == 'change':
                if self.submitted:
                    return
                self.jobName = self.jobTemplate['dropdown'].value
                self.job = self.jobs[self.jobName]
                self.hpcName = self.job['default_hpc']
                self.hpc = self.hpcs[self.hpcName]
                self.rerender(['description', 'computingResource', 'slurm', 'param', 'uploadData'])
        return on_change

    def onComputingResourceDropdownChange(self):
        def on_change(change):
            if change['type'] == 'change':
                if self.submitted: return
                self.hpcName = self.computingResource['dropdown'].value
                self.hpc = self.hpcs[self.hpcName]
                self.rerender(['description', 'slurm', 'param', 'uploadData'])
        return on_change

    # helpers
    def init(self):
        silent = widgets.Output()
        with silent:
            self.compute.login()

        self.jobs = self.compute.list_git(raw=True)
        self.hpcs = self.compute.list_hpc(raw=True)
        # state
        self.submitted = False
        self.jobFinished = False
        self.downloading = False
        # components
        self.jobTemplate = { 'output': None }
        self.description = { 'output': None }
        self.computingResource = { 'output': None }
        self.slurm = { 'output': None }
        self.email = { 'output': None }
        self.submit = { 'output': None, 'alert_output': None }
        self.param = { 'output': None }
        self.uploadData = { 'output': None }
        self.resultStatus = { 'output': None }
        self.resultEvents = { 'output': None }
        self.resultLogs = { 'output': None }
        self.download = { 'output': None, 'alert_output': None, 'result_output': None }
        # main
        self.tab = None
        # information
        self.jobName = self.defaultJobName
        self.job  = self.jobs[self.jobName]
        self.hpcName = self.job['default_hpc']
        self.hpc = self.hpcs[self.hpcName]

    def rerender(self, components = []):
        for c in components:
            getattr(self, c)['output'].clear_output()
        for c in components:
            cl = list(c)
            cl[0] = cl[0].upper()
            ct = ''.join(cl)
            getattr(self, 'render' + ct)()

    # data
    def get_data(self):
        out = {
            'job_template': self.jobTemplate['dropdown'].value,
            'computing_resource': self.computingResource['dropdown'].value,
            'slurm': {},
            'param': {},
            'email': self.email['text'].value if self.email['checkbox'].value else None,
        }

        for i in self.slurm_configs:
            if self.slurm[i] != None:
                config = self.job['slurm_input_rules'][i]
                if i in self.slurm_integer_storage_unit_config:
                    out['slurm'][i] = str(self.slurm[i].value) + str(config['unit'])
                elif i in self.slurm_integer_time_unit_config:
                    seconds = self.unitTimeToSecond(config['unit'], self.slurm[i].value)
                    out['slurm'][i] = self.secondsToTime(seconds)
                else:
                    out['slurm'][i] = self.slurm[i].value

        for i in self.job['param_rules']:
            if i in self.param:
                out['param'][i] = self.param[i].value

        return out

    def secondsToTime(self, seconds):
        days = math.floor(seconds / (60 * 60 * 24))
        hours = math.floor(seconds / (60 * 60) - (days * 24))
        minutes = math.floor(seconds / 60 -  (days * 60 * 24) - (hours * 60))

        d = '0' + str(days) if days < 10 else str(days)
        h = '0' + str(hours) if hours < 10 else str(hours)
        m = '0' + str(minutes) if minutes < 10 else str(minutes)

        if days == 0:
            if hours == 0:
                return m + ':00'
            else:
                return h + ':' + m + ':00'
        else:
            return d + '-' + h + ':' + m + ':00'

    def unitTimeToSecond(self, unit, time):
        if unit == 'Minutes': return time * 60
        elif unit == 'Hours': return time * 60 * 60
        elif unit == 'Days': return time * 60 * 60 * 24