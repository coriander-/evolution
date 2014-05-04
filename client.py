#client file
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
        
        #adjust game state set comp and other player position
        self.game.opponent = recv['player']
        self.game.fish = recv['comps']

    def connectionMade(self):
        print "Connection made"
        self.q.get().addCallback(self.ForwardData)

    def connectionLost(self, reason):
        #close game
        print "Error: connection lost"

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
        self.game = GameSpace(q) # every time game is change call q.put()
        self.game.main()

        #create loopingCall
        self.lc =LoopingCall(self.game.loop_iteration,None, None)
        self.lc.start(1/60)

    def buildProtocol(self, addr):    
        return Prot(self.q, self.game )

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed: check that server is running"
        self.lc.stop()
        reactor.stop()

#pass hostname and port in commandline
if __name__=='__main__':
    if sys.argc != 3:
        print 'usage: python client.py <hostname> <port>'
    else:
        f = Client(hostname, port)
        reactor.connectTCP(host, int(port), f)
        reactor.run()
