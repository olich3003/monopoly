from config import *
from new_classes import *
import uuid
import sqlite3 as sl
import os
from io import BytesIO

# Потом переделать на БД
users = dict()
rooms = list()


def create_bd():
    con = sl.connect('main_info.db')
    with con:
        data = con.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        existing_tables = [row[0] for row in data]
        print(existing_tables)
        if 'Users' not in existing_tables:
            con.execute(""" 
                CREATE TABLE Users (
                        id VARCHAR(200) PRIMARY KEY,
                        chat_id VARCHAR(200),
                        name VARCHAR(500), 
                        room_id VARCHAR(200), 
                        condition VARCHAR(200),
                        budget INTEGER, 
                        chip_type TEXT CHECK(chip_type IN ('ordinary', 'custom')),
                        chip_img BLOB, 
                        property TEXT,
                        property_img BLOB
                );
            """)
        if 'Rooms' not in existing_tables:
            con.execute("""
                CREATE TABLE Rooms (
                        id VARCHAR(200) PRIMARY KEY,
                        size INTEGER CHECK(size >= 2 AND size <= 6),
                        now_players INTEGER,
                        admin VARCHAR(200),
                        current_player INTEGER CHECK(current_player >= 0),
                        condition VARCHAR(200),
                        streets_type TEXT CHECK(streets_type IN ('ordinary', 'custom')),
                        FOREIGN KEY(admin) REFERENCES Users(id)
                )
            """)
    con.commit()



def print_all():
    # подключаемся к базе
    con = sl.connect('main_info.db')   
     # работаем с базой
    with con:
        # выполняем запрос к базе
        data = con.execute('SELECT * FROM Rooms')
        # перебираем все результаты
        for row in data:
            print("ROW:", row)
    print("ROOMS:", rooms)



async def start(update, context):
    create_bd()
    current_user = update.effective_user.id
    chat_id = update.effective_chat.id
    users[current_user] = User(None, None, chat_id)
    # создание и проверка пользователей через БД
    con = sl.connect('main_info.db')
    with con:
        existing_user = con.execute('SELECT * FROM Users WHERE id = :id;',{'id': current_user}).fetchone()
        if existing_user: # найден пользователь с текущим id 
            user_name = existing_user[2]
            if not user_name: # имя пользователя неизвесто
                text = f"Привет, напиши, пожалуйста, как мне тебя называть"
                context.chat_data['last'] = 'Поменять никнейм'
                context.chat_data['back'] = None
                await update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
            else: # имя пользователя известо
                users[current_user].name = user_name
                text = f"Привет, {user_name}!"
                keyboard = [["Поменять никнейм", "Выбрать игровую фишку"], ["Подключиться к игре", "Создать новую игру"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                context.chat_data['last'] = None
                context.chat_data['back'] = None
                await update.message.reply_text(text=text, reply_markup=reply_markup)
            con.commit()
        else: # пользователь новый
            insert_user_query = """
            INSERT INTO Users (id, chat_id, name, room_id, condition, custom_streets_number,
              custom_fields_number, budget, chip_type, chip_img, property, property_img)
            VALUES (?, ?, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
            """
            new_data = [(str(current_user), str(chat_id))]
            con.executemany(insert_user_query, new_data)
            text = f"Добро пожаловать в бота для игры в монополию! Для начала, напиши, пожалуйста, как мне тебя называть?"
            context.chat_data['last'] = 'Поменять никнейм'
            context.chat_data['back'] = None
            con.commit()
            insert_info_in_bd('Users', 'chip_type', 'ordinary', 'id', chat_id)
            await update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
        

                    
def check_code(code):
    for room in rooms:
        if room.id == code:            
            return room
    return False


def check_players_number(n):
    if int(n) in range(2, 7): 
        return True
    return False


def create_room(user_id, room_id, size, streets_type, bot):
    con = sl.connect('main_info.db')
    with con:
        insert_room_query = """
        INSERT INTO Rooms (id, size, now_players, admin, current_player, condition, streets_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        new_data = [(str(room_id), str(size), 1, str(user_id), 0, 'NULL', streets_type)]
        con.executemany(insert_room_query, new_data)
        con.commit()

    insert_info_in_bd('Users', 'condition', 'admin', 'id', user_id)
    insert_info_in_bd('Users', 'room_id', room_id, 'id', user_id)


def delete_room(room):
    room_id = room.id
    removed_room = None
    for room in rooms:
        if room.id == room_id:
            removed_room = room
            break
    if removed_room != None:
        for user in removed_room.users:
            user.cur_room = None
        rooms.remove(removed_room)

    con = sl.connect('main_info.db')
    cursor = con.cursor()
    query = """
    SELECT id FROM Users 
    WHERE room_id = ?
    """
    result = cursor.execute(query, (room_id,))
    data = result.fetchall()
    for row in data:
        user_id = row[0]
        insert_info_in_bd('Users', 'room_id', 'NULL', 'id', user_id)
        insert_info_in_bd('Users', 'condition', 'NULL', 'id', user_id)

    con = sl.connect('main_info.db')
    with con:
        query = """
        DELETE FROM Rooms 
        WHERE id = ?
        """
        con.execute(query, (room_id,))







def insert_info_in_bd(table, column, data, index, index_value):
    con = sl.connect('main_info.db')
    cursor = con.cursor()
    insert_query = f"""
        UPDATE {table}
        SET {column} = :data
        WHERE {index} = :id;
        """
    cursor.execute(insert_query, {'data':data, 'id':index_value})
    con.commit()

def insert_picture_in_bd(table, column, image_path, index, index_value):
    chip_image = Image.open(image_path)
    con = sl.connect('main_info.db')
    cursor = con.cursor()
    image_data = BytesIO()
    chip_image.save(image_data, format='PNG')
    image_data = image_data.getvalue()
    insert_query = f"""
        UPDATE {table}
        SET {column} = :img
        WHERE {index} = :id;
        """
    cursor.execute(insert_query, {'img':image_data, 'id':index_value})
    con.commit()

async def create_custom_chip(id, chip_file):
    photo_bytes = await chip_file.download_as_bytearray()
    with open(f'Users/user_{id}_photo.png', 'wb') as f:
        f.write(photo_bytes)
        f.close()
    image = Image.open(f'Users/user_{id}_photo.png')
    width, height = image.size
    size = min(width, height)
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    result = Image.new('RGB', (size, size))
    result.putalpha(mask)
    image =  image.crop(((width - size) // 2,
                         (height - size) // 2,
                         (width + size) // 2,
                         (height + size) // 2))
    result.paste(image, (0, 0), mask)
    result = result.resize((coef_y, coef_y))
    result.save(f'Users/user_{id}_chip.png', format='PNG')
    image.close()
    result.close()

    insert_picture_in_bd('Users', 'chip_img', f'Users/user_{id}_chip.png', 'id', id)
    os.remove(f'Users/user_{id}_photo.png')


def print_table(table, index, index_value):
    con = sl.connect('main_info.db')   
    with con:
        data = con.execute(f'SELECT chip_type FROM {table} WHERE {index} = :id;',{'id': index_value})
        for row in data:
            print(row)



async def image_handler(update, context):
    print("\n I'M IN IMAGE HANDLER\n")
    id = str(update.effective_user.id)
    current_user = users[update.effective_user.id]
    user_image = update.message.photo[-1]
    last_user_messege = context.chat_data['last']
    back = context.chat_data['back']

    if last_user_messege == 'Выбрать игровую фишку':
        insert_info_in_bd('Users', 'chip_type', 'custom', 'id', id)
        file = await context.bot.get_file(user_image.file_id)
        await create_custom_chip(id, file)
        context.chat_data['last'] = "Вернуться в главное меню"
        current_user.chip_type = 'custom'
    await text_handler(update, context)

async def send_txt_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    file_path = 'path_to_your_file.txt'
    
    # Отправляем файл
    await context.bot.send_document(
        chat_id=update.effective_user.id,
        document=open('OrdinaryFiles/streets.txt', 'rb'),
        filename=os.path.basename('OrdinaryFiles/streets.txt'),
        reply_to_message_id=update.message.message_id
    )


async def handle_document(update: Update, context: CallbackContext) -> None:
    id = str(update.effective_user.id)
    current_user = users[update.effective_user.id]
    document = update.message.document
    file = await document.get_file()
    file_path = os.path.join("Users/", document.file_name)
    await file.download_to_drive(file_path)



async def text_handler(update, context):
    current_user = users[update.effective_user.id]
    if current_user.status == 'gaming':
        await game_text_handler(update, context)
        return
    user_messege = update.message.text
    last_user_messege = context.chat_data['last']
    back = context.chat_data['back']
    context.chat_data['back'] = None
    id = str(update.effective_user.id)
    text = f""


    if user_messege == 'Назад':
        user_messege = back

    elif last_user_messege == "Вернуться в главное меню":
        user_messege = 'Главное меню'

    elif last_user_messege == 'Поменять никнейм':
        insert_info_in_bd('Users', 'name', user_messege, 'id', id)
        current_user.name = user_messege
        user_messege = 'Главное меню'

    elif last_user_messege == 'Подключиться к игре':
        room_for_user = check_code(user_messege)
        if not room_for_user:
            text = "Неверный код\n"
            user_messege = last_user_messege
        else:
            room_for_user.users.append(current_user)
            current_user.cur_room = room_for_user
            players_amount = len(room_for_user.users)
            insert_info_in_bd('Users', 'room_id', user_messege, 'id', id)
            insert_info_in_bd('Users', 'condition', 'player', 'id', id)
            insert_info_in_bd('Rooms', 'now_players', players_amount, 'id', user_messege)
            user_messege = 'Подключение к комнате'

    elif last_user_messege == 'Создать новую игру':
        if check_players_number(user_messege):
            context.user_data['n_of_players'] = user_messege
            text = f'Хотите поменять название полей и улиц, или сыграете в классическую версию монополии?'
            keyboard = [["Кастомизировать поле"], ["Классическая версия"]]
            context.chat_data['last'] = None
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')
            return
        else:
            text = "Количество игроков может быть только от 2 до 6\n" # пусть сообщения будут с привязкой к конфигу
            user_messege = last_user_messege

    ########################################################################################
    if user_messege == 'Стандартное поле':
        user_messege = 'Кастомизировать улицы'
    
    if user_messege ==  "Рандомный выбор":
        user_messege = 'Главное меню'
     
    if user_messege == "Кастомизировать поле":
        text = f"Хорошо, начнем с поля. Пришли мне основной цвет поля в формате RGB\n Вот так: (r, g, b)\n" \
                "Или нажми на кнопку 'Стандартное поле', если не хочешь менять его цвет"
        context.chat_data['back'] = 'Главное меню'
        keyboard = [['Стандартное поле'], ["Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if user_messege == 'Кастомизировать улицы':
        text = f"Я пришлю тебе шаблон текста, поменяй старые названия улиц и цветов на те, которые ты хочешь видеть на своем поле"
        keyboard = [['Передумал менять что-либо'], ["Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_user.id, text=text)
        await send_txt_file(update, context)
        context.chat_data['back'] = 'Главное меню'
        context.chat_data['last'] = 'Кастомизировать улицы'
        return
    

    if user_messege == "Удалить комнату":
        delete_room(current_user.cur_room)
        user_messege = 'Главное меню'

    if user_messege == "Классическая версия":
        room_id = str(uuid.uuid4())
        size = int(context.user_data['n_of_players'])
        streets_type = 'ordinary'
        create_room(id, room_id, size, streets_type, bot)

        room = Room(size, room_id, current_user, streets_type, bot)
        rooms.append(room)
        current_user.cur_room = room
        room.users.append(current_user)
        os.mkdir(f'Room_{room_id}')
        room.streets_file = 'OrdinaryFiles/streets.txt'

        text = f"Вы успешно создали игровую комнату!\nКод для комнаты: `{room_id}`\nСообщи его друзьям, чтобы они могли подключиться к игре\nОжидай подключения других игроков" 
        keyboard = [["Удалить комнату"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if user_messege == 'Главное меню':
        text = f"Хорошо, {current_user.name}, теперь выбери, что делать дальше"
        keyboard = [["Поменять никнейм","Выбрать игровую фишку"], ["Подключиться к игре", "Создать новую игру"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    if user_messege == 'Поменять никнейм':
        context.chat_data['back'] = 'Главное меню'
        text = "Как мне тебя называть?"
        keyboard = [["Назад"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)


    if user_messege == 'Выбрать игровую фишку':
        context.chat_data['back'] = 'Главное меню'
        text = f"Пришли мне картинку, из которой я сделаю тебе игровую фишку\n" \
               f"Можешь нажать на кнопку 'Рандомный выбор', тогда в начале игры" \
               " я назначу тебе одну из стандартных фишек"
        keyboard = [["Рандомный выбор"], ["Назад"]]
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
        context.chat_data['last'] = None
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
    first_word = user_messege.split()[0]
    context.chat_data['back'] = None


    if context.chat_data['last'] == 'В тюрьме': #если игрок в тюрьме
        if user_messege == 'Остаться в тюрьме': 
            context.chat_data['last'] = user_messege
            await current_user.cur_room.step(update, context)
            return
        if user_messege == 'Использовать карточку': # выход из тюрьмы
            current_user.jail_free = False
        current_user.prisoner = False
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
    if first_word == "Имущество":
        other_name = user_messege.split()[1]
        for user in current_user.cur_room.users:
            if user.name == other_name:
                await current_user.cur_room.send_other_property(update, context, current_user, user)
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
bot.add_handler(MessageHandler(filters.PHOTO, image_handler))
bot.add_handler(MessageHandler(filters.Document.FileExtension("txt"), handle_document))
while True:
    try:
        bot.run_polling()
    except:
        pass
#bot.run_polling() # запустить в бесконечном цикле с try/except, чтобы при ошибке был перезапуск
'''
Примерно
while True:
    try:
        bot.run_polling()
    except:
        pass
'''