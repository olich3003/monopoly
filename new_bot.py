from config import *
from new_classes import *
import uuid

users = dict()
rooms = list()


def check_code(code):
    for room in rooms:
        s = (room.id == code)
        if room.id == code:
            return room
    return False


def check_players_number(n):
    if int(n) in range(2, 7):
        return True
    return False


def create_room(size, time, id, bot, admin):
    room = Room(int(size), time, id, bot)
    rooms.append(room)
    admin.cur_room = room
    room.users.append(admin)
    

def add_player_in_room(room, user):
    room.users.append(user)
    user.cur_room = room


async def start(update, context):
    current_user = update.effective_user.id
    chat_id = update.effective_chat.id
    if not (current_user in users.keys()): #если пользователь новый
        users[current_user] = User(None, None, chat_id)
        text = f"Привет! Как мне тебя называть?"
        context.chat_data['last'] = 'Поменять никнейм'
        context.chat_data['back'] = None
        await update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
    else: #если пользователь уже играл
        text = f"Привет, {users[current_user].name}!"
        keyboard = [["Поменять никнейм", "Подключиться к игре", "Создать новую игру"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        context.chat_data['last'] = None
        context.chat_data['back'] = None
        await update.message.reply_text(text=text, reply_markup=reply_markup)


async def text_handler(update, context):
    current_user = users[update.effective_user.id]
    if current_user.status == 'gaming':
        await game_text_handler(update, context)
        return
    user_messege = update.message.text
    last_user_messege = context.chat_data['last']
    back = context.chat_data['back']
    context.chat_data['back'] = None

    text = f""

    if user_messege == 'Назад':
        user_messege = back

    elif last_user_messege == 'Поменять никнейм':
        current_user.name = user_messege
        user_messege = 'Главное меню'

    elif last_user_messege == 'Подключиться к игре':
        room_for_user = check_code(user_messege)
        if room_for_user:
            context.user_data['room'] = room_for_user
            user_messege  = 'Подключение к комнате'
        else:
            text = "Неверный код\n"
            user_messege = last_user_messege

    elif last_user_messege == 'Создать новую игру':
        if check_players_number(user_messege):
            context.chat_data['back'] = last_user_messege
            context.user_data['n_of_players'] = user_messege
            text = "Введите время (в минутах), доступное на ход игрокам"
            keyboard = [["Назад"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            user_messege  = 'Создание комнаты'
        else:
            text = "Количество игроков может быть только от 2 до 6\n"
            user_messege = last_user_messege

    elif last_user_messege == 'Создание комнаты':
        context.user_data['move_time'] = user_messege
        room_id = str(uuid.uuid4())
        create_room(context.user_data['n_of_players'], context.user_data['move_time'], room_id, bot,  current_user)
        text = f"Вы успешно создали игровую комнату!\nКод для комнаты: `{room_id}`\nСообщи его друзьям, чтобы они могли подключиться к игре"
        keyboard = [["Удалить комнату"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        print(current_user.cur_room)
        await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')
        await current_user.cur_room.waiting_for_players(update, context)
        return

    ########################################################################################
    if user_messege == 'Главное меню':
        text = f"Хорошо, {current_user.name}, теперь выбери, что делать дальше"
        keyboard = [["Поменять никнейм", "Подключиться к игре", "Создать новую игру"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if user_messege == 'Поменять никнейм':
        context.chat_data['back'] = 'Главное меню'
        text = "Как мне тебя называть?"
        keyboard = [["Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if user_messege == 'Подключиться к игре':
        context.chat_data['back'] = 'Главное меню'
        current_user.status = 'player'
        text += "Введи код комнаты"
        keyboard = [["Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    if user_messege == 'Создать новую игру':
        context.chat_data['back'] = 'Главное меню'
        current_user.status = 'admin'
        text += "Введите количество игроков"
        keyboard = [[], [], ["Назад"]]
        for i in range (2, 7):
            if i < 5:
                keyboard[0].append(f"{i}")
            else:
                keyboard[1].append(f"{i}")
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if user_messege == 'Подключение к комнате':
        add_player_in_room(context.user_data['room'], current_user)
        text = f"Вы подключились к игровой комнате! Админ комнаты: {context.user_data['room'].users[0].name}"
        keyboard = [["Начать игру", "Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if user_messege == 'Начать игру':
        context.chat_data['last'] = user_messege
        room = current_user.cur_room
        if len(room.users) < room.size:
            await current_user.cur_room.waiting_for_players(update, context)
        else:
            await current_user.cur_room.get_field(update, context)
        return
    ##################################################

    context.chat_data['last'] = user_messege
    await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')



async def game_text_handler(update, context):
    global HOD
    current_user = users[update.effective_user.id]
    user_messege = update.message.text
    last_user_messege = context.chat_data['last']
    context.chat_data['back'] = None


    if context.chat_data['last'] == 'В тюрьме': #если игрок в тюрьме
        if user_messege == 'Остаться в тюрьме': 
            context.chat_data['last'] = user_messege
            await current_user.cur_room.step(update, context)
            return
        if user_messege == 'Использовать карточку': # выход из тюрьмы
            current_user.jail_free = False
        current_user.prisoner = False
        current_user.jail_doubles = False
        context.chat_data['last'] = 'Бросить кубики'
        await current_user.cur_room.update_message(update, context)
        return
    
    
    if context.chat_data['last'] == 'Купить дом':
        context.chat_data['last'] = user_messege
        await current_user.cur_room.buing_house(update, context, current_user)
        return
        

    if user_messege == 'Моё имущество':
        await current_user.cur_room.send_property(update, context, current_user)
        return
    
    if user_messege == 'Все карточки':
        await current_user.cur_room.send_cards(update, context, current_user)
        return
    
    if user_messege == 'Бросить кубики':
        context.chat_data['last'] = user_messege
        if DEBAG: # режим дебага
            current_user.last_dices_value = hods[HOD]
            current_user.cell = hods[HOD]
            HOD = HOD + 1
            if current_user.prisoner:
                context.chat_data['last'] = 'В тюрьме'
                current_user.jail_doubles = True
                current_user.jail_free = True
            if current_user.cell == 30: # если попал на поле "отправляйся в тюрьму"
                current_user.cur_room.put_in_jail(current_user, 'cell')
        else: # обычный режим
            dice_1 = await context.bot.send_dice(chat_id=current_user.chat_id)
            dice_2 = await context.bot.send_dice(chat_id=current_user.chat_id)
            current_user.last_dices_value = dice_1.dice.value + dice_2.dice.value
            current_user.cell += (dice_1.dice.value + dice_2.dice.value)

            if dice_1.dice.value == dice_2.dice.value: # если выпали дубли
                current_user.doubles += 1
            else:
                current_user.doubles = 0

            if current_user.doubles == 3: # если выкинул 3 дубля подряд
                current_user.cur_room.put_in_jail(current_user, 'doubles')

            if current_user.cell == 30: # если попал на поле "отправляйся в тюрьму"
                current_user.cur_room.put_in_jail(current_user, 'cell')

            if current_user.prisoner: # если игрок в тюрьме
                current_user.turns_in_prison += 1
                if dice_1.dice.value == dice_2.dice.value:
                    current_user.jail_doubles = True
                context.chat_data['last'] = 'В тюрьме'    
        if current_user.cell // 40 == 1:
            current_user.budget += 200
        current_user.cell = current_user.cell % 40
        await current_user.cur_room.update_message(update, context)
        return

    if user_messege in ['Купить', 'Не покупать', 'Заплатить ренту']:
        context.chat_data['last'] = user_messege
        await current_user.cur_room.update_message(update, context)
        return
    
    if user_messege == 'Открыть карточку':
        context.chat_data['last'] = user_messege
        await current_user.cur_room.update_message(update, context)
    
    if user_messege == 'Купить дом': # покупка дома
        context.chat_data['last'] = user_messege
        await current_user.cur_room.update_message(update, context)
        return

    if user_messege == 'Закончить ход':
        context.chat_data['last'] = user_messege
        await current_user.cur_room.step(update, context)
        return


bot.add_handler(CommandHandler('start', start))
bot.add_handler(MessageHandler(filters.TEXT, text_handler))
bot.run_polling()
