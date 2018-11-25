# -*- coding: utf-8 -*-
from pandas import Series
from pandas import DataFrame
from pandas import TimeGrouper
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot
import numpy as np

class Charts_Plotter:

	def __init__(self, chartsFolder):
		self.savePath = chartsFolder
		self.floored_data = Series.from_csv(chartsFolder + '/floored_scores.csv', header=0)
		self.data = Series.from_csv(chartsFolder + '/scores.csv', header=0)

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

	def Autocorrelation(self):
		autocorrelation_plot(self.floored_data)
		pyplot.savefig(self.savePath + "/autocorrelation.png")
		pyplot.close()