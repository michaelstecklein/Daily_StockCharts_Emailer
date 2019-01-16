#!/usr/bin/env python3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
from bs4 import BeautifulSoup
import shutil, os
import datetime
from PIL import Image
import sys
sys.path.append('rsi_recognition')
import ocr


TICKER = "UCO"
STOCKCHARTS_IMG_EXT = ".png"
LAST_UPDATE_FILE = "last_update.date"
ERROR_IMG = "error.jpg"
STRATEGY_DESCRIPTION = "Buy $100 worth when the RSI value rises above 35 after dropping below 33. Sell all quantities purchased since the last sell when the RSI hits 70. Do not buy more than 2 consecutive batches ($100/batch) between sells, (and therefor do not sell more than twice consecutively as well)."


def get_date_str(with_time=False):
	if with_time:
		return datetime.datetime.now().strftime("%m_%d_%y_%H_%M")
	else:
		return datetime.datetime.now().strftime("%m_%d_%y")

def last_email():
	if not os.path.isfile(LAST_UPDATE_FILE):
		return "NONE"
	with open(LAST_UPDATE_FILE, "r") as f:
		return f.read()

def last_email_today():
	return last_email() == get_date_str()

def update_last_email():
	with open(LAST_UPDATE_FILE, "w") as f:
		f.write(get_date_str())

def get_request_url(ticker=None):
	return "http://stockcharts.com/h-sc/ui?s={}".format(TICKER.lower() if ticker is None else ticker)

def scrape_img(dest_img, ticker=None):
	''' Scrape chart image from stockcharts.com and save it to the
	destination image path. '''
	request_url = get_request_url(ticker)
	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
	headers = {'User-Agent': user_agent}
	page = requests.get(request_url, headers=headers)
	soup = BeautifulSoup(page.text, "lxml")
	img_tag = soup.find_all('img', {"id": "chartImg"})
	if len(img_tag) is 0:
		raise RuntimeError
	img_src = img_tag[0]['src']
	img_url = "http:" + img_src
	img_req = requests.get(img_url, headers=headers, stream=True)
	with open(dest_img, 'wb') as f:
		img_req.raw.decode_content = True
		shutil.copyfileobj(img_req.raw, f)

def send_email(subject, message, img_file=None):
	fromaddr = "bgrogh@gmail.com"
	toaddr = "michaelrstecklein@gmail.com"
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = subject
	msgEmbedded = MIMEMultipart("embedded")
	msg.attach(msgEmbedded)
	if img_file is not None:
		img_data = open(img_file, 'rb').read()
		image = MIMEImage(img_data, name=os.path.basename(img_file))
		msgEmbedded.attach(image)
	body = "{}".format(message)
	msgEmbedded.attach(MIMEText(body, 'plain'))
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "robert123abc")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
	update_last_email()

def main():
	if not last_email_today():
		# scrape chart image from stockcharts.com
		tmp_img_name = get_date_str(True) + STOCKCHARTS_IMG_EXT
		error_msg = ""
		try:
			scrape_img(tmp_img_name)
		except Exception as e:
			print("ERROR: ", e)
			error_msg = str(e)
			shutil.copyfile(ERROR_IMG, tmp_img_name)
		# read the RSI value
		rsi = ocr.get_rsi_str(Image.open(tmp_img_name))
		if rsi is None:
			rsi = "ERROR"
		# send email
		pretty_date = datetime.datetime.now().strftime("%B %d, %Y, %I:%M%p")
		subject = "RSI: {},  Today's chart for {} - {}".format(rsi, TICKER, pretty_date)
		message = subject + "\n" + get_request_url() + "\n" + error_msg + "\n" + STRATEGY_DESCRIPTION + "\n"
		send_email(subject, message, tmp_img_name)
		# cleanup
		os.remove(tmp_img_name)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		send_email("ERROR - RaspberryPi RSI Program", "An exception has been caught in main().\n%s" % str(e))
