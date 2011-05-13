import pygame
from pygame.locals import *
import os, sys
import socket, sys, signal
from threading import Lock
from ahoy.util.geo import *
from ahoy.eventapi import EventAPI
from ahoy.events.move import EntityMoveEvent
from ahoy.sensors.forwardcamera import ForwardCameraEvent

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

    def tuple(self) :
        return (self._x,self._y)

class node :
    def __init__(self, uid, type, loc, bear, agents) :
        self._uid = uid
        self._type = type
        self._loc = loc
        self._bear = bear
        self._agents = agents

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

    def has_agent(self, agent) :
        return agent in self._agents

class grid_gui :
    def __init__(self) :
        self._nodelist = {}
        self._vislist = {}
        self._vis_lock = Lock()
        self._fieldlist = {}
        self._field_lock = Lock()
        try :
            self._event_api = EventAPI()
        except :
            print 'Environmental variable "AHOY_PORT" not set, exiting.'
            quit(None, None)
        t = self._event_api.start()
        self._event_api.subscribe(EntityMoveEvent, self._on_move)
        self._event_api.subscribe(ForwardCameraEvent, self._on_camera)

    def _on_move(self, event) :
        global CW
        uid = event.get_uid()
        x = int(400+(event.get_long()/.004444)*400)
        y = int(400-(event.get_lat()/.004444)*400)
        type = event.get_type()
        bear = event.get_bearing()
        loca = loc(x,y)
        agents = event.get_agents()
        
        self._nodelist[uid] = node(uid, type, loca, bear, agents)

    def _on_camera(self, event) :
        uid = event.get_owner_uid()
        self._vis_lock.acquire()
        self._vislist[uid] = []
        for visible in event.get_visible() :
            x = int(400+(visible[1]/.004444)*400) #lon
            y = int(400-(visible[0]/.004444)*400) #lat
            self._vislist[uid].append((x, y))
        self._vis_lock.release()
        field = event.get_poly()
        self._field_lock.acquire()
        self._fieldlist[uid] = field
        self._field_lock.release()

    def draw_nodes(self) :
        for uid in self._nodelist :
            self.draw_node(self._nodelist[uid])

    def draw_node(self, node) :
        global CW
        origin = node.get_loc()
        x,y = origin.tuple()
        bear = node.get_bear()
        points = [loc(x+CW/2, y+CW/2), loc(x+CW/2, y-CW/4), loc(x+CW/4, y-CW/2), loc(x-CW/4, y-CW/2), loc(x-CW/2, y-CW/4), loc(x-CW/2, y+CW/2)]
        points = self._rotate_poly(origin, points, bear)
        color = (0,0,0)
        if node.has_agent('PredatorAgent') or node.has_agent('PredatorAgentImpl') :
            color = (255,0,0)
        elif node.has_agent('PreyAgent') :
            color = (0,0,255)
        pygame.draw.polygon(screen, color, points, 0)
        pygame.draw.polygon(screen, (0,0,0), points, 1)
        pygame.draw.circle(screen, (0,0,0), (x+1,y), 1, 1)

    def draw_vis(self) :
        self._vis_lock.acquire()
        for node, vis in self._vislist.iteritems() :
            for v in vis :
                pygame.draw.circle(screen, (0, 255, 0), (v[0], v[1]), 5, 0)
        self._vis_lock.release()

    def draw_fields(self) :
        self._field_lock.acquire()
        for field in self._fieldlist.values() :
            field_poly = []
            for point in field :
                x = int(400+(point[1]/.004444)*400)
                y = int(400-(point[0]/.004444)*400)
                field_poly.append((x,y))
            pygame.draw.polygon(screen,(0,0,255),field_poly,1)
        self._field_lock.release()

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
            screen.blit(text,(CW*25,CW*25-i*CW))

    def redraw(self) :
        pygame.display.flip()
        screen.fill((255, 255, 255))
        gui.draw_grid()
        gui.draw_fields()
        gui.draw_nodes()
        gui.draw_vis()

def quit(signal, frame) :
    pygame.quit()
    sys.exit()

gui = grid_gui()

pygame.init()
screen = pygame.display.set_mode((CW*50,CW*50))

signal.signal(signal.SIGINT, quit)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            quit(None, None)
    gui.redraw() 
