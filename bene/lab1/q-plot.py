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
        data = pd.read_csv("./output/3_out.csv")
        print data
        plt.figure()
        ax = data.plot(x='x',y='y')
        ax.set_xlabel("Utilization")
        ax.set_ylabel("Queueing Delay (ms)")
        fig = ax.get_figure()
        fig.savefig('line.png')

if __name__ == '__main__':
    p = Plotter()
    p.linePlot()
    #p.boxPlot()
    #p.histogramPlot()