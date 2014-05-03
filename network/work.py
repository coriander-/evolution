from twisted.internet import reactor, protocol
import sys
from twisted.internet.defer import DeferredQueue

#work client

#takes in coming data and puts it in putQ and gets data from getQ
class WorkClient(protocol.Protocol):
    def __init__(self, getQ, putQ):
        self.getQ = getQ
        self.putQ = putQ
    
    #when connection made, make ready to process data in getQ
    def connectionMade(self):
        self.getQ.get().addCallback(self.ForwardData)
    
    #called when data received on connection, puts data into putQ for other connection to write 
    def dataReceived(self, data):
        print "work: data received: ", data
        self.putQ.put(data)

    #writes data in getQ and prepares for next item
    def ForwardData(self, data):
        try:
            self.transport.write(data)
            self.getQ.get().addCallback(self.ForwardData)
            print "work: forwarded: ",data
        except Exception as ex:
            self.transport.write("work: Failed to write to forward: "+str(ex))

    def connectionLost(self, reason):
        print "work: connection lost"

#sets up client connected on correct port and initializes protocols with getQ and putQ
class WorkFactory(protocol.ClientFactory):
    def __init__(self, host, port, getQ, putQ):
        self.getQ = getQ
        self.putQ = putQ
        reactor.connectTCP(host, int(port), self)

    def buildProtocol(self, addr):    
        return WorkClient(self.getQ, self.putQ)

    def clientConnectionFailed(self, connector, reason):
        print "work: Connection failed - goodbye!"
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        print "work: Connection lost - goodbye!"
        reactor.stop()


# creates factories to connect to home and ssh along with their queues
class Work():
    def __init__(self, homehost, homeport, sshhost, sshport):
        sshQ = DeferredQueue()
        homeQ = DeferredQueue()
        self.sshClient = WorkFactory(sshhost, sshport, sshQ, homeQ)
        self.homeClient = WorkFactory(homehost, homeport, homeQ, sshQ)

if __name__ == '__main__':
    try:
                    #server 1 info           #server 2 info 
        work = Work("localhost",sys.argv[1], "localhost", sys.argv[2])
        reactor.run()
    except Exception as ex:
        print str(ex)
