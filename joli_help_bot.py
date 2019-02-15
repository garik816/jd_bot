#!/usr/bin/env python

### TODO:
#	Коллаж пусть делает
#	DialogflowAI
#	heroku online

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from PIL import Image
import logging
import shutil
import os
import apiai, json

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
 
# токен полученный при регистрации бота
telegram_token = '796136257:AAGO7X5TcPCG38uxZQxSfePzkH5NT5I8o_s'
updater = Updater(token=telegram_token) # Токен API к Telegram
dispatcher = updater.dispatcher

 
# start вызывается после команды /start
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Привет :)')
    bot.send_message(chat_id=update.message.chat_id, text='Я твой персональный помощник\n'
	'Просто отправь мне картинку\n'
	'Ещё со мной можно поговорить :)')
    user = update.message.from_user
    bot.send_message(chat_id=-365824280, text=user.first_name + ':\t' + '/start')
	
def flip_image(image_path, saved_location):
    image_obj = Image.open(image_path)
    rotated_image = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
    rotated_image.save(saved_location)

def textMessage(bot, update):
    request = apiai.ApiAI('d478fb04da3e4d5c89711e31a59d7150').text_request() # Токен API к Dialogflow
    request.lang = 'ru' # На каком языке будет послан запрос
    request.session_id = 'BatlabAIBot' # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.query = update.message.text # Посылаем запрос к ИИ с сообщением от юзера
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
    user = update.message.from_user
    bot.send_message(chat_id=-365824280, text=user.first_name + ':\t' + request.query)
    bot.send_message(chat_id=-365824280, text='БОТ: \t' + response)
    # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
    if response:
        bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        bot.send_message(chat_id=update.message.chat_id, text='я тугой, не понимаю')	
	
def flipEcho(bot, update):
    update.message.reply_text("отзеркаливаю...")
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join(os.getcwd(), '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
#    bot.send_message(update.message.chat.id, text=filename) # debug отправка сообщений!!!
    filename_tosend = filename.replace("\\","/")
#    bot.send_message(update.message.chat.id, text=filename_tosend) # debug
    flip_image(filename_tosend,'flipped.jpg')
    bot.send_photo(update.message.chat.id, photo=open('flipped.jpg', 'rb'))
    update.message.reply_text("обращайся)")

	
    if img_has_cat(filename):
        update.message.reply_text("if")
        new_filename = os.path.join('cats', '{}.jpg'.format(photo_file.file_id))
        os.rename(filename, new_filename)
    else:
        os.remove(filename)
        update.message.reply_text("else")	
 
# создаём основной объект для управления ботом
updater = Updater(telegram_token)
 
# регистрируем процедуру start как обработчик команды start
updater.dispatcher.add_handler(CommandHandler('start', startCommand))
 
# регистрируем процедуру textMessage как обработчик текстового сообщения (DialogflowAI)
updater.dispatcher.add_handler(MessageHandler(Filters.text, textMessage))

# echo + flip для картинок
updater.dispatcher.add_handler(MessageHandler(Filters.photo, flipEcho))
 
# запускаем бота
updater.start_polling(clean=True) #updater.start_polling()
updater.idle()