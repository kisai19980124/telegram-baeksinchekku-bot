import logging
import os
import random
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram.ext
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
# Enabling logging
ssl._create_default_https_context = ssl._create_unverified_context
# URLの指定




                      
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

TOKEN = os.getenv("TOKEN")
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
SOMECHATID= os.getenv("SOMECHATID")
WAKUCHIN = os.getenv("WAKUCHIN")

PORT = int(os.environ.get('PORT', 8443))

# def callback_enable(update: Update, context: telegram.ext.CallbackContext):
    # job_minute.enabled = True
    
def callback_minute( context: telegram.ext.CallbackContext):
    try:
        html = urlopen(WAKUCHIN)
        bsObj = BeautifulSoup(html, "html.parser")
        #print(bsObj.findAll("table", {"class":"tbl--type1"}))
        table = bsObj.findAll("table", {"class":"tbl--type1"})[0]
        #print("table")
        tabledata = table.findAll("td")
        tablehead = table.findAll("th")
        
        try:
            if '満了' in tabledata[1].string:
                pass
            else:
                text1=tablehead[0].string+": \n"+"　"+tabledata[0].string+"\n"+tablehead[1].string+": \n"+"　"+tabledata[1].string
                context.bot.send_message(chat_id=SOMECHATID, text=text1)
                # context.
        except IndexError:
            pass
        try:
            if '満了' in tabledata[4].string:
                pass
            else:
                text2=tablehead[0].string+": \n"+"　"+tabledata[3].string+"\n"+tablehead[1].string+": \n"+"　"+tabledata[4].string
                context.bot.send_message(chat_id=SOMECHATID, text=text2)
        except IndexError:
            pass
        
    except:
        pass
        #    context.bot.send_message(chat_id=SOMECHATID, text='One message every minute')
    return

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('こんにちは！/check で東京大規模接種センターの予約数を確認できます．')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def check(update, context):
    try:
    
        # URLの指定
        html = urlopen(WAKUCHIN)
        bsObj = BeautifulSoup(html, "html.parser")

        # テーブルを指定
        table = bsObj.findAll("table", {"class":"tbl--type1"})[0]
        tabledata = table.findAll("td")
        tablehead = table.findAll("th")
        try:
            text1=tablehead[0].string+": \n"+"　"+tabledata[0].string+"\n"+tablehead[1].string+": \n"+"　"+tabledata[1].string
            update.message.reply_text(text1)
        except IndexError:
            print("日程が公開されていません．")
        try:
            text2=tablehead[0].string+": \n"+"　"+tabledata[3].string+"\n"+tablehead[1].string+": \n"+"　"+tabledata[4].string
            update.message.reply_text(text2)
        except IndexError:
            pass
    except:
        print("データを取得できませんでした．")
    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
def main():
    updater  = Updater(TOKEN, use_context=True, request_kwargs={'read_timeout': 8, 'connect_timeout': 10})
        # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("check", check))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
    
    j = updater .job_queue
    job_minute = j.run_repeating(callback_minute, interval=300, first=0)
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://"+HEROKU_APP_NAME+".herokuapp.com/" + TOKEN)
    updater.start_polling()
    updater.idle()

                      
if __name__ == '__main__':
    main()