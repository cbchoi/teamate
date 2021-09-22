from evsim.system_simulator import SystemSimulator
from evsim.behavior_model_executor import BehaviorModelExecutor
from evsim.system_message import SysMessage
from evsim.definition import *

import subprocess as sp
import os
import datetime
from config import ASSESSMENT_HOME_DIR as ahd
from config import *

class Fetch(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)

        # Open CSV
        self.init_state("IDLE")
        self.insert_state("IDLE", Infinite)
        self.insert_state("PROCESS", 1)

        self.insert_input_port("start")
        # (id, git_id)
        self.student_list = STUDENT_ROSTER
        self.working_repo = os.path.abspath(f"{ahd}/repositories/")
        self.working_asses = os.path.abspath(f"{ahd}/assessments/")

    def ext_trans(self,port, msg):
        if port == "start":
            self._cur_state = "PROCESS"

    def process_student(self, _id, _github):
        # cwd: {ahd}/repositories/
        # check exist
        #  - init: mkdir _id
        #          change directory _id
        #          cwd: {ahd}/repositories/{_id}
        #          git clone
        #  - change directory _github
        #          cwd:{ahd}/repositories/{_id}/{_github}
        #          git pull
        #          git log ...
        #          write to assessment directory {ahd}/assessments/{date}/{_id}
        #  - cd ..
        target_dir = f"{self.working_repo}/{_id}"
        if not os.path.exists(target_dir):
            os.makedirs(f"{self.working_repo}/{_id}")
            os.chdir(f"{self.working_repo}/{_id}")

            new_command = f"https://{GIT_USER_ID}:{GIT_USER_PASSWORD}@github.com/HBNU-COME1101/daily-{_github}"

            sp.run(["git", "clone", new_command])
            os.chdir(f"{self.working_repo}")

        else:
            os.chdir(f"{target_dir}/daily-{_github}")
            print(target_dir)
            check_date = datetime.datetime.now().strftime("%Y%m%d")
            print(f"Processing {_id}'s {check_date} commit logs")
            sp.run([ "git", "pull"])

            beforedate = datetime.datetime.now()
            afterdate = beforedate - datetime.timedelta(days=130)

            op_after = "--after='{0}'".format(afterdate.isoformat())
            op_before = "--before='{0}'".format(beforedate.isoformat())

            result = sp.run(['git', 'log', '--pretty=format:\'\"!!@@##%cn, %cd, %s\"\'',
            '--stat','-p', op_after, op_before], stdout=sp.PIPE)

            if not os.path.exists(f"{self.working_asses}/{check_date}"):
                os.makedirs(f"{self.working_asses}/{check_date}")

            f = open(f"{self.working_asses}/{check_date}/{_id}.log", "wb")
            f.write(result.stdout)
            f.close()

            os.chdir("..")
        pass

    def output(self):
        for _id, _github in self.student_list:
            self.process_student(_id, _github)

        return None
        
    def int_trans(self):
        self._cur_state = "PROCESS"