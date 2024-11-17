#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests

logging.basicConfig(level=logging.DEBUG)

def split_string(input_string, max_length = 21):
    if not input_string:
        return []

    words = input_string.split()
    result = []
    current_line = ""

    for word in words:
        # If adding the word would exceed the max length, save the current line
        if len(current_line) + len(word) + 1 > max_length:  # +1 for space
            result.append(current_line.strip())
            current_line = word
        else:
            current_line += " " + word if current_line else word

    # Add the last line if there is any content left
    if current_line:
        result.append(current_line.strip())

    return result

def draw_lines(draw, lines, start_height):
	
	for line in lines:
		draw.text((10, start_height), line, font = font24, fill = 0)
		start_height += 24


def get_detailed_forecast():
    url = "https://api.weather.gov/gridpoints/BOX/71,90/forecast"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        detailed_forecast = data["properties"]["periods"][0]["detailedForecast"]

        return detailed_forecast

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except KeyError as e:
        return f"Error parsing weather data: {e}"

try:

    logging.info("epd2in7 Demo")   
    epd = epd2in7.EPD()
    
    '''2Gray(Black and white) display'''
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw_lines(draw, split_string(get_detailed_forecast()), 0)
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)
    
    logging.info("Clear...")
    #epd.Clear(0xFF)
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit(cleanup=True)
    exit()
