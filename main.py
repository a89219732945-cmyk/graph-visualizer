import pygame
import sys
import random

from algorithms import bfs, dfs
from math import dist,sqrt


class Node:
    def __init__(self,x,y):
        self.pos = [x,y]
        self.vel = [0,0]
        self.acc = [0,0]
        self.fixed = False

    def __str__(self):
        return f'Node {self.pos}'

    def is_clicked(self,x,y,r):
        d = dist(self.pos,(x,y))
        return d<r

class Edge:
    def __init__(self,u,v):
        self.u=u
        self.v=v

    def __str__(self):
        return f'Edge {self.u} {self.v}'

    def distance_to_point(self,x,y):
        x1,y1=graph.nodes[self.u].pos
        x2,y2=graph.nodes[self.v].pos
        AB = dist((x1, y1), (x2, y2))
        if AB == 0:
            return dist((x, y), graph.nodes[self.u].pos)
        AC = dist((x1, y1), (x, y))
        BC = dist((x2, y2), (x, y))
        AH = (AC * AC + AB * AB - BC * BC) / (2 * AB)
        BH = AB - AH
        if AH >= AB:
            return BC
        elif BH >= AB:
            return AC
        else:
            CH = sqrt(AC * AC - AH * AH)
            return CH


class Graph:
    def __init__(self):
        self.nodes=[]
        self.edges=[]
        self.cell_size = 200

    def __str__(self):
        return f'nodes {self.nodes} \n edges {self.edges}'

    def clicked_node_index(self,x,y,r):
        for i, node in enumerate(self.nodes):
            if node.is_clicked(x,y,r):
                return i
        return None

    def remove_node(self,index):
        self.nodes.pop(index)
        new_edges = []
        for edge in self.edges:
            if index in (edge.u,edge.v):
                continue
            if edge.u>index:
                edge.u-=1
            if edge.v>index:
                edge.v-=1
            new_edges.append(edge)
        self.edges = new_edges

    def remove_nearest_edge_if_can(self,x,y,d):
        for i,edge in enumerate(self.edges):
            if edge.distance_to_point(x,y)<d:
                self.edges.pop(i)
                break

    def draw(self,cam, visited_nodes=None, visited_edges=None, way_nodes=None,way_edges=None,queue_nodes=None):

        for edge in self.edges:
            u,v=edge.u,edge.v
            node_1_real = self.nodes[u].pos
            node_2_real = self.nodes[v].pos
            node_1_screen = cam.real_to_screen(node_1_real)
            node_2_screen = cam.real_to_screen(node_2_real)
            if way_edges and way_edges[u][v]:
                pygame.draw.line(screen, 'green', node_1_screen, node_2_screen, 4)
            elif visited_edges and visited_edges[u][v]:
                pygame.draw.line(screen, 'orange', node_1_screen, node_2_screen, 4)
            else:
                pygame.draw.line(screen, 'blue', node_1_screen, node_2_screen, 4)


        for i, node in enumerate(self.nodes):
            node_real=node.pos
            node_screen=cam.real_to_screen(node_real)

            if i == state.start_node:
                pygame.draw.circle(screen, 'green', node_screen, radius + 2, 4)
            elif i == state.end_node:
                pygame.draw.circle(screen, 'red', node_screen, radius + 2, 4)

            if state.link_mode:
                if i == state.first_link:
                    pygame.draw.circle(screen, 'green', node_screen, radius)
                else:
                    pygame.draw.circle(screen, 'grey', node_screen, radius)
            else:
                if i == state.selected_node:
                    pygame.draw.circle(screen, 'red', node_screen, radius)
                elif way_nodes and way_nodes[i]:
                    pygame.draw.circle(screen, 'green', node_screen, radius)
                elif visited_nodes and visited_nodes[i]:
                    pygame.draw.circle(screen, 'red', node_screen, radius)
                elif queue_nodes and queue_nodes[i]:
                    pygame.draw.circle(screen, 'blue', node_screen, radius)
                elif state.visualisation:
                    pygame.draw.circle(screen, 'white', node_screen, radius)
                else:
                    pygame.draw.circle(screen, 'black', node_screen, radius)
            pygame.draw.circle(screen, 'darkgrey', node_screen, radius, 4)


    # def draw_grid(self):
    #     if not state.show_grid:
    #         return
    #     w,h=screen.get_size()
    #
    #     top_left=(camera.x,camera.y)
    #     bottom_right=(camera.x+w/camera.zoom,camera.y+h/camera.zoom)

    def draw_grid(self, cam):
        if not state.show_grid:
            return

        w, h = screen.get_size()
        top_left = cam.screen_to_real((0, 0))
        bottom_right = cam.screen_to_real((w, h))

        min_cx = int(top_left[0] // self.cell_size)
        max_cx = int(bottom_right[0] // self.cell_size) + 1
        min_cy = int(top_left[1] // self.cell_size)
        max_cy = int(bottom_right[1] // self.cell_size) + 1

        for cx in range(min_cx,max_cx+1):
            x=cx*self.cell_size
            screen_x=(x-cam.x)*cam.zoom
            pygame.draw.line(screen,(200,200,200),(screen_x,0),(screen_x,h))

        for cy in range(min_cy,max_cy+2):
            y=cy*self.cell_size
            screen_y=(y-cam.y)*cam.zoom
            pygame.draw.line(screen,(200,200,200),(0,screen_y),(w,screen_y))





    def build_adjacency_list(self):
        graph = [[] for _ in range(len(self.nodes))]
        for edge in self.edges:
            u=edge.u
            v=edge.v
            graph[u].append(v)
            graph[v].append(u)
        return graph

    def apply_acceleration(self,dt):
        for node in self.nodes:
            if node.fixed:
                continue
            node.vel[0]+=node.acc[0]*dt
            node.vel[1]+=node.acc[1]*dt
            node.pos[0]+=node.vel[0]*dt
            node.pos[1]+=node.vel[1]*dt

    def update_physics(self,phys):
        for node in self.nodes:
            node.acc=[0,0]

        phys.coulomb_force(self)
        phys.force_attraction(self)
        phys.force_reduction(self)

        self.apply_acceleration(1/60)

    def build_grid(self):
        grid = {}
        for i, node in enumerate(self.nodes):
            node_x, node_y = node.pos
            cx = int(node_x // self.cell_size)
            cy = int(node_y // self.cell_size)
            key = (cx, cy)
            if key not in grid:
                grid[key] = []
            grid[key].append(i)
        return grid


class Physics:
    def __init__(self):
        self.repulsion=1000000
        self.reduction=0.5
        self.min_dist=1
        self.attraction=0.5
        self.good_len=100

        self.max_force = 10000000

    def coulomb_force(self,gr):
        grid = gr.build_grid()
        for node_1 in gr.nodes:
            if node_1.fixed:
                continue
            total_force=[0,0]
            x1, y1 = node_1.pos
            cx_1=int(x1//gr.cell_size)
            cy_1=int(y1//gr.cell_size)
            keys=[(cx_1+i,cy_1+j) for i in range(-1,2) for j in range(-1,2)]
            # print(keys)
            for key in keys:
                if key in grid:

                    cell = grid[key]
                    for index in cell:
                        node_2=gr.nodes[index]
                        if node_1==node_2:
                            continue

                        x2,y2=node_2.pos



                        rx=x1-x2
                        ry=y1-y2
                        if abs(rx)<self.min_dist:rx=self.min_dist
                        if abs(ry)<self.min_dist:ry=self.min_dist
                        sqr_c=(ry/rx)*(ry/rx)

                        d=dist((x1,y1),(x2,y2))
                        if d==0:
                            rx=random.uniform(-1,1)
                            ry=random.uniform(-1,1)

                        if d<self.min_dist:d=self.min_dist
                        force= self.repulsion / (d * d)
                        if force>self.max_force:
                            force=self.max_force



                        sqr_force = force*force
                        sqr_force_x = sqr_force/(1+sqr_c)
                        sqr_force_y = sqr_force - sqr_force_x

                        force_x = sqrt(sqr_force_x) * (1 if rx > 0 else -1)
                        force_y = sqrt(sqr_force_y) * (1 if ry > 0 else -1)


                        total_force[0]+=force_x
                        total_force[1]+=force_y
            node_1.acc[0] += total_force[0]
            node_1.acc[1] += total_force[1]

    def force_attraction(self,gr):
        for edge in gr.edges:
            u,v=edge.u,edge.v
            node_1=gr.nodes[u]
            node_2=gr.nodes[v]

            x1, y1 = node_1.pos
            x2, y2 = node_2.pos

            rx = x1 - x2
            ry = y1 - y2

            if rx == 0: rx = self.min_dist
            if ry == 0: ry = self.min_dist

            sqr_c = (ry / rx) * (ry / rx)

            d = dist((x1, y1), (x2, y2))
            if d<self.good_len:
                k=-1
            else:
                k=1
            force = d * self.attraction
            sqr_force = force * force
            sqr_force_x = sqr_force / (1 + sqr_c)
            sqr_force_y = sqr_force - sqr_force_x

            force_x = sqrt(sqr_force_x) * (-k if rx > 0 else k)
            force_y = sqrt(sqr_force_y) * (-k if ry > 0 else k)

            # force_x = sqrt(sqr_force_x) * (-1 if rx > 0 else 1)
            # force_y = sqrt(sqr_force_y) * (-1 if ry > 0 else 1)

            node_1.acc[0]+=force_x
            node_1.acc[1]+=force_y

            node_2.acc[0] -= force_x
            node_2.acc[1] -= force_y

    def force_reduction(self,gr):
        for node in gr.nodes:
            if node.fixed:
                continue
            vx,vy=node.vel
            anti_force_x=vx*(-self.reduction)
            anti_force_y=vy*(-self.reduction)

            node.acc[0]+=anti_force_x
            node.acc[1]+=anti_force_y







class Camera:
    def __init__(self):
        self.x=0
        self.y=0
        self.zoom=1
        self.min_zoom=0.1
        self.max_zoom=50
        self.pan_start_x = None  # Экранная координата мыши в момент нажатия
        self.pan_start_y = None
        self.pan_start_cam_x = None  # Состояние камеры в момент нажатия
        self.pan_start_cam_y = None

    def __str__(self):
        return f'{self.x} {self.y} {self.zoom}'

    def screen_to_real(self, coordinates):
        x,y=coordinates
        real_x = x / self.zoom + self.x
        real_y = y / self.zoom + self.y
        return [real_x, real_y]

    def real_to_screen(self, coordinates):
        x, y = coordinates
        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom
        return [screen_x, screen_y]

    def zoom_in(self,coordinates):
        if self.zoom*1.1<=self.max_zoom:
            real_x,real_y=coordinates
            self.zoom *= 1.1
            delta_x = (real_x - self.x) / 1.1
            delta_y = (real_y - self.y) / 1.1
            self.x = real_x - delta_x
            self.y = real_y - delta_y

    def zoom_out(self,coordinates):
        if self.zoom / 1.1 >= self.min_zoom:
            real_x, real_y = coordinates
            self.zoom /= 1.1
            delta_x = (real_x - self.x) * 1.1
            delta_y = (real_y - self.y) * 1.1
            self.x = real_x - delta_x
            self.y = real_y - delta_y

    def start_pan(self, mouse_screen_pos):
        self.pan_start_x, self.pan_start_y = mouse_screen_pos
        self.pan_start_cam_x, self.pan_start_cam_y = self.x, self.y

    def panning(self, mouse_screen_pos):
        if self.pan_start_x is None:
            return
        mx, my = mouse_screen_pos

        delta_x = mx - self.pan_start_x
        delta_y = my - self.pan_start_y

        self.x = self.pan_start_cam_x - delta_x / self.zoom
        self.y = self.pan_start_cam_y - delta_y / self.zoom


class AlgorithmController:
    def __init__(self):
        self.algorithms=[bfs,dfs]
        self.algorithm_index=0
        self.steps=[]
        self.current_step=0
        self.visited_nodes=[]
        self.visited_edges=[]
        self.queue_nodes = []
        self.way_nodes=[]
        self.way_edges=[]
        self.steps_count=0


    def start(self,gr,start,end):
        l=len(gr.nodes)
        adjacency_list=gr.build_adjacency_list()
        self.steps=self.algorithms[self.algorithm_index](l,adjacency_list,start,end)

        self.visited_nodes=[False]*l
        self.way_nodes=[False]*l
        self.queue_nodes=[False]*l

        self.visited_edges=[[False]*l for _ in range(l)]
        self.way_edges = [[False]*l for _ in range(l)]

        self.steps_count=len(self.steps)
        self.current_step = 0

    def next_step(self):

        action, *args = self.steps[self.current_step]
        if action == 'finish':
            self.way_nodes[args[0]]=True
        elif action == 'edge':
            u, v = args
            self.visited_nodes[u] = True
            self.visited_nodes[v] = True
            self.visited_edges[u][v]=True
            self.visited_edges[v][u] = True
        elif action == 'queue':
            self.queue_nodes[args[0]]=True
        elif action == 'return':
            u, v = args
            self.way_nodes[args[0]]=True
            self.way_edges[u][v]=True
            self.way_edges[v][u]=True
        self.current_step+=1


    def previous_step(self):
        self.current_step-=1
        action, *args = self.steps[self.current_step]
        if action == 'finish':
            self.way_nodes[args[0]]=False
        elif action == 'edge':
            u, v = args
            self.visited_nodes[v] = False
            self.visited_edges[u][v]=False
            self.visited_edges[v][u] = False
        elif action == 'queue':
            self.queue_nodes[args[0]]=False
        elif action == 'return':
            u, v = args
            self.way_nodes[args[0]]=False
            self.way_edges[u][v] = False
            self.way_edges[v][u] = False



class EditorState:
    def __init__(self):
        self.selected_node = None
        self.clicked_on_node = False
        self.link_mode = False
        self.first_link = None
        self.panning = False
        self.visualisation = False
        self.start_node=None
        self.end_node=None
        self.physics=False
        self.show_grid=False

    def link_mode_off(self):
        self.link_mode=False
        self.first_link=None

    def start_end_node_remove(self):
        self.start_node = None
        self.end_node = None
        print('Выбор вершин сброшен')

    def start_end_node_append(self):
        if self.start_node is None:
            self.start_node = self.selected_node
        else:
            if self.selected_node != self.start_node:
                self.end_node = self.selected_node
        state.selected_node = None











def new_edge():
    if state.clicked_on_node:
        if state.first_link is None:
            state.first_link = state.selected_node
        elif state.selected_node != state.first_link:
            exists=False
            u, v = state.first_link, state.selected_node
            for edge in graph.edges:
                if (edge.u == u and edge.v == v) or (edge.u == v and edge.v == u):
                    exists=True
                    break
            if not exists:
                graph.edges.append(Edge(state.first_link, state.selected_node))
            else:
                print('Already exists')
            state.first_link = None
    else:
        state.first_link = None




pygame.init()

screen=pygame.display.set_mode((1200,800))
screen.fill('white')
pygame.display.set_caption('Graph Visualizer')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

radius = 30
state = EditorState()
graph=Graph()
camera = Camera()
physics = Physics()

algorithm=AlgorithmController()

running=True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                if not state.visualisation:
                    state.link_mode = not state.link_mode
                    state.first_link = None
                    print(f"Режим связей: {'ВКЛ' if state.link_mode else 'ВЫКЛ'}")

            if event.key == pygame.K_LEFT:
                if state.visualisation:
                    if algorithm.current_step>0:
                        algorithm.previous_step()
                        print(algorithm.current_step)
            if event.key == pygame.K_RIGHT:
                if state.visualisation:
                    if algorithm.current_step<algorithm.steps_count:
                        algorithm.next_step()
                        print(algorithm.current_step)

            if event.key == pygame.K_c:
                state.visualisation = not state.visualisation
                if state.visualisation and state.end_node is not None:
                    state.link_mode_off()
                    algorithm.start(graph,state.start_node,state.end_node)
                else:
                    state.visualisation=False
                print(f"Визуализация: {'ВКЛ' if state.visualisation else 'ВЫКЛ'}")
            if event.key == pygame.K_f:
                state.physics = not state.physics

            if event.key == pygame.K_r:
                camera.x=0
                camera.y=0
                camera.zoom=1

            if event.key == pygame.K_g:
                state.show_grid = not state.show_grid




        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not state.visualisation:
                x,y=camera.screen_to_real(event.pos)
                state.selected_node = graph.clicked_node_index(x,y,radius/camera.zoom)


                if state.selected_node is None:
                    state.clicked_on_node = False
                else:
                    state.clicked_on_node = True
                    graph.nodes[state.selected_node].fixed=True

                mods = pygame.key.get_mods()


                if not state.link_mode:
                    if not state.clicked_on_node:
                        if mods & pygame.KMOD_SHIFT:
                            state.start_end_node_remove()
                        else:
                            graph.nodes.append(Node(x,y))
                    else:
                        if mods & pygame.KMOD_SHIFT:
                            state.start_end_node_append()

                else:
                    new_edge()

            elif event.button == 2:
                camera.start_pan(event.pos)
                state.panning = True

            elif event.button == 3 and not state.visualisation:
                x,y=camera.screen_to_real(event.pos)

                node_flag = graph.clicked_node_index(x,y,radius/camera.zoom)
                if not state.link_mode:
                    if node_flag is not None:
                        graph.remove_node(node_flag)
                else:
                    graph.remove_nearest_edge_if_can(x,y,4/camera.zoom)


        if event.type == pygame.MOUSEMOTION:
            if state.panning:
                camera.panning(event.pos)



        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if state.selected_node is not None:
                    print(graph.nodes[state.selected_node].pos)
                    graph.nodes[state.selected_node].fixed = False
                    graph.nodes[state.selected_node].vel=[0,0]
                state.selected_node = None

            elif event.button == 2:
                state.panning = False
            elif event.button == 3:
                pass

        if event.type == pygame.MOUSEWHEEL:
            x, y = camera.screen_to_real(pygame.mouse.get_pos())
            wheel_direction = event.y
            if wheel_direction > 0:
                camera.zoom_in((x,y))
            elif wheel_direction<0:
                camera.zoom_out((x,y))





    if state.selected_node is not None and not state.link_mode and not state.visualisation:
        if state.selected_node<len(graph.nodes):
            graph.nodes[state.selected_node].pos = camera.screen_to_real(pygame.mouse.get_pos())


    if state.physics:
        graph.update_physics(physics)


    screen.fill('white')
    if state.show_grid:
        graph.draw_grid(camera)
    if state.visualisation:
        graph.draw(camera,
                   algorithm.visited_nodes,
                   algorithm.visited_edges,
                   algorithm.way_nodes,
                   algorithm.way_edges,
                   algorithm.queue_nodes
                   )
    else:
        graph.draw(camera)

    pygame.display.flip()
    clock.tick(60)




pygame.quit()
sys.exit()
















