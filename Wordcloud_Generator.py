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
		self.regexp = re.compile(r'[!@#$:).;,?&]')
		self.commonWords = json.loads(commonWords)

		# dataset with sentiment-wise evaluated words using values within interval <-5,5>
		self.sentiment_dict = {}
		for line in open('AFFINN-111.txt'):
			word, score = line.split('\t')
			self.sentiment_dict[word] = int(score)

		self.mypath = os.path.dirname(__file__)

	def createWordcloud(self, chartsFolder, maxCloudWords, borderDate):
		# strings to store all the words from tweets
		words = ""
		wordsAfter = ""

		borderDate = parser.parse(borderDate)

		tweetFilesPath = os.path.join(self.mypath, 'tweets_To_Analyze')
		tweetFiles = [f for f in os.listdir(tweetFilesPath) if os.path.isfile(os.path.join(tweetFilesPath, f))]

		for file in tweetFiles:
			with open(os.path.join(tweetFilesPath, file)) as csvFile:
				reader = csv.reader(csvFile, delimiter=';')
				reader.next()  # pass headers
				for row in reader:
					tweet = row[4]
					# iterate over words in tweets
					for word in tweet.split():
						if not self.emoji_pattern.match(word) and not self.isCommon(word.lower()):
							if self.regexp.search(word):
								continue;
							postedDate = parser.parse(row[1].split(' ', 1)[0])
							if postedDate < borderDate:
								words = words + "," + word
							else:
								wordsAfter = wordsAfter + "," + word

		wordcloud = WordCloud(stopwords=STOPWORDS, max_words=int(maxCloudWords)).generate(words)
		wordcloud2 = WordCloud(stopwords=STOPWORDS, background_color='white', max_words=int(maxCloudWords)).generate(wordsAfter)
		self.plotWordcloud(wordcloud, wordcloud2,chartsFolder,3)

		#now plot the same but without shared words
		uniqueWords = self.getUniqueWords(words, wordsAfter)
		print uniqueWords
		uniqueWordsAfter = self.getUniqueWords(wordsAfter, words)
		wordcloud = WordCloud(stopwords=STOPWORDS, max_words=int(maxCloudWords)).generate(uniqueWords)
		wordcloud2 = WordCloud(stopwords=STOPWORDS, background_color='white', max_words=int(maxCloudWords)).generate(uniqueWordsAfter)
		self.plotWordcloud(wordcloud, wordcloud2, chartsFolder, 4)

	#compares two comma separated strings and returns just unique words from the first string
	def getUniqueWords(self,commaSeparatedWords1, commaSeparatedWords2):
		words1 = commaSeparatedWords1.split(",")
		words2 = commaSeparatedWords2.split(",")
		uniqueWordsList = list(set(words1) - set(words2))
		#return uniqueWordsList
		return ','.join(map(str, uniqueWordsList))

	def isCommon(self,word):
		for comm in self.commonWords:
			stripped = word.strip().decode('utf-8')
			if comm == stripped:
				return True
		return False

	#return word.lower() in self.commonWords;

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

