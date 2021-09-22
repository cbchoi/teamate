import contexts
# SIMULATION_MODE
SIMULATION_MODE = 'REAL_TIME'

# SIMULATION_MODEL
TIME_DENSITY= 1

ASSESSMENT_HOME_DIR = "STUDENTS_DIRECTORY"	

# Stores credential information
TELEGRAM_API_KEY='YOUR-TELEGRAM-BOT-KEY'

# Google Drive API, credentials
GOOGLE_SERVICE_KEY='YOUR-GOOGLE-SERVICE-KEY.json'

# Google Drive API, credentials
GOOGLE_SPREAD_SHEET='YOUR-GOOGLE-SPREADSHEET-NAME'


GIT_USER_ID = "" 
GIT_USER_PASSWORD = "" 

import os
if os.path.isfile("../instance/config.py"):
	from instance.config import *