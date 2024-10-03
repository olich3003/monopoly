from telegram import Update, Message
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton 
from telegram.ext import ApplicationBuilder, Application, ContextTypes, CallbackContext, filters
import sqlite3 as sl


TOKEN = '6824532109:AAHzoM0Jc3VCn5b87HsB6DV-3LFbVKbJs7g'
bot = ApplicationBuilder().token(TOKEN).build()
job = bot.job_queue
MAX_T = 60
PERIOD = 5
DEBAG = False
HOD = 0
hods = [30, 30, 30, 30, 30, 30]

field_number_and_cell = { 0: 'go', 1: 0, 2: 'treasury', 3: 1, 4: 'tax', 5: 22, 6: 2, 7: 'chance', 8: 3, 9: 4, 10: 'prison', 11: 5,
                12: 26, 13: 6, 14: 7, 15: 23, 16: 8, 17: 'treasury', 18: 9, 19: 10, 20: 'relax', 21: 11, 22: 'chance',
                23: 12, 24: 13, 25: 24, 26: 14, 27: 15, 28: 27, 29: 16, 30: 'go to prison', 31: 17, 32: 18, 33: 'treasury',
                34: 19, 35: 25, 36: 'chance', 37: 20, 38: 'super tax', 39: 21}

street_number_and_cell = {0: 1, 1: 3, 2: 6, 3: 8, 4: 9, 5: 11, 6: 13, 7: 14, 8: 16, 9: 18, 10: 19, 11: 21, 12: 23, 13: 24, 14: 26, 15: 27, 16: 29, 17: 31,
                          18: 32, 19: 34, 20: 37, 21: 39, 22: 5, 23: 15, 24: 25, 25: 35, 26: 12, 27: 28}

group_and_streets = [{0, 1}, {2, 3, 4}, {5, 6, 7}, {8, 9, 10}, {11, 12, 13}, {14, 15, 16}, {17, 18, 19}, {20, 21}, {22, 23, 24, 25}, {26, 27}]

streets_and_groups = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3, 11: 4, 12: 4, 13: 4, 16: 5, 14: 5, 15: 5,
                        17: 6, 18: 6, 19: 6, 20: 7, 21: 7, 24: 8, 25: 8, 22: 8, 23: 8, 26: 9, 27: 9}

############################ k * field_width - целочисленное, и field_width * (1 - 2 * k) должно делиться на 9
field_width = 1800
field_color = (202, 232, 224)
k = 0.11
n = 0.2
m = 0.15
l = 3
line_width = 3
border_width = 8
minifield_width = field_width // 9 * (1 - 2 * k)
minifield_colored_height = field_width * k * n
fill='black'

colors_top = [(255, 243, 1), (235, 55, 41)]
colors_bottom = [(190, 231, 249), (144, 68, 54)]
colors_left = [(247, 133, 44), (162, 50, 126)]
colors_right = [(54, 180, 96), (48, 129, 195)]
top = [0, 2, 3, 5, 6, 8]
bottom = [0, 1, 3, 6, 8]
left = [0, 1, 3, 5, 6, 8]
right = [0, 1, 3, 6, 8]
coef = round(line_width / 2)
coef_x = round(minifield_width / 2)
coef_y = round((field_width - (field_width - k * field_width * (1 - n))) / 3)
chips_colors_names = ['красный', 'желтый', 'зеленый', 'синий', 'оранжевый', 'розовый']
chips_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (255, 140, 0), (255, 20, 147)]

alpha = 0.1
card_height = round(field_width / (5 + 6 * alpha))
card_width = round(field_width * ((5 - alpha) / (6 * (5 + 6 * alpha))))
card_l = round(alpha * card_height)