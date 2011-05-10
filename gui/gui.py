import pygame
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

global screen
CW = 16 # Cell Width 

class loc :
    def __init__(self, x, y) :
        self._x = x
        self._y = y

    def _x(self) :
        return self._x

    def _y(self) :
        return self._y

    def get_pix(self) :
        # Converts x/y coordinates to pixel coords
        global CW
        return ((self._x+30)*CW,(self._y+30)*CW) 

    def tuple(self) :
        return (self._x,self._y)

class node :
    def __init__(self, uid, type, loc, bear) :
        self._uid = uid
        self._type = type
        self._loc = loc
        self._bear = bear

    def update_loc(self, loc) :
        self._loc = loc

    def get_uid(self) :
        return self._uid

    def get_type(self) :
        return self._type

    def get_loc(self) :
        return self._loc

    def get_bear(self) :
        return self._bear

class CS485_gui :
    def __init__(self, ip, port) :
        self._nodelist = {}
        self._nodecolor ={'Node':(100,100,255),'RadarSensor2':(255,100,100),'Scripted':(100,100,100)}

        self._remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote_sock.connect((ip, port))
        self._event_api = EventAPI(self._remote_sock)
        t = self._event_api.start()
        self._event_api.subscribe(EntityMoveEvent, self._on_move)

        # Testing
        self._nodelist[1] = node(1, 'foobar', loc(200,200), 45)
        self._nodelist[2] = node(2, 'foobar', loc(300,300), 90)
        self._nodelist[3] = node(3, 'foobar', loc(400,400), 0)

    def _on_move(self, event) :
        uid = event.get_uid()
        lon = event.get_long()
        lat = event.get_lat()
        type = event.get_type()
        
        self._nodelist[uid] = node(uid, type, loc)

    def draw_nodes(self) :
        for uid in self._nodelist :
            self.draw_node(self._nodelist[uid])

    def draw_node(self, node) :
        global CW
        origin = node.get_loc()
        x,y = origin.tuple()
        bear = node.get_bear()
        points = [loc(x-CW/2, y-CW/2), loc(x-CW/2, y+CW/4), loc(x-CW/4, y+CW/2), loc(x+CW/4, y+CW/2), loc(x+CW/2, y+CW/4), loc(x+CW/2, y-CW/2)]
        points = self._rotate_poly(origin, points, bear)
        pygame.draw.polygon(screen, (255,0,0,), points, 0)
        pygame.draw.polygon(screen, (0,0,0,), points, 1)
        #pygame.draw.circle(screen, (0,0,0), (x,y), 1, 1)
        pygame.draw.circle(screen, (0,0,0), (x+1,y), 1, 1)

    def _rotate_point(self, origin, point, angle) :
        x = origin._x + ((point._x - origin._x) * math.cos(angle) - (point._y - origin._y) * math.sin(angle))
        y = origin._y + ((point._x - origin._x) * math.sin(angle) + (point._y - origin._y) * math.cos(angle))
        return x,y

    def _rotate_poly(self, origin, points, angle) :
        new_poly = []
        for point in points :
            new_poly.append(self._rotate_point(origin, point, angle))
        return new_poly

    def draw_grid(self) :
        global CW
        for i in range(60) :
            pygame.draw.line(screen, (200,200,200), (0,i*CW), (CW*50,i*CW))
            pygame.draw.line(screen, (200,200,200), (i*CW, 0), (i*CW, CW*50))
        for i in range(-25, 25) :
            Font = pygame.font.Font(None,CW)
            text = Font.render(str(i),1,(200,200,200))
            screen.blit(text,(i*CW+CW*25,CW*25))
            screen.blit(text,(CW*25,i*CW+CW*25))

    def quit(self, signal, frame) :
        pygame.quit()
        sys.exit()

    def redraw(self) :
        pygame.display.flip()
        gui.draw_grid()
        gui.draw_nodes()

if len(sys.argv) <= 2 :
    print "USAGE: python draw.py <hostname> <port>"
    quit(None, None)

try :
    gui = CS485_gui(sys.argv[1], int(sys.argv[2]))
except socket.error :
    print "Invalid host or port, or TCP forwarder not started. Exiting."
    quit(None, None)

pygame.init()
screen = pygame.display.set_mode((CW*50,CW*50))
screen.fill((255, 255, 255))
#screen.blit(background, (0, 0))

signal.signal(signal.SIGINT, quit)
gui.redraw()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            gui.quit(None, None)
    gui.redraw() 
