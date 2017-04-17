import socket
import threading
import pickle

class ServerNode(object):
    def __init__(self):
        # init server info
        self.HOST_NAME = ''
        self.PORT = 7734
        self.peer_list = []
        self.rfc_index = {}

    def handleRequest(self, data):
        cmd = data[0]


    def connectClient(self, conn, addr):
        print 'Connected by', addr
        while True:
            data = pickle.loads(conn.recv(1024))
            print data
            if data[0] == 'quit':
                break
            else:
                self.handleRequest(data)

            
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
