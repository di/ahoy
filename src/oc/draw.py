import pygame
from pygame.locals import *
import os, sys
import socket, sys, signal, operator
from threading import Lock
from ahoy.util.geo import *
from ahoy.agents.rectanglesurveil import *
from ahoy.eventapi import EventAPI
from ahoy.events.link import LinkEvent
from ahoy.events.move import EntityMoveEvent
from ahoy.events.chemical import ChemicalSpillEvent
from ahoy.events.sensor import SensorEvent
from ahoy.sensors.radarsensor import RadarEvent

pygame.init()
pygame.display.set_caption("Operations Center")
surface = pygame.display.set_mode((1280,800))
image_surface = pygame.image.load("map_big.png")
# 461, 282

class ProofOfConcept :
    def __init__(self, ip, port) :
        self._nodelist = {}
        self._links = {}
        self._link_lock = Lock()
        self._nodecolor ={'Node':(100,100,255),'RadarSensor2':(255,100,100),'Scripted':(100,100,100)}
        self._radarlist = {}
        self._current_radar_bearing = None
        self._current_radar_loc = None

        self.tl_lat, self.tl_lon = (40.0140,-75.3321)
        self.br_lat, self.br_lon = (39.7590,-75.0000)
        self.d_lat = self.br_lat-self.tl_lat
        self.d_lon = self.br_lon-self.tl_lon

        dx, dy, ux, uy = 0,0,0,0
        gotFirst = False

        self._remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote_sock.connect((ip, port))
        self._event_api = EventAPI(self._remote_sock)
        t = self._event_api.start()
        self._event_api.subscribe(LinkEvent, self._on_link)
        self._event_api.subscribe(EntityMoveEvent, self._on_move)
        self._event_api.subscribe(RadarEvent, self._on_radar)
        self._event_api.subscribe(ChemicalSpillEvent, self._on_chemspill)
        self._event_api.subscribe(SensorEvent, self._on_sensor)

    def _get_pix(self, lat, lon) :
        try :
            x = int(((lon-self.tl_lon)/self.d_lon)*800)
            y = int(((lat-self.tl_lat)/self.d_lat)*600)
            return (x,y)
        except :
            return (0,0)

    def _get_ll(self, x, y) :
        lon = ((x/800.0)*self.d_lon)+self.tl_lon
        lat = ((y/600.0)*self.d_lat)+self.tl_lat
        return (lat,lon)

    def _on_link(self, event) :
        n1 = event.get_uid1()
        n2 = event.get_uid2()

        self._link_lock.acquire()
        self._links[tuple(sorted((n1, n2)))] = event.get_up()
        self._link_lock.release()

    def _on_move(self, event) :
        uid = event.get_uid()
        lon = event.get_long()
        lat = event.get_lat()
        type = event.get_type()
        
        self._nodelist[uid] = (self._get_pix(lat, lon),type)

    def _on_radar(self, event) :
        uid = event.get_owner_uid()
        t_loc = event.get_target_location()
        bear = round(math.degrees(event.get_bearing()))
        
        self._current_radar_bearing = bear
        self._current_radar_loc = self._nodelist[uid][0]

        self._radarlist[bear] = t_loc
    
    def _on_chemspill(self, event) :
        loc = event.get_location()
        int = event.get_intensity()

    def _on_sensor(self, event) :
        uid = event.get_owner_uid() 

    def send_bound(self, dx, dy, ux, uy) :
        p1 = self._get_ll(dx, dy)
        p2 = self._get_ll(ux, uy)

        self._event_api.publish(RectangleSurveilMove(0, p1, p2))
        self._event_api.publish(RectangleSurveilMove(1, p1, p2))
        self._event_api.publish(RectangleSurveilMove(2, p1, p2))
        self._event_api.publish(RectangleSurveilMove(3, p1, p2))

    def draw_nodes(self) :
        for uid in self._nodelist.keys() :
            (x, y), type = self._nodelist[uid]
            self.draw_node((x,y),type)

    def draw_radar(self) :
        if self._current_radar_loc is not None :
            x = int(self._current_radar_loc[0] + 800*math.cos(math.radians(self._current_radar_bearing-90)))
            y = int(self._current_radar_loc[1] + 600*math.sin(math.radians(self._current_radar_bearing-90)))
            pygame.draw.line(surface, (0,255,0), self._current_radar_loc, (x,y), 2) 
        for bear in self._radarlist.keys() :
            t_loc = self._radarlist[bear]
            if t_loc is None :
                del self._radarlist[bear]
            else :
                self.draw_blip(self._get_pix(*t_loc))

    def draw_blip(self, position) :
        x, y = position
        pygame.draw.circle(surface, (0,155,0), (x,y), 6, 0)
        pygame.draw.circle(surface, (100,255,100), (x,y), 4, 0)

    def draw_node(self, position, type) :
        x, y = position
        if self._nodecolor.has_key(type) :
            r,g,b = self._nodecolor[type]
        else :
            r,g,b = (100,100,100)

        pygame.draw.circle(surface, (255,255,255), (x,y), 10, 0)
        pygame.draw.circle(surface, (r,g,b), (x,y), 6, 0)
        pygame.draw.circle(surface, (r-100,g-100,b-100), (x,y), 8, 3)

    def draw_links(self) :
        self._link_lock.acquire()
        for link, up in self._links.iteritems() :
           if up :
               if self._nodelist.has_key(link[0]) and self._nodelist.has_key(link[1]) :
                   p1 = self._nodelist[link[0]][0]
                   p2 = self._nodelist[link[1]][0]
                   pygame.draw.line(surface, (255, 0, 0), p1, p2, 2)
        self._link_lock.release()

    def draw(self) :
        self.draw_nodes()
        self.draw_radar()
        self.draw_links()

def main() :

    center = (-1770,-2000)
    
    def quit(signal, frame) :
        pygame.quit()
        sys.exit()

    def redraw(move=(0,0)) :
        pygame.display.flip()
        new = map(operator.sub, center, move)
        surface.blit(image_surface,new)
        try :
            poc.draw()
        except NameError :
            pass
        return new

    if len(sys.argv) > 2 :
        poc = ProofOfConcept(sys.argv[1], int(sys.argv[2]))
    signal.signal(signal.SIGINT, quit)
    redraw()
    dx, dy, ux, uy = 0,0,0,0
    gotFirst = False

    while True:
        if pygame.key.get_mods() & KMOD_SHIFT:
            pass
            #print "shift"
        for event in pygame.event.get():
            if event.type == QUIT:
                quit(None, None)

        if pygame.mouse.get_pressed()[0] :
            if not gotFirst :
                dx, dy = pygame.mouse.get_pos()
                gotFirst = True
            ux, uy = pygame.mouse.get_pos()
        else:
            if gotFirst :
                center = redraw((dx-ux, dy-uy)) 
                dx, dy, ux, uy = 0,0,0,0
                #poc.send_bound(dx, dy, ux, uy)
            gotFirst = False    
        #pygame.draw.rect(surface,(0,0,255),(dx,dy,ux-dx,uy-dy),1)
        redraw((dx-ux, dy-uy)) 
main()
