from tkinter import *
from tkinter import messagebox
from socket import *
from threading import *
from time import *
import os

window_size_x=900
window_size_y=612
font="Arial"
font_size=10
font_size_list=9
cursor_pen="pencil"
cursor_eraser="circle"
title="SketchPy"
version="v1.0"
author="Vladimir Sindler (CppToast)"
date="2019-2020"
about_message="Special thanks to Mihael Bobicanec (my programming teacher) for making this happen. Also, thanks to a sizable amount of toast, chocolate milk, ice tea and cappuccino. They are delicious."

last_x=0
last_y=0
drawing=False
color="#000000"
bg_color="#FFFFFF"
thickness=4
tool=0
player_name=""
server_ip=""
server_name = ""
word=""
time_remaining=0
superchat=False
queue=[]
next_tick_queue = []
saved_servers = []
connected=False
last_draw_time = 0
last_comm_time = 0

def about():
    global title
    global version
    global author
    global date
    global photoimage_logo

    about_window_size_x=300
    about_window_size_y=250
    about_window=Toplevel() # because Tk() throws an error if used here
    about_window.title("About this game")
    about_window.minsize(about_window_size_x,about_window_size_y)
    about_window.maxsize(about_window_size_x,about_window_size_y)
    about_window.geometry("+{}+{}".format(int(about_window.winfo_screenwidth()/2-about_window_size_x/2),int(about_window.winfo_screenheight()/2-about_window_size_y/2)))
    about_window.focus_force()

    logo=Label(about_window,image=photoimage_logo)
    logo.place(x=20,y=20)

    about_info=Message(about_window,text=title+"\n"+version+"\nby "+author+"\n"+date+"\n\n"+about_message,width=200,font=(font,font_size_list))
    about_info.place(x=60,y=10)

    ok_button=Button(about_window,text="OK",width=10,command=about_window.destroy,font=(font,font_size))
    ok_button.place(x=180,y=200)

def refreshPreviewCanvas(thick):
    global color
    global bg_color
    global thickness
    thickness=int(thick)
    preview_canvas.coords(circle_pen,42-thickness,42-thickness,42+thickness,42+thickness)
    preview_canvas.itemconfig(circle_pen,fill=color)
    thickness_label.config(text="Thickness: "+str(thickness))

def changeColor(col):
    global color
    global thickness
    color=col
    refreshPreviewCanvas(thickness)

def toolPen():
    global tool
    tool=0
    button_pen.config(relief=SUNKEN)
    button_eraser.config(relief=RAISED)
    image_canvas.config(cursor=cursor_pen)

def toolEraser():
    global tool
    tool=1
    button_pen.config(relief=RAISED)
    button_eraser.config(relief=SUNKEN)
    image_canvas.config(cursor=cursor_eraser)

def clearCanvas():
    if drawing:
        image_canvas.delete("all")
        queue.append("e")

def paint(event):
    global last_x
    global last_y
    global color
    global thickness
    global tool
    global drawing
    global last_draw_time
    new_time = perf_counter()
    if drawing==True and new_time-last_draw_time>0.02:
        if tool==0: t_color=color
        if tool==1: t_color="#FFFFFF"
        image_canvas.create_line(last_x,last_y,event.x,event.y,width=thickness*2+1,fill=t_color,capstyle=ROUND,smooth=TRUE,splinesteps=36)
        queue.append("d\t"+str(last_x)+"\t"+str(last_y)+"\t"+str(event.x)+"\t"+str(event.y)+"\t"+t_color+"\t"+str(thickness))
        last_x=event.x
        last_y=event.y
        last_draw_time = new_time

def drawOnCanvas(x1,y1,x2,y2,color,thickness):
    global image_canvas
    image_canvas.create_line(x1,y1,x2,y2,width=thickness*2+1,fill=color,capstyle=ROUND,smooth=TRUE,splinesteps=36)

def reset(event):
    global last_x
    global last_y
    last_x=event.x
    last_y=event.y
    paint(event)

def printChatMessage(schat,sender,chat_message):
    global superchat
    chat_box.config(state=NORMAL)
    if schat==0:
        chat_box.insert(END,sender+": ","tag_sender")
        chat_box.insert(END,chat_message+"\n")
    if schat==1 and superchat == True:
        chat_box.insert(END,sender+": ","tag_super")
        chat_box.insert(END,chat_message+"\n")
    chat_box.config(state=DISABLED)
    chat_box.see("end")

def printStatus(status_message,tag):
    chat_box.config(state=NORMAL)
    chat_box.insert(END,status_message+"\n",tag)
    chat_box.config(state=DISABLED)
    chat_box.see("end")

def sendChatMessage(nan):
    global superchat
    chat_message=entry_chat.get()
    chat_message=chat_message.strip()
    entry_chat.delete(0,END)
    queue.append("c"+chat_message)

def updatePlayerList(players):
    global list_players
    list_players.delete(0,"end")
    if connected == True:
        players = players.strip()
        players = players.split("\t")
        for i in range(len(players)):
            list_players.insert(i,players[i])

def changeName():
    global player_name
    global name_change_dialog
    global player_name_entry

    name_change_dialog_size_x=350
    name_change_dialog_size_y=80
    name_change_dialog=Tk()
    name_change_dialog.title("Change player name")
    name_change_dialog.minsize(name_change_dialog_size_x,name_change_dialog_size_y)
    name_change_dialog.maxsize(name_change_dialog_size_x,name_change_dialog_size_y)
    name_change_dialog.geometry("+{}+{}".format(int(name_change_dialog.winfo_screenwidth()/2-name_change_dialog_size_x/2),int(name_change_dialog.winfo_screenheight()/2-name_change_dialog_size_y/2)))
    name_change_dialog.focus_force()

    player_name_label=Label(name_change_dialog,text="New player name:",font=(font,font_size))
    player_name_label.place(x=10,y=10)

    name_length_label=Label(name_change_dialog,text="Max. length is 32 characters.",font=(font,font_size))
    name_length_label.place(x=10,y=42)
    
    player_name_entry=Entry(name_change_dialog,width=29,bd=2,font=(font,font_size))
    player_name_entry.insert(0,player_name)
    player_name_entry.place(x=121,y=10)
    player_name_entry.bind("<Return>",lambda x: acceptNewName()) # lambda because bind passes an argument and the function doesn't accept arguments
    player_name_entry.focus_force()

    ok_button=Button(name_change_dialog,text="OK",width=10,command=acceptNewName,font=(font,font_size))
    ok_button.place(x=240,y=40)

def acceptNewName():
    global player_name
    player_name=player_name_entry.get()
    player_name=player_name.strip()
    player_name=player_name[:32]
    player_name=player_name.strip()
    name_change_dialog.destroy()
    queue.append("n\t"+player_name)
    saveSettings()

def pickWord(words):
    global player_name
    global word_pick_dialog
    global player_name_entry

    word_pick_dialog_size_x=410
    word_pick_dialog_size_y=110
    word_pick_dialog=Toplevel()
    word_pick_dialog.title("Pick a word!")
    word_pick_dialog.minsize(word_pick_dialog_size_x,word_pick_dialog_size_y)
    word_pick_dialog.maxsize(word_pick_dialog_size_x,word_pick_dialog_size_y)
    word_pick_dialog.geometry("+{}+{}".format(int(word_pick_dialog.winfo_screenwidth()/2-word_pick_dialog_size_x/2),int(word_pick_dialog.winfo_screenheight()/2-word_pick_dialog_size_y/2)))
    word_pick_dialog.focus_force()
    word_pick_dialog.protocol('WM_DELETE_WINDOW', lambda:word_pick_dialog.bell())

    word_pick_label=Label(word_pick_dialog,text="You are drawing! Pick a word:",font=(font,font_size))
    word_pick_label.place(x=10,y=10)

    words = words.split("\t")
    word_button_0=Button(word_pick_dialog,text=words[0],width=23,font=(font,font_size),command = lambda: sendWord("0",words[0]))
    word_button_0.place(x=200,y=10)
    word_button_1=Button(word_pick_dialog,text=words[1],width=23,font=(font,font_size),command = lambda: sendWord("1",words[1]))
    word_button_1.place(x=200,y=40)
    word_button_2=Button(word_pick_dialog,text=words[2],width=23,font=(font,font_size),command = lambda: sendWord("2",words[2]))
    word_button_2.place(x=200,y=70)

def sendWord(number,newword):
    global word_pick_dialog
    global word
    global label_word
    global socket_holder
    queue.append("x"+number)
    word = newword
    label_word.configure(text=word)
    word_pick_dialog.destroy()

def connectDialog():
    global server_ip
    global connect_dialog
    global connect_entry
    global server_list
    global saved_servers

    connect_dialog_size_x=350
    connect_dialog_size_y=394
    connect_dialog=Tk()
    connect_dialog.title("Connect to a server")
    connect_dialog.minsize(connect_dialog_size_x,connect_dialog_size_y)
    connect_dialog.maxsize(connect_dialog_size_x,connect_dialog_size_y)
    connect_dialog.geometry("+{}+{}".format(int(connect_dialog.winfo_screenwidth()/2-connect_dialog_size_x/2),int(connect_dialog.winfo_screenheight()/2-connect_dialog_size_y/2)))
    connect_dialog.focus_force()

    connect_label=Label(connect_dialog,text="Server IP adress:",font=(font,font_size))
    connect_label.place(x=10,y=10)
    
    connect_entry=Entry(connect_dialog,width=29,bd=2,font=(font,font_size))
    connect_entry.place(x=121,y=10)
    connect_entry.bind("<Return>",lambda x: acceptServerIP()) # lambda because bind passes an argument and the function doesn't accept arguments
    connect_entry.focus_force()

    server_list = Listbox(connect_dialog,width=48,height=17,font=(font,font_size_list),bd=2)
    server_list.bind("<<ListboxSelect>>",lambda x: copySavedIP())
    server_list.place(x=4,y=75)
    
    for i in range(len(saved_servers)):
        server_list.insert(i,saved_servers[i][1])

    server_erase_button = Button(connect_dialog,text="Remove server from favorites",width=41,font=(font,font_size),command = removeServerFromFavorites)
    server_erase_button.place(x=5,y=357)

    ok_button=Button(connect_dialog,text="Connect",width=10,command=acceptServerIP,font=(font,font_size))
    ok_button.place(x=240,y=40)

def addServerToFavorites():
    global saved_servers
    if connected:
        saved_servers.append([server_ip,server_name])
        saveSettings()
        messagebox.showinfo("Server saved","Server added to favorites.")
    else:
        messagebox.showerror("Error","You are not connected to any server.")

def removeServerFromFavorites():
    global server_list
    global saved_servers
    global connect_dialog

    delete = messagebox.askyesno("Remove server","Are you sure you want to remove this server from favorites?")
    if delete:
        sel_server_index = server_list.curselection()[0]
        saved_servers.pop(sel_server_index)
        saveSettings()
        server_list.delete(0,"end")
        for i in range(len(saved_servers)):
            server_list.insert(i,saved_servers[i][1])
    connect_dialog.lift()
    connect_dialog.focus_force()

def copySavedIP():
    global connect_entry
    global server_list
    global saved_servers

    connect_entry.delete(0,END)
    sel_server_index = server_list.curselection()[0]
    sel_server_ip = saved_servers[sel_server_index][0]
    connect_entry.insert(0,sel_server_ip)

def acceptServerIP():
    global status_bar
    global connect_dialog
    global connect_entry
    input_ip=connect_entry.get()
    ip_adress=input_ip.replace(":",".").split(".")
    valid=1
    if len(ip_adress)!=5: valid=0
    else:
        for i in ip_adress:
            if i.isdigit() == False:
                valid=0
                break
        else:
            port=int(ip_adress[4])
            ip_adress.pop()
            for i in ip_adress:
                t=int(i)
                if t<0 or t>255:
                    valid=0
                    break
            if port<0 or port>65535: valid=0
    if valid==1:
        connect_dialog.destroy()
        input_ip=str(ip_adress[0])+"."+str(ip_adress[1])+"."+str(ip_adress[2])+"."+str(ip_adress[3])+":"+str(port)
        connect(input_ip)
    else:
        messagebox.showerror("Error","Invalid IP adress")
        connect_dialog.lift()
        connect_dialog.focus_force()
        connect_entry.focus_force()


def connect(input_ip):
    global root
    global connected
    global socket_holder
    global server_ip
    global server_name
    global queue
    global spectating
    global t
    global drawing
    status_bar.configure(text="Connecting to "+input_ip+"...")
    root.update()
    try:
        ip,port = map(str,input_ip.split(":"))
        port = int(port)
        socket_holder = socket()
        socket_holder.settimeout(None)
        socket_holder.connect((ip,port))
        server_ip = input_ip
        socket_holder.send(player_name.encode("utf-8"))
        server_name = socket_holder.recv(128).decode("utf-8")
        if server_name == "b":
            disconnectFromServer("b")
            messagebox.showinfo("Disconnected","You are banned from this server.")
        else:
            if server_name == "t":
                disconnectFromServer("b")
                messagebox.showinfo("Disconnected","The server is full.")
            else:
                queue = []
                connected = True
                drawing = True
                t = Thread(target = communicate)
                t.start()
    except:
        connected = False
        messagebox.showerror("Error","Unable to connect to server.")
    refreshConnection()

def communicate():
    global queue
    global this_tick_queue
    global connected
    global last_comm_time
    global superchat
    global time_remaining
    global word
    global drawing
    global image_canvas
    while True:
        if connected == False: break
        new_time = perf_counter()
        if new_time-last_comm_time:
            try:
                while True:
                    if connected == False: break
                    command = socket_holder.recv(128).decode("utf-8")
                    if command!="":
                        if command[0] == "d" and drawing == False:
                            command,x1,y1,x2,y2,color,thickness = map(str,command.split())
                            drawOnCanvas(int(x1),int(y1),int(x2),int(y2),color,int(thickness))
                        if command[0] == "e" and drawing == False:
                            image_canvas.delete("all")
                        if command[0] == "c":
                            command,schat,player,message = map(str,command.split("\t"))
                            printChatMessage(int(schat),player,message)
                        if command[0] == "y":
                            superchat = True
                        if command[0] == "s":
                            command, tag, message = map(str,command.split("\t"))
                            printStatus(message,tag)
                        if command[0] == "o":
                            word_choices = command[1:]
                            pickWord(word_choices)
                            drawing = True
                            superchat = True
                        if command[0] == "m":
                            drawing = False
                            superchat = False
                            image_canvas.delete("all")
                        if command[0] == "t":
                            time_remaining = int(command[1:])
                            label_time.configure(text="Time remaining: "+str(time_remaining)+" seconds")
                        if command[0] == "w" and drawing == False:
                            word = command[1:]
                            label_word.configure(text=word)
                        if command[0] == "p":
                            updatePlayerList(command[1:])
                        if command[0] == "k":
                            disconnectFromServer("k")
                            socket_holder.send(".".encode("utf-8"))
                            messagebox.showinfo("Disconnected","You have been kicked from the server.")
                        if command[0] == "b":
                            disconnectFromServer("b")
                            socket_holder.send(".".encode("utf-8"))
                            messagebox.showinfo("Disconnected","You are banned from this server.")
                        if command[0] == "f":
                            disconnectFromServer("f")
                            socket_holder.send(".".encode("utf-8"))
                            messagebox.showinfo("Disconnected","The server is shutting down.")
                        if command == "a":
                            socket_holder.send(".".encode("utf-8"))
                            break
                    
                    socket_holder.send(".".encode("utf-8"))
                this_tick_queue=queue[:32]
                queue = queue[32:]
                last = "a"
                for i in this_tick_queue:
                    last = i
                    if i == "l":
                        break
                    socket_holder.send(i.encode("utf-8"))
                    confirm = socket_holder.recv(128).decode("utf-8")
                if last != "l":
                    socket_holder.send("a".encode("utf-8"))
                    confirm = socket_holder.recv(128).decode("utf-8")
                else:
                    break
            except:
                if command[0]!="k" and command[0]!="b" and command[0]!="f" and last!="l": 
                    disconnectFromServer("t")
                    messagebox.showerror("Disconnected","Lost connection to server.")
                break
            last_comm_time = new_time


def refreshConnection():
    global connected
    global status_bar
    global button_connection
    global drawing
    global label_word
    global word
    global entry_chat
    global image_canvas
    if connected==False:
        button_connection.configure(image=photoimage_connect,text="Connect",command=connectDialog)
        status_bar.configure(text="Welcome to "+title+"! Use the 'Connect' button to start a game.")
        image_canvas.delete("all")
        label_time.configure(text="")
        entry_chat.delete(0,END)
        entry_chat.configure(state=DISABLED)
        drawing=False
    if connected==True:
        button_connection.configure(image=photoimage_disconnect,text="Disconnect",command=lambda: disconnectFromServer("l"))
        status_bar.configure(text=server_name)
        entry_chat.configure(state=NORMAL)
    label_word.configure(text=word)

def disconnectFromServer(reason):
    global connected
    global word
    global socket_holder
    if reason == "l":
        queue.append("l")
        while len(queue)>0: pass
    socket_holder.close()
    connected=False
    word=""
    refreshConnection()
    list_players.delete(0,"end")
    chat_box.configure(state=NORMAL)
    chat_box.delete(1.0,END)
    chat_box.configure(state=DISABLED)

def likeDrawing():
    global connected
    if connected==True:
        queue.append("g")

def dislikeDrawing():
    global connected
    if connected==True:
        queue.append("b")

def closeClient():
    global connected
    if connected==True:
        disconnectFromServer("l")
    root.destroy()

def loadSettings():
    global player_name
    global saved_servers
    try:
        settings_file = open(os.path.dirname(__file__)+"/settings.txt","r")
        player_name = settings_file.readline()
        player_name = player_name.strip()
        if player_name.isspace() or player_name == "":
            player_name = "Word Sketcher"
            messagebox.showinfo("Hi!","Welcome to "+title+"! You seem to be running the game for the first time. Please set your name!")
            changeName()
        for i in settings_file:
            ip,name = map(str,i.split("\t"))
            name = name.strip()
            saved_servers.append([ip,name])
        settings_file.close()
    except:
        player_name = "Word Sketcher"
        messagebox.showinfo("Hi!","Welcome to "+title+"! You seem to be running the game for the first time. Please set your name!")
        changeName()

def saveSettings():
    global player_name
    global saved_servers
    settings_file = open(os.path.dirname(__file__)+"/settings.txt","w")
    settings_file.write(player_name+"\n")
    for i in saved_servers:
        settings_file.write(i[0]+"\t"+i[1]+"\n")
    settings_file.close()


root=Tk()
root.title(title+" "+version+" by "+author)
root.minsize(window_size_x,window_size_y)
root.maxsize(window_size_x,window_size_y)
root.geometry("+{}+{}".format(int(root.winfo_screenwidth()/2-window_size_x/2),int(root.winfo_screenheight()/2-window_size_y/2-20)))
root.protocol('WM_DELETE_WINDOW', closeClient)

main_menu=Menu(root)
game_menu=Menu(main_menu)
game_menu.add_command(label="Add server to favorites",command=addServerToFavorites)
game_menu.add_command(label="Change name",command=changeName)
game_menu.add_separator()
game_menu.add_command(label="About",command=about)
game_menu.add_command(label="Exit",command=closeClient)
main_menu.add_cascade(label="Game",menu=game_menu)

root.config(menu=main_menu)

label_time=Label(text="Time remaining: "+str(time_remaining)+" seconds",font=(font,font_size,"bold"))
label_time.place(x=4,y=0)

label_player=Label(text="Players:",font=(font,font_size))
label_player.place(x=4,y=20)
list_players=Listbox(width=34,height=18,font=(font,font_size_list),bd=2)
list_players.place(x=4,y=40)

label_chat=Label(text="Chat:",font=(font,font_size))
label_chat.place(x=4,y=334)
chat_box=Text(state=DISABLED,width=34,height=14,font=(font,font_size_list),bd=2,wrap=WORD)
chat_box.place(x=4,y=354)
chat_box.tag_config("tag_drawing",font=(font,font_size_list,"bold"),foreground="#808000",background="#FFFFA0")
chat_box.tag_config("tag_sender",font=(font,font_size_list,"bold"),foreground="#000000",background="#E0E0E0")
chat_box.tag_config("tag_guess",font=(font,font_size_list,"bold"),foreground="#000000",background="#00FF00")
chat_box.tag_config("tag_close",font=(font,font_size_list,"bold"),foreground="#000000",background="#FFFF00")
chat_box.tag_config("tag_super",font=(font,font_size_list,"bold"),foreground="#008000",background="#00FF00")
chat_box.tag_config("tag_name_change",font=(font,font_size_list,"bold"),foreground="#000080",background="#A0A0FF")
chat_box.tag_config("tag_like",font=(font,font_size_list,"bold"),foreground="#008000",background="#A0FFA0")
chat_box.tag_config("tag_dislike",font=(font,font_size_list,"bold"),foreground="#800000",background="#FFA0A0")
chat_box.tag_config("tag_switch",font=(font,font_size_list,"bold"),foreground="#800080",background="#FFA0FF")
chat_box.tag_config("tag_join_leave",font=(font,font_size_list,"bold"),foreground="#FFFFFF",background="#A0A0A0")
entry_chat=Entry(width=34,font=(font,font_size_list),bd=2)
entry_chat.bind("<Return>",sendChatMessage)
entry_chat.place(x=4,y=569)

label_word=Label(text=word,font=(font,font_size,"bold"),justify=CENTER,anchor=N,width=50)
label_word.place(x=378,y=0)
image_canvas=Canvas(width=640,height=480,relief=SUNKEN,bg="white",bd=2, cursor=cursor_pen)
image_canvas.place(x=248,y=20)
image_canvas.bind("<Button-1>",reset)
image_canvas.bind("<B1-Motion>",paint)

photoimage_pen=PhotoImage(file = os.path.dirname(__file__)+"/icons/pen.png")
button_pen=Button(image=photoimage_pen,command=toolPen,relief=SUNKEN)
button_pen.place(x=250,y=510)

photoimage_eraser=PhotoImage(file = os.path.dirname(__file__)+"/icons/eraser.png")
button_eraser=Button(image=photoimage_eraser,command=toolEraser)
button_eraser.place(x=290,y=510)

photoimage_clear=PhotoImage(file = os.path.dirname(__file__)+"/icons/trash.png")
button_clear=Button(image=photoimage_clear,command=clearCanvas)
button_clear.place(x=330,y=510)

photoimage_like=PhotoImage(file = os.path.dirname(__file__)+"/icons/like.png")
button_like=Button(image=photoimage_like,compound=LEFT,text="Like",font=(font,font_size),width=75,anchor=NW,command=likeDrawing)
button_like.place(x=725,y=510)

photoimage_dislike=PhotoImage(file = os.path.dirname(__file__)+"/icons/dislike.png")
button_dislike=Button(image=photoimage_dislike,compound=LEFT,text="Dislike",font=(font,font_size),width=75,anchor=NW,command=dislikeDrawing)
button_dislike.place(x=810,y=510)

photoimage_connect=PhotoImage(file = os.path.dirname(__file__)+"/icons/connect.png")
photoimage_disconnect=PhotoImage(file = os.path.dirname(__file__)+"/icons/disconnect.png")
button_connection=Button(image=photoimage_connect,compound=LEFT,text="Connect",font=(font,font_size),width=160,anchor=NW,command=connectDialog)
button_connection.place(x=725,y=550)

photoimage_logo=PhotoImage(file = os.path.dirname(__file__)+"/icons/logo.png")

thickness_label=Label(font=(font,font_size))
thickness_label.place(x=248,y=550)

preview_canvas=Canvas(width=76,height=76,relief=SUNKEN,bg="white",bd=2)
preview_canvas.place(x=373,y=508)

status_bar=Label(text=server_name,relief=SUNKEN,anchor=W,bd=1)
status_bar.pack(side=BOTTOM,fill=X)

circle_pen=preview_canvas.create_oval(42-thickness,42-thickness,42+thickness,42+thickness,fill=color,outline="")
thickness_slider=Scale(orient=HORIZONTAL,length=120,from_=1,to=20,resolution=1,showvalue=0,variable=thickness,command=refreshPreviewCanvas)
thickness_slider.set(thickness)
thickness_slider.place(x=248,y=570)

# TODO: TIDY THIS UP!
button_color_00=Button(relief=FLAT,bg="#FFFFFF",command=lambda:changeColor("#FFFFFF"))
button_color_00.place(x=460,y=510,width=20,height=20)
button_color_01=Button(relief=FLAT,bg="#C0C0C0",command=lambda:changeColor("#C0C0C0"))
button_color_01.place(x=460,y=530,width=20,height=20)
button_color_02=Button(relief=FLAT,bg="#808080",command=lambda:changeColor("#808080"))
button_color_02.place(x=460,y=550,width=20,height=20)
button_color_03=Button(relief=FLAT,bg="#000000",command=lambda:changeColor("#000000"))
button_color_03.place(x=460,y=570,width=20,height=20)
button_color_10=Button(relief=FLAT,bg="#FFBFBF",command=lambda:changeColor("#FFBFBF"))
button_color_10.place(x=480,y=510,width=20,height=20)
button_color_11=Button(relief=FLAT,bg="#FF0000",command=lambda:changeColor("#FF0000"))
button_color_11.place(x=480,y=530,width=20,height=20)
button_color_12=Button(relief=FLAT,bg="#BF0000",command=lambda:changeColor("#BF0000"))
button_color_12.place(x=480,y=550,width=20,height=20)
button_color_13=Button(relief=FLAT,bg="#800000",command=lambda:changeColor("#800000"))
button_color_13.place(x=480,y=570,width=20,height=20)
button_color_20=Button(relief=FLAT,bg="#FFDFBF",command=lambda:changeColor("#FFDFBF"))
button_color_20.place(x=500,y=510,width=20,height=20)
button_color_21=Button(relief=FLAT,bg="#FF8000",command=lambda:changeColor("#FF8000"))
button_color_21.place(x=500,y=530,width=20,height=20)
button_color_22=Button(relief=FLAT,bg="#BF6000",command=lambda:changeColor("#BF6000"))
button_color_22.place(x=500,y=550,width=20,height=20)
button_color_23=Button(relief=FLAT,bg="#804000",command=lambda:changeColor("#804000"))
button_color_23.place(x=500,y=570,width=20,height=20)
button_color_30=Button(relief=FLAT,bg="#FFFFBF",command=lambda:changeColor("#FFFFBF"))
button_color_30.place(x=520,y=510,width=20,height=20)
button_color_31=Button(relief=FLAT,bg="#FFFF00",command=lambda:changeColor("#FFFF00"))
button_color_31.place(x=520,y=530,width=20,height=20)
button_color_32=Button(relief=FLAT,bg="#BFBF00",command=lambda:changeColor("#BFBF00"))
button_color_32.place(x=520,y=550,width=20,height=20)
button_color_33=Button(relief=FLAT,bg="#808000",command=lambda:changeColor("#808000"))
button_color_33.place(x=520,y=570,width=20,height=20)
button_color_40=Button(relief=FLAT,bg="#DFFFBF",command=lambda:changeColor("#DFFFBF"))
button_color_40.place(x=540,y=510,width=20,height=20)
button_color_41=Button(relief=FLAT,bg="#80FF00",command=lambda:changeColor("#80FF00"))
button_color_41.place(x=540,y=530,width=20,height=20)
button_color_42=Button(relief=FLAT,bg="#60BF00",command=lambda:changeColor("#60BF00"))
button_color_42.place(x=540,y=550,width=20,height=20)
button_color_43=Button(relief=FLAT,bg="#408000",command=lambda:changeColor("#408000"))
button_color_43.place(x=540,y=570,width=20,height=20)
button_color_50=Button(relief=FLAT,bg="#BFFFBF",command=lambda:changeColor("#BFFFBF"))
button_color_50.place(x=560,y=510,width=20,height=20)
button_color_51=Button(relief=FLAT,bg="#00FF00",command=lambda:changeColor("#00FF00"))
button_color_51.place(x=560,y=530,width=20,height=20)
button_color_52=Button(relief=FLAT,bg="#00BF00",command=lambda:changeColor("#00BF00"))
button_color_52.place(x=560,y=550,width=20,height=20)
button_color_53=Button(relief=FLAT,bg="#008000",command=lambda:changeColor("#008000"))
button_color_53.place(x=560,y=570,width=20,height=20)
button_color_60=Button(relief=FLAT,bg="#BFFFDF",command=lambda:changeColor("#BFFFDF"))
button_color_60.place(x=580,y=510,width=20,height=20)
button_color_61=Button(relief=FLAT,bg="#00FF80",command=lambda:changeColor("#00FF80"))
button_color_61.place(x=580,y=530,width=20,height=20)
button_color_62=Button(relief=FLAT,bg="#00BF60",command=lambda:changeColor("#00BF60"))
button_color_62.place(x=580,y=550,width=20,height=20)
button_color_63=Button(relief=FLAT,bg="#008040",command=lambda:changeColor("#008040"))
button_color_63.place(x=580,y=570,width=20,height=20)
button_color_70=Button(relief=FLAT,bg="#BFFFFF",command=lambda:changeColor("#BFFFFF"))
button_color_70.place(x=600,y=510,width=20,height=20)
button_color_71=Button(relief=FLAT,bg="#00FFFF",command=lambda:changeColor("#00FFFF"))
button_color_71.place(x=600,y=530,width=20,height=20)
button_color_72=Button(relief=FLAT,bg="#00BFBF",command=lambda:changeColor("#00BFBF"))
button_color_72.place(x=600,y=550,width=20,height=20)
button_color_73=Button(relief=FLAT,bg="#008080",command=lambda:changeColor("#008080"))
button_color_73.place(x=600,y=570,width=20,height=20)
button_color_80=Button(relief=FLAT,bg="#BFDFFF",command=lambda:changeColor("#BFDFFF"))
button_color_80.place(x=620,y=510,width=20,height=20)
button_color_81=Button(relief=FLAT,bg="#0080FF",command=lambda:changeColor("#0080FF"))
button_color_81.place(x=620,y=530,width=20,height=20)
button_color_82=Button(relief=FLAT,bg="#0060BF",command=lambda:changeColor("#0060BF"))
button_color_82.place(x=620,y=550,width=20,height=20)
button_color_83=Button(relief=FLAT,bg="#004080",command=lambda:changeColor("#004080"))
button_color_83.place(x=620,y=570,width=20,height=20)
button_color_90=Button(relief=FLAT,bg="#BFBFFF",command=lambda:changeColor("#BFBFFF"))
button_color_90.place(x=640,y=510,width=20,height=20)
button_color_91=Button(relief=FLAT,bg="#0000FF",command=lambda:changeColor("#0000FF"))
button_color_91.place(x=640,y=530,width=20,height=20)
button_color_92=Button(relief=FLAT,bg="#0000BF",command=lambda:changeColor("#0000BF"))
button_color_92.place(x=640,y=550,width=20,height=20)
button_color_93=Button(relief=FLAT,bg="#000080",command=lambda:changeColor("#000080"))
button_color_93.place(x=640,y=570,width=20,height=20)
button_color_a0=Button(relief=FLAT,bg="#DFBFFF",command=lambda:changeColor("#DFBFFF"))
button_color_a0.place(x=660,y=510,width=20,height=20)
button_color_a1=Button(relief=FLAT,bg="#8000FF",command=lambda:changeColor("#8000FF"))
button_color_a1.place(x=660,y=530,width=20,height=20)
button_color_a2=Button(relief=FLAT,bg="#6000BF",command=lambda:changeColor("#6000BF"))
button_color_a2.place(x=660,y=550,width=20,height=20)
button_color_a3=Button(relief=FLAT,bg="#400080",command=lambda:changeColor("#400080"))
button_color_a3.place(x=660,y=570,width=20,height=20)
button_color_b0=Button(relief=FLAT,bg="#FFBFFF",command=lambda:changeColor("#FFBFFF"))
button_color_b0.place(x=680,y=510,width=20,height=20)
button_color_b1=Button(relief=FLAT,bg="#FF00FF",command=lambda:changeColor("#FF00FF"))
button_color_b1.place(x=680,y=530,width=20,height=20)
button_color_b2=Button(relief=FLAT,bg="#BF00BF",command=lambda:changeColor("#BF00BF"))
button_color_b2.place(x=680,y=550,width=20,height=20)
button_color_b3=Button(relief=FLAT,bg="#800080",command=lambda:changeColor("#800080"))
button_color_b3.place(x=680,y=570,width=20,height=20)
button_color_c0=Button(relief=FLAT,bg="#FFBFDF",command=lambda:changeColor("#FFBFDF"))
button_color_c0.place(x=700,y=510,width=20,height=20)
button_color_c1=Button(relief=FLAT,bg="#FF0080",command=lambda:changeColor("#FF0080"))
button_color_c1.place(x=700,y=530,width=20,height=20)
button_color_c2=Button(relief=FLAT,bg="#BF0060",command=lambda:changeColor("#BF0060"))
button_color_c2.place(x=700,y=550,width=20,height=20)
button_color_c3=Button(relief=FLAT,bg="#800040",command=lambda:changeColor("#800040"))
button_color_c3.place(x=700,y=570,width=20,height=20)

refreshConnection()
loadSettings()

mainloop()
