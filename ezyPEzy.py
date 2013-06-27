from Tkinter import*
from tkFileDialog import*
import tkMessageBox
import os

#import matplotlib modules
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#import pySerial
import serial
import time

#import modules used for saving data
import datetime
import csv

#define variables
arduino = serial.Serial("COM4",9600)
print(arduino)
global timeX
global digitalOutY
global analogInY
global intArray
timeX=[]
digitalOutY=[]
analogInY=[]
intArray=[]

#menu functions
def quit():
    if tkMessageBox.askyesno("Exit","Are you sure you want to exit? All unsaved data will be lost!"):
        global root
        root.destroy()

def new():
    if tkMessageBox.askyesno("New","Create a new graph? All unsaved data will be lost!\n\nThe program may appear to be frozen while collecting data."):
        timeX=[]
        digitalOutY=[]
        analogInY=[]
        intArray=[]
        getData()
        
def about():
    tkMessageBox.showinfo("About","This is a highly experimental project, designed to test ferroelectrics and capacitors via an Arduino.")

def save():
    currentDate = datetime.datetime.now()
    dateString = currentDate.strftime("\%m%d%y")
    newDir = os.getcwd()+"\saved" + dateString
    counter = 0
    itDir = newDir + '1'
    while os.path.exists(itDir):
        counter+=1
        itDir = newDir + str(counter)
    if tkMessageBox.askyesno("Save?","Save all files into the directory\n\n"+itDir+"?"):
        os.makedirs(itDir)
        graph.dgPlot.fig.savefig(itDir+"\c1plot.svg",facecolor='black')
        graph.anPlot.fig.savefig(itDir+"\c2plot.svg",facecolor='black')
        graph.intPlot.fig.savefig(itDir+"\c3plot.svg",facecolor='black')
        dataArray = [timeX,digitalOutY,analogInY,intArray]
        dataToWrite = zip(*dataArray)
        writeCSV=csv.writer(file(itDir+"\data.csv","wb"))
        writeCSV.writerows(dataToWrite)
        tkMessageBox.showinfo("Saved!","All files have been saved into the directory:\n\n"+itDir)

#serial functions
def getData():
    graph.dgPlot.fig.clf()
    graph.dgPlot.setGraphSettings('C1 Output Voltage vs Time','time','voltage')
    graph.dgPlot.ax.set_ylim([-5,5])
    graph.dgPlot.ax.set_autoscaley_on(False)
    graph.anPlot.fig.clf()
    graph.anPlot.setGraphSettings('C2 Input Voltage vs Time','time','voltage')
    graph.intPlot.fig.clf()
    graph.intPlot.setGraphSettings('C3 Polarization vs Applied Voltage','applied voltage','polarization')

    timeTrack = 0
    intSum = float(0)
    for j in range (0,10):
        getTime = arduino.readline()
        getTime = float(getTime.rstrip('\r\n'))
        getTime = getTime/252
        for i in range (0,252):
            getLine = arduino.readline()
            getLine = float(getLine.rstrip('\r\n'))/256*10-5
            digitalOutY.append(getLine)
            getLine = arduino.readline()
            getLine = float(getLine.rstrip('\r\n'))
            aY = getLine/(-1000)+7.9578
            analogInY.append(aY)
            timeX.append(timeTrack)
            timeTrack += getTime
            pointer = j*252+i
            intSum += float((timeX[pointer]-timeX[pointer-1])*analogInY[pointer])
            intArray.append(intSum/68000/.0000531+30)
        graph.dgPlot.ax.set_xlim([0,timeTrack])
        graph.anPlot.ax.set_xlim([0,timeTrack])
        graph.updatePlot()
        

#GUI start
root = Tk();

root.title('ezyPEzy')
root.resizable(width=FALSE, height=FALSE)
root.wm_iconbitmap('icon.ico')

#add menubars
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=new)
filemenu.add_command(label="Save", command=save)
filemenu.add_command(label="Settings", command=quit)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=about)
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)

#update matplotlib settings
matplotlib.rcParams.update({'font.size':7})


class plotCanvas(FigureCanvasTkAgg):
    def __init__(self,title,xlabel,ylabel,master=None, width=6, height=3, dpi=100):
        self.fig = Figure(figsize=(width,height), dpi=dpi, facecolor='k', edgecolor = 'none')
        FigureCanvasTkAgg.__init__(self,figure = self.fig,master = master)
        self.fig.subplots_adjust(bottom=0.15,left=0.1, right=0.95)
        self.setGraphSettings(title,xlabel,ylabel)

    def setGraphSettings(self,title,xlabel,ylabel):
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.grid(color='gray',linestyle='dashed')
        self.ax.set_axis_bgcolor('k')
        self.ax.set_title(title,color='w')
        self.ax.set_xlabel(xlabel,color='w')
        self.ax.set_ylabel(ylabel,color='w')
        self.ax.spines['bottom'].set_color('w')
        self.ax.spines['left'].set_color('w')
        self.ax.tick_params(colors='w')

    def update(self,x,y):
        self.ax.plot(x,y,'c')
        self.draw()
        
class graphRegion(Toplevel):
    def __init__(self, master):
        self.master = master

        #initialize digitalOutput plot
        self.dgPlot = plotCanvas('C1 Voltage vs Time','time','voltage',master)
        self.dgPlot.ax.set_ylim([0,5])
        self.dgPlot.ax.set_autoscaley_on(False)
        self.dgPlot.get_tk_widget().grid(row=0,column=0)

        #initialize analogInput plot
        self.anPlot = plotCanvas('C2 Current vs Time','time','voltage',master)
        self.anPlot.get_tk_widget().grid(row=1,column=0)

        #intialize integrandArray plot
        self.intPlot = plotCanvas('C3 Polarization vs Applied Voltage','applied voltage','polarization',master)
        self.intPlot.get_tk_widget().grid(row=0,column=1)

    def updatePlot(self):
        self.dgPlot.update(timeX,digitalOutY)
        self.anPlot.update(timeX,analogInY)
        self.intPlot.update(digitalOutY,intArray)

graph = graphRegion(root)
root.mainloop()
