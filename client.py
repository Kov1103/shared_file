import os
import json
import shutil
import tkinter as tk
import customtkinter
import socket
import threading
from hashfunction import MD5_hash
import tkinter.messagebox
import tkinter.filedialog
from tkinter import simpledialog

from Base import Base
from database_handler import *

FORMAT = "utf-8"
BUFFER_SIZE = 2048
OFFSET = 10000

def display_noti(title, content):
    tk.messagebox.showinfo(title, content)

#-------------------------------------------------App-------------------------------------------------#
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.chatroom_textCons = None

        self.frames = {}

        # iterating through a tuple consisting of the different page layouts
        for F in (StartPage, RegisterPage, LoginPage, RepoPage):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(bg='white')
        self.show_frame(StartPage)

    # display the current frame passed as parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

#-------------------------------------------------Start-------------------------------------------------#
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.page_title = customtkinter.CTkLabel(self, text="P2P File Sharing", font=("Arial Bold", 36))
        self.page_title.pack(pady=(80, 10))

        self.port_label = customtkinter.CTkLabel(self, text="Set Port (1024 -> 65535)", font=("Arial", 20))
        self.port_label.pack(pady=(10, 5))

        self.port_entry = customtkinter.CTkEntry(self, placeholder_text="Enter port number", border_width=2)
        self.port_entry.pack(pady=(0, 10))

        self.register_button = customtkinter.CTkButton(self, text="Đăng ký", command=lambda: 
                                self.enter_app(controller=controller, port=self.port_entry.get(), page=RegisterPage))
        self.register_button.pack(pady=10)
        
        self.login_button = customtkinter.CTkButton(self, text="Đăng nhập", command=lambda: 
                                self.enter_app(controller=controller, port=self.port_entry.get(), page=LoginPage))
        self.login_button.pack(pady=10)

    def enter_app(self, controller, port, page):
        if (int(port) >= 1024 and int(port) <= 65535 and port.isdigit()):
            # get peer current ip address
            hostname = socket.gethostname()   
            IPAddr = socket.gethostbyname(hostname)  

            # init server
            global network_peer
            network_peer = NetworkPeer(serverhost=IPAddr, serverport=int(port))
        
            # A child thread for receiving message
            recv_t = threading.Thread(target=network_peer.input_recv)
            recv_t.daemon = True
            recv_t.start()

            # A child thread for receiving file  
            recv_file_t = threading.Thread(target=network_peer.recv_file_content)
            recv_file_t.daemon = True
            recv_file_t.start()
            controller.show_frame(page)
        else:
            self.port_entry.delete(0, customtkinter.END)
            display_noti("Port Error!",  "Cổng đã được sử dụng hoặc chứa giá trị không hợp lệ")

#-------------------------------------------------Register-------------------------------------------------#
class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)   

        self.frame = customtkinter.CTkFrame(master=self, fg_color="white")
        self.frame.pack(fill='both', expand=True)

        self.title_label = customtkinter.CTkLabel(self.frame, text="Register", font=("Roboto Bold", 32))
        self.title_label.pack(pady=(80, 10))

        self.username = customtkinter.CTkLabel(self.frame, text="Username", font=("Roboto", 14))
        self.username.pack(pady=(0))
        self.username_entry = customtkinter.CTkEntry(self.frame, placeholder_text="Enter username", font=("Roboto", 12))
        self.username_entry.pack(pady=(0))

        self.password = customtkinter.CTkLabel(self.frame, text="Password", font=("Roboto", 14))
        self.password.pack(pady=(0))
        self.password_entry = customtkinter.CTkEntry(self.frame, placeholder_text="Enter password", font=("Roboto", 12), show = '*')
        self.password_entry.pack(pady=(0, 10))

        customtkinter.CTkButton(self.frame, text='Đăng ký', command=lambda: 
                                self.register_user(self.username_entry.get(), self.password_entry.get())).pack(pady=(0, 10))
        customtkinter.CTkLabel(self.frame, text="Đã có tài khoản ?", font=("Roboto", 11)).pack(pady=(70, 0))
        customtkinter.CTkButton(self.frame, text='Đăng nhập', command=lambda: controller.show_frame(LoginPage)).pack(pady=(0, 10))

    def register_user(self, username, password):
        if not username or not password:
            display_noti("Lỗi thông tin", "Thông tin không hợp lệ vui lòng nhập lại!")
            self.username_entry.delete(0, customtkinter.END)
            self.password_entry.delete(0, customtkinter.END)
        else:
            network_peer.name = str(username)
            # hash password by MD5 algorithm
            network_peer.password = MD5_hash(str(password))
            self.username_entry.delete(0, customtkinter.END)
            self.password_entry.delete(0, customtkinter.END)
            network_peer.send_register()

#-------------------------------------------------Login-------------------------------------------------#
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.frame = customtkinter.CTkFrame(master=self, fg_color="white")
        self.frame.pack(fill='both', expand=True)

        self.title_label = customtkinter.CTkLabel(self.frame, text="Log In", font=("Roboto Bold", 32))
        self.title_label.pack(pady=(80, 10))

        self.username = customtkinter.CTkLabel(self.frame, text="Username", font=("Roboto", 14))
        self.username.pack(pady=(0))
        self.username_entry = customtkinter.CTkEntry(self.frame, placeholder_text="Enter username", font=("Roboto", 12))
        self.username_entry.pack(pady=(0))

        self.password = customtkinter.CTkLabel(self.frame, text="Password", font=("Roboto", 14))
        self.password.pack(pady=(0))
        self.password_entry = customtkinter.CTkEntry(self.frame, placeholder_text="Enter password", font=("Roboto", 12), show = '*')
        self.password_entry.pack(pady=(0, 10))

        customtkinter.CTkButton(self.frame, text='Đăng nhập', command=lambda: self.login_user(username=self.username_entry.get(), password=self.password_entry.get())).pack(pady=(0, 10))
        customtkinter.CTkLabel(self.frame, text="Bạn chưa có tài khoản ?", font=("Roboto", 11)).pack(pady=(70, 0))
        customtkinter.CTkButton(self.frame, text='Đăng ký', cursor="hand2", command=lambda: controller.show_frame(RegisterPage)).pack(pady=(0, 10))

    def login_user(self, username, password):
        if not username or not password:
            display_noti("Lỗi thông tin", "Thông tin không hợp lệ vui lòng nhập lại!")
            self.username_entry.delete(0, customtkinter.END)
            self.password_entry.delete(0, customtkinter.END)
        else:
            network_peer.name = str(username)
            # hash password by MD5 algorithm
            network_peer.password = MD5_hash(str(password))
            self.username_entry.delete(0, customtkinter.END)
            self.password_entry.delete(0, customtkinter.END)
            network_peer.send_login()

#-------------------------------------------------Repo-------------------------------------------------#
class RepoPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent)       

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=17)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=15)
        self.grid_rowconfigure(1, weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="P2P Server", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button = customtkinter.CTkButton(self.sidebar_frame, text="Quit", command=lambda: self.quit_user())
        self.sidebar_button.grid(row=1, column=0, padx=20, pady=10)

        self.logout_button = customtkinter.CTkButton(self.sidebar_frame, text="Log Out", command=lambda: self.logout_user())
        self.logout_button.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:")
        self.appearance_mode_label.grid(row=3, column=0, padx=20, pady=(200, 0))
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=4, column=0, padx=20, pady=(5, 10))

        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:")
        self.scaling_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=6, column=0, padx=20, pady=(5, 20))


        self.repo_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.repo_frame.grid(row=0, column=1, columnspan=2, sticky="nsew")
        self.repo_frame.grid_rowconfigure(0, weight=1)
        self.repo_frame.grid_columnconfigure(0, weight=1)
        self.repo_frame.grid_columnconfigure(1, weight=1)
       

        self.scrollable_repo_frame = customtkinter.CTkScrollableFrame(self.repo_frame, label_text="Repository")
        self.scrollable_repo_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.scrollable_repo_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_repo_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_file_names = []
        self.fileListBox = tk.Listbox(self.scrollable_repo_frame, width=50)
        self.fileListBox.grid(row=0, column=0, padx=10, pady=(10, 10))
        

        self.temp_frame = customtkinter.CTkFrame(master=self.scrollable_repo_frame, fg_color="transparent")
        self.temp_frame.grid(row=1, column=0, sticky="nsew")
        self.temp_frame.grid_rowconfigure(0, weight=1)
        self.temp_frame.grid_columnconfigure(0, weight=1)
        self.temp_frame.grid_columnconfigure(1, weight=1)

        self.delete_button = customtkinter.CTkButton(master=self.temp_frame, border_width=2, text="Delete from Repo", command=lambda: self.deleteSelectedFile())
        self.delete_button.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.add_button = customtkinter.CTkButton(master=self.temp_frame, border_width=2, text="Add to Repo", command=lambda: self.chooseFile())
        self.add_button.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.update_button = customtkinter.CTkButton(master=self.scrollable_repo_frame, border_width=2, text="Update to Server", command=lambda: self.updateListFile())
        self.update_button.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.update_button = customtkinter.CTkButton(master=self.scrollable_repo_frame, border_width=2, text="Reload Repo", command=lambda: self.reloadRepo())
        self.update_button.grid(row=3, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        ### create frame for peer list
        self.peer_frame = customtkinter.CTkScrollableFrame(self.repo_frame, label_text="Peer List")
        self.peer_frame.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.peer_frame.grid_rowconfigure(0, weight=1)
        self.peer_frame.grid_columnconfigure(0, weight=1)
        self.peer_names = []
        self.peerListBox = tk.Listbox(self.peer_frame, width=50)
        self.peerListBox.grid(row=0, column=0, padx=10, pady=(10, 10))
        

        self.search_frame = customtkinter.CTkFrame(self.peer_frame, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.search_frame.grid_columnconfigure(0, weight=10)
        self.search_frame.grid_columnconfigure(1, weight=1)
        self.search_entry = customtkinter.CTkEntry(master=self.search_frame, placeholder_text="Search...")
        self.search_entry.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.search_button = customtkinter.CTkButton(master=self.search_frame, text="Search", border_width=2, command=lambda: self.get_users_share_file_from_entry())
        self.search_button.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")

        self.request_button = customtkinter.CTkButton(master=self.peer_frame, border_width=2, command=lambda:self.fileRequest(), text="Send Connect Request")
        self.request_button.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")


        self.entry = customtkinter.CTkEntry(self, placeholder_text="Command...")
        self.entry.grid(row=1, column=1, padx=(10, 10), pady=(20, 20), sticky="nsew")
        self.main_button_1 = customtkinter.CTkButton(master=self, text="Enter", command=lambda: self.commandLine(command = self.entry.get()), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.main_button_1.grid(row=1, column=2, padx=(10, 10), pady=(20, 20), sticky="nsew")


    def logout_user(self):
        if tkinter.messagebox.askokcancel("Đăng xuất", "Bạn muốn đăng xuất?"):
            network_peer.send_logout_request()
            app.show_frame(StartPage)

    def quit_user(self):
        if tkinter.messagebox.askokcancel("Thoát", "Bạn muốn thoát khỏi ứng dụng?"):
            network_peer.send_logout_request()
            app.destroy()
    
    def commandLine(self, command):
        parts = command.split()

        if parts[0] == "publish":
            if len(parts) == 3:
                file_path = parts[1]
                file_name = parts[2]

                network_peer.updateToServer(file_name, file_path)
                self.fileListBox.insert(0,file_name + "(" + file_path +")")
                self.sendtoServerPath(file_path)
                
            else:
                message = "Lệnh không hợp lệ vui lòng nhập lại!"
                tkinter.messagebox.showinfo(message)
        elif parts[0] == "fetch":
            if len(parts) == 2:
                file_name = parts[1]

                network_peer.send_listpeer(file_name)
                msg_box = tkinter.messagebox.askquestion('File Explorer', 'Send request?',
                                                    icon="question")
                if msg_box == 'yes':
                    network_peer.send_request(app.frames[RepoPage].peerListBox.get(0), file_name)
            else:
                message = "Lệnh không hợp lệ vui lòng nhập lại!"
                tkinter.messagebox.showinfo(message)
        else:
            message = "Lệnh không hợp lệ vui lòng nhập lại!"
            tkinter.messagebox.showinfo(message)
            
    def sendtoLocalPath(self, file_path):
        # create a folder named "repo" in this folder
        if not os.path.exists("localRepo"):
            os.makedirs("localRepo")
        destination = os.path.join(os.getcwd(), "localRepo")
        shutil.copy(file_path, destination)

    def deleteFromLocalPath(self, file_path):
        destination = os.path.join(os.getcwd(), "localRepo")
        file_name = os.path.basename(file_path)
        name = os.path.join(destination, file_name)
        os.remove(name)

    def sendtoServerPath(self, file_path):
        # create a folder named "repo" in this folder
        if not os.path.exists("serverRepo"):
            os.makedirs("serverRepo")
        destination = os.path.join(os.getcwd(), "serverRepo")
        shutil.copy(file_path, destination)    

    def chooseFile(self):
        file_path = tkinter.filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("All files", "*.*"),))

        if file_path:
            file_name = file_path
            msg_box = tkinter.messagebox.askquestion('File Explorer', 'Upload {} to local repository?'.format(file_name),
                                                    icon="question")
            if msg_box == 'yes':
                self.fileListBox.insert(0,file_name)
                tkinter.messagebox.showinfo(
                    "Local Repository", '{} has been added to local repo!'.format(file_name))
                self.sendtoLocalPath(file_name)
            
    def fileRequest(self):
        if self.peerListBox.get(tk.ANCHOR):
            peer_info = self.peerListBox.get(tk.ANCHOR)
            file_name = self.search_entry.get()
            network_peer.send_request(peer_info, file_name)
        else:
            display_noti("Warning", "Bạn phải chọn người dùng mong muốn!")

    def updateListFile(self):
        if self.fileListBox.get(tk.ANCHOR):
            self.fileNameServer = simpledialog.askstring("Input","Nhập tên file lưu trên Server", parent = self)
            file_path = self.fileListBox.get(tk.ANCHOR)
            self.sendtoServerPath(file_path)
            network_peer.updateToServer(self.fileNameServer, file_path)
            self.fileListBox.delete(tk.ANCHOR)
            self.fileListBox.insert(0,self.fileNameServer + "(" + file_path +")")
        else:
            display_noti("Warning", "Bạn phải chọn file mong muốn!")

    def updateListFilefromFetch(self, file_name, file_name_server):
        file_path = os.path.join(os.path.join(os.getcwd(), 'localRepo'), file_name)
        self.sendtoServerPath(file_path)
        network_peer.updateToServer(file_name_server, file_path)
        # self.fileListBox.delete(tk.ANCHOR)
        # self.fileListBox.insert(0,file_name_local + "(" + file_name +")")

    def deleteSelectedFile(self):
        if self.fileListBox.get(tk.ANCHOR):
            file_name = self.fileListBox.get(tk.ANCHOR)
            self.fileListBox.delete(tk.ANCHOR)
            self.deleteFromLocalPath(file_name)
            network_peer.deleteFileServer(file_name)
        else:
            display_noti("Warning", "Bạn phải chọn file mong muốn!")

    def get_users_share_file_from_entry(self):
        file_name = self.search_entry.get()
        self.peerListBox.delete(0, tk.END)
        network_peer.send_listpeer(file_name)

    def reloadRepo(self):
        for file in self.fileListBox.get(0, tk.END):
            self.fileListBox.delete(0, tk.END)
        path = os.path.join(os.getcwd(), "localRepo")
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            self.fileListBox.insert(tk.END, file_path)
        # network_peer.reloadRepoList()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


class NetworkPeer(Base):
    def __init__(self, serverhost='localhost', serverport=40000, server_info=('192.168.1.5', 40000)):
        super(NetworkPeer, self).__init__(serverhost, serverport)

        # init host and port of central server
        self.server_info = server_info

        # peer name
        self.name = ""
        # peer password
        self.password = ""

        # all peers it can connect (network peers)
        self.connectable_peer = {}

        # peers it has connected (friend)
        self.friendlist = {}

        self.message_format = '{peername}: {message}'
        # file buffer
        self.file_buf = []

        # define handlers for received message from network peer
        handlers = {
            'REGISTER_SUCCESS': self.register_success,
            'REGISTER_ERROR': self.register_error,
            'LOGIN_SUCCESS': self.login_success,
            'LOGIN_ERROR': self.login_error,
            'LIST_USER_SHARE_FILE': self.get_users_share_file,
            'FILE_REQUEST': self.file_request,
            'FILE_ACCEPT': self.file_accept,
            'FILE_REFUSE': self.file_refuse,
        }
        for msgtype, function in handlers.items():
            self.add_handler(msgtype, function)

    ## ==========implement protocol for user registration - network peer==========##
    def send_register(self):
        """ Send a request to server to register peer's information. """
        peer_info = {
            'peername': self.name,
            'password': self.password,
            'host': self.serverhost,
            'port': self.serverport
        }
        self.client_send(self.server_info, msgtype='PEER_REGISTER', msgdata=peer_info)

    def register_success(self, msgdata):
        """ Processing received message from server: Successful registration on the server. """
        display_noti('Register Notification', 'Đăng ký thành công, mời bạn đăng nhập')
        print('Register Successful.')
        app.show_frame(LoginPage)

    def register_error(self, msgdata):
        """ Processing received message from server: Registration failed on the server. """
        display_noti('Register Noti',
                     'Đăng ký thất bại. Tên đăng nhập đã tồn tại hoặc không hợp lệ!')
        print('Register Error. Username existed!')
    ## ===========================================================##

    ## ==========implement protocol for authentication (log in) - network peer==========##
    def send_login(self):
        """ Send a request to server to login. """
        peer_info = {
            'peername': self.name,
            'password': self.password,
            'host': self.serverhost,
            'port': self.serverport
        }
        self.client_send(self.server_info, msgtype='PEER_LOGIN', msgdata=peer_info)

    def login_success(self, msgdata):
        """ Processing received message from server: Successful login on the server. """
        print('Login Successful.')
        display_noti('Login Notification', 'Đăng nhập thành công')
        app.show_frame(RepoPage)

    def login_error(self, msgdata):
        """ Processing received message from server: Login failed on the server. """
        display_noti('Login Notification', 'Đăng nhập thất bại! Sai tên đăng nhập hoặc mật khẩu.')
        print('Login Error. Username not existed or wrong password')
    ## ===========================================================##

    ## ==========implement protocol for getting online user list who have file that client find==========##
    def send_listpeer(self, filename):
        """ Send a request to server to get all online peers who have file that client find. """
        peer_info = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': filename
        }
        self.client_send(self.server_info, msgtype='PEER_SEARCH', msgdata=peer_info)
        
    def get_users_share_file(self, msgdata):
        shareList = msgdata['online_user_list_have_file']
        for peername, data in shareList.items():
            peer_host, peer_port = data
            info = str(peer_host) + "," + str(peer_port)
            app.frames[RepoPage].peerListBox.insert(0, info)
            print(app.frames[RepoPage].peerListBox.get(0))

    # def reloadRepoList(self):
    #     fileList = []
    #     fileList = get_user_file(self.name)
    #     for file in fileList:
    #         app.frames[RepoPage].fileListBox.insert(0,file)

    ## ===========================================================##

    ## ==========implement protocol for file request==========##
    def send_request(self, peerinfo, filename):
        """ Send a file request to an online user. """
        peerhost, peerport = peerinfo.split(',')
        print(peerhost, peerport)
        peer = (peerhost, int(peerport))
        data = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': filename
        }
        self.client_send(peer, msgtype='FILE_REQUEST', msgdata=data)

    ##=====Hàm này dùng để hiển thị có yêu cầu chia sẻ file để người dùng chọn đồng ý hoặc không====#
    def file_request(self, msgdata):
        """ Processing received file request message from peer. """
        peername = msgdata['peername']
        host, port = msgdata['host'], msgdata['port']
        filename = msgdata['filename']
        msg_box = tkinter.messagebox.askquestion('File Request', '{} - {}:{} request to take the file "{}"?'.format(peername, host, port, filename),
                                            icon="question")
        if msg_box == 'yes':
            # if request is agreed, connect to peer (add to friendlist)
            data = {
                'peername': self.name,
                'host': self.serverhost,
                'port': self.serverport
            }
            display_noti("File Request Accepted", "Send The File!")
            self.friendlist[peername] = (host, port)
            destination = os.path.join(os.getcwd(), "localRepo")
            file_path = tkinter.filedialog.askopenfilename(initialdir=destination,
                                                       title="Select a File",
                                                       filetypes=(("All files", "*.*"),))
            file_name = os.path.basename(file_path)
            msg_box = tkinter.messagebox.askquestion('File Explorer', 'Are you sure to send {} to {}?'.format(file_name, peername),
                                                 icon="question")
            if msg_box == 'yes':
                self.client_send((host, port), msgtype='FILE_ACCEPT', msgdata=data)
                sf_t = threading.Thread(
                    target=network_peer.transfer_file, args=(peername, file_path, filename))
                sf_t.daemon = True
                sf_t.start()
                tkinter.messagebox.showinfo(
                    "File Transfer", '{} has been sent to {}!'.format(file_name, peername))
            else:
                self.client_send((host, port), msgtype='FILE_REFUSE', msgdata={})

    #=======Hàm này dùng để chuyển file cho máy khách sau khi đã chọn đồng ý=======#
    def file_accept(self, msgdata):
        """ Processing received accept file request message from peer.
            Add the peer to collection of friends. """
        peername = msgdata['peername']
        host = msgdata['host']
        port = msgdata['port']
        display_noti("File Request Result",
                     "User accept to send the file!")
        self.friendlist[peername] = (host, port)

    def file_refuse(self, msgdata):
        """ Processing received refuse chat request message from peer. """
        display_noti("File Request Result", 'User refuse to send file!')
    ## ===========================================================##
    
    def recv_public_message(self, msgdata):
        """ Processing received public chat message from central server."""
        # insert messages to text box
        message = msgdata['name'] + ": " + msgdata['message']
        app.chatroom_textCons.config(state=tkinter.NORMAL)
        app.chatroom_textCons.insert(tkinter.END, message+"\n\n")
        app.chatroom_textCons.config(state=tkinter.DISABLED)
        app.chatroom_textCons.see(tkinter.END)
    ## ===========================================================##

    ## ==========implement protocol for file tranfering==========##
    def transfer_file(self, peer, file_path, file_name_server):
        """ Transfer a file. """
        try:
            peer_info = self.friendlist[peer]
        except KeyError:
            display_noti("File Transfer Result", 'Friend does not exist!')
        else:
            file_name = os.path.basename(file_path)
            def fileThread(filename):
                file_sent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                file_sent.connect((peer_info[0], peer_info[1] + OFFSET))

                # send filename and friendname
                fileInfo = {
                    'filename': filename,
                    'friendname': peer,
                    'filenameserver': file_name_server
                }

                fileInfo = json.dumps(fileInfo).encode(FORMAT)
                file_sent.send(fileInfo)
                
                msg = file_sent.recv(BUFFER_SIZE).decode(FORMAT)
                print(msg)

                with open(file_path, "rb") as f:
                    while True:
                        # read the bytes from the file
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            break
                        file_sent.sendall(bytes_read)
                file_sent.shutdown(socket.SHUT_WR)
                file_sent.close()
                display_noti("File Transfer Result", 'File has been sent!')
                return
            t_sf = threading.Thread(target=fileThread,args=(file_name,))
            t_sf.daemon = True
            t_sf.start()

    def recv_file_content(self):
        """ Processing received file content from peer."""
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to our local address
        self.file_socket.bind((self.serverhost, int(self.serverport) + OFFSET))
        self.file_socket.listen(5)

        while True:
            conn, addr = self.file_socket.accept()
            buf = conn.recv(BUFFER_SIZE)
            message = buf.decode(FORMAT)

            # deserialize (json type -> python type)
            recv_file_info = json.loads(message)

            conn.send("Filename received.".encode(FORMAT))
            print(recv_file_info)

            file_name = recv_file_info['filename']
            friend_name = recv_file_info['friendname']
            file_name_server = recv_file_info['filenameserver']

            lr = os.path.join(os.getcwd(), 'localRepo')
            with open(os.path.join(lr, file_name), "wb") as f:
                while True:
                    bytes_read = conn.recv(BUFFER_SIZE)
                    if not bytes_read:    
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)
            
            repo = RepoPage()
            repo.updateListFilefromFetch(file_name, file_name_server)
            conn.shutdown(socket.SHUT_WR)
            conn.close()

            display_noti("File Transfer Result", 'You receive a file with name ' + file_name + ' from ' + friend_name)
    
    ## ===========================================================##
    
    ## ==========implement protocol for log out & exit ===================##

    def send_logout_request(self):
        """ Central Server deletes user out of online user list """
        peer_info = {
            'peername': self.name,
        }
        self.client_send(self.server_info, msgtype='PEER_LOGOUT', msgdata=peer_info)
        print("Logout successful!")

    ## ===========================================================##
    def deleteFileServer(self,file_name):
        """ Delete file from server. """
        peer_info = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': file_name
        }
        self.client_send(self.server_info, msgtype='DELETE_FILE', msgdata=peer_info)
        
    def updateToServer(self, file_name, file_path):
        """ Upload repo to server. """
        peer_info = {
            'peername': self.name,
            'host': self.serverhost,
            'port': self.serverport,
            'filename': file_name,
            'filepath': file_path
        }
        self.client_send(self.server_info, msgtype='FILE_REPO', msgdata=peer_info)
    
# ------ app run ---------- #
if __name__ == "__main__":
    app = App()
    app.title('P2P File Sharing')
    app.geometry("1024x600")
    app.resizable(False, False)
    app.iconbitmap(os.path.join(os.path.join(os.path.dirname(__file__), 'image'), 'icon.ico'))

    def handle_on_closing_event():
        if tkinter.messagebox.askokcancel("Thoát", "Bạn muốn thoát khỏi ứng dụng?"):
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", handle_on_closing_event)
    app.mainloop()
