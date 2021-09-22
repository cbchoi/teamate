import contexts
from config import *

from evsim.system_simulator import SystemSimulator
from evsim.behavior_model_executor import BehaviorModelExecutor
from evsim.system_message import SysMessage
from evsim.definition import *

from fetch import Fetch

# System Simulator Initialization
se = SystemSimulator()

model = Fetch(0, Infinite, "fetch", "sname")

se.register_engine("sname", SIMULATION_MODE, TIME_DENSITY)

se.get_engine("sname").insert_input_port("start")

se.get_engine("sname").coupling_relation(None, "start", model, "start")
se.get_engine("sname").register_entity(model)

se.get_engine("sname").insert_external_event("start", None)
se.get_engine("sname").simulate()