from IPython.display import display, Markdown
import ipywidgets as widgets

class UI:
    def __init__(self, compute):
        self.compute = compute
        self.style = {'description_width': 'auto'}
        self.jobs = None
        self.hpcs = None
        # selection
        self.job = None
        self.jobName = None
        self.hpc = None
        self.hpcName = None
        # state
        self.submitted = False
        # components
        self.jobTemplate = { 'output': None }
        self.computingResource = { 'output': None }
        self.slurm = { 'output': None }
        self.email = { 'output': None }
        self.submit = { 'output': None }
        self.result = { 'output': None }
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
            display(self.result['output'])

        # assemble into tabs
        self.tab = widgets.Tab(children=[
            job_config,
            job_status
        ])
        self.tab.set_title(0, 'Job Configuration')
        self.tab.set_title(1, 'Your Job Status')
        display(self.tab)

    def renderCompoenets(self):
        self.renderJobTemplate()
        self.renderComputingResource()
        self.renderSlurm()
        self.renderEmail()
        self.renderSubmit()
        self.renderResult()

    # components
    def renderJobTemplate(self):
        if self.jobTemplate['output'] == None:
            self.jobTemplate['output'] = widgets.Output()
        # create components
        self.jobTemplate['dropdown'] = widgets.Dropdown(options=[i for i in self.jobs], value=self.jobName, description='📦 Job Templates:', style=self.style)
        self.jobTemplate['description'] = Markdown('**' + self.jobName + 'Description:** ' + self.job['description'])
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
        self.slurm['partition'] = widgets.Text(value='partition')

        self.slurm['gpus'] = widgets.IntSlider(
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

        self.slurm['gpus_per_node'] = widgets.IntSlider(
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

        self.slurm['gpus_per_task'] = widgets.IntSlider(
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

        self.slurm['memory_in_mb'] = widgets.IntSlider(
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

        self.slurm['memory_in_gb'] = widgets.IntSlider(
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

        self.slurm['memory_per_cpu_in_mb'] = widgets.IntSlider(
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

        self.slurm['memory_per_cpu_in_gb'] = widgets.IntSlider(
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

        self.slurm['memory_per_gpu_in_mb'] = widgets.IntSlider(
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

        self.slurm['memory_per_gpu_in_gb'] = widgets.IntSlider(
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

        self.slurm['num_of_task'] = widgets.IntSlider(
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

        self.slurm['cpu_per_task'] = widgets.IntSlider(
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

        self.slurm['gpus_per_task'] = widgets.IntSlider(
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

        self.slurm['gpus_per_node'] = widgets.IntSlider(
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

        w = []
        for i in ['partition', 'gpus', 'gpus_per_node', 'gpus_per_task', 'memory_in_mb', 'memory_in_gb', 'memory_per_cpu_in_mb', 'memory_per_cpu_in_gb', 'memory_per_gpu_in_mb', 'memory_per_gpu_in_gb', 'num_of_task', 'cpu_per_task', 'gpus_per_task', 'gpus_per_node']:
            if self.slurm[i] != None:
                w.append(self.slurm[i])
        self.slurm['hbox'] = widgets.HBox(w)

        # settings end
        self.slurm['accordion'] = widgets.Accordion(children=( widgets.VBox(children=(self.slurm['description'], self.slurm['hbox'])), ), selected_index=None)
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

    def renderResult(self):
        if self.result['output'] == None:
            self.result['output'] = widgets.Output()

        # create components
        if 'output_status' not in self.result:
            self.result['output_status'] = widgets.Output()
        if 'output_events' not in self.result:
            self.result['output_events'] = widgets.Output()
        if 'output_logs' not in self.result:
            self.result['output_logs'] = widgets.Output()

        if self.submitted:
            divider = Markdown('***')
            with self.result['output_status']:
                display(widgets.Label(value='✅ job submitted with ID: ' + self.compute.job.id))
                display(self.compute.job.status())
            with self.result['output_events']:
                display(self.compute.job.events())
            with self.result['output_logs']:
                display(self.compute.job.logs())
            with self.result['output']:
                display(self.result['output_status'], divider, self.result['output_events'], divider, self.result['output_logs'])
        else:
            with self.result['output']:
                display('you need to submit your job first')

    # events
    def onSubmitButtonClick(self):
        def on_click(change):
            if self.submitted:
                return
            data = self.get_data()
            self.compute.job = self.compute.create_job(hpc=data['computing_resource'], printJob=False)
            self.compute.job.set(executableFolder='git://' + data['job_template'], printJob=False)
            self.compute.job.submit()
            self.tab.selected_index = 1
            self.submitted = True
            self.rerender(['result', 'submit'])
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