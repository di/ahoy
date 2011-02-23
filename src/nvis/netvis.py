import pygame
from pygame.locals import *
import os, sys
import socket, sys, signal
from threading import Lock
##from ahoy.util.geo import *
##from ahoy.agents.rectanglesurveil import *
from ahoy.eventapi import EventAPI
from ahoy.events.link import LinkEvent
##from ahoy.events.move import EntityMoveEvent
##from ahoy.events.sensor import RadarEvent
from ahoy.events.communication import CommunicationSendEvent, CommunicationRecvEvent
from ahoy.events.startup import *
from ahoy.agents import *
from ahoy.entities.node import Node
from ahoy.entities.scripted import Scripted

pygame.init()
surface = pygame.display.set_mode((800,600))
##image_surface = pygame.image.load("image.png")
# 461, 282


class ItemDrawer :
    def __init__(self, width=300, height=100):
        self.x = 0
        self.y = 0
        self._width = width
        self._height = height
        self._border = 5
    
    def make_text(self, str, color=pygame.Color(255,255,255)): #, bg=None):
        # Create a font
        font = pygame.font.Font(None, 17)

        # Render the text
        #text = font.render(str, True, color, bg)
        text = font.render(str, True, color)

        # Create a rectangle
        #textRect = text.get_rect()
        
        # Blit the text
        ##screen.blit(text, textRect)
        
        #return textRect
        return text

class DaemonDraw(ItemDrawer):
    
    def __init__(self, id):
        ItemDrawer.__init__(self)
        self._id = id
        self._entities = []     # list of EntityDraw
        
    def add_entity(self, e):
        self._entities.append(e)
    
    def draw(self, left, top):
        height = 0
        
        # Make text description
        text = self.make_text( 'Entity' + str(self._id) )
        surface.blit(text, (left,top))
        height += text.get_height()
        
        y = top + height
        for entity_d in self._entities:
            height += entity_d.draw(left, y)
            y = top + height + self._border
        
        pygame.draw.rect(surface, pygame.Color(192,168,255), pygame.Rect(left,top,self._width,height), 5)
            
        

class EntityDraw(ItemDrawer):
    def __init__(self, entity):
        ItemDrawer.__init__(self)
        self._id = entity.get_uid()
    
    def draw(self, left, top):
        print 'Drawing Entity', self._id
        
        height = 0
        
        # Make text description
        text = self.make_text( 'Entity' + str(self._id) )
        surface.blit(text, (left,top))
        height += text.get_height()
        
        pygame.draw.rect(surface, pygame.Color(192,168,192), pygame.Rect(left, top, self._width, height), 2)
        return height
        


class NodeDraw(EntityDraw):
    def __init__(self, node):
        EntityDraw.__init__(self, node)
        #self._interfaces = node.get_interfaces()   # TODO
        self._agents = []   # list of AgentDraw
    
    def add_agent(self, a):
        ## Add agents to list of this node
        self._agents.append( a )
    
    def draw(self, left, top):
        print 'Drawing Node', self._id
        
        height = 0
        
        # Make text description
        text = self.make_text( 'Node' + str(self._id) )
        surface.blit(text, (left,top))
        height += text.get_height()
        
        y = top + height + self._border
        for agent in self._agents:
            height += agent.draw(left, y)
            y = top + height + self._border
        
        pygame.draw.rect(surface, pygame.Color(192,168,192), pygame.Rect(left, top, height, self._width), 2)
        
        return height
        
class AgentDraw(ItemDrawer):
    def __init__(self, agent_id):
        self._id = agent_id
    
    def draw(self, left, top):
        print 'Drawing agent', self._id
        
        height = 0
        
        # Make text description
        text = self.make_text( 'Agent ' + str(self._id) )
        surface.blit(text, (left,top))
        height += text.get_height()
        
        return height

    
    
    
    
    
class NetworkVisualizer :
    def __init__(self, ip, port) :
        self._nodelist = {}
        self._links = {}
        self._link_lock = Lock()
        self._net_map = {}
        
        self._phys_machines = {}
        self._entities = {}
        self._agents = {}
        
##        self._nodecolor ={'Node':(100,100,255),'RadarSensor2':(255,100,100),'Scripted':(100,100,100)}
##        self._radarlist = {}
##        self._current_radar_bearing = None
##        self._current_radar_loc = None

##        dx, dy, ux, uy = 0,0,0,0
##        gotFirst = False

        self._remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote_sock.connect((ip, port))
        self._event_api = EventAPI(self._remote_sock)
        t = self._event_api.start()
        self._event_api.subscribe(LinkEvent, self._on_link)
        ##self._event_api.subscribe(EntityMoveEvent, self._on_move)
        ##self._event_api.subscribe(RadarEvent, self._on_radar)
        
        ##self._event_api.subscribe(StartupEvent, self._on_startup)
        ##self._event_api.subscribe(AckStartupEvent, self._on_ack_startup)
        self._event_api.subscribe(StartSimulationEvent, self._on_start_sim)
        self._event_api.subscribe(StopSimulationEvent, self._on_stop_sim)
        
        self._event_api.subscribe(CommunicationSendEvent, self._on_send_event)
        self._event_api.subscribe(CommunicationRecvEvent, self._on_recv_event)


    def _on_link(self, event):
        n1 = event.get_uid1()
        n2 = event.get_uid2()

        self._link_lock.acquire()
        self._links[tuple(sorted((n1, n2)))] = event.get_up()
        self._link_lock.release()
        ##print 'Got link: ', n1, 'and', n2, ': ', self._links[tuple(sorted((n1,n2)))]


#~ 
    #~ def _on_startup(self, event):
        #~ print 'Got startup'
#~ 
#~ 
    #~ def _on_ack_startup(self, event):
        #~ print 'Got ack startup'


    def _on_start_sim(self, event):
        '''
        Got StartSimulationEvent.
        Calls get_mapping(), which gives the mapping of physical entities to nodes.
        '''
        print 'Got start sim'
        mapping = event.get_mapping()
        for phy in mapping:
            daemon_d = DaemonDraw(phy)
            
            ##self._net_map[phy] = {}
            for entity in mapping[phy]:
                #
                entity_d = None
                if isinstance(entity, Node):
                    entity_d = NodeDraw(entity)
                    for agent_id in entity.get_agent_uids():
                        #agent = entity.get_agent( agent_id)
                        agent_d = AgentDraw(agent_id)
                        entity_d.add_agent( agent_d )
                        
                        self._agents[agent_id] = agent_d
                else:
                    entity_d = EntityDraw(entity)
                    
                daemon_d.add_entity( entity_d )
                self._entities[entity_d._id] = entity_d
            
            self._phys_machines[phy] = daemon_d
                
                #~ #
                #~ entity_id = entity.get_uid()
                #~ 
                #~ ## Add agents to list of this node
                #~ agent_ids = []
                #~ if isinstance(entity, Node):
                    #~ agent_ids = entity.get_agent_uids()
                    #~ print 'Got agent ids: ', agent_ids
                #~ 
                #~ self._net_map[phy][(entity_id, type(entity))] = agent_ids
                
        #~ print 'mapping: ', self._net_map
        #~ for phy in self._net_map.keys():
            #~ print 'self._net_map[',phy,'] = ',
            #~ for entity_key in self._net_map[phy].keys():
                #~ print self._net_map[phy][entity_key]    # prints agent_ids, if any
        


    def _on_stop_sim(self, event):
        print 'Got stop sim'
        sys.exit()
    
    
    def _on_send_event(self, event):
        print 'Got send event'
    
    
    def _on_recv_event(self, event):
        print 'Got receive event'



##    def draw_nodes(self) :
##        for uid in self._nodelist.keys() :
##            (x, y), type = self._nodelist[uid]
##            #print type
##            #self.draw_node((100,255,100), (x,y))
##            self.draw_node((x,y),type)
    
    def draw_net(self):
        num_phys = len(self._net_map.keys())
        s_width, s_height = surface.get_size()
        
        #width = s_width / num_phys
        height = 250
        width = 150
        border = 10
        max_per_row = int(s_width/(width+border))
        
        count = 0
        for phy in self._phys_machines.keys():
            left = (width+border) * (count % max_per_row)
            top = height * int(count/max_per_row)
            self._phys_machines[phy].draw(left, top)
        
        ##print 'num physical machines: ', len(self._net_map.keys())
        #~ left = 10
        #~ for phy in self._net_map.keys():
            #~ entities = self._net_map[phy].keys()
            #~ num_entities = len(entities)
            #~ top_buffer = 0
            #~ for entity_id, entity_type in entities:
                #~ top_buffer += 30
                #~ 
                #~ 
            #~ pygame.draw.rect(surface, pygame.Color(0,0,255), pygame.Rect(left, 10, width, 10), 2)
            #~ left += 20
        ##pygame.draw.rect(surface, pygame.Color(192,168,255), pygame.Rect(40,60,20,20), 5)
            
            

##    def draw_radar(self) :
##        if self._current_radar_loc is not None :
##            x = int(self._current_radar_loc[0] + 800*math.cos(math.radians(self._current_radar_bearing-90)))
##            y = int(self._current_radar_loc[1] + 600*math.sin(math.radians(self._current_radar_bearing-90)))
##            pygame.draw.line(surface, (0,255,0), self._current_radar_loc, (x,y), 2)
##        for bear in self._radarlist.keys() :
##            t_loc = self._radarlist[bear]
##            if t_loc is None :
##                del self._radarlist[bear]
##            else :
##                self.draw_blip(self._get_pix(*t_loc))

##    def draw_blip(self, position) :
##        x, y = position
##        pygame.draw.circle(surface, (0,155,0), (x,y), 6, 0)
##        pygame.draw.circle(surface, (100,255,100), (x,y), 4, 0)

##    def draw_node(self, position, type) :
##        x, y = position
##        if self._nodecolor.has_key(type) :
##            r,g,b = self._nodecolor[type]
##        else :
##            r,g,b = (100,100,100)
##
##        pygame.draw.circle(surface, (255,255,255), (x,y), 10, 0)
##        pygame.draw.circle(surface, (r,g,b), (x,y), 6, 0)
##        pygame.draw.circle(surface, (r-100,g-100,b-100), (x,y), 8, 3)
    

    def draw_links(self) :
        self._link_lock.acquire()
        for link, up in self._links.iteritems() :
           if up :
               if self._nodelist.has_key(link[0]) and self._nodelist.has_key(link[1]) :
                   p1 = self._nodelist[link[0]][0]
                   p2 = self._nodelist[link[1]][0]
                   pygame.draw.line(surface, (255, 0, 0), p1, p2, 2)
        self._link_lock.release()

def main() :

    def quit(signal, frame) :
##        pygame.quit()
        sys.exit()

    def redraw() :
        #net_vis.draw_links()
        net_vis.draw_net()
        
        pygame.display.flip()
        
##        surface.blit(image_surface,(0,0))
##        poc.draw_nodes()
##        poc.draw_radar()
##        poc.draw_links()
    
    ip='192.168.1.121'
    port = 12345
    
    if len(sys.argv) > 2:
        ip = sys.argv[1]
        port = sys.argv[2]
    
    
    net_vis = NetworkVisualizer(ip, port)
    signal.signal(signal.SIGINT, quit)
    redraw()
    
##    dx, dy, ux, uy = 0,0,0,0
    gotFirst = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit(None, None)
                #pygame.quit(); sys.exit()
        redraw()

main()
