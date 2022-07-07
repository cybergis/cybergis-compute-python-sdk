"""
This module exposes Client class which creates a Client
object that serves as a tool to make requests to different servers

Example:
        client = Client()
"""
import http.client as client
import json
from os import path


class Client:
    """
    An inteface that handles requests made to different servers

    Args:
        url (str): url that needs to be accessed
        port (str): port of the Jupyter or Python interface
        protocol (str): Typically HTTP or HTTPS
        suffix (str): specify version. For e.g v2

    Attributes:
        url (str): url that needs to be accessed
        port (str): port of the Jupyter or Python interface
        suffix (str): specify version. For e.g v2
    """
    def __init__(
        self, url="cgjobsup.cigi.illinois.edu",
            port=443, protocol="HTTPS", suffix="v2"):
        self.url = url + ':' + str(port)
        self.protocol = protocol
        self.suffix = suffix

    def request(self, method, uri, body={}):
        """
        Returns data from a request made to the specified uri

        Args:
            methods (str): type of request that needs to be
                made. For e.g "POST"
            uri (str): uri of the server
            body (str): data that needs to be sent

        Returns:
            JSON: output thats returned by the server
        """
        if self.protocol == 'HTTP':
            connection = client.HTTPConnection(self.url)
        else:
            connection = client.HTTPSConnection(self.url)
        headers = {'Content-type': 'application/json'}
        connection.request(
            method, '/' + path.join(self.suffix.strip('/'), uri.strip('/')),
            json.dumps(body), headers)
        response = connection.getresponse()
        out = response.read().decode()
        try:
            data = json.loads(out)
        except:
            raise Exception('cannot decode data: ' + out)

        if 'error' in data:
            msg = ''
            if 'messages' in data:
                msg = str(data['messages'])
            raise Exception('server ' + self.url + uri + ' responded with error "' + data['error'] + msg + '"')

        return data
