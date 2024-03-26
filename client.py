import socket


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = self.input_server()
        self.username = self.input_username()
        self.message = self.input_message()


    def run(self):
        print('connecting to {}'.format(self.server['address'], self.server['port']))
        while True:
            full_message = self.create_message(self.username, self.message)

            print('send Massge {} '.format(full_message))

            sent = self.sock.sendto(full_message,  self.server)
            print('sent to byte {}'.format(sent))

            # レシーバーの実装
            responce_data, responce_server = self.sock.recvfrom(4096)

            if responce_data:
                responce_username, responce_name_byte_length = self.get_username(responce_data)
                responce_message = self.get_message(responce_data, responce_name_byte_length)

                print('server: {}, username: {}\n, message: {}'.format( responce_server, responce_username, responce_message))


    def input_server(self):
        server_address = '127.0.0.1'
        server_port = 9001
        server = {'address': server_address, 'port': server_port}
        return server


    def input_username(self):
        while True:
            username = input('username: ')
            username_encoded = username.encode('utf-8')

            if len(username_encoded) <  255:
                break
            else:
                raise ValueError('over username 255')

        return username_encoded


    def input_message(self):
        while True:
            message = input('message: ')
            message_encoded = message.encode('utf-8')

            if len(message_encoded) < 4096:
                break
            else:
                print('error: message oversize')
        return message_encoded


    def create_message(self, username, message):
        header = len(username).to_bytes(1, byteorder='big')
        full_message = header + username + message
        return full_message


    def get_username(self, data):
        name_byte_length = int.from_bytes(data[:1], 'big')
        data = data.decode('utf-8')
        username = data[1:1 + name_byte_length]

        return username ,name_byte_length

    def get_message(self, data, name_byte_length):
        data = data.decode('utf-8')
        message = data[1+name_byte_length:]
        return message 



if __name__ == '__main__':
    client = Client()
    client.run()