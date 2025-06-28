#!/usr/bin/env python3
# Integrate VLC Window in main Window
# Memory save last location...... Dirlist - Browse
# Delete Dir Entry no feedback

# Dependencies:
##sudo pip3 install psutil --break-system-packages

import os
import sys
import time
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import subprocess
import shutil
from send2trash import send2trash
import psutil
import webbrowser
import path


root = Tk()

# Main Frame ###init 700
frame = Frame(root, height=800, width=700, bd=3, relief=RIDGE)
frame.grid()

# Sub Frame for Play, Prev, Next Buttons
frame1 = Frame(frame, height=50, width=500, bd=3, relief=GROOVE)
frame1.grid(row=0, column=0, columnspan=2, sticky=NW)

# For Listbox, Progressbar, MoveDir Checkbox, Undo Button
frame2 = Frame(frame, height=300, width=400, bd=3, relief=GROOVE)
frame2.grid(row=1, column=0, sticky=N)

# For Right side Buttons ###init 100
frame3 = Frame(frame, height=300, width=100, bd=3, relief=SUNKEN)
frame3.grid(row=0, column=1, rowspan=2, sticky=N)

# For Right side Buttons ###init 100
frame4 = Frame(frame, height=300, width=100, bd=3, relief=GROOVE)
frame4.grid(row=0, column=2, rowspan=2, sticky=N)

# Output Logs Box
scrollbarv = Scrollbar(frame2, orient=VERTICAL, cursor='sb_v_double_arrow')
scrollbarh = Scrollbar(frame2, orient=HORIZONTAL, cursor='sb_h_double_arrow')
listbox = Listbox(frame2, height=40, width=73, yscrollcommand=scrollbarv.set, xscrollcommand=scrollbarh.set)
listbox.xview_scroll(5, "pages")
listbox.yview_scroll(3, "pages")
scrollbarv.config(command=listbox.yview)
scrollbarh.config(command=listbox.xview)
listbox.grid(row=0, column=0, columnspan=3)
scrollbarv.grid(row=0, column=3, sticky=E, ipady=345)
scrollbarh.grid(row=1, column=0, columnspan=3, sticky=S, ipadx=280)

# Statusbar
statusbar = Label(frame, anchor=W, text="Ready.." )
statusbar.grid(row=2, column=0, columnspan=3, sticky=W)

# Variables
array,playlist,MODES = [],[],[]
curr = 0
loc_mem = 0
loc_mem2 = 0

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
    global loc_mem
    try:
        global playlist, current
        playlist = []
        current = 0
        try:
            if loc_mem:
                dir = filedialog.askdirectory(parent=frame, initialdir=loc_mem, title='Please select a directory')
            else:
                dir = filedialog.askdirectory(parent=frame1, initialdir=path.browse, title='Please select a directory')
        except:
            dir = filedialog.askdirectory(parent=frame1, initialdir=os.getcwd(), title='Please select a directory')
        loc_mem = dir
        en.delete(0,END)
        en.insert(0,dir)
        for filename in os.listdir(en.get()):
                if os.path.isfile(os.path.join(en.get(), filename)):
                    playlist.append(os.path.join(en.get(), filename))
        statusbar.config(text="Total no of Files: "+str(len(playlist)))
    except FileNotFoundError:
        lb("Error: Directory not selected")
        lb("")

def openfolder():
    if en.get():
        if os.path.isdir(en.get()):
            path = 'nautilus "%s"' %en.get()
            subprocess.Popen(path, shell=True)
            lb("Directory opened: "+en.get())
            lb("")
        else:
            lb("Error: Directory does not exists")
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def ls_dir():
    if en.get():
        count = [name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))]
        if (len(count)==0):
            lb("Error: No Files in Directory")
            lb("")
        else:
            lb("File List:")
            for i in range(len(count)):
                lb(str(i+1)+ ". " + count[i] + " ["+ filesize(en.get()+"/"+count[i]) + "MB]")
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def play(delta):
    global current
    if en.get():
        if not (0 <= current + delta < len(playlist)):
            lb("Info: End of Playlist")
            lb("")
            return
        current += delta
        #song = 'vlc -q "%s" 2> /dev/null' %playlist[current]
        song = 'cvlc --play-and-exit "%s" 2> /dev/null' %playlist[current]
        if os.path.isfile(playlist[current]):
            #lb(str(current+1)+": "+"vlc: "+(playlist[current]).split('/')[-1]+ " " + "["+ filesize(playlist[current]) + "MB" + "]")
            st = str(current+1)+": "+"vlc: "+(playlist[current]).split('/')[-1]+ " " + "["+ filesize(playlist[current]) + "MB" + "]"
            statusbar.config(text=st)
            subprocess.Popen(song, shell=True)
        else:
            lb("Error: File not found: "+(playlist[current]).split('/')[-1])
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def move(mode):
    global orig_file
    global new_path
    if en.get():
        try:
            if os.path.isdir(mode):
                try:
                    if os.path.isfile(playlist[current]):
                        frame.config(cursor="watch")
                        frame.update()
                        shutil.move(playlist[current], mode)
                        orig_file = playlist[current]
                        new_path = mode
                        lb("Moved: "+(playlist[current]).split('/')[-1]+" => "+mode)
                        #lb("")
                        frame.config(cursor="")
                        play(+1)
                    else:
                        lb("Error: Source file does not exist: "+(playlist[current]).split('/')[-1])
                        lb("")
                except shutil.Error:
                    lb("Error: "+(playlist[current]).split('/')[-1]+": already exists at destination: "+mode)
                    lb("")
                    frame.config(cursor="")
                except FileNotFoundError:
                    lb("Error: File not found: "+(playlist[current]).split('/')[-1])
                    lb("")
                    frame.config(cursor="")
            else:
                lb("Error: Directory does not exist: "+mode)
                lb("")
        except NameError:
            lb("Error: Directory is empty or invalid")
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def moveto(loc_mem2):
    global orig_file
    global new_path
    if en.get():
        try:
            '''
            try:
                if loc_mem2:
                    mvdir = filedialog.askdirectory(parent=frame, initialdir=loc_mem2, title='Please select a directory')
                else:
                    mvdir = filedialog.askdirectory(parent=frame, initialdir=path.moveto, title='Please select a directory')
            except:
                mvdir = filedialog.askdirectory(parent=frame, initialdir=os.getcwd(), title='Please select a directory')
            loc_mem2 = mvdir
            '''
            mvdir = filedialog.askdirectory(parent=frame, initialdir=loc_mem2, title='Please select a directory')
            if os.path.isdir(mvdir):
                try:
                    if os.path.isfile(playlist[current]):
                        frame.config(cursor="watch")
                        frame.update()
                        shutil.move(playlist[current], mvdir)
                        orig_file = playlist[current]
                        new_path = mvdir
                        lb("Moved: "+playlist[current]+" => "+mvdir)
                        #lb("")
                        frame.config(cursor="")
                        play(+1)
                    else:
                        lb("Error: Source file does not exist: "+(playlist[current]).split('/')[-1])
                        lb("")
                except shutil.Error:
                    lb("Error: "+(playlist[current]).split('/')[-1]+": already exists at destination: "+mvdir)
                    lb("")
                    frame.config(cursor="")
                except FileNotFoundError:
                    lb("Error: File not found: "+(playlist[current]).split('/')[-1])
                    lb("")
                    frame.config(cursor="")
                except IndexError:
                    lb("Error: No file in Directory: " + en.get())
                    lb("")
                    frame.config(cursor="")
            else:
                lb("Error: Directory does not exist: "+mvdir)
                lb("")
        except TypeError:
            lb("Info: Move Directory operation cancelled by User")
            lb("")
        except NameError:
            lb("Error: Directory is empty or invalid")
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def delete():
    if en.get():
        try:
            if os.path.isfile(playlist[current]):
                send2trash(playlist[current])
                lb("Deleted: "+playlist[current])
                #lb("")
                play(+1)
            else:
                lb("Error: File not found/moved/already deleted:" + playlist[current])
                lb("")
        except NameError:
            lb("Error: Directory does not exist or not selected")
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def exit():
    for proc in psutil.process_iter():
        if proc.name() == "vlc":
            proc.kill()
    root.quit()

def vmode(delta):
    global curr
    if not (0 <= curr + delta < len(MODES)):
        lb("Info: End of Directory List")
        lb("")
        return
    curr += delta
    v.set(MODES[curr][1])

def restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)

def undo():
    try:
        name = orig_file.split('/')[-1]
        path = os.path.join(new_path +'/'+name)
        orig_dir = os.path.dirname(orig_file)
        if os.path.isfile(path):
            if os.path.isdir(orig_dir):
                shutil.move(path,orig_dir)
                lb("Undo: Moved file: "+name+" to Dir "+orig_dir)
                lb("")
            else:
                lb("Error: Source Dir does not exist: "+ orig_dir)
                lb("")
        else:
            lb("Error: File not found: "+ name + "in Dir: " + path)
            lb("")
    except NameError:
        lb("Error: No file moved, Cannot use Undo function")
        lb("")

# Keyboard Binding related functions
def playnext(event):
    play(+1)

def playprev(event):
    play(-1)

def playcurr(event):
    play(0)

def br(event):
    browse()

def delt(event):
    delete()

def modeup(event):
    vmode(-1)

def modedown(event):
    vmode(+1)
    

# Menu Configuration
menu = Menu(frame)

item1 = Menu(menu, tearoff=0)
item1.add_command(label='Open Dir', command=openfolder)
item1.add_command(label='List Files', command=ls_dir)
item1.add_separator()
item1.add_command(label='Restart', command=restart)
item1.add_command(label='Exit', command=exit)

menu.add_cascade(label='File', menu=item1)

root.config(menu=menu)

# Buttons Config:
Button(frame1, text="Browse", command=browse).grid(row=0, column=0)
Button(frame1, text='Play (\u23CE)', command=lambda: play(0), width=7).grid(row=0, column=1)
Button(frame1, text='Prev (\u2190)', command=lambda: play(-1), width=7).grid(row=0, column=2)
Button(frame1, text='Next (\u2192)', command=lambda: play(+1), width=7).grid(row=0, column=3)
Button(frame1, text="Undo", command=undo).grid(row=0, column=4)
Button(frame1, text="Delete", command=lambda: delete(), width=10, fg="red").grid(row=0, column=5)

# Entry Box
en = Entry(frame1)
en.grid(row=1, column=0, columnspan=6, sticky=W, ipadx=150)

# Directory buttons
v = StringVar()

i = 0    # no of Row for the buttons in column no 4
j = 4    # no of Column (4 or 5)

with open('dirlist.ini') as my_file:
    array = my_file.readlines()
        
try:
    for array_line in array:
        array_info = array_line.strip()
        if array_info == 'NEXT':
            j = j+1
            i = 0
        else:
            text,mode = array_info.split(';')

            if j <= 8:
                if text == 'MOVETO':
                    b = Button(frame3, text=text, textvariable=mode, command=lambda mode=mode: moveto(mode), width=10)
                else:
                    b = Button(frame3, text=text, textvariable=mode, command=lambda mode=mode: move(mode), width=10)
                b.grid(row=i, column=j, sticky=W)
            else:
                if text == 'MOVETO':
                    b = Button(frame4, text=text, textvariable=mode, command=lambda mode=mode: moveto(mode), width=10)
                else:
                    b = Button(frame4, text=text, textvariable=mode, command=lambda mode=mode: move(mode), width=10)
                b.grid(row=i, column=j, sticky=W)
            
            # Validate Directories & disable button if not present
            if not os.path.exists(mode):
                lb("Dir not found: "+ text +" - "+ mode)
                b.config(state=DISABLED)
            i += 1
except ValueError:
    lb("Error: Data in Dirlist.ini not correctly formatted")
    lb("")

if i==0:
    lb("Error: No Directories found in Dirlist.ini")
    lb("")

statusbar.config(text="Ready..")

root.title("Video Collection Manager")
root.bind('<Return>', playcurr)
root.bind('<Left>', playprev)
root.bind('<Right>', playnext)
#root.bind('z', mv)
root.bind('x', delt)
root.bind('b', br)

try:
    img = PhotoImage(file='icon.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
except:
    lb("Error: icon.png file not found")
    lb("")

root.mainloop()
