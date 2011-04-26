import pygame
import time
from pygame.locals import *
import os, sys
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
center = (-1770,-2000)
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
        global center
        cx, cy = center
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

    def redraw() :
        pygame.display.flip()
        surface.blit(image_surface,(0,0))

    filename = sys.argv[1]
    f = open(filename,'w')

    ended = False
    poc = LatLonMapper()
    signal.signal(signal.SIGINT, quit)
    redraw()
    dx, dy, ux, uy = 0,0,0,0
    lastlat = 0
    lastlon = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                f.close()
                quit(None, None)
                #pygame.quit(); sys.exit()

        if pygame.mouse.get_pressed()[0] and (pygame.key.get_mods() & KMOD_SHIFT):
            ux, uy = pygame.mouse.get_pos()
            lat, lon = poc.get_ll(ux,uy) 
            if(not(lat == lastlat) and not(lon == lastlon)):
                f.write(str(lat) + "," + str(lon) + "\n")
                print str(lat) + "," + str(lon)
            lastlat = lat
            lastlon = lon
            ended = False
        elif pygame.mouse.get_pressed()[2]:
            if not ended:
                f.write("@@@\n")
                print "Ending this path"
                ended = True

        redraw() 
        #time.sleep(1)
main()
