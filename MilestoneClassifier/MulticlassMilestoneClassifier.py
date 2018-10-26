import sys
import os
import numpy
import csv
import re
import pickle
import importlib
from operator import add
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import NearestCentroid,KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, Perceptron, PassiveAggressiveClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB,GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.linear_model import RidgeClassifier, RidgeClassifierCV
from enum import Enum,unique

# importlib.reload(sys)
# sys.setdefaultencoding('utf8')

@unique
class TrainingMode(Enum):
   BINARY = 1
   MULTI = 2

@unique
class PredictionMode(Enum):
   BINARY_LABELS = 1
   BINARY_CONFIDENCE = 2
   MULTI_LABELS = 3

class MulticlassMilestoneClassifier:

   def __init__(self):
      self.basicLearners = [LogisticRegression()]
      self.vectorizer = TfidfVectorizer()

   def train(self,corpus,labels,mode):
      self.labels = numpy.array(list(set(labels)))  # labels->unique labels->list->array of floats
      train_corpus_tf_idf = self.transformTrainingCorpus(corpus)

      for classifier in self.basicLearners:
         classifier.fit(train_corpus_tf_idf,labels)

   def predict(self,corpus,mode):
      if mode == PredictionMode.BINARY_LABELS:
         return self.predictBinaryLabels(corpus)
      elif mode == PredictionMode.BINARY_CONFIDENCE:
         return self.predictBinaryConfidence(corpus)
      elif mode == PredictionMode.MULTI_LABELS:
         return self.predictMultiLabels(corpus)


   ###*** each classifier does the 1/0 prediction, method returns percentual value of how many of used classifiers identified the post as positive ***###
   ###*** therefore min value 0.0 and max value 1.0 ***###
   def predictBinaryLabels(self,corpus):
      vectorizedCorpus = self.transformCorpusToAnalyze(corpus)
      results = [0.0] * vectorizedCorpus.shape[0]
      for classifier in self.basicLearners:
         results += classifier.predict(vectorizedCorpus)

      return [x / len(self.basicLearners) for x in results]


   ###*** returns averaged list of confidence values about being "positive" for each post in corpus ***###
   ###*** not every scikit classifier is able to output probablity(some do just 1/0), so not all used classifiers will do their prediction here***###
   def predictBinaryConfidence(self,corpus):
      countOfProbabilityClassifiers = 0
      vectorizedCorpus = self.transformCorpusToAnalyze(corpus)
      results = [0.0] * vectorizedCorpus.shape[0]

      for classifier in self.basicLearners:
         if hasattr(classifier, 'predict_proba'):
            res = classifier.predict_proba(vectorizedCorpus)
            # element-wise addition of positive confidence
            results = map(add, results, [score[1] for score in res] )
            countOfProbabilityClassifiers += 1

      return  [x / countOfProbabilityClassifiers for x in results]


   def predictMultiLabels(self,corpus):
      vectorizedCorpus = self.transformCorpusToAnalyze(corpus)
      #array of posts represented by dictionaries
      #each dictionary represents count of classifiers(value) which have chosen particular label(key)
      dictionaries = [dict((key, 0) for key in self.labels) for x in range(vectorizedCorpus.shape[0])]

      #predict labels with each classifier
      for classifier in self.basicLearners:
         res = classifier.predict(vectorizedCorpus)
         for idx,label in enumerate(res):
            #increase counter of label for post with id idx
            dictionaries[idx][label] += 1

      #construct results array of labels chosen the most for each post
      results = []
      for idx, post_dict in enumerate(dictionaries):
         mostly_chosen_label = max(post_dict, key=post_dict.get)
         results.append(mostly_chosen_label)

      return results


   def transformTrainingCorpus(self,corpus):
      return self.vectorizer.fit_transform(corpus)

   def transformCorpusToAnalyze(self,corpus):
      return self.vectorizer.transform(corpus)