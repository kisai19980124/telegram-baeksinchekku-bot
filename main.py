import logging
import os
import random
import sys

from telegram.ext import Updater, CommandHandler
import telegram.ext
# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def callback_minute(context: telegram.ext.CallbackContext):

    context.bot.send_message(chat_id=SOMECHATID, text='One message every minute')

    
def main():
    u = Updater('TOKEN', use_context=True)
    j = u.job_queue
    job_minute = j.run_repeating(callback_minute, interval=60, first=0)
    u.start_polling()

main()