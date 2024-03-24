import socket
import time


class ClientInfo:
    def __init__(self, address):
        self.address = address
        self.last_activity_time = time.time()


clients = {} 


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = '0.0.0.0'
server_port = 9001
server = (server_address, server_port)

sock.bind(server)


timeout = 60 
#def check_nonactive_client():

def get_username(data):
    name_byte_length = int.from_bytes(data[:1], 'big')
    username = data[1:1 + name_byte_length].decode('utf-8')

    return username, name_byte_length

def get_message(data, name_byte_length):
    message = data[1+name_byte_length:].decode('utf-8')
    return message 


def update_client_activity(username, address):
    if username in clients:
        clients[username].last_activity_time = time.time()
    else:
        clients[username] = ClientInfo(address)

def delete_inactive_client(inactive_clients):
    for inactive_client in inactive_clients:
        del clients[inactive_client]
        print('delete {}'.format(inactive_client))


def create_full_message(username, message):
    header = len(username).to_bytes(1, byteorder='big')
    username = username.encode()
    message = message.encode()
    full_message = header + username + message
    print('header: {}, username: {}, message: {}'.format(header, username, message))
    return full_message




while True:
    print('Lissten.........')
    data, address = sock.recvfrom(4096)


    username, name_byte_length = get_username(data)

    update_client_activity(username, address)
    message = get_message(data, name_byte_length)

    print('username: {}, message: {}'.format(username.encode(), message))


    if data:
        # 現在時刻を取得 
        current_time = time.time()

        print('data: {}, address: {}'.format( data.decode(), address))
        inactive_clients = [username for username, info in clients.items() if current_time - info.last_activity_time > timeout]
        delete_inactive_client(inactive_clients)

        for client_username, client_info in clients.items():
            if client_username != username and current_time - client_info.last_activity_time < timeout:

                full_message = create_full_message(username, message) 

                sock.sendto(full_message, client_info.address)
                print('relay {}'.format(client_info.address))


