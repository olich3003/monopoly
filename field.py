from PIL import Image, ImageDraw, ImageOps, ImageFont
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
