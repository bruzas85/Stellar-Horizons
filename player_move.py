import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Размеры комнаты и камеры
ROOM_WIDTH = 4000
ROOM_HEIGHT = 4000
CAMERA_WIDTH = 800
CAMERA_HEIGHT = 600

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Создаем экран
screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT))
pygame.display.set_caption('Космическая игра с астероидами')

# Загрузка спрайтов

fog_image = pygame.image.load("bg_98_98_fog.png").convert_alpha()  # Добавить нормальное изображение тумана
stars_image = pygame.image.load("stars.png").convert_alpha()  # Добавить нормальное изображение звезд

sprite_folder = "class_ships_4/"
idle_sprite = pygame.image.load(sprite_folder + "trport_mod01_s64_anim00.png").convert_alpha()
movement_sprites = [
    pygame.image.load(sprite_folder + f"trport_mod01_s64_anim0{i}.png").convert_alpha()
    for i in range(1, 4)
]

# Астероиды
asteroid_sprites = {
    "ast_mod01_s16": pygame.image.load("ast_mod01_s16.png").convert_alpha(),
    "ast_mod01_s32": pygame.image.load("ast_mod01_s32.png").convert_alpha(),
    "ast_mod01_s64": pygame.image.load("ast_mod01_s64.png").convert_alpha(),
}

# Размеры корабля
ship_width, ship_height = idle_sprite.get_size()

# Позиция и скорость корабля
ship_x, ship_y = ROOM_WIDTH // 2, ROOM_HEIGHT // 2
ship_speed = 5
ship_angle = 0
velocity = pygame.math.Vector2(0, 0)

# Параметры анимации
animation_index = 0
animation_timer = 0
animation_speed = 100  # Скорость анимации в миллисекундах

# Параметры распрделения по гаусу
mu_x, mu_y = 2000, 2000 # среднее значение для распределения
sigma = 300 # стандартное отклонение

# Камера
camera = pygame.Rect(0, 0, CAMERA_WIDTH, CAMERA_HEIGHT)


class Asteroid:
    def __init__(self, sprite, x, y, angle, rotation_speed):
        self.sprite = sprite
        self.x = x
        self.y = y
        self.angle = angle
        self.rotation_speed = rotation_speed

    def update(self):
        self.angle += self.rotation_speed

    def draw(self, screen, camera):
        rotated_sprite = pygame.transform.rotate(asteroid_sprites[self.sprite], math.degrees(self.angle))
        rotated_rect = rotated_sprite.get_rect(center=(self.x - camera.left, self.y - camera.top))
        screen.blit(rotated_sprite, rotated_rect.topleft)


# Класс для создания пояса астероидов
class AsteroidBelt:
    def __init__(self, center_x, center_y, inner_radius, outer_radius, asteroid_counts):
        self.center_x = center_x
        self.center_y = center_y
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.asteroid_counts = asteroid_counts
        self.asteroids = self._generate_asteroids()

    def _generate_asteroids(self):
        asteroids = []
        for sprite, count in self.asteroid_counts.items():
            for _ in range(count):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(self.inner_radius, self.outer_radius)
                x = self.center_x + math.cos(angle) * distance
                y = self.center_y + math.sin(angle) * distance

                if not any(math.hypot(x - a["x"], y - a["y"]) < 64 for a in asteroids):
                    asteroids.append({
                        "sprite": sprite,
                        "x": x,
                        "y": y,
                        "angle": random.uniform(0, 2 * math.pi),
                        "rotation_speed": random.uniform(-0.05, 0.05),
                        "orbit_angle": angle,
                        "orbit_speed": random.uniform(0.002, 0.01),
                        "distance": distance,
                    })
        return asteroids

    def update_and_draw(self, screen, camera):
        for asteroid in self.asteroids:
            asteroid["orbit_angle"] += asteroid["orbit_speed"]
            asteroid["x"] = self.center_x + math.cos(asteroid["orbit_angle"]) * asteroid["distance"]
            asteroid["y"] = self.center_y + math.sin(asteroid["orbit_angle"]) * asteroid["distance"]

            asteroid["angle"] += asteroid.get("rotation_speed", 0)
            sprite = asteroid_sprites[asteroid["sprite"]]
            rotated_sprite = pygame.transform.rotate(sprite, math.degrees(asteroid["angle"]))
            rotated_rect = rotated_sprite.get_rect(center=(asteroid["x"] - camera.left, asteroid["y"] - camera.top))

            screen.blit(rotated_sprite, rotated_rect.topleft)


class AsteroidField:
    def __init__(self):
        self.asteroids = []

    def generate_asteroids(self, asteroid_counts, center_x, center_y, inner_radius, outer_radius):
        for sprite, count in asteroid_counts.items():
            for _ in range(count):
                # Генерация координат с использованием нормального распределения
                x = random.gauss(center_x, sigma)
                y = random.gauss(center_y, sigma)

                # Убедимся, что астероид не выходит за пределы комнаты
                x = max(0, min(ROOM_WIDTH, x))
                y = max(0, min(ROOM_HEIGHT, y))
                rotation_speed = random.uniform(-0.05, 0.05)

                if not any(math.hypot(x - a.x, y - a.y) < 64 for a in self.asteroids):
                    self.asteroids.append(Asteroid(sprite, x, y, random.uniform(0, 2 * math.pi), rotation_speed))

    def update_and_draw(self, screen, camera):
        for asteroid in self.asteroids:
            asteroid.update()
            asteroid.draw(screen, camera)


# Сетка комнат
rooms = {}
for x in range(99, 102):  # Координаты по X
    for y in range(99, 102):  # Координаты по Y
        rooms[(x, y)] = {"asteroids": []}

# Создание коллекции астероидов
asteroid_field = AsteroidField()

# Генерация астероидов в комнате 99x100
asteroid_field.generate_asteroids({
    "ast_mod01_s16": random.randint(20, 30),
    "ast_mod01_s32": random.randint(10, 15),
    "ast_mod01_s64": 10,
}, ROOM_WIDTH // 2, ROOM_HEIGHT // 2, 400, 700)

# Создание пояса астероидов
belt_center_x, belt_center_y = ROOM_WIDTH // 2, ROOM_HEIGHT // 2
belt_radius = 700
belt_inner_radius = 400
asteroid_belt = AsteroidBelt(belt_center_x, belt_center_y, belt_inner_radius, belt_radius, {
    "ast_mod01_s16": random.randint(50, 100),
    "ast_mod01_s32": random.randint(30, 60),
    "ast_mod01_s64": 50,
})

current_room = (100, 100)  # Начальная комната


# Функция для перемещения корабля
def move_ship(keys):
    global velocity, ship_angle

    if keys[pygame.K_UP]:
        thrust = pygame.math.Vector2(0.2, 0).rotate(-ship_angle)
        velocity += thrust

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ship_angle += 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ship_angle -= 5

    velocity *= 0.98


# Функция для обновления позиции и перехода между комнатами
def update_position():
    global ship_x, ship_y, current_room

    ship_x += velocity.x
    ship_y += velocity.y

    if ship_x < 0:
        current_room = (current_room[0] - 1, current_room[1])
        ship_x = ROOM_WIDTH - 1
    elif ship_x > ROOM_WIDTH:
        current_room = (current_room[0] + 1, current_room[1])
        ship_x = 0

    if ship_y < 0:
        current_room = (current_room[0], current_room[1] - 1)
        ship_y = ROOM_HEIGHT - 1
    elif ship_y > ROOM_HEIGHT:
        current_room = (current_room[0], current_room[1] + 1)
        ship_y = 0


# Функция для обновления камеры
def update_camera():
    camera.center = (ship_x, ship_y)
    camera.left = max(0, min(ROOM_WIDTH - CAMERA_WIDTH, camera.left))
    camera.top = max(0, min(ROOM_HEIGHT - CAMERA_HEIGHT, camera.top))


# Функция для отрисовки корабля с анимацией
def draw_ship():
    global animation_index, animation_timer

    if velocity.length() > 0.1:
        now = pygame.time.get_ticks()
        if now - animation_timer > animation_speed:
            animation_timer = now
            animation_index = (animation_index + 1) % len(movement_sprites)
        current_sprite = movement_sprites[animation_index]
    else:
        current_sprite = idle_sprite

    rotated_ship = pygame.transform.rotate(current_sprite, ship_angle)
    rotated_rect = rotated_ship.get_rect(center=(ship_x - camera.left, ship_y - camera.top))

    screen.blit(rotated_ship, rotated_rect.topleft)


fog_scroll_speed = 0.6  # Туман двигается в 0.6 раза медленнее камеры
star_scroll_speed = 0.2  # Звезды двигаются в 0.1 раза медленнее камеры


def draw_background(screen, camera, background_image, scroll_speed):
    image_width, image_height = background_image.get_size()
    scroll_x = -camera.left * scroll_speed
    scroll_y = -camera.top * scroll_speed

    for x in range(-image_width, CAMERA_WIDTH + image_width, image_width):
        for y in range(-image_height, CAMERA_HEIGHT + image_height, image_height):
            screen.blit(background_image, (x + scroll_x, y + scroll_y))


def distance(x1, x2, y1, y2): # функция проверки дистанции до объекта
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# Главный игровой цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    move_ship(keys)
    update_position()
    update_camera()

    screen.fill(BLACK)

    # Рисуем звезды
    draw_background(screen, camera, stars_image, star_scroll_speed)

    # Отображение пояса астероидов
    if current_room == (101, 101):
        asteroid_belt.update_and_draw(screen, camera)

    # Отображение астероидов
    if current_room == (99, 100):
        asteroid_field.update_and_draw(screen, camera)

    if current_room == (100, 100):
        asteroid_field.update_and_draw(screen, camera)


    draw_ship()
    draw_background(screen, camera, fog_image, fog_scroll_speed)  # туман по верх всех объектов в сцене

    font = pygame.font.SysFont(None, 36)
    room_text = font.render(f"Room: {current_room[0]}x{current_room[1]}", True, WHITE)
    screen.blit(room_text, (10, 10))

    # Проверка расстояния до астероидов "ast_mod01_s16"
    for asteroid in asteroid_field.asteroids:
        if asteroid.sprite == "ast_mod01_s16":
            dist = distance(ship_x, asteroid.x, ship_y, asteroid.y)
            if dist < 100:  # Пример: если расстояние меньше 100 пикселей
                pygame.draw.line(screen, (0,0,255), (ship_x-camera.left, ship_y-camera.top), (asteroid.x-camera.left, asteroid.y-camera.top), 1)
                print(f"Опасность! Расстояние до астероида: {dist}, {(ship_x, ship_y)},==== {(asteroid.x, asteroid.y)}" )

    pygame.display.flip()
    pygame.time.Clock().tick(60)