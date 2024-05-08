from config import *
from field import *
import re
import random
import enum

all_others = {'go': 'ВПЕРЕД', 'treasury': 'ОБЩЕСТВЕННАЯ КАЗНА', 'tax': 'ПОДОХОДНЫЙ НАЛОГ', 'chance': 'ШАНС', 'super tax': 'СВЕРХНАЛОГ', 
              'prison': 'ТЮРЬМА', 'relax': 'БЕСПЛАТНАЯ СТОЯНКА', 'go to prison': 'ОТПРАВЛЯЙСЯ В ТЮРЬМУ'}



class SpecialCardType(enum.Enum):
    MOVE = 0
    GET = 1
    PAY = 2
    JAIL_FREE = 3
    NEAREST_RAILWAY = 4
    NEAREST_UTILITIES = 5
    REPAIR = 6
    GET_EVERYONE = 7
    PAY_EVERYONE = 8
    GO_BACK = 9
    GO_FORWARD = 10
    GO = 11
    PRISON = 12

class SpecialCard:
    def __init__(self, text, type, value):
        self.text = text
        self.type = type
        self.value = value


class SpecialCards:
    def __init__(self, all_streets):
        self.chance = list()
        self.treasury = list()
        self.image_types = {'get' : [SpecialCardType.GET, SpecialCardType.GET_EVERYONE],
                            'move' : [SpecialCardType.MOVE, SpecialCardType.NEAREST_RAILWAY, SpecialCardType.NEAREST_UTILITIES, SpecialCardType.GO, SpecialCardType.GO_BACK, SpecialCardType.GO_FORWARD],
                            'pay' : [SpecialCardType.PAY, SpecialCardType.PAY_EVERYONE],
                            'go_prison' : [SpecialCardType.PRISON],
                            'jail_free' : [SpecialCardType.JAIL_FREE],
                            'repair' : [SpecialCardType.REPAIR]}
        
        '''# все карточки move в шансе
        streets_len = len(all_streets)
        for street_n in random.sample(range(streets_len), 5):
            self.chance.append(SpecialCard(text=f'Отправляйтесь на поле {all_streets[street_n].name}',
                                           type=SpecialCardType.MOVE,
                                           value=street_number_and_cell[street_n]))
        # карточки get в шансе
        for sum in [50, 100]:
            texts = [f'Наступил срок исполнения платежа по вашей ссуде на строительство. Получите {sum}$',
                    f'Банк платит вам дивиденды в размере {sum}$']
            for text in texts:
                self.chance.append(SpecialCard(text=text,
                                               type=SpecialCardType.GET, 
                                               value=sum))
        # карточки pay в шансе
        for sum in [15, 30, 50]:
            texts = [f'Штраф за превышение скорости {sum}$']
            for text in texts:
                self.chance.append(SpecialCard(text=text,
                                               type=SpecialCardType.PAY, 
                                               value=sum))
                
        # карточки get в казне
        for sum in [10, 25, 50, 100, 200]:
            texts = [f'Банковская ошибка в вашу пользу. Получите {sum}$',
                    f'Вы заняли второе место на конкурсе красоты. Получите {sum}$',
                    f'Наступил срок исполнения платежа по страхованию жизни. Получите {sum}$', 
                    f'Наступил срок исполнения платежа по отпускному фонду. Получите {sum}$', 
                    f'На продаже акций вы зарабатываете {sum}$', 
                    f'Возмещение подоходного налога. Получите {sum}$', 
                    f'Получите {sum}$ за консалтинговые услуги', 
                    f'Вы получаете в наследство {sum}$']
            for text in random.sample(texts, 2):
                self.treasury.append(SpecialCard(text=text,
                                               type=SpecialCardType.GET, 
                                               value=sum))
                
        # карточки pay в казне
        for sum in [50, 100]:
            texts = [f'Визит к врачу. Заплатите {sum}$',
                    f'Оплатите расходы на госпитализацию в размере {sum}$',
                    f'Оплатите обучение в размере {sum}$']
            for text in random.sample(texts, 2):
                self.treasury.append(SpecialCard(text=text,
                                               type=SpecialCardType.PAY, 
                                               value=sum))
                
        # карточка освобождения из тюрьмы в казне и шансе
        self.chance.append(SpecialCard(text='Бесплатное освобождение из тюрьмы',
                                       type=SpecialCardType.JAIL_FREE,
                                       value=None))
        self.treasury.append(SpecialCard(text='Бесплатное освобождение из тюрьмы',
                                         type=SpecialCardType.JAIL_FREE,
                                         value=None))
        
        # ближайшая ж/д и коммунальное предприятие в шансе
        text = 'Идите на ближайшее поле коммунального предприятия.\n' \
               'Если оно находится в собственности, бросьте кубики и заплатите владельцу сумму, ' \
               'в 10 раз превышающую сумму выпавших очков'
        self.chance.append(SpecialCard(text=text,
                                       type=SpecialCardType.NEAREST_UTILITIES,
                                       value=None))
        
        text = 'Идите на ближайшую ж/д станцию.\n' \
               'Если она находится в собственности, заплатите владельцу арендную плату, ' \
               'вдвое превышающую обычную'
        self.chance.append(SpecialCard(text=text,
                                       type=SpecialCardType.NEAREST_RAILWAY,
                                       value=None))
        
        # карточки repair в шансе и казне
        text = 'Подошло время капитального ремонта всей вашей собственности:\n' \
               'заплатите за каждый дом по 25$,\nзаплатите за каждый отель по 100$'
        self.chance.append(SpecialCard(text=text,
                                       type=SpecialCardType.REPAIR,
                                       value=(25, 100)))
        
        text = 'От вас требуется провести ремонтные уличные работы:\n' \
               '40$ за каждый дом,\n115$ за каждый отель'
        self.treasury.append(SpecialCard(text=text,
                                       type=SpecialCardType.REPAIR,
                                       value=(40, 115)))
        
        # карточки get_everyone в казне
        text = 'Сегодня ваш день рождения. Получите по 10$ от каждого игрока'
        self.treasury.append(SpecialCard(text=text,
                                       type=SpecialCardType.GET_EVERYONE,
                                       value=10))

        # карточки pay_everyone в шансе
        text = 'Вас избрали председателем совета директоров. Заплатите каждому игроку по 50$'
        self.treasury.append(SpecialCard(text=text,
                                       type=SpecialCardType.PAY_EVERYONE,
                                       value=50))

        # карточки go_back в шансе
        for step in [2, 3, 4]:
            text = f'Вернитесь на {step} шага назад'
            self.chance.append(SpecialCard(text=text,
                                           type=SpecialCardType.GO_BACK,
                                           value=step))
            
        # карточки go_forward в шансе
        for step in [5, 6, 7, 8]:
            text = f'Перейдите на {step} шагов вперед'
            self.chance.append(SpecialCard(text=text,
                                           type=SpecialCardType.GO_FORWARD,
                                           value=step))'''

        # карточки prison в шансе и казне
        text = 'Отправляйтесь в тюрьму. Не проходите поле "ВПЕРЕД" и не получайте 200$'
        self.chance.append(SpecialCard(text=text,
                                       type=SpecialCardType.PRISON,
                                       value=None))
        self.treasury.append(SpecialCard(text=text,
                                         type=SpecialCardType.PRISON,
                                         value=None))

        # карточки go в шансе и казне
        text = 'Идите на поле "ВПЕРЕД". Получите 200$'
        self.chance.append(SpecialCard(text=text,
                                       type=SpecialCardType.GO,
                                       value=200))
        self.treasury.append(SpecialCard(text=text,
                                         type=SpecialCardType.GO,
                                         value=200))
        

    def get_image_type(self, card):
        for image_type, value in self.image_types.items():
            if card.type in value:
                return image_type 
            
    def draw_special_card(self, img, card_type, card=None):
        image = Image.open(img)
        draw = ImageDraw.Draw(image)
        rec_coef = 1.6
        rec_h = 0.2
        x_0 = 0.5 * field_width - 0.5 * rec_coef * rec_h * field_width
        y_0 = 0.5 * field_width - 0.5 * rec_h * field_width
        x_1 = 0.5 * field_width + 0.5 * rec_coef * rec_h * field_width
        y_1 = 0.5 * field_width + 0.5 * rec_h * field_width
        colors = {'chance' : (254, 134, 43), 'treasury' : (81, 207, 255)}
        titles = {'chance' : 'ШАНС', 'treasury' : 'ОБЩЕСТВЕННАЯ КАЗНА'}

        if not card: # отрисовка рубашки карточки
            draw.rectangle([(x_0, y_0), (x_1, y_1)], outline=(0, 0, 0), fill=colors[card_type], width=5)
            picture = Image.open(f'pictures/{card_type}_card.png')
            size = round(0.15 * field_width)
            picture = picture.resize((size, size))

            width, height = picture.size
            x = round((x_0 + x_1) // 2)
            y = round((y_0 + y_1) // 2)
            image.paste(picture, (x - width // 2, y - height // 2), picture)
        else: # отрисовка лицевой стороны карточки
            draw.rectangle([(x_0, y_0), (x_1, y_1)],outline=(0,0,0), width=5, fill='white')
            small_rec_shift = 0.009 * field_width
            draw.rectangle([(x_0 + small_rec_shift, y_0 + small_rec_shift), (x_1 - small_rec_shift, y_1 - small_rec_shift)],
                            outline=(0, 0, 0), fill='white', width=3)
            
            # отрисовка названия карточки
            font = ImageFont.truetype('draw/Cygre_Blank.ttf', 33)
            color = 'black'
            left, top, right, bottom = draw.multiline_textbbox((0, 0), text=titles[card_type], font=font)
            title_width = right - left
            title_height = bottom - top
            x = round((x_0 + x_1) // 2)
            y = round(y_0 + 2 * small_rec_shift)
            draw.text((x - (title_width // 2), y), titles[card_type], font=font, align='center', fill=color)

            # отрисовка текста карочки

            content_split = 0.7
            content_width = x_1 - x_0 - 5 * small_rec_shift
            content_height = y_1 - y_0 - title_height - 5 * small_rec_shift
            x_0_text = x_0 + 2 * small_rec_shift
            y_0_text = y_0 + 3 * small_rec_shift + title_height
            x_1_text = x_0 + 2 * small_rec_shift + content_width * content_split
            y_1_text = y_0 + 3 * small_rec_shift + title_height + content_height
            font = ImageFont.truetype('draw/Cygre.ttf', 26)
            max_chars_per_line = 20
            wrapped_text = textwrap.wrap(card.text, width=max_chars_per_line)
            formatted_text = "\n".join(wrapped_text)
            left, top, right, bottom = draw.multiline_textbbox((0, 0), text=formatted_text, font=font)
            text_width = right - left
            text_height = bottom - top
            x = x_0_text + (x_1_text - x_0_text - text_width) // 2
            y = y_0_text + (y_1_text - y_0_text - text_height) // 2
            draw.text((x, y), formatted_text, font=font, align='center', fill=color)

            # отрисовка изображения карточки
            x_0_img = x_0_text + content_width * content_split + small_rec_shift
            y_0_img = y_0_text
            x_1_img = x_1 - 2 * small_rec_shift
            y_1_img = y_1_text
            image_type = self.get_image_type(card)
            card_image = Image.open(f'pictures/{image_type}.png')
            size = round(x_1_img - x_0_img)
            card_image = card_image.resize((size, size))
            x = x_0_img + (x_1_img - x_0_img - size) // 2
            y = y_0_img + (y_1_img - y_0_img - size) // 2
            image.paste(card_image, (round(x), round(y)), card_image)
        image.save(img)


    def generate_special_card(self, user, card_type):
        if card_type == 'chance':
            card = random.choice(self.chance)
        else:
            card = random.choice(self.treasury)
        user.special_card = (card, card_type)
        print(card.type, '\n\n',  card.text)

    def processing_user(self, user):
        print('FUNC processing_user')
        card = user.special_card[0]
        if card.type == SpecialCardType.MOVE: # тип карты перейти на поле ...
            if user.cell >= card.value:
                user.budget += 200
            user.cell = card.value

        elif card.type == SpecialCardType.GET: # получи
            user.budget += card.value

        elif card.type == SpecialCardType.PAY: # заплати
            user.budget -= card.value

        elif card.type == SpecialCardType.JAIL_FREE: # бесплатный выход из тюрьмы
            user.jail_free += 1

        elif card.type == SpecialCardType.NEAREST_RAILWAY: # ближайшая ж/д
            new_cell = 5
            for i in [5, 15, 25, 35]:
                if i > user.cell:
                    new_cell = i
                    break
            if user.cell >= new_cell:
                user.budget += 200
            user.cell = new_cell

        elif card.type == SpecialCardType.NEAREST_UTILITIES: # ближайшее коммунальное
            new_cell = 12
            for i in [12, 28]:
                if i > user.cell:
                    new_cell = i
                    break
            if user.cell >= new_cell:
                user.budget += 200
            user.cell = new_cell
        
        elif card.type == SpecialCardType.REPAIR: # ремонтные работы
            total_sum = user.houses_amount * card.value[0] + user.hotels_amount * card.value[1]
            user.budget -= total_sum
        
        elif card.type == SpecialCardType.PAY_EVERYONE: # заплати каждому
            players_amount = len(user.cur_room.users) - 1
            user.budget -= players_amount * card.value
            for player in user.cur_room.users:
                if player != user:
                    player.budget += card.value

        elif card.type == SpecialCardType.GET_EVERYONE: # получи от каждого
            players_amount = len(user.cur_room.users) - 1
            user.budget += players_amount * card.value
            for player in user.cur_room.users:
                if player != user:
                    player.budget -= card.value

        elif card.type == SpecialCardType.GO_BACK: # иди назад на ... шагов
            new_cell = user.cell - card.value
            user.cell = new_cell

        elif card.type == SpecialCardType.GO_FORWARD: # иди вперед на ... шагов
            new_cell = user.cell + card.value
            if user.cell >= new_cell:
                user.budget += 200
            user.cell = new_cell
        
        elif card.type == SpecialCardType.GO: # иди на поле "вперед"
            user.cell = 0
            user.budget += 200

        elif card.type == SpecialCardType.PRISON: # отправляйся в тюрьму
            user.prisoner = True
            user.cell = 10

        
        
        



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
        self.houses = 0
        self.color = data['color']


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
        self.chip_color = None
        self.cell = 0
        self.property = []
        self.kits = []
        self.houses_amount = 0
        self.hotels_amount = 0
        self.doubles = 0
        self.prisoner = False
        self.turns_in_prison = 0
        self.jail_free = 0
        self.jail_doubles = False
        self.jail_reason = ''
        self.special_card = None
        

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
        self.cards = 'all_cards.png'
        self.all_streets = []
        self.special_cards = None
        self.image_items_list = []
        self.output_image = 'field_output.png'

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
                    color_list = words[1].replace('(', '').replace(')', '').split(',')
                    color_tuple = tuple(int(i) for i in color_list)
                    card_data[words[0]] = color_tuple
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
            #print(all_streets, len(all_streets))
        self.special_cards = SpecialCards(all_streets)


    async def get_field(self, update, context):
        im = Image.new('RGBA', (field_width + 1, field_width + 1), field_color)
        im = draw_special_cells(im)
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
                    x, y = calculate_coordinates_for_pictures(i)
                    draw_cells_pictures(im, int(x), int(y), i)
                    continue
                angle =  90
                im = im.rotate(angle)
                draw = ImageDraw.Draw(im)
                x, y = calculate_coordinates_for_pictures(i)
                draw_cells_pictures(im, int(x), int(y), i)
                continue
            if type(field_card) == int:
                street = self.all_streets[field_card]
                if field_card < 22:
                    x, y = calculate_coordinates_for_streets(i, 'street')
                else:
                    x, y = calculate_coordinates_for_streets(i, 'other')
                draw_streets_titles(draw, street.name, x, y)
                x, y = calculate_coordinates_for_costs(i)
                draw_streets_costs(draw, str(street.cost) + '$', x, y)
            else:
                x, y = calculate_coordinates_for_streets(i, 'other')
                draw_streets_titles(draw, all_others[field_card], x, y)
            x, y = calculate_coordinates_for_pictures(i)
            draw_cells_pictures(im, int(x), int(y), i)
        im = im.rotate(90, expand=True)
        draw = ImageDraw.Draw(im)
        im.save(f'field.png')
        await self.start_game(update, context)


    def generating_chips(self):
        for i in range(len(self.users)):
            size = (coef_y, coef_y)
            img = Image.new('RGBA', size, (255,  255,  255,  0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([0,  0, coef_y - 1, coef_y - 1], fill=chips_colors[i])
            self.users[i].chip = f'chip_{i}.png'
            self.users[i].chip_color = chips_colors[i]
            img.save(f'chip_{i}.png')


    def draw_houses(self, image, street_number, type, house_img, number):
        img = Image.open(image)
        side = street_number_and_cell[street_number] // 10
        i = 10 * (side + 1)
        img = img.rotate(90 * side)
        x_1 = round(field_width * k + (i - 1 - street_number_and_cell[street_number]) * minifield_width)
        x_2 = (field_width * k + (i - street_number_and_cell[street_number]) * minifield_width)
        y_1 = round(field_width * (1 - k))
        y_2 = round(field_width * (1 - k) + field_width * k * n)

        if type == 'house':
            width, height = round((x_2 - x_1) // 4), round((x_2 - x_1) // 4)
            x_1 += width * number
            picture = Image.open(house_img)
        else:
            height = round(y_2 - y_1)
            picture = Image.open(house_img)
            width_old, height_old = picture.size
            width = round((width_old * height) / height_old)
            x_1 = round((x_1 + x_2) // 2 - width // 2)
        picture = picture.resize((width, height))
        img.paste(picture, (x_1, y_1), picture)
        img = img.rotate(-90 * side)
        img.save(f'f_with_house.png')
        img.show()


    def draw_chip(self, img, x, y, user):
        chip = Image.open(user.chip)
        mask = Image.new("L", chip.size,  0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((5,  5, coef_y - 5, coef_y - 5), fill=255)

        outline_image = Image.new("RGBA", (chip.width, chip.height), (0, 0, 0, 0))
        outline_draw = ImageDraw.Draw(outline_image)
        outline_draw.ellipse((5, 5, coef_y - 5, coef_y - 5), outline='black', width=4)
        chip_with_outline = Image.alpha_composite(chip.convert('RGBA'), outline_image)

        img.paste(chip_with_outline, (x, y), mask)


    def draw_chips_in_prison(self, img, chips_list):
        chip = Image.open(f'chip_0.png')
        side = 1
        i = 10 * (side + 1)
        img = img.rotate(90 * side)
        prisoners_list = [chip for chip in chips_list if chip.prisoner]
        free_chips_list = [chip for chip in chips_list if not chip.prisoner]
        if len(prisoners_list) != 0:
            prison_height = field_width * (2 / 3) * k
            prison_coef = 0.2
            x_0 = field_width * (1 - k) + prison_height * prison_coef - chip.width // 2 + coef
            y_0 = field_width * (1 - k) - chip.width // 2 + coef
            x_len = prison_height * (1 - prison_coef) + chip.width - 3 * coef
            y_len = prison_height + chip.width - 3 * coef
            chips_count = len(prisoners_list)
            num_lines = (chips_count - 1) // 3 + 1
            x_list = [x_0 + (i * x_len) / (num_lines + 1) for i in range(1, num_lines + 1)]
            if num_lines == 1:
                y_list = [[y_0 + (i * y_len) / (chips_count + 1) for i in range(1, chips_count + 1)]]
            else:
                y_list = [[y_0 + (i * y_len) / (chips_count // 2 + chips_count % 2 + 1) for i in range(1, chips_count // 2 + chips_count % 2 + 1)],
                        [y_0 + (i * y_len) / (1 + chips_count // 2) for i in range(1, 1 + chips_count // 2)]]
            counter = 0
            for line in range(num_lines):
                x = round(x_list[line])
                for y in y_list[line]:
                    y = round(y)
                    self.draw_chip(img, x - chip.width // 2, y - chip.width // 2, prisoners_list[counter])
                    counter += 1
        if len(free_chips_list) != 0:
            l = chip.width + field_width * (5/3) * k
            coords = [(i * l / (len(free_chips_list) + 1) - chip.width // 2) for i in range(1, len(free_chips_list) + 1)]
            for i, coord in enumerate(coords):
                if coord < field_width * (5/6) * k:
                    x = field_width * (1 - k) + coord - chip.width // 2
                    y = field_width * (1 - (1/6) * k) - chip.width // 2
                else:
                    y = field_width * (1 - (1 / 6) * k) - (coord - (5 / 6) * k * field_width) - chip.width // 2
                    x = field_width * (1 - (1/6) * k) - chip.width // 2
                x = round(x)
                y = round(y)
                self.draw_chip(img, x, y, free_chips_list[i])
        img = img.rotate(-90 * side)
        return img


    def draw_chips_positions(self, image, positions, output_image):
        #print('FUNCTION draw_chips_positions')
        img = Image.open(image)
        chip = Image.open(f'chip_0.png')
        chip_width = chip.width
        chip.close()

        for field_number, chips_list in positions.items():
            if field_number == 10:# обработка поля "тюрьма"
                img = self.draw_chips_in_prison(img, chips_list)
                continue

            #поворот поля
            side = field_number // 10
            i = 10 * (side + 1)
            img = img.rotate(90 * side)
                
            #коэффициенты для границ отрисовки фишек
            coef_chips_field_bottom = 0.15
            coef_chips_field_top = 0.25
            minifield_height = field_width * k - minifield_colored_height
            
            if field_number % 10 == 0: # обработка угловых полей
                x_0 = round((field_width * k + (i - 1 - field_number) * minifield_width) + coef - chip_width // 2 + coef_chips_field_bottom * field_width * k)
                y_0 = round(field_width * (1 - k) + coef - chip_width // 2 + coef_chips_field_bottom * field_width * k)
                x_len = field_width * k - 2 * coef + chip_width - coef_chips_field_bottom * field_width * k
                y_len = field_width * k - 2 * coef + chip_width - coef_chips_field_bottom * field_width * k
            else: # обработка обычных полей
                x_0 = round((field_width * k + (i - 1 - field_number) * minifield_width) + coef - chip_width // 2)
                y_0 = round(round(field_width * (1 - k) + field_width * k * n) + coef +
                            minifield_height * coef_chips_field_top - chip_width // 2)
                x_len = minifield_width - 2 * coef + chip_width
                y_len = minifield_height * (1- coef_chips_field_bottom - coef_chips_field_top) - 2 * coef + chip_width
            
            chips_count = len(chips_list)
            num_lines = (chips_count - 1) // 3 + 1
            y_list = [y_0 + (i * y_len) / (num_lines + 1) for i in range(1, num_lines + 1)]
            if num_lines == 1:
                x_list = [[x_0 + (i * x_len) / (chips_count + 1) for i in range(1, chips_count + 1)]]
            else:
                x_list = [[x_0 + (i * x_len) / (chips_count // 2 + chips_count % 2 + 1) for i in range(1, chips_count // 2 + chips_count % 2 + 1)],
                        [x_0 + (i * x_len) / (1 + chips_count // 2) for i in range(1, 1 + chips_count // 2)]]
        
            counter = 0
            for line in range(num_lines):
                y = round(y_list[line])
                for x in x_list[line]:
                    x = round(x)
                    #print(chips_list[counter])
                    self.draw_chip(img, x - chip.width // 2, y - chip.width // 2, chips_list[counter])
                    counter += 1
            
            img = img.rotate(-90 * side)
        img.save(output_image)


    def create_cards_images(self):
        im = Image.new('RGB', (field_width + 1, field_width + 1), field_color)
        draw = ImageDraw.Draw(im)
        create_cards_img(draw, len(self.all_streets))
        #print(self.all_streets, len(self.all_streets))
        for i in range(len(self.all_streets)):
            street = self.all_streets[i]
            x_1, x_2, y_1, y_2 = calculate_coord_for_cards(i)
            if i < 22:
                new_y_1 = draw_cards_titles(draw, street.name, x_1, x_2, y_1, y_2, 'street', street.color)
                draw_card_info(draw, street.rent, street.house_cost, street.collateral_value,
                                x_1, x_2, new_y_1, y_2, 'street')
            else:
                new_y_1 = draw_cards_titles(draw, street.name, x_1, x_2, y_1, y_2,'other', None)
                if i < 26:
                    draw_card_info(draw, street.rent, None, street.collateral_value, 
                                x_1, x_2, new_y_1, y_2, 'railway')
                else:
                    draw_card_info(draw, None, None, street.collateral_value, 
                                x_1, x_2, new_y_1, y_2, 'utilities')
        im.save(f'all_cards.png')

    def draw_propetry(self, image, street_number, player):
        img = Image.open(image)
        side = street_number_and_cell[street_number] // 10
        i = 10 * (side + 1)
        img = img.rotate(90 * side)
        draw = ImageDraw.Draw(img)
        x_1 = (field_width * k + (i - 1 - street_number_and_cell[street_number]) * minifield_width) + minifield_width // 7
        x_2 = (field_width * k + (i - street_number_and_cell[street_number]) * minifield_width) - minifield_width // 7
        y_1 = field_width * (1 - k) - 2 * minifield_colored_height // 4
        y_2 = field_width * (1 - k)
        draw.rectangle([(x_1 + coef, y_1 + coef), (x_2 - coef, y_2 - coef)], fill=player.chip_color,
                        outline=(0, 0, 0, 128), width=1)
        img = img.rotate(-90 * side)
        img.save(f'field.png')

    async def waiting_for_players(self, update, context):
        print('WAITING FOR PLAYERS')
        print(self.users)
        for player in self.users:
            print(player.last_message_id)
            text = f"Ожидайте подключения других игроков\nСейчас в комнате находятся: "
            text += ', '.join([i.name for i in self.users])
            if player.last_message_id == None:
                message = await context.bot.send_message(chat_id=player.chat_id, text=text)
            else:
                message = await context.bot.edit_message_text(chat_id=player.chat_id, message_id=player.last_message_id, text=text)
            player.last_message_id = message.message_id

    async def start_game(self, update, context):
        self.now_player = (self.now_player + 1) % len(self.users)
        self.generating_chips()
        self.create_cards_images()
        self.generate_image()
        for i, player in enumerate(self.users):
            player.status = 'gaming'
            player.budget = 1500
            if i != (len(self.users) - 1):
                await context.bot.delete_message(chat_id=player.chat_id, message_id=player.last_message_id)
            if i == self.now_player: #сейчас ход i-го игрока
                text = f"Цвет твоей фишки - {chips_colors_names[i]}\nТвой бюджет - {self.users[i].budget}$\nСейчас твой ход"
                keyboard = [["Бросить кубики", "Моё имущество"], ["Все карточки"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            else:
                text = f"Цвет твоей фишки - {chips_colors_names[i]}\nТвой бюджет - {self.users[i].budget}$\nСейчас ход игрока {self.users[self.now_player].name}"
                keyboard = [["Моё имущество"], ["Все карточки"]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            message = await context.bot.send_photo(chat_id=player.chat_id, photo=open(self.output_image, 'rb'), caption=text,
                                                   reply_markup=reply_markup)
            player.last_message_id = message.message_id
        

    def update_rent_for_others(self, street_n, player):
        if street_n < 26:
            streets_counter = -1
            streets_numbers = []
            for i in [22, 23, 24, 25]:
                street_owner = self.all_streets[i].current_owner
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
        if buyer.budget >= self.all_streets[street_n].cost: # если бюджета игрока хватает на покупку улицы
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
        #print(street_n, self.all_streets[street_n].name, self.all_streets[street_n].current_rent)
        rent = 0
        if street_n < 26:
            rent = self.all_streets[street_n].current_rent
        else:
            rent = player.last_dices_value * self.all_streets[street_n].rent_counter
        return rent

    
    def put_in_jail(self, player, reason):
        player.jail_reason = reason
        player.prisoner = True
        player.cell = 10
        return

    def jail_turns(self):
        ans = ''
        if self.users[self.now_player].turns_in_prison == 3:
            ans = 'end'
        elif self.users[self.now_player].jail_free:
            ans = 'free'
            if self.users[self.now_player].jail_doubles:
                ans = 'both'
        elif self.users[self.now_player].jail_doubles:
            ans = 'doubles'
        return ans


    '''
    def generate_prison_text(self, last_users_action):
        text_cur, text_others = "", ""
        condition = self.jail_turns()
        if condition == 'both':
            text_cur += f'Ты сейчас в тюрьме\nУ тебя есть бесплатный выход, а еще тебе выпали дубли!\n' \
                        f'Выбери,'
    '''

    def processing_other_fields(self, street, current_user, text, keyboard):
        #print('DEF processing_other_fields')
        if street == 'tax':
            current_user.budget -= 200
            text += 'Ты заплатил 200$\n'
            keyboard.append(['Закончить ход'])
        elif street == 'super tax':
            current_user.budget -= 100
            text += 'Ты заплатил 100$\n'
            keyboard.append(['Закончить ход'])
        elif street == 'treasury' or street == 'chance':
            self.image_items_list.append(('card_shirt', street))
            self.special_cards.generate_special_card(current_user, street)
            keyboard.append(['Открыть карточку'])
        return text
    

    def check_move_type(self, type):
        ans = False
        if type is SpecialCardType.MOVE:
            ans = True
        #elif type == SpecialCardType.NEAREST_RAILWAY:
            #ans = True
        #elif type == SpecialCardType.NEAREST_UTILITIES:
            #ans = True
        elif type == SpecialCardType.GO_BACK:
            ans = True
        elif type == SpecialCardType.GO_FORWARD:
            ans = True
        elif type == SpecialCardType.GO:
            ans = True
        elif type == SpecialCardType.PRISON:
            ans = True
        return ans
        


    def generating_text_and_keyboard(self, last_users_action):
        text_cur, text_others = "", ""
        keyboard_cur, keyboard_others = [], []
        current_user = self.users[self.now_player]

        if last_users_action == 'Открыть карточку':
            self.special_cards.processing_user(current_user)
            self.image_items_list.append(('front_card_side', current_user.special_card))
            print(current_user.special_card[0].type)
            if self.check_move_type(current_user.special_card[0].type):
                last_users_action = 'Бросить кубики'
                print('type is move')
            elif current_user.special_card[0].type == SpecialCardType.NEAREST_UTILITIES:
                keyboard_cur.append(['Бросить кубики'])
            else:
                keyboard_cur.append(["Моё имущество"])
                keyboard_cur.append(['Закончить ход'])
        cell = self.users[self.now_player].cell
        street = field_number_and_cell[cell]
        print(cell, last_users_action)

        if (street == 'go' and last_users_action == 'Начать игру') or last_users_action == 'Закончить ход':
            text_cur += f'Сейчас твой ход'
            keyboard_cur.append(["Бросить кубики"])
            text_others += f'Сейчас ход игрока {current_user.name}'
            keyboard_cur.append(["Моё имущество"])

        if last_users_action == 'В тюрьме': # обработка тюрьмы
            condition = self.jail_turns()
            if condition == 'both':
                text_cur += f'Ты сейчас в тюрьме, но у тебя есть бесплатный выход, а еще тебе выпали дубли\n' \
                            f'Ты можешь выйти из тюрьмы благодаря дублям, или использовать карточку "выход из тюрьмы"'
                keyboard_cur.append(["Использовать карточку", "Выйти по дублям", "Отсаться в тюрьме"])
                text_others += f'Игрок {current_user.name} в тюрьме\n'
            elif condition == 'free':
                text_cur += f'Ты сейчас в тюрьме, но у тебя есть бесплатный выход\nХочешь его использовать?'
                text_others += f'Игрок {current_user.name} в тюрьме\n'
                keyboard_cur.append(["Использовать карточку", "Отсаться в тюрьме"])
            elif condition == 'doubles':
                text_cur += f'Ты сейчас в тюрьме, но тебе выпали дубли\nХочешь выйти из тюрьмы?'
                text_others += f'Игрок {current_user.name} в тюрьме\n'
                keyboard_cur.append(["Выйти из тюрьмы", "Отсаться в тюрьме"])
            elif condition == 'end':
                text_cur += f'Ты честно отсидел 3 круга и выходишь из тюрьмы\n'
                text_others += f'Игрок {current_user.name} выходит из тюрьмы\n'
                current_user.prisoner = False
                self.get_field_with_chips()
                last_users_action = 'Бросить кубики'
            else:
                text_cur += f'Ты все еще сидишь в тюрьме\n'
                text_others += f'Игрок {current_user.name} в тюрьме\n'

        if last_users_action == 'Бросить кубики': # если бросили кубики
            if cell == 10 and current_user.prisoner:
                text_cur += f'Тебя посадили в тюрьму!'
                text_others += f'Сейчас ход игрока {current_user.name}\nЕго посадили в тюрьму'
                keyboard_cur.append(["Моё имущество", "Закончить ход"]) 
            elif type(street) == int: # если попал на улицу
                street_owner = self.all_streets[street].current_owner
                street_name = self.all_streets[street].name
                if street_owner == None: # если нет владельца
                    text_cur += f'Ты попал на поле {street_name} и оно свободно!\n' \
                                f'Хочешь купить его за {self.all_streets[street].cost}$?'
                    keyboard_cur.append(["Купить", "Не покупать"])
                    text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {street_name}'
                    keyboard_cur.append(["Моё имущество"])
                else: # есть владелец
                    rent = self.calculate_rent(street,  current_user)
                    if street_owner != current_user: # если владелец не текущий игрок
                        text_cur += f'Ты попал на поле {street_name}, которое принадлежит игроку {street_owner.name}\n' \
                                    f'Ты должен заплатить ему {rent}$'
                        text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {street_name}'
                        keyboard_cur.append(["Заплатить ренту"])
                    else: # если владелец - текущай игрок
                        text_cur += f'Ты попал на поле {street_name}, которое принадлежит тебе\n'
                        text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {street_name}'
                        keyboard_cur.append(["Моё имущество", "Закончить ход"])
            else: # если попал на поле (не улицу)
                text_cur += f'Ты попал на поле {all_others[street]}\n'
                text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {all_others[street]}'
                text_cur = self.processing_other_fields(street, current_user, text_cur, keyboard_cur)
                keyboard_cur.append(["Моё имущество"])

        elif last_users_action == 'Купить': # если хочет купить улицу
            purchase = self.property_purchase(street, current_user)
            if purchase == False:
                text_cur += f'Тебе не хватает денег для покупки поля {self.all_streets[street].name}'
                text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {self.all_streets[street].name}'
            else:
                self.draw_propetry('field.png', street, current_user)
                text_cur += f'Ты приобрел поле {self.all_streets[street].name}!'
                text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {self.all_streets[street].name} и купил его'
            keyboard_cur.append(["Моё имущество", "Закончить ход"])
        
        elif last_users_action == 'Не покупать': # если не хочет покупать улицу
            text_cur += f'Ты не купил поле {self.all_streets[street].name}'
            text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {self.all_streets[street].name}, но не купил его'
            keyboard_cur.append(["Моё имущество", "Закончить ход"])

        elif last_users_action == 'Заплатить ренту': # если должен заплатить ренту
            rent = self.calculate_rent(street,  current_user)
            current_user.budget -= rent
            self.all_streets[street].current_owner.budget += rent
            text_cur += f'Ты заплатил игроку {self.all_streets[street].current_owner.name} {rent}$'
            text_others += f'Сейчас ход игрока {current_user.name}\nОн попал на поле {self.all_streets[street].name} ' \
                            f'и заплатил игроку {self.all_streets[street].current_owner.name} {rent}$'
            keyboard_cur.append(["Моё имущество", "Закончить ход"])
        
        elif last_users_action == 'Купить дом':
            #func bye house
            pass

        #keyboard_cur.append(["Информация о комнате", "Покинуть игру"])
        #keyboard_cur.append(['Купить дом'])
        keyboard_cur.append(["Купить дом"])
        keyboard_cur.append(["Все карточки"])

        keyboard_others.append(["Купить дом"])
        keyboard_others.append(["Моё имущество"])
        keyboard_others.append(["Все карточки"])
        #keyboard_others.append(["Информация о комнате", "Покинуть игру"])          
        return text_cur, text_others, keyboard_cur, keyboard_others


    async def step(self, update, context):
        self.now_player = (self.now_player + 1) % len(self.users)
        await self.update_message(update, context)



    def find_streets_accessible_to_houses(self, kit):
        streets = [self.all_streets[street] for street in group_and_streets[kit]]
        houses_count = {street.name: street.houses for street in streets}
        min_houses = min(houses_count.values())
        if min_houses == 5:
            return None
        available_for_houses = [street.name for street in streets if street.houses == min_houses]
        return available_for_houses

    async def choosing_street_for_house(self, update, context, current_user):
        #await context.bot.send_photo(chat_id=current_user.chat_id, photo=open(self.cards, 'rb'))
        if len(current_user.kits) == 0:
            await context.bot.send_message(chat_id=current_user.chat_id, text='Нет доступных улиц для постройки домов')
            #ВЫВЕСТИ текст что нет доступных улиц для постройки домов
        else:
            keyboard = []
            for kit in current_user.kits:
                if kit not in [8, 9]:
                    streets = self.find_streets_accessible_to_houses(kit)
                    #добавить в клавиатуру
                    if streets != None:
                        keyboard.append(streets)
            if len(keyboard) == 0:
                await context.bot.send_message(chat_id=current_user.chat_id, text='Нет доступных улиц для постройки домов')
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await context.bot.send_message(chat_id=current_user.chat_id, 
                                            text='Выберите, на какой улице поставить дом', 
                                            keyboard=reply_markup)
                

    def determining_house_type(self, current_user, street_name):
        for street in current_user.property:
            if self.all_streets[street].name == street_name:
                street_n = street
                house_n = self.all_streets[street].houses + 1
                break
        if house_n == 5:
            type = 'hotel'
        else:
            type = 'house'
            return street_n, type, house_n 


    async def buing_house(self, update, context, current_user):
        street_name = context.chat_data['last']
        street_n, type, house_n = self.determining_house_type(current_user, street_name)

        
        if current_user.budget >= self.all_streets[street_n].house_cost: # если бюджета игрока хватает на покупку дома
            if type == 'house':
                house_img = 'house.png'
                current_user.houses_amount += 1
            else:
                house_img = 'hotel.png'
                current_user.hotels_amount += 1
            current_user.budget -= self.all_streets[street_n].house_cost
            self.all_streets[street_n].houses += 1
            self.draw_houses('field.png', street_n, type, house_img, house_n)
            for i, user in enumerate(self.users):
                if user == current_user:
                    await context.bot.send_message(chat_id=current_user.chat_id,
                                            text=f'Поздравляю с покупкой дома ' \
                                                  f'на улице {street_name}!')
                else:
                    await context.bot.send_message(chat_id=user.chat_id,
                                            text=f'Игрок {current_user.name} купил дом ' \
                                                  f'на улице {street_name}')
        else:
            await context.bot.send_message(chat_id=current_user.chat_id,
                                            text=f'Недостаточно средств, чтобы купить дом ' \
                                                  f'на улице {street_name} за {self.all_streets[street_n].house_cost}')


    
    async def send_cards(self, update, context, current_user):
        await context.bot.send_photo(chat_id=current_user.chat_id, photo=open(self.cards, 'rb'))

    async def send_property(self, update, context, current_user):
        im = Image.new('RGB', (field_width + 1, field_width + 1), field_color)
        draw = ImageDraw.Draw(im)
        '''if current_user == self.now_player:
            keyboard = [['Закончить ход']]
        else:
            keyboard=[]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)'''
        if  len(current_user.property) == 0:
            await context.bot.send_message(chat_id=current_user.chat_id, text='Упс! У вас пока нет ни одной купленной улицы')
        else:
            create_cards_img(draw, len(current_user.property))
            for number, i in enumerate(current_user.property):
                street = self.all_streets[i]
                x_1, x_2, y_1, y_2 = calculate_coord_for_cards(number)
                if i < 22:
                    new_y_1 = draw_cards_titles(draw, street.name, x_1, x_2, y_1, y_2, 'street', street.color)
                    draw_card_info(draw, street.rent, street.house_cost, street.collateral_value,
                                    x_1, x_2, new_y_1, y_2, 'street')
                else:
                    new_y_1 = draw_cards_titles(draw, street.name, x_1, x_2, y_1, y_2,'other', None)
                    if i < 26:
                        draw_card_info(draw, street.rent, None, street.collateral_value, 
                                    x_1, x_2, new_y_1, y_2, 'railway')
                    else:
                        draw_card_info(draw, None, None, street.collateral_value, 
                                    x_1, x_2, new_y_1, y_2, 'utilities')
            im.save(f'self_property.png')
            await context.bot.send_photo(chat_id=current_user.chat_id, photo=open('self_property.png', 'rb'))
        #im.show()



    def get_field_with_chips(self, image, output_image):
        # заполняем словарь {поле: [список фишек]}
        field_and_chip = dict()
        #print('FUNCTION',  'get_field_with_chips')
        for chip in self.users:
            #print(chip)
            field = chip.cell
            if not(field in field_and_chip):
                field_and_chip[field] = []
            field_and_chip[field].append(chip)
        self.draw_chips_positions(image, field_and_chip, output_image)
    
    def generate_image(self):
        self.get_field_with_chips(self.field, self.output_image)
        print(self.image_items_list)
        for key, value in self.image_items_list:
            if key == 'card_shirt':
                self.special_cards.draw_special_card(self.output_image, value)
            elif key == 'front_card_side':
                print(value[1], value[0])
                self.special_cards.draw_special_card(self.output_image, value[1], value[0])
                print("ok")
        self.image_items_list = []

    async def update_message(self, update, context):
        text_cur, text_others, keyboard_cur, keyboard_others = self.generating_text_and_keyboard(context.chat_data['last'])
        self.generate_image()
        for i, player in enumerate(self.users):
            #await context.bot.delete_message(chat_id=player.chat_id, message_id=player.last_message_id)
            if i == self.now_player: #сейчас ход i-го игрока
                text = f"Цвет твоей фишки - {chips_colors_names[i]}\nТвой бюджет - {self.users[i].budget}$\n" + text_cur
                keyboard = keyboard_cur
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
            else:
                text = f"Цвет твоей фишки - {chips_colors_names[i]}\nТвой бюджет - {self.users[i].budget}$\n" + text_others
                keyboard = keyboard_others
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
            message = await context.bot.send_photo(chat_id=player.chat_id, photo=open(self.output_image, 'rb'), caption=text,
                                                reply_markup=reply_markup)
            player.last_message_id = message.message_id
