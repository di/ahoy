import pygame
import time
from pygame.locals import *
import os, sys
import socket, sys, signal, operator
import socket, sys, signal
from threading import Lock
from ahoy.util.geo import *
from ahoy.agents.rectanglesurveil import *
from ahoy.eventapi import EventAPI
from ahoy.events.link import LinkEvent
from ahoy.events.move import EntityMoveEvent
from ahoy.sensors.radarsensor import RadarEvent

pygame.init()
pygame.display.set_caption("Path Finder 2000")
surface = pygame.display.set_mode((1280,800))
image_surface = pygame.image.load("map_big.png")
# 461, 282
window_center = (-1770,-2000)

class LatLonMapper :
    #def __init__(self, ip, port) :
    def __init__(self):

        self.tl_lat, self.tl_lon = (40.0140,-75.3321)
        self.br_lat, self.br_lon = (39.7590,-75.0000)
        self.d_lat = self.br_lat-self.tl_lat
        self.d_lon = self.br_lon-self.tl_lon
        dx, dy, ux, uy = 0,0,0,0
        gotFirst = False


    def _get_pix(self, lat, lon) :
        global window_center
        cx, cy = window_center
        try :
            x = int(((lon-self.tl_lon)/self.d_lon)*4800)+cx
            y = int(((lat-self.tl_lat)/self.d_lat)*4800)+cy
            return (x,y)
        except :
            return (0,0)

    def _get_ll(self, x, y) :
        lon = ((x/4800.0)*self.d_lon)+self.tl_lon
        lat = ((y/4800.0)*self.d_lat)+self.tl_lat
        return (lat,lon)

def main() :
    
    def quit(signal, frame) :
        pygame.quit()
        sys.exit()

    def redraw(move=(0,0)) :
        global window_center
        pygame.display.flip()
        new = map(operator.sub, window_center, move)
        surface.blit(image_surface,new)
        #poc.draw()
        return new

    filename = sys.argv[1]
    f = open(filename,'w')

    gotFirst = False
    ended = False
    poc = LatLonMapper()
    signal.signal(signal.SIGINT, quit)
    redraw()
    dx, dy, ux, uy = 0,0,0,0
    lastlat = 0
    lastlon = 0
    while True:
        global window_center
        for event in pygame.event.get():
            if event.type == QUIT:
                f.close()
                quit(None, None)

        if pygame.mouse.get_pressed()[0] and (pygame.key.get_mods() & KMOD_SHIFT):
            s_ux, s_uy = pygame.mouse.get_pos()
            lat, lon = poc._get_ll(s_ux,s_uy) 
            if(not(lat == lastlat) and not(lon == lastlon)):
                f.write(str(lat) + "," + str(lon) + "\n")
                print str(lat) + "," + str(lon)
            lastlat = lat
            lastlon = lon
            ended = False
        elif pygame.mouse.get_pressed()[0]:
            if not gotFirst:
                dy, dy = pygame.mouse.get_pos()
                gotFirst = True
            ux,uy = pygame.mouse.get_pos()
            #window_center = redraw((dx-ux,dy-uy))
        elif pygame.mouse.get_pressed()[2]:
            if not ended:
                f.write("@@@\n")
                print "Ending this path"
                ended = True
        else :
            if gotFirst:
                window_center = redraw((dx-ux,dy-uy))
                dx,dy,ux,uy = 0,0,0,0
            gotFirst = False

        redraw((dx-ux,dy-uy)) 
        #time.sleep(1)
main()
