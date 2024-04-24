import socket
import json
import threading
import struct
import math
import random
import tcrp as Tcrp
import tcrp_parser as Tcrp_parser
import clientInfo as ClientInfo


class Client:
    def __init__(self):
        self.tcp_server = ''
        self.udp_server = ''
        self.udp_sock = self.create_udp_socket() 
        self.tcp_sock = self.create_tcp_socket()

    def create_tcp_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

    def create_udp_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        return sock

    def run(self):
        # create clientInfo
        self.client_info = ClientInfo.ClientInfo(tcp_address='127.0.0.1')

        #TCP
        self.tcp_server = self.input_server(self.client_info.get_tcp_address(), 9002)
        self.tcp_sock.connect((self.tcp_server))
        print('----------接続しました----------')
        print(self.udp_sock.getsockname())        
        tcrp_packet = self.create_tcrp_packet()
        self.tcp_sock.sendall(tcrp_packet)
        print('----------送信しました----------')



        self.receive_tcrp_packet()
        print('----------受信しました----------')

        self.tcp_sock.close()
        print('----------tcp server close----------')

        # UDP
        print('----------chat start----------')
        self.start_chat()



    # input
    def input_server(self, address='127.0.0.1', port=9001):
        server_address = address
        server_port = port 
        server = (server_address, server_port)
        return server


    def input_username(self):
        while True:
            username = input('username: ')
            username_encoded = username.encode('utf-8')

            if len(username_encoded) <  255:
                break
            else:
                raise ValueError('over username 255')

        return username


    def input_password(self):
        while True:
            password = input('password: ')
            password_encoded = password.encode('utf-8')
            if len(password_encoded) < 4096:
                break
            else:
                print('error: password oversize')
        
        return password



    def input_operation_code(self):
        while True:
            code = input('1: create chatroom, 2: join chatroom : ')

            if code in ['1', '2']:
                code = int(code)
                break
            else:
                print('error!! 1 or 2')

        return code

    def input_chatroom_name(self):
        MAX_SIZE = 256
        while True:
            chatroom_name = input('chatRoom name: ')
            byte_chatroom_name = chatroom_name.encode('utf-8')
            if len(byte_chatroom_name) > MAX_SIZE:
                print('error over size')
            else:
                break

        return chatroom_name

    def input_message(self):
        while True:
            message = input('you: ')
            message_encoded = message.encode('utf-8')

            if len(message_encoded) < 4096:
                break
            else:
                print('error: message oversize')

        return message



    # create
    def create_udp_packet(self, room_name, token, message):
        #header = len(room_name).to_bytes(1, byteorder='big')
        header = struct.pack('BB', len(room_name), len(token))
        json_payload = json.dumps({'room_name': room_name,'token': token, 'message': message})
        body = json_payload.encode('utf-8')
        #full_message = header + username.encode() + message.encode()
        full_message = header + body
        return full_message


    def create_tcrp_packet(self):
        # input

        get_user_name = self.input_username()
        self.client_info.set_user_name(get_user_name)

        room_name = self.input_chatroom_name()
        self.client_info.set_room_name(room_name)

        operation_code = self.input_operation_code()
        password = self.input_password()
        self.client_info.set_password(password)
        self.client_info.set_udp_address(self.udp_sock.getsockname())
        payload_json = self.encode_payload_to_json()
        print(payload_json)

        # create tcrp packet
        tcrp = Tcrp.Tcrp()
        self.set_tcrp_header(tcrp, self.client_info.get_room_name(), operation_code, state=0)
        tcrp.set_payload(payload_json)

        tcrp_message = tcrp.build_packet()        

        return tcrp_message

    # encode
    def encode_payload_to_json(self):
        payload = {
            'user_name': self.client_info.get_user_name(),
            'udp_address': self.client_info.get_udp_address(),
            'password' : self.client_info.get_password()
        }

        payload_json = json.dumps(payload)

        return payload_json


    # get
    def get_username(self, data):
        name_byte_length = int.from_bytes(data[:1], 'big')
        data = data.decode('utf-8')
        username = data[1:1 + name_byte_length]

        return username ,name_byte_length

    def get_udp_message(self, data):
        data = data.decode()
        print(data)
        message = data['message']
        return message 


    def get_token_from_payload(self, payload):
            payload = payload.decode()
            parse_json_payload = json.loads(payload)
            self.client_info.set_token(parse_json_payload['token'])

    def get_udp_message_from_payload(self, payload):
            payload = payload.decode('utf-8')
            res_message = json.loads(payload)['message']
            return res_message


    # set
    def set_tcrp_header(self, tcrp, chatroom_name, operation, state):
        tcrp.set_room_name(chatroom_name)
        tcrp.set_operation(operation)
        tcrp.set_state(state)

    # send
    def send_udp_packet(self):
        target_server = ('127.0.0.1', 9001)
        while True:
            message = self.input_message()
            self.client_info.set_chat_message(message)

            '''
            header: RoomNameSize（1 バイト）| TokenSize（1 バイト）
            body:   RoomNameSize バイトはルーム名 |  TokenSize バイトはトークン文字列 | message
            '''
            full_message = self.create_udp_packet(
                self.client_info.get_room_name(), 
                self.client_info.get_token(), 
                self.client_info.get_chat_message()
            )

            if full_message:
                self.udp_sock.sendto(full_message,  target_server)


    # receive
    def receive_udp_packet(self):
        print('----receive_udp_packet')
        while True:
                data, _ = self.udp_sock.recvfrom(4096)
                if data:
                    self.udp_parser(data)


    def receive_tcrp_packet(self):
        tcrp_parser = Tcrp_parser.Tcrp_parser(32)
        while True: 
            try:
                responce = self.tcp_sock.recv(4096)
                tcrp_parser.parse_packet(responce)
                state = tcrp_parser.get_state()
                payload = tcrp_parser.get_payload()
                if state == 2:
                    self.get_token_from_payload(payload)
                    res_message = self.get_udp_message_from_payload(payload)
                    print('message: {}'.format(res_message))
                    print('token: {}'.format(self.client_info.get_token()))
                    break

                elif state == 1:
                    res_message = self.get_udp_message_from_payload(payload)
                    print('---responce message-----')
                    print(res_message)

            except self.tcp_sock.timeout:
                print('recv: time out')
                break
                

            
            finally:
                pass

    # udp parser
    def udp_parser(self, data):
        data = data.decode('utf-8')
        data_json = json.loads(data) 
        print('user: {}'.format(data_json['message']))

    # Udp_Chat_start
    def start_chat(self):
        # port　ramdom
        '''
        port = int(random.uniform(9003, 9100))
        print('----port---')
        print(port)
        '''

        thread_send = threading.Thread(target=self.send_udp_packet)
        thread_receive = threading.Thread(target=self.receive_udp_packet)

        thread_send.start()
        thread_receive.start()



if __name__ == '__main__':
    client = Client()
    client.run()