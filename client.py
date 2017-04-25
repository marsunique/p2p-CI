import socket
import threading
import pickle
import random
import time
import sys
import platform

class ClientNode(object):
    def __init__(self, server_name):
        # init server info
        #SERVER_NAME = socket.gethostname()
        self.SERVER_NAME = server_name
        self.SERVER_PORT = 7734
        self.SERVER_ADDR = socket.gethostbyname(self.SERVER_NAME)
        # init upload hostname and port
        self.UPLOAD_HOSTNAME = socket.gethostname()
        self.UPLOAD_PORT = 60000 + random.randint(1,500)
        # init sockets
        self.mainSocket = None
        self.uploadSocket = None
        self.downloadSocket = None
        print 'server name: ' + self.SERVER_NAME + \
                '\nserver address: ' + self.SERVER_ADDR + \
                '\nserver port: ' + str(self.SERVER_PORT) + \
                '\nupload hostname: ' + self.UPLOAD_HOSTNAME + \
                '\nupload port: ' + str(self.UPLOAD_PORT)
        # init upload listen thread stop flag
        self.client_isStop = False

    def quitUploadListen(self):
        _tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _tempSocket.connect((self.UPLOAD_HOSTNAME, self.UPLOAD_PORT))
        data = 'QUIT\n'
        _tempSocket.sendall(data)
        time.sleep(1)
        _tempSocket.close()

    def uploadConnect(self, conn, addr):
        recv_data = conn.recv(1024)
        if recv_data[:4] == 'QUIT':
            conn.close()
        else:
            print '\nDownload request:'
            print recv_data,
            print 'From', addr
            conn.sendall(recv_data.upper())
            conn.close()
    
    def uploadListen(self):
        # create upload socket
        self.uploadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.uploadSocket.bind((self.UPLOAD_HOSTNAME, self.UPLOAD_PORT))
        self.uploadSocket.listen(1)
        print '\nReady to upload'
        # accept connection
        while not self.client_isStop:
            conn, addr = self.uploadSocket.accept()
            t_uploadConnect = threading.Thread(target=self.uploadConnect, args=(conn, addr))
            t_uploadConnect.start()
        # wait
        t_uploadConnect.join()
        self.uploadSocket.close()
        print '\nUpload is closed'




    def downloadPeer(self):
        rfc_num = raw_input("Please provide RFC number you wish to download: ")
        host_name = raw_input("Please provide hostname from which you wish to download: ")
        peer_upload_port = raw_input("Please provide the upload port: ")
        os_info = platform.platform()
        # prepare data
        line_1 = 'GET RFC %s P2P-CI/1.0\n' % (rfc_num)
        line_2 = 'Host: %s\n' % (host_name)
        line_3 = 'OS: %s\n' % (os_info)
        data = line_1 + line_2 + line_3
        # build connection
        self.downloadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.downloadSocket.connect((host_name, int(peer_upload_port)))
        self.downloadSocket.sendall(data)
        print 'Download request is sent!'
        recv_data = self.downloadSocket.recv(1024)
        print '-------Received--------'
        print recv_data
        self.downloadSocket.close()


    def connectServer(self):
        # create client socket
        self.mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mainSocket.connect((self.SERVER_NAME, self.SERVER_PORT))
        print 'Server is connected!'
        data = 'CONNECT %s\n' % (str(self.UPLOAD_PORT))
        self.mainSocket.sendall(data)

    def addSever(self):
        # provide rfc numbers that are available
        num = raw_input("Please provide RFC number: ")
        title = raw_input("RFC title: ")
        # format request data
        line_1 = 'ADD RFC %s P2P-CI/1.0\n' % (num)
        line_2 = 'Host: %s\n' % (socket.gethostname())
        line_3 = 'Port: %s\n' % (self.UPLOAD_PORT)
        line_4 = 'Title: %s\n' % (title)
        data = line_1+line_2+line_3+line_4
        self.mainSocket.sendall(data)
        # receive add response
        recv_data = self.mainSocket.recv(1024)
        print recv_data


    def queryServer(self):
        data = 'QUERY\n'
        self.mainSocket.sendall(data)
        # receive query response
        recv_data = pickle.loads(self.mainSocket.recv(1024))
        print recv_data

    def lookupServer(self):
        num = raw_input("Please provide RFC number: ")
        title = raw_input("RFC title: ")
        # format request data
        line_1 = 'LOOKUP RFC %s P2P-CI/1.0\n' % (num)
        line_2 = 'Host: %s\n' % (socket.gethostname())
        line_3 = 'Port: %s\n' % (self.UPLOAD_PORT)
        line_4 = 'Title: %s\n' % (title)
        data = line_1+line_2+line_3+line_4
        self.mainSocket.sendall(data)
        # receive lookup response
        recv_data = self.mainSocket.recv(1024)
        print recv_data

    def listServer(self):
        # format request data
        line_1 = 'LIST ALL P2P-CI/1.0\n'
        line_2 = 'Host: %s\n' % (socket.gethostname())
        line_3 = 'Port: %s\n' % (self.UPLOAD_PORT)
        data = line_1+line_2+line_3
        self.mainSocket.sendall(data)
        # receive lookup response
        recv_data = self.mainSocket.recv(1024)
        print recv_data

    def quitServer(self):
        data = 'QUIT\n'
        self.mainSocket.sendall(data)

    def testSever(self):
        cmd = raw_input("Choose test type (bad or version): ")
        if cmd == 'bad':
            data = 'BAD P2P-CI/1.0\n'
        else:
            data = 'BAD P2P-CI/2.0\n'
        self.mainSocket.sendall(data)
        recv_data = self.mainSocket.recv(1024)
        print recv_data
    
    def tcpClose(self):
        self.mainSocket.close()

    def main(self):
        # create a thread to deal with upload socket
        t_uploadListen = threading.Thread(target=self.uploadListen, args=())
        t_uploadListen.start()

        time.sleep(0.5)
        while True:
            cmd = raw_input('Please enter your command: ')
            '''
            cmd has types:
            1. connect
                - data format: 'CONNECT UPLOAD_PORT\n'
            2. add
                - data format: P2S application layer protocol
            3. query
                - data format: 'QUERY\n'
            4. lookup
                - data format: P2S application layer protocol
            5. list
                - data format: P2S application layer protocol
            6. quit
                - data format: 'QUIT\n'
            7. download
                - this cmd doesn't need to be transmited to server, handled locally
            '''
            if cmd == 'download':
                self.downloadPeer()
            elif cmd == 'connect':
                if not self.mainSocket:
                    self.connectServer()
                else:
                    print 'You have already connected the server'
            else:
                if not self.mainSocket:
                    print 'Error. Connect the server first!'
                    continue
                elif cmd == 'add':
                    self.addSever()
                elif cmd == 'query':
                    self.queryServer()
                elif cmd == 'lookup':
                    self.lookupServer()
                elif cmd == 'list':
                    self.listServer()
                elif cmd == 'quit':
                    self.client_isStop = True
                    self.quitServer()
                    self.quitUploadListen()
                    self.tcpClose()
                    print 'Connection terminated'
                    break
                # elif cmd == 'test':
                #     self.testSever()
                # elif cmd == 'download':
                #     self.downloadPeer()

                else:
                    print 'Error. Invalid Command!'


if __name__ == '__main__':
    client = ClientNode('localhost')
    client.main()

