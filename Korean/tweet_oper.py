import re
import json

# Counts the number of tweets per topic
def topic_count(fname):
	with open(fname) as f:
		tweets = f.read()

	count = 0

	print("\n########Korean Tweet Count##########\n")

	politicsRegex = re.compile(r'\"topic\":\s?\"Politics\"')
	match = politicsRegex.findall(tweets)
	count += len(match)
	print("topic - Politics: ",len(match))

	politicsRegex = re.compile(r'\"topic\":\s?\"Tech\"')
	match = politicsRegex.findall(tweets)
	count += len(match)
	print("topic - Tech: ",len(match))

	politicsRegex = re.compile(r'\"topic\":\s?\"World News\"')
	match = politicsRegex.findall(tweets)
	count += len(match)
	print("topic - World News: ",len(match))

	politicsRegex = re.compile(r'\"topic\":\s?\"T.V. Series\"')
	match = politicsRegex.findall(tweets)
	count += len(match)
	print("topic - T.V. Series: ",len(match))

	politicsRegex = re.compile(r'\"topic\":\s?\"Sports\"')
	match = politicsRegex.findall(tweets)
	count += len(match)
	print("topic - Sports: ",len(match))
	
	print("\n\nTotal Tweets: ",count)
	

# filters the tweets 
def tweets(fname):

	# Correcting dates in all tweets

	with open(fname) as f:
		tweets = f.read()
# "tweet_date": "2016-09-11T02:00:00Z"
	datePattern = re.compile(r'(\"tweet_date\":\s?\")(\d{4}\-\d{2}\-\d{2}T\d{2}\:\d{2}\:\d{2})\"')

	text1 = datePattern.sub(r'\1\2Z"',tweets)


	# Correcting coordinates

	# "tweet_loc": []
	locPatter = re.compile(r'(\"tweet_loc\":\s?)(\[\])')
	text2 = locPatter.sub(r'\1null',text1)

	# "tweet_loc": [151.19981289, -33.87429942]
	# "tweet_loc": "[37.090240, -95.712891]"

	locPatter2 = re.compile(r'(\"tweet_loc\":\s?)(\[)(\-?\d+\.\d+)(\,\s?)(\-?\d+\.\d+)(\])')
	# match = locPatter2.findall(text2)
	# print(match)
	text = locPatter2.sub(r'\1"\5\4\3"',text2)
	# print(text)


	# writing the changes to file
	f = open(fname,'w')
	f.write(text)
	f.close()	

	print('Successful....')

# topic_count("index4_korean.jsonl")
tweets("index4_korean.jsonl")
