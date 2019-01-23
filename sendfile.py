#!/usr/bin/python3

from flask import Flask, send_file, request
from flask_restful import Api, Resource, reqparse

import launcher
import config

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
        out = {'request': 'POST JSON with job specification',
             'getfile/<id>': 'Download results as file',
             'control/list?state=<item>': 'show jobs with state item {todo,running,done,error}',
             'control/show?id=<id>:': 'show all information about job',
             'control/set': 'set status',
             'control/version': 'show API version'
             }
        return out

    def get(self):
        return self.show(),200

    def post(self):
        return self.show(),200

app = Flask(__name__)
api = Api(app)

api.add_resource(Reqfile,"/daimon/request")
api.add_resource(Control,"/daimon/control/<cmd>")
api.add_resource(Getfile,"/daimon/getfile/<_id>")
api.add_resource(Help,"/daimon/help")
app.run(host=config.addr,port=config.port,debug=config.debug)

