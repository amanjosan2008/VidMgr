#!/usr/bin/env python3

import vlc
import os,sys
import time
from tkinter import Label, Tk, Frame, Button, messagebox, StringVar, Radiobutton, filedialog, Entry
from tkinter import *
import tkinter
import subprocess
import shutil
from send2trash import send2trash

root = Tk()

# Variables
array,playlist,MODES = [],[],[]
#global song
m,d = 0,0

# Populate Directory List
array = [line.rstrip('\n') for line in open('dirlist.ini')]

for i in range(len(array)):
    MODES.append(array[i].split('\t'))

# Various Functions
def browse():
    try:
        global playlist, current, d, m
        playlist = []
        current,d,m = 0,0,0
        try:
            dir = filedialog.askdirectory(parent=root, initialdir='/data/.folder/', title='Please select a directory')
        except:
            dir = filedialog.askdirectory(parent=root, initialdir=os.getcwd(), title='Please select a directory')
        en.delete(0,END)
        en.insert(0,dir)
        for filename in os.listdir(en.get()):
                if os.path.isfile(os.path.join(en.get(), filename)):
                    playlist.append(os.path.join(en.get(), filename))
        listbox.insert(END, "Total no of Files: "+str(len(playlist)))
    except FileNotFoundError:
        listbox.insert(END, "Error: Directory not selected")

def plist():
    count = [name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))]
    if (len(count)==0):
        listbox.insert(END, "Error: No Files in Directory")
    else:
        for i in range(len(count)):
            listbox.insert(END, count[i])

def stats():
    listbox.insert(END, "Initial Count: "+str(len(playlist)))
    listbox.insert(END, "Current Count: "+str(len([name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))])))
    listbox.insert(END, "Deleted: "+str(d))
    listbox.insert(END, "Moved: "+str(m))

def play(delta):
    global current
    if not (0 <= current + delta < len(playlist)):
        listbox.insert(END, "End of List")
        return
    current += delta
    song = 'vlc "%s"' %playlist[current]
    if os.path.isfile(playlist[current]):
        listbox.insert(END, str(current+1)+": "+song)
        subprocess.Popen(song, shell=True)
    else:
        listbox.insert(END, "Error: File not found: "+(playlist[current]).split('/')[-1])

def move():
    if os.path.isdir(v.get()):
        try:
            if os.path.isfile(playlist[current]):
                shutil.move(playlist[current], v.get())
                listbox.insert(END, "Moved: "+playlist[current]+" => "+v.get())
                global m
                m += 1
                play(+1)
            else:
                listbox.insert(END, "Error: Source file does not exist: "+(playlist[current]).split('/')[-1])
        except shutil.Error:
            listbox.insert(END, "Error: "+(playlist[current]).split('/')[-1]+": already exists at destination: "+v.get())
        except FileNotFoundError:
            listbox.insert(END, "Error: File not found: "+(playlist[current]).split('/')[-1])
    else:
        listbox.insert(END, "Error: Directory does not exist: "+v.get())

def delete():
    send2trash(playlist[current])
    listbox.insert(END, "Deleted: "+playlist[current])
    global d
    d += 1
    play(+1)

def deleteall():
    listbox.insert(END, "Deleted All files: ")
    for i in range(len(playlist)):
         try:
             send2trash(playlist[i])
             listbox.insert(END, " -  "+playlist[i])
             global d
             d += 1
         except:
             listbox.insert(END, " -  "+"Already Deleted: "+playlist[i])

def clear():
    listbox.delete(0, END)

def exit():
    p = subprocess.Popen("killall vlc", shell=True, stdout=subprocess.PIPE)
    sys.exit()

def browse2():
    try:
        dir = filedialog.askdirectory(parent=root, initialdir='/media/system/Data/Vids/', title='Please select a directory')
    except:
        dir = filedialog.askdirectory(parent=root, initialdir=os.getcwd(), title='Please select a directory')    
    en3.delete(0,END)
    en3.insert(0,dir)

def save():
    if en2.get() and en3.get():
        f = open('dirlist.ini','a')
        f.write(en2.get()+"\t"+en3.get()+"\r")
        f.close()
        listbox.insert(END, "Saved Directory: "+en2.get()+" "+en3.get())
    else:
        listbox.insert(END, "Error: Directory/Name not selected")

def delentry():
    f = open('dirlist.ini','r')
    l = f.readlines()
    if en4.get():
        n = int(en4.get())-1
    else:
        listbox.insert(END, "Error: Number not entered")
        return
    try:
        listbox.insert(END, "Removing Listed Directory: " + l[n])
        line = l[0:n] + l[n+1:]
        f.close()
        f2 = open('dirlist.ini','w')
        for i in line:
            f2.write(i)
        f2.close()
    except IndexError:
        listbox.insert(END, "Error: Invalid Number Entered")


# Buttons Config:
Button(root, text="Browse", command=browse).grid(row=0, column=0, rowspan=1, columnspan=1)
Button(root, text='Play', command=lambda: play(0)).grid(row=0, column=1, rowspan=1, columnspan=1)
Button(root, text='Previous', command=lambda: play(-1)).grid(row=0, column=2, rowspan=1, columnspan=1)
Button(root, text='Next', command=lambda: play(+1)).grid(row=0, column=3, rowspan=1, columnspan=1)
Button(root, text='Move', command=lambda: move()).grid(row=0, column=4, rowspan=1, columnspan=1)
Button(root, text='List', command=lambda: plist()).grid(row=0, column=5, rowspan=1, columnspan=1)
Button(root, text='Stats', command=lambda: stats()).grid(row=0, column=6, rowspan=1, columnspan=1)
Button(root, text='Delete', command=lambda: delete()).grid(row=0, column=7, rowspan=1, columnspan=1)
Button(root, text='Delete All', command=lambda: deleteall()).grid(row=0, column=8, rowspan=1, columnspan=1)
Button(root, text='Clear', command=lambda: clear()).grid(row=0, column=9, rowspan=1, columnspan=1)
Button(root, text='Quit', command=exit).grid(row=0, column=10, rowspan=1, columnspan=1)

# Browse Entry Box
en = Entry(root, width=60)
en.grid(row=2, column=1, rowspan=1, columnspan=8, sticky=W)
en.focus_set()

# Directory buttons
v = StringVar()
try:
    v.set(MODES[0][1]) # initialize
    i = 3
    for text, mode in MODES:
        b = Radiobutton(root, text=text, variable=v, value=mode)
        b.grid(row=i, column=0, rowspan=1, columnspan=1,sticky=W)
        i += 1
except:
    pass

# Output Logs Box
listbox = Listbox(root, height=20, width=70)
listbox.xview_scroll(3, "pages")
listbox.yview_scroll(3, "pages")
listbox.grid(row=3, column=1, rowspan=12, columnspan=9)

listbox.insert(END, "Ready, Log Output: ")

# Validate Directories
try: 
    for i in range(len(MODES)):
        if os.path.exists(MODES[i][1]):
            pass
        else:
            listbox.insert(END, "Error: Directory does not exist: "+MODES[i][0]+" - "+MODES[i][1])
except:
    pass

#Save Directory list Section
Label(root, text="Insert Directory to Side Panel:").grid(row=15, column=1,rowspan=1, columnspan=8)

en2 = Entry(root, width=20)
en2.grid(row=16, column=1, rowspan=1, columnspan=8, sticky=W)

en3 = Entry(root, width=40)
en3.grid(row=16, column=2, rowspan=1, columnspan=8, sticky=W)

Button(root, text="Browse", command=browse2).grid(row=16, column=7, rowspan=1, columnspan=1)
Button(root, text="Save", command=save).grid(row=16, column=8, rowspan=1, columnspan=1)

en4 = Entry(root, width=10)
en4.grid(row=18, column=1, rowspan=1, columnspan=1, sticky=W)

Button(root, text="Del Entry", command=lambda: delentry()).grid(row=18, column=2, rowspan=1, columnspan=1)

root.geometry('800x600')
root.mainloop()

