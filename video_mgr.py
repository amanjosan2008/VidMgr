#!/usr/bin/env python3
# Keyboard Events Capture to play, next, delete
# Integrate VLC Window in main Window
# Add Icon to all Buttons
# Busy => Hourglass & in Ext Doctor also

import os,sys
import time
from tkinter import Label, Tk, Frame, Button, messagebox, StringVar, Radiobutton, filedialog, Entry, messagebox
from tkinter import *
import tkinter
import subprocess
import shutil
from send2trash import send2trash
import psutil

try:
    root = Tk()

    # Variables
    array,playlist,MODES = [],[],[]
    m,d = 0,0

    # Populate Directory List
    try:
        array = [line.rstrip('\n') for line in open('dirlist.ini')]
    except FileNotFoundError:
        print("Error: dirlist.ini not found. Please create the file.")
        root.quit()

    for i in range(len(array)):
        MODES.append(array[i].split('\t'))

    def filesize(file):
        size = os.path.getsize(file)
        sizeinmb = size/1000000
        sizeflt = "{:.2f}".format(sizeinmb)
        return sizeflt

    def lb(text):
        listbox.insert(END, text)
        listbox.yview(END)

    # Various Functions
    def browse():
        try:
            global playlist, current, d, m
            playlist = []
            current,d,m = 0,0,0
            try:
                dir = filedialog.askdirectory(parent=root, initialdir='/data/.folder/Short/Vids/', title='Please select a directory')
            except:
                dir = filedialog.askdirectory(parent=root, initialdir=os.getcwd(), title='Please select a directory')
            en.delete(0,END)
            en.insert(0,dir)
            for filename in os.listdir(en.get()):
                    if os.path.isfile(os.path.join(en.get(), filename)):
                        playlist.append(os.path.join(en.get(), filename))
            lb("Total no of Files: "+str(len(playlist)))
        except FileNotFoundError:
            lb("Error: Directory not selected")
        lb("")

    def openfolder():
        if en.get():
            path = 'nautilus "%s"' %en.get()
            subprocess.Popen(path, shell=True)
            lb("Directory opened: "+en.get())
        else:
            lb("Error: Directory not selected")
        lb("")

    def ls_dir():
        if en.get():
            count = [name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))]
            if (len(count)==0):
                lb("Error: No Files in Directory")
            else:
                lb("File List:")
                for i in range(len(count)):
                    lb(str(i+1)+ ". " + count[i] + " " + "["+ filesize(en.get()+"/"+count[i]) + "MB" + "]")
        else:
            lb("Error: Directory not selected")
        lb("")

    def stats():
        try:
            count = len([name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))])
        except:
            count = "No Files"
        lb("File Operation Stats:")
        lb("Initial Count: "+str(len(playlist)))
        lb("Current Count: "+str(count))
        lb("Deleted: "+str(d))
        lb("Moved: "+str(m))
        lb("")

    def play(delta):
        global current
        if en.get():
            if not (0 <= current + delta < len(playlist)):
                lb("End of List")
                lb("")
                return
            current += delta
            song = 'vlc -q "%s" 2> /dev/null' %playlist[current]
            if os.path.isfile(playlist[current]):
                lb(str(current+1)+": "+"VLC: "+playlist[current]+ " " + "["+ filesize(playlist[current]) + "MB" + "]")
                subprocess.Popen(song, shell=True)
            else:
                lb("Error: File not found: "+(playlist[current]).split('/')[-1])
                lb("")
        else:
            lb("Error: Directory not selected")
            lb("")

    def move():
        if en.get():
            if os.path.isdir(v.get()):
                try:
                    if os.path.isfile(playlist[current]):
                        shutil.move(playlist[current], v.get())
                        lb("Moved: "+playlist[current]+" => "+v.get())
                        lb("")
                        global m
                        m += 1
                        play(+1)
                    else:
                        lb("Error: Source file does not exist: "+(playlist[current]).split('/')[-1])
                except shutil.Error:
                    lb("Error: "+(playlist[current]).split('/')[-1]+": already exists at destination: "+v.get())
                except FileNotFoundError:
                    lb("Error: File not found: "+(playlist[current]).split('/')[-1])
            else:
                lb("Error: Directory does not exist: "+v.get())
        else:
            lb("Error: Directory not selected")
        lb("")

    def movedir():
        if en.get():
            if os.path.isdir(v.get()):
                try:
                    shutil.move(en.get(), v.get())
                    lb("Moved: "+en.get()+" => "+v.get())
                except shutil.Error:
                    lb("Error: "+en.get()+": already exists at destination: "+v.get())
            else:
                lb("Error: Directory does not exist: "+v.get())
        else:
            lb("Error: Directory not selected")
        lb("")

    def delete():
        if en.get():
            send2trash(playlist[current])
            lb("Deleted: "+playlist[current])
            lb("")
            global d
            d += 1
            play(+1)
        else:
            lb("Error: Directory not selected")
        lb("")

    def deleteall():
        if en.get():
            res = messagebox.askyesno('Confirmation','Do you want to Delete all files?')
            if res:
                lb("Deleted All files: ")
                for i in range(len(playlist)):
                     try:
                         send2trash(playlist[i])
                         lb(" -  "+playlist[i])
                         global d
                         d += 1
                     except:
                         lb(" -  "+"Already Deleted: "+playlist[i])
            else:
                lb("Info: Operation to delete all files cancelled")
        else:
            lb("Error: Directory not selected")
        lb("")

    def del_dir():
        if en.get():
            try:
                if os.listdir(en.get()) == []:
                    os.rmdir(en.get())
                    lb("Directory Deleted: "+ en.get())
                else:            
                    lb("Directory not empty: Contains "+ str(len(os.listdir(en.get()))) + " files")
            except FileNotFoundError:
                lb("Error: Directory not found, probably already deleted")
        else:
            lb("Error: Directory not selected")
        lb("")

    def clear():
        listbox.delete(0, END)

    def exit():
        for proc in psutil.process_iter():
            if proc.name() == "vlc":
                proc.kill()
        root.quit()

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
            lb("Saved Directory: "+en2.get()+" "+en3.get())
        else:
            lb("Error: Directory/Name not selected")
        lb("")

    def delentry():
        f = open('dirlist.ini','r')
        l = f.readlines()
        if en4.get():
            n = int(en4.get())-1
        else:
            lb("Error: Number not entered")
            return
        try:
            lb("Removing Listed Directory: " + l[n])
            line = l[0:n] + l[n+1:]
            f.close()
            f2 = open('dirlist.ini','w')
            for i in line:
                f2.write(i)
            f2.close()
        except IndexError:
            lb("Error: Invalid Number Entered")
        lb("")

    #Save Directory list Section
    def dirlist():
        win1 = tkinter.Toplevel()
        Label(win1, text="Insert Directory").grid(row=0, column=0, rowspan=1, columnspan=8)
        
        global en2, en3, en4
        en2 = tkinter.Entry(win1, width=10)
        en2.grid(row=1, column=0, rowspan=1, columnspan=1, sticky=W)

        en3 = tkinter.Entry(win1, width=40)
        en3.grid(row=1, column=1, rowspan=1, columnspan=4, sticky=W)

        Button(win1, text="Browse", command=browse2).grid(row=1, column=5, rowspan=1, columnspan=1, ipadx=10)
        Button(win1, text="Save", command=save).grid(row=1, column=6, rowspan=1, columnspan=1, ipadx=10)

        Label(win1, text="Remove Directory").grid(row=2, column=0, rowspan=1, columnspan=8)
        en4 = tkinter.Entry(win1, width=10)
        en4.grid(row=3, column=0, rowspan=1, columnspan=1, sticky=W)

        Button(win1, text="Del Entry", command=lambda: delentry()).grid(row=3, column=1, rowspan=1, columnspan=1, ipadx=10)
        Button(win1, text='Quit', command=win1.destroy).grid(row=3, column=6, rowspan=1, columnspan=1, ipadx=15)

    # Buttons Config:
    Button(root, text='Play',  command=lambda: play(0)).grid(row=0, column=1, rowspan=1, columnspan=1, ipadx=10)
    Button(root, text='Prev', command=lambda: play(-1)).grid(row=0, column=2, rowspan=1, columnspan=1, ipadx=10)
    Button(root, text='Next', command=lambda: play(+1)).grid(row=0, column=3, rowspan=1, columnspan=1, ipadx=10)
    Button(root, text='List', command=lambda: ls_dir()).grid(row=0, column=4, rowspan=1, columnspan=1, ipadx=10)
    Button(root, text='Stats', command=lambda: stats()).grid(row=0, column=5, rowspan=1, columnspan=1, ipadx=10)
    Button(root, text='Clear', command=lambda: clear()).grid(row=0, column=6, rowspan=1, columnspan=1, ipadx=10)

    # Browse & Entry Box
    Button(root, text="Browse", command=browse).grid(row=1, column=1, rowspan=1, columnspan=1, ipadx=10)
    en = Entry(root)
    en.grid(row=1, column=2, rowspan=1, columnspan=8, sticky=W, ipadx=100)
    en.focus_set()
    Button(root, text="Open", command=openfolder).grid(row=1, column=8, rowspan=1, columnspan=1, ipadx=10)

    # Directory buttons
    v = StringVar()
    try:
        head = Label(root, text="Directory:")
        head.grid(row=0, column=0, rowspan=1, columnspan=1)
        v.set(MODES[0][1])  # Initialize
        i = 1               # Start Dir List from Row no 3
        for text, mode in MODES:
            b = Radiobutton(root, text=text, variable=v, value=mode)
            b.grid(row=i, column=0, rowspan=1, columnspan=1,sticky=W)
            i += 1
    except:
        pass

    # Output Logs Box
    scrollbar = Scrollbar(root, orient=VERTICAL)
    listbox = Listbox(root, height=20, width=70, yscrollcommand=scrollbar.set)
    listbox.xview_scroll(3, "pages")
    listbox.yview_scroll(3, "pages")
    scrollbar.config(command=listbox.yview)
    listbox.grid(row=3, column=1, rowspan=12, columnspan=9)
    scrollbar.grid(row=3, column=10, rowspan=13, columnspan=1, sticky=NW, ipady = 148)

    lb("Ready, Log Output:")
    lb("")

    #var = IntVar()
    #var2 = IntVar()

    # Buttons with file operations
    Button(root, text='Move', command=lambda: move()).grid(row=3, column=13, rowspan=1, columnspan=1, ipadx=13)
    Button(root, text='Move Dir', command=lambda: movedir()).grid(row=5, column=13, rowspan=1, columnspan=1, ipadx=3)
    Button(root, text='Delete', command=lambda: delete()).grid(row=7, column=13, rowspan=1, columnspan=1, ipadx=10)
    Button(root, text='Del All', command=lambda: deleteall()).grid(row=9, column=13, rowspan=1, columnspan=1, ipadx=10)
    #Checkbutton(root, text="Confirm", variable=var).grid(row=9, column=14, rowspan=1, columnspan=1)
    Button(root, text='Del Dir', command=lambda: del_dir()).grid(row=11, column=13, rowspan=1, columnspan=1, ipadx=10)
    #Checkbutton(root, text="Confirm", variable=var2).grid(row=11, column=14, rowspan=1, columnspan=1)
    Button(root, text='Edit Dir', command=lambda: dirlist()).grid(row=13, column=13, rowspan=1, columnspan=1, ipadx=9)
    Button(root, text='Quit', command=exit).grid(row=15, column=13, rowspan=1, columnspan=1, ipadx=17)

    # Validate Directories
    try: 
        for i in range(len(MODES)):
            if os.path.exists(MODES[i][1]):
                pass
            else:
                lb("Error: Directory does not exist: "+MODES[i][0]+" - "+MODES[i][1])
        lb("")
    except:
        pass

    root.geometry('800x450')
    root.title("Video Collection Manager")
    
    try:
        img = PhotoImage(file='icon.png')
        root.tk.call('wm', 'iconphoto', root._w, img)
    except:
        lb("icon.png file not found")
        
    root.mainloop()

except:
    print("Error:", sys.exc_info())
    f = open('vigmgr_error.log', 'a')
    f.write(str(sys.exc_info())+"\r")
    f.close()
    sys.exit()

