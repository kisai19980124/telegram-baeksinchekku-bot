import logging
import os
import random
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram.ext
from telegram import Update, Bot
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import threading
import json
from flask import Flask,request
from telegram.ext import Dispatcher
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
import telegram
from numba import jit
import numpy as np
from PIL import Image
import time
import configparser
from mag import handle_image
import requests
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
bot = telegram.Bot(TOKEN)
# def callback_enable(update: Update, context: telegram.ext.CallbackContext):
    # job_minute.enabled = True
emojis = "😂😘😍😊😁😔😄😭😒😳😜😉😃😢😝😱😡😏😞😅😚😌😀😋😆😐😕👍👌👿❤🖤💤🎵🔞"

give_up_time = 23

def random_emoji():
	return emojis[random.randint(0,len(emojis)-1)]


def isNum(char):
	return ord('0')<=ord(char) and ord(char) <= ord('9')

def findStickerNumInUrl(string):
	allSplit = string.split("/")
	temp = [i.split("?") for i in allSplit]
	for i in temp:
		allSplit += i

	print(allSplit)
	if string.find("sticonshop") == -1:
		for i in allSplit:
			ok = True

			for j in i:
				if not isNum(j):
					ok = False

			if ok and len(i)>0:
				return i

	for i in range(len(allSplit)):
		if allSplit[i] == "sticon":
			return allSplit[i+1]

		if allSplit[i] == "product":
			return allSplit[i+1]
		

	return -1

def getPack(sticker_number):
	a_len = -1
	a = 0
	try:
		a = bot.getStickerSet(name="line"+str(sticker_number)+"_by_RekcitsEnilbot")
		a_len = len(a.stickers)
	except:
		a_len=0

	return a_len, a

def main_handle(sticker_number,chat_id,main_message,all_stickers,title):

	if str(sticker_number) == "-1":
		print("no sticker number")
		bot.editMessageText(chat_id = chat_id,
						message_id = main_message,
						text = "沒有貼圖編號，無法建立貼圖包。\n\nThere isn't any sticker number so I can't create sticker pack.")
		return
	a_len, a = getPack(sticker_number)
	status = 0
	if a_len == 0:
		status = -1
	else:
		status = 1


	start_time = time.time()
	#threading.Timer(20,con_req,[sticker_number,chat_id,main_message,all_stickers,title]).start()
	#con_timer = threading.Timer(give_up_time,con_req,[sticker_number,chat_id,main_message,all_stickers,title])
	#con_timer.start()

	head_sticker=0
	temp_message = title+"\n發現"+str(len(all_stickers))+"張貼圖\n\nFound "+str(len(all_stickers))+" stickers\n"
	for i in range(a_len,len(all_stickers)):
		z = requests.get(all_stickers[i]).content
		open('temp'+str(i)+'.png', 'wb').write(z)
		img = Image.open('temp'+str(i)+'.png').convert('RGBA')
		arr = np.array(img)
		mag=512/max(len(arr[0]),len(arr))
		#new_arr = handle_image(mag,arr)
		#Image.fromarray(new_arr, 'RGBA').save("output"+str(i)+".png")
		img.resize((round(len(arr[0])*mag), round(len(arr)*mag)),Image.ANTIALIAS).save("output"+str(i)+".png")
		sticker = bot.uploadStickerFile(user_id = chat_id,
								png_sticker=open("output"+str(i)+".png", 'rb')).file_id
		rnd_emoji = random_emoji()
		if i==0 and status == -1:
			head_sticker = sticker
			print(sticker_number)
			print("line"+str(sticker_number)+"_by_RekcitsEnilbot")
			try:
				bot.createNewStickerSet(user_id=chat_id,
										name = "line"+str(sticker_number)+"_by_RekcitsEnilbot",
										title = title+" @RekcitsEnilbot",
										png_sticker = sticker,
										emojis = rnd_emoji)
			except:
				#con_timer.cancel()
				return
		else:
			a_len, a = getPack(sticker_number)
			if a_len != i:
				bot.deleteMessage(chat_id = chat_id,
				 					message_id = main_message)
				#con_timer.cancel()
				# bot.editMessageText(chat_id = chat_id,
				# 					message_id = main_message,
				# 					text = "出了點問題，具體來說是同時有兩個在上傳貼圖\n\nError:Multi thread is not available.")
				return 
			bot.addStickerToSet(user_id=chat_id,
								name = "line"+str(sticker_number)+"_by_RekcitsEnilbot",
								png_sticker = sticker,
								emojis = rnd_emoji)
		'''bot.sendDocument(chat_id = update.message.chat.id, 
						document = open("output"+str(i)+".png", 'rb'),
						caption = "")'''

		temp_message2 = temp_message
		for j in range(i+1):
			temp_message2 += "￭"
		for j in range(len(all_stickers)-i-1):
			temp_message2 += "_"
		temp_message2 += str(i+1)+"/" + str(len(all_stickers))
		try:
			bot.editMessageText(chat_id = chat_id,
						message_id = main_message,
						text = temp_message2)
		except:
			pass
		if time.time() - start_time > give_up_time:
			return
	#con_timer.cancel()
	bot.sendMessage(chat_id = chat_id,
						text = "噠啦～☆\n\nFinished!"+"\n\nLine sticker number:"+str(sticker_number)+"\nhttps://t.me/addstickers/line"+str(sticker_number)+"_by_RekcitsEnilbot")
	if head_sticker == 0:
		head_sticker = a.stickers[0].file_id

	bot.sendSticker(chat_id = chat_id,
					sticker = head_sticker,
					reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = title,url="https://t.me/addstickers/line"+str(sticker_number)+"_by_RekcitsEnilbot")]]))

	return 

def main_handle_for_message_sticker(sticker_number,chat_id,main_message,all_stickers,title):
	if str(sticker_number) == "-1":
		print("no sticker number")
		bot.editMessageText(chat_id = chat_id,
						message_id = main_message,
						text = "沒有貼圖編號，無法建立貼圖包。\n\nThere isn't any sticker number so I can't create sticker pack.")
		return

	a_len, a = getPack(sticker_number)
	status = 0
	if a_len == 0:
		status = -1
	else:
		status = 1

	start_time = time.time()
	#threading.Timer(20,con_req_for_massage_sticker,[sticker_number,chat_id,main_message,all_stickers,title]).start()
	#con_timer = threading.Timer(give_up_time,con_req_for_massage_sticker,[sticker_number,chat_id,main_message,all_stickers,title])
	#con_timer.start()

	head_sticker=0
	temp_message = title+"\n發現"+str(len(all_stickers))+"張貼圖\n\nFound "+str(len(all_stickers))+" stickers\n"
	for i in range(a_len,len(all_stickers)):
		z = requests.get(all_stickers[i][0]).content
		open('temp1'+str(i)+'.png', 'wb').write(z)
		img = Image.open('temp1'+str(i)+'.png').convert('RGBA')
		base = np.array(img)

		z = requests.get(all_stickers[i][1]).content
		open('temp2'+str(i)+'.png', 'wb').write(z)
		img = Image.open('temp2'+str(i)+'.png').convert('RGBA')
		text = np.array(img)

		for ii in range(len(base)):
			for jj in range(len(base[ii])):
				power = text[ii][jj][3]/255
				base[ii][jj] = base[ii][jj] * (1-power) + text[ii][jj] * power

		

		mag=512/max(len(base[0]),len(base))
		#new_arr = handle_image(mag,base)
		#Image.fromarray(new_arr, 'RGBA').save("output"+str(i)+".png")
		Image.fromarray(base, 'RGBA').resize((round(len(base[0])*mag), round(len(base)*mag)),Image.ANTIALIAS).save("output"+str(i)+".png")


		sticker = bot.uploadStickerFile(user_id = chat_id,
								png_sticker=open("output"+str(i)+".png", 'rb')).file_id
		rnd_emoji = random_emoji()
		if i==0 and status == -1:
			head_sticker = sticker
			bot.createNewStickerSet(user_id=chat_id,
									name = "line"+str(sticker_number)+"_by_RekcitsEnilbot",
									title = title+" @RekcitsEnilbot",
									png_sticker = sticker,
									emojis = rnd_emoji)
		else:
			a_len, a = getPack(sticker_number)
			if a_len != i:
				bot.deleteMessage(chat_id = chat_id,
				 					message_id = main_message)
				#con_timer.cancel()
				# bot.editMessageText(chat_id = chat_id,
				# 					message_id = main_message,
				# 					text = "出了點問題，具體來說是同時有兩個在上傳貼圖\n\nError:Multi thread is not available.")
				return 
			bot.addStickerToSet(user_id=chat_id,
								name = "line"+str(sticker_number)+"_by_RekcitsEnilbot",
								png_sticker = sticker,
								emojis = rnd_emoji)
		'''bot.sendDocument(chat_id = update.message.chat.id, 
						document = open("output"+str(i)+".png", 'rb'),
						caption = "")'''

		temp_message2 = temp_message
		for j in range(i+1):
			temp_message2 += "￭"
		for j in range(len(all_stickers)-i-1):
			temp_message2 += "_"
		temp_message2 += str(i+1)+"/" + str(len(all_stickers))
		try:
			bot.editMessageText(chat_id = chat_id,
						message_id = main_message,
						text = temp_message2)
		except:
			pass

		if time.time() - start_time > give_up_time:
			return
	#con_timer.cancel()
	bot.sendMessage(chat_id = chat_id,
						text = "噠啦～☆\n\nFinished!"+"\n\nLine sticker number:"+str(sticker_number)+"\nhttps://t.me/addstickers/line"+str(sticker_number)+"_by_RekcitsEnilbot")
	if head_sticker == 0:
		head_sticker = a.stickers[0].file_id

	bot.sendSticker(chat_id = chat_id,
					sticker = head_sticker,
					reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = title,url="https://t.me/addstickers/line"+str(sticker_number)+"_by_RekcitsEnilbot")]]))

	return 



def con_req(sticker_number,chat_id,main_message,all_stickers,title):
	a_len, a = getPack(sticker_number)
	if a_len < len(all_stickers):
		data={
			"sticker_number":sticker_number,
			"chat_id":chat_id,
			"main_message":main_message,
			"all_stickers":json.dumps(all_stickers),
			"title":title
		}
		requests.post("https://rekcits.herokuapp.com/continue",data=data)
		#requests.post("https://06775bc4b6d1.ngrok.io/continue",data=data)

	else:
		return



def con_req_for_massage_sticker(sticker_number,chat_id,main_message,all_stickers,title):
	a_len, a = getPack(sticker_number)
	if a_len < len(all_stickers):
		data={
			"sticker_number":sticker_number,
			"chat_id":chat_id,
			"main_message":main_message,
			"all_stickers":json.dumps(all_stickers),
			"title":title
		}
		requests.post("https://rekcits.herokuapp.com/continue2",data=data)
		#requests.post("https://06775bc4b6d1.ngrok.io/continue2",data=data)

	else:
		return


def continue_():
	all_data = request.form
	threading.Timer(0,main_handle,[all_data["sticker_number"],all_data["chat_id"],all_data["main_message"],json.loads(all_data["all_stickers"]),all_data["title"]]).start()
	return 'ok'

def continue2_():
	all_data = request.form
	threading.Timer(0,main_handle_for_message_sticker,[all_data["sticker_number"],all_data["chat_id"],all_data["main_message"],json.loads(all_data["all_stickers"]),all_data["title"]]).start()
	return 'ok'

def equalStr(a, b):
	if len(a)!=len(b):
		return False
	for i in range(len(a)):
		if a[i] != b[i]:
			return False
	return True

def aIsInb(a, b):
	for i in b:
		if equalStr(a,i):
			return True
	return False

def find_sticker_sites(text):
	all_sticker =  [""]
	x = text.find('"mdCMN09Image"')
	while x!=-1:
		#text = text[text[text.find('"mdCMN09Image"'):].find('https'):]
		text = text[text.find('"mdCMN09Image"'):]
		text = text[text.find('https'):]
		add = text[:text.find('.png')+4]
		all_sticker.append(add)
		x = text.find('"mdCMN09Image"')

	if len(all_sticker[1:]) == 0 and text.find('data-default-text') == -1:
		x = text.find('"mdCMN09Image FnCustomBase"')
		while x!=-1:
			#text = text[text[text.find('"mdCMN09Image"'):].find('https'):]
			text = text[text.find('"mdCMN09Image FnCustomBase"'):]
			text = text[text.find('https'):]
			add = text[:text.find('.png')+4]
			all_sticker.append(add)
			x = text.find('"mdCMN09Image FnCustomBase"')
	
	out = []

	for i in all_sticker[1:]:
		if not aIsInb(i, out):
			out.append(i)

	return out


def find_message_sticker_sites(text):
	all_sticker =  [[""]]
	x = text.find('"mdCMN09Li FnStickerPreviewItem"')
	while x!=-1:
		#text = text[text[text.find('"mdCMN09Image"'):].find('https'):]
		text = text[text.find('"mdCMN09Li FnStickerPreviewItem"'):]
		
		temp = []
		text = text[text.find('staticUrl'):]
		text = text[text.find('https'):]
		add = text[:text.find('.png')+4]
		temp.append(add)
		text = text[text.find('customOverlayUrl'):]
		text = text[text.find('https'):]
		add = text[:text.find('.png')+4]
		temp.append(add)

		all_sticker.append(temp)
		x = text.find('"mdCMN09Li FnStickerPreviewItem"')

	out = []

	for i in all_sticker[1:]:
		if not aIsInb(i, out):
			out.append(i)

	return out




def find_ex(string,key_string):
	return string[string.find(key_string):]
    
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
        print("error")
        pass
        #    context.bot.send_message(chat_id=SOMECHATID, text='One message every minute')
    return

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('こんにちは！/check で東京大規模接種センターの予約数を確認できます．')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

# def echo(update, context):
    # """Echo the user message."""
    # update.message.reply_text(update.message.text)
    
def webhook_handler():
	if request.method == "POST":
		update = telegram.Update.de_json(request.get_json(force=True), bot)
		dispatcher.process_update(update)
	return 'ok'
    
def reply_handler(update: Update, context: telegram.ext.CallbackContext):

	text = update.message.text

	main_message = bot.sendMessage(chat_id = update.message.chat.id,
						text = "正在試試看這東西\n\nTrying this.").message_id
	print(text)
	try:
		n = requests.get(text)
	except:
		bot.editMessageText(chat_id = update.message.chat.id,
							message_id = main_message,
							text = "無效網址\n\nInvalid URL")
		return
	#print(n.text)
	all_stickers = find_sticker_sites(n.text)

	if len(all_stickers)!=0:

		print(len(all_stickers))

		# temp = text.find("product")
		# if temp!=-1:
		# 	temp = text[temp+8:]
		# else:
		# 	temp = text.find("sticker")
		# 	temp = text[temp+8:]
		# sticker_number = temp[:temp.find("/")]
		sticker_number = findStickerNumInUrl(text)
		print(sticker_number)
		title = find_ex(find_ex(n.text,"head"),"title")[6:find_ex(find_ex(n.text,"head"),"title")[:].find("LINE")-2].replace("&amp;","&")

		#Check if sticker exist
		a_len, a = getPack(sticker_number)
		status = 0
		if a_len == 0:
			status = -1
		else:
			status = 1


		if status == 1:
			if len(a.stickers) != len(all_stickers):
				bot.editMessageText(chat_id = update.message.chat.id,
									message_id = main_message,
									text = "貼圖包更新\n\nUpdate the sticker set.")
			else:
				bot.editMessageText(chat_id = update.message.chat.id,
									message_id = main_message,
									text = "總算找到了\nThis one?!"+"\n\nLine sticker number:"+str(sticker_number))

				bot.sendSticker(chat_id = update.message.chat.id,
							sticker = a.stickers[0].file_id,
							reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = title,url="https://t.me/addstickers/"+"line"+str(sticker_number)+"_by_RekcitsEnilbot")]]))
				return

		temp_message = title+"\n發現"+str(len(all_stickers))+"張貼圖\n\nFound "+str(len(all_stickers))+" stickers\n"
		temp_message2 = temp_message
		for i in range(len(all_stickers)):
			temp_message2 += "_"
		temp_message2 += "0/" + str(len(all_stickers))
		bot.editMessageText(chat_id = update.message.chat.id,
							message_id = main_message,
							text = temp_message2)


		main_handle(sticker_number,update.message.chat.id,main_message,all_stickers,title)

	else:

		all_stickers = find_message_sticker_sites(n.text)
		#print(n.text)

		print(len(all_stickers))
		if len(all_stickers)==0:
			bot.editMessageText(chat_id = update.message.chat.id,
							message_id = main_message,
							text = "沒有找到任何Line貼圖？！\n\nCan't find any line sticker?!")
			return

		sticker_number = findStickerNumInUrl(text)

		print(sticker_number)

		title = find_ex(find_ex(n.text,"head"),"title")[6:find_ex(find_ex(n.text,"head"),"title")[:].find("LINE")-2].replace("&amp;","&")

		#Check if sticker exist
		a_len, a = getPack(sticker_number)
		status = 0
		if a_len == 0:
			status = -1
		else:
			status = 1

		if status == 1:
			if len(a.stickers) != len(all_stickers):
				bot.editMessageText(chat_id = update.message.chat.id,
									message_id = main_message,
									text = "貼圖包更新\n\nUpdate the sticker set.")
			else:
				bot.editMessageText(chat_id = update.message.chat.id,
									message_id = main_message,
									text = "總算找到了\nThis one?!"+"\n\nLine sticker number:"+str(sticker_number))

				bot.sendSticker(chat_id = update.message.chat.id,
							sticker = a.stickers[0].file_id,
							reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text = title,url="https://t.me/addstickers/"+"line"+str(sticker_number)+"_by_RekcitsEnilbot")]]))
				return

		temp_message = title+"\n發現"+str(len(all_stickers))+"張貼圖\n\nFound "+str(len(all_stickers))+" stickers\n"
		temp_message2 = temp_message
		for i in range(len(all_stickers)):
			temp_message2 += "_"
		temp_message2 += "0/" + str(len(all_stickers))
		bot.editMessageText(chat_id = update.message.chat.id,
							message_id = main_message,
							text = temp_message2)


		main_handle_for_message_sticker(sticker_number,update.message.chat.id,main_message,all_stickers,title)

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
    dp.add_handler(MessageHandler(Filters.text, reply_handler))

    # log all errors
    dp.add_error_handler(error)
    

    j = updater.job_queue
    job_minute = j.run_repeating(callback_minute, interval=3600, first=0)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url="https://"+HEROKU_APP_NAME+".herokuapp.com/" + TOKEN)
    updater.start_polling()
    updater.idle()

                      
if __name__ == '__main__':
    main()