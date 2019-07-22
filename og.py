from sys import stdin
import threading
import time
import socket
import sys
peerNo = int(sys.argv[1])
peer1 = int(sys.argv[2])
peer2 = int(sys.argv[3])
PORT = int(sys.argv[1])+50000
identity_succ1 = int(sys.argv[2])+50000
identity_succ2 = int(sys.argv[3])+50000
maxi = int(sys.argv[4])
server_address = ('localhost', PORT)
file_path = "./request.txt"


class peer:

    def __init__(self):

        self.peers = [{"port": int(sys.argv[2])+50000, "seq":0, "lastrespond":0, "no":int(sys.argv[2])}, {
            "port": int(sys.argv[3])+50000, "seq":0, "lastrespond":0, "no":int(sys.argv[3])}]
        self.pres = [-1, -1]
        self.die = False

    def hash(self, num):
        assert(num >= 0 and num <= 9999)
        return num % 256
    # listen for tcp
###################################

    def send_file_to(self, src):

        print("send to "+src)

        pass

    def listenTCP(self):
        myTCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        myTCPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        myTCPsocket.bind(server_address)

        while True:

            if self.die:
                sys.exit()
            myTCPsocket.listen(5)
            client, (addr, peerport) = myTCPsocket.accept()
            threading.Thread(
                target=self.handleTCP, args=[client]).start()
    # response tcp
    def handleTCP(self, client):

        data = client.recv(1024)
        data_str = data.decode("ASCII")
        info = data_str.split("-")

        typ = info[0]
        src = info[1]
        fil = info[2]

        if int(typ) == 1:
            # find the fil

            print("fil request from "+str(src))
            self.send_request_type(int(fil), int(src))
            pass
        elif(int(typ) == 2):
            self.send_file_to(src)

            # the send the file to the src directly
        elif int(typ) == 4:
            peerFrom = int(info[1])
            print("a request from pre"+info[1]+" "+str(self.pres[peerFrom]))

            requestPeer = int(info[2])
            newTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newTCP.connect(("localhost", self.pres[peerFrom]+50000))
            if peerFrom == 1:
                # someone's first successor (peer0) is is dead
                assert(requestPeer == 0)
                # update your peer 1 to my peer 0(update your peer 0 to me)
                newTCP.send(("5-"+"1-"+str(self.peers[0]['no'])).encode())
            else:
                assert(requestPeer == 0)
                # update your peer 1 to my peer 0
                newTCP.send(("5-"+"0-"+str(self.peers[0]['no'])).encode())
            newTCP.close()
            pass
        elif int(typ) == 5:
            peerToUpdate = int(info[1])
            peerNoToUpdate = int(info[2])
            if peerToUpdate == 1:
                # update my peer 0 from my peer 1
                self.peers[0] = self.peers[1]
                # update my peer 1 to the one given
                self.peers[1] = {"port": int(
                    peerNoToUpdate)+50000, "seq": 0, "lastrespond": 0, "no": int(peerNoToUpdate)}
            else:
                # update your peer 1 from nfo
                self.peers[1] = {"port": int(
                    peerNoToUpdate)+50000, "seq": 0, "lastrespond": 0, "no": int(peerNoToUpdate)}
            print("My first successor is now peer "+str(self.peers[0]["no"]))
            print("My second successor is now peer "+str(self.peers[1]["no"]))
            pass
        elif int(typ) == 6:

            peerToUpdate = int(info[1])
            peerNoToUpdate = int(info[2])

            if peerToUpdate == 0:

                self.peers[0] = self.peers[1]
                self.peers[1] = {"port": int(
                    peerNoToUpdate)+50000, "seq": 0, "lastrespond": 0, "no": int(peerNoToUpdate)}

            else:
                assert(peerToUpdate == 1)
                self.peers[peerToUpdate] = {"port": int(
                    peerNoToUpdate)+50000, "seq": 0, "lastrespond": 0, "no": int(peerNoToUpdate)}
            print("My first successor is now peer "+str(self.peers[0]["no"]))
            print("My second successor is now peer "+str(self.peers[1]["no"]))
        client.close()
        pass
    # all args are int

    def send_tcp_packet(self, byt, dest_port):
        # TODO: BUG Transport endpoint is already connected
        myTCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        myTCPsocket.connect(("localhost", dest_port))
        myTCPsocket.send(byt)
        myTCPsocket.close()

    def generate_tcp_file_request(self, typ,  location, src):

        return (str(typ)+"-"+str(src)+"-"+str(location)).encode()
        # type-src location - file location

    # all args are int
    def send_request_type(self, location, src):
        print("the src is "+str(src))
        if peerNo < self.peers[0]["no"]:
            #

            if location > self.peers[0]["no"] or location < peerNo:

                self.send_tcp_packet(
                    self.generate_tcp_file_request(1, location, src), self.peers[0]["port"])

            else:
                self.send_tcp_packet(
                    self.generate_tcp_file_request(2, location, src), self.peers[0]["port"])
        else:

            if location > peerNo or location <= self.peers[0]["no"]:
                self.send_tcp_packet(
                    self.generate_tcp_file_request(2, location, src), self.peers[0]["port"])
            else:
                self.send_tcp_packet(
                    self.generate_tcp_file_request(1, location, src), self.peers[0]["port"])

    def readInput(self):

        for line in stdin:
            print("user request "+line)
            if (line[0:7] == "request"):

                location = hash(int(line[8:12]))
                self.send_request_type(location, peerNo)

            elif(line[0:4] == "quit"):

                myTcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                myTcpSocket.connect(("localhost", (self.pres[0]+50000)))

                myTcpSocket.send(("6-"+"0-"+str(self.peers[1]['no'])).encode())

                myTcpSocket.close()

                myTcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                myTcpSocket.connect(("localhost", (self.pres[1]+50000)))

                myTcpSocket.send(("6-"+"1-"+str(self.peers[0]['no'])).encode())

                myTcpSocket.close()
                self.die == True
                sys.exit()
                pass


###################################


    def pingToPeer(self, identity):
        # myUDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       # myUDPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # myUDPsocket.bind(server_address)
        myUDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            if self.die:
                break

            seq = self.peers[identity]['seq']
            lastack = self.peers[identity]['lastrespond']
            peerport = self.peers[identity]['port']
            if seq >= lastack + 2:
                print("Peer " + str(self.peers[identity]
                                    ["no"])+" is no longer alive")
                # handle peer die procedure
                if identity == 0:  # first peer is dead
                    myTCPsocket = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
                    myTCPsocket.connect(("localhost", self.peers[1]['port']))
                    myTCPsocket.send(("4-"+"1-"+"0").encode()
                                     )  # type-from-peerno
                    myTCPsocket.close()

                else:

                    # second peer is dead
                    # wait for the first succ to handle the change of peer
                    time.sleep(20)
                    myTCPsocket = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM)
                    myTCPsocket.connect(("localhost", self.peers[0]['port']))
                    myTCPsocket.send(("4-"+"0-"+"0").encode()
                                     )  # type-from-peerno
                    myTCPsocket.close()
                time.sleep(15)
            else:
                # send a normal ping request
                s = "1-"+str(seq)+"-"+str(identity)+"-"+str(peerNo)
                myUDPsocket.sendto(s.encode(),
                                   ("localhost", peerport))
                self.peers[identity]['seq'] += 1
                time.sleep(8)
        myUDPsocket.close()
        pass

    def handleRespondPing(self,  data):

        myUDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = data.decode("ASCII")  # string
        data = data.split("-")
        typ = int(data[0])
        seq = int(data[1])
        peerFrom = int(data[3])
        if typ == 1:  # request
            identity = int(data[2])
            self.pres[identity] = peerFrom  # update the peerFrom number of pre
            s = "2-"+str(seq+1)+"-"+str(identity)+"-"+str(peerNo)
            myUDPsocket.sendto(s.encode(), ("localhost", 50000+peerFrom))
            print("A ping request is received from peer " +
                  str(self.pres[identity]))
            pass
        elif typ == 2:  # respond from succ
            identity = int(data[2])
            # update the last received respond no
            self.peers[identity]['lastrespond'] = seq
            print("A ping respond is received from peer " +
                  str(self.peers[identity]["no"]))
            pass
        elif typ == 3:  # file
            pass
        elif typ == 4:  # ack
            pass
        myUDPsocket.close()

    def listenToPeerUDP(self, myUDPsocket):
        # myUDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # myUDPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # myUDPsocket.bind(server_address)
        while True:
            if self.die:
                sys.exit()
            data, (addr, p) = myUDPsocket.recvfrom(1024)  # receive udp packet
            threading.Thread(target=self.handleRespondPing,
                             args=[data]).start()

    # read user input, send request to other user
###################################

    def udp_run(self):
        myUDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        myUDPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        myUDPsocket.bind(server_address)
        listenPingThread1 = threading.Thread(
            target=self.listenToPeerUDP, args=[myUDPsocket])

        ping1Thread = threading.Thread(
            target=self.pingToPeer, args=[0])
        ping2Thread = threading.Thread(
            target=self.pingToPeer, args=[1])
        listenPingThread1.start()

        ping2Thread.start()
        ping1Thread.start()
        pass

    def listen_for_file(self):
        pass

    def send_file(self):

        pass

    def run(self):

        threading.Thread(
            target=self.udp_run, args=[]).start()

        listenTCPthread = threading.Thread(
            target=self.listenTCP, args=[])
        inputThread = threading.Thread(
            target=self.readInput, args=[])
        # listen for tcp message
        # wait user input
        listenTCPthread.start()

        inputThread.start()

        # listen for ping messages

        # listen to two peers


if __name__ == "__main__":
    p = peer()
    p.run()
