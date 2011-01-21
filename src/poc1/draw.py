import pygame
from pygame.locals import *
import os, sys
import socket, sys, signal
from ahoy.util.geo import *
from ahoy.agents.rectanglesurveil import *
from ahoy.eventapi import EventAPI
from ahoy.events.link import LinkEvent
from ahoy.events.move import EntityMoveEvent
from ahoy.events.sensor import RadarEvent

pygame.init()
surface = pygame.display.set_mode((800,600))
image_surface = pygame.image.load("image.png")
# 461, 282

class ProofOfConcept :
    def __init__(self, ip, port) :
        self._nodelist = {}
        self._nodecolor ={'Node':(100,100,255),'RadarSensor2':(255,100,100)}
        self._radarlist = {}
        self._current_radar_bearing = None
        self._current_radar_loc = None

        self.tl_lat, self.tl_lon = (39.960609,-75.17086)
        self.br_lat, self.br_lon = (39.920993,-75.102625)
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

    def _get_pix(self, lat, lon) :
        x = int(((lon-self.tl_lon)/self.d_lon)*800)
        y = int(((lat-self.tl_lat)/self.d_lat)*600)
        return (x,y)

    def _get_ll(self, x, y) :
        lon = ((x/800.0)*self.d_lon)+self.tl_lon
        lat = ((y/600.0)*self.d_lat)+self.tl_lat
        return (lat,lon)

    def _on_link(self, event) :
        pass

    def _on_move(self, event) :
        uid = event.get_uid()
        lon = event.get_long()
        lat = event.get_lat()
        type = event.get_type()
        
        self._nodelist[uid] = (self._get_pix(lat, lon),type)

    def _on_radar(self, event) :
        uid = event.get_sensor_id()
        t_loc = event.get_target_location()
        bear = round(math.degrees(event.get_bearing()))
        (lat,lon,agl) = event.get_radar_loc()
        
        self._current_radar_bearing = bear
        self._current_radar_loc = self._get_pix(lat, lon)

        self._radarlist[bear] = t_loc
        #if t_loc is not None :
        #    (t_lat,t_lon) = t_loc 
            #print int(math.degrees(bear))
            #print self._get_pix(t_lat, t_lon)

        self._nodelist[uid] = (self._get_pix(lat, lon),'RadarSensor2')

    def send_bound(self, dx, dy, ux, uy) :
        #print dx, dy, ux, uy
        p1 = self._get_ll(dx, dy)
        p2 = self._get_ll(ux, uy)

        self._event_api.publish(RectangleSurveilMove(0, p1, p2))
        self._event_api.publish(RectangleSurveilMove(1, p1, p2))
        self._event_api.publish(RectangleSurveilMove(2, p1, p2))

        print p1, p2

    def draw_nodes(self) :
        for uid in self._nodelist.keys() :
            (x, y), type = self._nodelist[uid]
            #print type
            #self.draw_node((100,255,100), (x,y))
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

def main() :
    
    def quit(signal, frame) :
        pygame.quit()
        sys.exit()

    def redraw() :
        pygame.display.flip()
        surface.blit(image_surface,(0,0))
        poc.draw_nodes()
        poc.draw_radar()

    poc = ProofOfConcept(sys.argv[1], int(sys.argv[2]))
    signal.signal(signal.SIGINT, quit)
    redraw()
    dx, dy, ux, uy = 0,0,0,0
    gotFirst = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit(None, None)
                #pygame.quit(); sys.exit()

        if pygame.mouse.get_pressed()[0] :
            if not gotFirst :
                dx, dy = pygame.mouse.get_pos()
                gotFirst = True
            ux, uy = pygame.mouse.get_pos()
        else:
            if gotFirst :
                poc.send_bound(dx, dy, ux, uy)
            gotFirst = False    
        pygame.draw.rect(surface,(255,0,0),(dx,dy,ux-dx,uy-dy),1)
        redraw() 
main()
