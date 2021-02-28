#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import numpy as np
import math

#TODO add time measurement
#TODO save cluster affiliations

RGBA_VALS = [[0.000, 0.000, 1.000, 1], [1.000, 0.000, 0.000, 1], [0.000, 1.000, 0.000, 1], [1.000, 0.647, 0.000, 1],
             [0.118, 0.565, 1.000, 1], [1.000, 0.078, 0.576, 1], [1.000, 1.000, 0.000, 1], [1.000, 0.000, 1.000, 1],
             [0.502, 0.000, 0.502, 1], [0.647, 0.165, 0.165, 1], [0.251, 0.878, 0.816, 1], [0.804, 0.361, 0.361, 1],
             [0.741, 0.718, 0.420, 1], [0.000, 0.392, 0.000, 1], [0.690, 0.878, 0.902, 1], [0.502, 0.000, 0.000, 1]]

class MainApp(tk.Tk):
    """The controller of data and window contents."""
    def __init__(self, *args, **kwargs):
        """Create the main window and assign commands to buttons of the sidepane.
        """
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Isodata Fuzzy-C-Means playground")

        #self.xData = list(np.random.rand(50))
        #self.yData = list(np.random.rand(50))
        self.filePath = ""
        try:
            self.xData, self.yData = np.loadtxt("two_clusters.txt").tolist()
        except FileNotFoundError:
            print("Could not find '8clusters.txt', will start with empty field!")
            self.xData = []
            self.yData = []

        self.colors = [RGBA_VALS[0]]
        self.centerXCoords = []
        self.centerYCoords = []
        self.affiliations = np.array([])
        self.filePath = ""

        self.sidepane = Sidepane(self, padding="3 3 12 12")
        self.sidepane.grid(column=5, row=5, sticky="nsew")
        self.sidepane.loadButton.config(command=self.loadData)
        self.sidepane.saveButton.config(command=self.saveData)
        self.sidepane.saveAsButton.config(command=self.saveDataAs)
        self.sidepane.resetButton.config(command=self.resetData)
        self.sidepane.randDataButton.config(command=self.randomizeData)
        self.sidepane.numRandDataChooser.bind("<Return>", self.randomizeData)
        self.sidepane.numClusterChooser.bind("<Return>", self.runFCM)
        self.sidepane.startFCMButton.config(command=self.runFCM)

        self.plotArea = PlotArea(self, padding="3 3 12 12")
        self.plotArea.grid(column=10, row=5, sticky="nsew")
        self.plotArea.canvas.mpl_connect('button_press_event', self.onClick)
        self.plotArea.canvas.mpl_connect('pick_event', self.onPick)

        self.columnconfigure(10, weight=1)
        self.rowconfigure(5, weight=1)

    def saveData(self, *args):
        """Save data in xData and yData to the file in filePath. If filePath is
        empty, call saveDataAs()
        """
        if self.filePath:
            np.savetxt(self.filePath, (self.xData, self.yData))
        else:
            self.saveDataAs(self, *args)

    def saveDataAs(self, *args):
        """Open dialog to select location and filename to save the data from
        xData and yData. File path will be saved to filePath.
        """
        self.filePath = tk.filedialog.asksaveasfilename(initialdir=self.filePath, parent=self)
        if self.filePath:
            np.savetxt(self.filePath, (self.xData, self.yData))

    def loadData(self, *args):
        """Open dialog to select a file and load its content in to xData and
        yData when possible
        """
        self.filePath = tk.filedialog.askopenfilename(initialdir=self.filePath, parent=self)
        self.xData, self.yData = np.loadtxt(self.filePath).tolist()
        self.affiliations = np.array([])
        self.plotArea.redraw()
        self.sidepane.update()

    def onClick(self, event):
        """Handle clicks in the plot area. When left mouse button is clicked,
        the point is added to xData, yData and shown in the plot.
        """
        if (event.button == 1 and event.xdata is not None and
            event.ydata is not None):
            self.xData.append(event.xdata)
            self.yData.append(event.ydata)
            self.affiliations = np.array([])
            self.plotArea.redraw()
            self.sidepane.update()

    def onPick(self, event):
        """Handle pick events. If there is a mousebutton3-click on a data point
        it will be removed from the dataset
        """
        if event.mouseevent.button == 3:
            xMouse = event.mouseevent.xdata
            yMouse = event.mouseevent.ydata
            distances = [((xMouse-x)**2+(yMouse-y)**2)**0.5 for (x, y) in zip(self.xData, self.yData)]
            index = distances.index(min(distances))
            del self.xData[index]
            del self.yData[index]
            self.affiliations = np.array([])
            self.colors = [RGBA_VALS[0]]
            self.plotArea.redraw()
            self.sidepane.update()

    def resetData(self):
        """Initializes xData, yData with empty lists and redraws the plot."""
        self.xData = []
        self.yData = []
        self.filePath = ""
        self.affiliations = np.array([])
        self.colors = [RGBA_VALS[0]]
        self.plotArea.redraw()
        self.sidepane.update()

    def randomizeData(self, *args):
        """Fill the list of datapoints with random data. The number of points
        is determined by the spinbox from the sidepane. Even though there's a
        max limit to the box you can enter higher numbers than the limit. That's
        why there's another limit in this method (double as high).
        """
        self.xData = list(np.random.rand(min(self.sidepane.numRandData.get(), 10000)))
        self.yData = list(np.random.rand(min(self.sidepane.numRandData.get(), 10000)))
        self.filePath = ""
        self.affiliations = np.array([])
        self.colors = [RGBA_VALS[0]]
        self.plotArea.redraw()
        self.sidepane.update()

    def runFCM(self, *args):
        self.fcm = FCM(self.xData, self.yData, int(self.sidepane.numClusterChooser.get()), self.sidepane.contrast.get(), self.sidepane.truncErr.get())
        self.fcm.run()

        self.centerXCoords = self.fcm.centerXCoords
        self.centerYCoords = self.fcm.centerYCoords
        self.affiliations = self.fcm.affiliations

        '''For each data point will exist numCluster RGBA values, RGB belongs to a cluster,
        and the alpha value is the affiliation to this cluster.'''
        self.colors = np.empty((self.fcm.numCluster, len(self.xData), 4))
        for j in range(self.fcm.numCluster):
            self.colors[j] = np.array([RGBA_VALS[j]] * len(self.xData))
            for i in range(len(self.xData)):
                self.colors[j][i][3] = self.affiliations[i][j]
        self.plotArea.redraw()

class FCM():
    """Implements the Fuzzy-C-Means algorithm for 2D data. Uses no data
    encapsulation or anything fancy (like the very fancy act of checking
    parameters).

    Note: i denotes the index determining the data point, j the one determining
    the cluster.
    """
    def __init__(self, xData=[], yData=[], numCluster=2, contrast=1, truncErr=0.5):
        """Initialization."""
        self.xData = xData
        self.yData = yData
        self.numCluster = numCluster
        self.contrast = contrast
        self.truncErr = truncErr
        self.affiliations = np.random.rand(len(xData), numCluster)
        self.distances = np.empty((len(xData), numCluster))
        for i in range(self.affiliations.shape[0]):
            self.affiliations[i] = self.normalized(self.affiliations[i])

    def normalized(self, vec):
        """Normalizes values in a list/vector so that the sum of all values equals ~1"""
        s = vec.sum()
        return np.array([float(vec[j])/s for j in range(vec.shape[0])])
     
    def calcDistances(self):
        """Calcuates the distances from all data points to each cluster center"""
        for i in range(0, len(self.xData)):
            for j in range(0, self.numCluster):
                self.distances[i][j] = math.sqrt((self.xData[i] - self.centerXCoords[j])**2 + (self.yData[i] - self.centerYCoords[j])**2)
     
    def calcCenters(self):
        """Calculates the locations of the cluster centers"""
        self.centerXCoords = [0] * self.numCluster;
        self.centerYCoords = [0] * self.numCluster;
        
        for j in range(0, self.numCluster):
            denominator = 0.0
            for i in range(0, len(self.xData)):
                affiliationVal = self.affiliations[i][j]**self.contrast
                denominator += affiliationVal
                self.centerXCoords[j] += self.xData[i] * affiliationVal
                self.centerYCoords[j] += self.yData[i] * affiliationVal
            self.centerXCoords[j] /= denominator
            self.centerYCoords[j] /= denominator
     
    def calcAffiliation(self):
        """Recalculates the affiliation of each datapoint to each cluster by
        the distance to their centers. Returns the maximum distance between
        an old and the new value."""
        maxDist = 0.0
        exponent = 2 / (self.contrast - 1)
        for i in range(len(self.xData)):
            if min(self.distances[i]) == 0:
                clusters = []
                while min(self.distances[i]) == 0:
                    index = list(self.distances[i]).index(0)
                    clusters.append(index)
                    self.distances[i][index] = 1
                for j in range(0, len(self.affiliations[i])):
                    if j in clusters:
                        newVal = 1.0/len(clusters)
                    else:
                        newVal = 0
                    if abs(newVal - self.affiliations[i][j]) > maxDist:
                        maxDist = abs(newVal - self.affiliations[i][j])
                    self.affiliations[i][j] = newVal
            else:
                newVec = [1/sum([(distj/dist)**exponent for dist in self.distances[i]]) for distj in self.distances[i]]
                maxDistI = max(abs(newVec - self.affiliations[i]))
                if maxDistI > maxDist:
                    maxDist = maxDistI
                self.affiliations[i] = newVec
        return maxDist

    def run(self):
        while True:
            self.calcCenters()
            self.calcDistances()
            if self.calcAffiliation() < self.truncErr:
                break
        return self.centerXCoords, self.centerYCoords

class Sidepane(ttk.Frame):
    """Contains all the buttons without any functionality."""
    def __init__(self, master, *args, **kwargs):
        """Build the interface."""
        self.master = master
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.saveButton = ttk.Button(self, text="Save Data")
        self.saveButton.grid(column=5, row=5, sticky="nsew")
        self.saveAsButton = ttk.Button(self, text="Save as...")
        self.saveAsButton.grid(column=10, row=5, sticky="nsew")
        self.loadButton = ttk.Button(self, text="Load Data...")
        self.loadButton.grid(column=5, row=10, sticky="nsew")
        self.resetButton = ttk.Button(self, text="Reset Data")
        self.resetButton.grid(column=10, row=10, sticky="nsew")

        divider = ttk.Separator(self, orient=tk.HORIZONTAL)
        divider.grid(column=5, row=15, columnspan=10, sticky="nsew")

        randDataDesc = ttk.Label(self, text="Create x random Datapoints:")
        randDataDesc.grid(column=5, row=16, columnspan=10, sticky="nsew")
        self.numRandData = tk.IntVar()
        self.numRandData.set(500)
        self.numRandDataChooser = tk.Spinbox(self, from_=1, to=5000, textvariable=self.numRandData)
        self.numRandDataChooser.grid(column=5, row=17, sticky="nsew")
        self.randDataButton = ttk.Button(self, text="Randomize Data!")
        self.randDataButton.grid(column=10, row=17, sticky="nsew")

        divider = ttk.Separator(self, orient=tk.HORIZONTAL)
        divider.grid(column=5, row=18, columnspan=10, sticky="nsew")

        numClusterDesc = ttk.Label(self, text="Number of clusters:")
        numClusterDesc.grid(column=5, row=20, sticky="nsew")
        self.numClusterChooser = tk.Spinbox(self, from_=2, to=max(2, len(self.master.xData)))
        self.numClusterChooser.grid(column=5, row=21, sticky="nsw")

        contrastDesc = ttk.Label(self, text="Set cluster contrast variable:")
        contrastDesc.grid(column=5, row=24, sticky="nsew")
        self.contrast = tk.DoubleVar()
        contrastChooser = ttk.Scale(self, from_=1.01, to=15, variable=self.contrast)
        contrastChooser.grid(column=5, row=26, sticky="nsew")
        contrastChooser.set(2)
        contrastDisplay = ttk.Label(self, textvariable=self.contrast, width=5)
        contrastDisplay.grid(column=10, row = 26, sticky="w")

        truncErrDesc = ttk.Label(self, text="Set truncation error:")
        truncErrDesc.grid(column=5, row=30, sticky="nsew")
        self.truncErr = tk.DoubleVar()
        truncErrChooser = ttk.Scale(self, from_=0.0001, to=0.3, variable=self.truncErr)
        truncErrChooser.grid(column=5, row=31, sticky="nsew")
        truncErrChooser.set(0.01)
        truncErrDisplay = ttk.Label(self, textvariable=self.truncErr, width=5)
        truncErrDisplay.grid(column=10, row = 31, sticky="w")

        self.startFCMButton = ttk.Button(self, text="Calc Clusters")
        self.startFCMButton.grid(column=5, row=35, columnspan=10, sticky="nsew")

        for child in self.winfo_children(): child.grid_configure(padx=2, pady=5)

    def update(self):
        self.numClusterChooser.config(to=max(2, len(self.master.xData)))

class PlotArea(ttk.Frame):
    """Contains the area with the data visualization, provided by matplotlib."""
    def __init__(self, master, *args, **kwargs):
        """Initialize a scatter diagram using matplotlib."""
        self.master = master
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.figure = Figure(figsize=(6, 6))
        self.subplot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.redraw()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def redraw(self):
        """Update shown graph after master's xData, yData changed."""
        self.subplot.clear()
        if not self.master.affiliations.size:
            self.subplot.scatter(self.master.xData, self.master.yData, c='blue', cmap=None, lw=0.2, picker=3, s=75)
        else:
            for rgbMat in self.master.colors:
                self.subplot.scatter(self.master.xData, self.master.yData, c=rgbMat, lw=0.2, picker=3, s=75)
            self.subplot.scatter(self.master.centerXCoords, self.master.centerYCoords, edgecolor='black', color='white', marker='o', alpha = 1, s=150, lw=3)

        if (not self.master.xData or not self.master.yData or
            (max(self.master.xData) <= 1 and max(self.master.yData) <= 1 
                and min(self.master.xData) >= 0 and min(self.master.yData) >= 0)):
            self.subplot.axis([0, 1, 0, 1])
        self.canvas.draw()

def main():
    """Function to call when module runs as main application."""
    mainApp = MainApp()
    mainApp.mainloop()

def FCM_test():
	'''FCM test function to compare computed values to manually calculated ones
    No assertion stuff because of different truncation errors and laziness'''
	xData = [1, 2, 2]
	yData = [3, 1, 3]
	fcm = FCM(xData, yData, 2, 2, 0.1)
	fcm.affiliations = np.array([[0.75, 0.25], [0.25, 0.75], [0.4, 0.6]])
	fcm.calcCenters()
	print("Center xCoords:	")
	print(fcm.centerXCoords)
	print("Center yCoords:	")
	print(fcm.centerYCoords)
	fcm.calcDistances()
	print("Distances:")
	print(fcm.distances)
	print("Max dist to last affiliations: " + str(fcm.calcAffiliation()))
	print("Affiliations:")
	print(fcm.affiliations)

if __name__ == '__main__':
    main()
