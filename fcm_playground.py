#!/usr/bin/python3
#TODO Clicks außerhalb des Wertebereichs behandeln!

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import numpy as np
import os

class MainApp(tk.Tk):
    """The controller of data and window contents."""
    def __init__(self, *args, **kwargs):
        """Create the main window and assign commands to buttons of the sidepane.
        """
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Isodata Fuzzy-C-Means playground")

        self.xData = []
        self.yData = []
        self.filePath = ""

        self.sidepane = Sidepane(self, padding="3 3 12 12")
        self.sidepane.grid(column=5, row=5, sticky="nsew")
        self.sidepane.loadButton.config(command=self.loadData)
        self.sidepane.saveButton.config(command=self.saveData)
        self.sidepane.saveAsButton.config(command=self.saveDataAs)
        self.sidepane.resetButton.config(command=self.resetData)

        self.plotArea = PlotArea(self, padding="3 3 12 12")
        self.plotArea.grid(column=10, row=5, sticky="nsew")
        self.plotArea.canvas.mpl_connect('button_press_event', self.addDataAtClick)

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
        """Open dialog to select a fila and load its content in to xData and
        yData when possible
        """
        self.filePath = tk.filedialog.askopenfilename(initialdir=self.filePath, parent=self)
        self.xData, self.yData = np.loadtxt(self.filePath).tolist()
        self.plotArea.redraw()

    def addDataAtClick(self, event):
        """Handle clicks into the plot area. When left mouse button is clicked,
        the point is added to xData, yData and shown in the plot.
        """
        if (event.button == 1 and event.xdata is not None and
            event.ydata is not None):
            self.xData.append(event.xdata)
            self.yData.append(event.ydata)
            self.plotArea.redraw()

    def resetData(self):
        """Initializes xData, yData with empty lists and redraws the plot."""
        self.xData = []
        self.yData = []
        self.plotArea.redraw()

class Sidepane(ttk.Frame):
    """Contains all the buttons to control the application but whithout any
    functions.
    """
    def __init__(self, master, *args, **kwargs):
        """Build the interface."""
        self.master = master
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.loadButton = ttk.Button(self, text="Load Data...")
        self.loadButton.grid(column=5, row=5, sticky="nsew")
        self.saveButton = ttk.Button(self, text="Save Data")
        self.saveButton.grid(column=10, row=5, sticky="nsew")
        self.saveAsButton = ttk.Button(self, text="Save as...")
        self.saveAsButton.grid(column=15, row=5, sticky="nsew")
        self.resetButton = ttk.Button(self, text="Reset Data")
        self.resetButton.grid(column=5, row=10, sticky="nsew")

        for child in self.winfo_children(): child.grid_configure(padx=2, pady=2)

class PlotArea(ttk.Frame):
    """Contains the area with the data visualization, provided by matplotlib."""
    def __init__(self, master, *args, **kwargs):
        """Initialize a scatter diagram using matplotlib."""
        self.master = master
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.figure = Figure(figsize=(6, 6))
        self.subplot = self.figure.add_subplot(111)
        self.plot = self.subplot.scatter(master.xData, master.yData, alpha=0.5)
        self.subplot.axis([0, 1, 0, 1])
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def redraw(self):
        """Update shown graph after master's xData, yData changed."""
        self.subplot.clear()
        self.plot = self.subplot.scatter(self.master.xData, self.master.yData, alpha=0.5)
        if (not self.master.xData or not self.master.yData or
            (max(self.master.xData) <= 1 and max(self.master.yData) <= 1)):
            self.subplot.axis([0, 1, 0, 1])
        self.canvas.show()

def main():
    """Function to call when module runs as own application."""
    mainApp = MainApp()
    mainApp.mainloop()

if __name__ == '__main__':
    main()
