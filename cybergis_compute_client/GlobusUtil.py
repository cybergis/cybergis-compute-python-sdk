"""
This module exposes GlobusUtil class which creates a GlobusUtil
object that serves as an entry point to the Globus Data Transfer Tool

Example:
        cybergis = GlobusUtil(compute)
"""


class GlobusUtil:
    """
    GlobusUtil class
    An interface that handles all interactions with Globus Data Transfer Tool

    Args:
        compute (CyberGISCompute): compute instance
            that was initialized by the user

    Attributes:
        compute (CyberGISCompute): instance of CyberGISCompute
            that was initialized earlier
    """
    def __init__(self, compute):
        self.compute = compute

    def download(self, endpoint, path, hpc):
        """
        Sends a download request to Globus API

        Args:
            endpoint (str): endpoint that needs to be accessed
            path (str): path to endpoint
            hpc (str): hpc resource where the endpoint is
                located. For e.g "keeling-community"

        Returns:
            JSON: output thats returned by the server
        """
        self.compute.login()
        return self.compute.client.request(
            'GET', '/globus-util/jupyter/download', {'jupyterhubApiToken': self.compute.jupyterhubApiToken, 'to': '{}:{}'.format(endpoint, path), 'hpc': hpc})

    def upload(self, endpoint, path, hpc):
        """
        Sends an upload request to Globus API

        Args:
            endpoint (str): endpoint that needs to be accessed
            path (str): path to endpoint
            hpc (str): hpc resource where the
            endpoint is located. For e.g "keeling-community"

        Returns:
            JSON: output thats returned by the server
        """
        self.compute.login()
        return self.compute.client.request(
            'GET', '/globus-util/jupyter/upload', {'jupyterhubApiToken': self.compute.jupyterhubApiToken, 'from': '{}:{}'.format(endpoint, path), 'hpc': hpc})
