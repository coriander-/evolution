#server
from twisted.internet import reactor, protocol
import sys
from twisted.internet.defer import DeferredQueue
from evolution import *
import pickle
from twisted.internet.task import LoopingCall
import pygame


#protocol for server and client
class Prot(protocol.Protocol):
    def __init__(self):
        self.q = DeferredQueue() 
        self.quit = False

    def dataReceived(self, data):#when data received
        try:
            #adjust other player
            if data=='QUIT':
                print "The other player ended the game"
            else:
                recv = pickle.loads(data)#load game state and set game state
                self.game.game_state = recv
                self.game.unpack()

        except Exception as ex:
            #print 'Pickle done messed up on '+data+': ' + str(ex)
            pass
        
        
    def connectionMade(self):
        print "Connection made"
        #create game and set as self.game
        if client:
            self.game = GameSpace(self.q, False);# every time game is change call q.put()
        else:
            self.game = GameSpace(self.q, True);# every time game is change call q.put()

        #create loopingCall
        self.lc =LoopingCall(self.game.loop_iteration)
        self.lc.start(1/60)

        self.q.get().addCallback(self.ForwardData)

    def connectionLost(self, reason):
        if self.quit == False:
            #close game
            self.lc.stop()
            reactor.stop()    
            self.quit = True
            print "Connection Lost: Game ended"
        else: #game has already 
            print "You terminated the connection"

    #writes data in q and prepares for next item
    def ForwardData(self, data):
        try:
            #send quit to other player
            if data == 'QUIT':
                self.transport.write('QUIT')
                self.connectionLost('you ended the game')
                print "You ended the game"
            else:
            #send player and computer array
                self.game.pack()
            
                w = pickle.dumps(self.game.game_state) #serialize 
                self.transport.write(w) #send game state

                self.q.get().addCallback(self.ForwardData)
        except Exception as ex:
            #print "Failed to send game state: "+str(ex)
            #self.transport.write("Failed to get update")
            pass

#factory to create connection
class Server(protocol.Factory):
    def buildProtocol(self, addr):    
        return Prot()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed"
        try:
            reactor.stop()    
        except Exception as ex:
            print str(ex)

#factory to create connection
class Client(protocol.ClientFactory):
    def buildProtocol(self, addr):    
        return Prot()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed"
        try:
            reactor.stop()    
        except Exception as ex:
            print str(ex)

#pass port in commandline
if __name__=='__main__':
    try:
        if sys.argv[1] == 'client':
            client = True
            f = Client()
            reactor.connectTCP(sys.argv[2], int(sys.argv[3]), f)
        elif sys.argv[1] == 'server':
            client = False
            f = Server()
            reactor.listenTCP(int(sys.argv[2]), f)
        else:
            raise Exception('not server or client')
        reactor.run()
    except Exception as ex:
        print 'usage: python network.py <client|server> <hostname?> <port>'
        print str(ex)
