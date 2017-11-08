import json
import requests
import urllib
import ConfigParser
import sys

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
	data = json.loads(post_data)
	uri = url + '/' + data['mand']['sourceId']
	headers = {"Content-Type":"application/json","Accept":"application/json"}
	for items in data['opt']['comment']:
		payload = "{'comments':'" + urllib.quote_plus(str(items['opt']['content'])) + "'}"
		response = requests.put(uri, auth=(user,password), headers=headers, data=payload)
		if ( response.status_code != 200 ):
			print response.json()
	if ( data['free']['State'] == "Resolved" ):
		print 'RESOLVED'
		payload = "{'state': 'Closed Complete', 'comments':'Issue Resolved'}"
		response = requests.put(uri, auth=(user,password), headers=headers, data=payload)
                if ( response.status_code != 200 ):
                        print response.json()

def run(server_class=HTTPServer, handler_class=S, port=9999):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    if ( len(sys.argv) != 2):
        print 'Usage: ' + sys.argv[0] + ' <config_file_path>'
        exit(0)
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    url = config.get('SNOW', 'url')
    user = config.get('SNOW', 'user')
    password = config.get('SNOW', 'password')
    run()
