import json

class Tcrp:
    def __init__(self, operaion=0, state='', room_name='', payload=''):
        self.header = '' 
        self.body = ''
        self.operation = operaion 
        self.state = state
        self.room_name = room_name 
        self.payload = payload

    def set_operation(self, operation):
        if isinstance(operation, str) :
            self.operation = int(operation)
        else:
            self.operation = operation

    def set_state(self, state=0):
        self.state = state

    def set_room_name(self, room_name):
        self.room_name = room_name

    def set_payload(self, payload='template payload'):
        self.payload = payload

    def set_body(self):
        self.body = self.room_name + self.payload


    def create_header(self, room_name, operation, state, payload):
        room_name_encoded = room_name.encode('utf-8')
        operation_size = len(payload).to_bytes(29, byteorder='big')
        print('------------tcrp check header-----------')
        print('len: {}, op: {}, state: {}'.format(type(room_name_encoded), type(operation), type(state)))
        header = bytearray([len(room_name_encoded), operation, state, ]) + operation_size

        return header


    def process_header(self):
        self.header = self.create_header(self.room_name, self.operation, self.state, self.payload)

    def porcess_body(self):
        self.body = self.body.encode('utf-8')

    def build_packet(self):
        self.process_header()
        self.set_body()
        self.porcess_body()
        message = self.header + self.body
        return  message