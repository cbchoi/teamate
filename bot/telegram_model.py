from evsim.system_simulator import SystemSimulator
from evsim.behavior_model_executor import BehaviorModelExecutor
from evsim.system_message import SysMessage
from evsim.definition import *

from config import *

class TelegramModel(BehaviorModelExecutor):
    def __init__(self, instance_time, destruct_time, name, engine_name, updater):
        BehaviorModelExecutor.__init__(self, instance_time, destruct_time, name, engine_name)
        self.init_state("IDLE")
        self.insert_state("IDLE", Infinite)
        self.insert_state("WAKE", 5)
  
        self.insert_input_port("msg")

        self.recv_msg = []
        self.updater = updater
         
    def ext_trans(self,port, msg):
        if port == "msg":
            print("[Model] Received Msg")
            self._cur_state = "WAKE"
            self.recv_msg.append(msg.retrieve()[0])
                        
    def output(self):
        if self._cur_state == "WAKE":
            print(self.recv_msg)
            for msg in self.recv_msg:
                self.updater.bot.send_message(msg[1], str(msg[0]))
            self.recv_msg = []
            pass

    def int_trans(self):
        if self._cur_state == "WAKE":
            self._cur_state = "IDLE"
    
    def __del__(self):
        pass