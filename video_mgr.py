#!/usr/bin/env python3
# Integrate VLC Window in main Window
# Add Icon to all Buttons
# Undo last operation Button
# DelEntry() lb print remove '\t'
# Restart Menu Item not Working

import os,sys
import time
from tkinter import *
from tkinter import ttk, filedialog, messagebox
import subprocess
import shutil
from send2trash import send2trash
import psutil
import webbrowser

root = Tk()

# Main Frame
frame = Frame(root, height=800, width=700, bd=3, relief=RIDGE)
frame.grid()

# Sub Frames
frame1 = Frame(frame, height=50, width=500, bd=3, relief=GROOVE)
frame1.grid(row=0, column=0, columnspan=2, sticky=NW)

frame2 = Frame(frame, height=300, width=400, bd=3, relief=GROOVE)
frame2.grid(row=1, column=0, sticky=N)

frame3 = Frame(frame, height=300, width=100, bd=3, relief=GROOVE)
frame3.grid(row=0, column=1, rowspan=2, sticky=N)

# Output Logs Box
scrollbar = Scrollbar(frame2, orient=VERTICAL, cursor='sb_v_double_arrow')
listbox = Listbox(frame2, height=40, width=63, yscrollcommand=scrollbar.set)
listbox.xview_scroll(3, "pages")
listbox.yview_scroll(3, "pages")
scrollbar.config(command=listbox.yview)
listbox.grid(row=0, column=0, columnspan=2)
scrollbar.grid(row=0, column=2, sticky=E, ipady=306)

# Variables
array,playlist,MODES = [],[],[]
m,d,curr = 0,0,0

# Populate Directory List
try:
    array = [line.rstrip('\n') for line in open('dirlist.ini')]
except FileNotFoundError:
    print("Error: dirlist.ini not found. Please create the file.")
    sys.exit()

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
            dir = filedialog.askdirectory(parent=frame1, initialdir='/data/.folder/', title='Please select a directory')
        except:
            dir = filedialog.askdirectory(parent=frame1, initialdir=os.getcwd(), title='Please select a directory')
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
        if os.path.isdir(en.get()):
            path = 'nautilus "%s"' %en.get()
            subprocess.Popen(path, shell=True)
            lb("Directory opened: "+en.get())
        else:
            lb("Error: Directory does not exists")
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
            lb("Info: End of Playlist")
            lb("")
            bar['value'] = 100
            return
        current += delta
        song = 'vlc -q "%s" 2> /dev/null' %playlist[current]
        if os.path.isfile(playlist[current]):
            lb(str(current+1)+": "+"VLC: "+playlist[current]+ " " + "["+ filesize(playlist[current]) + "MB" + "]")
            bar['value'] = int((current/len(playlist))*100)
            subprocess.Popen(song, shell=True)
        else:
            lb("Error: File not found: "+(playlist[current]).split('/')[-1])
            lb("")
    else:
        lb("Error: Directory not selected")
        lb("")

def move(mode):
    if en.get():
        if os.path.isdir(mode):
            if var.get():
                res1 = messagebox.askyesno('Confirmation','Do you want to move selected Directory?', parent=frame)
                if res1:
                    try:
                        frame.config(cursor="watch")
                        frame.update()
                        shutil.move(en.get(), mode)
                        frame.config(cursor="")
                        lb("Info: Directory moved: "+en.get()+" => "+mode)
                    except shutil.Error:
                        lb("Error: "+en.get()+": already exists at destination: "+mode)
                else:
                    lb("Info: Operation to delete all files cancelled")
            else:
                try:
                    if os.path.isfile(playlist[current]):
                        frame.config(cursor="watch")
                        frame.update()
                        shutil.move(playlist[current], mode)
                        lb("Moved: "+playlist[current]+" => "+mode)
                        lb("")
                        frame.config(cursor="")
                        global m
                        m += 1
                        play(+1)
                    else:
                        lb("Error: Source file does not exist: "+(playlist[current]).split('/')[-1])
                except shutil.Error:
                    lb("Error: "+(playlist[current]).split('/')[-1]+": already exists at destination: "+mode)
                    frame.config(cursor="")
                except FileNotFoundError:
                    lb("Error: File not found: "+(playlist[current]).split('/')[-1])
                    frame.config(cursor="")
        else:
            lb("Error: Directory does not exist: "+mode)
    else:
        lb("Error: Directory not selected")
    lb("")

def movedir():
    if en.get():
        try:
            try:
                mvdir = filedialog.askdirectory(parent=frame, initialdir='/media/system/Data/Vids/', title='Please select a directory')
            except:
                mvdir = filedialog.askdirectory(parent=frame, initialdir=os.getcwd(), title='Please select a directory')
            if os.path.isdir(mvdir):
                try:
                    if os.path.isfile(playlist[current]):
                        frame.config(cursor="watch")
                        frame.update()
                        shutil.move(playlist[current], mvdir)
                        lb("Moved: "+playlist[current]+" => "+mvdir)
                        lb("")
                        frame.config(cursor="")
                        global m
                        m += 1
                        play(+1)
                    else:
                        lb("Error: Source file does not exist: "+(playlist[current]).split('/')[-1])
                except shutil.Error:
                    lb("Error: "+(playlist[current]).split('/')[-1]+": already exists at destination: "+mvdir)
                    frame.config(cursor="")
                except FileNotFoundError:
                    lb("Error: File not found: "+(playlist[current]).split('/')[-1])
                    frame.config(cursor="")
            else:
                lb("Error: Directory does not exist: "+mvdir)
        except TypeError:
            lb("Info: Move Directory operation cancelled by User")
    else:
        lb("Error: Directory not selected")
    lb("")

def delete():
    if en.get():
        if os.path.isfile(playlist[current]):
            send2trash(playlist[current])
            lb("Deleted: "+playlist[current])
            lb("")
            global d
            d += 1
            play(+1)
        else:
            lb("Error: File not found/moved/already deleted")
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

def vmode(delta):
    global curr
    if not (0 <= curr + delta < len(MODES)):
        lb("Info: End of Directory List")
        lb("")
        return
    curr += delta
    v.set(MODES[curr][1])

def restart():
    root.update()

# Keyboard Binding related functions
def playnext(event):
    play(+1)

def playprev(event):
    play(-1)
    
def playcurr(event):
    play(0)

def br(event):
    browse()

#def mv(event):
#    movedir()

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

    frame4 = Frame(win2, height=100, width=300, bd=3, relief=GROOVE)
    frame4.grid()
    Button(frame4, text="Visit Project Page", command=page).grid(row=0, sticky=W)


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
        x = i.split('\t')
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
    lb("Removing Listed Directory: " + l[n].rstrip()+" Restart the App to load Directories")
    lb("")
    win1.destroy()
    dirlist()

def browse2():
    try:
        dir = filedialog.askdirectory(parent=frame4, initialdir='/media/system/Data/Vids/', title='Please select a directory')
    except:
        dir = filedialog.askdirectory(parent=frame4, initialdir=os.getcwd(), title='Please select a directory')
    en3.delete(0,END)
    en3.insert(0,dir)

def save():
    if en2.get() and en3.get():
        f = open('dirlist.ini','a')
        f.write(en2.get()+"\t"+en3.get()+"\r")
        f.close()
        lb("Info: Dirlist.ini Entry saved => "+en2.get()+" - "+en3.get()+" Restart the App to load Directories")
        win1.destroy()
        dirlist()
    else:
        messagebox.showerror('Empty','Please Enter data in both columns', parent=frame4)

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

item3 = Menu(menu, tearoff=0)
item3.add_command(label='List Files', command=ls_dir)
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
en.grid(row=0, column=3, columnspan=4, sticky=W, ipadx=50)

# Directory buttons
v = StringVar()

i = 0
try:
    for text, mode in MODES:
        b = Button(frame3, text=text, textvariable=mode, command=lambda mode=mode: move(mode), width=10)
        b.grid(row=i, sticky=W)
        i += 1
except ValueError:
    lb("Error: Data in Dirlist.ini not correctly formatted")

if i==0:
    lb("Error: No Directories found in Dirlist.ini")

# Buttons with Directory operations
Button(frame3, text='Move to ..', command=movedir, width=10).grid(row=i+1)
Button(frame3, text='Delete (X)', command=lambda: delete(), width=10, fg="red").grid(row=i+2)

lb("Ready, Log Output:")
lb("")

# Progress Bar
bar = ttk.Progressbar(frame2, length=420)
bar.grid(row=1,column=0)

# Move Dir Checkbox
var = IntVar()
Checkbutton(frame2, text="Move Dir", variable=var).grid(row=1, column=1)

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

#root.geometry('830x450')
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

root.mainloop()


