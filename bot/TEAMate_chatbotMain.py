import logging
import re
import telegram
from telegram import Update, message ,Poll,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext,CommandHandler,CallbackQueryHandler,ConversationHandler
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

state_map = ["GET_STUDENT_ID", "GET_NEW_PWD", "ID_CHECKED", "HANDLE_SUMMARY_DETAIL", "DETAIL"]
logger = logging.getLogger(__name__)

#
def start_TM():
    pass

def build_box(buttons, n_cols,header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i+n_cols] for i in range(0,len(buttons),n_cols)]
    if header_buttons:
        menu.insert(0,header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)

    return menu


def whether_to_start(update: Update, context: CallbackContext) -> None:
    #if update.message.chat_id != Prof_id:
    if (update.effective_user.id != 1739915236): #or update.message.chat_id < 0:
        context.bot.send_message(chat_id=update.message.chat_id, text="교수자 권한 기능입니다.")
    else:
        show_list =[]
        show_list.append(InlineKeyboardButton("Yes",callback_data="peer_evaluation_yes"))
        show_list.append(InlineKeyboardButton("No",callback_data="peer_evaluation_no"))
        show_markup = InlineKeyboardMarkup(build_box(show_list,len(show_list)-1))
        update.message.reply_text("팀 프로젝트 참여자들 대상으로 동료평가를 시작하시겠습니까?",reply_markup=show_markup)



def callback_get(update: Update, context: CallbackContext) -> None:
    if update.callback_query.data == "peer_evaluation_yes":
        q = ['자신의 기여가 충분하다고 생각하시나요??','무임승차자가 있다고 생각하시나요?']
        answers = ['yes', 'no']
        context.bot.send_message(chat_id=1739915236, text="참여자들에게 동료평가를 시작합니다.")
        context.bot.send_poll(chat_id=1739915236, question=q[0], options=answers, type=Poll.REGULAR, open_period =15)
        context.bot.send_poll(chat_id=1739915236, question=q[1], options=answers, type=Poll.REGULAR, open_period =15)

    else:
        pass
#동료평가
#def peer_evaluation(update: Update, context: CallbackContext) -> None:
#    print("pear")
#    questions_list=[]
#    q = ['자신의 기여가 충분하다고 생각하시나요??','무임승차자가 있다고 생각하시나요?']
#    answers = ['yes', 'no']
#    context.bot.send_poll(chat_id=update.message.chat_id, question=q[1], options=answers, type=Poll.REGULAR, open_period =15)

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
    chat_data_df = wks.get_as_df()
    #print(stu_list_df)
    preprocessing_chat = re.sub('[.,;:\)*?!~`’^\-_+<>@\#$%&=#/(}※ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅎㅊㅋㅌㅍㅠㅜ]','', update.message.text)
    wks.update_value('A' + str(len(chat_data_df)+2), str(update.message.date))
    wks.update_value('B' + str(len(chat_data_df)+2), update.message.chat_id)
    wks.update_value('C' + str(len(chat_data_df)+2), update.effective_user.id)        
    wks.update_value('D' + str(len(chat_data_df)+2), preprocessing_chat)

def team_registration(update: Update, context: CallbackContext) -> None:
    gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
    sh = gc.open(GOOGLE_SPREAD_SHEET)
    wks = sh.worksheet('title','참여자 정보')
    stu_list_df = wks.get_as_df()
    #print(stu_list_df)

    show_list=[]
    show_list.append(InlineKeyboardButton("Yes",callback_data="peer_evaluation_yes"))
    show_list.append(InlineKeyboardButton("No",callback_data="peer_evaluation_no"))
    show_markup = InlineKeyboardMarkup(build_box(show_list,len(show_list)-1))
    update.message.reply_text("팀 프로젝트 참여자들 대상으로 동료평가를 시작하시겠습니까?",reply_markup=show_markup)
    wks.update_value('A' + str(len(stu_list_df)+2), str(update.message.date))
    wks.update_value('B' + str(len(stu_list_df)+2), update.message.chat_id)
    wks.update_value('C' + str(len(stu_list_df)+2), update.effective_user.id)        
    wks.update_value('D' + str(len(stu_list_df)+2), preprocessing_chat)

def handle_register_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("학번을 입력해주세요.")
    context.user_data['next_state'] = "GET_STUDENT_ID"
    return state_map[context.user_data['next_state']]

def check_valid_user(user_id:int) -> bool:
    
    gc = pygsheets.authorize(service_file=GOOGLE_SERVICE_KEY)
    sh = gc.open(GOOGLE_SPREAD_SHEET)
    wks = sh.worksheet('title','참여자 정보')
    df = wks.get_as_df()

    user_data = df.index[df['user_id'] == user_id].tolist()
    if user_data:
        return user_data[0]
    else:
        return -1

def handle_check_user(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
#    if (row := check_valid_user(user_id)) > 0:
# := 정의한다,,,?
    if (row := check_valid_user(user_id)) > 0:
        context.user_data['id'] = user_id        
        context.user_data['row'] = row + 2
        context.user_data['next_state'] = "ID_CHECKED"

        update.message.reply_text("비밀번호를 입력해주세요.")
        return state_map[context.user_data['next_state']]
    else:
        update.message.reply_text("수강신청 등록이 안된 사용자입니다.\n담당교수님께 확인하시길 바랍니다.")
        context.user_data.clear()
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    context.user_data.clear()
    update.message.reply_text("취소 되었습니다.")
    return ConversationHandler.END

def main() -> None:


    updater = Updater(TELEGRAM_API_KEY, use_context=True)
    
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, collect_msg))

    dispatcher.add_handler(CommandHandler('teamate',start_TM))
    dispatcher.add_handler(CommandHandler('current_score',current_score))
    #dispatcher.add_handler(PollHandler(peer_evaluation, pass_chat_data=True, pass_user_data=True))
    dispatcher.add_handler(CommandHandler("Start_peer_evaluation",whether_to_start))
    dispatcher.add_handler(ConversationHandler(
                                    entry_points=[CommandHandler('register', handle_register_start)],
                                    states={state_map["GET_STUDENT_ID"]:[CommandHandler(
                                    "check_register", handle_check_user),]},
                                    fallbacks=[CommandHandler('cancel', cancel)]))
    dispatcher.add_handler(CallbackQueryHandler(callback_get))
    
    #dispatcher.add_handler(CommandHandler("peer_evaluation",peer_evaluation))
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()

