import logging
import re
from telegram import Update, message
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext,CommandHandler, commandhandler
#import TM_analysis
import pygsheets
import pandas as pd

from config import *
from instance.config import *
#from oauth2client.service_account import ServiceAccountCredentials
# Enable logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#
def start_TM():
    pass

#동료평가
def peer_evaluation():
    pass


def current_score(update: Update, context: CallbackContext) -> None:
    #교수자와 학생들이 개인적으로 점수 확인할 수 있도록 group_id 를 가지고 있는 update.message가 입력되면 사용할 수 없다는 알림 메시지 작동
    if update.message.chat_id < 0:
        print(update.message)
        context.bot.send_message(chat_id=update.message.chat_id, text="그룹채팅방에서는 사용할 수 없는 기능입니다. TEAMAtebot 을 친구추가 해주신후 다시 질문해주세요")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,text=f"{update.effective_user.first_name}님의 참여도 색은 ___입니다.")

def collect_msg(update: Update, context: CallbackContext) -> None:

    gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
    sh = gc.open(GOOGLE_SPREAD_SHEET)
    wks = sh.worksheet('title','chat_data')
    stu_list_df = wks.get_as_df()
    #print(stu_list_df)
    preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', update.message.text)
    wks.update_value('A' + str(len(stu_list_df)+2), str(update.message.date))
    wks.update_value('B' + str(len(stu_list_df)+2), update.message.chat_id)
    wks.update_value('C' + str(len(stu_list_df)+2), update.effective_user.id)        
    wks.update_value('D' + str(len(stu_list_df)+2), preprocessing_chat)

def team_registration():
    pass

def main() -> None:
    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, collect_msg))

    dispatcher.add_handler(CommandHandler('teamate',start_TM))
    dispatcher.add_handler(CommandHandler('current_score',current_score))
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()

