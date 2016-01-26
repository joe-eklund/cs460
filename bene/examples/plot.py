import optparse
import sys

import pandas as pd
import matplotlib.pyplot as plt

# Class that parses a file and plots several graphs
class Plotter:
    def __init__(self):
        plt.style.use('ggplot')
        pd.set_option('display.width', 1000)
        pass

    def linePlot(self):
        """ Create a line graph. """
        data = pd.read_csv("data1.csv")
        plt.figure()
        ax = data.plot(x='Time',y='Value of Company')
        ax.set_xlabel("Days")
        ax.set_ylabel("Dollars (millions)")
        fig = ax.get_figure()
        fig.savefig('line.png')


    def boxPlot(self):
        """ Create a box plot. """
        data = pd.read_csv("data2.csv")
        plt.figure()
        ax = data.boxplot(return_type='axes')
        ax.set_xlabel("Day")
        ax.set_ylabel("Level of Stress")
        fig = ax.get_figure()
        fig.savefig('boxplot.png')

    def histogramPlot(self):
        """ Create a histogram. """
        data = pd.read_csv("data3.csv")
        plt.figure()
        fig, ax = plt.subplots()
        data.hist(ax=ax)
        ax.set_xlabel("Pets")
        ax.set_ylabel("Number of People")
        fig = ax.get_figure()
        fig.savefig('histogram.png')

if __name__ == '__main__':
    p = Plotter()
    p.linePlot()
    p.boxPlot()
    p.histogramPlot()