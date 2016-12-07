import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.mlab as mlab
import sys, getopt 
import re
import itertools 
from filePlotting import *



'''
A thin wrapper around matplotlib to 
easily plot arrays of data,
the member 'markers' can be used to insert rulers at 
certain values on the x axis
'''
class Plotter:
        def __init__(self,fignum=1):
                self.markers = []
                self.fignum = fignum
                self.colors = iter(cmx.rainbow(np.linspace(0,1,100)))
        
                self.x=np.array([])
                self.y=np.array([])

                self.xs=[]
                self.ys=[]
                self.labels=[]
                self.colormap=cmx.rainbow
                self.numcolors = 100
                self.coloriter=iter(self.colormap(np.linspace(0,1,self.numcolors)))

        def setColormap(self,colormap,numcolor):
                self.numcolors=numcolor
                self.colormap=colormap
                self.coloriter=iter(self.colormap(np.linspace(0,1,self.numcolors)))
                
        def setX(self, xdata):
                self.x =np.array(xdata)

        def setY(self, ydata):
                self.y =np.array(ydata)

        def addX(self, xdata):
                self.xs.append(np.array(xdata))

        def addY(self, ydata):
                self.ys.append(np.array(ydata))

        def addLabel(self,label):
                self.labels.append(label)

        def addLabels(self,labels=[]):
                self.labels.extend(labels)


        def createAll(self):
                
                self.fig = plt.figure(self.fignum)
                self.mainaxis = self.fig.add_subplot(111)
                if self.x.size and self.y.size:
                        self.mainaxis.plot(self.x,self.y)
                        if self.ys and not self.xs:
                          for y in self.ys:
                            self.mainaxis.plot(self.x,y)
                if self.xs and self.ys and len(self.xs)<= len(self.ys):
                          for i in range(len(self.xs)):
                              label=str(i)
                              if i < len(self.labels):
                                label=str(self.labels[i])
                              color=next(self.coloriter)
                              self.mainaxis.plot(self.xs[i],self.ys[i],label=label,c=color)
                
                if self.markers:
                  for m in self.markers:
                    plt.axvline(x=m)


        def setAxesLabels(self,x="x",y="y"):
                axes = self.fig.get_axes()
                for a in axes:
                  a.set_xlabel(x)
                  a.set_ylabel(y)


        def plotCurrentState(self,xlim=[]):
                if xlim:
                        plt.xlim(xlim)
                plt.legend()
                plt.grid()
                plt.show()


