import contexts
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

#2021.08.26
from evsim.system_simulator import SystemSimulator
from evsim.behavior_model_executor import BehaviorModelExecutor
from evsim.system_message import SysMessage
from evsim.definition import *

from telegram_model import TelegramModel as TM

import signal
import sys

import sys,os

'''
# Simulation Configuration


se.get_engine("sname").simulate()'''

class TelegramManager():
	def __init__(self, engine, tel_token):
		self.se = engine
		self.updater = Updater(tel_token)

		signal.signal(signal.SIGINT,  self.signal_handler)
		signal.signal(signal.SIGABRT, self.signal_handler)
		signal.signal(signal.SIGTERM, self.signal_handler)

		self.is_terminating = False

		model = TM(0, Infinite, "tm", "sname", self.updater)

		self.se.coupling_relation(None, "start", model, "start")
		self.se.coupling_relation(None, "msg", model, "msg")

		self.se.register_entity(model)

	def greet(self, update: Update, context: CallbackContext) -> None:
		"""Send a message when the command /start is issued."""
		user = update.effective_user
		update.message.reply_markdown_v2(
		    fr'Hi {user.mention_markdown_v2()}\!',
		    reply_markup=ForceReply(selective=True),
		)

	def update_freq(self, update: Update, context: CallbackContext) -> None:
		print(update.message.text)
		user = update.effective_user
		tokens = update.message.text.split(" ")
		#self.se.simulate()
		self.se.insert_external_event("msg", [float(tokens[1]), user.id])

	def start(self) -> None:
		"""Start the bot."""
		# Create the Updater and pass it your bot's token.

		# Get the dispatcher to register handlers
		dispatcher = self.updater.dispatcher

		# on different commands - answer in Telegram
		dispatcher.add_handler(CommandHandler("start", self.greet))
		dispatcher.add_handler(CommandHandler("update", self.update_freq))

		# Start the Bot
		self.updater.start_polling()

		self.se.insert_external_event("start", 'msg')
		self.se.simulate()

	def signal_handler(self, sig, frame):
		print("Terminating Monitoring System")
		
		if not self.is_terminating:
			self.is_terminating = True
			self.updater.stop()
			del self.se
		
		sys.exit(0)