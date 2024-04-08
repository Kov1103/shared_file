import customtkinter
from database_handler import *
import tkinter.messagebox
import os

class App(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # configure app window
        self.title("P2P File Sharing Server")
        self.geometry("1100x580")
        self.resizable(False, False)
        self.iconbitmap(os.path.join(os.path.join(os.path.dirname(__file__), 'image'), 'icon.ico'))

        # create a grid layout
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=16)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=15)
        self.grid_rowconfigure(1, weight=1)

        # Frame: sidebar
        self.sidebar_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)


        self.server_label = customtkinter.CTkLabel(self.sidebar_frame, text="P2P Server", font=customtkinter.CTkFont(size=25, weight="bold"))
        self.server_label.grid(row=0, column=0, padx=20, pady=20)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:")
        self.appearance_mode_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionmenu.grid(row=2, column=0, padx=20, pady=(5, 10))

        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:")
        self.scaling_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionmenu.grid(row=4, column=0, padx=20, pady=5)

        self.reset_button = customtkinter.CTkButton(master=self.sidebar_frame, text="Reset", command=self.reset, hover_color="#FFFF00")
        self.reset_button.grid(row=5, column=0, padx=20, pady=50)

        # Frame: Clients list
        self.clients_frame = customtkinter.CTkScrollableFrame(self, label_text="Clients")
        self.clients_frame.grid(row=0, column=1, columnspan=2 ,padx=(10, 0), sticky="nsew")
        self.clients_frame.grid_columnconfigure(0, weight=10)
        self.clients_frame.grid_columnconfigure(0, weight=1)
        self.clients_frame.grid_columnconfigure(0, weight=1)
        self.clients_names = get_all_users()
        self.clients_labels = []

        for i, username in enumerate(self.clients_names):
            client_label = customtkinter.CTkLabel(master=self.clients_frame, text=username)
            client_label.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.clients_labels.append(client_label)

            view_button = customtkinter.CTkButton(master=self.clients_frame, text="View Files", command=lambda username=username: self.view_client_files(username), hover_color="#00b359")
            view_button.grid(row=i, column=1, padx=10, pady=(0, 20))
            self.files_list = None

            ping_button = customtkinter.CTkButton(master=self.clients_frame, text="Ping", command = lambda username = username: self.ping_client(username), hover_color="#f67c41")
            ping_button.grid(row=i, column=2, padx=10, pady=(0, 20))
        
        ## Command line
        self.cmd_input = customtkinter.CTkEntry(self, placeholder_text="Command...")
        self.cmd_input.grid(row=1, column=1, padx=(10, 10), pady=10, sticky="nsew")
        self.enter_btn = customtkinter.CTkButton(master=self, text="Enter", command = lambda:self.commandLine(command = self.cmd_input.get()), border_width=2, text_color=("gray10", "#DCE4EE"))
        self.enter_btn.grid(row=1, column=2, padx=(10, 10), pady=10, sticky="nsew")

    def reset(self):
        self.clients_names = get_all_users()
        self.clients_labels = []

        for i, username in enumerate(self.clients_names):
            client_label = customtkinter.CTkLabel(master=self.clients_frame, text=username)
            client_label.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.clients_labels.append(client_label)

            view_button = customtkinter.CTkButton(master=self.clients_frame, text="View Files", command=lambda username=username: self.view_client_files(username), hover_color="#00b359")
            view_button.grid(row=i, column=1, padx=10, pady=(0, 20))
            self.files_list = None

            ping_button = customtkinter.CTkButton(master=self.clients_frame, text="Ping", command = lambda username = username: self.ping_client(username), hover_color="#f67c41")
            ping_button.grid(row=i, column=2, padx=10, pady=(0, 20))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def view_client_files(self,username):
        self.files_list = get_user_file(username)
        if self.files_list is None or not isinstance(self.files_list, ClientFilesList):
            self.files_list = ClientFilesList(self, username)
        else:
            self.files_list.focus()

    def ping_client(self, username):
        onlineList = get_onl_users()
        if username in onlineList:
            status_message = f"Người dùng {username} hiện đang online."
        else:
            status_message = f"Người dùng {username} hiện không trực tuyến."
        tkinter.messagebox.showinfo("Trạng thái người dùng", status_message)

    def commandLine(self, command):
        parts = command.split()

        if len(parts) != 2:
            message = "Lệnh không hợp lệ vui lòng nhập lại!"
            tkinter.messagebox.showinfo("Lỗi", message)
        else:
            if parts[0] == "discover":
                username = parts[1]
                self.view_client_files(username)

            elif parts[0] == "ping":
                username = parts[1]
                self.ping_client(username)

            else:
                message = "Lệnh không hợp lệ vui lòng nhập lại!"
                tkinter.messagebox.showinfo(message)


class ClientFilesList(customtkinter.CTkToplevel):
    def __init__(self, master, username, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.username = username
        self.title(f"{self.username}'s Files List")
        self.geometry("550x290")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.files_frame = customtkinter.CTkScrollableFrame(self, label_text="List of Files")
        self.files_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        
        self.clients_files = get_user_file(self.username)
        self.clients_files_labels = []
        for i, file_name in enumerate(self.clients_files):
            client_label = customtkinter.CTkLabel(master=self.files_frame, text=file_name)
            client_label.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.clients_files_labels.append(client_label)