#home server

from twisted.internet import reactor, protocol
import sys
from twisted.internet.defer import DeferredQueue

#takes in coming data and puts it in putQ and gets data from getQ
class Forward(protocol.Protocol):
    def __init__(self, getQ, putQ):
        self.getQ = getQ
        self.putQ = putQ

    #when connection made, make ready to process data in getQ
    def connectionMade(self):
        print "home: Connection made"
        self.getQ.get().addCallback(self.ForwardData)

    #called when data received on connection, puts data into putQ for other connection to write 
    def dataReceived(self, data):
        #As soon as any data is received from client, write it to queue
        self.putQ.put(data)
        print "home: data received: "+data

    #writes data in getQ and prepares for next item
    def ForwardData(self, data):
        try:
            print "home: forward data: "+data
            #print self.writeConn
            self.transport.write(data)
            self.getQ.get().addCallback(self.ForwardData)
        except Exception as ex:
            self.transport.write("home: Failed to write to forward: "+str(ex))
        
#sets up server listening on correct port and initializes protocols with getQ and putQ
class DataFactory(protocol.Factory):
    def __init__(self, port, getQ, putQ): 
        reactor.listenTCP(port,self)
        self.getQ = getQ
        self.putQ = putQ
 
    #sets protocol for connection with getQ and putQ
    def buildProtocol(self, addr):
        return Forward(self.getQ,self.putQ)

#sets up queue for client and work connections and creates factories
class HomeServer():
    def __init__(self, clientPort, workPort):
        #print "here"
        clientQ = DeferredQueue() #things to be sent to client
        workQ = DeferredQueue()#things to be sent to work
        self.client = DataFactory(clientPort,clientQ, workQ)
        self.work = DataFactory(workPort, workQ, clientQ)
        #clientQ.put("Can pass in from other places")
        
if __name__ == '__main__':
    try:
                         #ports to relay info between 
        hs = HomeServer( int(sys.argv[1]), int(sys.argv[2]))
        reactor.run()
    except Exception as ex:
        print str(ex)
