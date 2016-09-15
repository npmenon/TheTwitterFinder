import re
import json
import tweepy
import datetime
import time

# Reading secure info from secret_file
access_keys = None
with open('access_keys.json') as json_data:
    access_keys = json.load(json_data)

# Authentication using access tokens
authentication = tweepy.OAuthHandler(access_keys["consumer_key"], access_keys["consumer_secret"])
authentication.set_access_token(access_keys["access_token"], access_keys["access_secret"])

api = tweepy.API(authentication)

# tweet filtering - punctuation, emoticons, emojis, kaomojis, hashtags, mentions, URLs 
# and other Twitter discourse tokens
def tweet_filter(text):
	url_regex = r'(https|http)(:(\w|.|\/)+(\s|\n)?)?'
	hashtag_regex = r'#(\w|\.|\/|\')+(\s|\n)?'
	mentions_regex = r'(RT\s)?@(\w|\.|\/)+(\:|\s)?'
	emoji_compiled_regex = re.compile(u'['
    u'\U0001F300-\U0001F64F'
    u'\U0001F680-\U0001F6FF'
    u'\u2600-\u26FF\u2700-\u27BF]+', re.UNICODE)
	punct_regex = r'(\-|\:|\!|\%|\*|\)|\(|\+|\-|\/|\$|\'|\"|\*|\[|\]|\{|\}|\#|\^|\,|\.|\?)+'
	entity_regex = r'&\w+;'

	# remove hyperlinks
	pattern = re.compile(url_regex)
	text = pattern.sub('',text)

	# remove hashtags
	pattern = re.compile(hashtag_regex)
	text = pattern.sub('',text)	

	# remove mentions
	pattern = re.compile(mentions_regex)
	text = pattern.sub('',text)	

	# remove emojis
	emojis = None
	match = emoji_compiled_regex.findall(text)
	if match:
		emojis = match
	text = emoji_compiled_regex.sub('',text)	

	# remove punctuations
	pattern = re.compile(punct_regex)
	text = pattern.sub('',text)	

	# remove entities
	pattern = re.compile(entity_regex)
	text = pattern.sub('',text)	

	return text, emojis

date_handler = lambda obj: (
	obj.isoformat()
	if isinstance(obj, datetime.datetime)
	or isinstance(obj, datetime.date)
	else None
)

# If results only below a specific ID are, set max_id to that ID.
# else default to no upper limit, start from the most recent tweet matching the search query.

def load_document(tweets, topic, tweet_count):
	document = []
	max_id = tweets[-1].id
	for tweet in tweets:

		# to remove retweets
		try:
			if tweet.retweeted_status:
				continue
		except Exception:
			tweet_count += 1

			tweet_data = {}
			tweet_data['topic'] = topic
			tweet_data['tweet_lang'] = tweet.lang
			tweet_data['tweet_text'] = tweet.text

			if tweet.lang == 'en':
				tweet_data['text_en'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
				tweet_data['text_en'] = tweet_data['text_en'].strip()

			elif tweet.lang == 'es':
				tweet_data['text_es'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
				tweet_data['text_es'] = tweet_data['text_es'].strip()

			elif tweet.lang == 'tr':
				tweet_data['text_tr'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
				tweet_data['text_tr'] = tweet_data['text_tr'].strip()
				
			elif tweet.lang == 'ko' :
				tweet_data['text_ko'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
				tweet_data['text_ko'] = tweet_data['text_ko'].strip()

			# retrieving the urls
			tweet_data['tweet_urls'] = []
			for jsonurl in tweet.entities['urls']:
				tweet_data['tweet_urls'].append(jsonurl["expanded_url"])

			# retrieving the hashtags
			tweet_data['tweet_hashtags'] = []
			for jsontags in tweet.entities['hashtags']:
				tweet_data['tweet_hashtags'].append(jsontags["text"])

			# retrieving user mentions
			tweet_data['tweet_mentions'] = []
			for jsonmention in tweet.entities['user_mentions']:
				tweet_data['tweet_mentions'].append(jsonmention["name"])

			tweet_data['tweet_loc'] = []
			if tweet.coordinates:
				tweet_data['tweet_loc'] = tweet.coordinates["coordinates"]
			
			# rounding off time
			tdatetime = tweet.created_at
			minute  = tdatetime.minute
			second = tdatetime.second

			if minute < 30:
				new_date = tdatetime - datetime.timedelta(minutes=minute,seconds=second)
			else:
				new_date = tdatetime - datetime.timedelta(minutes=minute,seconds=second)
				new_date = new_date + datetime.timedelta(hours=1)

			tweet_data['tweet_date'] = (new_date)	

			# appending the json to a document
			document.append(json.dumps(tweet_data, default=date_handler,ensure_ascii=False))

	return document, tweet_count, max_id

# init
# topic = 'T.V. Series'
# topic = 'Sports'
topic = 'Politics'
# topic = 'Tech'
# topic = 'World News'
_tweet_count = 0
document = []

# max_id of tweets retrieved from a file
id_file = open('max_id_file.txt','r')
max_id = int(id_file.read())
id_file.close()

# Crawls Turkish tweets
while _tweet_count < 500:

	try:
		if max_id <= 0:
			tweets = api.search(q="bize seçim",lang="tr")
		else:
			tweets = api.search(q="bize seçim",lang="tr",max_id=str(max_id - 1))
	except Exception as e:
		print("Error encontered: ",e)
		print('Exiting now')
		break

	if tweets:
		document, _tweet_count, max_id = load_document(tweets,topic, _tweet_count)
	else:
		print('No tweets')

	target = open('index2_turkish.jsonl','a')

	for tweet in document:
		target.write(tweet)
		target.write('\n')

	target.close()

print('Retrieved: ',_tweet_count,' tweets')
print('\nLast max_id: ',max_id)
id_file = open('max_id_file.txt','w')
id_file.write(str(max_id))
id_file.close()


# streaming data
class Streamer(tweepy.StreamListener):

	# list of status objects
	streamed_data = []
	_count = 0

	# tweepy passes on data from on_data method to on_status method	
	def on_status(self, data):
		print('Received: ',Streamer._count," documents")
		Streamer.streamed_data.append(data)

		Streamer._count += 1
		if Streamer._count == 200:
			return False

    #returning False in on_data disconnects the stream
	def on_error(self, status_code):
		if status_code == 420:
			return False

def stream_twitter():
	twitterStream = tweepy.Stream(auth = api.auth, listener=Streamer())
	# twitterStream.filter(track=['#SDF','@syrianrefugeeun','#PrayForSyria','#SyrianRefugees'])
	# twitterStream.filter(track=['#usopen'])
	# twitterStream.filter(track=['#apple'])
	twitterStream.filter(track=['gameofdaily'])
	return Streamer.streamed_data


# print('Starting to stream!\n')
# tweets = stream_twitter()
# target = open('index2_turkish.jsonl','a')
# document,_tweet_count = load_document(tweets, topic, _tweet_count)

# for tweet in document:
# 	target.write(tweet)
# 	target.write('\n')

# target.close()
# print('\nTotal streamed tweets: ',_tweet_count)


#========================================================================================

# tweets = api.search(q="us election",lang="tr")

# for tweet in tweets:
# 	print(tweet,end='\n\n')

# for doc in document:
# 	document = json.loads(doc)
# 	print('Text: ',document['tweet_text'],end='\n')
# 	print('url: ',document['tweet_urls'],end='\n')
# 	print('hashtags: ',document['tweet_hashtags'],end='\n')
# 	print('mentions: ',document['tweet_mentions'],end='\n')
# 	print('created time: ',document['tweet_date'],end='\n')
# 	print('emoticons: ',document['tweet_emoticons'],end='\n')
# 	print('Shortened text:',document['text_en'],end='\n\n')