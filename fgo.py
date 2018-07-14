#!/usr/bin/env python3

import requests
import json
from pprint import pprint
from time import sleep
from datetime import datetime
import threading
from random import choice
from os import environ

API = 'https://api.telegram.org/bot'
API_TOKEN = environ['API_TOKEN']
URL = API + API_TOKEN
TIMEZONE = -8
BOT_NAME = '@FGO_Platy_Bot'
REFRESH_RATE = 60

with open('id.txt') as f:
	allChatID = f.read().strip().split('\n')

with open('lines.txt') as f:
	lines = f.read().strip().split('\n')

def getMe(): # Get info on bot
	r = requests.get(URL + '/getme')
	return json.loads(r.text)

def getUpdates(): # Get messages sent to bot
	r = requests.get(URL + '/getupdates')
	return json.loads(r.text)

def sendMessage(cid, text='Welcome to Fate Grind Order!'):
	payload = {'chat_id': cid, 'text': text}
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
	sendMessage(int(cid), '{}\nRemember to collect your daily login!'.format(choice(lines)))

def getNew():
	data = getUpdates()['result']

	with open('msg.txt', 'r') as f:
		location = int(f.read())

	for i in range(location, len(data)):
		current_id = data[i]['message']['chat']['id']
		try:
			current_text = data[i]['message']['text']
		except:
			current_text = ''
		current_type = data[i]['message']['chat']['type']
		
		if current_text == '/start' and current_type == 'private' or current_text == '/start' + BOT_NAME:
			print('Added', current_id)
			storeID(current_id)
		elif current_text == '/stop' and current_type == 'private' or current_text == '/stop' + BOT_NAME:
			print('Removed', current_id)
			removeID(current_id)

		with open('msg.txt', 'w') as f:
			f.write(str(i + 1))

	with open('id.txt', 'w') as f:
		f.write('\n'.join(allChatID))

def main():
	while True:
		time = str(datetime.now().time()).split(':')
		
		if int(time[0]) == 12 + TIMEZONE and int(time[1]) == 0:
			getNew()
			for i in allChatID:
				threading.Thread(target=blastMsg, args=(None, i)).start()

		sleep(REFRESH_RATE)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt as e:
		print('\nStopping server')
	except Exception as e:
		raise e
