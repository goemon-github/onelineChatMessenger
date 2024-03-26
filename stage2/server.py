import socket
import time


class ClientInfo:
    def __init__(self, address):
        self.address = address
        self.last_activity_time = time.time()


class Server:
    def __init__(self, host='0.0.0.0', port=9001, timeout=30) :
        self.host = host  
        self.port = port
        self.sock = self.create_socket()
        self.timeout = timeout
        self.clients = {}

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(self.host, self.port)
        print('Listen.............')

        return sock

    def run(self):
        while True:
            data, address = self.sock.recvfrom(4096)

            username, name_byte_length = self.get_username(data)

            self.update_client_activity(username, address)
            message = self.get_message(data, name_byte_length)

            print('username: {}, message: {}'.format(username.encode(), message))

            if data:
                # 現在時刻を取得 
                current_time = time.time()

                print('data: {}, address: {}'.format( data.decode(), address))
                inactive_clients = [username for username, info in self.clients.items() if current_time - info.last_activity_time > self.timeout]
                self.delete_inactive_client(inactive_clients)

                for client_username, client_info in self.clients.items():
                    if client_username != username and current_time - client_info.last_activity_time < self.timeout:

                        full_message = self.create_full_message(username, message) 

                        self.sock.sendto(full_message, client_info.address)
                        print('relay {}'.format(client_info.address))



    def update_timeout(self, timeout):
        self.timeout = timeout

    
    #def  process_recived_message(data):

        
    def get_username(self, data):
        name_byte_length = int.from_bytes(data[:1], 'big')
        username = data[1:1 + name_byte_length].decode('utf-8')

        return username, name_byte_length

    def get_message(self, data, name_byte_length):
        message = data[1+name_byte_length:].decode('utf-8')
        return message 


    def update_client_activity(self, username, address):
        if username in self.clients:
            self.clients[username].last_activity_time = time.time()
        else:
            self.clients[username] = ClientInfo(address)

    def delete_inactive_client(self, inactive_clients):
        for inactive_client in inactive_clients:
            del self.clients[inactive_client]
            print('delete {}'.format(inactive_client))


    def create_full_message(self, username, message):
        header = len(username).to_bytes(1, byteorder='big')
        username = username.encode()
        message = message.encode()
        full_message = header + username + message
        print('header: {}, username: {}, message: {}'.format(header, username, message))
        return full_message

        


if __name__ == '__main__':
    server = Server()
    server.run()