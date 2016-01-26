import optparse
import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Class that parses a file and plots several graphs
class Plotter:
    def __init__(self):
        plt.style.use('ggplot')
        pd.set_option('display.width', 1000)
        pass

    def theory(self, p):
        mu = 1000000.0/8000.0
        const = 1.0/(2.0*mu)
        val = p/(1.0-p)
        toReturn = const * val
        for idx, val in enumerate(toReturn):
            if val > .3:
                toReturn[idx] = .3
        return toReturn

    def linePlot(self):
        """ Create a line graph. """
        data = pd.read_csv("./output/3_out.csv")
        print data.as_matrix(['x']).flatten()

        # print data
        plt.figure()
        ax = data.plot(x='x',y='Average')
        ax.set_xlabel("Utilization")
        ax.set_ylabel("Queueing Delay (ms)")

        x = np.linspace(.1, 1, 100)
        plt.plot(x,self.theory(x),label='Theory')

        plt.show()

        # print range(0,5,.1)
        # fig.savefig('line.png')

if __name__ == '__main__':
    p = Plotter()
    p.linePlot()
    #p.boxPlot()
    #p.histogramPlot()