from .Client import *
from .Job import *

class CyberGISCompute:
    def __init__(self, url="cgjobsup.cigi.illinois.edu", port=443, isJupyter=False, protocol='HTTPS'):
        self.client = Client(url, port, protocol)
        self.isJupyter = isJupyter

    def create_job(self, maintainer, hpc=None, user=None, password=None):
        return Job(maintainer, hpc, None, user, password, self.client, isJupyter=self.isJupyter)

    def create_job_from_id(self, id=None):
        return Job(id=id, isJupyter=self.isJupyter)

    def list_hpc(self):
        hpc = self.client.request('GET', '/hpc')['hpc']
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

    def list_git(self):
        git = self.client.request('GET', '/git')['git']
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

    def list_maintainer(self):
        maintainers = self.client.request('GET', '/maintainer')['maintainer']
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
