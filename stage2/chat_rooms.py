
class Chatrooms:
    def __init__(self ):
        self.rooms = {}
        self.max_users = 5

    def create_room(self, room_name, host_info, token, password=''):
        if room_name not in self.rooms:
            self.rooms[room_name] ={
                'room_name': room_name,
                'host': host_info,
                'users': set([host_info]),
                'password': password,
                'token': token,
                'max_users': self.max_users
            }

    def join_room(self, room_name, user_info):
        if room_name in self.rooms:
            self.rooms[room_name]['users'].add(user_info)
    
    def remove_user_from_room(self, room_name, user_info):
        if room_name in self.rooms:
            self.rooms[room_name]['users'].remove(user_info)

    def get_room(self, room_name):
        if room_name in self.rooms:
            print(self.rooms[room_name])
            return self.rooms[room_name]
    
    def get_users_from_room(self, room_name):
        room = self.get_room(room_name)
        return room['users']

    def get_token(self, room_name, token):
        room = self.get_room(room_name)
        return room[token]
    
    def get_active_users(self, room_name):
        room = self.get_room(room_name)
        users = room['users']
        return users

    
    def chat_room_exists(self, room_name):
        return  room_name in self.rooms

    def room_password_exists(self, room_name, request_password):
        room = self.get_room(room_name)
        return room['password'] == request_password
