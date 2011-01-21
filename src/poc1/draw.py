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

        dx, dy, ux, uy = 0,0,0,0
        gotFirst = False

        self._remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote_sock.connect((ip, port))
        self._event_api = EventAPI(self._remote_sock)
        t = self._event_api.start()
        self._event_api.subscribe(LinkEvent, self._on_link)
        self._event_api.subscribe(EntityMoveEvent, self._on_move)
        self._event_api.subscribe(RadarEvent, self._on_radar)

    def _on_link(self, event) :
        pass

    def _on_move(self, event) :
        uid = event.get_uid()
        lon = event.get_long()
        lat = event.get_lat()
        # TODO Change this to do it the dumb way
        x, y, z = sph_to_lin(lat, lon, 0)
        dx, dy, dz = (1049.5729025143785, -3953.302616399923, 4884.6121796385296)
        y = int((y - dy)/(5.808/800)) + 461
        z = int((z - dz)/(4.356/600)) + 282
        self._nodelist[uid] = (y, z)

    def _on_radar(self, event) :
        pass

    def send_bound(self, dy, dz, uy, uz) :
        delta_x, delta_y, delta_z = (1049.5729025143785, -3953.302616399923, 4884.6121796385296)
        dy = ((dy - 461) * (5.808/800)) + delta_y
        dz = ((dz - 282) * (4.356/600)) + delta_z
        uy = ((uy - 461) * (5.808/800)) + delta_y
        uz = ((uz - 282) * (4.356/600)) + delta_z

        print lin_to_sph(0, dy, dz), lin_to_sph(0, uy, uz, )

    def draw_nodes(self) :
        for uid in self._nodelist.keys() :
            y, z = self._nodelist[uid]
            self.draw_node((100,255,100), (y,z))

    def draw_node(self, color, position) :
        r, g, b = color
        x, y = position

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

    poc = ProofOfConcept(sys.argv[1], int(sys.argv[2]))
    signal.signal(signal.SIGINT, quit)
    redraw()

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
            pygame.draw.rect(surface,(255,0,0),(dx,dy,ux-dx,uy-dy),1)
            poc.send_bound(dx, dy, ux, uy)
        else:
            gotFirst = False    
        redraw() 
main()
