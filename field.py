from PIL import Image, ImageDraw, ImageOps, ImageFont, ImageEnhance
import textwrap
from config import *
import re


def draw_main_border(draw):
    draw.line([(k * field_width, 0), (k * field_width, field_width)], fill=fill, width=line_width) # левая
    draw.line([(0, k * field_width), (field_width, k * field_width)], fill=fill, width=line_width) # верхняя
    draw.line([((1 - k) * field_width, 0), ((1 - k) * field_width, field_width)], fill=fill, width=line_width) # правая
    draw.line([(0, (1 - k) * field_width), (field_width, (1 - k) * field_width)], fill=fill, width=line_width) # нижняя


def draw_streets_borders(draw):
    for i in range(8):
        draw.line([(0, k * field_width + (i + 1) * minifield_width), (k * field_width, k * field_width + (i + 1) * minifield_width)], fill=fill, width=line_width) # лево
        draw.line([(k * field_width + (i + 1) * minifield_width, 0), (k * field_width + (i + 1) * minifield_width, k * field_width)], fill=fill, width=line_width) # верх
        draw.line([(field_width * (1 - k), k * field_width + (i + 1) * minifield_width), (field_width, k * field_width + (i + 1) * minifield_width)], fill=fill, width=line_width) # право 
        draw.line([(k * field_width + (i + 1) * minifield_width, field_width * (1 - k)), (k * field_width + (i + 1) * minifield_width, field_width)], fill=fill, width=line_width) # низ


def draw_streets_colors(draw):
    for i in range(9):
        if i in top:
            x_1 = k * field_width + (i) * minifield_width
            y_1 = round(field_width * k * (1 - n))
            x_2 = k * field_width + (i + 1) * minifield_width
            y_2 = k * field_width
            draw.line([(x_1, y_1), (x_2, y_1)], fill=fill, width=line_width)
            if i > 3:
                col = colors_top[1]
            else:
                col = colors_top[0]
            draw.rectangle([(x_1 + coef, y_1 + coef), (x_2 - coef, y_2 - coef)], fill=col)
        if i in bottom:
            x_1 = k * field_width + (i) * minifield_width
            y_1 = field_width * (1 - k)
            x_2 = k * field_width + (i + 1) * minifield_width
            y_2 = round(field_width * (1 - k) + field_width * k * n)
            draw.line([(x_1, y_2), (x_2, y_2)], fill=fill, width=line_width)
            if i > 3:
                col = colors_bottom[1]
            else:
                col = colors_bottom[0]
            draw.rectangle([(x_1 + coef, y_1 + coef), (x_2 - coef, y_2 - coef)], fill=col)
        if i in left:
            y_1 = k * field_width + (i) * minifield_width
            x_1 = round(field_width * k * (1 - n))
            y_2 = k * field_width + (i + 1) * minifield_width
            x_2 = k * field_width
            draw.line([(x_1, y_1), (x_1, y_2)], fill=fill, width=line_width)
            if i > 3:
                col = colors_left[1]
            else:
                col = colors_left[0]
            draw.rectangle([(x_1 + coef, y_1 + coef), (x_2 - coef, y_2 - coef)], fill=col)
        if i in right:
            y_1 = k * field_width + (i) * minifield_width
            x_1 = field_width * (1 - k)
            y_2 = k * field_width + (i + 1) * minifield_width
            x_2 = round(field_width * (1 - k) + field_width * k * n)
            draw.line([(x_2, y_1), (x_2, y_2)], fill=fill, width=line_width)
            if i > 3:
                col = colors_right[1]
            else:
                col = colors_right[0]
            draw.rectangle([(x_1 + coef, y_1 + coef), (x_2 - coef, y_2 - coef)], fill=col)


def draw_prison(draw):
    x_1 = round(field_width * k // 3)
    y_1 = field_width * (1 - k)
    x_2 = field_width * k
    y_2 = round(field_width - field_width * k // 3)
    draw.line([(x_1, y_1), (x_1, y_2)], fill=fill, width=line_width) # тюрьма
    draw.line([(x_1 - line_width // 2, y_2), (x_2, y_2)], fill=fill, width=line_width) # тюрьма



def draw_streets_titles(draw, title, x, y):
    text = title
    font = ImageFont.truetype('draw/Cygre.ttf',   15)
    color = 'black'
    max_chars_per_line =  14
    wrapped_text = textwrap.wrap(text, width=max_chars_per_line)
    text_width = max(font.font.getsize(line)[0][0] for line in wrapped_text)
    text_height = sum(font.font.getsize(line)[0][1] for line in wrapped_text)
    formatted_text = "\n".join(wrapped_text)
    x = x - (text_width // 2)
    y = y - (text_height // 2)
    draw.text((x, y), formatted_text, font=font, align="center", fill=color)

def draw_streets_costs(draw, title, x, y):
    font = ImageFont.truetype('draw/Cygre.ttf', 15)
    color = 'black'
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text=title, font=font)
    text_width = right - left
    text_height = bottom - top
    x = x - (text_width // 2)
    y = y - text_height
    draw.text((x, y), title, font=font, align="center", fill=color)


def calculate_coordinates_for_pictures(field_number):
    side = field_number // 10
    if field_number == 10:
        x_2 = field_width - round(field_width * k // 3)
        x_1 = round(field_width * (1 - k) + field_width * k * n)
        y = (field_width * (1 - k) + round(field_width - field_width * k // 3)) // 2
    elif field_number % 10 == 0:
        x_1 = field_width
        x_2 = field_width * (1 - k)
        y = field_width * (2 - k) // 2
    else:
        x_1 = field_width * k + ((side * 10 + 10) - 1 - field_number) * minifield_width
        x_2 = field_width * k + ((side * 10 + 10) - field_number) * minifield_width       
        y = round(field_width * (2 - k + k * n)) // 2
    return (x_2 + x_1) // 2, y

def draw_cells_pictures(im, x, y, n):
    transparency = 1
    brightness = 0.9
    size = round(minifield_width // 1.5)
    rotation = 0
    if n == 0:
        file = 'pictures/go.png'
    elif n == 10:
        file = 'pictures/prison.png'
        size = int(abs(field_width * (1 - k) - (field_width - round(field_width * k // 3))) // 1.5)
        rotation = -90
    elif n in [2, 17, 33]:
        file = 'pictures/treasury.png'
        transparency = 0.75
        brightness = 0.7
    elif n  in [7, 22, 36]:
        file = 'pictures/chance.png'
        transparency = 0.75
        brightness = 0.7
    elif n in [5, 15, 25, 35]:
        file = 'pictures/train.png'
        transparency = 0.75
        brightness = 0.7
    elif n == 28:
        file = 'pictures/faucet.png'
        transparency = 0.75
        brightness = 0.7
    elif n == 12:
        file = 'pictures/lamp.png'
        transparency = 0.75
        brightness = 0.7
    elif n == 20:
        file = 'pictures/car.png'
        rotation = 45
        size = round(minifield_width)
    elif n == 30:
        file = 'pictures/police.png'
        rotation = 45
        size = round(minifield_width)
    elif n == 4:
        file = 'pictures/tax.png'
        transparency = 0.75
        brightness = 0.7
    elif n == 38:
        file = 'pictures/supertax.png'
    else:
        return
    picture = Image.open(file)
    #width, height = picture.size
    picture = picture.rotate(rotation, expand=True)
    picture = picture.resize((size, size))

    enhancer = ImageEnhance.Brightness(picture)
    picture = enhancer.enhance(brightness)
    alpha = picture.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(transparency)
    picture.putalpha(alpha)

    width, height = picture.size
    im.paste(picture, (x - width // 2, y - height // 2), picture)

def calculate_coordinates_for_streets(field_number, type):
    side = field_number // 10
    i = 10
    if side == 1:
        i = 20
    elif side == 2:
        i = 30
    elif side == 3:
        i = 40
    x_1 = field_width * k + (i - 1 - field_number) * minifield_width
    x_2 = field_width * k + (i - field_number) * minifield_width
    if type == 'street':
        y = round(field_width - k * field_width * ( 1 - n - m * (1 - n)))
    else:
        y = round(field_width - k * field_width * (1 - m))
    return (x_2 + x_1) // 2, y


def calculate_coordinates_for_costs(field_number):
    side = field_number // 10
    i = 10
    if side == 1:
        i = 20
    elif side == 2:
        i = 30
    elif side == 3:
        i = 40
    x_1 = field_width * k + (i - 1 - field_number) * minifield_width
    x_2 = field_width * k + (i - field_number) * minifield_width
    y = field_width - field_width * k * n * m
    return (x_2 + x_1) // 2, y


def create_cards_img(draw, n):
    for i in range(n):
        x, y = card_l + (i % 6) * (card_l + card_width), card_l + (i // 6) * (card_l + card_height)
        draw.line([(x, y), (x + card_width, y)], fill=fill, width=line_width)
        draw.line([(x, y), (x, y + card_height)], fill=fill, width=line_width)
        draw.line([(x + card_width, y), (x + card_width, y + card_height)], fill=fill, width=line_width)
        draw.line([(x, y + card_height), (x + card_width, y + card_height)], fill=fill, width=line_width)
    return

def calculate_coord_for_cards(i):
    x_1 = card_l + (i % 6) * (card_l + card_width)
    x_2 = x_1 + card_width
    y_1 = (card_l + (i // 6) * (card_l + card_height)) + card_height * alpha
    y_2 = (card_l + (i // 6) * (card_l + card_height))
    return x_1, x_2, y_1, y_2


def draw_cards_colors(draw, x_1, x_2, y_1, y_2, col):
    draw.rectangle([(x_1 + coef, y_1 + coef), (x_2 - coef, y_2 - coef)], fill=col)
    draw.line([(x_1, y_2), (x_2, y_2)], fill=fill, width=line_width)


def draw_cards_titles(draw, title, x_1, x_2, y_1, y_2, type, col):
    text = title
    font = ImageFont.truetype('draw/Cygre.ttf',   22)
    color = 'black'
    max_chars_per_line =  14
    wrapped_text = textwrap.wrap(text, width=max_chars_per_line)
    text_width = max(font.font.getsize(line)[0][0] for line in wrapped_text)
    text_height = sum(font.font.getsize(line)[0][1] for line in wrapped_text)
    formatted_text = "\n".join(wrapped_text)
    x = (x_1 + x_2) // 2
    x = x - (text_width // 2)
    y = y_1 - (text_height // 2)
    left, top, right, bottom = draw.multiline_textbbox((x, y), text=formatted_text, font=font)
    y_1 = bottom + card_height * alpha - (text_height // 2)
    if type == 'street':
        draw_cards_colors(draw, x_1, x_2, y_2, y_1, col)
    draw.text((x, y), formatted_text, font=font, align="center", fill=color)
    return y_1


def draw_card_info_lines(draw, text, align, x, y):
    font = ImageFont.truetype('draw/Cygre.ttf',   22)
    color = 'black'
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text=text, font=font)
    text_width = right - left
    text_height = bottom - top
    if align == 'center':
        draw.text((x - (text_width // 2), y), text, font=font, align=align, fill=color)
    elif align == 'left':
        draw.text((x, y), text, font=font, align=align, fill=color)
    else:
        draw.text((x - text_width, y), text, font=font, align=align, fill=color)
    return text_height


def draw_card_info(draw, rent, house_cost, collateral_value, x_1, x_2, y_1, y_2, type):
    small_interval = round((y_1 - y_2) * (alpha // 2) + coef)
    large_interval = round((y_1 - y_2) * alpha + coef)
    texts = []
    if type == 'street':
        texts.append(["Арендная плата:", "center"])
        texts.append(["За участок\n1 дом\n2 дома\n3 дома\n4 дома\nОтель", "left"])
        texts.append(['$\n'.join(map(str, rent)) + '$', "right"])
        texts.append(["Стоимость:", "center"])
        texts.append(["Залоговая\nЦена дома\nЦена отеля", "left"])
        texts.append([f"{collateral_value}$\n{house_cost}$\n{house_cost}$", "right"])
    elif type == 'railway':
        texts.append(["Арендная плата:", "center"])
        texts.append(["1 объект\n\n2 объекта\n\n3 объекта\n\n4 объекта", "left"])
        texts.append(['$\n\n'.join(map(str, rent)) + '$', "right"])
        texts.append(["Стоимость:", "center"])
        texts.append(["Залоговая", "left"])
        texts.append([f"{collateral_value}$", "right"])
    else:
        texts.append(["Арендная плата:", "center"])
        texts.append(["1 предприятие\n\n2 предприятия", "left"])
        texts.append(["4\n\n10", "right"])
        texts.append(["умножается на сумму\nочков на кубиках", "center"])
        texts.append(["Стоимость:", "center"])
        texts.append(["Залоговая", "left"])
        texts.append([f"{collateral_value}$", "right"])
    new_y = y_1
    text_height = 0
    for i in range(len(texts)):
        if texts[i][1] == "center":
            x = (x_1 + x_2) // 2
            if i == 0:
                if type == 'street':
                    y = new_y + small_interval
                    text_height = draw_card_info_lines(draw, texts[i][0], "center", x, y)
                    new_y += text_height
                else:
                    y = new_y + small_interval
                    text_height = draw_card_info_lines(draw, texts[i][0], "center", x, y)
                    new_y += text_height 
            else:
                y = new_y + large_interval
                text_height = draw_card_info_lines(draw, texts[i][0], "center", x, y)
                new_y += text_height + large_interval
                if  texts[i][0] != "Стоимость:":
                    new_y += text_height
        if texts[i][1] == "left":
            texts[i][1]
            x = x_1 + large_interval
            if type == 'street':
                y = new_y + small_interval
                text_height = draw_card_info_lines(draw, texts[i][0], "left", x, y)
                new_y += text_height
            else:
                y = new_y + large_interval
                text_height = draw_card_info_lines(draw, texts[i][0], "left", x, y)
                new_y += text_height + large_interval
        if texts[i][1] == "right":
            x = x_2 - large_interval
            if type == 'street':
                y = new_y - text_height + small_interval
            else:
                y = new_y - text_height
            text_height = draw_card_info_lines(draw, texts[i][0], "right", x, y)



def draw_special_cells(image):
    font = ImageFont.truetype('draw/Cygre.ttf',   22)
    color = 'black'
    texts = ['ПОЛЕ', 'ВПЕРЕД', 'ПРОСТО', 'ПОСЕТИТЕЛЬ', 'ТЮРЬМА', 'БЕСПЛАТНАЯ', 'СТОЯНКА','ОТПРАВЛЯЙСЯ', 'В ТЮРЬМУ']
    texts_coords = [[round(field_width * k) // 2, round(field_width * (1 - k))], 
                    [round(field_width * (2 - k)) // 2, round(field_width * (1 - k))], 
                    [round(field_width * (2 - k) - field_width * k // 3) // 2, round(2 * field_width - field_width * k // 3) // 2],
                    [field_width * k // 2, round(2 * field_width - field_width * k // 3) // 2], 
                    [round(field_width * k + field_width * k // 3) // 2, round(field_width * (1 - k))], 
                    [field_width * k // 2, round(field_width * (1 - k))], 
                    [field_width * (2 - k)// 2,  round(field_width * (1 - k))], 
                    [field_width * k // 2, round(field_width * (1 - k))], 
                    [field_width * (2 - k)// 2, round(field_width * (1 - k))]]
    rotations = [-90, 90, 90, -90 , 0, 90, 90, 0, 90]
    for i, coords in enumerate(texts_coords):
        image = image.rotate(rotations[i])
        draw = ImageDraw.Draw(image)
        left, top, right, bottom = draw.multiline_textbbox((0, 0), text=texts[i], font=font)
        text_width = right - left
        text_height = bottom - top
        if i in [2, 3]:
            draw.text((coords[0] - text_width // 2, coords[1] - text_height // 2), texts[i], font=font, align="center", fill=color)
        else:
            draw.text((coords[0] - text_width // 2, coords[1] + text_height // 2), texts[i], font=font, align="center", fill=color)

    image = image.rotate(90)
    return image


'''
def generating_chips(chips_count):
    chips_colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (255, 140, 0), (255, 20, 147)]
    for i in range(chips_count):
        size = (coef_y, coef_y)
        img = Image.new('RGBA', size, (255,  255,  255,  0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([0,  0, coef_y - 1, coef_y - 1], fill=chips_colors[i])
        img.save(f"chip_{i}.png")


def draw_chips_positions(image_path, field_number, chip_number):
    img = Image.open(image_path)
    side = field_number // 10
    i = 10 * (side + 1)
    img = img.rotate(90 * side)
    x = round((field_width * k + (i - 1 - field_number) * minifield_width) + coef + (chip_number % 2) * coef_x)
    y = round(round(field_width * (1 - k) + field_width * k * n) + coef + (chip_number // 2) * coef_y )
    x = x + (coef_x - coef_y) // 2
    y = y + (coef_y - coef_y) // 2
    chip = Image.open(f'chip_{chip_number}.png')
    mask = Image.new("L", chip.size,  0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((5,  5) + (coef_y - 5, coef_y - 5), fill=255)
    img.paste(chip, (x, y), mask)
    img = img.rotate(-90 * side)
    img.save('field_with_chips.png')
'''
