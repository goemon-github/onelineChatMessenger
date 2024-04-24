class Room:
    MAX_USERS = 5

    def __init__(self, host, password, token):
        self.host = host
        self.users = set([self.host])
        self.password = password
        self.token = token
        

    def get_users(self):
        return self.users

    def get_token(self):
        return self.token

    def join_room(self, user):
        self.users.add(user)
    
    def remove_user_from_room(self, user):
        self.users.remove(user)
    
    def room_password_exists(self, reqest_password):
        return self.password == reqest_password

