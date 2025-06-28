#!/usr/bin/env python3
# Integrate VLC Window in main Window
# Undo Button for Deleted Files
# Memory save last location...... Dirlist - Browse
# Delete Empty Folders Function update
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
frame3 = Frame(frame, height=300, width=100, bd=3, relief=GROOVE)
frame3.grid(row=0, column=1, rowspan=2, sticky=N)

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

# Variables
array,playlist,MODES = [],[],[]
m,d,curr = 0,0,0
loc_mem = 0
loc_mem2 = 0

# Populate Directory List
try:
    array = [line.rstrip('\n') for line in open('dirlist.ini')]
except FileNotFoundError:
    '''print("Error: dirlist.ini not found. Please create the file.")
    sys.exit()'''
    lb("Error: dirlist.ini not found. Please create the file.")

for i in range(len(array)):
    MODES.append(array[i].split(';'))

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
        global playlist, current, d, m
        playlist = []
        current,d,m = 0,0,0
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
        lb("Total no of Files: "+str(len(playlist)))
        lb("")
    except FileNotFoundError:
        lb("Error: Directory not selected")
        lb("")

def top():
    lb("Fn Under Construction")
    try:
        global playlist, current, d, m
        playlist = []
        temp_pl = {}
        for root,dire,filelist in os.walk(en.get()):
                for filename in filelist:
                    filepath = os.path.join(root, filename)
                    filesize = os.path.getsize(filepath)
                    temp_pl.update({filepath:filesize})
        pl = sorted([(v, k) for k, v in temp_pl.items()], reverse=True)[0:10]
        for l in pl:
            lb("File: " + str(l[1]) + " [" + str(round(l[0]/(1024*1024))) + "MB]")
            playlist.append(l[1])
        lb("Total no of Files: " + str(len(playlist)))
        lb("playlist")
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
            lb("Info: End of Playlist")
            lb("")
            bar['value'] = 100
            return
        current += delta
        song = 'vlc -q "%s" 2> /dev/null' %playlist[current]
        if os.path.isfile(playlist[current]):
            lb(str(current+1)+": "+"vlc: "+(playlist[current]).split('/')[-1]+ " " + "["+ filesize(playlist[current]) + "MB" + "]")
            bar['value'] = int((current/len(playlist))*100)
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
                if var.get():
                    res1 = messagebox.askyesno('Confirmation','Do you want to move selected Directory?', parent=frame)
                    if res1:
                        try:
                            frame.config(cursor="watch")
                            frame.update()
                            shutil.move(en.get(), mode)
                            orig_file = en.get()
                            new_path = mode
                            frame.config(cursor="")
                            lb("Info: Directory moved: "+en.get()+" => "+mode)
                        except shutil.Error:
                            lb("Error: "+en.get()+": already exists at destination: "+mode)
                            lb("")
                    else:
                        lb("Info: Operation to delete all files cancelled")
                        lb("")
                else:
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
                            global m
                            m += 1
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

def moveto():
    global orig_file
    global new_path
    global loc_mem2
    if en.get():
        try:
            try:
                if loc_mem2:
                    mvdir = filedialog.askdirectory(parent=frame, initialdir=loc_mem2, title='Please select a directory')
                else:
                    mvdir = filedialog.askdirectory(parent=frame, initialdir=path.moveto, title='Please select a directory')
            except:
                mvdir = filedialog.askdirectory(parent=frame, initialdir=os.getcwd(), title='Please select a directory')
            loc_mem2 = mvdir
            if os.path.isdir(mvdir):
                if var.get():
                    res2 = messagebox.askyesno('Confirmation','Do you want to move selected Directory?', parent=frame)
                    if res2:
                        try:
                            frame.config(cursor="watch")
                            frame.update()
                            shutil.move(en.get(), mvdir)
                            orig_file = en.get()
                            new_path = mvdir
                            frame.config(cursor="")
                            lb("Info: Directory moved: "+en.get()+" => "+mvdir)
                            lb("")
                        except shutil.Error:
                            lb("Error: "+en.get()+": already exists at destination: "+mvdir)
                            lb("")
                    else:
                        lb("Info: Operation to delete all files cancelled")
                        lb("")
                else:
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
                            global m
                            m += 1
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
                global d
                d += 1
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

def deleteall():
    if en.get():
        res2 = messagebox.askyesno('Confirmation','Do you want to Delete all files?', parent=frame)
        if res2:
            lb("Deleted All files: ")
            for i in range(len(playlist)):
                 try:
                     send2trash(playlist[i])
                     lb(" -  "+playlist[i])
                     global d
                     d += 1
                 except:
                     lb(" -  "+"Already Deleted: "+playlist[i])
                     lb("")
        else:
            lb("Info: Operation to delete all files cancelled")
            lb("")
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
                lb("")
        except FileNotFoundError:
            lb("Error: Directory not found, probably already deleted")
            lb("")
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

def empty_folder_del():
    if en.get():
        deleted_dir = os.popen('find /data/.folder/ -type d -empty -print -delete')
        lb(("Deleted:", deleted_dir.readlines()))
        lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

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

def page():
    webbrowser.open_new(r"https://github.com/amanjosan2008/Video-Collection-Manager")

def about():
    win2 = Toplevel()
    win2.attributes('-topmost','true')
    win2.title("About")

    frame5 = Frame(win2, height=100, width=300, bd=3, relief=GROOVE)
    frame5.grid()
    Button(frame5, text="Visit Project Page", command=page).grid(row=0, sticky=W)


#Save Directory list Section
def dirlist():
    global win1
    win1 = Toplevel()
    win1.attributes('-topmost', 'true')
    win1.title("Directory Operations")

    global frame4
    frame4 = Frame(win1, height=800, width=700, bd=3, relief=GROOVE)
    frame4.grid()

    Label(frame4, text="Directory List:").grid(row=0, columnspan=8)

    f = open('dirlist.ini','r')
    l = f.readlines()
    j = 1
    for i in l:
        x = i.split(';')
        Button(frame4, width=30, text=x[0], relief=SUNKEN).grid(row=j, column=0, sticky=W)
        Button(frame4, width=60, text=x[1].rstrip(), relief=SUNKEN).grid(row=j, column=1, columnspan=2, sticky=W)
        Button(frame4, width=5, text="Del", command=lambda j=j-1: delentry(j)).grid(row=j, column=3, sticky=W)
        j += 1

    global en2,en3
    en2 = Entry(frame4, width=30)
    en2.grid(row=j+1,column=0)
    en3 = Entry(frame4, width=50)
    en3.grid(row=j+1,column=1)
    Button(frame4, text="Browse", command=browse2).grid(row=j+1, column=2)
    Button(frame4, text="Save", command=save).grid(row=j+1, column=3)
    Button(frame4, text='Quit', command=win1.destroy).grid(row=j+2, column=3)

def delentry(n):
    f = open('dirlist.ini','r')
    l = f.readlines()
    line = l[0:n] + l[n+1:]
    f.close()
    f2 = open('dirlist.ini','w')
    for i in line:
        f2.write(i)
    f2.close()
    i = l[n].split()
    lb("Info: Removing Listed Directory: " + i[0]+" - "+i[1]+"; Restart the App to load Directories")
    lb("")
    win1.destroy()
    dirlist()

def browse2():
    try:
        dir = filedialog.askdirectory(parent=frame4, initialdir=path.browse2, title='Please select a directory')
    except:
        dir = filedialog.askdirectory(parent=frame4, initialdir=os.getcwd(), title='Please select a directory')
    en3.delete(0,END)
    en3.insert(0,dir)

def save():
    if en2.get() and en3.get():
        f = open('dirlist.ini','a')
        f.write(en2.get()+";"+en3.get()+"\r")
        f.close()
        lb("Info: Dirlist.ini Entry saved => "+en2.get()+" - "+en3.get()+"; Restart the App to load Directories")
        lb("")
        win1.destroy()
        dirlist()
    else:
        messagebox.showerror('Empty','Please Enter data in both columns', parent=frame4)
        lb("")

# Menu Configuration
menu = Menu(frame)

item1 = Menu(menu, tearoff=0)
item1.add_command(label='Browse', command=browse)
item1.add_command(label='Explore', command=openfolder)
item1.add_separator()
item1.add_command(label='Restart', command=restart)
item1.add_command(label='Exit', command=exit)

item2 = Menu(menu, tearoff=0)
item2.add_command(label='Edit Dirlist', command=dirlist)
item2.add_separator()
item2.add_command(label='Delete All', command=deleteall)
item2.add_command(label='Delete Dir', command=del_dir)
item2.add_command(label='Delete Empty Dir', command=empty_folder_del)

item3 = Menu(menu, tearoff=0)
item3.add_command(label='List Files', command=ls_dir)
item3.add_command(label='Top10 Files', command=top)
item3.add_command(label='Stats', command=stats)
item3.add_command(label='Clear Logs', command=clear)

item4 = Menu(menu, tearoff=0)
item4.add_command(label='About', command=about)

menu.add_cascade(label='File', menu=item1)
menu.add_cascade(label='Operations', menu=item2)
menu.add_cascade(label='Options', menu=item3)
menu.add_cascade(label='Help', menu=item4)

root.config(menu=menu)

# Buttons Config:
Button(frame1, text='Play (\u23CE)', command=lambda: play(0), width=7).grid(row=0, column=0)
Button(frame1, text='Prev (\u2190)', command=lambda: play(-1), width=7).grid(row=0, column=1)
Button(frame1, text='Next (\u2192)', command=lambda: play(+1), width=7).grid(row=0, column=2)

# Entry Box
en = Entry(frame1)
en.grid(row=0, column=3, columnspan=4, sticky=W, ipadx=90)

# Directory buttons
v = StringVar()

i = 0    # no of Row for the buttons in column no 4
j = 4    # no of Column (4 or 5)
#k = 0    # no of Row for the buttons in column no 5
l = 27   # no of buttons for next column
#m = 0    # no of Row for the buttons in column no 6

try:
    for text, mode in MODES:
        b = Button(frame3, text=text, textvariable=mode, command=lambda mode=mode: move(mode), width=10)
        b.grid(row=i, column=j, sticky=W)
        if i > l:
            j += 1
            i = 0
            b.grid(row=i, column=j, sticky=W)
        i += 1
except ValueError:
    lb("Error: Data in Dirlist.ini not correctly formatted")
    lb("")

if i==0:
    lb("Error: No Directories found in Dirlist.ini")
    lb("")

# Buttons with Directory operations
'''
if i <= l:
    Button(frame3, text='Move to ..', command=moveto, width=10).grid(row=i+1)
    Button(frame3, text='Delete (X)', command=lambda: delete(), width=10, fg="red").grid(row=i+2)
elif i > l:
    if i > (l*2):
        Button(frame3, text='Move to ..', command=moveto, width=10).grid(row=m, column=j+2)
        Button(frame3, text='Delete (X)', command=lambda: delete(), width=10, fg="red").grid(row=m+1, column=j+2)
    else:
        Button(frame3, text='Move to ..', command=moveto, width=10).grid(row=k, column=j+1)
        Button(frame3, text='Delete (X)', command=lambda: delete(), width=10, fg="red").grid(row=k+1, column=j+1)
'''

Button(frame3, text='Move to ..', command=moveto, width=10).grid(row=i, column=j)
Button(frame3, text='Delete (X)', command=lambda: delete(), width=10, fg="red").grid(row=i+1, column=j)

lb("Ready, Log Output:")
#lb("")

# Progress Bar
bar = ttk.Progressbar(frame2, length=430)
bar.grid(row=2,column=0)

# Move Dir Checkbox
var = IntVar()
Checkbutton(frame2, text="Move Dir", variable=var).grid(row=2, column=1)

# Undo Button
Button(frame2, text="Undo", command=undo).grid(row=2, column=2)

# Validate Directories
try:
    for k in range(len(MODES)):
        if os.path.exists(MODES[k][1]):
            pass
        else:
            lb("Error: Directory does not exist: "+MODES[k][0]+" - "+MODES[k][1])
            lb("")
except:
    pass

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
