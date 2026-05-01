from tabnanny import check

import pygame
import sys
import random
import json

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
        self.quadtree_squares=[]
        self.centers_of_mass=[]

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


    def save(self):
        nodes_information=[]
        for node in self.nodes:
            nodes_information.append(node.pos)

        edges_information=[]
        for edge in self.edges:
            edges_information.append((edge.u,edge.v))

        data = {
            'nodes':nodes_information,
            'edges':edges_information
        }

        with open("saves/save.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Сохранено: {len(self.nodes)} вершин, {len(self.edges)} рёбер")

    def load(self):
        with open("saves/save.json", "r") as f:
            data = json.load(f)

        self.nodes = []
        self.edges = []

        for pos in data["nodes"]:
            self.nodes.append(Node(pos[0], pos[1]))

        for edge in data["edges"]:
            self.edges.append(Edge(edge[0], edge[1]))

        print(f"Загружено: {len(self.nodes)} вершин, {len(self.edges)} рёбер")

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
        phys.coulomb_force_apply(self)
        phys.force_attraction(self)
        phys.force_reduction(self)
        phys.reduction+=0.01
        self.apply_acceleration(1/60)

    def find_quadtree_root(self):
        min_x=min_y=float('inf')
        max_x=max_y=float('-inf')
        for node in self.nodes:
            x,y=node.pos
            if x<min_x:
                min_x=x
            if x>max_x:
                max_x=x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
        side_x=max_x-min_x
        side_y=max_y-min_y
        side=max(side_x,side_y)
        return min_x,min_y,side

    def build_quadtree(self):
        eps=1e-9
        self.quadtree_squares = []

        root_square_x1,root_square_y1,root_square_size = self.find_quadtree_root()
        root_square_x2,root_square_y2 = root_square_x1+root_square_size,root_square_y1+root_square_size
        self.quadtree_squares.append(((root_square_x1,root_square_y1),(root_square_x2,root_square_y2)))


        quadtree_root=QuadTree(root_square_x1,root_square_y1,root_square_x2,root_square_y2)

        for i in range(len(self.nodes)):
            current_quadtree = quadtree_root
            node_x,node_y=self.nodes[i].pos

            while current_quadtree is not None:
                current_quadtree.count+=1
                current_quadtree.center_x+=node_x
                current_quadtree.center_y+=node_y


                if current_quadtree.count>current_quadtree.capacity and not current_quadtree.is_divided:
                    if current_quadtree.level<=current_quadtree.max_level:
                        current_quadtree.divide(self)
                    else:
                        self.nodes[current_quadtree.nodes[0]].pos[0]+=random.uniform(-1, 1)
                        self.nodes[current_quadtree.nodes[0]].pos[0]+=random.uniform(-1, 1)
                if current_quadtree.is_divided:
                    for child in current_quadtree.childs:
                        x1,y1,x2,y2 = child.boundary
                        if x1-eps<=node_x<=x2+eps and y1-eps<=node_y<=y2+eps:

                            current_quadtree = child
                            break

                else:
                    current_quadtree.nodes.append(i)
                    current_quadtree = None

        self.centers_of_mass=[]
        stack=[quadtree_root]

        while stack:
            current=stack.pop()
            if current.count>0:
                c_x=current.center_x/current.count
                c_y=current.center_y/current.count
                self.centers_of_mass.append(((c_x,c_y),current.level,current.count))
            if current.childs:
                stack+=current.childs



        return quadtree_root

    def draw_quadtree(self,cam,phys):
        for point1,point2 in self.quadtree_squares:
            x1,y1 = cam.real_to_screen(point1)
            x2,y2 = cam.real_to_screen(point2)

            side = x2-x1
            pygame.draw.rect(screen, (200, 200, 200),
                             (x1,y1,side,side), 2)

        for center_of_mass,level,count in self.centers_of_mass:

            x_center, y_center = cam.real_to_screen(center_of_mass)
            if level == 1:
                pygame.draw.circle(screen,'blue',(x_center,y_center),(1*count)*cam.zoom)
            elif level == 2:
                pygame.draw.circle(screen, 'green', (x_center, y_center), (1 * count) * cam.zoom)
            else:
                pygame.draw.circle(screen, 'red', (x_center, y_center), (1 * count) * cam.zoom)




class QuadTree:
    def __init__(self,x1,y1,x2,y2):
        self.boundary=(x1,y1,x2,y2)
        self.side = x2-x1
        self.capacity = 1
        self.is_divided = False
        self.childs= []
        self.nodes = []
        self.count = 0
        self.center_x=0
        self.center_y=0
        self.level=1
        self.max_level=20


    def divide(self,gr):
        eps = 1e-9
        side = self.side / 2
        x, y = self.boundary[0], self.boundary[1]
        positions = [(x, y), (x + side, y), (x, y + side), (x + side, y + side)]

        for pos_x,pos_y in positions:
            child = QuadTree(pos_x,pos_y,pos_x+side,pos_y+side)
            child.level=self.level+1
            self.childs.append(child)
            gr.quadtree_squares.append(((pos_x,pos_y),(pos_x+side,pos_y+side)))

        for i in self.nodes:
            node_x,node_y=gr.nodes[i].pos
            for j, (pos_x, pos_y) in enumerate(positions):
                if pos_x-eps<=node_x<=pos_x+side+eps and pos_y-eps<=node_y<=pos_y+side+eps:
                    self.childs[j].nodes.append(i)
                    self.childs[j].count+=1
                    self.childs[j].center_x += node_x
                    self.childs[j].center_y += node_y
                    break

        self.nodes=[]
        self.is_divided = True


    def check_if_node_in_boundary(self,coordinates):
        x,y=coordinates
        bx1,by1,bx2,by2=self.boundary
        eps = 1e-9
        return bx1-eps<=x<=bx2+eps and by1-eps<=y<=by2+eps





class Physics:
    def __init__(self):
        self.repulsion=1000000
        self.reduction=0
        self.min_dist=5
        self.attraction=30
        self.good_len=20
        self.max_force = 10000000


    def coulomb_force(self,x1,y1,x2,y2,count):
        rx = x1 - x2
        ry = y1 - y2
        if abs(rx) < self.min_dist:  rx = random.uniform(-1,1)
        if abs(ry) < self.min_dist:  rx = random.uniform(-1,1)
        sqr_c = (ry / rx) * (ry / rx)

        d = dist((x1, y1), (x2, y2))
        if d == 0:
            rx = random.uniform(-1, 1)
            ry = random.uniform(-1, 1)

        if d < self.min_dist: d = self.min_dist
        force = self.repulsion * count / (d * d)
        if force > self.max_force:
            force = self.max_force

        sqr_force = force * force
        sqr_force_x = sqr_force / (1 + sqr_c)
        sqr_force_y = sqr_force - sqr_force_x

        force_x = sqrt(sqr_force_x) * (1 if rx > 0 else -1)
        force_y = sqrt(sqr_force_y) * (1 if ry > 0 else -1)

        return force_x,force_y


    def coulomb_force_apply(self,gr):
        quadtree = gr.build_quadtree() # корень дерева
        theta = 1
        for i,node in enumerate(gr.nodes):
            if node.fixed:
                continue
            x1, y1 = node.pos
            total_force=[0,0]
            stack=[quadtree]
            while stack:
                current = stack.pop()
                count = current.count
                if count == 0:
                    continue

                x2 = current.center_x / count
                y2 = current.center_y / count
                if not current.is_divided:
                    if current.check_if_node_in_boundary((x1,y1)):
                        continue
                    else:
                        force_x,force_y = self.coulomb_force(x1,y1,x2,y2,count)
                        total_force[0] += force_x
                        total_force[1] += force_y
                else:
                    side=current.side
                    d=dist((x1,y1),(x2,y2))
                    if d>0 and side/d<theta: # тут d>0 исключительно чтобы не было ошибки при ==0, т.к. при d==0 side/d < theta невозможно
                        if current.check_if_node_in_boundary((x1,y1)):
                            another_x2 = (current.center_x-x1) / (count-1)
                            another_y2 = (current.center_y-y1) / (count-1)
                            force_x, force_y = self.coulomb_force(x1, y1, another_x2, another_y2, count-1)

                        else:
                            force_x,force_y = self.coulomb_force(x1,y1,x2,y2,count)

                        total_force[0] += force_x
                        total_force[1] += force_y
                    else:
                        stack+=current.childs


            node.acc[0] += total_force[0]
            node.acc[1] += total_force[1]







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
            force = (d - self.good_len) * self.attraction

            sqr_force = force * force
            sqr_force_x = sqr_force / (1 + sqr_c)
            sqr_force_y = sqr_force - sqr_force_x

            force_x = sqrt(sqr_force_x) * (-1 if rx > 0 else 1)
            force_y = sqrt(sqr_force_y) * (-1 if ry > 0 else 1)

            if force < 0:
                force_x = -force_x
                force_y = -force_y

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
        self.show_grid=True
        self.show_quadtree=False

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
                physics.reduction=0

            if event.key == pygame.K_r:
                camera.x=0
                camera.y=0
                camera.zoom=1
                graph.nodes=[]
                graph.edges=[]

            if event.key == pygame.K_g:
                state.show_grid = not state.show_grid
            if event.key == pygame.K_h:
                state.show_quadtree = not state.show_quadtree

            if event.key == pygame.K_F5:
                graph.save()
            if event.key == pygame.K_F9:
                graph.load()

            if event.key == pygame.K_UP:
                physics.repulsion *= 10

            if event.key == pygame.K_DOWN:
                physics.repulsion /= 10




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
                    # print(graph.nodes[state.selected_node].pos)
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

    screen.fill('white')
    if state.physics:
        graph.update_physics(physics)


    if state.show_quadtree:
        graph.draw_quadtree(camera, physics)


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
















