from IPython.display import display, Markdown
import ipywidgets as widgets
from ipyfilechooser import FileChooser

class UI:
    def __init__(self, compute):
        self.compute = compute
        self.style = {'description_width': 'auto'}
        self.layout = widgets.Layout(width='60%')
        self.jobs = None
        self.hpcs = None
        # selection
        self.job = None
        self.jobName = None
        self.hpc = None
        self.hpcName = None
        # state
        self.submitted = False
        self.jobFinished = False
        # components
        self.jobTemplate = { 'output': None }
        self.computingResource = { 'output': None }
        self.slurm = { 'output': None }
        self.email = { 'output': None }
        self.submit = { 'output': None }
        self.resultStatus = { 'output': None }
        self.resultEvents = { 'output': None }
        self.resultLogs = { 'output': None }
        self.download = { 'output': None }
        # main
        self.tab = None

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
            display(self.computingResource['output'])
            display(self.slurm['output'])
            display(self.email['output'])
            display(self.submit['output'])
        
        # 2. job status
        job_status = widgets.Output()
        with job_status:
            display(Markdown('# ✌️ Your Job is Here!'))
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
        self.renderComputingResource()
        self.renderSlurm()
        self.renderEmail()
        self.renderSubmit()
        self.renderResultStatus()
        self.renderResultEvents()
        self.renderResultLogs()
        self.renderDownload()

    # components
    def renderJobTemplate(self):
        if self.jobTemplate['output'] == None:
            self.jobTemplate['output'] = widgets.Output()
        # create components
        self.jobTemplate['dropdown'] = widgets.Dropdown(options=[i for i in self.jobs], value=self.jobName, description='📦 Job Templates:', style=self.style)
        self.jobTemplate['description'] = Markdown('**' + self.jobName + ' Description:** ' + self.job['description'])
        self.jobTemplate['estimated_runtime'] = Markdown('**Estimated Runtime:** ' + self.job['estimated_runtime'])
        self.jobTemplate['dropdown'].observe(self.onJobDropdownChange())
        with self.jobTemplate['output']:
            display(self.jobTemplate['dropdown'], self.jobTemplate['description'], self.jobTemplate['estimated_runtime'])

    def renderComputingResource(self):
        if self.computingResource['output'] == None:
            self.computingResource['output'] = widgets.Output()
        # create components
        self.computingResource['dropdown'] = widgets.Dropdown(options=[i for i in self.job['supported_hpc']], value=self.hpcName, description='🖥 Computing Recourse:', style=self.style)
        self.computingResource['description'] = widgets.Label(value=self.hpcName + ' Description: ' + self.hpc['description'])
        self.computingResource['accordion'] = widgets.Accordion(children=( widgets.VBox(children=(self.computingResource['dropdown'], self.computingResource['description'])), ), selected_index=None)
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
        # create components
        self.slurm['description'] = widgets.Label(value='All configs are optional. Please refer to Slurm official documentation at https://slurm.schedmd.com/sbatch.html')
        # settings
        self.slurm['partition'] = widgets.Text(value='xxx', description='partition', style=self.style)

        self.slurm['gpus'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='gpus',
            style=self.style, layout=self.layout
        )

        self.slurm['gpus_per_node'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='gpus_per_node',
            style=self.style, layout=self.layout
        )

        self.slurm['gpus_per_task'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='gpus_per_task',
            style=self.style, layout=self.layout
        )

        self.slurm['memory_in_mb'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='gpus_per_task',
            style=self.style, layout=self.layout
        )

        self.slurm['memory_in_gb'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='memory_in_gb',
            style=self.style, layout=self.layout
        )

        self.slurm['memory_per_cpu_in_mb'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='memory_per_cpu_in_mb',
            style=self.style, layout=self.layout
        )

        self.slurm['memory_per_cpu_in_gb'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='memory_per_cpu_in_gb',
            style=self.style, layout=self.layout
        )

        self.slurm['memory_per_gpu_in_mb'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='memory_per_gpu_in_mb',
            style=self.style, layout=self.layout
        )

        self.slurm['memory_per_gpu_in_gb'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='memory_per_gpu_in_gb',
            style=self.style, layout=self.layout
        )

        self.slurm['num_of_task'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='num_of_task',
            style=self.style, layout=self.layout
        )

        self.slurm['cpu_per_task'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='cpu_per_task',
            style=self.style, layout=self.layout
        )

        self.slurm['gpus_per_task'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='gpus_per_task',
            style=self.style, layout=self.layout
        )

        self.slurm['gpus_per_node'] = widgets.IntSlider(
            value=1,
            min=1,
            max=20,
            step=1,
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
            description='gpus_per_node',
            style=self.style, layout=self.layout
        )

        w = []
        for i in ['partition', 'gpus', 'gpus_per_node', 'gpus_per_task', 'memory_in_mb', 'memory_in_gb', 'memory_per_cpu_in_mb', 'memory_per_cpu_in_gb', 'memory_per_gpu_in_mb', 'memory_per_gpu_in_gb', 'num_of_task', 'cpu_per_task', 'gpus_per_task', 'gpus_per_node']:
            if self.slurm[i] != None:
                w.append(self.slurm[i])
        self.slurm['vbox'] = widgets.VBox(w)

        # settings end
        self.slurm['accordion'] = widgets.Accordion(children=( widgets.VBox(children=(self.slurm['description'], self.slurm['vbox'])), ), selected_index=None)
        self.slurm['accordion'].set_title(0, 'Slurm Computing Configurations')
        with self.slurm['output']:
            display(self.slurm['accordion'])

    def renderSubmit(self):
        if self.submit['output'] == None:
            self.submit['output'] = widgets.Output()
        # create components
        if self.submitted:
            self.submit['button'] = widgets.Button(description="Job Submitted ✅", disabled=True)
        else:
            self.submit['button'] = widgets.Button(description="Submit Job")
        self.submit['button'].on_click(self.onSubmitButtonClick())
        with self.submit['output']:
            display(self.submit['button'])


    def renderDownload(self):
        if self.download['output'] == None:
            self.download['output'] = widgets.Output()
        # create components
        self.download['selector'] = None
        if self.jobFinished:
            self.download['selector'] = FileChooser('./')
            self.download['selector'].show_only_dirs = True
            self.download['selector'].title = 'Please Select a Folder'
            self.download['button'] = widgets.Button(description="👇 Download")
        else:
            self.download['button'] = widgets.Button(description="👇 Download", disabled=True)
        self.download['button'].on_click(self.onDownloadButtonClick())
        
        with self.download['output']:
            if self.jobFinished:
                display(Markdown('# ☁️ Download Job Result'))
                display(self.download['selector'])
            else:
                display(Markdown('# ⏳ Waiting for Job to Finish...'))
            display(self.download['button'])


    def renderResultStatus(self):
        if self.resultStatus['output'] == None:
            self.resultStatus['output'] = widgets.Output()
        
        if not self.submitted:
            with self.resultStatus['output']:
                display(Markdown('# 😴 No Job to Work On'))
                display('you need to submit your job first')
            return

        with self.resultStatus['output']:
            self.compute.job.status()
        return

    def renderResultEvents(self):
        if self.resultEvents['output'] == None:
            self.resultEvents['output'] = widgets.Output()
        
        if not self.submitted:
            return

        with self.resultEvents['output']:
            self.compute.job.events()
        return

    def renderResultLogs(self):
        if self.resultLogs['output'] == None:
            self.resultLogs['output'] = widgets.Output()
        
        if not self.submitted:
            return

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
            return
        return on_click

    def onSubmitButtonClick(self):
        def on_click(change):
            if self.submitted:
                return
            data = self.get_data()
            self.compute.job = self.compute.create_job(hpc=data['computing_resource'], printJob=False)
            # slurm
            slurm = {}
            if data['email'] != None:
                slurm['mail_user'] = [data['email']]
                slurm['mail_type'] = ['FAIL', 'END', 'BEGIN']
            # submit
            self.compute.job.set(executableFolder='git://' + data['job_template'], printJob=False)
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
                self.rerender(['jobTemplate', 'computingResource', 'slurm'])
        return on_change

    def onComputingResourceDropdownChange(self):
        def on_change(change):
            if change['type'] == 'change':
                if self.submitted:
                    return
                self.hpcName = self.computingResource['dropdown'].value
                self.hpc = self.hpcs[self.hpcName]
                self.rerender(['computingResource', 'slurm'])
        return on_change

    # helpers
    def init(self):
        if self.jobs == None:
            self.jobs = self.compute.list_git(raw=True)
            self.jobName = 'hello_world'
            self.job  = self.jobs[self.jobName]
        if self.hpcs == None:
            self.hpcs = self.compute.list_hpc(raw=True)
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
        return {
                'job_template': self.jobTemplate['dropdown'].value,
                'computing_resource': self.computingResource['dropdown'].value,
                'slurm': {
                    'partition': None if self.slurm['partition'] == None else self.slurm['partition'].value,
                    'gpus': None if self.slurm['gpus'] == None else self.slurm['gpus'].value,
                    'gpus_per_node': None if self.slurm['gpus'] == None else self.slurm['gpus'].value,
                    'gpus_per_task': None if self.slurm['gpus_per_task'] == None else self.slurm['gpus_per_task'].value,
                    'memory_in_mb': None if self.slurm['memory_in_mb'] == None else self.slurm['memory_in_mb'].value,
                    'memory_in_gb': None if self.slurm['memory_in_gb'] == None else self.slurm['memory_in_gb'].value,
                    'memory_per_cpu_in_mb': None if self.slurm['memory_per_cpu_in_mb'] == None else self.slurm['memory_per_cpu_in_mb'].value,
                    'memory_per_cpu_in_gb': None if self.slurm['memory_per_cpu_in_gb'] == None else self.slurm['memory_per_cpu_in_gb'].value,
                    'memory_per_gpu_in_mb': None if self.slurm['memory_per_gpu_in_mb'] == None else self.slurm['memory_per_gpu_in_mb'].value,
                    'memory_per_gpu_in_gb': None if self.slurm['memory_per_gpu_in_gb'] == None else self.slurm['memory_per_gpu_in_gb'].value,
                    'num_of_task': None if self.slurm['num_of_task'] == None else self.slurm['num_of_task'].value,
                    'cpu_per_task': None if self.slurm['cpu_per_task'] == None else self.slurm['cpu_per_task'].value,
                    'gpus_per_task': None if self.slurm['gpus_per_task'] == None else self.slurm['gpus_per_task'].value,
                    'gpus_per_node': None if self.slurm['gpus_per_node'] == None else self.slurm['gpus_per_node'].value,
                },
                'email': self.email['text'].value if self.email['checkbox'] else None,
                # 'globus': {
                #     'custom_download': {
                #         'globus_download_endpoint': globus_download_endpoint.value,
                #         'globus_download_path': globus_download_path.value,
                #         'is_globus_download': globus_download_cbox.value
                #     },
                #     'custom_upload': {
                #         'globus_upload_endpoint': globus_upload_endpoint.value,
                #         'globus_upload_path': globus_upload_path.value,
                #         'is_globus_upload': globus_upload_cbox.value
                #     },
                #     'jupyter_download': {
                #         'is_globus_download': globus_jupyter_download_cbox.value
                #     },
                #     'jupyter_upload': {
                #         'globus_upload_path': globus_jupyter_upload_path.value,
                #         'is_globus_upload': globus_jupyter_upload_cbox.value
                #     }
                # }
            }