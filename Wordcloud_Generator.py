# -*- coding: utf-8 -*-
import sys, os, csv
import re #regex
import tweepy
import operator
import unicodedata  #smileys
import datetime
import json
import pickle
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import defaultdict
from dateutil import parser

class Wordcloud_Generator:

	def __init__(self, commonWords):
		self.emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE)
		self.hashtag_pattern = re.compile(r"#(\w+)")
		self.commonWords = json.loads(commonWords)

		# dataset with sentiment-wise evaluated words using values within interval <-5,5>
		self.sentiment_dict = {}
		for line in open('AFFINN-111.txt'):
			word, score = line.split('\t')
			self.sentiment_dict[word] = int(score)

		self.mypath = os.path.dirname(__file__)

	def createWordcloud(self, chartsFolder):
		# strings to store all the words from tweets
		emojis = ""
		hashtags = ""
		words = ""
		hashtagsAfter = ""
		wordsAfter = ""

		tweetFilesPath = os.path.join(self.mypath, 'tweets_To_Analyze')
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
						if self.emoji_pattern.match(word):
							emojis = emojis + ", " + word
						elif self.hashtag_pattern.match(word):
							hashtags = hashtags + ", " + word
						elif not self.isCommon(word.lower()):
							# analyze emotion semantics of particular word
							# overalTweetEmotion = overalTweetEmotion + sentiment_dict.get(word,0)
							words = words + ", " + word

		tweetFilesPath = os.path.join(self.mypath, 'tweets_To_Analyze')
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
						if self.emoji_pattern.match(word):
							emojis = emojis + ", " + word
						elif self.hashtag_pattern.match(word):
							hashtagsAfter = hashtagsAfter + ", " + word
						elif not self.isCommon(word.lower()):
							# analyze emotion semantics of particular word
							# overalTweetEmotion = overalTweetEmotion + sentiment_dict.get(word,0)
							wordsAfter = wordsAfter + ", " + word

		wordcloud = WordCloud(stopwords=STOPWORDS, max_words=10).generate(words)
		wordcloud2 = WordCloud(stopwords=STOPWORDS, background_color='white', max_words=10).generate(wordsAfter)
		self.plotWordcloud(wordcloud, wordcloud2,chartsFolder,3)

	def isCommon(self,word):
		return word.lower() in self.commonWords;

	def plotWordcloud(self,before, after, chartsFolder, picNum):
		plt.subplot(211)
		plt.title('Before')
		plt.axis('off')
		plt.imshow(before)

		plt.subplot(212)
		plt.title('After')
		plt.axis('off')
		plt.imshow(after)

		plt.savefig(chartsFolder + "/" + str(picNum) + ".png")
		plt.close()

