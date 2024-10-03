from classes import *
from random import randint
    
all_users = dict()
all_rooms = list()

    


def delete_room(query):
    all_users[query.message.chat.id].score = 0
    room = all_users[query.message.chat.id].cur_room
    all_users[query.message.chat.id].cur_room = None
    room.users.remove(all_users[query.message.chat.id])
    print(len(room.users), all_users[query.message.chat.id].name)
    if len(room.users) == 0:
        all_rooms.remove(room)
    return

def spare_room():
    answer = False
    for room in all_rooms:
        if len(room.users) != ROOM_SIZE:
            answer = room
            break
    return answer

def ready_to_play(room):
    if len(room.users) == ROOM_SIZE:
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Подключиться", callback_data='go')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.effective_chat.id not in all_users:
        all_users[update.effective_chat.id] = User(update.effective_chat.id, update.effective_user.username)
    print(f"Игрок {update.effective_user.username} подключился")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Добрый день, {update.effective_user.username}',
                                    reply_markup=reply_markup)

async def button(update, context):
    query = update.callback_query
    await query.answer()
    all_users[query.message.chat.id].last_message = query.message.id
    if query.data == 'go':
        room = spare_room()
        if room == False:
            all_rooms.append(Room(bot))
            room = all_rooms[len(all_rooms) - 1]
        room.users.append(all_users[query.message.chat.id])
        all_users[query.message.chat.id].cur_room = room
        if len(room.users) != ROOM_SIZE:
            await query.edit_message_text(text=f"Ожидайте подключения второго игрока")
        else:
            await query.edit_message_text(text=f"Вы подключились к игровой комнате")
            await room.step(context)
    elif query.data == 'hod':
        all_users[query.message.chat.id].cur_room.step_timer.schedule_removal() #стоп таймер
        keyboard = [[InlineKeyboardButton("Закончить ход", callback_data='end_hod')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        score = randint(1, 6)
        all_users[query.message.chat.id].score += score
        await query.edit_message_text(text=f"Вaм выпало {score}", reply_markup=reply_markup)
    elif query.data == 'end_hod':
        await all_users[query.message.chat.id].cur_room.step(context)
    elif query.data == 'end_game':
        delete_room(query)
        keyboard = [[InlineKeyboardButton("Начать заново", callback_data='go')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Спасибо за игру!", reply_markup=reply_markup)
        print(all_rooms)


bot.add_handler(CommandHandler("start", start))
bot.add_handler(CallbackQueryHandler(button))
bot.run_polling()