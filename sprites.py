import math
import random

import pygame
import os
import config
from itertools import permutations
from queue import PriorityQueue


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        nodes = []
        visited = set()
        nodes.append(0)
        path = []
        while len(nodes) > 0:
            neighbors = []
            cost = []
            current = nodes.pop(0)
            if current in visited:
                continue
            cost = coin_distance[current]
            print(cost)
            neighbors = (sorted(range(len(cost)), key=lambda k: cost[k]))
            nodes = neighbors + nodes
            path.append(current)
            visited.add(current)
        return path + [0]


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = []
        minimum = float('inf')
        permu = list(permutations(range(1, len(coin_distance[0]))))
        # print(permu)
        for p in permu:
            cost = coin_distance[0][p[0]]
            for i in range(len(p) - 1):
                cost = cost + coin_distance[p[i]][p[i + 1]]
            cost = cost + coin_distance[p[i + 1]][0]
            if cost < minimum:
                minimum = cost
                path = []
                for i in p:
                    path.append(i)
        return [0] + path + [0]


class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        nodes = PriorityQueue()
        nodes.put((0, len(coin_distance[0]) - len([0]), 0, [0]))
        n = len(coin_distance[0])
        while nodes.qsize() > 0:
            current = nodes.get()
            if len(current[3]) == n:
                path = current[3]
                break
            for i in range(0, len(coin_distance[0])):
                if i == current[2]:
                    continue
                cost = current[0] + coin_distance[current[2]][i]
                if i not in current[3]:
                    if len(current[3]) + 1 == n:
                        cost = cost + coin_distance[i][0]
                    nodes.put((cost, len(coin_distance[0]) - len(current[3] + [i]), i, current[3] + [i]))
                    # print("Sta i koliko puta ubacujem u ovom foru?? ", cost, current[1]+1, i, current[3]+[i])
            # print("U redu mi je: ", nodes.queue)
        return path + [0]


class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def calculate_heuristic(self, node, coin_distance):
        #MST
        cost = 0
        visited = [node]
        last = node
        while len(visited) < len(coin_distance[0]):
            minimum = min([i for i in coin_distance[last] if i != 0 and i not in visited])
            cost = cost+minimum
            visited = visited + [coin_distance[last].index(minimum)]
        return cost

    def get_agent_path(self, coin_distance):
        nodes = PriorityQueue()
        nodes.put((0, len(coin_distance[0]) - len([0]), 0, [0]))
        n = len(coin_distance[0])
        while nodes.qsize() > 0:
            current = nodes.get()
            if len(current[3]) == n:
                path = current[3]
                break
            for i in range(0, len(coin_distance[0])):
                if i == current[2]:
                    continue
                cost = current[0] + coin_distance[current[2]][i]
                cost = cost + self.calculate_heuristic(i, coin_distance)
                if i not in current[3]:
                    if len(current[3]) + 1 == n:
                        cost = cost + coin_distance[i][0]
                        # ovo treba da proverim dal mi treba
                    nodes.put((cost, len(coin_distance[0]) - len(current[3] + [i]), i, current[3] + [i]))
                    # print("Sta i koliko puta ubacujem u ovom foru?? ", cost, current[1]+1, i, current[3]+[i])
            # print("U redu mi je: ", nodes.queue)
        return path + [0]