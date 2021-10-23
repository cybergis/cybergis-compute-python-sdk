from IPython.display import display, Markdown
import ipywidgets as widgets

class UI:
    def __init__(self, compute):
        self.compute = compute
        self.style = {'description_width': '120px'}
        self.jobs = compute.list_git(raw=True)
        self.hpcs = compute.list_hpc(raw=True)
        self.job = None

    def render(self):
        self.assembleCompoenets()
        # job template
        display(self.jobTemplate['dropdown'], self.jobTemplate['output'])

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
                with self.jobTemplate['output']:
                    description = Markdown('**Description: **' + self.job['description'])
                    estimated_runtime = Markdown('**Estimated Runtime:** ' + self.job['estimated_runtime'])
                    display(description, estimated_runtime)
        return on_change
