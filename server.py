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
        data = data.split('\n')
        # interpret the method
        cmd = data[0].split(' ')[0]

        if len(data[0].split(' ')) == 1:
            # data is 'QUERY\n' or 'QUIT\n'
            if cmd == 'QUERY':
                data = pickle.dumps(self.peer_info)
                conn.sendall(data)
            
            elif cmd == 'QUIT':
                _info = self.peer_info.pop(addr)
                # info = [_upload_port, _rfc_num], _rfc_num is a dictionary
                for _num in _info[1]:
                    record = _info[1][_num]
                    self.rfc_index[_num].remove(record)
                    if not self.rfc_index[_num]:
                        # index is empty
                        self.rfc_index.pop(_num)
                # return True used to close the socket
                return True
            
            else:
                conn.sendall('P2P-CI/1.0 400 Bad Request\n')
        
        else:
            version = data[0].split(' ')[-1]
            if version != 'P2P-CI/1.0':
                # wrong version
                conn.sendall('P2P-CI/1.0 505 P2P-CI Version Not Supported\n')
            
            else:
                if cmd == 'CONNECT':
                    # register peer information
                    _upload_port = int(data[0].split(' ')[1])
                    self.peer_info[addr] = [_upload_port, {}]
                
                elif cmd == 'ADD':
                    # add rfc
                    _num = data[0].split(' ')[2]
                    _host = data[1].split(' ')[1]
                    _upload_port = data[2].split(' ')[1]
                    _title = data[3].split(' ')[1]
                    self.rfc_index.setdefault(_num, [])
                    self.rfc_index[_num].append((_host, _upload_port, _title))
                    # updata peer_info, self.peer_info[addr] = [_upload_port, {}]
                    self.peer_info[addr][1][_num] = (_host, _upload_port, _title)
                    # echo
                    data = 'P2P-CI/1.0 200 OK\n'
                    data += 'RFC %s %s %s %s\n' % (_num, _title, _host, _upload_port)
                    conn.sendall(data)

                elif cmd == 'LOOKUP':
                    # find peers have the specified rfc
                    _num = data[0].split(' ')[2]
                    if not _num in self.rfc_index:
                        _status_code = '404'
                        _phrase = 'Not Found'
                        data = 'P2P-CI/1.0 %s %s\n' % (_status_code, _phrase)
                    else:
                        _status_code = '200'
                        _phrase = 'OK'
                        data = 'P2P-CI/1.0 %s %s\n' % (_status_code, _phrase)
                        for record in self.rfc_index[_num]:
                            #record = (_host, _upload_port, _title)
                            data += 'RFC %s %s %s %s\n' % (_num, record[2], record[0], record[1])
                    conn.sendall(data)

                elif cmd == 'LIST':
                    # list all rfc index
                    if not self.rfc_index:
                        _status_code = '404'
                        _phrase = 'Not Found'
                        data = 'P2P-CI/1.0 %s %s\n' % (_status_code, _phrase)
                    else:
                        _status_code = '200'
                        _phrase = 'OK'
                        data = 'P2P-CI/1.0 %s %s\n' % (_status_code, _phrase)
                        for _num in self.rfc_index:
                            for record in self.rfc_index[_num]:
                                #record = (_host, _upload_port, _title)
                                data += 'RFC %s %s %s %s\n' % (_num, record[2], record[0], record[1])
                    conn.sendall(data)
                
                else:
                    conn.sendall('P2P-CI/1.0 400 Bad Request\n')
        # return False anyway used to keep the socket alive
        return False


    def connectClient(self, conn, addr):
        print 'Connected by', addr
        while True:
            data = conn.recv(1024)
            print '\nrequest:'
            print data,
            print 'from', addr
            isQuit = self.handleRequest(data, conn, addr)
            if isQuit:
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
