from asyncore import dispatcher
from telegram.ext import Updater
from io import BytesIO
import cv2
import numpy as np
import requests
import base64
import json
from argparse import ArgumentParser

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import MessageHandler, Filters
import logging
from datetime import datetime
from pathlib import Path

parser = ArgumentParser()
parser.add_argument("-l", "--log_dir", 
                    help="Log directory", required=True)

args = parser.parse_args()

def log_photo(photo, logdir):
    if  not Path(logdir).exists():
        Path(logdir).mkdir()
    now = datetime.now()
    print('saving to '+logdir+'/'+now.strftime('%Y/%m/%d %H:%M:%s')+'.jpg')
    with open(logdir+'/'+now.strftime('%Y_%m_%d_%H:%M:%s')+'.jpg', 'wb') as file:
        file.write(photo)
    

updater = Updater(token='5290610386:AAFze6y38D5QsIXHzpF_N2_JuGx4zYGyQV4', use_context=True)
dispatcher = updater.dispatcher


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Please send me any picture and I'll give you back picture with human body keypoints. Author: shil.d@yandex.ru")

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def photo_f(update: Update, context: CallbackContext):
    img_stream = BytesIO(context.bot.getFile(update.message.photo[-1].file_id).download_as_bytearray())
    img = cv2.imdecode(np.frombuffer(img_stream.read(), np.uint8), 1)
    string_img = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    req = {'img':string_img}
    context.bot.send_message(chat_id=update.effective_chat.id, text="I've got a photo from you. Please whait for a while. This bot is not optimised for inference speed.")
    r = requests.post('http://computer-vision-api.com/api/v1/pose_estimation', json=req)
    txt = json.loads(r.text)
    img = base64.b64decode(txt['img'].encode('utf-8'))
    log_photo(img, args.log_dir)
    context.bot.send_photo(update.effective_chat.id, photo=img)


photo_handler = MessageHandler(Filters.photo& (~Filters.command), photo_f)
dispatcher.add_handler(photo_handler)
