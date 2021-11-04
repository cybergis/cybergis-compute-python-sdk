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
        # components
        self.jobTemplate = { 'output': None }
        self.computingResource = { 'output': None }
        self.slurm = { 'output': None }

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

        # assemble into tabs
        tab = widgets.Tab(children=[
            job_config
        ])
        tab.set_title(0, 'Job Configuration')
        display(tab)

    def renderCompoenets(self):
        self.renderJobTemplate()
        self.renderComputingResource()

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

    def renderSlurm(self):
        if self.slurm['output'] == None:
            self.slurm['output'] = widgets.Output()
        # create components
        self.slurm['description'] = widgets.Label(value='All configs are optional. Please refer to Slurm official documentation at https://slurm.schedmd.com/sbatch.html')
        # settings
        self.slurm['total_gpu'] = widgets.IntSlider(
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

        # settings end
        self.slurm['accordion'] = widgets.Accordion(children=( widgets.VBox(children=(self.slurm['description'], self.slurm['total_gpu'])), ), selected_index=None)
        self.slurm['accordion'].set_title(0, 'Slurm Computing Configurations')
        with self.slurm['output']:
            display(self.slurm['accordion'])

    # events
    def onJobDropdownChange(self):
        def on_change(change):
            if change['type'] == 'change':
                self.jobName = self.jobTemplate['dropdown'].value
                self.job = self.jobs[self.jobName]
                self.hpcName = self.job['default_hpc']
                self.hpc = self.hpcs[self.hpcName]
                self.rerender(['jobTemplate', 'computingResource', 'slurm'])
        return on_change

    def onComputingResourceDropdownChange(self):
        def on_change(change):
            if change['type'] == 'change':
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
