import requests
import re
import numpy as np
import json

TOKEN = "hidden"
api_pre = "https://slack.com/api/"

# sets global TOKEN by api file
def get_token(file_name: str):
	global TOKEN
	with open(file_name, "r") as f:
		TOKEN = re.sub(r'[^a-zA-Z0-9-]+', '', f.readline())

# given channel name, gets internal slack id value 
def get_channel_id(name: str):
	URL = api_pre + "conversations.list"
	PARAMS = {
		'token': TOKEN,
		'limit': 1000,
	}
	r = requests.get(url = URL, params = PARAMS)
	data = r.json()
	for ch in data['channels']:
		if ch['name'] == 'test-slackbots':
			return ch['id']
	return -1

# given a user id, gets the actual name of user
def get_user_name(user_id: str):
	URL = api_pre + "users.info"
	PARAMS = {
		'token': TOKEN,
		'user': user_id,
	}
	r = requests.get(url = URL, params = PARAMS)
	data = r.json()
	if data['user']['is_bot']:
		return -1
	return data['user']['real_name']

# gets ids and names of all members in a channel
def get_channel_members(name: str):
	ch_id = get_channel_id(name)
	URL = api_pre + "channels.info"
	PARAMS = {
		'token': TOKEN,
		'channel': ch_id,
	}
	r = requests.get(url = URL, params = PARAMS)
	data = r.json()
	member_ids = data['channel']['members']

	member_names = [get_user_name(user_id) for user_id in member_ids]
	member_ids = [user_id for user_id, member_name in zip(member_ids, member_names) if member_name != -1]
	member_names = [member_name for member_name in member_names if member_name != -1]

	return member_ids, member_names

def create_welcome_message(user_names: [str], user_ids: [str]):
	message_text = "Hello " + ("<@%s>, " * (len(user_ids) - 1)) % tuple(user_ids[:-1])
	message_text = message_text[:-2] + " and <@%s>!" % user_ids[-1]
	message_text += "\n #TODO: Welcome message"
	return message_text

def create_channel_message(pairings: [[str]]):
	message_text = "This week's pairings are: \n"
	for group in pairings:
		message_text += (("<@%s>,     " * len(group)) % tuple(group))[:-5]
	return message_text  

def send_users_message(users: [str], message: str):
	# open the channel
	URL = api_pre + "conversations.open"
	user_str = ",".join(users)
	DATA = {
		"token": TOKEN,
		"users": user_str,
	}
	data = requests.post(url = URL, data=DATA).json()
	if not data['ok']:
		return -1

	channel_id = data['channel']['id']
	URL = api_pre + "chat.postMessage"
	DATA = {
		"token": TOKEN,
		"channel": channel_id,
		"text": message,
	}
	return requests.post(url = URL, data=DATA).json()

# sends message to a channel
def send_channel_message(channel: str, message: str):
	URL = api_pre + "chat.postMessage"
	DATA = {
		"token": TOKEN,
		"channel": channel,
		"text": message,
	}
	return requests.post(url = URL, data=DATA).json()

if __name__ == "__main__":
	get_token("API_KEY")
	channel = "test-slackbots"
	pairing_groups = []

	member_ids, member_names = get_channel_members(channel)
	perm = np.random.permutation(len(member_ids))
	for i in range(0, len(member_ids) - 1, 2):
		group_names = [member_names[perm[i]], member_names[perm[i+1]]]
		group_ids = [member_ids[perm[i]], member_ids[perm[i+1]]]
		if i + 2 == len(member_ids) - 1:
			group_names += [member_names[perm[i+2]]]
			group_ids += [member_ids[perm[i+2]]]
		pairing_groups.append(group_ids)
		message = create_welcome_message(group_names, group_ids)
		print(send_users_message(group_ids, message))

	channel_message = create_channel_message(pairing_groups)
	send_channel_message(get_channel_id(channel), channel_message)