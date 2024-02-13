from config import *
from field import *
import re

all_others = {'treasury': 'ОБЩЕСТВЕННАЯ КАЗНА', 'tax': 'ПОДОХОДНЫЙ НАЛОГ', 'chance': 'ШАНС', 'super tax': 'СВЕРХНАЛОГ', 
              'prison': 'ТЮРЬМА', 'relax': 'БЕСПЛАТНАЯ СТОЯНКА', 'go to prison': 'ОТПРАВЛЯЙСЯ В ТЮРЬМУ'}

class Street:
    def __init__(self, data):
        self.group = data['group']
        self.name = data['name']
        self.cost = data['cost']
        self.house_cost = data['house_cost']
        self.collateral_value = data['collateral_value']
        self.rent = data['rent']
        self.current_rent = self.rent[0]
        self.current_owner = None
        self.houses = []

class Railway:
    def __init__(self, data):
        self.group = data['group']
        self.name = data['name']
        self.cost = data['cost']
        self.collateral_value = data['collateral_value']
        self.rent = data['rent']
        self.current_rent = self.rent[0]
        self.current_owner = None

class Utilities:
    def __init__(self, data):
        self.group = data['group']
        self.name = data['name']
        self.cost = data['cost']
        self.collateral_value = data['collateral_value']
        self.rent_counter = 4
        self.current_owner = None

class User:
    def __init__(self, name, room, chat_id):
        self.name = name
        self.cur_room = room
        self.status = None
        self.budget = 0
        self.chat_id = chat_id
        self.last_message_id = None
        self.last_dices_value = 0
        self.chip = None
        self.cell = 0
        self.property = []
        self.kits = []
        


class Room:
    def __init__(self, size, time, id, bot):
        self.users = list()
        self.size = size
        self.move_time = time
        self.id = id
        self.now_player = -1
        self.bot = bot
        self.file = 'streets.txt'
        self.field = 'field.png'
        self.field_with_chips = 'field_with_chips.png'
        self.all_streets = []

    def create_cards(self, file, all_streets):
        # Читаем содержимое файла
        with open(file, 'r', encoding='utf-8') as myfile:
            content = myfile.read()
        # Регулярное выражение для поиска двух последовательных пустых строк
        pattern = re.compile("\n\n")
        # Делим содержимое файла на блоки по пустым строкам
        blocks = pattern.split(content)
        for block in blocks:
            type = None
            card_data = {}
            block_lines = block.splitlines()
            for line in block_lines:
                words = line.split(": ")
                if words[0] == 'type':
                    type = words[1]
                elif words[0] == 'color':
                    pass
                elif words[0] in ['group', 'cost', 'house_cost', 'collateral_value']:
                    card_data[words[0]] = int(words[1])
                elif words[0] == 'rent':
                    card_data[words[0]] = list(map(int, words[1].split(", ")))
                else:
                    card_data[words[0]] = words[1]
            if type == 'street':
                all_streets.append(Street(card_data))
            elif type == 'railway':
                all_streets.append(Railway(card_data))
            else:
                all_streets.append(Utilities(card_data))


    async def get_field(self, update, context):
        im = Image.new('RGB', (field_width + 1, field_width + 1), field_color)
        draw = ImageDraw.Draw(im)
        draw_main_border(draw)
        draw_streets_borders(draw)
        draw_prison(draw)
        draw_streets_colors(draw)
        self.create_cards(self.file, self.all_streets)
        for i in range(len(field_number_and_cell)):
            field_card = field_number_and_cell[i]
            if i % 10 == 0:
                if i == 0:
                    continue
                angle =  90
                im = im.rotate(angle)
                draw = ImageDraw.Draw(im)
                continue
            if type(field_card) == int:
                street = self.all_streets[field_card]
                if field_card < 22:
                    x, y = calculate_coordinates_for_streets(i, 'street')
                else:
                    x, y = calculate_coordinates_for_streets(i, 'other')
                draw_streets_titles(draw, street.name, x, y)
            else:
                x, y = calculate_coordinates_for_streets(i, 'other')
                draw_streets_titles(draw, all_others[field_card], x, y)

        im = im.rotate(90, expand=True)
        draw = ImageDraw.Draw(im)
        im.save(f'field.png')
        await self.start_game(update, context)


    def generating_chips(self):
        chips_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (255, 140, 0), (255, 20, 147)]
        for i in range(len(self.users)):
            size = (coef_y, coef_y)
            img = Image.new('RGBA', size, (255,  255,  255,  0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([0,  0, coef_y - 1, coef_y - 1], fill=chips_colors[i])
            self.users[i].chip = f'chip_{i}.png'
            img.save(f'chip_{i}.png')

    def draw_chips_positions(self, image, field_number, chip_number):
        img = Image.open(image)
        side = field_number // 10
        i = 10 * (side + 1)
        img = img.rotate(90 * side)
        x = round((field_width * k + (i - 1 - field_number) * minifield_width) + coef + (chip_number % 2) * coef_x)
        y = round(round(field_width * (1 - k) + field_width * k * n) + coef + (chip_number // 2) * coef_y )
        x = x + (coef_x - coef_y) // 2
        y = y + (coef_y - coef_y) // 2
        chip = Image.open(self.users[chip_number].chip)
        mask = Image.new("L", chip.size,  0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((5,  5) + (coef_y - 5, coef_y - 5), fill=255)
        img.paste(chip, (x, y), mask)
        img = img.rotate(-90 * side)
        self.field_with_chips = f'field_with_chips.png'
        img.save(f'field_with_chips.png')

    async def waiting_for_players(self, update, context):
        for player in self.users:
            text = f"Ожидайте подключения других игроков\nСейчас в комнате находятся: "
            text += ', '.join([i.name for i in self.users])
            if player.last_message_id == None:
                message = await context.bot.send_message(chat_id=player.chat_id, text=text)
            else:
                message = await context.bot.edit_message_text(chat_id=player.chat_id, message_id=player.last_message_id, text=text)
            player.last_message_id = message.message_id

    async def start_game(self, update, context):
        self.now_player = (self.now_player + 1) % len(self.users)
        self.create_cards(self.file, self.all_streets)
        print(self.all_streets[22].rent, type(self.all_streets[22].rent))
        for i in self.all_streets[22].rent:
            print(i, type(i))
        self.generating_chips()
        self.draw_chips_positions(self.field, self.users[0].cell, 0)
        for i in range(1, len(self.users)):
            self.draw_chips_positions(self.field_with_chips, self.users[i].cell, i)
        for i, player in enumerate(self.users):
            player.budget = 1500
            if i != (len(self.users) - 1):
                await context.bot.delete_message(chat_id=player.chat_id, message_id=player.last_message_id)
            if i == self.now_player: #сейчас ход i-го игрока
                text = f"Цвет твоей фишки - {chips_colors[i]}\nСейчас твой ход"
                keyboard = [["Бросить кубики", "Имущество"], ["Информация о комнате", "Покинуть игру"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            else:
                text = f"Цвет твоей фишки - {chips_colors[i]}\nСейчас ход игрока {self.users[self.now_player].name}"
                keyboard = [["Имущество"], ["Информация о комнате", "Покинуть игру"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            message = await context.bot.send_photo(chat_id=player.chat_id, photo=open(self.field_with_chips, 'rb'), caption=text,
                                                   reply_markup=reply_markup)
            player.last_message_id = message.message_id
        

    def update_rent_for_others(self, street_n, player):
        if street_n < 26:
            streets_counter = -1
            streets_numbers = []
            for i in [22, 23, 24, 25]:
                street_owner = self.all_streets[street_n].current_owner
                if street_owner is player:
                    streets_counter += 1
                    streets_numbers.append(i)
            for i in streets_numbers:
                self.all_streets[i].current_rent = self.all_streets[street_n].rent[streets_counter]
        else:
            streets_counter = 0
            for i in [26, 27]:
                street_owner = self.all_streets[i].current_owner
                if street_owner is player:
                    streets_counter += 1
            if streets_counter == 2:
                for i in [26, 27]:
                    self.all_streets[i].rent_counter = 10

    def update_rent_for_streets(self, kit):
        for street in kit:
            houses_amount = len(self.all_streets[street].houses)
            if houses_amount == 0:
                self.all_streets[street].current_rent *= 2
            else:
                self.all_streets[street].current_rent = self.all_streets[street].rent[houses_amount]

    def update_kits(self, street_n, player):
        kit_of_current_street = streets_and_groups[street_n]
        all_streets_from_kit = group_and_streets[kit_of_current_street]
        for i in all_streets_from_kit:
            if i != street_n:
                if not (self.all_streets[i].current_owner is player):
                    return
        player.kits.append(kit_of_current_street)
        self.update_rent_for_streets(all_streets_from_kit)

    def property_purchase(self, street_n, buyer):
        if buyer.budget >= self.all_streets[street_n].cost:
            buyer.budget -= self.all_streets[street_n].cost
            self.all_streets[street_n].current_owner = buyer
            buyer.property.append(street_n)
            if street_n < 22:
                added_kit = self.update_kits(street_n, buyer)
                if added_kit != None:
                    self.update_rent(self, added_kit)
            else:
                self.update_rent_for_others(street_n, buyer)
        else:
            return False

    def calculate_rent(self, street_n, player):
        rent = 0
        if street_n < 26:
            rent = self.all_streets[street_n].current_rent
        else:
            rent = player.last_dices_value * self.all_streets[street_n].rent_counter
        return rent
    
    def generating_text_and_keyboard(self, last_users_action):
        text_cur, text_others = "", ""
        keyboard_cur, keyboard_others = [], []
        cell = self.users[self.now_player].cell
        street = field_number_and_cell[cell]
        if (street == 'go' and last_users_action == 'Начать игру') or last_users_action == 'Закончить ход':
            text_cur += f'Сейчас твой ход'
            keyboard_cur.append(["Бросить кубики"])
            text_others += f'Сейчас ход игрока {self.users[self.now_player].name}'
            keyboard_cur.append(["Имущество"])
        if last_users_action == 'Бросить кубики':
            if type(street) == int:
                street_owner = self.all_streets[street].current_owner
                street_name = self.all_streets[street].name
                if street_owner == None:
                    text_cur += f'Ты попал на поле {street_name} и оно свободно!\n' \
                                f'Хочешь купить его за {self.all_streets[street].cost}$?'
                    keyboard_cur.append(["Купить", "Не покупать"])
                    text_others += f'Сейчас ход игрока {self.users[self.now_player].name}\nОн попал на поле {street_name}'
                    keyboard_cur.append(["Имущество"])
                else:
                    rent = self.calculate_rent(street,  self.users[self.now_player])
                    if street_owner != self.users[self.now_player]:
                        text_cur += f'Ты попал на поле {street_name}, которое принадлежит игроку {street_owner.name}\n' \
                                    f'Ты должен заплатить ему {rent}$'
                        text_others += f'Сейчас ход игрока {self.users[self.now_player].name}\nОн попал на поле {street_name}'
                        keyboard_cur.append(["Заплатить ренту"])
                    else:
                        text_cur += f'Ты попал на поле {street_name}, которое принадлежит тебе\n'
                        text_others += f'Сейчас ход игрока {self.users[self.now_player].name}\nОн попал на поле {street_name}'
                        keyboard_cur.append(["Имущество"])
            else:
                text_cur += f'Ты попал на поле {all_others[street]}\n'
                text_others += f'Сейчас ход игрока {self.users[self.now_player].name}\nОн попал на поле {all_others[street]}'
                keyboard_cur.append(["Имущество", "Закончить ход"])

        elif last_users_action == 'Купить':
            purchase = self.property_purchase(street, self.users[self.now_player])
            if purchase == False:
                text_cur += f'Тебе не хватает денег для покупки поля {self.all_streets[street].name}'
                text_others += f'Сейчас ход игрока {self.users[self.now_player].name}\nОн попал на поле {self.all_streets[street].name}'
            else:
                text_cur += f'Ты приобрел поле {self.all_streets[street].name}!'
                text_others += f'Сейчас ход игрока {self.users[self.now_player].name}\nОн попал на поле {self.all_streets[street].name} и купил его'
            keyboard_cur.append(["Имущество", "Закончить ход"])

        elif last_users_action == 'Заплатить ренту':
            rent = self.calculate_rent(street,  self.users[self.now_player])
            self.users[self.now_player].budget -= rent
            self.all_streets[street].current_owner.budget += rent
            text_cur += f'Ты заплатил игроку {self.all_streets[street].current_owner.name} {rent}$'
            text_others += f'Сейчас ход игрока {self.users[self.now_player].name}\nОн попал на поле {self.all_streets[street].name} ' \
                            f'и заплатил игроку {self.all_streets[street].current_owner.name} {rent}$'
            keyboard_cur.append(["Имущество", "Закончить ход"])

        keyboard_cur.append(["Информация о комнате", "Покинуть игру"])
        keyboard_others.append(["Имущество"])
        keyboard_others.append(["Информация о комнате", "Покинуть игру"])          
        return text_cur, text_others, keyboard_cur, keyboard_others


    async def step(self, update, context):
        self.now_player = (self.now_player + 1) % len(self.users)
        await self.update_message(update, context)

    async def update_message(self, update, context):
        self.draw_chips_positions(self.field, self.users[0].cell, 0)
        for i in range(1, len(self.users)):
            self.draw_chips_positions(self.field_with_chips, self.users[i].cell, i)
        text_cur, text_others, keyboard_cur, keyboard_others = self.generating_text_and_keyboard(context.chat_data['last'])
        for i, player in enumerate(self.users):
            await context.bot.delete_message(chat_id=player.chat_id, message_id=player.last_message_id)
            if i == self.now_player: #сейчас ход i-го игрока
                text = f"Цвет твоей фишки - {chips_colors[i]}\nТвой бюджет - {self.users[i].budget}\n" + text_cur
                keyboard = keyboard_cur
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            else:
                text = f"Цвет твоей фишки - {chips_colors[i]}\nТвой бюджет - {self.users[i].budget}\n" + text_others
                keyboard = keyboard_others
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            message = await context.bot.send_photo(chat_id=player.chat_id, photo=open(self.field_with_chips, 'rb'), caption=text,
                                                reply_markup=reply_markup)
            player.last_message_id = message.message_id






    async def game_move(self, update, context):
        #если попали на улицу и она свободна
        text = f"Тебе выпало {context.chat_data['dice_1']} и {context.chat_data['dice_2']}"
        keyboard = [["Купить улицу", "Не покупать улицу"], ["Имущество"], ["Информация о комнате", "Покинуть игру"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(text=text, reply_markup=reply_markup)