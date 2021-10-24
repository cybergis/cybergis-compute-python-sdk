from IPython.display import display, Markdown
import ipywidgets as widgets

class UI:
    def __init__(self, compute):
        self.compute = compute
        self.style = {'description_width': '200px'}
        self.jobs = None
        self.hpcs = None
        # selection
        self.job = None
        self.jobName = None
        # components
        self.jobTemplate = { 'output': None }
        self.computingResource = { 'output': None }

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
        self.jobTemplate['description'] = Markdown('**Description:** ' + self.job['description'])
        self.jobTemplate['estimated_runtime'] = Markdown('**Estimated Runtime:** ' + self.job['estimated_runtime'])
        self.jobTemplate['dropdown'].observe(self.onJobDropdownChange())
        with self.jobTemplate['output']:
            display(self.jobTemplate['dropdown'], self.jobTemplate['description'], self.jobTemplate['estimated_runtime'])

    def renderComputingResource(self):
        if self.computingResource['output'] == None:
            self.computingResource['output'] = widgets.Output()
        # create components
        hpcName = self.job['default_hpc']
        self.jobTemplate['dropdown'] = widgets.Dropdown(options=[i for i in self.job['supported_hpc']], value=hpcName, description='🖥 Computing Recourse:', style=self.style)
        self.jobTemplate['description'] = widgets.Label(value=self.hpcs[hpcName]['description'])
        self.jobTemplate['accordion'] = widgets.Accordion(children=( widgets.VBox(children=(self.jobTemplate['dropdown'], self.jobTemplate['description'])), ), titles=('Computing Resource'))
        with self.computingResource['output']:
            display(self.jobTemplate['accordion'])

    def createSlurm(self):
        return

    # events
    def onJobDropdownChange(self):
        def on_change(change):
            if change['type'] == 'change':
                self.jobName = self.jobTemplate['dropdown'].value
                self.job = self.jobs[self.jobName]
                self.rerender(['jobTemplate', 'computingResource'])
        return on_change

    # helpers
    def init(self):
        if self.jobs == None:
            self.jobs = self.compute.list_git(raw=True)
            self.jobName = 'hello_world'
            self.job  = self.jobs[self.jobName]
        if self.hpcs == None:
            self.hpcs = self.compute.list_hpc(raw=True)

    def rerender(self, components = []):
        for c in components:
            getattr(self, c)['output'].clear_output()
            getattr(self, 'render' + c.title())
