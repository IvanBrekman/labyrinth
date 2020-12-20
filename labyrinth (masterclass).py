import pygame
from collections import deque

pygame.init()  # Инициализация движка pygame

size = width, height = 800, 600  # Размеры окна

screen = pygame.display.set_mode(size)  # Создание холста
pygame.display.set_caption('Лабиринт')  # Изменение заголовка

# Цвета
black = pygame.Color('black')
white = pygame.Color('white')

red = pygame.Color('red')
green = pygame.Color('green')
blue = pygame.Color('blue')

gray = pygame.Color((120, 120, 120))
dark_gray = pygame.Color((50, 50, 50))
dark_green = pygame.Color((50, 70, 0))

TILE_SIZE = 32
ENEMY_EVENT_TYPE = pygame.USEREVENT


class Labyrinth:
    def __init__(self, filename, free_tiles, finish_tile):
        self.map = []
        with open(filename) as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.height = len(self.map)
        self.width = len(self.map[0])

        set_size(TILE_SIZE, self.height, self.width)

        self.tile_size = TILE_SIZE
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile

    def render(self):
        colors = {0: black, 1: gray, 2: dark_gray}
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                   self.tile_size, self.tile_size)
                screen.fill(colors[self.get_tile_id((x, y))], rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def find_path_step(self, start, target):
        inf = float('inf')
        x, y = start
        distance = [[inf] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = deque([(x, y)])

        while queue:
            x, y = queue.popleft()
            for dx, dy in (-1, 0), (0, -1), (1, 0), (0, 1):
                next_x, next_y = x + dx, y + dy
                if (0 <= next_y < self.height and 0 <= next_x < self.width and
                        self.is_free((next_x, next_y)) and distance[next_y][next_x] == inf):
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))

        x, y = target
        if distance[y][x] == inf or target == start:
            return start

        while prev[y][x] != start:
            x, y = prev[y][x]

        return x, y


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def render(self):
        center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, white, center, TILE_SIZE // 2)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.delay = 100
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def render(self):
        center = self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, red, center, TILE_SIZE // 2)


class Game:
    def __init__(self, lab: Labyrinth, player: Player, en: Enemy):
        self.labyrinth = lab
        self.hero = player
        self.enemy = en

    def render(self):
        self.labyrinth.render()
        self.hero.render()
        self.enemy.render()

    def update_hero(self):
        next_x, next_y = self.hero.get_pos()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.hero.set_pos(next_x, next_y)
    
    def move_enemy(self):
        next_position = self.labyrinth.find_path_step(self.enemy.get_pos(), self.hero.get_pos())
        self.enemy.set_pos(*next_position)

    def check_win(self):
        return self.labyrinth.get_tile_id(self.hero.get_pos()) == self.labyrinth.finish_tile

    def check_lose(self):
        return self.hero.get_pos() == self.enemy.get_pos()


def set_size(cell_size, h, w):
    global size, width, height
    size = width, height = w * cell_size, h * cell_size
    pygame.display.set_mode(size)


def draw():  # Функция отрисовки кадров
    game.render()


def show_message(surface, text):
    font = pygame.font.Font(None, 50)
    text = font.render(text, True, dark_green)

    text_x = width // 2 - text.get_width() // 2
    text_y = height // 2 - text.get_height() // 2
    text_w, text_h = text.get_width(), text.get_height()

    pygame.draw.rect(surface, (200, 150, 50), (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
    surface.blit(text, (text_x, text_y))


if __name__ == '__main__':
    fps = 15  # количество кадров в секунду
    clock = pygame.time.Clock()
    running = True

    game_over = False

    labyrinth = Labyrinth('simple_map.txt', [0, 2], 2)
    hero = Player(7, 7)
    enemy = Enemy(7, 1)
    game = Game(labyrinth, hero, enemy)

    while running:  # главный игровой цикл
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == ENEMY_EVENT_TYPE and not game_over:
                game.move_enemy()

        # формирование кадра
        if not game_over:
            game.update_hero()
        # ...

        draw()

        # изменение игрового мира
        if game.check_win():
            game_over = True
            show_message(screen, "You won!")

        if game.check_lose():
            game_over = True
            show_message(screen, "You lost!")
        # ...
        pygame.display.flip()  # смена кадра

        # временная задержка
        clock.tick(fps)
