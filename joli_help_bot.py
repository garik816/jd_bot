#!/usr/bin/env python

### TODO:
#	
#	Dialogflow
#	heroku
#	перейти на вебхуки
#	будильник
#	

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from PIL import Image
import logging
import shutil
import os
import apiai, json

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
 
# токен полученный при регистрации бота
TOKEN = "796136257:AAGO7X5TcPCG38uxZQxSfePzkH5NT5I8o_s"
PORT = int(os.environ.get('PORT', '8443'))
#updater = Updater(token=TOKEN) # Токен API к Telegram
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

 
# start вызывается после команды /start
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Привет :)')
    bot.send_message(chat_id=update.message.chat_id, text='меня зовут JD\n'
	'Я умею отзеркаливать картинки\n'
	'Ещё со мной можно поговорить :)')
    user = update.message.from_user
    bot.send_message(chat_id=-365824280, text=user.first_name + ':\t' + '/start')
	
def joliWakeUpCommand(bot, update):
    bot.send_message(chat_id=664814569, text='доброе утро 😘')
    request = apiai.ApiAI('d478fb04da3e4d5c89711e31a59d7150').text_request() # Токен API к Dialogflow  # 'd478fb04da3e4d5c89711e31a59d7150'
    request.lang = 'ru' # На каком языке будет послан запрос # 'ru'
    request.session_id = 'BatlabAIBot' # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.query = 'порадуй меня' # Посылаем запрос к ИИ с сообщением от юзера
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
    bot.send_message(chat_id=664814569, text=response)
    user = update.message.from_user
    bot.send_message(chat_id=-365824280, text=user.first_name + ':\t' + request.query)
    bot.send_message(chat_id=-365824280, text='БОТ to ' + 'Joli: \t' + response)
	
def flip_image(image_path, saved_location):
    image_obj = Image.open(image_path)
    rotated_image = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
    rotated_image.save(saved_location)

def textMessage(bot, update):
    request = apiai.ApiAI('d478fb04da3e4d5c89711e31a59d7150').text_request() # Токен API к Dialogflow  # 'd478fb04da3e4d5c89711e31a59d7150'
    request.lang = 'ru' # На каком языке будет послан запрос # 'ru'
    request.session_id = 'BatlabAIBot' # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.query = update.message.text # Посылаем запрос к ИИ с сообщением от юзера
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
    user = update.message.from_user
    bot.send_message(chat_id=-365824280, text=user.first_name + ':\t' + request.query)
    bot.send_message(chat_id=-365824280, text='БОТ to ' + user.first_name + ':\t' + response)
    
    if response:
        bot.send_message(chat_id=update.message.chat_id, text=response) # Если есть ответ от бота - присылаем юзеру, 
    else:
        bot.send_message(chat_id=update.message.chat_id, text='я тугой, не понимаю') #если нет - бот его не понял
	
def flipEcho(bot, update):
    update.message.reply_text("отзеркаливаю...")
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join(os.getcwd(), '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    filename_tosend = filename.replace("\\","/")
    flip_image(filename_tosend,'flipped.jpg')
    user = update.message.from_user
    bot.send_photo(update.message.chat.id, photo=open('flipped.jpg', 'rb'))
    bot.send_message(chat_id=-365824280, text=user.first_name + ':\t' + 'flipp the imgage')
    bot.send_photo(chat_id=-365824280, photo=open('flipped.jpg', 'rb'))
    os.remove(filename_tosend)
    os.remove('flipped.jpg')
    update.message.reply_text("обращайся)")

updater.dispatcher.add_handler(CommandHandler('start', startCommand)) # регистрируем процедуру start как обработчик команды start
updater.dispatcher.add_handler(CommandHandler('joli', joliWakeUpCommand))
updater.dispatcher.add_handler(MessageHandler(Filters.text, textMessage)) # регистрируем процедуру textMessage как обработчик текстового сообщения (DialogflowAI)
updater.dispatcher.add_handler(MessageHandler(Filters.photo, flipEcho)) # echo + flip для картинок	
	
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.set_webhook("https://joli-help-bot.herokuapp.com/" + TOKEN)
updater.idle()	
	
	
#updater = Updater(TOKEN) # создаём основной объект для управления ботом
#updater.dispatcher.add_handler(CommandHandler('start', startCommand)) # регистрируем процедуру start как обработчик команды start
#updater.dispatcher.add_handler(CommandHandler('joli', joliWakeUpCommand))
#updater.dispatcher.add_handler(MessageHandler(Filters.text, textMessage)) # регистрируем процедуру textMessage как обработчик текстового сообщения (DialogflowAI)
#updater.dispatcher.add_handler(MessageHandler(Filters.photo, flipEcho)) # echo + flip для картинок
#updater.start_polling(clean=True) #updater.start_polling() # запускаем бота
#updater.idle()