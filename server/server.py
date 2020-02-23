from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from socket import *
from threading import *
from time import *
from random import *
from math import *
import os

def printStatus(status_message,tag):
    chat_box.config(state=NORMAL)
    chat_box.insert(END,status_message+"\n",tag)
    chat_box.config(state=DISABLED)
    chat_box.see("end")

def changeName():
    name_change_dialog_size_x=350
    name_change_dialog_size_y=80
    name_change_dialog=Tk()
    name_change_dialog.title("Change server name")
    name_change_dialog.minsize(name_change_dialog_size_x,name_change_dialog_size_y)
    name_change_dialog.maxsize(name_change_dialog_size_x,name_change_dialog_size_y)
    name_change_dialog.geometry("+{}+{}".format(int(name_change_dialog.winfo_screenwidth()/2-name_change_dialog_size_x/2),int(name_change_dialog.winfo_screenheight()/2-name_change_dialog_size_y/2)))
    name_change_dialog.focus_force()

    player_name_label=Label(name_change_dialog,text="New server name:",font=(font,font_size))
    player_name_label.place(x=10,y=10)

    name_length_label=Label(name_change_dialog,text="Max. length is 256 characters.",font=(font,font_size))
    name_length_label.place(x=10,y=42)
    
    player_name_entry=Entry(name_change_dialog,width=29,bd=2,font=(font,font_size))
    player_name_entry.place(x=121,y=10)
    
    player_name_entry.focus_force()

    ok_button=Button(name_change_dialog,text="OK",width=10,font=(font,font_size))
    ok_button.place(x=240,y=40)

def changeWordList():
    global server
    filename = filedialog.askopenfilename(title = "Open a word list file",filetypes = (("Text files","*.txt"),("All files","*.*")))
    server.loadWordList(filename)
    messagebox.showinfo("Success","New word list loaded.")

def kickClient():
    global list_clients
    try:
        client_index = list_clients.curselection()[0]
    except:
        messagebox.showerror("Error","Please select a client.")
    clientlist[client_index].disconnect("k")

def banClient():
    global list_clients
    try:
        client_index = list_clients.curselection()[0]
    except:
        messagebox.showerror("Error","Please select a client.")
    client_ip = clientlist[client_index].address
    banlist.append(client_ip)
    clientlist[client_index].disconnect("b")
    ban_file = open(os.path.dirname(__file__)+"/banned.txt","a")
    ban_file.write(client_ip+"\n")
    ban_file.close()
    
def refreshBanList():
    global banlist
    banlist = []
    ban_file = open(os.path.dirname(__file__)+"/banned.txt","r")
    for i in ban_file:
        banlist.append(i.strip())
    ban_file.close()
    messagebox.showinfo("Refreshed","The ban list has been refreshed.")

def loadSettings():
    global server_name
    global server_port
    global time_per_round
    global maxclients
    try:
        settings_file = open(os.path.dirname(__file__)+"/settings.txt","r")
        server_name = settings_file.readline()
        server_name = server_name.strip()
        server_port = settings_file.readline()
        server_port = int(server_port.strip())
        time_per_round = settings_file.readline()
        time_per_round = int(time_per_round.strip())
        maxclients = settings_file.readline()
        maxclients = int(maxclients.strip())
        settings_file.close()
    except:
        server_name = "SketchPy Server"
        server_port = 27952
        time_per_round = 180
        maxclients = 20
        recreate = messagebox.askyesno("Error","Invalid or missing settings.txt file. Do you want to create a new one with default settings?")
        if recreate:
            settings_file = open(os.path.dirname(__file__)+"/settings.txt","w")
            settings_file.write(server_name+"\n")
            settings_file.write(str(server_port)+"\n")
            settings_file.write(str(time_per_round)+"\n")
            settings_file.write(str(maxclients)+"\n")
            settings_file.close()
            messagebox.showinfo("Created","A new settings.txt file has been created.")

def runGame():
    global clientlist
    global word
    global round_over
    global client_draw_queue
    while True:
        game_running = True
        if len(clientlist)<2:
            break
        client_draw_queue = clientlist
        for i in client_draw_queue:
            disconnected = False
            if len(clientlist)<2:
                break
            word = ""
            sendToAll("m")
            sendToAll("s\ttag_drawing\t"+i.name+" is drawing!")
            printStatus(i.name+" is drawing!","tag_drawing")
            try:
                words = sample(wordlist,3)
                i.drawing = True
                i.superchat = True
                i.queue.append("o"+words[0]+"\t"+words[1]+"\t"+words[2])
                while word=="": pass
                if word=="0": word=words[0]
                if word=="1": word=words[1]
                if word=="2": word=words[2]
                round_over = False
                sendToAll("s\ttag_drawing\t"+i.name+" has chosen a word.")
                printStatus(i.name+" has chosen a word.","tag_drawing")
                sendToAll("e")
                t_time=Thread(target=keepTime)
                t_time.start()
                while True:
                    try:
                        i.comm.settimeout(None)
                    except:
                        disconnected = True
                        break
                    all_guessed = True
                    for j in clientlist:
                        if j.superchat == False:
                            all_guessed = False
                            break
                    if all_guessed or time_remaining == 0:
                        break
                sendToAll("s\ttag_drawing\tRound over!")
                printStatus("Round over!","tag_drawing")
                round_over = True
                if disconnected: break
                score_sum = 0
                for j in clientlist:
                    score_sum+=j.score+1
                    j.drawing = False
                    j.superchat = False
                i.score+=int(ceil(score_sum/len(clientlist)))
                i.updateClientList()
            except:
                pass
    game_running = False
    sendToAll("s\ttag_dislike\tNot enough players to continue the game. Waiting for more players.")
    printStatus("Not enough players to continue the game. Waiting for more players.","tag_dislike")
    #messagebox.showerror("Not enough players","The game has stopped because there is not enough players.")

def keepTime():
    global time_per_round
    global time_remaining
    global round_over
    global word
    global revealed
    revealed = ""
    for i in word:
        if i.isalnum():
            revealed+="*"
        else:
            revealed+=i
    sendToAll("w"+revealed)
    reveal_time = time_per_round * 1.3 // len(word)
    last_state=time_per_round
    time_remaining = time_per_round
    start_time = process_time()
    while time_remaining>=0:
        current_time = time_per_round - (process_time() - start_time)
        time_remaining = trunc(current_time)
        if time_remaining != last_state:
            last_state = time_remaining
            sendToAll("t"+str(time_remaining))
            if (time_per_round - time_remaining) % reveal_time == 0:
                unrevealed=[]
                for i in range(len(word)):
                    if revealed[i]=="*":
                        unrevealed.append(i)
                reveal_index = choice(unrevealed)
                revealed = list(revealed)
                revealed[reveal_index] = word[reveal_index]
                revealed = "".join(revealed)
                sendToAll("w"+revealed)
        if round_over:
            round_over = False
            if time_remaining < 0: time_remaining = 0
            break


class Server():
    def __init__(self):
        global server_name
        global draw_queue
        global clientlist
        global word
        global revealed
        global maxclients
        global server_port
        global time_per_round
        global wordlist
        self.hostname = gethostname()
        self.local_ip = gethostbyname(self.hostname)
        self.socket = socket()
        self.socket.bind((self.hostname,server_port))
        self.socket.listen(maxclients)
        word = ""
        revealed = ""
        draw_queue = []
        clientlist = []
        wordlist = []
        self.loadWordList(os.path.dirname(__file__)+"/wordlists/default.txt")
        
    def start(self):
        while True:
            c,a = self.socket.accept()
            printStatus("A client from "+a[0]+" has connected.","no_tag")
            if a[0] in banlist:
                c.send("b".encode("utf-8"))
                c.close()
                printStatus("Rejected connection because they are banned.","no_tag")
            else:
                if len(clientlist)>=maxclients:
                    c.send("t".encode("utf-8"))
                    c.close()
                    printStatus("Rejected connection because the server is full.","no_tag")
                else:
                    t_comm = Thread(target = self.runClient, args = (c,a[0]))
                    t_comm.start()

    def runClient(self,comm,adress):
        client = Client(comm,adress)
        last_comm_time = perf_counter()
        while True:
            new_time = perf_counter()
            if new_time-last_comm_time>=0:
                try:
                    client.communicate()
                except:
                    break
                last_comm_time = new_time
    
    def loadWordList(self,filename):
        global wordlist
        wordfile = open(filename,"r")
        words = wordfile.readlines()
        for i in words:
            word = i.strip()
            if word != "": wordlist.append(word)
    
    def startGame(self):
        global clientlist
        global game_running
        if len(clientlist)>1 and game_running == False:
            sendToAll("s\ttag_drawing\tThe game has started.")
            t_game = Thread(target = runGame)
            t_game.start()
        else:
            if game_running:
                messagebox.showerror("Error","A game is already in progress.")
            else:
                messagebox.showerror("Error","At least 2 players are required to start the game.")

    def shutDown(self):
        global root
        global clientlist
        printStatus("Shutting down server...","no_tag")
        for i in clientlist:
            i.disconnect("f")
        root.destroy()

class Client(Server):
    def __init__(self,comm,address):
        global server_name
        global draw_queue
        global clientlist
        global word
        global revealed
        self.comm = comm
        self.address = address
        self.id = 1
        self.queue = draw_queue
        self.drawing = False
        self.superchat = False
        self.rated = False
        self.name = self.comm.recv(128).decode("utf-8")
        self.comm.send(server_name.encode("utf-8"))
        self.score = 0
        self.updateClientList()
        sendToAll("s\ttag_join_leave\t"+self.name+" has joined the game.")
        printStatus(self.name+" has joined the game.","tag_join_leave")
        clientlist.append(self)
        self.updateClientList()
        
    def updateClientList(self):
        global clientlist
        global list_clients
        global label_clients
        msg = "p"
        sorted_clients = clientlist
        sorted_clients.sort(key = lambda x:x.score, reverse=True)
        list_clients.delete(0,"end")
        for i in range(len(sorted_clients)):
            text = ""
            text+="#"+str(i+1)+" "+sorted_clients[i].name+" ("+str(sorted_clients[i].score)+")"
            if sorted_clients[i].drawing == True:
                text+=" (drawing)"
            list_clients.insert(i,text)
            msg+=text+"\t"
        label_clients.config(text = "Clients: "+str(len(clientlist))+" / "+str(maxclients),font = (font,font_size))
        sendToAll(msg)
    
    def communicate(self):
        global draw_queue
        global word
        this_tick_queue = self.queue
        self.queue = []
        for i in this_tick_queue:
            self.comm.send(i.encode("utf-8"))
            confirm = self.comm.recv(128).decode("utf-8")
        self.comm.send("a".encode("utf-8"))
        confirm = self.comm.recv(128).decode("utf-8")
        while True:
            try:
                command = self.comm.recv(128).decode("utf-8")
                command_id=command[0]
                if (command_id=="d"):
                    sendToAll(command)
                    draw_queue.append(command)
                
                if (command_id=="e") and self.drawing == True:
                    sendToAll("e")
                    draw_queue = []

                if command_id=="c":
                    message = command[1:]
                    message = message.strip()
                    if message.isspace() == False and message != "":
                        if self.superchat == False:
                            check = self.checkWord(message)
                            if check == 0:
                                sendToAll("c\t0\t"+self.name+"\t"+message)
                            if check == 1:
                                sendToAll("s\ttag_guess\t"+self.name+" has guessed the word!")
                                printStatus(self.name+" has guessed the word!","tag_guess")
                                self.superchat = True
                                self.queue.append("y")
                                self.score+=time_remaining
                            if check == 2:
                                sendToAll("c\t0\t"+self.name+"\t"+message)
                                self.queue.append("s\ttag_close\t'"+message+"' is close...")
                        else:
                            sendToAll("c\t1\t"+self.name+"\t"+message)
            
                if command_id=="n":
                    oldname = self.name
                    com,self.name = map(str,command.split("\t"))
                    sendToAll("s\ttag_name_change\t'"+oldname+"' changed their name to '"+self.name+"'")
                    printStatus("'"+oldname+"' changed their name to '"+self.name+"'","tag_name_change")
                    self.updateClientList()

                if command_id=="g":
                    if not self.rated:
                        sendToAll("s\ttag_like\t"+self.name+" likes this drawing!")
                        printStatus(self.name+" likes this drawing!","tag_like")
                        self.rated = True

                if command_id=="b":
                    if not self.rated:
                        sendToAll("s\ttag_dislike\t"+self.name+" dislikes this drawing!")
                        printStatus(self.name+" dislikes this drawing!","tag_dislike")
                        self.rated = True

                if command_id=="r":
                    self.queue.append("n\t"+Server.name)

                if command_id=="a":
                    self.comm.send(".".encode("utf-8"))
                    break
                if command_id=="x" and self.drawing==True:
                    word=command[1:]
                if command_id=="l":
                    self.comm.send(".".encode("utf-8"))
                    self.disconnect("l")
                self.comm.send(".".encode("utf-8"))

                
            except:
                self.disconnect("l")

    def disconnect(self,reason):
        if reason != "l":
            self.queue.append(reason)
            try:
                while len(self.queue)>0:
                    self.comm.settimeout(None)
                    pass
                self.comm.close()
            except:
                pass
        clientlist.remove(self)
        try:
            client_draw_queue.remove(self)
        except:
            pass
        if reason == "l":
            sendToAll("s\ttag_join_leave\t"+self.name+" has left the game.")
            printStatus(self.name+" has left the game.","tag_join_leave")
        if reason == "k":
            sendToAll("s\ttag_join_leave\t"+self.name+" has been kicked from the game.")
            printStatus(self.name+" has been kicked from the game.","tag_join_leave")
        if reason == "b":
            sendToAll("s\ttag_join_leave\t"+self.name+" has been banned.")
            printStatus(self.name+" has been banned.","tag_join_leave")
        if reason != "f": self.updateClientList()
                
    def checkWord(self,guess):
        global word
        guess=guess.lower()
        wordt=word.lower()
        if guess == wordt:
            self.superchat = True
            return 1
        else:
            if len(word)-len(guess) == 1 or len(word)-len(guess) == -1 or len(word)==len(guess):
                difference=0
                if len(wordt) < len(guess): wordt+=" "      # adding a space for words one letter longer
                if len(wordt) > len(guess): guess+=" "      # adding a space for words one letter shorter
                for i in range(min(len(wordt),len(guess))):
                    if wordt[i]!=guess[i]: difference+=1
                    if difference > 1: return 0
                if difference == 1:
                    return 2
            return 0

def sendToAll(command):
    for i in range(len(clientlist)):
        clientlist[i].queue.append(command)

banlist = []
ban_file = open(os.path.dirname(__file__)+"/banned.txt","r")
for i in ban_file:
    banlist.append(i.strip())
ban_file.close()

window_size_x = 498
window_size_y = 427
font="Arial"
font_size=10
font_size_list=9
title="SketchPy"
version="v1.0"
game_running = False

root = Tk()
root.minsize(window_size_x,window_size_y)
root.maxsize(window_size_x,window_size_y)
root.title(title+" "+version+" server")

loadSettings()

server = Server()
t = Thread(target=server.start)
t.start()
root.protocol('WM_DELETE_WINDOW', server.shutDown)

main_menu=Menu(root)
game_menu=Menu(main_menu)
game_menu.add_command(label="Start game",command = server.startGame)
game_menu.add_separator()
game_menu.add_command(label="Change word list",command = changeWordList)
game_menu.add_command(label="Refresh ban list",command = refreshBanList)
game_menu.add_separator()
game_menu.add_command(label="Shut down",command = server.shutDown)
main_menu.add_cascade(label="Server",menu=game_menu)
root.config(menu=main_menu)

label_server_name = Label(text = "Server name: "+server_name,font = (font,font_size))
label_server_name.place(x=4,y=4)

label_server_ip = Label(text = "Local IP: "+server.local_ip+":"+str(server_port),font = (font,font_size))
label_server_ip.place(x=4,y=24)

label_clients = Label(text = "Clients: "+str(len(clientlist))+" / "+str(maxclients),font = (font,font_size))
label_clients.place(x=4,y=44)

label_client=Label(text="Clients:",font=(font,font_size))
label_client.place(x=4,y=77)
list_clients=Listbox(width=34,height=18,font=(font,font_size_list),bd=2)
list_clients.place(x=4,y=97)

button_kick = Button(text = "Kick client",width = 13,font=(font,font_size),command = kickClient)
button_kick.place(x=10,y=392)
button_ban = Button(text = "Ban client",width = 13,font=(font,font_size),command = banClient)
button_ban.place(x=125,y=392)

label_chat=Label(text="Status messages:",font=(font,font_size))
label_chat.place(x=250,y=4)
chat_box=Text(state=DISABLED,width=34,height=26,font=(font,font_size_list),bd=2,wrap=WORD)
chat_box.place(x=250,y=24)
chat_box.tag_config("tag_drawing",font=(font,font_size_list,"bold"),foreground="#808000",background="#FFFFA0")
chat_box.tag_config("tag_sender",font=(font,font_size_list,"bold"),foreground="#000000",background="#E0E0E0")
chat_box.tag_config("tag_guess",font=(font,font_size_list,"bold"),foreground="#000000",background="#00FF00")
chat_box.tag_config("tag_close",font=(font,font_size_list,"bold"),foreground="#000000",background="#FFFF00")
chat_box.tag_config("tag_super",font=(font,font_size_list,"bold"),foreground="#008000",background="#00FF00")
chat_box.tag_config("tag_name_change",font=(font,font_size_list,"bold"),foreground="#000080",background="#A0A0FF")
chat_box.tag_config("tag_like",font=(font,font_size_list,"bold"),foreground="#008000",background="#A0FFA0")
chat_box.tag_config("tag_dislike",font=(font,font_size_list,"bold"),foreground="#800000",background="#FFA0A0")
chat_box.tag_config("tag_switch",font=(font,font_size_list,"bold"),foreground="#800080",background="#FFA0FF")
chat_box.tag_config("tag_join_leave",font=(font,font_size_list,"bold"),foreground="#FFFFFF",background="#808080")

mainloop()


        
