import socket
import threading
import os

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[Server disconnected]")
                os._exit(0)
            print(f"\n{message}")
        except:
            print("\n[Connection closed]")
            os._exit(0)

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect(('127.0.0.1', 9999))
    except ConnectionRefusedError:
        print("Could not connect to the server. Is it running?")
        return
        
    # Ask for username upon connecting
    username = input("Enter your username (e.g., User1, User2): ")
    client_socket.send(username.encode('utf-8'))
    
    print("\n--- CHAT INSTRUCTIONS ---")
    print("1. Broadcast (All) : Just type your message")
    print("2. Unicast (One)   : Type @username your_message")
    print("3. Join Group      : Type /join groupname")
    print("4. Multicast (Grp) : Type !groupname your_message")
    print("5. Quit            : Type quit")
    print("-------------------------\n")
    
    # Thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.daemon = True
    receive_thread.start()
    
    # Main thread to send messages
    while True:
        try:
            message = input()
            if message.lower() == 'quit':
                client_socket.send('quit'.encode('utf-8'))
                break
            client_socket.send(message.encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            break
            
    client_socket.close()
    os._exit(0)

if __name__ == "__main__":
    start_client()