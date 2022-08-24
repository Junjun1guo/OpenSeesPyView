#-*-coding: UTF-8-*-
import numpy as np
import matplotlib.pyplot as plt
import os
########################################################################
coreInfo= np.loadtxt("pylonUpper/coreDivide.txt")
coverInfo= np.loadtxt("pylonUpper/coverDivide.txt")
barInfo= np.loadtxt("pylonUpper/barDivide.txt")
print(sum(coreInfo[:,2]))
plt.subplot(111)
plt.grid("on")
plt.plot(coreInfo[:,0],coreInfo[:,1],".")
plt.plot(coverInfo[:,0],coverInfo[:,1],"r.")
plt.plot(barInfo[:,0],barInfo[:,1],"b.")
plt.show()

