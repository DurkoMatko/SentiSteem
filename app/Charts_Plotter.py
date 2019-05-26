# -*- coding: utf-8 -*-
from pandas import Series, DataFrame, TimeGrouper, ExcelFile
import pandas as pd
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot
import numpy as np
import datetime as dt
import math

class Charts_Plotter:

	def __init__(self, chartsFolder, reportFileName):
		self.savePath = chartsFolder
		self.floored_data = Series.from_csv(chartsFolder + '/floored_scores.csv', header=0)
		self.data = Series.from_csv(chartsFolder + '/scores.csv', header=0)
		self.excelData = pd.read_excel(chartsFolder + '/scores.xlsx')
		self.reportFileName = reportFileName

	def LinePlot(self):
		self.floored_data.plot()
		pyplot.xlabel("Date")
		pyplot.ylabel("Sentiment score")
		pyplot.savefig(self.savePath + "/linechart.png")
		pyplot.close()

	def YearlyLinePlot(self):
		self.floored_data.plot()
		groups = self.floored_data.groupby(TimeGrouper('A'))
		years = DataFrame()
		iter = 1
		for name, group in groups:
			extendedValues = group.values

			#fill zeros for the sentiment of months of the first analyzed year
			if iter == 1:
				extendedValues = np.append(np.zeros(12-len(group.values)) ,group.values)
			# fill zeros for the sentiment of months of the last analyzed year
			if iter == len(groups):
				extendedValues = np.append(group.values, np.zeros(12 - len(group.values)))

			years[name.year] = extendedValues
			pyplot.ylabel(name.year)
			iter += 1

		years.plot(subplots=True, legend=False)
		pyplot.xlabel("Month")
		pyplot.ylabel("Year")
		pyplot.savefig(self.savePath + "/yearlyLinechart.png")
		pyplot.close()

	def Histogram(self):
		self.floored_data.hist(bins = 2,range=[0,1])
		pyplot.xlabel("Date")
		pyplot.ylabel("Sentiment score")
		pyplot.savefig(self.savePath + "/histogram.png")
		pyplot.close()

	def HeatMapBlurry(self):
		self.floored_data.plot()
		groups = self.floored_data.groupby(TimeGrouper('A'))
		yearLabels = []
		for key, value in groups.groups.iteritems():
			yearLabels.append(str(key.year))
		yearLabels.sort()

		years = DataFrame()
		iter = 1
		for name, group in groups:
			extendedValues = group.values

			# fill zeros for the sentiment of months of the first analyzed year
			if iter == 1:
				extendedValues = np.append(np.zeros(12 - len(group.values)), group.values)
			# fill zeros for the sentiment of months of the last analyzed year
			if iter == len(groups):
				extendedValues = np.append(group.values, np.zeros(12 - len(group.values)))

			years[name.year] = extendedValues
			pyplot.ylabel(name.year)
			iter += 1
		years = years.T
		pyplot.matshow(years, interpolation=None, aspect='auto')
		#pyplot.colorbar(heatmap)
		pyplot.savefig(self.savePath + "/heatMap.png")
		pyplot.close()

	def HeatMap(self):
		groups = self.floored_data.groupby(TimeGrouper('A'))

		finalData = []
		years=[]
		iter = 1
		hadToAddZeros = False
		for name, group in groups:
			extendedValues = group.values

			#if there are some months missing in a year
			if (12 - len(group.values) > 0):
				# fill zeros for the sentiment of months of the first analyzed year
				if iter == 1:
					extendedValues = np.append(np.zeros(12 - len(group.values)), group.values)
					hadToAddZeros = True
				# fill zeros for the sentiment of months of the last analyzed year
				if iter == len(groups):
					extendedValues = np.append(group.values, np.zeros(12 - len(group.values)))
					hadToAddZeros = True

			finalData.append(extendedValues)
			years.append(str(name.year))
			iter += 1

		data = np.array(finalData)
		fig, axis = pyplot.subplots()

		#if I added zeroes, color scheme needs to be adjusted
		if hadToAddZeros:
			heatmap = axis.pcolor(data)
		else:
			heatmap = axis.pcolor(data, cmap=pyplot.cm.Reds)

		axis.set_yticks(np.arange(data.shape[0]) + 0.6, minor=False)
		axis.set_xticks(np.arange(data.shape[1]) + 0.6, minor=False)
		axis.invert_yaxis()
		column_labels = ["Jan","Feb","Mar","Apr","Mai","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]
		axis.set_yticklabels(years, minor=False)
		axis.set_xticklabels(column_labels, minor=False)

		figureHeight = len(years)*0.5
		fig.set_size_inches(11, figureHeight)
		pyplot.colorbar(heatmap)
		pyplot.savefig(self.savePath + "/heatMap.png", dpi=100)

		#once plotted, replace placeholders in the post
		with open(self.reportFileName) as f:
			newText = f.read().replace('<HEATMAP_MONTHLY_HIGHEST>', "{0:.2f}".format(round(np.max(data),2)))
			newText = newText.replace('<HEATMAP_MONTHLY_LOWEST>', "{0:.2f}".format(round(np.min(data),2)))
		with open(self.reportFileName, "w") as f:
			f.write(newText)

	def HeatMapWeekly(self):
		groups = self.data.groupby(TimeGrouper('A'))
		finalData = []
		years=[]
		iter = 1
		hadToAddZeros = False

		for name, group in groups:
			extendedValues = group.values

			# if there are some weeks missing in a year
			if (52 - len(group.values) > 0):
				# fill zeros for the sentiment of months of the first analyzed year
				if iter == 1:
					extendedValues = np.append(np.zeros(52 - len(group.values)), group.values)
					hadToAddZeros = True
				# fill zeros for the sentiment of months of the last analyzed year
				if iter == len(groups):
					extendedValues = np.append(group.values, np.zeros(52 - len(group.values)))
					hadToAddZeros = True

			#remove extra weeks if one week somehow jumps from year to year in December/January
			if len(extendedValues) > 52:
				extendedValues = extendedValues[:52]

			finalData.append(extendedValues)
			years.append(str(name.year))
			iter += 1

		data = np.array(finalData)
		fig, axis = pyplot.subplots()

		# if I added zeroes, color scheme needs to be adjusted
		if hadToAddZeros:
			heatmap = axis.pcolor(data)
		else:
			heatmap = axis.pcolor(data, cmap=pyplot.cm.Reds)

		axis.set_yticks(np.arange(data.shape[0]) + 0.6, minor=False)
		axis.set_xticks(np.arange(data.shape[1]) + 0.6, minor=False)
		axis.invert_yaxis()
		column_labels = ["{:02d}".format(x) for x in range(1, 53)]
		axis.set_yticklabels(years, minor=False)
		axis.set_xticklabels(column_labels, minor=False)
		axis.set_xlim(0, len(column_labels))
		figureHeight = len(years) * 0.5
		fig.set_size_inches(11, figureHeight)

		pyplot.colorbar(heatmap)
		pyplot.xticks(fontsize=7)
		pyplot.savefig(self.savePath + "/heatMapWeekly.png", dpi=100)

		# once plotted, replace placeholders in the post
		with open(self.reportFileName) as f:
			newText = f.read().replace('<HEATMAP_WEEKLY_HIGHEST>', "{0:.2f}".format(round(np.max(data),2)))
			newText = newText.replace('<HEATMAP_WEEKLY_LOWEST>', "{0:.2f}".format(round(np.min(data),2)))
		with open(self.reportFileName, "w") as f:
			f.write(newText)

	def Autocorrelation(self):
		autocorrelation_plot(self.floored_data)
		pyplot.savefig(self.savePath + "/autocorrelation.png")
		pyplot.close()

	def convertDatesToPassedDays(self, dates):
		minDate = min(dates)
		passedDays = []

		for date in dates:
			passedDays.append(abs((date - minDate).days))
		return passedDays

	def convertPassedDaysToDates(self, minDate, days):
		dates = []

		for passed in days:
			dates.append((minDate + dt.timedelta(days=passed)).date())

		return dates

	def sentimentLinechart(self):
		#getting data from excel columns
		dateColumn = self.excelData['Date']
		dates = [dateColumn[i] for i in dateColumn.index]
		minDate = min(dates)

		flooredDateColumn = self.excelData['Floored date']
		flooredDates = []
		for i in flooredDateColumn.index:
			if not pd.isnull(flooredDateColumn[i]):
				flooredDates.append(flooredDateColumn[i])
		passedDays = self.convertDatesToPassedDays(dates=flooredDates)

		scoresColumn = self.excelData['Floored score']
		scores = []
		for i in scoresColumn.index:
			if not math.isnan(scoresColumn[i]):
				scores.append(scoresColumn[i])

		#plotting
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

		flooredPassedDays = self.convertDatesToPassedDays(dates=flooredDates)
		#revert original x-axis passed days to date format
		original_dates = self.convertPassedDaysToDates(minDate=minDate,days=flooredPassedDays)

		#revert regression x-axis values to datetime format
		regression_dates = self.convertPassedDaysToDates(minDate=minDate, days=x_new)

		# set x-axis labels to datetime format
		fig, ax = pyplot.subplots()
		fig.autofmt_xdate()

		# plot original and regression data
		pyplot.plot(original_dates, y, 'o')
		d = dt.timedelta(days=14)
		pyplot.xlim(xmax=max(original_dates)+d, xmin=min(original_dates)-d)
		pyplot.ylim(ymax=max(y)+0.025, ymin=min(y)-0.025)
		pyplot.grid()

		pyplot.plot(regression_dates, y_new2, '.', label='quadratic polynomial fit')
		pyplot.plot(regression_dates, y_new3, '-',label='cubic polynomial fit')
		pyplot.plot(regression_dates,y_new4, '--',label='quartic polynomial fit')


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
		pyplot.title("")
		#plt.show()
		pyplot.savefig(self.savePath+"/sentiment.png")
		pyplot.close()