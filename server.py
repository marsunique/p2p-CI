import socket
import threading
import pickle

class ServerNode(object):
    def __init__(self):
        # init server info
        self.HOST_NAME = ''
        self.PORT = 7734
        self.peer_info = {}
        self.rfc_index = {}

    def handleRequest(self, data, conn, addr):
        cmd = data[0]
        if cmd == 'connect':
            # register peer information
            _upload_port = data[1]
            _rfc_num = data[2]
            self.peer_info[addr] = (_upload_port, _rfc_num)
            for _num in _rfc_num:
                self.rfc_index.setdefault(_num, [])
                self.rfc_index[_num].append(addr)

        elif cmd == 'query':
            # send back requested information
            # query has two types: query or query with rfc number
            if len(data) == 1:
                # type 1
                data = pickle.dumps(self.peer_info)
                conn.sendall(data)
            else:
                # type 2
                _rfc_num = data[1]
                if not data[1] in self.rfc_index:
                    # rfc number is not stored in the rfc_index
                    data = pickle.dumps('RFC not available')
                else: 
                    data = pickle.dumps(self.rfc_index[_rfc_num])
                conn.sendall(data)

        elif cmd == 'quit':
            _info = self.peer_info.pop(addr)
            # info = (_upload_port, _rfc_num), _rfc_num is a list
            for _num in _info[1]:
                self.rfc_index[_num].remove(addr)
                if not self.rfc_index[_num]:
                    # index is empty
                    self.rfc_index.pop(_num)




    def connectClient(self, conn, addr):
        print 'Connected by', addr
        while True:
            data = pickle.loads(conn.recv(1024))
            print data
            self.handleRequest(data, conn, addr)
            if data[0] == 'quit':
                break

            
        conn.close()
    
    def main(self):
        # create server socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind((self.HOST_NAME, self.PORT))
        self.serverSocket.listen(1)
        print 'Server is ready to receive message!'

        # accept connection
        while True:
            conn, addr = self.serverSocket.accept()
            t = threading.Thread(target=self.connectClient, args=(conn, addr))
            t.start()
            

if __name__ == '__main__':
    server = ServerNode()
    server.main()
