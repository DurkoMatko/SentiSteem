# -*- coding: utf-8 -*-
import sys, os, csv
import re #regex
import tweepy
import operator
import unicodedata  #smileys
import datetime
import json
import pickle
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import defaultdict
from dateutil import parser

class Wordcloud_Generator:

	def __init__(self, commonWords, reportFileName, tweetsFolder):
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
		self.reportFileName = reportFileName
		self.tweetsFolder = tweetsFolder

	def createWordcloud(self, chartsFolder, maskFolder, maxCloudWords, borderDateString):
		# strings to store all the words from tweets
		words = ""
		wordsAfter = ""

		borderDate = parser.parse(borderDateString)

		#read tweets
		tweetFilesPath = os.path.join(self.mypath, self.tweetsFolder)
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


		#FIX: Wordcloud interprets word HELLO-WORLD as two separate words, therefore I'm replacing "-" with empty string to make the word unique
		words = words.replace("-", "")
		wordsAfter = wordsAfter.replace("-", "")

		#FIX: "/" interpreted as space as well, causing word STATUS to be popular
		words = words.replace("/", "")
		wordsAfter = wordsAfter.replace("/", "")

		wordcloud = WordCloud(stopwords=STOPWORDS, max_words=int(maxCloudWords)).generate(words)
		wordcloud2 = WordCloud(stopwords=STOPWORDS, background_color='white', max_words=int(maxCloudWords)).generate(wordsAfter)
		self.plotWordcloud(wordcloud, wordcloud2,chartsFolder,'CommonWords')

		#now plot the same but without shared words
		uniqueWords = self.getUniqueWords(words, wordsAfter)
		uniqueWordsAfter = self.getUniqueWords(wordsAfter, words)
		wordcloud = WordCloud(stopwords=STOPWORDS, max_words=int(maxCloudWords)).generate(uniqueWords)
		wordcloud2 = WordCloud(stopwords=STOPWORDS, background_color='white', max_words=int(maxCloudWords)).generate(uniqueWordsAfter)
		self.plotWordcloud(wordcloud, wordcloud2, chartsFolder, 'UniqueWords')

		#replace common words in the report file
		with open(self.reportFileName) as f:
			newText = f.read().replace('<EXCLUDED_WORDS_LIST>', ",".join(self.commonWords))
			newText = newText.replace('<BORDER_DATE>', borderDateString)
		with open(self.reportFileName, "w") as f:
			f.write(newText)

		#generate shaped wordcloud if there's a mask
		maskFolderPath = os.path.join(self.mypath, maskFolder)
		if any(File.endswith(".png") for File in os.listdir(maskFolderPath)):
			self.createShapedWordcloud(words+wordsAfter, chartsFolder, maskFolder);

	def transform_mask_format(self,val):
		if val == 0:
			return 255
		else:
			return val
	
	def createShapedWordcloud(self, allWords, chartsFolder, maskFolder):
		wine_mask = np.array(Image.open(maskFolder+"/mask.png"))
		
		transformed_wine_mask = np.ndarray((wine_mask.shape[0],wine_mask.shape[1]), np.int32)
		for i in range(len(wine_mask)):
			transformed_wine_mask[i] = list(map(self.transform_mask_format, wine_mask[i]))

		wc = WordCloud(colormap="Reds", max_words=500, mask=transformed_wine_mask, stopwords=STOPWORDS, contour_width=1, contour_color='white')
			   
		wc.generate(allWords)
		wc.to_file(chartsFolder+"/shapedWords.png")


	#compares two comma separated strings and returns just unique words from the first string
	def getUniqueWords(self,commaSeparatedWords1, commaSeparatedWords2):
		words1 = commaSeparatedWords1.split(",")
		words2 = commaSeparatedWords2.split(",")
		wordset1 = set(words1)
		wordset2 = set(words2)
		uniqueWordsList = list(wordset1 - wordset2)
		#return uniqueWordsList
		return ','.join(map(str, uniqueWordsList))

	def isCommon(self,word):
		for comm in self.commonWords:
			stripped = word.strip().decode('utf-8')
			if comm == stripped:
				return True
		return False

	#return word.lower() in self.commonWords;

	def plotWordcloud(self,before, after, chartsFolder, picName):
		plt.subplot(211)
		plt.title('Before')
		plt.axis('off')
		plt.imshow(before, interpolation="bilinear")   #interpolation needed because Matplotlib v2 doesn't do image interpolation for imshow any more (https://github.com/amueller/word_cloud/issues/188)

		plt.subplot(212)
		plt.title('After')
		plt.axis('off')
		plt.imshow(after, interpolation="bilinear")    #interpolation needed because Matplotlib v2 doesn't do image interpolation for imshow any more(https://github.com/amueller/word_cloud/issues/188)

		plt.savefig(chartsFolder + "/" + picName + ".png")
		plt.close()


