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
		self.data = Series.from_csv(chartsFolder + '/scores.csv', header=0)

	def LinePlot(self):
		self.data.plot()
		pyplot.xlabel("Date")
		pyplot.ylabel("Sentiment score")
		pyplot.savefig(self.savePath + "/linechart.png")
		pyplot.close()

	def YearlyLinePlot(self):
		self.data.plot()
		groups = self.data.groupby(TimeGrouper('A'))
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
		self.data.hist(bins = 2,range=[0,1])
		pyplot.xlabel("Date")
		pyplot.ylabel("Sentiment score")
		pyplot.savefig(self.savePath + "/histogram.png")
		pyplot.close()

	def HeatMap(self):
		self.data.plot()
		groups = self.data.groupby(TimeGrouper('A'))
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

	def HeatMapSquared(self):
		groups = self.data.groupby(TimeGrouper('A'))
		column_labels = ["Jan","Feb","Mar","Apr","Mai","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]

		finalData = []
		years=[]
		iter = 1
		for name, group in groups:
			extendedValues = group.values

			# fill zeros for the sentiment of months of the first analyzed year
			if iter == 1:
				extendedValues = np.append(np.zeros(12 - len(group.values)), group.values)
			# fill zeros for the sentiment of months of the last analyzed year
			if iter == len(groups):
				extendedValues = np.append(group.values, np.zeros(12 - len(group.values)))

			finalData.append(extendedValues)
			years.append(str(name.year))
			iter += 1

		data = np.array(finalData)
		fig, axis = pyplot.subplots()
		heatmap = axis.pcolor(data)  #,cmap=pyplot.cm.YlOrRd

		axis.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)
		axis.set_xticks(np.arange(data.shape[1]) + 0.5, minor=False)

		axis.invert_yaxis()

		axis.set_yticklabels(years, minor=False)
		axis.set_xticklabels(column_labels, minor=False)

		fig.set_size_inches(11.03, 3.5)
		pyplot.colorbar(heatmap)
		pyplot.savefig(self.savePath + "/heatMapSquared.png", dpi=100)

	def Autocorrelation(self):
		autocorrelation_plot(self.data)
		pyplot.savefig(self.savePath + "/autocorrelation.png")
		pyplot.close()