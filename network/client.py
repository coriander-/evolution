#client file
from twisted.internet import reactor, protocol
import sys
from twisted.internet.defer import DeferredQueue
from ../evolution import Game

#protocol for client
class Prot(protocol.Protocol):
    def dataReceived(self, data):#when data received
        #update game state
        #load game state
        #set game state
        pass
    
    def connectionLost(self, reason):
        #close game
        print "Error: connection lost"

#factory to create connection
class Client(protocol.ClientFactory):
    def __init__(self, host, port):
        reactor.connectTCP(host, int(port), self)       

    def buildProtocol(self, addr):    
        return Prot()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed: check that server is running"
        reactor.stop()

#pass hostname and port in commandline
if __name__=='__main__':
    if sys.argc != 3:
        print 'usage: python client.py <hostname> <port>'
    else:
        Client(hostname, port)

