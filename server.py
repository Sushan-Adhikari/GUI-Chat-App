# For the server we do not need GUI
# Server only accepts the connection
# It just broadcasts messages

import socket
import threading

# for using it over the internet, specify your private IP(from ipconffig or ifconfig)
HOST = '127.0.0.1'
# For connecting from a user you need your public IP
# can find it in myip.is
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))  # we need a tuple here

server.listen()

clients = []  # empty list of clients at first
nicknames = []  # nicknames for client to chat

# we need to run three different functions in parallel(multithreading)

# The first one broadcasts the messages to all the connected users


def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))

# Another function will define how to handle the client once connected


def handle(client):
    while True:
        try:
            # If the client is connected then
            message = client.recv(1024).decode('utf-8')
            # since the nicknames and clients are on the same index in their respective tuples
            print(f"{nicknames[clients.index(client)]} says {message}")
            broadcast(f'{nicknames[clients.index(client)]}: {message}')
        except:
            # If the client gets disconnected or any error occurs
            index = clients.index(client)
            # remove the client
            clients.remove(client)
            # close the connection from the client
            client.close()

            # now remove the nickname
            nickname = nicknames[index]
            print(f"{nickname} has left the chat!")
            nicknames.remove(nickname)
            break


# Another function would continuously listen for new connections
# It would receive connections
# It has to run on the main thread as once receiving connections is stopped, other threads should also be stopped
def receive():
    while True:
        # The server has to accept new connections continuously
        client, address = server.accept()
        # we establish a socket with the client
        # The client is the socket and address is address of the connection
        # address has to be typecasted to string
        print(f"Connected with{str(address)}")
        # whenever we send something from the server we send it to the client via the socket
        client.send("Nickname: ".encode('utf-8'))
        # receiving 1024 bytes as a response from the client
        nickname = client.recv(1024).decode('utf-8')
        # need to include the nickname of the client in the  nicknames tuple
        nicknames.append(nickname)
        # Also need to know the socket for the connection
        clients.append(client)
        # notice one thing that the nickname and client end up in their respective tuple in the same position
        # we can use index to see which nickname belongs to which client

        # Displaying the nickname of the client
        print(f"Nickname of the client is: {nickname}")
        # Let others know that a person  with a specific nickname has joined the chat
        # broadcast(f"{nickname} connected to the server!\n")
        # Just an acknowledgement to the respective client by the server
        client.send("connected to the server.".encode('utf-8'))

        # now it is time to send the client to the handle function
        # using threading for this purpose
        # The reason for comma is that it requires a tuple
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server running.....")
receive()
