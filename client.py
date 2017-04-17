import socket
import threading
import pickle
import random

class ClientNode(object):
    def __init__(self, server_name):
        # init server info
        #SERVER_NAME = socket.gethostname()
        self.SERVER_NAME = server_name
        self.SERVER_PORT = 7734
        self.SERVER_ADDR = socket.gethostbyname(self.SERVER_NAME)
        self.UPLOAD_PORT = 60000 + random.randint(1,500)
        self.mainSocket = None
        print 'server name: ' + self.SERVER_NAME + \
                '\nserver address: ' + self.SERVER_ADDR + \
                '\nserver port: ' + str(self.SERVER_PORT)
    
    def connectServer(self):
        # create client socket
        self.mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mainSocket.connect((self.SERVER_NAME, self.SERVER_PORT))
        print 'Server is connected!'
        # provide rfc numbers that are available
        nums = raw_input("Please provide RFC numbers (separated by ','): ")
        nums = nums.split(',')
        rfc_num = []
        for _num in nums:
            _num = _num.strip()
            rfc_num.append(_num)
        data = pickle.dumps(['connect', self.UPLOAD_PORT, rfc_num])
        # data = [cmd, upload_port, rfc_num]
        self.mainSocket.send(data)

    def queryServer(self, cmd):
        cmd = cmd.strip()
        cmd = cmd.split(' ')
        print cmd
        if not self.mainSocket:
            print 'Error. Connect the server first!'
            return
        data = pickle.dumps(cmd)
        self.mainSocket.send(data)
        # receive query response
        recv_data = pickle.loads(self.mainSocket.recv(1024))
        print recv_data
    
    def tcpClose(self):
        self.mainSocket.close()

    def main(self):
        while True:
            cmd = raw_input('Please enter your command: ')
            '''
            cmd has types:
            1. connect (provide register info)
                - data format: ['connect', upload_port, rfc_num]
            2. download (provide RFC number)
                - data format: ['download', self_defined_protocol]
            3. query
                -data format: ['query', rfc_num(optional)]
            4. quit
                -data format: ['quit']
            '''
            if cmd == 'connect':
                self.connectServer()
            if 'query' in cmd:
                self.queryServer(cmd)
            if cmd == 'quit':
                self.mainSocket.send(pickle.dumps(['quit']))
                self.tcpClose()
                print 'Connection terminated'
                break


if __name__ == '__main__':
    client = ClientNode('localhost')
    client.main()

