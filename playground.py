import requests

TOKEN = "xoxb-44822465026-765690064661-zMxFtAQv8mfcppH2xrzajWxy"
api_pre = "https://slack.com/api/"


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
	member_names = [member_name for member_name in member_names if member_name != -1]
	return member_ids, member_names

if __name__ == "__main__":
	member_ids, member_names = get_channel_members("test-slackbots")
	print(member_ids, member_names)