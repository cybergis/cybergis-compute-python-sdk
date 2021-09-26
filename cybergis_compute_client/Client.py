import http.client as client
import requests
import json


class Client:
    def __init__(self, url="cglogger.cigi.illinois.edu", port=443, protocol="HTTPS"):
        self.url = url + ':' + str(port)
        self.protocol = protocol

    def request(self, method, uri, body={}):
        if self.protocol == 'HTTP':
            connection = client.HTTPConnection(self.url)
        else:
            connection = client.HTTPSConnection(self.url)
        headers = {'Content-type': 'application/json'}
        connection.request(method, uri, json.dumps(body), headers)
        response = connection.getresponse()
        out = response.read().decode()
        print(out)
        data = json.loads(out)

        if 'error' in data:
            msg = ''
            if 'messages' in data:
                msg = str(data['messages'])
            raise Exception('server ' + self.url + ' responded with error "' + data['error'] + msg + '"')

        return data

    def download(self, method, uri, body, localDir):
        url = self.protocol.lower() + '://' + self.url + uri
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
        url = self.protocol.lower() + '://' + self.url + uri
        data = json.loads(requests.post(url, data=body, files={'file': file}).content.decode())
        if 'error' in data:
            return '❌ server ' + self.url + ' responded with error "' + data['error'] + '"'
        return data
