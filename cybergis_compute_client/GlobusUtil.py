class GlobusUtil:
    def __init__(self, compute):
        self.compute = compute

    def download(self, endpoint, path, hpc):
        self.compute.login()
        return self.compute.client.request('GET', '/globus-util/jupyter/download', {
            'jupyterhubApiToken': self.compute.jupyterhubApiToken,
            'to': '{}:{}'.format(endpoint, path),
            'hpc': hpc
        })

    def upload(self, endpoint, path, hpc):
        self.compute.login()
        return self.compute.client.request('GET', '/globus-util/jupyter/upload', {
            'jupyterhubApiToken': self.compute.jupyterhubApiToken,
            'from': '{}:{}'.format(endpoint, path),
            'hpc': hpc
        })
