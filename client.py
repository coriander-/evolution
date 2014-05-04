#client file
from twisted.internet import reactor, protocol
import sys
from twisted.internet.defer import DeferredQueue
from evolution import GameSpace 
import pickle
from twisted.internet.task import LoopingCall

#protocol for server and client
class Prot(protocol.Protocol):
    def __init__(self,q, game):
        self.q = q
        self.game = game

    def dataReceived(self, data):#when data received
        recv = pickle.loads(data)#load game state and set game state
        
        #adjust game state set comp and other player position
        self.game.opponent = recv['player']
        self.game.fish = recv['fish']

    def connectionMade(self):
        print "Connection made"
        self.q.get().addCallback(self.ForwardData)

        #create loopingCall
        self.lc =LoopingCall(self.game.loop_iteration)
        self.lc.start(1/60)

    def connectionLost(self, reason):
        #close game
        print "Error: connection lost"
        self.lc.stop()

    #writes data in q and prepares for next item
    def ForwardData(self, data):
        try:
            #send player and computer array
            toSend = self.game.player

            w = pickle.dumps(toSend) #serialize game state
            self.transport.write(w) #send game state
            self.q.get().addCallback(self.ForwardData)
        except Exception as ex:
            print "Failed to send game state: "
            self.transport.write("Failed to get update")


#factory to create connection
class Client(protocol.ClientFactory):
    def __init__(self, host, port):       
        self.q = DeferredQueue()

        #create game and set as self.game
        self.game = GameSpace(self.q, False) # every time game is change call q.put()

        

    def buildProtocol(self, addr):    
        return Prot(self.q, self.game )

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed: check that server is running"
        self.lc.stop()
        reactor.stop()

#pass hostname and port in commandline
if __name__=='__main__':
    if len(sys.argv) != 3:
        print 'usage: python client.py <hostname> <port>'
    else:
        f = Client(sys.argv[1], sys.argv[2])
        reactor.connectTCP(sys.argv[1], int(sys.argv[2]), f)
        reactor.run()
