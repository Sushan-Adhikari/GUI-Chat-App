import socket
import threading
import tkinter  #it is the GUI of the python, it's part of core python stack
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1' #if it is hosted then need to specify the public IP
PORT = 9090

#Client is going to be a class
# we need objects

class Client:
    #constructing a default constructor
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        #need a window for the message
        msg = tkinter.Tk()  #makes the message box pop up
        msg.withdraw() #for creating a context

        #ask for nickname in a dialog box
        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg )

        #setting a flag to manipulate the GUI
        self.gui_done = False

        #flag if everything is running
        self.running = True

        #Running the threads, one for the GUI and the other for dealing with the server
        gui_thread = threading.Thread(target = self.gui_loop)
        receive_thread = threading.Thread(target = self.receive)

        gui_thread.start()
        receive_thread.start()
    
    #this is going to create the frontend
    #creating the buttons and other stuff
    def gui_loop(self):
        self.win = tkinter.Tk() #returns a toplevel widget
        self.win.configure(bg="lightgray")

        #setting the label to have a lightgray background, otherwise it will be white
        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray") #individual component
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        #we want to have the text area now to see the chat history
        #self.win defines that the widget is to be used
        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        #Defining that the messages in the history area can't be edited
        self.text_area.config(state='disabled') #consequence: can't alter the stylings of the messages in the history
        #need to make it default(enable) again to style it

        #Label for message area
        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray") #individual component
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        #Area for the message
        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        #For the send button
        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        #setting the flag of the GUI to done
        self.gui_done = True

        #To define what to do after we close the  window
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop() #calls the mainloop of Tk

    #write function defined
    def write(self):
        #we can set the nickname from the client side as well as server side
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}" #1.0 meaning starting from the beginning of the text to the end

        #send the message through the socket
        self.sock.send(message.encode('utf-8'))

        #After entering need to clear the text box
        self.input_area.delete('1.0', 'end')

    #function for stopping(what to do when widget is closed)
    def stop(self):
        #set running flag to false
        self.running = False

        #destroy the tkinter widget after the main loop updates
        self.win.after(1, self.win.destroy)

        #close the socket
        self.sock.close()

        #exit
        exit(0)
    #Function for dealing with the server
    def receive(self):
        
        #while the gui is running
        while self.running:
            try:
                #receive a message from the server via socket
                message = self.sock.recv(1024).decode('utf-8')

                #if the server is asking for nickname
                if message == "Nickname: ":
                    self.sock.send(self.nickname.encode('utf-8'))
                
                #if it isn't asking for nickname
                else:

                    #if gui is all loaded
                    if self.gui_done:
                        #change the state of the text_area to normal
                        self.text_area.config(state='normal')

                        #insert the message that the client has typed at the end
                        self.text_area.insert('end', message)

                        #Always scroll down to the end
                        self.text_area.yview('end')
                        
                        #Need to disable the text_area again
                        self.text_area.config(state='disabled')

            except ConnectionAbortedError:
                #if connection is aborted
                break
            except:
                #any other type of error
                print("Error")

                #close the socket
                self.sock.close()

                break

#making an object
client = Client(HOST, PORT)


