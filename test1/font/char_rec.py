#!/usr/bin/python
# -*-coding:utf-8-*-
import cv2
from PIL import Image
import numpy as np
from fontTools.ttLib import TTFont

image_width = 1014
image_height = 1014
resize_pixel = 100
char_number = 20

from aip import AipOcr
import time

""" 你的 APPID AK SK """
# APP_ID = '11466958'
# API_KEY = 'Ps5pBmtmQHDp09lBZp0Gb37c'
# SECRET_KEY = 'czMUSlfa0mkzqyCeWK3wZAfRWKxznVTx'

APP_ID = '11557153'
API_KEY = '3y937tsmmPzi0D3sIzLYcalP'
SECRET_KEY = 'IfGH5qLj5zdcWFCQXvr9BMaHhv1TFEdG '


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def rec_image_baidu(imgpath, number, single_width):
    assert number * single_width < 4096
    image = get_file_content(imgpath)
    options = {}
    options["recognize_granularity"] = "small"
    options["vertexes_location"] = "true"
    options["probability"] = "true"
    time.sleep(1)
    """ 带参数调用通用文字识别（含位置高精度版） """
    result = client.general(image, options)
    chars = result['words_result'][0]['chars']
    return_char = []
    return_location = []
    for char in chars:
        location = round(char['location']['left'] / 100.0)
        return_char.append(char['char'])
        return_location.append(location)
    return return_char, return_location


def extract_coordinate(wofffile):
    onlineFonts = TTFont(wofffile)
    onlineFonts.saveXML('temp.xml')

    import xml.dom.minidom

    dom = xml.dom.minidom.parse('temp.xml')

    root = dom.documentElement

    all_chars = root.getElementsByTagName('TTGlyph')
    all_code_name_maps = root.getElementsByTagName('map')

    code_name_map = {}
    for all_code_name_map in all_code_name_maps:
        code = all_code_name_map.getAttribute("code")
        nc = unichr(int(code, 16))
        name = all_code_name_map.getAttribute("name")
        code_name_map[name] = nc
    chars_array = []
    names = []
    for char0 in all_chars:
        try:
            name = char0.getAttribute("name")
            names.append(name)
        except:
            continue
        try:
            xmin = int(char0.getAttribute("xMin"))
            ymax = int(char0.getAttribute("yMax"))
        except:
            xmin = 0
            ymax = image_height
        contours = char0.getElementsByTagName('contour')
        char_array = []
        for contour in contours:
            contour_array = []
            childnodes = contour.childNodes
            for childnode in childnodes:
                try:
                    x = int(childnode.getAttribute("x")) - xmin
                    y = ymax - int(childnode.getAttribute("y"))
                    contour_array.append([x, y])
                except:
                    continue
            char_array.append(contour_array)
        chars_array.append(char_array)
    return chars_array, names, code_name_map


def save_image(vertical_array, name):
    arr = np.ones([image_width, image_height], dtype=np.uint8) * 255
    for contour in vertical_array:
        cv2.polylines(arr, [np.array(contour, np.int32)], 1, 0, 50)
        # cv2.fillPoly(arr, [np.array(contour, np.int32)], 255)
    img = Image.fromarray(arr)
    img = img.convert('L')
    img = img.resize((resize_pixel, resize_pixel))
    # image_path = '/data/%s.jpg' % name
    img.save('./data/%s.jpg' % name)
    return img


def write(f, str):
    f.write(str.encode('utf-8'))

if __name__ == '__main__':
    file_name = 'tyc-num'
    wofffile = file_name + '.woff'
    chars_array, names, code_name_map = extract_coordinate(wofffile)

    combined_image = Image.new('L', (char_number * resize_pixel, resize_pixel))
    patch_names = []
    outputfile = open(file_name + '.txt', 'w')
    for index, char_array in enumerate(chars_array):
        img = save_image(char_array, index)
        if (index + 1) % char_number:
            patch_names.append(names[index])
            combined_image.paste(img, (
            (index % char_number) * resize_pixel, 0, ((index + 1) % char_number) * resize_pixel, resize_pixel))
        else:
            combined_image.paste(img,
                                 ((index % char_number) * resize_pixel, 0, char_number * resize_pixel, resize_pixel))
            combined_image.save('temp.jpg')
            patch_names.append(names[index])
            rec_char, location = rec_image_baidu('temp.jpg', char_number, resize_pixel)
            for i in range(char_number):
                if i in location:
                    write(outputfile, '%s=%s\n' % (code_name_map[patch_names[i]], rec_char[location.index(i)]))
                    print((patch_names[i], code_name_map[patch_names[i]], rec_char[location.index(i)]))
                else:
                    write(outputfile,
                          '%s=%s\n' % (code_name_map[patch_names[i]], code_name_map[patch_names[i]] + '? '))
            combined_image = Image.new('L', (char_number * resize_pixel, resize_pixel))
            patch_names = []
        if index + 1 >= len(chars_array):
            combined_image.save('temp.jpg')
            patch_names.append(names[index])
            rec_char, location = rec_image_baidu('temp.jpg', char_number, resize_pixel)
            for i in range(char_number):
                if i in location:
                    write(outputfile, '%s=%s\n' % (code_name_map[patch_names[i]], rec_char[location.index(i)]))
                    print((patch_names[i], code_name_map[patch_names[i]], rec_char[location.index(i)]))
                else:
                    write(outputfile,
                          '%s=%s\n' % (code_name_map[patch_names[i]], code_name_map[patch_names[i]] + '? '))
