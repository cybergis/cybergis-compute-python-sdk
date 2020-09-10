import http.client as client
import requests
import json

class Client:
    def __init__(self, url="cglogger.cigi.illinois.edu", port=3030):
        self.url = url + ':' + str(port)

    def request(self, method, uri, body, protocol='HTTP'):
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

    def download(self, method, uri, body, localDir, protocol='HTTP'):
        if protocol == 'HTTP':
            connection = client.HTTPConnection(self.url)
        else:
            connection = client.HTTPSConnection(self.url)
        headers = {'Content-type': 'application/json'}
        connection.request(method, uri, json.dumps(body), headers)
        response = connection.getresponse().read()
        with open(localDir, "wb") as file:
            file.write(response)

    def upload(self, uri, body, file, protocol='HTTP'):
        data = json.loads(requests.post(protocol.lower() + '://' + self.url + uri, data=body, files={'file': file}).content.decode())
        if 'error' in data:
            raise Exception('server ' + self.url + ' responded with error "' + data['error'] + '"')
        return data