#!/usr/bin/python3

from flask import Flask, send_file, request
from flask_restful import Api, Resource
from datetime import datetime

import launcher

_IIN=0


class Reqfile(Resource):
    '''
request JSON
{"leakage_type":"...",
"initialization_time":"2018-01-01T22:00:00.000Z",
"position": {
    "type":"Feature",
    "geometry": {
        "type":"Point",
        "coordinates": [15.413818359374998,55.27442182695317]
        }
    }
}
    '''
    def post(self):
        global _IIN
        ret={}
        _IIN=_IIN+1
        mdata=request.get_json(force=True)
        date=datetime.strptime(mdata['initialization_time'],"%Y-%m-%dT%H:%M:%S.%fZ")
        sdate=date.strftime("%Y%m%d_%H%M")
        fname="leakage_model_"+sdate+"_{0:03d}.txt".format(_IIN)
        mdata.update({'app':'/opt/daimon/jobexec.sh'})
        mdata.update({'id':fname})
        mdata.update({'arguments':''})
        if 'lifetime' not in mdata:
            mdata.update({'lifetime':3600})
      
        run = launcher.Launch(fname,mdata)
        ret['file_name'] = run.get_id()
        return ret,200



class Getfile(Resource):

#    def post(self):
#        return send_file("/tmp/nowy")
  
    def get(self,_id):
        filename='/opt/daimon/none.txt'
        try:
            filename=launcher.Jobs[_id].get_path()+'/result.nc'
        except KeyError:
            return 'File not found',404
        launcher.Jobs_expire()
        return send_file(filename,mimetype='',attachment_filename='result.nc',cache_timeout=3600)

class Control(Resource):
    def listJobs(self):
        ret={}
        ret.update({'length':len(launcher.Jobs)})
        ret.update({'jobs':list(launcher.Jobs)})
        return ret

    def get(self,cmd):
        if cmd == 'list':
            return self.listJobs()
        elif cmd == 'expire_all':
            launcher.Jobs_expire()
        else:
            return 'command not found',404

app = Flask(__name__)
api = Api(app)
#app = Flask(__name__)
#api = Api(app)

api.add_resource(Reqfile,"/daimon/request")
api.add_resource(Control,"/daimon/control/<cmd>")
api.add_resource(Getfile,"/daimon/getfile/<_id>")
app.run(host='0.0.0.0',port=8900,debug=False)

