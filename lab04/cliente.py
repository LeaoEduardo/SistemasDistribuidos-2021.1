import socket
import json
from pprint import pprint
from random import randint
from tkinter import *
import tkinter.messagebox
import os
import select

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

import threading
from PIL import Image, ImageTk

from user import User
from variables import SERVER_HOST, SERVER_PORT, PRIMARY_FONT, SECONDARY_FONT, TERTIARY_FONT

server_sock = socket.socket()

server_sock.connect((SERVER_HOST, SERVER_PORT)) 

def send_message_to_server(user, command, type="request", message=None, server_sock=server_sock):

    if message is None:
        message = user.name

    msg_dict = {
        "type" : type,
        "source": [SERVER_HOST, user.address[1]],
        "destiny" : (SERVER_HOST, SERVER_PORT),
        "command" : command,
        "message" : message
    }
    msg = json.dumps(msg_dict)

    server_sock.sendall(bytes(msg, encoding='utf-8'))

def receive_server_response():
    raw_answer = server_sock.recv(1024)
    answer = json.loads(str(raw_answer,encoding='utf-8'))
    pprint(answer)
    return answer

class GUI:

    def __init__(self):

        self.threads = []

        self.window = Tk()
        self.window.withdraw()

        self.configure_login()

        self.window.protocol("WM_DELETE_WINDOW", lambda: self.quit(self.window))
        self.login.protocol("WM_DELETE_WINDOW", lambda: self.quit(self.login))

        self.window.mainloop()

    def configure_login(self):
        self.login = Toplevel()
        self.login.resizable(width=True,height=True)
        self.login.configure(width=640,height=560)
        self.label = Label(self.login, text="What's your name?", font= PRIMARY_FONT)
        self.label.place(relheight=0.20,
                        relx=0.32,
                        rely=0.2)
        # campo de input para nome de usuário
        self.user_name = Entry(self.login, 
                             font = TERTIARY_FONT)
          
        self.user_name.place(relwidth = 0.35, 
                             relheight = 0.07,
                             relx = 0.3,

                             rely = 0.35)
          
        # coloca o foco no campo de input
        self.user_name.focus()
          
        # criação de botão de "Entrar", que chama a função 'loginToChat'
        self.enter = Button(self.login,
                         text = "Enter", 
                         font = SECONDARY_FONT, 
                         command = lambda: self.create_user(self.user_name.get()))
          
        self.enter.place(relx = 0.4,
                      rely = 0.55)

    def quit(self, window):
        window.destroy()
        if len(self.threads) != 0:
            for thread in self.threads:
                thread.join(timeout=1)
        os._exit(0)

    def receive_server_update(self):

        address = (SERVER_HOST,SERVER_PORT)
        
        while True:
            message = receive_server_response()
            if message["type"] == "request":
                if message["command"] == "update":
                    self.available_users = message["users"]
                    self.usernames = [ user["user"] for user in self.available_users if user["user"] != self.user.name]
                    try:
                        self.update_users_box()
                    except AttributeError:
                        print("Users box not yet created")
                    send_message_to_server(user=self.user, command='update',type="response", message="SUCCESS")
            

    def handle_peer_requests(self, clisock, address):
        while True:
            try:
                data = clisock.recv(1024) 
            except ConnectionResetError:
                pass
            if not data: 
                clisock.close()
                return
            else: 
                msg = json.loads(data) 
                if msg["type"] == "p2p":
                    if msg["command"] == 'send':
                        self.display_msg(msg["message"])

    def receive_connections(self):
        while True:
            readList, _, _ = select.select(self.user.entries, [], [])
            for ready in readList:
                if ready == self.user.sock: 
                    clisock, address = self.user.accept_connection()
                    client = threading.Thread(target=self.handle_peer_requests, args=(clisock,address))
                    client.start()
                    self.user.clients.append(client)

    def create_user(self, user_name):
        self.user = User(name=user_name, port=randint(6000,10000), server_sock=server_sock)
        send_message_to_server(self.user, 'open')
        answer = receive_server_response()
        if answer["message"] != "SUCCESS":
            tkinter.messagebox.showerror('Erro', answer['message'])
            return
        self.status = "online"
        self.available_users = answer["users"]
        self.usernames = [ user["user"] for user in self.available_users if user["user"] != self.user.name]
        self.login.withdraw()
        self.user.init_server()
        self.chat_thread = threading.Thread(target=self.chat)
        self.chat_thread.start()
        self.user_thread = threading.Thread(target=self.receive_connections)
        self.user_thread.start()
        self.server_thread = threading.Thread(target=self.receive_server_update)
        self.server_thread.start()
        self.threads = [self.server_thread, self.user_thread, self.chat_thread]

    #janela de bate papo
    def chat(self):
        self.window.deiconify()
        self.window.title("Chat")
        self.window.resizable(width=True,height=True)
        self.window.configure(width=640,height=560)
        
        self.welcome = Label(self.window, text=f"Welcome, {self.user.name}", font=PRIMARY_FONT)
        self.welcome.place(relwidth=1, rely=0.01)

        self.separator = Label(self.window, background='black')
        self.separator.place(relwidth=1, rely=0.06, relheight=0.001)

        self.online_button = ImageTk.PhotoImage((Image.open(f"{ROOT_DIR}/images/on.png")).resize((50,20)))
        self.offline_button = ImageTk.PhotoImage((Image.open(f"{ROOT_DIR}/images/off.png")).resize((50,20)))    

        self.view_messages = Text(self.window,
                             width = 19, 
                             height = 2,
                             font = TERTIARY_FONT, 
                             bg = "white",
                             fg = "black",
                             padx = 5,
                             pady = 5)
          
        self.view_messages.place(relheight = 0.7,
                            relwidth = 0.7, 
                            rely = 0.08,
                            relx = 0.01)

        self.view_messages.config(cursor = "arrow")

        self.users_box = Listbox(self.window,
                               width = 15, 
                               height = 10, 
                               bg = "white",
                               fg = "black",
                               activestyle = 'dotbox', 
                               font = SECONDARY_FONT)
        
        self.users_box.place(relheight = 0.7,
                           relwidth = 0.25,
                           relx = 0.74,
                           rely = 0.08)

        self.status_msg = Label(self.window,
                            text=f"Status:",
                            font=SECONDARY_FONT,
                            bg="white",
                            )            
        self.status_msg.place(relx=0.75, rely=0.7)   

        self.toggle = Button(self.window, 
                            image=self.online_button, 
                            command=self.switch_status, 
                            bd=0,
                            bg="white",)
        self.toggle.place(relx=0.90, rely=0.7)  

        self.send_lable = Label(self.window,
                                #  bg = "white",
                                 height = 80)
          
        self.send_lable.place(relwidth = 1,
                               rely = 0.8)
          
        self.write_msg = Entry(self.send_lable,
                              bg = "black",
                              fg = "white",
                              font = TERTIARY_FONT)
          
        self.write_msg.place(relwidth = 0.68,
                            relheight = 0.06,
                            rely = 0.008,
                            relx = 0.011,
                            )
  
        self.write_msg.focus()
          
        self.send_button = Button(self.send_lable,
                                text = "Send",
                                font = SECONDARY_FONT, 
                                width = 20,
                                bg = "#ABB2B9",
                                command = lambda : self.send_msg_to_peer())
          
        self.send_button.place(relx = 0.77,
                             rely = 0.008,
                             relheight = 0.06, 
                             relwidth = 0.22)
                    
        scrollbar = Scrollbar(self.window)
          
        scrollbar.place(relheight = 0.745,
                        relx = 0.72,
                        rely = 0.08)
          
        scrollbar.config(command = self.view_messages.yview)

        # mensagem a ser exibida para o usuário
        display_msg = 'You have connected to the chat. Select the user you want to send a message to.\n\n'

        # insere o nome do usuário na lista de usuários ativos
        self.users_box.insert(END, f' {self.user.name} (You)')

        self.write_msg.delete(0, END)

        # insere a mensagem display_msg no bate-papo
        self.display_msg(display_msg)
        self.update_users_box()
        

    def switch_status(self):
        if self.status == "online":
            send_message_to_server(self.user, 'close')
            self.toggle.config(image=self.offline_button)
            self.status = "offline"
            self.users_box.delete(0,END) 
            
        elif self.status == "offline":
            send_message_to_server(self.user, 'open')
            self.toggle.config(image=self.online_button)
            self.status = "online"
            self.users_box.insert(END, f' {self.user.name} (You)')
            self.update_users_box()
            

    def send_msg_to_peer(self):
        peer_name = self.users_box.get(ANCHOR).strip()
        msg = self.write_msg.get()
        if peer_name == "":
            self.display_msg("You have to select an active user!\n")
        elif peer_name == f" {self.user.name} (You)":
            self.display_msg("You can't send a message to yourself!\n")
        else:
            peer = self.get_peer(peer_name)
            peer_address = tuple(peer["open"])
            self.connect_p2p(peer, peer_name, peer_address)
            message = f"({self.user.name}): " + msg + '\n'
            self.send_request_to_peer(peer_address=peer_address, command='send', message=message)
            self.user.close_socket(peer_name, peer_address)
            self.display_msg(f"(To {peer_name}): {msg}\n")

    def send_request_to_peer(self, peer_address, command, message, destiny_sock=None):

        msg_dict = {
            "type" : "p2p",
            "source": (SERVER_HOST, self.user.address[1]),
            "destiny" : peer_address,
            "command" : command,
            "message" : message
        }
        msg = json.dumps(msg_dict)

        if destiny_sock is None:
            destiny_sock = self.user.connections.get(peer_address, "ERROR")
            if destiny_sock == 'ERROR':
                print("SOCKET NOT VALID: ", peer_address, " not found")
                return
        
        destiny_sock.sendall(bytes(msg, encoding='utf-8'))

    def connect_p2p(self, peer, peer_name, peer_address):
        new_sock = socket.socket()
        new_sock.connect(peer_address)
        self.user.peers[peer_name] = peer_address
        self.user.connections[peer_address] = new_sock

    def get_peer(self, peer_name):
        for peer in self.available_users:
            if peer["user"] == peer_name:
                return peer

    def display_msg(self, msg):
        self.view_messages.config(state = NORMAL)
        self.view_messages.insert(END, msg)
        self.view_messages.config(state = DISABLED)
        self.view_messages.see(END)

    def update_users_box(self):
        self.users_box.delete(1,END)
        for user in self.usernames:
            self.users_box.insert(END, f' {user}')

g = GUI()

server_sock.close() 
