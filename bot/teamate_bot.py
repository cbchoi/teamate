
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



def update_dataframe():
    #wks = doc.worksheet('timestamp','group_id','user_chatid','msg')
    df = pd.DataFrame('', index=[], columns=[])


'''
수정할 내용 : tean 별 시트 만들어기지, 날짜 인식, update_row 사용해서 시간 줄이기
=> 그래프 나오게 add_chart 사용

'''
def teamate_progress(update: Update, context: CallbackContext) -> None:
    starttext = "  반갑습니다 :) \n 팀 프로젝트 도우미 TEAMate 입니다😎\n\n"+"채팅방을 이용하지않고 프로젝트 진행 시 평가과정에서 불이익을 받을 수 있습니다.\n\n ❗️/help 를 입력하면 더 많은 설명을 들을 수 있습니다 :)❗️\n\n ❗️교수님의 공지도 챗봇을 통해 전달됩니다❗️"
    #context.bot.send_message(chat_id=-466802174,text=starttext)
    context.bot.send_message(chat_id=update.message.chat_id, text=starttext)

def help(update: Update, context: CallbackContext) -> None:
    helptext="teamate 봇은 다음과 같은 명령어들을 사용 가능합니다.\n/teamregist : 수업코드를 입력하여 팀을 등록합니다.\n/user_regist : 개인정보 등록\n/current_score : 현재 자신의 참여도를 상대적으로 알 수 있습니다."
    context.bot.send_message(chat_id=update.message.chat_id, text=helptext)

def current_score(update: Update, context: CallbackContext) -> None:
    
    #분석코드 작동 
    if update.message.chat_id < 0:
        print(update.message)
        context.bot.send_message(chat_id=update.message.chat_id, text="그룹채팅방에서는 사용할 수 없는 기능입니다. TEAMAtebot 을 친구추가 해주신후 다시 질문해주세요")
    else:
        context.bot.send_message(chat_id=update.message.chat_id,text=f"{update.effective_user.first_name}님의 참여도 색은 ___입니다.")


def collect_msg(update: Update, context: CallbackContext) -> None:

    

    print(update.message.text)

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




def main() -> None:
    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, collect_msg))

    dispatcher.add_handler(CommandHandler('teamate',teamate_progress))
    dispatcher.add_handler(CommandHandler('help',help))
    dispatcher.add_handler(CommandHandler('current_score',current_score))
    updater.start_polling()

    updater.idle()



if __name__ == '__main__':
    main()

