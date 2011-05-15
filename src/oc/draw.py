import pygame
from pygame.locals import *
import os, sys
import socket, sys, signal, operator
import random
from threading import Lock
from ahoy.util.geo import *
from ahoy.agents.uav import *
from ahoy.eventapi import EventAPI
from ahoy.events.startup import StartupEvent
from ahoy.events.startup import StopSimulationEvent
from ahoy.events.link import LinkEvent
from ahoy.events.move import EntityMoveEvent
from ahoy.events.chemical import ChemicalSpillEvent
from ahoy.events.sensor import SensorEvent
from ahoy.events.correlation import CorrelationEvent 
from ahoy.events.prox_threat import ProximityThreatEvent
from ahoy.events.divert import DivertEvent
from ahoy.sensors.radarsensor import RadarEvent
from ahoy.sensors.sonarsensor import SonarEvent
from ahoy.sensors.camerasensor import CameraEvent 
from ahoy.sensors.chemicalsensor import ChemicalDetectEvent

center = (-1770,-2000)
window_center = (-1770,-2000)
surface = pygame.display.set_mode((1280,800))

def quit(signal, frame) :
    pygame.quit()
    sys.exit()

class ProofOfConcept :
    def __init__(self, ip, port) :
        self._nodelist = {}
        self._links = {}
        self._correlations = {}
        self._fields = {}
        self._cameranodes = {}
        self._threats = {}
        self._chemsensors = {}
        self._chemsensors_detect = {}
        self._divert_points = [] 
        self._threat_lock = Lock()
        self._link_lock = Lock()
        self._correlation_lock = Lock()
        self._fields_lock = Lock()
        self._cameranodes_lock = Lock()
        self._divert_lock = Lock()
        self._chem_lock = Lock()
        self._nodecolor ={'Node':(100,100,255),'RadarSensor2':(255,100,100),'Scripted':(100,100,100)}
        self._radarlist = {}
        self._sonarlist = {}
        self._aaron_sucks = {} # Agent lists
        self._current_radar_bearing = None
        self._current_radar_loc = None
        self._current_sonar_bearing= {} 
        self._current_sonar_loc = {} 

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

        self._event_api.subscribe(StartupEvent, self._on_startup)
        self._event_api.subscribe(StopSimulationEvent, self._on_shutdown)
        self._event_api.subscribe(LinkEvent, self._on_link)
        self._event_api.subscribe(EntityMoveEvent, self._on_move)
        self._event_api.subscribe(RadarEvent, self._on_radar)
        self._event_api.subscribe(SonarEvent, self._on_sonar)
        self._event_api.subscribe(ChemicalSpillEvent, self._on_chemspill)
       # self._event_api.subscribe(SensorEvent, self._on_sensor)
        self._event_api.subscribe(CorrelationEvent, self._on_correlation)
        self._event_api.subscribe(ProximityThreatEvent, self._on_prox_threat)
        self._event_api.subscribe(CameraEvent, self._on_camera)
        self._event_api.subscribe(ChemicalDetectEvent, self._on_chem_detect)


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

    def _on_startup(self, event) :
        self._world = event.get_world()
        entities = self._world.get_entities()
        for entity in entities :
            sensors = entity.get_sensors().values()
            for sensor in sensors:
                if sensor.__class__.__name__ == 'ChemicalSensor' :
                    uid = sensor.get_owner().get_uid()
                    self._chemsensors[uid] = sensor.get_owner().get_position()

    def _on_shutdown(self, event) :
        quit(None, None)

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
        try :
            agent = map(lambda a : a.__class__.__name__, self._world.get_entity(uid).get_agents().values()) 
            self._aaron_sucks[uid] = agent 
        except AttributeError :
            print 'Simulation was started before interface'
            quit(None, None)

        self._nodelist[uid] = ((lat, lon),type)

    def _on_sonar(self, event) :
        uid = event.get_owner_uid()
        t_loc = event.get_detects()
        bear = event.get_bearing()
        
        self._current_sonar_bearing[uid] = bear
        self._current_sonar_loc[uid] = self._nodelist[uid][0]

        self._sonarlist[bear] = t_loc

    def _on_radar(self, event) :
        uid = event.get_owner_uid()
        t_loc = event.get_target_location()
        bear = round(math.degrees(event.get_bearing()))
        
        self._current_radar_bearing = bear
        self._current_radar_loc = self._nodelist[uid][0]

        self._radarlist[bear] = t_loc
    
    def _on_chemspill(self, event) :
        print 'Chemical spill happened'
        loc = event.get_location()
        #int = event.get_intensity()

    def _on_chem_detect(self,event) :
        loc = event.get_location()
        uid = event.get_owner_uid()
        self._chem_lock.acquire()
        self._chemsensors_detect[uid] = loc
        self._chem_lock.release()
        print 'Chemical detected at ' , loc


    def _on_sensor(self, event) :
        print 'Got sensor event'
        uid = event.get_owner_uid() 

    def _on_correlation(self, event) :
        p1, p2 = event.get_locations()
        uid = event.get_ais_uid()
        print 'CORRELATION AIS id %s AT %s' % (uid, p2)

        self._correlation_lock.acquire()
        self._correlations[uid] = tuple(sorted((p1, p2)))
        self._correlation_lock.release()

    def _on_prox_threat(self, event) :
        uid = event.get_threatened_uid()
        loc = event.get_threat_location()

        self._threat_lock.acquire()
        self._threats[uid] = loc
        self._threat_lock.release()

    def _on_camera(self, event) :
        field = event.get_field()
        cameranodes = event.get_visible()
        uid = event.get_owner_uid()

        self._fields_lock.acquire()
        self._fields[uid] = field
        self._fields_lock.release()

        self._cameranodes_lock.acquire()
        self._cameranodes[uid] = cameranodes
        self._cameranodes_lock.release()

    def send_bound(self, uid, dx, dy, ux, uy) :
        p1 = self._get_ll(dx, dy)
        p2 = self._get_ll(ux, uy)
        self._event_api.publish(UAVSurveilArea(uid, p1, p2))

    def send_divert(self, points):
        ll_points = []
        for p in points:
            lat, lon = self._get_ll(p[0], p[1])
            ll_points.append([lat,lon])
        self._event_api.publish(DivertEvent(ll_points))

    def draw_chem_sensors(self) :
        detected = self._chemsensors_detect.keys()
        for uid in self._chemsensors.keys():
            if (detected.count(uid) == 0):
                loc = self._chemsensors[uid]
                self.draw_chem_sensor(loc,(0,255,0))
        for uid in detected:
            loc = self._chemsensors_detect[uid]
            self.draw_chem_sensor(loc,(255,0,0))
    

    def draw_chem_sensor(self, loc, color):
        x,y = self._get_pix(loc[0], loc[1])
        pygame.draw.circle(surface, color,(x,y),10,0)

    def draw_nodes(self) :
        for uid in self._nodelist.keys() :
            (lat, lon), type = self._nodelist[uid]
            self.draw_node(self._get_pix(lat,lon),type,uid)

    def draw_sonar(self) :
        #print 'drawing sonar'
        global center
        cx, cy = center

        for uid in self._current_sonar_loc.keys() :
            px, py = self._get_pix(*self._current_sonar_loc[uid])
            x = int(px + 4800*math.cos(math.radians(self._current_sonar_bearing[uid]-90)))
            y = int(py + 4800*math.sin(math.radians(self._current_sonar_bearing[uid]-90)))
            pygame.draw.line(surface, (255,255,0), self._get_pix(*self._current_sonar_loc[uid]), (x,y), 2) 
        
        for bear in self._sonarlist.keys() :
            t_loc = self._sonarlist[bear]
            if len(t_loc) < 3 :
                #print '< 3', t_loc
                del self._sonarlist[bear]
            else :
                #print 't_loc', t_loc
                try:
                    lat, lon, bs = t_loc
                    #print 'drawing', lat, lon, bs
                    self.draw_blip(self._get_pix(lat, lon), (255,255,100))
                except:
                    if self._sonarlist.has_key(bear) :
                        del self._sonarlist[bear]

    def draw_radar(self) :
        global center
        cx, cy = center
        if self._current_radar_loc is not None :
            px, py = self._get_pix(*self._current_radar_loc)
            x = int(px + 4800*math.cos(math.radians(self._current_radar_bearing-90)))
            y = int(py + 4800*math.sin(math.radians(self._current_radar_bearing-90)))
            pygame.draw.line(surface, (0,255,0), self._get_pix(*self._current_radar_loc), (x,y), 2) 
        for bear in self._radarlist.keys() :
            t_loc = self._radarlist[bear]
            if t_loc is None :
                del self._radarlist[bear]
            else :
                self.draw_blip(self._get_pix(*t_loc), (100,255,100))

    def draw_blip(self, position, color) :
        x, y = position
        r, g, b = color
        pygame.draw.circle(surface, (r-100, g-100, b-100), (x,y), 6, 0)
        pygame.draw.circle(surface, (r,g,b), (x,y), 4, 0)

    def draw_node(self, position, type, uid) :
        Font = pygame.font.Font(None,20)
        text = Font.render(','.join(str(n) for n in self._aaron_sucks[uid]) + (' (%s)' % uid),1,(0,0,0))

        x, y = position
        if self._nodecolor.has_key(type) :
            r,g,b = self._nodecolor[type]
        else :
            r,g,b = (100,100,100)

        pygame.draw.circle(surface, (255,255,255), (x,y), 10, 0)
        pygame.draw.circle(surface, (r,g,b), (x,y), 6, 0)
        pygame.draw.circle(surface, (r-100,g-100,b-100), (x,y), 8, 3)
        surface.blit(text,(x+7,y+7))

    def draw_correlation(self) :
        self._correlation_lock.acquire()
        for uid, correlation in self._correlations.iteritems() :
            p1 = self._get_pix(*correlation[0])
            p2 = self._get_pix(*correlation[1])
            num_ais = 6.0
            color = ((255.0 / num_ais) * uid)
            pygame.draw.circle(surface, (color, color, color), p1, 13, 3)
            pygame.draw.circle(surface, (color, color, color), p2, 13, 3)
            pygame.draw.line(surface, (255, 0, 255), p1, p2, 5)
        self._correlation_lock.release()

    def draw_links(self) :
        self._link_lock.acquire()
        for link, up in self._links.iteritems() :
           if up :
               if self._nodelist.has_key(link[0]) and self._nodelist.has_key(link[1]) :
                   p1 = self._get_pix(*self._nodelist[link[0]][0])
                   p2 = self._get_pix(*self._nodelist[link[1]][0])
                   pygame.draw.line(surface, (255, 0, 0), p1, p2, 2)
        self._link_lock.release()

    def draw_fields(self) :
        self._fields_lock.acquire()
        for field in self._fields.values() :
            field_poly = []
            for point in field :
                field_poly.append(self._get_pix(*point))
            pygame.draw.polygon(surface,(0,0,255),field_poly,1)
        self._fields_lock.release()

    def draw_cameranodes(self) :
        self._cameranodes_lock.acquire()
        for uid in self._cameranodes.keys() :
            nodes = self._cameranodes[uid]
            for node in nodes :
                lat, lon, agl = node
                x, y = self._get_pix(lat, lon)
                box_width = 20
                pygame.draw.rect(surface,(0,0,255),(x-(box_width/2),y-(box_width/2),box_width,box_width),1)
        self._cameranodes_lock.release()

    def draw_threats(self) :
        self._threat_lock.acquire()
        for uid in self._threats.keys() :
            loc = self._threats[uid]
            pos = self._get_pix(*loc)
            pygame.draw.circle(surface, (255,0,0), pos, 10, 1)
            pygame.draw.circle(surface, (255,0,0), pos, 15, 1)
            pygame.draw.circle(surface, (255,0,0), pos, 20, 1)
        self._threat_lock.release()

    def draw_divert(self) :
        self._divert_lock.acquire()
        for point in self._divert_points:
            x, y = point
            pygame.draw.circle(surface,(255,0,255),(x,y),5)
        self._divert_lock.release()

    def draw(self) :
        self.draw_links()
        self.draw_nodes()
        self.draw_radar()
        self.draw_correlation()
        self.draw_fields()
        self.draw_cameranodes()
        self.draw_threats()
        self.draw_chem_sensors()
        self.draw_divert()
        self.draw_sonar()

    def main(self) :
        
        def redraw(move=(0,0)) :
            global window_center
            pygame.display.flip()
            new = map(operator.sub, window_center, move)
            surface.blit(image_surface,new)
            poc.draw()
            return new

        pygame.init()
        pygame.display.set_caption('Operations Center')
        image_surface = pygame.image.load('map_big.png')
        signal.signal(signal.SIGINT, quit)
        redraw()
        dx, dy, ux, uy = 0,0,0,0
        gotFirst = False
        b1x, b1y, b2x, b2y = 0,0,0,0
        boundFirst = False
        divert = False

        while True:
            global center
            global window_center
            # Quit code
            for event in pygame.event.get():
                if event.type == QUIT:
                    quit(None, None)
            
            # Detecting 'shift' keys
            if pygame.mouse.get_pressed()[0] and pygame.key.get_mods() & KMOD_SHIFT :
                if not boundFirst :
                    b1x, b1y = pygame.mouse.get_pos()
                    boundFirst = True
                else :
                    b2x, b2y = pygame.mouse.get_pos()
                    pygame.draw.rect(surface,(0,0,255),(b1x,b1y,b2x-b1x,b2y-b1y),1)
            elif pygame.mouse.get_pressed()[0] and pygame.key.get_mods() & KMOD_CTRL :
                x,y = pygame.mouse.get_pos()
                if(self._divert_points.count([x,y]) == 0):
                    self._divert_lock.acquire()
                    self._divert_points.append([x,y])
                    self._divert_lock.release()
            elif pygame.mouse.get_pressed()[2] and pygame.key.get_mods() & KMOD_CTRL :
                divert = True
            elif pygame.mouse.get_pressed()[0] :
                if not gotFirst :
                    dx, dy = pygame.mouse.get_pos()
                    gotFirst = True
                ux, uy = pygame.mouse.get_pos()
                center = redraw((dx-ux, dy-uy)) 
            else:
                if boundFirst :
                    poc.send_bound(1, b1x, b1y, b2x, b2y)
                    boundFirst = False
                if gotFirst :
                    window_center = redraw((dx-ux, dy-uy)) 
                    dx, dy, ux, uy = 0,0,0,0
                if divert:
                    poc.send_divert(self._divert_points)
                    #self._divert_points[:] = []
                    divert = False
                gotFirst = False    
            redraw((dx-ux, dy-uy)) 
        
if len(sys.argv) <= 2 :
    print 'USAGE: python draw.py <hostname> <port>'
    quit(None, None)

try : 
    poc = ProofOfConcept(sys.argv[1], int(sys.argv[2]))
except socket.error :
    print 'Invalid host or port, or TCP forwarder not started. Exiting.'
    quit(None, None)

poc.main()
