#!/usr/bin/env python3
from image_processing import *
import os


STOCK_DIGITS = None


def __init_stock_digits():
	global STOCK_DIGITS
	if not STOCK_DIGITS is None:
		return
	name_locations = [
		("0",	"data/stock_digits/0.png"),
		("1",	"data/stock_digits/1.png"),
		("2",	"data/stock_digits/2.png"),
		("3",	"data/stock_digits/3.png"),
		("4",	"data/stock_digits/4.png"),
		("5",	"data/stock_digits/5.png"),
		("6",	"data/stock_digits/6.png"),
		("7",	"data/stock_digits/7.png"),
		("8",	"data/stock_digits/8.png"),
		("9",	"data/stock_digits/9.png"),
		(".",	"data/stock_digits/period.png")
	]
	STOCK_DIGITS = []
	file_path = os.path.realpath(__file__)
	file_path = file_path[:file_path.rfind('/')]
	for str_stock, img_path in name_locations:
		I = Image.open(file_path + "/" + img_path)
		STOCK_DIGITS.append((I, str_stock))


def __match(I1, I2):
		if I1.width != I2.width or I1.height != I2.height:
			return False
		for r in range(I1.height):
			for c in range(I1.width):
				if I1.getpixel((c,r)) != I2.getpixel((c,r)):
					return False
		return True


def __get_str_digit(I_digit):
	global STOCK_DIGITS
	for I_stock, str_stock in STOCK_DIGITS:
		if __match(I_stock, I_digit):
			return str_stock
	return None


def get_rsi_str(I_chart):
	''' Given the chart image, returns a string of the RSI value, or None
	if an error occurred. '''
	__init_stock_digits()
	I_digits = get_digits_from_chart(I_chart)
	str_rsi = ""
	for I_dig in I_digits:
		str_dig = __get_str_digit(I_dig)
		if str_dig is None:
			return None
		str_rsi += str_dig
	return str_rsi


if __name__ == "__main__":
	I_chart = Image.open("example_chart.png")
	rsi = get_rsi_str(I_chart)
	print("RSI: ", rsi)
