import tkinter as  tk
import winsound
from pylsl import StreamInfo, StreamOutlet
import csv, random


class soundPerceptionGui:
    numTrials=0
    durationSounds=1
    durationCross=0.5
    durationPause=20

    def __init__(self, master, stims):
        self.root = master
        self.stims = stims

        #Layout
        self.width = self.root.winfo_screenwidth() * 2 / 3
        self.height =self.root.winfo_screenheight() * 2 / 3
        self.root.geometry('%dx%d+0+0' % (self.width, self.height))
        self.root.title("Sound Perception")
        #Initialize LSL
        info = StreamInfo('SoundPerceptionMarkerStream', 'Markers', 1, 0, 'string', 'emuidw22')
        # next make an outlet
        self.outlet = StreamOutlet(info)

        self.label = tk.Label(font=('Helvetica bold', 22)) #, background='gray'
        self.lblVar = tk.StringVar()
        self.label.configure(textvariable=self.lblVar)
        self.lblVar.set("Press <Space> to Start")
        self.label.pack(expand=1)
        
        self.root.bind('<space>', self.run)

    def run(self, event):
        self.root.unbind('<space>')
        self.outlet.push_sample(['experimentStarted'])
        self.root.bind('<space>', self.targetPress)
        self.root.after(0, self.trial)

    def targetPress(self, event):
        self.outlet.push_sample(['keyPress;space'])

    def trial(self):
        self.label.pack(expand=1)
        self.root.update_idletasks()
        if len(self.stims)==0:
            self.root.after(0,self.end)
        else:
            
            stim=self.stims.pop()
            self.outlet.push_sample(['start;' +  stim])
            self.lblVar.set('+')
            self.root.update_idletasks()
            
            winsound.PlaySound('./Experiment2_Sounds/' + stim ,winsound.SND_ASYNC) # winsound.SND_FILENAME 
            self.root.after(self.durationSounds*1000) # self.durationSounds*1000
            self.outlet.push_sample(['end;' +  stim])
            self.lblVar.set('+')
            self.root.update_idletasks()
            #Long duration only needed in fNIRS
            
            self.numTrials= self.numTrials+1
            if self.numTrials%81==0 and len(self.stims)!=0:
                #long pause
                self.lblVar.set('Pauze')
                self.root.update_idletasks()
                self.root.after(int(self.durationPause*1000), self.trial)
            else:
                self.root.after(int(self.durationCross*1000), self.trial)
        
    def end(self):
        self.outlet.push_sample(['experimentEnded'])
        self.lblVar.set("End of Experiment")
        self.root.update_idletasks()


def getWords(filename):
    with open(filename, newline='') as file:
        words = [line.rstrip('\r\n') for line in file]
    return words

if __name__=='__main__':
    stims=getWords('stimSequence1.txt')[::-1]
    root = tk.Tk()
    my_gui = soundPerceptionGui(root,stims)
    root.mainloop()