#!/usr/bin/env python3

import requests
import json
from time import sleep
from datetime import datetime, timedelta
import threading
from random import choice
from os import environ
import re

API = 'https://api.telegram.org/bot'
API_TOKEN = environ['API_TOKEN']
URL = API + API_TOKEN
TIMEZONE = -8
BOT_NAME = '@FGO_Platy_Bot'.lower()
REFRESH_RATE = 60
SGT = 15
LIMIT = 100

with open('id.txt') as f:
	allChatID = f.read().strip().split('\n')
	try:
		allChatID.remove('')
	except:
		pass

with open('lines.txt') as f:
	lines = f.read().strip().split('\n')

def getUpdates(update_id): # Get messages sent to bot
	r = requests.get(URL + '/getupdates', params={'offset': update_id, 'limit': LIMIT})
	return json.loads(r.text)

def sendMessage(cid, text='Welcome to Fate Grind Order!'):
	payload = {'chat_id': cid, 'text': text, 'parse_mode': 'markdown'}
	r = requests.get(URL + '/sendmessage', params=payload)

def storeID(cid):
	if str(cid) not in allChatID:
		allChatID.append(str(cid))

def removeID(cid):
	try:
		allChatID.remove(str(cid))
	except:
		pass

def blastMsg(whut, cid):
	sendMessage(int(cid), '*Daily Login Reminder!*\n{}\n_~ Astolfo_ ♥'.format(choice(lines)))

def getNew():
	while True:
		with open('msg.txt', 'r') as f:
			update_id = int(f.read())

		data = getUpdates(update_id)['result']

		if len(data) == 0:
			break

		for msg in data:
			try:
				current_id = msg['message']['chat']['id']
				current_text = msg['message']['text'].lower()
				current_type = msg['message']['chat']['type']
				update_id = msg['update_id']
			except:
				current_text = None
				current_type = None

			if current_text == '/start' and current_type == 'private' or current_text == '/start{}'.format(BOT_NAME):
				print('Added', current_id)
				storeID(current_id)
			elif current_text == '/stop' and current_type == 'private' or current_text == '/stop{}'.format(BOT_NAME):
				print('Removed', current_id)
				removeID(current_id)

		if update_id > 0:
			with open('msg.txt', 'w') as f:
				f.write(str(update_id + 1))

	with open('id.txt', 'w') as f:
		f.write('\n'.join(allChatID))

def getNews():
	r = requests.get('https://webview.fate-go.us/iframe/maintenance/')
	return re.findall(r'<a href=\"(.+)\" class=\".+\">', r.text), re.findall(r'<span class=\"title\">(.+)\((.+) .{3}\)</span>', r.text)

def maintenance():
	updates = ''
	link, section = getNews()
	for i in zip(link, section):
		href = 'https://webview.fate-go.us' + i[0]
		href = '[{}]({})'.format(href, href)
		maintain = datetime.strptime(i[1][1].strip() + ' {}'.format(i[0].split('/')[2]), '%m-%d %H:%M %Y') + timedelta(hours=SGT)

		if maintain - datetime.now() > timedelta(minutes=1):
			time = maintain.strftime("%A %d/%m %I:%M%p")
			text = i[1][0].strip()
			updates += '{}: {}\nMaintenance starts at: {}\n{}'.format(maintain.strftime('%d/%m/%y'), text, maintain.strftime("%I:%M%p SGT (%A)"), href) +'\n\n'

	return updates.strip()

def blastMaintain(whut, cid, details):
	sendMessage(int(cid), '*Maintenance updates:*\n{}\n_~ Astolfo_ ♥'.format(details))

def main():
	print('------- Started -------')
	print(API_TOKEN)
	while True:
		time = str(datetime.now().time()).split(':')
		
		if int(time[0]) == 12 + TIMEZONE and int(time[1]) == 0:
			getNew()
			update = maintenance()
			for i in allChatID:
				print('Blasting', i)
				threading.Thread(target=blastMsg, args=(None, i)).start()
				if update != '':
					threading.Thread(target=blastMaintain, args=(None, i, update)).start()

		sleep(REFRESH_RATE)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as e:
		print('\nStopping server')
	except Exception as e:
		raise e
