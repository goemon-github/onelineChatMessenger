import time


class ClientInfo:
    def __init__(self, tcp_address=None, udp_address=None, user_name=None, room_name='', token=None, is_host=False):
        self.tcp_address = tcp_address
        self.udp_address =udp_address
        self.user_name = user_name
        self.join_room_name = room_name 
        self.token =  token 
        self.password = ''
        self.chat_send_message = ''
        self.host = is_host 
        self.last_activity_time = time.time()


    def set_user_name(self, user_name):
        self.user_name = user_name

    def set_room_name(self, room_name):
        self.join_room_name = room_name

    def set_token(self, token):
        self.token = token

    def set_chat_message(self, message):
        self.chat_send_message = message

    def set_password(self, password):
        self.password = password
    
    def set_udp_address(self, address):
        self.udp_address = address


    def get_tcp_address(self):
        return self.tcp_address

    def get_udp_address(self):
        return self.udp_address

    def get_user_name(self):
        return self.user_name

    def get_room_name(self):
        return self.join_room_name

    def get_token(self):
        return self.token

    def get_password(self):
        return self.password
    
    def get_chat_message(self):
        return self.chat_send_message

    def get_last_activity_time(self):
        return self.last_activity_time

    def update_last_activity_time(self, time):
        self.last_activity_time = time