from threading import Thread
from Base import Base
from database_handler import *
import tkinter.messagebox

from server_app import App

class CentralServer(Base):
    def __init__(self, serverhost='172.16.3.28', serverport=40000):
        super(CentralServer, self).__init__(serverhost, serverport)

        # manage registered user list
        self.peerList = get_all_users()

        # manage online user list
        self.onlineList = {} 

        # manage online user list have file which have been searched
        self.shareList = {}

        # Delete data remaining in the latest run on the table "online" of the database
        delete_all_onl_users()

        # handlers for received message of the client
        handlers = {
            'PEER_REGISTER': self.peer_register,
            'PEER_LOGIN': self.peer_login,
            'PEER_SEARCH': self.peer_search,
            'PEER_LOGOUT': self.peer_logout,
            'FILE_REPO': self.peer_upload,
            'DELETE_FILE': self.delete_file,
        }

        for msgtype, function in handlers.items():
            self.add_handler(msgtype, function)
        
    ## ==========implement protocol for user registration - central server==========##
    def peer_register(self, msgdata):
        # received register info (msgdata): name, host, port, password (MD5 hashed)
        peer_name = msgdata['peername']
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        peer_password = msgdata['password']
        
        # if exist, error, else add to the user list
        if peer_name in self.peerList:
            self.client_send((peer_host, peer_port), msgtype='REGISTER_ERROR', msgdata={})
            print(peer_name, " has been existed in central server's managed user list!!")
        else:
            self.peerList.append(peer_name)
            add_new_user(peer_name, peer_password) # add new user to database
            self.client_send((peer_host, peer_port), msgtype='REGISTER_SUCCESS', msgdata={})
            print(peer_name, " has been added to central server's managed user list!")
    ## ===========================================================##

    ## ==========implement protocol for authentication (log in) - central server==========##
    def peer_login(self, msgdata):
        # received login info (msgdata): name, host, port, password (MD5 hashed)
        peer_name = msgdata['peername'] 
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        peer_password = msgdata['password']
        # If not register yet, error, else add to the online list
        if peer_name in self.peerList:
            # check password
            peer_password_check = get_user_password(peer_name)
            if str(peer_password) == peer_password_check:
                self.onlineList[peer_name] = tuple((peer_host, peer_port))
                add_onl_user(peer_name) # add online user to database
                self.client_send((peer_host, peer_port), msgtype='LOGIN_SUCCESS', msgdata={})

                # update the database
                update_user_address_port(peer_name, peer_host, peer_port)
                print(peer_name, " has been added to central server's online user list!")

            else:
                self.client_send((peer_host, peer_port), msgtype='LOGIN_ERROR', msgdata={})
                print("Password incorrect!")
        else:
            self.client_send((peer_host, peer_port), msgtype='LOGIN_ERROR', msgdata={})
            print(peer_name, " has not been existed in central server!")
    ## ===========================================================##

    ## =========implement protocol for finding user list who have file searched==============##
    def peer_search(self, msgdata):
        peer_name = msgdata['peername']
        peer_host = msgdata['host']
        peer_port = msgdata['port']
        file_name = msgdata['filename']
        user_list = search_file_name(file_name)

        for file_searched_peer in user_list:
            if file_searched_peer in self.onlineList:
                self.shareList[file_searched_peer] = self.onlineList[file_searched_peer]

        data = {
            'online_user_list_have_file': self.shareList
        }

        self.client_send((peer_host, peer_port), msgtype='LIST_USER_SHARE_FILE', msgdata=data)
        print(peer_name, " has been sent latest online user list have file!")
        self.shareList.clear()

    ## ================implement protocol for log out & exit=============##
    def peer_logout(self, msgdata):
        peer_name = msgdata['peername']
        # get the online user data from database
        onlineList = get_onl_users()
        # delete peer out of online user list 
        if peer_name in onlineList:
            onlineList.remove(peer_name)
            # remove the logging out user
            remove_onl_user(peer_name)
            print(peer_name, " has been removed from central server's online user list!")
    ## ===========================================================##

    ## ================implement protocol for peer upload file=============##
    def peer_upload(self, msgdata):
        peer_name = msgdata['peername']
        file_name = msgdata['filename']
        file_path = msgdata['filepath']
        add_new_file(peer_name, file_name, file_path)
    ## ===========================================================##


    ##=================implement protocol for peer delete file=============##
    def delete_file(self, msgdata):
        peer_name = msgdata['peername']
        file_name = msgdata['filename']
        delete_file(peer_name, file_name)

def run_server():
    server = CentralServer()
    server.input_recv()

if __name__ == '__main__':
    app = App()

    server_thread = Thread(target=run_server)
    server_thread.start()

    def handle_on_closing_event():
        if tkinter.messagebox.askokcancel("Thoát", "Bạn muốn thoát khỏi ứng dụng?"):
            app.destroy()
    app.protocol("WM_DELETE_WINDOW", handle_on_closing_event)

    app.mainloop()