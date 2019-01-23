import json
import urllib
import os
import subprocess
import config
from datetime import datetime
webURL = urllib.urlopen('http://127.0.0.1:8900/daimon/control/list?state=todo')
data = webURL.read()
print(data)
TODO = json.loads(data.decode())
#{u'properties': {u'state': u'todo', u'id': u'20190118212332081897', u'token': u'0yf5z99c'}, u'options': {u'initialization_time': u'2018-01-01T22:00:00.000Z', u'app': u'/opt/daimon/jobexec.sh', u'arguments': u'', u'lifetime': 3600, u'position': {u'geometry': {u'type': u'Point', u'coordinates': [15.413818359374998, 55.27442182695317]}, u'type': u'Feature'}, u'id': u'leakage_model_20180101_2200_003.txt', u'leakage_type': u'...'}}

for i in TODO:
    w = urllib.urlopen('http://{0:s}:{1:d}/daimon/control/show?jid={2:s}'.format(config.addr,config.port,i))
    d2 = w.read()
    prop = json.loads(d2.decode('ascii'))
    print(prop)
    crd = prop['options']['position']['geometry']['coordinates']
    token = prop['properties']['token']
    try:
        os.mkdir(token)
    except OSError as e:
        print(e)
    os.chdir(token)
    date = datetime.strptime(prop['options']['initialization_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
    cmd = "sbatch ../run.sh {0:s} {1:s} {2:s} {3:f} {4:f} {5:d} {6:d} {7:d} {8:d}"\
        .format(token, prop['properties']['id'], 'NN', crd[0], crd[1], date.year, date.month, date.day, date.hour)
    print(cmd)
    cmd_out = subprocess.check_output(cmd.split())
    ll = cmd_out.split()
    slurm_id=ll[len(ll)-1]
    sw = urllib.urlopen('http://{0:s}:{1:d}/daimon/control/set?jid={2:s}?slurm={3:s}'.format(config.addr,config.port,i,slurm_id))





