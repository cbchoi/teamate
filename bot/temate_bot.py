
import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from pymongo import MongaoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def get_mgs(update: Update, context: CallbackContext) -> None:

    
    print(update.message.text)
    # print(update.message.from_user['first_name'])
    # print(update.message.chat.title)
    # print(update.message.date)
    # print(update.message.chat_id)
    # print(update.effective_user.id)
    print("fifi")
    TEAMateclient = MongoClient('mongodb://syhan:0220171631@127.0.0.1:27017/TM_db')
    TEAMateDB = TEAMateclient["TM_db"]
  
    #"groupname" : update.message.chat.title,
    #"username" :update.message.from_user['first_name'],
    TMchat_line = {"datetime" : update.message.date,
                    "group_id" : update.message.chat_id, 
                    "user_chatid" : update.effective_user.id,
                    "text": update.message.text
                }
    #print(TMchat_line)
    TMchat = TEAMateDB.TMchat
    TMchat.insert_one(TMchat_line)
    print("성공")

    


def start(update: Update, context: CallbackContext) -> None:
    starttext = "  반갑습니다 :) \n 팀 프로젝트 도우미 TEAMate 입니다😎\n\n"+"채팅방을 이용하지않고 프로젝트 진행 시 평가과정에서 불이익을 받을 수 있습니다.\n\n ❗️/help 를 입력하면 더 많은 설명을 들을 수 있습니다 :)❗️\n\n ❗️교수님의 공지도 챗봇을 통해 전달됩니다❗️"
    #context.bot.send_message(chat_id=-466802174,text=starttext)
    context.bot.send_message(chat_id=update.message.chat_id, text=starttext)
    #update.message.reply_text(starttext)
    print(update.message.text)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def question_command(update, context):
    context.bot.message.reply_text('질문~~!')
    context.bot.send_message(chat_id=update.message.chat_id, text="질문을 교수에게 모아서 전달?")


def TMtask_button(update, context):
    function_button = [[InlineKeyboardButton("공지 확인",callback_data=1),InlineKeyboardButton("일정 확인",callback_data=2)],[InlineKeyboardButton("학번등록(팀등록)",callback_data=3)]]
    
    reply_markup = InlineKeyboardMarkup(function_button)

    context.bot.send_message(
        chat_id = update.message.chat_id, text = "원하는 기능을 선택해주세요🧐",reply_markup=reply_markup
    )



def main() -> None:

    updater = Updater("")
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("question", question_command))
    
    #기능선택버튼
    dispatcher.add_handler(CommandHandler("task",TMtask_button))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, get_mgs))
    
    
    
    

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()