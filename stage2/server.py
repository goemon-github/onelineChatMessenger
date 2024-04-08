import socket
import time
import json
import hashlib
import secrets
import tcrp as Tcrp
import tcrp_parser as Tcrp_parser
import clientInfo as ClientInfo
import chat_rooms as Chat_rooms






class TcpServer:
    def __init__(self, chat_rooms, host='0.0.0.0', port=9002):
        self.chat_rooms = chat_rooms
        self.host = host
        self.port = port 
        self.sock = self.create_socket() 
        self.tcrp_parser = Tcrp_parser.Tcrp_parser(32)
        self.clients = {}
        self.INIT_SERVER = 0
        self.RESPONSE_REQUEST = 1
        self.REQEST_CONPLETE = 2



    # run
    def run(self):
        while True:
            print('run')
            connection, self.client_address = self.sock.accept()
            try:
                data = connection.recv(4096)
                self.tcrp_parser.parse_packet(data)

                self.room_name, self.operation, self.state, self.payload_size = self.tcrp_parser.get_parse_header()
                self.room_name, self.payload = self.tcrp_parser.get_parse_body()
                print('receive: ')
                print(self.room_name, self.operation, self.state, self.payload_size )
                print(self.room_name, self.payload)


                # test#
                res = self.process_responce()
                print(res)
                tcrp = Tcrp.Tcrp(state= 1 , operation_payload=res)
                message = tcrp.build_packet()
                print('message: ')
                print(message)

                connection.sendall(message)
                

            finally:
                print('closing tcp server')
                connection.close()


    # create
    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(1)
        print('tcp Listen.................')
        return sock


    def create_client(address, user_name, is_host, token=None):
        client_info = ClientInfo.ClientInfo(address, user_name, token, is_host)
        return client_info


    def create_chat_room(self):
        if self.chat_room_exists():
            token = self.generate_token()
            client_info = self.create_client(self.client_address, self.room_name, True, token)
            self.clients[token] = client_info
            self.chat_rooms.create_room(self.room_name, client_info, token)
            


    # generate
    def generate_token(self):
        token = secrets.token_urlsafe(8)
        return token

    def generate_responce_message_reqest(self,  boolean):
        if boolean:
            message = 'リクエストを受け付けました.....'
        else:
            message = 'リクエスト拒否しました....すでに同じ部屋は存在しています'

        return message

    def generate_responce_join(self,  boolean):
        responce_tcrp = Tcrp.Tcrp(operaion=2,state=2, room_name=self.room_name)
        
        pass

    # assingn
    def assign_user_token(self):
        token = self.generate_token()
        client_info = self.create_client(self.client_address, self.client_name, token, True)
        self.clients[token] = client_info
        pass


    # process
    def process_responce(self):
        chat_room_exitsts = self.chat_rooms.chat_room_exists(self.room_name)
        res_tcrp = Tcrp.Tcrp()

        if self.operation == 2:
            # join
            pass
        elif self.operation == 1:
            # create_room
            print('---process_responce-----')
            message = self.generate_responce_message_reqest(chat_room_exitsts)
            # json形式にする
            payload_json = self.encode_responce_json(message) 
            if not chat_room_exitsts:
                pass

            return payload_json 

    # encode
    def encode_responce_json(self, message):
        payload = {
            'message': message
        }
        payload_json = json.dumps(payload)

        return payload_json





class UdpServer:
    def __init__(self, chat_rooms, host='0.0.0.0', port=9001, timeout=30) :
        self.chat_rooms = chat_rooms
        self.host = host  
        self.port = port
        self.sock = self.create_socket()
        self.timeout = timeout
        self.clients = {}

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
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
            self.clients[username] = ClientInfo.ClientInfo(address)

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


    def create_chatromm(self):
        pass

    def connection_chatroom(self):
        pass

    def create_client_token(self):
        pass

        


if __name__ == '__main__':
    chat_rooms = Chat_rooms.Chatrooms()

    tcpServer = TcpServer(chat_rooms)
    tcpServer.run()


    #udpServer = UdpServer()
    #udpServer.run()