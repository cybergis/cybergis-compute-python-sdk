import http.client as client
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
        return json.loads(response.read().decode())

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