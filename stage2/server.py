import socket
import time
import json
import threading
import secrets
import struct
import tcrp as Tcrp
import tcrp_parser as Tcrp_parser
import clientInfo as ClientInfo
import chat_rooms as Chat_rooms






class Tcp_server:
    def __init__(self, chat_rooms, clients, host='0.0.0.0', port=9002):
        self.chat_rooms = chat_rooms
        self.host = host
        self.port = port 
        self.sock = self.create_socket() 
        self.tcrp_parser = Tcrp_parser.Tcrp_parser(32)
        self.clients =  clients
        self.receive_parsed_packet_data = {}
        self.INIT_SERVER = 0
        self.RESPONSE_REQUEST = 1
        self.REQEST_CONPLETE = 2



    # run
    def run(self):
        while True:
            connection, self.client_address = self.sock.accept()
            try:
                # receive
                data = connection.recv(4096)
                
                # tcrp parse
                self.tcrp_parser.parse_packet(data)
                _, operation, state, _ = self.tcrp_parser.get_parse_header()
                room_name, payload = self.tcrp_parser.get_parse_body()
                self.set_received_packet_data(operation, state, room_name, payload)
                print(self.receive_parsed_packet_data)
                self.parsed_payload()

                # create responce
                complete_packet = self.process_responce(connection)
                connection.sendall(complete_packet)
                

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

    def create_chat_room(self, client_info):
        chat_room_exists = self.chat_rooms.chat_room_exists(self.receive_parsed_packet_data['room_name'])

        if not chat_room_exists:
            self.chat_rooms.create_room(
                client_info.get_room_name(), 
                client_info, 
                client_info.get_token(),
                client_info.get_password()
                )
            


    # generate
    def generate_token(self):
        token = secrets.token_urlsafe(8)
        return token

    def generate_responce_message_request(self, chat_room_exists):
        if not chat_room_exists:
            message = 'リクエストを受け付けました.....'
            hash_payload = self.generate_responce_payload(message=message)
        else:
            message = 'リクエスト拒否しました....すでに同じ部屋は存在しています'
            hash_payload = self.generate_responce_payload(message=message)

        return hash_payload

    def generate_responce_join(self, chat_room_exists, password_exists, token=None):
        print('----responce join-----')
        print(chat_room_exists)
        print(password_exists)
        if chat_room_exists and password_exists:
            message = 'ルームに参加しました トークンを発行します'
            hash_payload = self.generate_responce_payload(message, token)
        else:
            message = 'ルーム名又はパスワードが違います'
            hash_payload = self.generate_responce_payload(message, token)
        
        return hash_payload 


    def generate_responce_payload(self, message='', token=''):
        hash_payload = {}
        if message:
            hash_payload['message'] = message

        if token:
            hash_payload['token'] = token

        return hash_payload

    def generate_responce(self, tcrp, state, hash_payload):
        res_payload_json = self.encode_payload_json(hash_payload)
        tcrp.set_state(state)
        tcrp.set_payload(res_payload_json)
        complete_packet = tcrp.build_packet() 

        return complete_packet

    # assingn
    def assign_user_token(self):
        token = self.generate_token()
        client_info = self.create_client(self.client_address, self.client_name, token, True)
        self.clients[token] = client_info
        pass


    # parser
    def parsed_payload(self):
        payload = self.receive_parsed_packet_data["payload"]
        payload_json = json.loads(payload)
        self.receive_parsed_packet_data["user_name"] = payload_json['user_name']
        self.receive_parsed_packet_data["udp_address"] =tuple(payload_json['udp_address'])
        self.receive_parsed_packet_data["password"] = payload_json['password']


    # process
    def process_responce(self, connection):
        print('-----check room_name-----')
        print(self.receive_parsed_packet_data['room_name'])
        res_tcrp = Tcrp.Tcrp()

        # operationCodeごとに分ける
        if self.receive_parsed_packet_data['operation'] == 2:
            print('-----process 2------')
            chat_room_exists = self.chat_rooms.chat_room_exists(self.receive_parsed_packet_data['room_name'])
            print('-----check is chat_room_name-----')
            print(chat_room_exists)
            """
            ルームネームの確認
            パスワードの確認
                エラーであれば、エラーで返答「ルームネーム、パスワードいずれかが違います」
            """
            password_exists = self.chat_rooms.room_password_exists(
                self.receive_parsed_packet_data['room_name'],
                self.receive_parsed_packet_data['password'])

            hash_payload = self.generate_responce_join(chat_room_exists, password_exists)

            if chat_room_exists and password_exists:
                """
                クライアントを作成
                トークンを生成
                clientsに追加
                """
                # create_client
                token = self.generate_token()
                print(token)
                client_info = ClientInfo.ClientInfo(
                    self.client_address, 
                    self.receive_parsed_packet_data['udp_address'],
                    self.receive_parsed_packet_data['user_name'],
                    self.receive_parsed_packet_data['room_name'],
                    token= token,
                    is_host=False
                )

                self.clients[token] = client_info

                """
                ルームへの参加
                """
                # room join
                self.chat_rooms.join_room(
                    self.receive_parsed_packet_data['room_name'],
                    client_info
                )

                """
                レスポンスの作成
                    トークンを返す
                    payloadの作成
                        jsonに変換
                """
                # payloadを生成
                hash_payload = self.generate_responce_join(
                    True,
                    True,
                    client_info.get_token()
                )

                # send
                complete_packet = self.generate_responce(res_tcrp, self.REQEST_CONPLETE, hash_payload)
                return complete_packet


            else:
                complete_packet = self.generate_responce(res_tcrp,  self.REQEST_CONPLETE, hash_payload)
                return complete_packet




        elif self.receive_parsed_packet_data['operation'] == 1:
            print('-----process 1------')
            """
            ルームネームがかぶらないか確認
            ルーム作成が可能であれば「リクエストを受け付けました」 
            ルーム作成が不可能であれば「ルームを作成できません」 
            いずれかを返答
            """
            chat_room_exists = self.chat_rooms.chat_room_exists(self.receive_parsed_packet_data['room_name'])
            hash_payload = self.generate_responce_message_request(chat_room_exists)

            # メッセージを送る
            complete_packet = self.generate_responce(res_tcrp, self.RESPONSE_REQUEST, hash_payload)
            connection.sendall(complete_packet)


            """
            クライアントを作成
                クライアントを作成 
                トークンを生成
                clientsに追加
            """
            token = self.generate_token() 
            print('---token---')
            print(token)

            client_info = ClientInfo.ClientInfo(
                self.client_address, 
                self.receive_parsed_packet_data['udp_address'],
                self.receive_parsed_packet_data["user_name"],
                self.receive_parsed_packet_data['room_name'],
                token=token, 
                is_host=True
            )

            client_info.set_password(self.receive_parsed_packet_data['password'])

            self.clients[token] = client_info


            """
            ルームを作成
            """

            # create_room
            self.create_chat_room(client_info)
            room = self.chat_rooms.get_room(client_info.get_room_name())


            # 確認用
            print('----room----')
            print(room)


            """
            レスポンスを作成
                payloadの作成
                    jsonに変換
                tcrpに変換
            """
            # payloadを生成
            hash_payload = self.generate_responce_join(
                True,
                True,
                client_info.get_token()
                )

            # send
            complete_packet = self.generate_responce(res_tcrp, self.REQEST_CONPLETE, hash_payload)

            return complete_packet




    # set
    def set_received_packet_data(self, operation=0, state=0, room_name='', payload=''):
        room_name = self.decode_receive_packet(room_name)
        payload = self.decode_receive_packet(payload)
        self.receive_parsed_packet_data = {
           "operation": operation,
           "state": state,
           "room_name": room_name,
            "payload": payload
        }

    def set_client_info(self):
        pass

    # encode
    def encode_payload_json(self, hash_payload):
        payload_json = json.dumps(hash_payload)

        return payload_json

    # decode
    def decode_receive_packet(self, target):
        target_decode = target.decode('utf-8')
        return target_decode





class Udp_server:
    def __init__(self, chat_rooms, clients, host='0.0.0.0', port=9001, timeout=18000):
        self.chat_rooms = chat_rooms
        self.host = host  
        self.port = port
        self.sock = self.create_socket()
        self.timeout = timeout
        self.clients = clients 

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        print('UDP Listen.............')

        return sock

    def run(self):

        while True:
            data, address = self.sock.recvfrom(4096)
            user_name, name_byte_length = self.get_username(data)

            self.update_client_activity(user_name, address)
            message = self.get_udp_message(data, name_byte_length)

            print('username: {}, message: {}'.format(user_name, message))

            if data:
                    # 現在時刻を取得 
                current_time = time.time()
                print('---check udp  data -----')
                payload = self.udp_parser(data)
                payload_json = json.loads(payload)
                room_name = payload_json['room_name']
                token = payload_json['token']
                message = payload_json['message']
                print('room_name: {}, token: {}, message: {}'
                    .format(payload_json['room_name'], payload_json['token'], payload_json['message']))

                current_client = self.clients[token]

                room = self.chat_rooms.get_room(current_client.get_room_name())

                inactive_cliets = [client_info 
                                  for client_info in room['users']
                                  if current_time - client_info.get_last_activity_time() > self.timeout
                                ]
                
                self.delete_inactive_client(room['room_name'], inactive_cliets)

                active_clients = self.chat_rooms.get_users_from_room(room['room_name'])
                for active_client in active_clients:
                    if current_client.get_token() != active_client.get_token() and current_time - active_client.get_last_activity_time() < self.timeout:

                        full_message = self.create_full_message( message) 
                        print('----------udp send---------')
                        print(full_message)
                        self.sock.sendto(full_message, active_client.get_udp_address())
                        print('user: {} relay {}'.format(active_client.get_user_name(), active_client.get_udp_address()))
                


    def update_timeout(self, timeout):
        self.timeout = timeout

    
    # get
        
    def get_username(self, data):
        name_byte_length = int.from_bytes(data[:1], 'big')
        username = data[1:1 + name_byte_length].decode('utf-8')

        return username, name_byte_length

    def get_udp_message(self, data, name_byte_length):
        message = data[1+name_byte_length:].decode('utf-8')
        return message 

    def get_room_participants(self, room):
        return room['particpants']

    # update
    def update_client_activity(self, username, address):
        if username in self.clients:
            self.clients[username].last_activity_time = time.time()
        else:
            self.clients[username] = ClientInfo.ClientInfo(address)

    def delete_inactive_client(self, room_name, inactive_clients):
        for client in inactive_clients:
            self.chat_rooms.remove_users_from_room(room_name, client)


    def create_full_message(self, message):
        full_message = {"message": message}
        full_message_json = json.dumps(full_message)
        encode_full_message = full_message_json.encode('utf-8')
        print(' message: {}'.format(message))
        return encode_full_message



    def udp_parser(self, data):
        header_size = 2
        print(data.decode('utf-8'))
        body = data[header_size:]
        body = body.decode('utf-8')
        return body



        


if __name__ == '__main__':
    chat_rooms = Chat_rooms.Chatrooms()
    clients = {}

    tcp_server = Tcp_server(chat_rooms, clients)

    udp_server = Udp_server(chat_rooms, clients)

    thread_tcp_server = threading.Thread(target=tcp_server.run)
    thread_udp_server = threading.Thread(target=udp_server.run)

    thread_tcp_server.start()
    thread_udp_server.start()

