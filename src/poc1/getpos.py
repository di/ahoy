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
surface = pygame.display.set_mode((1341,744))
image_surface = pygame.image.load("river.png")
lat_comp = 0.004086 
lon_comp = 0.001935
# 461, 282
class LatLonMapper :
    #def __init__(self, ip, port) :
    def __init__(self):
        self.tl_lat, self.tl_lon = (40.0037,-75.456)
        self.br_lat, self.br_lon = (39.815,-74.994)
        self.d_lat = self.br_lat-self.tl_lat
        self.d_lon = self.br_lon-self.tl_lon

        dx, dy, ux, uy = 0,0,0,0
        gotFirst = False


    def get_pix(self, lat, lon) :
        try :
            x = int(((lon-self.tl_lon)/self.d_lon)*1341)
            y = int(((lat-self.tl_lat)/self.d_lat)*744)
            return (x,y)
        except :
            return (0,0)

    def get_ll(self, x, y) :
        lon = ((x/1341.0)*self.d_lon)+self.tl_lon
        lat = ((y/744.0)*self.d_lat)+self.tl_lat
        lon = lon + lon_comp
        lat = lat - lat_comp
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

        if pygame.mouse.get_pressed()[0] :
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
