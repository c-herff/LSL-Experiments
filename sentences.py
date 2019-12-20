import tkinter as  tk
from pylsl import StreamInfo, StreamOutlet
import csv, random


class sentenceGui:
    numTrials=100
    durationSentence=4
    durationCross=1

    def __init__(self, master, words):
        self.root = master
        self.sentences = sentences

        #Layout
        self.width = self.root.winfo_screenwidth() * 2 / 3
        self.height =self.root.winfo_screenheight() * 2 / 3
        self.root.geometry('%dx%d+0+0' % (self.width, self.height))
        self.root.title("Speech Task")
        #Initialize LSL
        info = StreamInfo('SentencesMarkerStream', 'Markers', 1, 0, 'string', 'emuidw22')
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
        self.root.after(0, self.trial)


    def trial(self):
        self.label.pack(expand=1)
        self.root.update_idletasks()
        if len(self.sentences)==0 or self.numTrials==0:
            self.root.after(0,self.end)
        else:
            self.numTrials= self.numTrials-1
            idx = random.randint(1,len(self.sentences))-1
            sen=self.sentences.pop(idx)
            self.outlet.push_sample(['start;' +  sen])
            self.lblVar.set(sen)
            self.root.update_idletasks()
            self.root.after(self.durationSentence*1000)
            self.outlet.push_sample(['end;' +  sen])
            self.lblVar.set('+')
            self.root.update_idletasks()
            #Long duration only needed in fNIRS
            self.root.after(self.durationCross*1000, self.trial)
        
    def end(self):
        self.outlet.push_sample(['experimentEnded'])
        self.lblVar.set("End of Experiment")
        self.root.update_idletasks()


def getSentences(filename):
    with open(filename, newline='',encoding="utf8") as file:
        sentences=[line.rstrip('\n') for line in file if len(line.split()) in range(5,11)]
    return sentences


if __name__=='__main__':
    sentences=getSentences('sentences.txt')
    root = tk.Tk()
    my_gui = sentenceGui(root,sentences)
    root.mainloop()