import socket



def input_username():
    while True:
        username = input('username: ')
        username_encoded = username.encode('utf-8')

        if len(username_encoded) <  255:
            break
        else:
            raise ValueError('over username 255')

    return username_encoded


def input_message():
    while True:
        message = input('message: ')
        message_encoded = message.encode('utf-8')

        if len(message_encoded) < 4096:
            break
        else:
            print('error: message oversize')
    return message_encoded


def create_message(username, message):
    header = len(username).to_bytes(1, byteorder='big')
    full_message = header + username + message
    return full_message


def get_username(data):
    name_byte_length = int.from_bytes(data[:1], 'big')
    data = data.decode('utf-8')
    username = data[1:1 + name_byte_length]

    return username ,name_byte_length

def get_message(data, name_byte_length):
    data = data.decode('utf-8')
    message = data[1+name_byte_length:]
    return message 




sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


server_address = '127.0.0.1'
server_port = 9001
server = (server_address, server_port)

print('connecting to {}'.format(server_address, server_port))


username = input_username()

while True:
    message = input_message()
    full_message = create_message(username, message)

    print('send Massge {} '.format(full_message))
    #print('send Massge {} '.format(full_message.decode()))

    sent = sock.sendto(full_message,  server)
    print('sent to byte {}'.format(sent))

    # レシーバーの実装
    data, server = sock.recvfrom(4096)

    if data:
        responce_username, responce_name_byte_length = get_username(data)
        responce_message = get_message(data, responce_name_byte_length)

        print('server: {}, username: {}\n, message: {}'.format( server, responce_username, responce_message))


   
   
