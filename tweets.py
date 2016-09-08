import re
import json
import tweepy
import datetime
import time

# initializations
tweet_id = 1

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
	# print(text, end='\n\n')
	url_regex = r'(https|http)(:(\w|.|\/)+(\s|\n)?)?'
	hashtag_regex = r'#(\w|\.|\/|\')+(\s|\n)?'
	mentions_regex = r'(RT\s)?@(\w|\.|\/)+(\:|\s)?'
	emoji_compiled_regex = re.compile(u'['
    u'\U0001F300-\U0001F64F'
    u'\U0001F680-\U0001F6FF'
    u'\u2600-\u26FF\u2700-\u27BF]+', re.UNICODE)

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
	return text, emojis

print(tweet_filter('Donald Trump just cozied up even closer to Putin 😌 http://huff.to/2cj67ii '))

def load_document(tweets, topic, tweet_id):
	document = []
	for tweet in tweets:

		tweet_data = {}
		tweet_data['id'] = tweet_id
		tweet_data['topic'] = topic
		tweet_data['tweet_lang'] = tweet.lang
		tweet_data['tweet_text'] = tweet.text

		if tweet.lang == 'en':
			tweet_data['ttext_en'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
			tweet_data['ttext_en'] = tweet_data['ttext_en'].strip()

		elif tweet.lang == 'es':
			tweet_data['ttext_es'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
			tweet_data['ttext_es'] = tweet_data['ttext_es'].strip()

		elif tweet.lang == 'tr':
			tweet_data['ttext_tr'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
			tweet_data['ttext_tr'] = tweet_data['ttext_tr'].strip()
			
		elif tweet.lang == 'ko' :
			tweet_data['ttext_ko'],tweet_data['tweet_emoticons'] = tweet_filter(tweet.text)
			tweet_data['ttext_ko'] = tweet_data['ttext_ko'].strip()

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

		tweet_data['tweet_loc'] = tweet.coordinates
		
		# rounding off time
		tdatetime = tweet.created_at
		minute  = tdatetime.minute
		second = tdatetime.second

		if minute < 30:
			new_date = tdatetime - datetime.timedelta(minutes=minute,seconds=second)
		else:
			new_date = tdatetime - datetime.timedelta(minutes=minute,seconds=second)
			new_date = new_date + datetime.timedelta(hours=1)

		print('old_date: ',tdatetime)
		print('time: ',new_date)

		tweet_data['tweet_date'] = str(new_date)	

		# appending the json to a document
		document.append(json.dumps(tweet_data))
		tweet_id += 1


	return document, tweet_id

# english
# tweets = api.search(q="Election2016",lang="en")
# eng_document, tweet_id = load_document(tweets, 'Politics', tweet_id)

# for doc in eng_document:
# 	document = json.loads(doc)
# 	print('id: ',document['id'],end='\n')
# 	print('Text: ',document['tweet_text'],end='\n')
# 	print('url: ',document['tweet_urls'],end='\n')
# 	print('hashtags: ',document['tweet_hashtags'],end='\n')
# 	print('mentions: ',document['tweet_mentions'],end='\n')
# 	print('created time: ',document['tweet_date'],end='\n')
# 	print('emoticons: ',document['tweet_emoticons'],end='\n')
# 	print('Shortened text:',document['ttext_en'],end='\n\n')

# streaming data
class Streamer(tweepy.StreamListener):

	# list of status objects
	streamed_data = []
	_count = 0

	# tweepy passes on data from on_data method to on_status method	
	def on_status(self, data):
		print(data,end='\n')
		Streamer.streamed_data.append(data)

		Streamer._count += 1
		if Streamer._count == 5:
			return False

    #returning False in on_data disconnects the stream
	def on_error(self, status_code):
		if status_code == 420:
			return False

def stream_twitter():
	twitterStream = tweepy.Stream(auth = api.auth, listener=Streamer())
	twitterStream.filter(track=['Election2016'])
	return Streamer.streamed_data

tweets = stream_twitter()
target = open('eng_streamed_tweets.jsonl','w')
document, tweet_id = load_document(tweets, 'Politics', tweet_id)

for tweet in document:
	target.write(tweet)
	target.write('\n')

target.close()