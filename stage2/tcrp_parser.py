
class Tcrp_parser:
    def __init__(self, header_length):
        self.HEADER_LENGTH = header_length

    def parse_packet(self, data):
        header =  data[:self.HEADER_LENGTH]
        body = data[self.HEADER_LENGTH:]
        self.__parse_header(header)
        self.__parse_body(body)

        """
            print('-----parse packet-----------------')
            self.check_packet(header, body)
            print('----------------------')
        
        """

    def __parse_header(self, header):
        self.room_name_size = int.from_bytes(header[:1], 'big')
        self.operation = int.from_bytes(header[1:2], 'big')
        self.state = int.from_bytes(header[2:3], 'big')
        self.payload_size = int.from_bytes(header[3:], 'big')


    def __parse_body(self, body):
        self.room_name = body[:self.room_name_size]
        self.payload = body[self.room_name_size:]


    def get_parse_header(self):
        return self.room_name_size, self.operation, self.state, self.payload_size

    def get_parse_body(self):
        return self.room_name, self.payload

    def get_operation(self):
        return self.operation

    def get_state(self):
        return self.state

    def get_payload(self):
        return self.payload

    # self check method
    def check_packet(self, header, body):
        print('header---------------')
        name_length = self.check_header(header)

        print('body------------------')
        self.check_body(body.decode(), name_length)

    def check_header(self, header):
        name_length = int.from_bytes(header[:1], 'big')
        operation = int.from_bytes(header[1:2], 'big')
        state = int.from_bytes(header[2:3], 'big')
        payload_size = int.from_bytes(header[3:], 'big')

        print('name_length: {}'.format(name_length))
        print('operation: {}'.format(operation))
        print('state: {}'.format(state))
        print('payload_size: {}'.format(payload_size))
        return name_length


    def check_body(self, body, name_size):
        room_name = body[:name_size]
        payload = body[name_size:]
        print('room_name: {}'.format(room_name))
        print('payload: {}'.format(payload))
