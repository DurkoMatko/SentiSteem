from os import listdir,system
from os.path import isfile, join
import os, sys
import datetime

def main(argv):
	KEYWORD = "altcoins"
	FROM = "2017-09-11"
	TILL = "2018-03-20"
	DAY_INTERVAL = 3

	#create date object
	requestDate = datetime.datetime.strptime(FROM, "%Y-%m-%d").date()
	tillDate 	= datetime.datetime.strptime(TILL, "%Y-%m-%d").date()

	while requestDate < tillDate:
		#create command command
		miningConsoleCommand = "python Exporter.py --querysearch '" + KEYWORD + "' --since " + str(requestDate - datetime.timedelta(days=1)) + " --until " + str(requestDate)   + " --lang " + "en" + " --maxtweets 100  --output='" + KEYWORD + ".csv" + "'"
		#execute the command
		system(miningConsoleCommand)
		#calculate next date
		requestDate = requestDate + datetime.timedelta(days=DAY_INTERVAL)

if __name__ == '__main__':
	main(sys.argv)
	print("done")

reload(sys)
sys.setdefaultencoding('utf8')