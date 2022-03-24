"""
This module exposes Client class which creates a Client
object that serves as a tool to make requests to different servers

Example:
        client = Client()
"""
import http.client as client
import requests
import json
from os import path

class Client:
    """
    Client class
    An inteface that handles requests made to different servers
    Attributes:
        url (str)                   : url that needs to be accessed
        port (str)                  : port of the Jupyter or Python interface
        suffix (str)                : specify version. For e.g v2
    """
    def __init__(self, url="cgjobsup.cigi.illinois.edu", port=443, protocol="HTTPS", suffix="v2"):
        """
        Initializes instance Client using inputs from the client
        Args:
            url (str)               : url that needs to be accessed
            port (str)              : port of the Jupyter or Python interface
            protocol (str)          : Typically HTTP or HTTPS
            suffix (str)            : specify version. For e.g v2
        Returns:
            (obj)                   : this Client
        """
        self.url = url + ':' + str(port)
        self.protocol = protocol
        self.suffix = suffix

    def request(self, method, uri, body={}):
        """
        Returns data from a request made to the specified uri
        Args:
            methods (str)           : type of request that needs to be made.
                                    For e.g "POST"
            uri (str)               : uri of the server
            body (str)              : data that needs to be sent
        Returns:
            JSON                    : output thats returned by the server
        """
        if self.protocol == 'HTTP':
            connection = client.HTTPConnection(self.url)
        else:
            connection = client.HTTPSConnection(self.url)
        headers = {'Content-type': 'application/json'}
        connection.request(method, '/' + path.join(self.suffix.strip('/'), uri.strip('/')), json.dumps(body), headers)
        response = connection.getresponse()
        out = response.read().decode()
        data = json.loads(out)

        if 'error' in data:
            msg = ''
            if 'messages' in data:
                msg = str(data['messages'])
            raise Exception('server ' + self.url + ' responded with error "' + data['error'] + msg + '"')

        return data

    def download(self, uri, body, localDir):
        """
        Downloads data from a request made to the specified uri onto the specifed path
        Args:
            uri (str)               : uri of the server
            body (str)              : data that needs to be dowloaded
            localDir (str)          : path where the data needs to be downloaded

        Returns:
            str                     : path where the data is stored
        """
        url = self.protocol.lower() + '://' + path.join(self.url.strip('/'), self.suffix.strip('/'), uri.strip('/'))
        response = requests.get(url, data=body, stream=True)
        contentType = response.headers['Content-Type']

        if response.encoding is None:
            response.encoding = 'utf-8'

        if 'json' in contentType:
            data = json.loads(response.content.decode())
            localDir += '.json'
            # handel file not found error which is returned as a JSON
            if 'error' in data:
                msg = ''
                if 'messages' in data:
                    msg = str(data['messages'])
                print('❌ server ' + self.url + ' responded with error "' + data['error'] + '"')

        if 'tar' in contentType:
            localDir += '.tar'

        if 'zip' in contentType:
            localDir += '.zip'

        with open(localDir, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        response.close()
        return localDir

    def upload(self, uri, body, file):
        """
        Uploads data using a request made to the specified uri
        Args:
            uri (str)               : uri of the server
            body (str)              : data that needs to be uploaded
            file (str)              : file that needs to be uploaded

        Returns:
            JSON                    : output from the upload request to the server
        """
        url = self.protocol.lower() + '://' + path.join(self.url.strip('/'), self.suffix.strip('/'), uri.strip('/'))
        data = json.loads(requests.post(url, data=body, files={'file': file}).content.decode())
        if 'error' in data:
            return '❌ server ' + self.url + ' responded with error "' + data['error'] + '"'
        return data