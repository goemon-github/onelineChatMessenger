import time


class ClientInfo:
    def __init__(self, address=None, username=None, token=None, is_host=False):
        self.address = address
        self.username = username
        self.room_name = ''
        self.token =  token 
        self.password = ''
        self.message = ''
        self.host = is_host 
        self.last_activity_time = time.time()


    def set_username(self, username):
        self.username = username

    def set_room_name(self, room_name):
        self.room_name = room_name

    def set_token(self, token):
        self.token = token

    def set_message(self, message):
        self.message = message

    def set_password(self, password):
        self.password = password


    def get_address(self):
        return self.address

    def get_username(self):
        return self.username

    def get_room_name(self):
        return self.room_name

    def get_password(self):
        return self.password

    def get_last_activity_time(self):
        return self.last_activity_time

    def update_last_activity_time(self, time):
        self.last_activity_time = time