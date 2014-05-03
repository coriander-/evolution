#server
from twisted.internet import reactor, protocol
import sys
from twisted.internet.defer import DeferredQueue
from ../evolution import GameSpace
import pickle
from twisted.internet.task import LoopingCall


#protocol for server and client
class Prot(protocol.Protocol):
    def __init__(self,q, game):
        self.q = q
        self.game = game

    def dataReceived(self, data):#when data received
        recv = pickle.loads(data)#load game state and set game state
        
        #adjust other player
        self.game.enemy = recv

    def connectionMade(self):
        print "Connection made"
        #create loopingCall
        self.lc =LoopingCall(self.game.loop_iteration,None, None)
        self.lc.start(1/60)

        self.q.get().addCallback(self.ForwardData)

    def connectionLost(self, reason):
        #close game
        lc.stop()
        print "Error: connection lost"

    #writes data in q and prepares for next item
    def ForwardData(self, data):
        try:
            #send player and computer array
            toSend = dict()
            toSend['player'] = self.game.player
            toSend['fish'] = self.game.fish

            w = pickle.dumps(toSend) #serialize 
            self.transport.write(w) #send game state
            self.q.get().addCallback(self.ForwardData)
        except Exception as ex:
            print "Failed to send game state: "
            self.transport.write("Failed to get update")

#factory to create connection
class Server(protocol.Factory):
    def __init__(self):
        self.q = DeferredQueue() 
        
        #create game and set as self.game
        self.game = GameSpace(q);# every time game is change call q.put()

    def buildProtocol(self, addr):    
        return Prot(self.q, self.game)

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed"

#pass port in commandline
if __name__=='__main__':
    if sys.argc != 2:
        print 'usage: python client.py <port>'
    else:
        f=Server()
        listenTCP(sys.arv[1], sys.argv[2], f)
        reactor.run()

