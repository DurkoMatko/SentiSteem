# -*- coding: utf-8 -*-
import sys, os, csv
import re #regex
import tweepy
import operator
import unicodedata  #smileys
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from collections import defaultdict
import pickle
from dateutil import parser
import datetime

#yields data chronologicaly from the dictionary
def sortdict(d):
    for key in sorted(d): yield key,d[key]


def wordCloudGraph():

	#regexes for emoticons and hashtags
	emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
	hashtag_pattern = re.compile(r"#(\w+)")

	#strings to store all the words from tweets
	emojis = ""
	hashtags = ""
	words = ""
	hashtagsAfter = ""
	wordsAfter = ""

	#dataset with sentiment-wise evaluated words using values within interval <-5,5>
	sentiment_dict = {}
	for line in open('AFFINN-111.txt'):
		word, score = line.split('\t')
		sentiment_dict[word] = int(score)

	#values for tweet emotions
	worstEmotion = 0
	bestEmotion = 0
	#axes for line chart
	x=[]
	y=[]

	# set where to find tweets to analyze
	mypath = os.path.dirname(__file__)
	tweetFilesPath = os.path.join(mypath, 'tweets_To_Analyze')
	tweetFiles = [f for f in os.listdir(tweetFilesPath) if os.path.isfile(os.path.join(tweetFilesPath, f))]

	for file in tweetFiles:
		with open(os.path.join(tweetFilesPath, file)) as csvFile:
			reader = csv.reader(csvFile, delimiter=';')
			for row in reader:
				tweet = row[4]
				#timestamp = parser.parse(row[1].split(' ', 1)[0])
				overalTweetEmotion = 0
				#iterate over words in tweets
				for word in tweet.split():
					if emoji_pattern.match(word):
						emojis = emojis + ", " + word
					elif hashtag_pattern.match(word):
						hashtags = hashtags + ", " + word
					elif not isCommon(word.lower()):
							#analyze emotion semantics of particular word
							#overalTweetEmotion = overalTweetEmotion + sentiment_dict.get(word,0)
							words = words + ", " + word

	tweetFilesPath = os.path.join(mypath, 'tweets_To_Analyze')
	tweetFiles = [f for f in os.listdir(tweetFilesPath) if os.path.isfile(os.path.join(tweetFilesPath, f))]

	for file in tweetFiles:
		with open(os.path.join(tweetFilesPath, file)) as csvFile:
			reader = csv.reader(csvFile, delimiter=';')
			for row in reader:
				tweet = row[4]
				# timestamp = parser.parse(row[1].split(' ', 1)[0])
				overalTweetEmotion = 0
				# iterate over words in tweets
				for word in tweet.split():
					if emoji_pattern.match(word):
						emojis = emojis + ", " + word
					elif hashtag_pattern.match(word):
						hashtagsAfter = hashtagsAfter + ", " + word
					elif not isCommon(word.lower()):
						# analyze emotion semantics of particular word
						# overalTweetEmotion = overalTweetEmotion + sentiment_dict.get(word,0)
						wordsAfter = wordsAfter + ", " + word

	wordcloud = WordCloud(stopwords=STOPWORDS,max_words=10).generate(words)
	wordcloud2 = WordCloud(stopwords=STOPWORDS,background_color='white',max_words=10).generate(wordsAfter)
	createPlot(wordcloud,wordcloud2)

	'''print worstTweet
	print bestTweet'''

def isCommon(word):
	commonWords = ["new","via","price","dlvr","gl","eth","bitcoin",'bitcoin',"blockchain","btc","ethereum","crypto","cryptocurrency","twitter","exchange","https","reddit","pic","cryptocurrencies", "ly", "ift"]
	for comm in commonWords:
		if comm in word.lower():
			return True
	return False

def createPlot(before, after):
	plt.subplot(211)
	plt.title('Before')
	plt.axis('off')
	plt.imshow(before)

	plt.subplot(212)
	plt.title('After')
	plt.axis('off')
	plt.imshow(after)

	'''plt.subplot(313)
	plt.plot(x,y,'-')
	plt.title('Sentiment analysis over time')'''
	plt.show()



def main(argv):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	wordCloudGraph()


if __name__ == "__main__":
	main(sys.argv)
