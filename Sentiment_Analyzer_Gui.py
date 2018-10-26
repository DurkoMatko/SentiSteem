from tkinter import *
from subprocess import call
import sys
import os
import ConfigParser
import shutil
import pickle
import csv
import collections
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from dateutil import parser
from MilestoneClassifier.MulticlassMilestoneClassifier import MulticlassMilestoneClassifier, PredictionMode, TrainingMode
from Wordcloud_Generator import Wordcloud_Generator

def downloadTweets():
	#build Exporter command
	cmdCommand = "python2.7 GetOldTweets-python-master/Exporter.py"
	cmdCommand = cmdCommand + " --since " + since.get()
	cmdCommand = cmdCommand + " --until " + until.get()

	if (len(near.get()) != 0):
		cmdCommand = cmdCommand + " --near " + near.get()
	if (len(within.get()) != 0):
		cmdCommand = cmdCommand + " --within " + within.get()
	if (len(language.get()) != 0):
		cmdCommand = cmdCommand + " --lang '" + language.get() + "'"


	cmdCommand = cmdCommand + " --maxtweets " + maxtweets.get()
	cmdCommand = cmdCommand + " --querysearch '" + querysearch.get() + "'"
	outputName = output.get() + "_" + maxtweets.get() + ".csv"
	cmdCommand = cmdCommand + " --output='" + outputName + "'"

	#execute Exporter command
	os.popen(cmdCommand).readlines()

	#copy file to configured tweets folder
	tweetsFolder = config.get('FolderTree', 'tweetsFolder')
	shutil.move(outputName, tweetsFolder+"/"+outputName)

##################### PLOTTING ###################################
def getDatesAndScores(reader,classifier):
    #create corpus of tweets to be analyzed
    tweetsCorpus = []
    dates = []

    print "Creating a corpus from tweets to be analyzed"

    for row in reader:
        #create arrays of tweets to analyze
        tweetsCorpus.append(unicode(row[4], errors='ignore'))
        dates.append(parser.parse(row[1].split(' ', 1)[0]).date())

    #make prediction
    print "Predicting sentiment scores for tweets corpus"
    #scores = scikitModel.predict(vectorizedTweetsCorpus)
    scores = classifier.predict(corpus=tweetsCorpus,mode=PredictionMode.BINARY_CONFIDENCE)

    #not usable if using confidence values
    #print "Number of analyzed tweets:" + str(len(scores))
    #print "Number of positive tweets" + str(sum(scores == 1))
    #print "Number of negative tweets" + str(sum(scores == 0))

    #analyze quality attribute related tweets and their sentiment
    #analyzeIsoSentiment(mainn=mainn, use=use, secur=secur, scores=scores)

    #process sentimentData scores
    sentimentScoresDict = dict()
    flooredSentimentScoresDict = dict()
    dateCounts = dict()
    flooredDateCounts = dict()
    averageScores = dict()
    flooredAverageScores = dict()

    print "Processing sentiment scores returned for tweets corpus"
    sum = 0
    for idx, score in enumerate(scores):

        correspondingDate = dates[idx]
        sum = sum + score

        if (correspondingDate in sentimentScoresDict):
            sentimentScoresDict[correspondingDate] = sentimentScoresDict[correspondingDate] + score
            dateCounts[correspondingDate] = dateCounts[correspondingDate] + 1;
            correspondingDate = correspondingDate.replace(day=1)
            flooredSentimentScoresDict[correspondingDate] = flooredSentimentScoresDict[correspondingDate] + score
            flooredDateCounts[correspondingDate] = flooredDateCounts[correspondingDate] + 1;
        else:
            sentimentScoresDict[correspondingDate] = score
            dateCounts[correspondingDate] = 1;
            correspondingDate = correspondingDate.replace(day=1)
            flooredSentimentScoresDict[correspondingDate] = score
            flooredDateCounts[correspondingDate] = 1

    print str(sum / len(scores))

    #calculate average scores for every day
    print "Calculating average scores for every day"
    for date, scoreSum in sentimentScoresDict.iteritems():
        averageScores[date] = scoreSum / dateCounts[date]

    #calculate average scores for each year-month
    print "Calculating average scores for year-month combinations"
    for flooredDate, scoreSum in flooredSentimentScoresDict.iteritems():
        flooredAverageScores[flooredDate] = scoreSum / flooredDateCounts[flooredDate]

    return averageScores.keys(), averageScores.values(), flooredAverageScores.keys(), flooredAverageScores.values()


def executeAnalysis():
	chartsFolder = config.get('FolderTree', 'chartsFolder')
	wordcloudGenerator = Wordcloud_Generator(config.get('Wordcloud', 'commonWords'))
	wordcloudGenerator.createWordcloud(chartsFolder)

	f = open("trainedClassifier.pickle", 'rb')
	myClassifier = pickle.load(f)
	f.close()

	# get the tweets file
	mypath = os.path.dirname(__file__)
	tweetsFolder = config.get('FolderTree', 'tweetsFolder')
	tweetFilesPath = os.path.join(mypath, tweetsFolder)
	tweetFiles = [f for f in os.listdir(tweetFilesPath) if os.path.isfile(os.path.join(tweetFilesPath, f))]

	# analyze each tweets file
	for file in tweetFiles:
		with open(os.path.join(tweetFilesPath, file)) as csvFile:
			reader = csv.reader(csvFile, delimiter=';')
			reader.next()  #pass headers
			dates, scores, flooredDates, flooredScores = getDatesAndScores(reader=reader, classifier=myClassifier)

			#this plot looks too chaotic, data need to be aggregated
			#passedDays = convertDatesToPassedDays(dates)
			#plotPolynomials(minDate=min(dates), passedDays=passedDays, scores=scores, mypath=mypath, picNum=1)

			flooredPassedDays = convertDatesToPassedDays(dates=flooredDates)
			plotPolynomials(minDate=min(dates), passedDays=flooredPassedDays, scores=flooredScores, chartsFolder=chartsFolder, picNum=2)

			csvFile.close()



def convertDatesToPassedDays(dates):
    minDate = min(dates)
    passedDays = []

    for date in dates:
        passedDays.append(abs((date - minDate).days))
    return passedDays

def convertPassedDaysToDates(minDate,days):
    dates = []

    for passed in days:
        dates.append(minDate + dt.timedelta(days=passed))

    return dates

def plotPolynomials(minDate,passedDays,scores,chartsFolder,picNum):
    x = passedDays
    y = scores
    print "max x:" + str(max(x))
    # calculate polynomial
    z2 = np.polyfit(x, y, 2)
    z3 = np.polyfit(x, y, 3)
    z4 = np.polyfit(x, y, 4)
    f2 = np.poly1d(z2)
    f3 = np.poly1d(z3)
    f4 = np.poly1d(z4)

    # calculate new x's and y's for regression
    x_new = np.linspace(0, max(x), 200)
    y_new2 = f2(x_new)
    y_new3 = f3(x_new)
    y_new4 = f4(x_new)

    #revert original x-axis passed days to date format
    original_dates = convertPassedDaysToDates(minDate=minDate,days=passedDays)

    #revert regression x-axis values to datetime format
    regression_dates = convertPassedDaysToDates(minDate=minDate, days=x_new)

    # set x-axis labels to datetime format
    fig, ax = plt.subplots()
    fig.autofmt_xdate()

    # plot original and regression data
    plt.plot(original_dates, y, 'o')
    plt.ylim(ymax=max(y)+0.025, ymin=min(y)-0.025)
    plt.grid()

    plt.plot(regression_dates, y_new2, '.', label='quadratic polynomial fit')
    plt.plot(regression_dates, y_new3, '-',label='cubic polynomial fit')
    plt.plot(regression_dates,y_new4, '--',label='quartic polynomial fit')


    # if it is cryptocurrency, get history prices
    #cryptoPricesPath = os.path.join(mypath, 'cryptoPrices')
    #priceFiles = [f for f in os.listdir(cryptoPricesPath) if os.path.isfile(os.path.join(cryptoPricesPath, f))]

    #if projectName in priceFiles:
    #    #get prices and dates
    #    priceDates,prices = getCryptoPrices(projectName=projectName, cryptoPricesPath=cryptoPricesPath)
    #    #insert first price 0 to make the graph nicer
    #    priceDates.insert(len(priceDates), min(original_dates))
    #    prices.insert(len(prices),0)

     #   #add secondary y-axis
    #    ax2 = ax.twinx()
    #    ax2.plot(priceDates, prices,'grey',label='Price')

    legend = ax.legend(loc='lower left', shadow=True)
    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')
    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
    plt.title("")
    #plt.show()
    plt.savefig(chartsFolder+"/"+str(picNum)+".png")
    plt.close()


if __name__ == '__main__':
	config = ConfigParser.ConfigParser()
	config.readfp(open(r'app.config'))
	GUI_WIDTH = int(config.get('GUI', 'guiWidth'))

	analyzerGui = Tk()
	since = StringVar()
	until = StringVar()
	near = StringVar()
	within = StringVar()
	maxtweets = StringVar()
	language = StringVar()
	querysearch = StringVar()
	output = StringVar()

	analyzerGui.geometry(str(GUI_WIDTH)+'x700+300+100')
	analyzerGui.title('Sentiment analyzer by @matkodurko')

	# get tweets elements
	mlabel = Label(analyzerGui, text="Get tweets").pack()
	Label(analyzerGui, text='Since', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=since).pack()
	Label(analyzerGui, text='Until', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=until).pack()
	Label(analyzerGui, text='Near', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=near).pack()
	Label(analyzerGui, text='Within', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=within).pack()
	Label(analyzerGui, text='Maxtweets', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=maxtweets).pack()
	Label(analyzerGui, text='Langugae', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=language).pack()
	Label(analyzerGui, text='Query', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=querysearch).pack()
	Label(analyzerGui, text='Output', justify=LEFT).pack()  # .grid(sticky=W, column=1, row=0)
	Entry(analyzerGui, textvariable=output).pack()
	Button(analyzerGui, text="Download!", command=downloadTweets, fg="red").pack()
	Frame(analyzerGui, height=1, width=GUI_WIDTH, bg="black").pack()

	# execute sentiment analysis
	mlabel = Label(analyzerGui, text="Sentiment analysis execution").pack()

	Button(analyzerGui, text="Execute analysis!", command=executeAnalysis, fg="red").pack()
	Frame(analyzerGui, height=1, width=GUI_WIDTH, bg="black").pack()


	analyzerGui.mainloop()
