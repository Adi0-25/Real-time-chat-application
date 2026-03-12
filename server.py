import socket
import threading
import os

# Store connected users: {username: connection_object}
clients = {}
# Store multicast groups: {group_name: [username1, username2]}
groups = {}

def handle_client(conn, addr):
    # First message received is the username
    try:
        username = conn.recv(1024).decode('utf-8')
        clients[username] = conn
        print(f"{username} connected from {addr}")
        broadcast(f"[Server] {username} has joined the chat!", "Server")
    except:
        conn.close()
        return

    # Listen for messages from this user
    while True:
        try:
            message = conn.recv(1024).decode('utf-8')
            if not message or message.lower() == 'quit':
                break
            
            # 1. UNICAST (Send to one specific user)
            # Format: @username message
            if message.startswith('@'):
                parts = message.split(' ', 1)
                if len(parts) > 1:
                    target_user = parts[0][1:] # Remove the '@'
                    msg_content = parts[1]
                    unicast(f"[Private from {username}]: {msg_content}", target_user, conn)
            
            # 2. JOIN A GROUP (For Multicast)
            # Format: /join groupname
            elif message.startswith('/join '):
                group_name = message.split(' ', 1)[1]
                if group_name not in groups:
                    groups[group_name] = [] # Create group if it doesn't exist
                if username not in groups[group_name]:
                    groups[group_name].append(username)
                conn.send(f"[Server] You joined group '{group_name}'\n".encode('utf-8'))

            # 3. MULTICAST (Send to a specific group)
            # Format: !groupname message
            elif message.startswith('!'):
                parts = message.split(' ', 1)
                if len(parts) > 1:
                    group_name = parts[0][1:] # Remove the '!'
                    msg_content = parts[1]
                    multicast(f"[Group {group_name} - {username}]: {msg_content}", group_name, username, conn)
            
            # 4. BROADCAST (Send to everyone)
            # Format: just type the message
            else:
                broadcast(f"[{username}]: {message}", username)

        except:
            break

    # Cleanup when user disconnects
    if username in clients:
        del clients[username]
    for group in groups.values():
        if username in group:
            group.remove(username)
    conn.close()
    broadcast(f"[Server] {username} has left the chat.", "Server")

def unicast(message, target_user, sender_conn):
    if target_user in clients:
        clients[target_user].send(message.encode('utf-8'))
    else:
        sender_conn.send(f"[Server] User '{target_user}' not found.\n".encode('utf-8'))

def multicast(message, group_name, sender_username, sender_conn):
    if group_name in groups:
        for user in groups[group_name]:
            if user != sender_username and user in clients:
                clients[user].send(message.encode('utf-8'))
    else:
        sender_conn.send(f"[Server] Group '{group_name}' not found.\n".encode('utf-8'))

def broadcast(message, sender_username):
    for user, conn in clients.items():
        if user != sender_username:
            try:
                conn.send(message.encode('utf-8'))
            except:
                pass

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 9999))
    server_socket.listen(5) # Allow multiple users to connect
    
    print("Server is running on 127.0.0.1:9999...")
    print("Waiting for users to connect...")
    
    while True:
        conn, addr = server_socket.accept()
        # Create a new thread for every user that connects
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()