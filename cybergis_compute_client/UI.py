from IPython.display import display, Markdown
import ipywidgets as widgets

class UI:
    def __init__(self, compute):
        self.compute = compute
        self.style = {'description_width': '120px'}
        self.jobs = None
        self.hpcs = None
        self.job = None

    def render(self):
        self.init()
        self.assembleCompoenets()
        # job template
        job_template_output = widgets.Output()
        with job_template_output:
            display(self.jobTemplate['dropdown'], self.jobTemplate['output'])
        # tab
        tab = widgets.Tab(children=[
            job_template_output
        ])
        display(tab)

    def assembleCompoenets(self):
        self.jobTemplate = self.createJobTemplate()
        self.slurm = self.createSlurm()

    # components
    def createJobTemplate(self):
        ui = {
            'dropdown': widgets.Dropdown(options=[i for i in self.jobs], value='hello_world', description='📦 Job Templates:', style=self.style),
            'output': widgets.Output()
        }
        ui['dropdown'].observe(self.onJobDropdownChange())
        return ui

    def createSlurm(self):
        return

    # events
    def onJobDropdownChange(self):
        def on_change(change):
            if change['type'] == 'change':
                self.job = self.jobs[self.jobTemplate['dropdown'].value]
                self.jobTemplate['output'].clear_output()
                with self.jobTemplate['output']:
                    description = Markdown('**Template Description:** ' + self.job['description'])
                    estimated_runtime = Markdown('**Estimated Runtime:** ' + self.job['estimated_runtime'])
                    display(description, estimated_runtime)
        return on_change

    # helpers
    def init(self):
        if self.jobs == None:
            self.jobs = self.compute.list_git(raw=True)
        if self.hpcs == None:
            self.hpcs = self.compute.list_hpc(raw=True)