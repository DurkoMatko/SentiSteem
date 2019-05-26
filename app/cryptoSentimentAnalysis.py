import os, csv, sys, re
import numpy as np
from dateutil import parser
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime as dt
import pickle
import collections
from MilestoneClassifier.MulticlassMilestoneClassifier import MulticlassMilestoneClassifier, PredictionMode, TrainingMode

reload(sys)
sys.setdefaultencoding('utf8')

def main(argv):
    # Create a corpus from training data
    corpus, labels = make_Corpus_From_Tweets(root_dir='datasets/Sentiment140')
    #corpus, labels = make_Corpus_From_Movies(root_dir='datasets/Movie_review_data')
    #corpus, labels = make_Corpus_From_Tweets(root_dir='datasets/Crypto_Labeled_Data')

    #find best performing vectorizer for feature extraction
    #tuneVectorizerParameters(corpus=corpus,labels=labels)

    #define vectorizer for corpus vectorization
    #vectorizer = TfidfVectorizer(min_df=5, max_df=0.9, sublinear_tf=True, stop_words='english')
    vectorizer = TfidfVectorizer()

    #find best parameters for classifiers
    #tuneModelParameters(corpus=corpus,labels=labels,vectorizer=vectorizer)


    #train on movies, evaluate tweets
    #train1_test2(corpus2,labels2,corpus1,labels1,vectorizer)
    #execute_crossValidation(fold_splits=4, corpus=corpus, labels=labels, vectorizer=vectorizer)
    #model3 = create_Models(corpus=corpus,labels=labels,vectorizer=)

    f = open("trainedClassifier.pickle", 'rb')
    myClassifier = pickle.load(f)
    f.close()

    #myClassifier = MulticlassMilestoneClassifier()
    #myClassifier.train(corpus=corpus,labels=labels,mode=TrainingMode.BINARY)
    #f = open("trainedClassifier.pickle", 'wb')
    #pickle.dump(myClassifier, f)
    #f.close()

    #playing with thresholds in confidence to differ among positive, negative and neutral tweets
    #PosNeg_thresholds_on_test_data(model=model3_logisticRegression,vectorizer=vectorizer)
    
    # set where to find tweets to analyze
    mypath = os.path.dirname(__file__)
    tweetFilesPath = os.path.join(mypath, 'tweets_To_Analyze')
    tweetFiles = [f for f in os.listdir(tweetFilesPath) if os.path.isfile(os.path.join(tweetFilesPath, f))]


    projectName = "bitcoin.csv"
    with open(os.path.join(tweetFilesPath,projectName)) as csvFile:
        reader = csv.reader(csvFile, delimiter=';')
        reader.next()
        print file
        dates, scores, flooredDates, flooredScores = getDatesAndScores(reader=reader, classifier=myClassifier)
        passedDays = convertDatesToPassedDays(dates)
        plotPolynomials(minDate=min(dates), passedDays=passedDays, scores=scores, projectName=projectName,mypath=mypath)
        flooredPassedDays = convertDatesToPassedDays(dates=flooredDates)
        plotPolynomials(minDate=min(dates),passedDays=flooredPassedDays, scores=flooredScores, projectName=projectName,mypath=mypath)

        csvFile.close()


def make_Corpus_From_Tweets(root_dir):
    print "Creating training corpus from training tweets"
    mypath = os.path.dirname(__file__)
    trainDataPath = os.path.join(mypath, root_dir)
    trainDataFiles = [f for f in os.listdir(trainDataPath) if os.path.isfile(os.path.join(trainDataPath, f))]

    corpus = []
    #initialization of numpy array needed (1,600,000 is size of my sentiment140 training dataset, 499 of test set)
    labels = np.zeros(1600000);
    for file in trainDataFiles:
        with open(os.path.join(mypath, root_dir+'/') + file) as trainingFile:
            reader = csv.reader(trainingFile, delimiter=',')
            iterator = -1;
            a = 0
            #for each tweet in file
            for row in reader:
                #if it's either positive or negative
                if (row[0] == "0" or row[0] == "4"):
                    #increase index because we're adding to corpus
                    iterator = iterator + 1
                    #add the tweet to corpus
                    corpus.append(unicode(preprocess(row[5]), errors='ignore'))
                    #add positive or negative label
                    if (row[0] == "0"):
                        labels[iterator] = 0
                    elif (row[0] == "4"):
                        labels[iterator] = 1

        trainingFile.close()
    return corpus,labels

def make_Corpus_From_Movies(root_dir):
    print "Creating training corpus from movie reviews"
    polarity_dirs = [os.path.join(os.path.join(os.path.dirname(__file__), root_dir),f) for f in os.listdir(os.path.join(os.path.dirname(__file__), root_dir))]
    #polarity_dirs = [os.path.join(root_dir, f) for f in os.listdir(root_dir)]
    corpus = []
    for polarity_dir in polarity_dirs:
        reviews = [os.path.join(polarity_dir, f) for f in os.listdir(polarity_dir)]
        for review in reviews:
            doc_string = "";
            with open(review) as rev:
                for line in rev:
                    doc_string = doc_string + line
            if not corpus:
                corpus = [doc_string]
            else:
                corpus.append(doc_string)

    labels = np.zeros(2000);
    labels[1000:]=1
    return corpus, labels

def make_Corpus_From_Test_Tweets(root_dir):
    print "Creating training corpus from training tweets"
    mypath = os.path.dirname(__file__)
    trainDataPath = os.path.join(mypath, root_dir)
    trainDataFiles = [f for f in os.listdir(trainDataPath) if os.path.isfile(os.path.join(trainDataPath, f))]

    testingCorpus = []
    #initialization of numpy array needed (1,600,000 is size of my sentiment140 training dataset, 499 of test set)
    labels = np.zeros(499);
    for file in trainDataFiles:
        with open(os.path.join(mypath, root_dir+'/') + file) as trainingFile:
            reader = csv.reader(trainingFile, delimiter=',')
            iterator = -1;
            #for each tweet in file
            for row in reader:
                if row[0]==2:
                    continue
                #increase index because we're adding to corpus
                iterator = iterator + 1
                #add the tweet to corpus
                testingCorpus.append(unicode(preprocess(row[5]), errors='ignore'))
                labels[iterator] = row[0]

        trainingFile.close()
    return testingCorpus,labels

def execute_crossValidation(fold_splits, corpus, labels, vectorizer):
    kf = StratifiedKFold(n_splits=fold_splits)

    #choose classifiers to evaluate
    iter=1;
    classifiers = [LinearSVC(), MultinomialNB(), BernoulliNB(),LogisticRegression()]
    names = ['LinearSVC', 'MultinomialNB', 'BernoulliNB','LogisticRegression']

    #performance metrics initialization
    crossValidationAccuracy = dict()
    confusionMetrices = dict()
    for name in names:
        crossValidationAccuracy[name] = []
        confusionMetrices[name] = np.zeros((2, 2));  #confusion matrix

    print "Starting n-fold training with number of folds:"+str(fold_splits)
    for train_index, test_index in kf.split(corpus, labels):
        #create arrays and corpuses according to current fold
        X_train = [corpus[i] for i in train_index]
        X_test = [corpus[i] for i in test_index]
        y_train, y_test = labels[train_index], labels[test_index]
        train_corpus_tf_idf = vectorizer.fit_transform(X_train)
        test_corpus_tf_idf = vectorizer.transform(X_test)

        #fit(train) models and check performance on testing part of data
        for name,clf in zip(names, classifiers):
            clf.fit(train_corpus_tf_idf, y_train)
            result = clf.predict(test_corpus_tf_idf)
            crossValidationAccuracy[name].append(accuracy_score(y_test,result))
            confusionMetrices[name] = confusionMetrices[name] + confusion_matrix(y_test, result)

        print "Models succesfully trained, number of iteration:" + str(iter)

        #iterator for logging messages
        iter = iter+1

    print str(fold_splits) + "-fold cross validation done, confusion matrices:"

    for name in names:
        print name
        print "Cross validation results: ",
        for item in crossValidationAccuracy[name]: print item,
        print "Cross validation average:" + str(sum(crossValidationAccuracy[name]) / len(crossValidationAccuracy[name]))

def train1_test2(trainCorpus, trainLabels, testCorpus, testLabels, vectorizer):
    #choose classifiers to evaluate
    classifiers = [LinearSVC(), MultinomialNB(), BernoulliNB(),LogisticRegression()]
    names = ['LinearSVC', 'MultinomialNB', 'BernoulliNB','LogisticRegression']

    #performance metrics initialization
    crossValidationAccuracy = dict()
    confusionMetrices = dict()
    for name in names:
        crossValidationAccuracy[name] = []
        confusionMetrices[name] = np.zeros((2, 2));  #confusion matrix

    print "Vectorizing data corpuses"

    train_corpus_tf_idf = vectorizer.fit_transform(trainCorpus)
    test_corpus_tf_idf = vectorizer.transform(testCorpus)

    #fit(train) models and check performance on testing part of data
    for name,clf in zip(names, classifiers):
        print "Currently being trained:" + name
        clf.fit(train_corpus_tf_idf, trainLabels)
        print "Currently predicting on testing data:" + name
        result = clf.predict(test_corpus_tf_idf)
        crossValidationAccuracy[name].append(accuracy_score(testLabels,result))
        confusionMetrices[name] = confusionMetrices[name] + confusion_matrix(testLabels, result)

    print "Confusion matrices:"

    for name in names:
        print name
        print "Cross validation results: ",
        for item in crossValidationAccuracy[name]: print item,
        print "Cross validation average:" + str(sum(crossValidationAccuracy[name]) / len(crossValidationAccuracy[name]))

def create_Models(corpus, labels, vectorizer):
    print "Vectorizing training corpus"
    train_corpus_tf_idf = vectorizer.fit_transform(corpus)

    # define and fit(train) models
    model1_linearSVC = LinearSVC()
    model2_multinomNB = MultinomialNB()
    model3_logisticRegression = LogisticRegression()
    #model1_linearSVC.fit(train_corpus_tf_idf, labels)
    #model2_multinomNB.fit(train_corpus_tf_idf, labels)
    model3_logisticRegression.fit(train_corpus_tf_idf, labels)
    print "SciKit models trained and being returned"

    return model3_logisticRegression

def PosNeg_thresholds_on_test_data(model,vectorizer):
    testCorpus, testLabels = make_Corpus_From_Test_Tweets(root_dir='datasets/Sentiment140_testData')

    vectorizedTestCorpus = vectorizer.transform(testCorpus)
    scores = model.predict_proba(vectorizedTestCorpus)
    #scores = model.predict(vectorizedTestCorpus)

    # initialization of numpy array needed (1,600,000 is size of my sentiment140 training dataset)
    labels = np.zeros(len(scores));
    for idx, score in enumerate(scores):
        if score[1]>0.6:
            labels[idx] = 4
        elif score[0]<0.4:
            labels[idx] = 0
        else:
            labels[idx] = 2

        '''if score==1:
           labels[idx] = 4
        else:
           labels[idx] = 0
        '''

    print accuracy_score(testLabels[:len(scores)],labels)


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

def plotPolynomials(minDate,passedDays,scores,projectName,mypath):
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
    ax.set_ylim([0, 1.2])

    # plot original and regression data
    plt.plot(original_dates, y, 'o')
    plt.plot(regression_dates, y_new2, '.', label='quadratic polynomial fit')
    plt.plot(regression_dates, y_new3, '-',label='cubic polynomial fit')
    plt.plot(regression_dates,y_new4, '--',label='quartic polynomial fit')

    # if it is cryptocurrency, get history prices
    cryptoPricesPath = os.path.join(mypath, 'cryptoPrices')
    priceFiles = [f for f in os.listdir(cryptoPricesPath) if os.path.isfile(os.path.join(cryptoPricesPath, f))]
    if projectName in priceFiles:
        #get prices and dates
        priceDates,prices = getCryptoPrices(projectName=projectName, cryptoPricesPath=cryptoPricesPath)
        #insert first price 0 to make the graph nicer
        priceDates.insert(len(priceDates), min(original_dates))
        prices.insert(len(prices),0)

        #add secondary y-axis
        ax2 = ax.twinx()
        ax2.plot(priceDates, prices,'grey',label='Price')

    legend = ax.legend(loc='lower left', shadow=True)
    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')
    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width
    plt.title(projectName)

    plt.show()


def getCryptoPrices(projectName,cryptoPricesPath):
    with open(os.path.join(cryptoPricesPath, projectName)) as priceFile:
        reader = csv.reader(priceFile, delimiter=',')
        priceDates = []
        prices = []
        for row in reader:
            # skip first row
            if (row[0] == 'Date'):
                continue;
            # create arrays
            toAppend = dt.datetime.strptime(row[0],'%b %d, %Y')
            priceDates.append(toAppend)
            prices.append(float(row[1]))

    return priceDates, prices

def analyzeIsoSentiment(mainn,use,secur,scores):
    s = 0
    for i in mainn:
        s = s + scores[i][1]

    print "Average maintainability score: " + str(s / len(mainn))
    print "Number of tweets: " + str(len(mainn))
    print "Percentage: " + str(float(len(mainn) / len(scores)))

    s = 0
    for i in use:
        s = s + scores[i][1]

    print "Average usability score: " + str(s / len(use))
    print "Number of tweets: " + str(len(use))
    print "Percentage: " + str(float(len(use) / len(scores)))

    s = 0
    for i in secur:
        s = s + scores[i][1]

    print "Average security score: " + str(s / len(secur))
    print "Number of tweets: " + str(len(secur))
    print "Percentage: " + str(float(len(secur) / len(scores)))


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

def tuneModelParameters(corpus,labels,vectorizer):
    kf = StratifiedKFold(n_splits=2)

    for train_index, test_index in kf.split(corpus, labels):
        #create arrays and corpuses according to current fold
        X_train = [corpus[i] for i in train_index]
        X_test = [corpus[i] for i in test_index]
        y_train, y_test = labels[train_index], labels[test_index]
        train_corpus_tf_idf = vectorizer.fit_transform(X_train)
        test_corpus_tf_idf = vectorizer.transform(X_test)

        scores = ['accuracy']
        # Set the parameters by to combine
        SVC_parameters = [{'C': [1,10,100,1000],
                             #'loss': ['hinge','squared_hinge'],
                             #'multi_class': ['ovr','crammer_singer'],
                             'fit_intercept': [True,False]
                             }]
        MultiNB_parameters = [{'alpha': [1.0, 2.0, 5.0, 10.0],
                             'fit_prior': [True, False]
                             }]
        BernoulliNB_parameters = [{'alpha': [1.0, 2.0, 5.0, 10.0],
                                   'binarize': [0.0, 2.0, 5.0, 10.0],
                                 'fit_prior': [True, False]
                                 }]

        for score in scores:
            print("Tuning hyper-parameters for %s" % score)

            clf = GridSearchCV(LinearSVC(), SVC_parameters, cv=5,scoring='%s' % score)
            clf.fit(train_corpus_tf_idf, y_train)

            print("Best parameters set found:")
            print(clf.best_params_)
            print("Performance for all combinations:")
            means = clf.cv_results_['mean_test_score']
            stds = clf.cv_results_['std_test_score']
            for mean, std, params in zip(means, stds, clf.cv_results_['params']):
                print("%0.3f (+/-%0.03f) for %r"
                      % (mean, std * 2, params))

            print("Detailed classification report of model trained and evaluated on full dev/eval sets:")
            y_true, y_pred = y_test, clf.predict(test_corpus_tf_idf)
            print(classification_report(y_true, y_pred))

def tuneVectorizerParameters(corpus,labels):
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LinearSVC()),
    ])
    parameters = {
        'tfidf__max_df': (0.75, 0.9),
        'tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)],
        'tfidf__sublinear_tf': (True, False),
        'tfidf__stop_words':['english']
    }

    grid_search_tune = GridSearchCV(pipeline, parameters, cv=2, n_jobs=2, verbose=3)
    print("Searching best parameters combination:")
    grid_search_tune.fit(corpus, labels)

    print("Best parameters set:")
    print grid_search_tune.best_estimator_.steps


def preprocess(raw_text):
    #remove hashtags, @references,
    letters_only_text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(#[A-Za-z0-9]+)|(\w+:\/\/\S+)"," ",raw_text).split())
    return letters_only_text

if __name__ == "__main__":
    main(sys.argv)

reload(sys)
sys.setdefaultencoding('utf8')


