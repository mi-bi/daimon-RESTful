from subprocess import Popen, PIPE
import time
import json
import tempfile
from datetime import datetime, timedelta

Jobs = dict()

def Jobs_del(_jid):
    del(Jobs[str(_jid)])

def Jobs_expire():
    for j in Jobs:
        if Jobs[j].expired():
            Jobs_del(j)


class Launch(Popen):

    def __init__(self, _name, argjson):
        tmp_id = datetime.strftime(datetime.utcnow(), "%Y%m%d%H%M%S%f")
        while tmp_id in Jobs:
            tmp_id=str(int(tmp_id)+1)
        self._id=tmp_id
        self.name = _name
        self.jobid = self.name+self._id
        self.wdir = tempfile.TemporaryDirectory(prefix='daimon-')
        self.options = argjson
        self.properties = {'id':self._id,'state':'todo','token':self.wdir.name.split('daimon-')[1]}
        self.timestamp = datetime.utcnow()
        self.prepare()
        if 'arguments' not in self.options:
            self.options['arguments'] = ''
        if 'lifetime' in self.options:
            self.expire_period=timedelta(seconds=self.options['lifetime'])
        else:
            self.expire_period=timedelta(seconds=120*60)

        super().__init__([self.options['app'],self.options['arguments']],cwd=self.wdir.name, stdout=PIPE)
        Jobs.update({self._id: self})

    def prepare(self):
        with open(self.wdir.name+"/options.json", 'w') as fp:
            json.dump(self.options, fp)

    def ready(self):
        return self.poll() is not None

    def expired(self):
        ep=self.expire_period

        #if not self.downloaded:
         #   ep = timedelta(seconds=10) + timedelta(seconds=60*30)
        return datetime.utcnow() - self.timestamp > ep

    def get_path(self):
        return self.wdir.name

    def get_id(self):
        return self._id

    def __str__(self):
        return self._id


if __name__ == '__main__':
    args = {'app':'/home/skorka/PycharmProjects/daimon/jobexec.sh', 'id': 123,'lifetime':10, "data": {"x": 12334.423, "y": 745467.4, "z": -1234.3}}
    z = Launch('zero', args)
    Launch('raz', args)
    time.sleep(3)
    Launch('raz', args)
    Jobs_del(z)
    Launch('dwa', args)
    Launch('trzy', args)
    while len(Jobs) > 0:
        for p in list(Jobs):
            if Jobs[p].ready():
                print(Jobs[p].name)
                if Jobs[p].expired():
                    wdir = Jobs[p].get_path()
                    print(wdir)
                    Jobs_del(p)
        time.sleep(2)
