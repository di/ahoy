import pygame
from pygame.locals import *
import os, sys
import socket, sys, signal, operator
from threading import Lock
from ahoy.util.geo import *

# 461, 282
center = (-1770,-2000)
window_center = (-1770,-2000)
surface = pygame.display.set_mode((1280,800))

class LatLonMapper:
    def __init__(self) :
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
        global center
        cx, cy = center
        lon = (((x-cx)/4800.0)*self.d_lon)+self.tl_lon
        lat = (((y-cy)/4800.0)*self.d_lat)+self.tl_lat
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
        return new

    filename = sys.argv[1]
    f = open(filename,'w')
    
    pygame.init()
    pygame.display.set_caption("Path Finder 2000")
    image_surface = pygame.image.load("map_big.png")
    signal.signal(signal.SIGINT, quit)
    redraw()
    dx, dy, ux, uy = 0,0,0,0
    gotFirst = False

    LLM = LatLonMapper()
    lastlat = 0
    lastlon = 0
    ended = False

    while True:
        global center
        global window_center
        # Quit code
        for event in pygame.event.get():
            if event.type == QUIT:
                quit(None, None)
        
        if pygame.mouse.get_pressed()[0] and pygame.key.get_mods() & KMOD_SHIFT :
            s_ux, s_uy = pygame.mouse.get_pos()
            lat, lon = LLM._get_ll(s_ux, s_uy)
            if(not(lat == lastlat) and not(lon == lastlon)):
                f.write(str(lat) + "," + str(lon) + "\n")
                print str(lat) + "," + str(lon)
            lastlat = lat
            lastlon = lon
            ended = False

        elif pygame.mouse.get_pressed()[0] :
            if not gotFirst :
                dx, dy = pygame.mouse.get_pos()
                gotFirst = True
            ux, uy = pygame.mouse.get_pos()
            center = redraw((dx-ux, dy-uy)) 
        elif pygame.mouse.get_pressed()[2] :
            if not ended :
                f.write("@@@\n")
                print "Ending this path"
                ended = True
        else:
            if gotFirst :
                #global center
                window_center = redraw((dx-ux, dy-uy)) 
                dx, dy, ux, uy = 0,0,0,0
            gotFirst = False    
        redraw((dx-ux, dy-uy)) 
main()
