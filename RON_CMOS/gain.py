import matplotlib.pyplot as plt 
import numpy as np 
import os 
import math 

import sys
sys.path.append("..")
import loadImage

class GAIN: 

    def __init__(self, relativePathLight, relativePathDark):
        self.absPath = os.path.dirname(__file__)
        
        self.fullPathFlat = os.path.join(self.absPath, relativePathLight)
        self.fitsLoaderFlat = loadImage.fitsLoader(self.fullPathFlat) 
        self.fitsLoaderFlat.loadImages() 

        self.fullPathDark = os.path.join(self.absPath, relativePathDark)
        self.fitsLoaderDark = loadImage.fitsLoader(self.fullPathDark)
        self.fitsLoaderDark.loadImages() 


        self.varVals = []
        self.meanVals = [] 

        self.gainValues = [] 


    def midROI(self): 
        """
        Grabs the X and Y index for the centermost 300x300 region of a frame
        startX, startY
        endX, endY 
        """
        width = self.fitsLoaderDark.getHeaderInfo('WIDTH')
        height = self.fitsLoaderDark.getHeaderInfo('HEIGHT')
        self.startX = (width - 300) // 2
        self.startY = (height - 300) // 2
        self.endX = self.startX + 300 
        self.endY = self.startY + 300
#---------------------------TRY NUMBER 3----------------------------------------------------
#               Take flats - same exp time different levels
#               Take corresponding darks - same exposure time
#               Subtract darks from each flat and find variance and mean

    def calcPTC(self):
        #Calculate Midpoint 
        self.midROI()
        #Create Master Dark 
        masterDark = np.stack(self.fitsLoaderDark.images, axis=0)
        masterDark = np.mean(masterDark, axis=0)
       
        for frame in self.fitsLoaderFlat.images:
            subFrame = frame - masterDark     
            # get region of interest within frame
            ROI = subFrame[self.startX:self.endX, self.startY:self.endY]
            #ROI = subFrame[1204:1304, 1204:1304]

            mean = np.mean(ROI)
            variance = np.var(ROI)

            self.meanVals.append(mean) 
            self.varVals.append(variance) 

        self.plotPTC() 
    

    def plotPTC(self):
        """
        Plots the photon transfer curve 
        """
        slope, intercept = np.polyfit(self.meanVals, self.varVals, 1)
        # Super scuffed linear fit line (just a bunch of tightly grouped points)
        bestFit = np.poly1d([slope, intercept])
        x_line = np.linspace(min(self.meanVals), max(self.meanVals), 1000)
        y_line = bestFit(x_line)
        # Plot data points and line of best fit
        plt.scatter(self.meanVals, self.varVals, label='Data Points')
        plt.scatter(x_line, y_line, color='red', label=f'Fit: y = {slope:.2f}x + {intercept:.2f}', s=0.1)
        plt.xlabel("Mean")
        plt.ylabel("Variance")
        # Print gain which is the slope 
        print(f"gain: {slope}")
        # Show the plot
        plt.title("Photon Transfer Curve")
        plt.legend() 
        plt.show()


    def spacialVariation(self): 
        """
        AHHH WHAT DOES THIS DO ITS IN MY BRAIN
        """
        #Create Master Dark 
        masterDark = np.stack(self.fitsLoaderDark.images, axis=0)
        masterDark = np.mean(masterDark, axis=0)

        ### ADD THE LOOP HERE 48 box size

        for x in range(0, 3216, 48):
            for y in range(0, 2208, 48):
                
                meanNums = []
                varNums = [] 

                for frame in self.fitsLoaderFlat.images:
                    subFrame = frame - masterDark     
                    # get region of interest within frame
                    ROI = subFrame[x:x+48, y:y+48]
                    mean = np.mean(ROI)
                    variance = np.var(ROI)

                    meanNums.append(mean) 
                    varNums.append(variance)

                gain, intercept = np.polyfit(meanNums, varNums, 1)

                self.gainValues.append(gain) 


        original = np.zeros((3216, 2208))

        gainValues = np.array(self.gainValues).reshape(3216 // 48, 2208 // 48)

        for i in range(67):
            for j in range(46):
                original[i*48:(i+1)*48, j*48:(j+1)*48] = gainValues[i,j]
        
        plt.imshow(original, cmap='viridis', origin='lower', aspect='auto')
        plt.colorbar(label='Gain Value')
        plt.title("Gain Values Heatmap")
        plt.show() 

    def printKeyandVals(self, imageList):
        """
        Debugging function 
        Given a dictionary of images
        Print the key and number of values associated with that key
        """
        for key, value in imageList.items():
            print(f"Key: {key}, num of Values: {len(value)}")

    
    def gcd(self):
        """
        Helper function to find greatest common square size for a nxm image
        Throws exception if result is not an integer value
        """
        height, width = np.shape(self.fitsLoaderFlat.images[0])
        gcd = math.gcd(width, height)
        if not isinstance(gcd, int):
            raise ValueError("Square Size is not an Integer")
        print(gcd)
        return gcd
