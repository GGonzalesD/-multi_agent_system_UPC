import networkx as nx
import random as random
import matplotlib.pyplot as plt
import math
import numpy as np

import pygame
import pygame.locals as lcs
from sympy import ordered
import gui
from key_manager import KeyManager

## GRAPH

def draw_graph(graph, pos):
    nx.draw(graph, pos, node_color='b', node_size=20, with_labels=False)
    plt.title('Road Network')
    plt.show()

def generate_2D_graph(n, coef=-1):
    graph = nx.grid_2d_graph(n, n) # Grilla de n x n
    if coef > 0:
        nb_ = int ( len(list(graph.nodes)) * coef )
        random_edge(graph, nb_)
    pos = nx.spring_layout(graph, iterations = 100)
    graph.remove_edges_from(list(nx.isolates(graph))) # Eliminar los sin conexion
    graph = graph.to_directed()
    return graph, pos

def random_edge(graph, nb_edges, delete=True):
    edges = list(graph.edges)
    nonedges = list(nx.non_edges(graph))
    if delete:
        chosen_edges = random.sample(edges, nb_edges)
        for edge in chosen_edges:
            graph.remove_edge(edge[0], edge[1])
    else:
        chosen_nonedges = random.sample(nonedges, nb_edges)
        for nonedge in chosen_nonedges:
            graph.add_edge(nonedge[0], nonedge[1])
    return graph



class Agent:
    id = 0
    agents = []
    def __init__(self):
        self.id = Agent.id
        self.alive = True
        Agent.id += 1
        Agent.agents.append(self)
    
    @classmethod
    def clear(cls):
        cls.id = 0
        cls.agents.clear()

    def __repr__(self):
        return f"Agent@{self.id}$[A:{self.alive}]"

    def update(self):
        pass
    
    def decide(self):
        pass

class RestaurantAgent(Agent):

    local_find = 10
    locals = []

    agents = []

    def __init__(self, max_orders):
        super(RestaurantAgent, self).__init__()
        global graph, pos
        
        self.max_orders = max_orders
        self.orders = [None for _ in range(self.max_orders)]
        self.n_orders = 0

        self.position = None
        self.node = None

        for _ in range(RestaurantAgent.local_find):
            p = random.choice(list(graph.nodes))
            self.position = list(pos[p])
            self.node = p
            if not p in RestaurantAgent.locals:
                self.locals.append(p)
                break
        
        RestaurantAgent.agents.append(self)
    
    @property
    def has_orders(self):
        return self.n_orders < self.max_orders
    
    def make_order(self, client):
        for i in range(self.max_orders):
            if self.orders[i] == None:
                self.orders[i] = [client, random.randint(2, 12), None]
                self.n_orders += 1
                break

    def __repr__(self):
        return f"Restaurant@{self.id}$[A:{self.alive},O:{self.orders}]"
    
    def update(self):
        for orden in self.orders:
            if orden != None:
                orden[1] -= 1
    
    def decide(self):
        pass

class ClientAgent(Agent):

    agents = []

    def __init__(self):
        super(ClientAgent, self).__init__()
        p = random.choice(list(graph.nodes))
        self.position = list(pos[p])
        self.node = p
        self.order = None
        self.tick = 0
        self.tick_limit = 1000
        self.hungry = False
        self.waiting = False

        ClientAgent.agents.append(self)

    def recibir(self):
        self.waiting = False
        self.hungry = False
        self.tick_limit = random.randint(10000, 15000)
        self.tick = 0

    def update(self):
        self.tick += 1

        if self.tick > self.tick_limit:
            self.tick = 0
            if not self.hungry: # Si no tiene hambre, espera hasta que tenga hambre
                self.hungry = True
                self.tick_limit = random.randint(100, 150)
            elif not self.waiting: # Si no esta esperando nada
                r = random.choice(RestaurantAgent.agents)
                if r.has_orders:
                    self.tick_limit = random.randint(10000, 14000)
                    self.waiting = True
                    r.make_order(self)
                else:
                    self.tick_limit = random.randint(100, 140)
            else:
                self.tick_limit = random.randint(100, 140)

class DriverAgent(Agent):

    agents = []

    def __init__(self, trip=None):
        super(DriverAgent, self).__init__()
        global pos, graph
        
        if trip == None:            
            n1, n2 = random.sample(list(graph.nodes), 2)
            trip = nx.shortest_path(graph, n1, n2)
        self.package = None

        self.esquina = False
        self.final = trip[-1]
        self.current = trip[0]
        self.last = self.current
        self.position = list(pos[self.current])
        self.ocupado = False
        self.rest = None
        
        self.trip = trip

        DriverAgent.agents.append(self)

    def update_trip(self, trip):
        self.final = trip[-1]
        self.current = trip[0]
        self.trip = trip

    def __repr__(self):
        return f"Driver@{self.id}$[A:{self.alive},T:{self.trip}]"
    
    def update(self):
        global graph

        # Recoger pedido
        if self.ocupado:
            if self.package == None:
                if len(self.trip) == 0:
                    if self.rest.n_orders > 0:
                        for i in range(self.rest.max_orders):
                            if self.rest.orders[i] != None and self.rest.orders[i][2] == self:
                                cli, _, _ = self.rest.orders[i]
                                self.package = cli
                                trip = nx.shortest_path(graph, self.last, cli.node)
                                self.update_trip(trip)
                                self.rest.n_orders -= 1
                                self.rest.orders[i] = None
                                self.rest = None
                                #print("Paquete recogido")
                                break
                    else:
                        self.rest = None
                        self.ocupado = False
            else:
                if len(self.trip) == 0:
                    self.package.recibir()
                    #print(f"Delivery#{self.id} entrego el paquete a Cliente#{self.package.id}")
                    self.package = None
                    self.ocupado = False

        # Buscar un restaurante con pedidos
        if self.esquina and not self.ocupado:
            self.rest = random.choice(RestaurantAgent.agents)
            if self.rest.n_orders > 0:
                for i in range(self.rest.max_orders):
                    if self.rest.orders[i] != None and self.rest.orders[i][1] < 1 and self.rest.orders[i][2] == None:
                        self.rest.orders[i][2] = self
                        trip = nx.shortest_path(graph, self.last, self.rest.node)
                        self.update_trip(trip)
                        self.ocupado = True
                        #print(f"Delivery#{self.id} de camino a restaurante#{self.rest.id} por una orden para Cliente#{self.rest.orders[i][0].id}")
                        break

        # Diambular
        if not self.alive and not self.ocupado:
            n = random.choice(list(graph.nodes))
            # recuperados el camino mas corto entre los 2 nodos
            trip = nx.shortest_path(graph, self.current, n)
            self.update_trip(trip)
            self.alive = True
            #print(f"Driver@{self.id}$Update:{self.trip}")

    def decide(self):
        global pos
        if len(self.trip) > 0:
            crrt_p = pos[self.current]
            d = math.hypot(crrt_p[0]-self.position[0], crrt_p[1]-self.position[1])
            if  d < 1: # Conductor llega a una esquina
                self.esquina = True
                self.last = self.trip.pop(0)
                if len(self.trip):
                    self.current = self.trip[0]
                #print(f"Driver@{self.id}$[from:{self.last},to:{self.current}]")
            else: # Seguir ruta
                self.esquina = False
                g = math.atan2(self.position[1]-crrt_p[1], self.position[0]-crrt_p[0])
                if self.ocupado:
                    self.position[0] -= math.cos(g)*0.41
                    self.position[1] -= math.sin(g)*0.41
                else:
                    self.position[0] -= math.cos(g)*0.1
                    self.position[1] -= math.sin(g)*0.1
        else:
            self.alive = False
            #print(f"Driver@{self.id}$Arrived")



pygame.init()

size = 480
complex = 2
graph, pos = generate_2D_graph(complex, coef=0.2)

#for k in pos:
#    pos[k] = (size//2)*pos[k] + (size//2, size//2)



# Modo de ejecucion
# 0: Configuración
# 1: Simulación
# 2: Pausa

class DATA:
    MODE = 0
    SURFACE = None

font = pygame.font.SysFont("Fira code", 40)
win = pygame.display.set_mode((size, size))
manager = KeyManager()

gui.Widget((100, 20), "Clients", font, (255, 255, 255))
rng_clients = gui.Range((100, 50), 130, 2000, font, (255, 255, 255), (40, 100, 40))
gui.Widget((100, 80), "Distributors", font, (255, 255, 255))
rng_distributors = gui.Range((100, 110), 130, 300, font, (255, 255, 255), (100, 100, 40))
gui.Widget((100, 140), "Restaurants", font, (255, 255, 255))
rng_restaurants = gui.Range((100, 170), 130, 100, font, (255, 255, 255), (40, 100, 100))
gui.Widget((100, 200), "MaxOrders", font, (255, 255, 255))
rng_maxord = gui.Range((100, 230), 130, 10, font, (255, 255, 255), (40, 100, 100))
gui.Widget((100, 260), "Map complex", font, (255, 255, 255))
rng_map_complex = gui.Range((100, 290), 130, 40, font, (255, 255, 255), (200, 100, 30))

def fn_makemap():
    global graph, pos
    complex = rng_map_complex.get_int()
    graph, pos = generate_2D_graph(complex, coef=0.2)
    for k in pos:
        pos[k] = (size//2)*pos[k] + (size//2, size//2)

    DATA.SURFACE = pygame.Surface((size, size))
    DATA.SURFACE.fill((10, 10, 10))

    for p1, p2 in graph.edges():
        p1 = pos[p1]
        p2 = pos[p2]
        pygame.draw.line(DATA.SURFACE, (40, 40, 40), p1, p2, 2)

def fn_create():
    if DATA.SURFACE == None:
        fn_makemap()

    Agent.clear()
    for _ in range(rng_restaurants.get_int()):
        RestaurantAgent(rng_maxord.get_int())
    for _ in range(rng_clients.get_int()):
        ClientAgent()
    for _ in range(rng_distributors.get_int()):
        DriverAgent()
    DATA.MODE = 1

btn_create = gui.Button((144, 450), "Preview Map", font, (255, 255, 255), (150, 70, 30), fn_makemap)
btn_create = gui.Button((320, 450), "Create", font, (255, 255, 255), (30, 70, 30), fn_create)



while True:
    manager.update_manager(pygame.event.get())

    if manager.key_check(lcs.K_SPACE):
        #print(pygame.mouse.get_pos())
        pass

    if DATA.MODE == 0:
        win.fill((0, 0, 0))

        if DATA.SURFACE != None:
            sur = pygame.transform.scale(DATA.SURFACE, (250, 250))
            win.blit(sur, (210, 15))

        for widget in gui.Widget.widgets:
            widget.update(win, manager)
        pass
    elif DATA.MODE == 1:
        win.blit(DATA.SURFACE, (0, 0))
        for a in Agent.agents:
            if type(a) == DriverAgent:
                if a.package != None:
                    pygame.draw.circle(win, (255, 255, 0), a.position, 3)
                else:
                    if a.ocupado:
                        pygame.draw.circle(win, (255, 100, 50), a.position, 3)
                    else:
                        pygame.draw.circle(win, (0, 120, 200), a.position, 3)
                    
            elif type(a) == RestaurantAgent:
                pygame.draw.circle(win, (100, 255, 255), a.position, 7)
            else:
                if a.waiting:
                    pygame.draw.circle(win, (255, 0, 255), a.position, 3)
                elif a.hungry:
                    pygame.draw.circle(win, (100, 255, 100), a.position, 3)
                else:
                    pygame.draw.circle(win, (100, 100, 100), a.position, 3)
            a.update()
            a.decide()

        if manager.key_check(lcs.K_SPACE):
            ords = 0
            con_d = 0
            rep = 0
            for a in DriverAgent.agents:
                if a.rest != None:
                    rep += 1
            for a in RestaurantAgent.agents:
                for o in a.orders:
                    if o!=None and o[1] < 1:
                        ords += 1
                        if o[2] != None:
                            con_d += 1
            print(f"Ordenes Listas: {ords}")
            print(f"Ordenes ListasD: {con_d}")
            print(f"De camino al rest: {rep}")
            print(f"")

        if manager.key_check(lcs.K_q):
            DATA.MODE = 0
            Agent.clear()
    
    pygame.display.update()
