#!/usr/bin/env python3
import string
import random
from PIL import Image
import matplotlib.pyplot as plt
import os
import sys 
sys.path.append('..')
from image_processing import *
sys.path.append('../..')
import Daily_StockCharts_Emailer


NUM_SAMPLES = 25 # number of floats to samples (not digits)
TMP_IMG_NAME = "TMP_IMG.png"


def __imshow_prompt_char(I, prompt="<Enter char>", title=None):
	fig = plt.figure()
	plt.imshow(I)
	if title is not None:
		plt.title(title)
	plt.draw()
	plt.pause(0.1)
	char = input(prompt)
	plt.close(fig)
	return char


def get_samples_dir(char):
	if char == ".":
		return "period"
	if char == "b":
		return "bad"
	if len(char) == 1 and char.isdigit():
		return char
	return None


def generate_rand_ticker():
	ticker = ""
	for _ in range(3):
		ticker += random.choice(string.ascii_letters)
	return ticker.upper()


def get_chart_image(ticker):
	Daily_StockCharts_Emailer.scrape_img(TMP_IMG_NAME, ticker)
	I = Image.open(TMP_IMG_NAME)
	os.remove(TMP_IMG_NAME)
	return I


def main():
	for i in range(NUM_SAMPLES):
		print("Sample #" + str(i))
		# Get a chart image from a random ticker
		print("Getting chart image")
		I_chart = None
		try_cnt = 0
		while (I_chart is None):
			try:
				rand_ticker = generate_rand_ticker()
				I_chart = get_chart_image(rand_ticker)
				print("Successfully scraped chart for ", rand_ticker)
			except Exception as e:
				print("Failed to scrape ", rand_ticker, e)
				try_cnt += 1
				if try_cnt > 50:
					print("Try count exceeded, exiting...")
					exit(1)
		# Process array of characters in RSI float from chart
		print("Processing image")
		I_chars = get_digits_from_chart(I_chart)
		# Prompt user asking which digit each character is
		print("Prompting user")
		inputs = []
		for I_digit in I_chars:
			inpt = __imshow_prompt_char(I_digit)
			if inpt.lower() == "q":
				exit(0)
			inputs.append(inpt)
		# Catagorize digit images
		print("Inputs: ", inputs)
		for inpt, I_digit in zip(inputs, I_chars):
			dest_dir = get_samples_dir(inpt)
			if dest_dir is None:
				print("ERROR: invalid input, no destination dir: ", inpt)
				continue
			if not os.path.exists(dest_dir):
				os.makedirs(dest_dir)
			image_name = Daily_StockCharts_Emailer.get_date_str(True) + "_" + rand_ticker
			I_digit.save(dest_dir + "/" + image_name + ".png", "PNG")


if __name__ == "__main__":
	main()
