import json
import urllib
webURL = urllib.urlopen('http://127.0.0.1:8900/daimon/control/todo')
data = webURL.read()
TODO = json.loads(data.decode())
#{u'properties': {u'state': u'todo', u'id': u'20190118212332081897', u'token': u'0yf5z99c'}, u'options': {u'initialization_time': u'2018-01-01T22:00:00.000Z', u'app': u'/opt/daimon/jobexec.sh', u'arguments': u'', u'lifetime': 3600, u'position': {u'geometry': {u'type': u'Point', u'coordinates': [15.413818359374998, 55.27442182695317]}, u'type': u'Feature'}, u'id': u'leakage_model_20180101_2200_003.txt', u'leakage_type': u'...'}}

for i in TODO:
    w=urllib.urlopen('http://127.0.0.1:8900/daimon/control/show?jid={0:s}'.format(i))
    d2=w.read()
    prop=json.loads(d2.decode('ascii'))
    print(prop['options']['position']['geometry']['coordinates'])

