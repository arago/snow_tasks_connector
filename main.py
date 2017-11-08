#version 0.0.4

import requests
import json
import ConfigParser
import sys

if ( len(sys.argv) != 2):
	print 'Usage: ' + sys.argv[0] + ' <config_file_path>'
	exit(0)

config = ConfigParser.ConfigParser()
config.read(sys.argv[1])

url = config.get('SNOW', 'url') + "?" + config.get('SNOW', 'filter_field') + "=" + config.get('SNOW', 'group_id')
sdf = config.get('HIRO', 'sdf')
sdf = json.loads(sdf)
user = config.get('SNOW', 'user')
pwd = config.get('SNOW', 'password')
headers = {"Content-Type":"application/json","Accept":"application/json"}
hiro_url = config.get('HIRO', 'url')

history = []
history_file = config.get('CONNECTOR', 'history_file')
with open(history_file) as f:
	for line in f:
		history.append(line.rstrip('\n'))
f.close()

response = requests.get(url, auth=(user, pwd), headers=headers)
if response.status_code != 200: 
    print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
    exit()

data = response.json()
task_count = len(data['result'])
counter = 0
while ( counter < task_count ):
	if any(data['result'][counter]['number'] in s for s in history):
		counter = counter + 1
		continue
	sdf['mand']['sourceId'] = data['result'][counter]['sys_id']
	sdf['mand']['eventId'] = data['result'][counter]['number']
	sdf['mand']['description'] = data['result'][counter]['description']
	sdf['mand']['eventName'] = data['result'][counter]['number']
	sdf['free']['State'] = "New"
	sdf['free']['impact'] = data['result'][counter]['impact']
	sdf['opt']['sourceStatus'] = "New"
	hiro_headers = {"Content-Type":"application/json", "Cache-Control": "no-cache"}
	payload = (json.dumps(sdf)).decode('utf-8')
	post = requests.post(hiro_url, headers=hiro_headers, data=payload, verify=False)
	if post.status_code != 200:
		print 'POST error'
		exit()
	history.append(data['result'][counter]['number'])
	counter = counter + 1

save_file = open(history_file, "w")
for entry in history:
	save_file.write("%s\n" % entry)
save_file.close()
