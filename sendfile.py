#!/usr/bin/python3

from flask import Flask, send_file, request, make_response
from flask_restful import Api, Resource, reqparse

import launcher
import config
import os

_IIN = 0
VERSION = 0.3

class Reqfile(Resource):
    def post(self):
        global _IIN
        ret={}
        _IIN=_IIN+1
        mdata=request.get_json(force=True)
        fname="job_{0:03d}".format(_IIN)
        mdata.update({'app':config.app})
        mdata.update({'id':fname})
        mdata.update({'arguments':''})
        if 'lifetime' not in mdata:
            mdata.update({'lifetime':3600})
        run = launcher.Launch(fname,argjson=mdata,tmpdir=config.tmp)
        ret['file_name'] = run.get_id()
        return ret,200



class Getfile(Resource):

    def get(self,_id):
        try:
            filename=launcher.Jobs[_id].get_path()+'/'+config.resultFile
            if not os.path.isfile(filename):
                return 'File not ready',404
        except KeyError:
            return 'File not found',404
        launcher.jobs_expire()
        return send_file(filename,mimetype='',attachment_filename='result.nc',cache_timeout=3600)

class Control(Resource):
    def listJobs(self):
        ret=[]
        for j in launcher.Jobs.values():
            ret.append({'id':j.get_id(),'state':j.properties['state']})

        return ret

    def listSTATE(self,state):
        ret=[]
        for j in launcher.Jobs.values():
            if j.properties['state'] == state:
                ret.append(j.get_id())
        return ret

    def list(self):
        parser = reqparse.RequestParser()
        parser.add_argument('state')
        args = parser.parse_args()
        state = args['state']
        if state == 'all' or state is None:
            return self.listJobs()
        else:
            return self.listSTATE(state)

    def show(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id')
        args=parser.parse_args()
        try:
            job=launcher.Jobs[args['id']]
            return {'properties':job.properties,'options':job.options}
        except KeyError:
            return 'Missing',404
 
    def set(self):
        parser=reqparse.RequestParser()
        parser.add_argument('id')
        parser.add_argument('state')
        parser.add_argument('slurm')
        args=parser.parse_args()
        try:
            job=launcher.Jobs[args['id']]
            if args['state'] is not None:
                job.properties['state']=args['state']
            if args['slurm'] is not None:
                job.properties['slurm']=args['slurm']
            return job.properties
        except KeyError:
            return 'Missing',404
 

    def post(self,cmd):
        return self.get(cmd)

    def get(self,cmd):
        if cmd == 'list':
            return self.list()
        elif cmd == 'expire_all':
            launcher.jobs_expire()
            return 'OK',200
        elif cmd == 'show':
            return self.show()
        elif cmd == 'set':
            return self.set()
        elif cmd == 'version':
            return VERSION
        else:
            return 'command not found',404

class Help(Resource):
    def show(self):
        return '''<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><body>
<table border=1>
  <tr><th>COMMAND</th><th>description<th></tr>
  <tr><td>request</td><td> POST JSON with job specification</td></tr>
  <tr><td>getfile/&lt;id&gt;</td><td> Download results as file</td></tr>
  <tr><td>control/list</td><td> list all jobs</td></tr>
  <tr><td>control/list?state=&lt;state&gt;</td><td> list jobs with state: {todo,running,done,error, all}</td></tr>
  <tr><td>control/show?id=&lt;id&gt;</td><td>show all information about job</td></tr>
  <tr><td>control/set?id=&lt;id&gt;&amp;state=&lt;state&gt;</td><td>set status</td></tr>
  <tr><td>control/version</td><td>show API version</td></tr>
</table>
</html></body>'''

    def get(self):
        return make_response(self.show(),200)

    def post(self):
        return make_response(self.show(),200)

app = Flask(__name__)
api = Api(app)

api.add_resource(Reqfile,"/daimon/request")
api.add_resource(Control,"/daimon/control/<cmd>")
api.add_resource(Getfile,"/daimon/getfile/<_id>")
api.add_resource(Help,"/daimon/help")
app.run(host=config.addr,port=config.port,debug=config.debug)

