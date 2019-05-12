# SentiSteem
Twitter sentiment analyzer developed as a part of my Master Thesis in 2017/2018. 

Main functionality is:

<ol>
<li>Download specified number of tweets in a specified time window. Language can be specified. Geodata are not implemented (yet).</li>
<li>Execute sentiment analysis on downloaded tweets. Classifier was pre-trained on <a href="http://help.sentiment140.com/for-students">Sentiment140</a> dataset</li>
<li>Create linegraph, heatmap and various wordclouds(common words, unique words, shaped wordcloud)</li>
<li>Generate Steemit blog post using template defined in reports folder.</li>
</ol>

<center><img src="https://i.imgur.com/PXykeZN.png"></center>

### Requirements
Following modules need to be installed:
<code>
* apt-get install python-tk
* pip install XlsxWriter
* apt install python-numpy
* apt-get install python-matplotlib
* pip install tweepy
* pip install -U scikit-learn scipy matplotlib
* pip install wordcloud
* pip install pandas
* pip install geoplotlib
* apt-get install libxml2-dev libxslt1-dev python-dev
* pip install pyquery
* pip install xlrd
</code>

### Run it
Simply run Sentiment_Analyzer_Gui.py in python2.7. Python3 is not supported

<code>python2.7 Sentiment_Analyzer_Gui.py</code>

UI shows up where tweet parameters can be defined. Parameters are:
<ul>
<li>Keyword</li>
<li>Number of tweets</li>
<li>Language of tweets</li>
<li>Tweets from</li>
<li>Tweets to</li>
<li>Geolocation - not implemented yet</li>
</ul>

You can run all 4 steps of SentiSteem pipeline with one button but every step can also be executed separately with it's own button.

Adjust app.config to fit your preferred folder structure, GUI size and also words skipped in wordclouds. 