# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 2014

Dieses Programm zeigt in einem Tkinter Fenster ein 10x10 Kästchen an, in dem nacheinander Punkte zufällig in den Kästchen erscheinen. Nach 2 bis 5 Punkten verschwinden die Punkte und es erscheint der Befehl die verherige Positionen der Punkte anzuklicken.
In der unteren linken Ecke ist ein Kästchen gezeichnet, dessen Farbe
von schwarz nach weiß beim Anzeigen des 10x10 Kästchens.

@author: Alexander Friedrich
"""

import tkinter as tk
import random
import logging
import time
from pylsl import StreamInfo, StreamOutlet

# App, die den Experiment durchführt
class App():
    # Constructor
    def __init__(self, dot_time = 0.9, post_dot_time = 0.1, result_time = 1, alter_time = 1, postTrial_time = 0, post_alert_time = 0.5, practice_trials = 2, difficulty_level = 6, trials_per_difficulty = 15):

        # Loggingattribute initialisieren
        #logging.basicConfig(format='%(asctime)s;%(message)s', filename= 'SSTM' + str(time.time()) + '.log', level=logging.INFO)
        
        #Initialize LSL
        info = StreamInfo('SSTMMarkerStream', 'Markers', 1, 0, 'string', 'sstmuidw43536')

        # next make an outlet
        self.outlet = StreamOutlet(info)


        # Zeitattribute initialisieren
        self.dot_time = dot_time				# Dots displayed length
        self.post_dot_time = post_dot_time		# Interval between dots
        self.result_time = result_time			# Length for "Draw the Dots"
        self.alter_time = alter_time			# Length for "Alert!!"
        self.postTrial_time = postTrial_time	# Interval from the last dot disapear to "Draw the dots" shows
        self.post_alert_time = post_alert_time	# Interval from "Alert!!" disapear to first dot displayed

        # Stimluluskontrollattribute initialisieren
        self.practice_trials = practice_trials	# Number of practice trial (Must be 2)
        self.difficulty_level = difficulty_level
        self.trials_per_difficulty = trials_per_difficulty
        self.test_trials = (self.difficulty_level - 1) * self.trials_per_difficulty		# Number of test trial (Must bigger than 1)
        self.visited_tuples = []
        self.difficulty_level_liste = []
        difficulties = self.difficulty_level - 1
        while difficulties > 0:
            difficulties -= 1
            self.difficulty_level_liste.append(self.trials_per_difficulty)
        dot_coords = []
        
        print(self.difficulty_level_liste)

        # Tkinter Fenster zeichnen
        self.root = tk.Tk()
        self.segment_color = 'white'
        
        # Tkinter Fenster initialisieren
        self.root.configure(background='gray')
        self.root.bind('<space>', self.start)
        self.root.bind('<Configure>', self.on_resize)

        # Fenster soll 2/3 der Breite/Höhe des Bildschirms besetzen
        self.width = self.root.winfo_screenwidth() * 2 / 3
        self.height =self.root.winfo_screenheight() * 2 / 3
        self.root.geometry('%dx%d+0+0' % (self.width, self.height))
        self.root.title("SSTM")
        self.corners = [(0,9),(9,0),(0,0),(9,9)]
		
        # Label initialisieren
        self.label = tk.Label(font=('Helvetica bold', 22), background='gray')
        if practice_trials != 0:
            self.label.configure(text="U begint met " + str(practice_trials) + " oefen rondes.\n  Druk <spatiebalk> om te starten")
        else:
            self.label.configure(text="Druk <spatiebalk> om te starten")
        self.label.pack(expand=1)
		
        # Button initialisieren
        self.button = tk.Button(text="Doorgaan", font=('Helvetica bold', 22), state='disabled', command = self.next)
        
        # Kästchen zeichnen
        self.segment_frame = tk.Frame(background=self.segment_color, height=80, width=80)
        self.segment_frame.pack(side='left',fill='none',anchor='sw')
        
        # Fixation Cross
        self.cross = tk.Canvas(width=150, height=300, borderwidth=0, highlightthickness=0, background = "gray")
        self.cross.create_line(75,0,75,150,fill="black")
        self.cross.create_line(0,75,150,75,fill="black")

        # Tkinter loop ausführen
        self.root.mainloop()
    
    def start(self, event):
        # Nicht mehr auf Leerzeichen reagieren
        self.root.unbind('<space>')
        self.label.configure(text="Voorbereiden!")
        self.root.after(alter_time * 1000, self.draw_grid)
    
    def draw_grid(self):
        self.cross.pack_forget()
        self.segment_toggle()
        self.label.pack_forget()
        self.canvas = tk.Canvas(width=501, height=501, borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand="true")
        self.rows = 10
        self.columns = 10
        self.cellwidth = 50
        self.cellheight = 50

        self.rect = {}
        self.oval = {}
        for column in range(10):
            for row in range(10):
                x1 = column*self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.rect[row,column] = self.canvas.create_rectangle(x1,y1,x2,y2, fill="white")
                self.oval[row,column] = self.canvas.create_oval(x1+15,y1+15,x2-15,y2-15, fill="white",outline = "white", tags= (row, column))
        self.label.configure(text="Plaats de stippen.", fg = "gray")
        self.label.pack(fill="both", expand="true")
        self.button.pack(side='right', anchor='sw')
        self.button.config(state='disabled')
        
        if self.practice_trials == 0:
            number_of_points = random.randint(2, self.difficulty_level)
            while self.difficulty_level_liste[number_of_points - 2] == 0:
                number_of_points = random.randint(2, self.difficulty_level)
            self.difficulty_level_liste[number_of_points - 2] -= 1
            print(self.difficulty_level_liste)
            self.outlet.push_sample(['trialDispStartDifficulty:' + str(number_of_points)])
            # Use if trials should always have the same length:
            #self.spawn_dots(number_of_points, self.difficulty_level - number_of_points)
            self.spawn_dots(number_of_points, 0)
        else:
            randomint = random.randint(2,self.difficulty_level)
            # Use if trials should always have the same length:
            #self.spawn_dots(randomint, self.difficulty_level - randomint)
            self.spawn_dots(randomint, 0)
    def spawn_dots(self, remaining_dots, diff):
        if remaining_dots > 0:
            row = random.randint(0,9)
            col = random.randint(0,9)
            while ((row,col) in self.corners or (row,col) in self.visited_tuples):
                row = random.randint(0,9)
                col = random.randint(0,9)
            self.visited_tuples.insert(0, (row,col))
            item_id = self.oval[row,col]
            self.canvas.itemconfig(item_id, fill="black", outline="black")
            if self.practice_trials == 0:
                self.outlet.push_sample(['dotAt:'+ str(row) + ',' + str(col)])
            self.root.after(int(dot_time * 1000), lambda: self.canvas.itemconfig(item_id, fill="white", outline="white"))
            self.root.after(int((dot_time + post_dot_time) * 1000), lambda: self.spawn_dots(remaining_dots - 1, diff))
        elif diff > 0:
            length = len(self.visited_tuples)
            randomint = random.randint(0,length - 1)
            row = self.visited_tuples[randomint][0]
            col = self.visited_tuples[randomint][1]
            item_id = self.oval[row,col]
            self.canvas.itemconfig(item_id, fill="black", outline="black")
            if self.practice_trials == 0:
                self.outlet.push_sample(['repeatDotAt:'+ str(row) + ',' + str(col)])
            self.root.after(int(dot_time * 1000), lambda: self.canvas.itemconfig(item_id, fill="white", outline="white"))
            self.root.after(int((dot_time + post_dot_time) * 1000), lambda: self.spawn_dots(remaining_dots, diff - 1))
        else:
            if self.practice_trials == 0: 
                selected_dots = ""
                for visited in self.visited_tuples:
                    selected_dots += str(visited[0])
                    selected_dots += str(visited[1])+";"
                self.outlet.push_sample(["trialDispStopVisited:" + selected_dots[:-1]])
            self.segment_toggle()
            self.button.config(state='active')
            self.draw_dots()
        
    def draw_dots(self):
        self.label.configure(fg = "black")
        if self.practice_trials == 0:
            self.outlet.push_sample(['trialClickStart'])
        self.canvas.bind("<Button-1>", self.dot)
    
    def dot(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked_items = self.canvas.find_enclosed(x-35, y-35, x+35, y+35)
        if clicked_items:
            for item in clicked_items:
                if self.canvas.type(item) == "oval":
                    if self.canvas.itemcget(item, "fill") == "white":
                        if len(self.canvas.find_withtag("selected")) < self.difficulty_level:
                            tags = self.canvas.itemcget(item, "tags") + " selected"
                            self.canvas.itemconfig(item, fill="blue", outline= "blue", tag=tags)
                            if self.practice_trials == 0:
                                row, col = self.canvas.gettags(item)[:2]
                                self.outlet.push_sample(['ChoseBox:' + str(row) + ',' + str(col) ])
                    else:
                        self.canvas.itemconfig(item, fill="white", outline= "white")
                        self.canvas.dtag(item, "selected")
                        if self.practice_trials == 0:
                            row, col = self.canvas.gettags(item)[:2]
                            self.outlet.push_sample(['UnchoseBox:' + str(row) + ',' + str(col)])
    
    def next(self):
        if self.practice_trials == 0:
            selected_dots = ""
            for selected in self.canvas.find_withtag("selected"):
                selected_dots += str(self.canvas.gettags(selected)[0])
                selected_dots += str(self.canvas.gettags(selected)[1])+";"
            self.outlet.push_sample(["trialClickStopChosen:" + selected_dots[:-1]])
        self.canvas.dtag("selected")
        self.visited_tuples = []
        self.button.pack_forget()
        self.canvas.pack_forget()
        self.label.pack_forget()
        randomint = random.randint(15,18)
        if self.practice_trials > 0:
            #logging.info("practice,"+str(
            self.practice_trials -= 1
            if self.practice_trials == 0:
                self.practice_end()
            else:
                self.cross.pack(expand=1)
                #Long duration only needed in fNIRS
                randomint=1
                self.root.after(randomint*1000, self.draw_grid)
        else:
            self.test_trials -= 1
            if self.test_trials > 0:
                self.cross.pack(expand=1)
                #Long duration only needed for fNIRS
                randomint=1
                self.root.after(randomint*1000, self.draw_grid)
            else:
                self.end()

    def practice_end(self):
        self.label.configure(text="Druk <spatiebalk> om te starten.")
        self.label.pack(expand=1)
        self.root.bind('<space>', self.start)
                
    def end(self):
        self.label.configure(text="Bedankt! Dit is het einde van het experiment.")
        self.label.pack(expand=1)
        
    # Kästchenfarbe wechseln
    def segment_toggle(self):
        if self.segment_color == 'white':
            self.segment_color = 'black'
        else:
            self.segment_color = 'white'
        # Kästchenfarbe im Fenster aktualisieren
        self.segment_frame.configure(background=self.segment_color)

    # Fenstergrößeveränderung verarbeiten
    def on_resize(self, event):
        self.width = self.root.winfo_width()
        self.wraplength = self.width
        self.label.configure(wraplength=self.wraplength)

# Konfigurierbare Parameter
dot_time = 1.4 #0.9
post_dot_time = 0.1
result_time = 1
alter_time = 1
postTrial_time = 0
post_alert_time = 0.5

practice_trials = 2
difficulty_level = 4
trials_per_difficulty = 10

# App ausführen
app=App(dot_time, post_dot_time, result_time, alter_time, postTrial_time, post_alert_time, practice_trials, difficulty_level, trials_per_difficulty)
