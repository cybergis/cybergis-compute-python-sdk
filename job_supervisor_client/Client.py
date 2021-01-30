import http.client as client
import requests
import json
import shutil
import os

class Client:
    def __init__(self, url="cglogger.cigi.illinois.edu", port=443):
        self.url = url + ':' + str(port)

    def request(self, method, uri, body, protocol='HTTPS'):
        if protocol == 'HTTP':
            connection = client.HTTPConnection(self.url)
        else:
            connection = client.HTTPSConnection(self.url)
        headers = {'Content-type': 'application/json'}
        connection.request(method, uri, json.dumps(body), headers)
        response = connection.getresponse()
        data = json.loads(response.read().decode())

        if 'error' in data:
            msg = ''
            if 'messages' in data:
                msg = str(data['messages'])
            raise Exception('server ' + self.url + ' responded with error "' + data['error'] + msg + '"')

        return data

    def download(self, method, uri, body, localDir, protocol='HTTPS'):
        if protocol == 'HTTP':
            connection = client.HTTPConnection(self.url)
        else:
            connection = client.HTTPSConnection(self.url)
        headers = {'Content-type': 'application/json'}
        connection.request(method, uri, json.dumps(body), headers)
        response = connection.getresponse()
        contentType = response.getheader('Content-Type')

        if 'json' in contentType:
            data = json.loads(response.read().decode())
            localDir += '.json'
            # handel file not found error which is returned as a JSON
            if 'error' in data:
                msg = ''
                if 'messages' in data:
                    msg = str(data['messages'])
                raise Exception('server ' + self.url + ' responded with error "' + data['error'] + msg + '"')

        if 'tar' in contentType:
            localDir += '.tar'

        if 'zip' in contentType:
            localDir += '.zip'

        with open(localDir, "wb") as d:
            with os.fdopen(response.fileno(), "r") as s:
                # stream socket to file
                shutil.copyfileobj(s, d)

        response.close()
        return localDir

    def upload(self, uri, body, file, protocol='HTTPS'):
        data = json.loads(requests.post(protocol.lower() + '://' + self.url + uri, data=body, files={'file': file}).content.decode())
        if 'error' in data:
            raise Exception('server ' + self.url + ' responded with error "' + data['error'] + '"')
        return data