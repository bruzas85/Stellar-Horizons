from typing import Tuple

import pygame
import math

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Расстояние между объектами")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Позиции объектов
object1_pos = (100, 100)  # (x1, y1)
object2_pos = (400, 300)  # (x2, y2)

# Функция для вычисления расстояния
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Заливка экрана белым цветом
    screen.fill(WHITE)

    # Рисуем объекты
    pygame.draw.circle(screen, RED, object1_pos, 20)  # Объект 1
    pygame.draw.circle(screen, GREEN, object2_pos, 20)  # Объект 2

    # Вычисляем расстояние между объектами
    dist = distance(object1_pos[0], object1_pos[1], object2_pos[0], object2_pos[1])
    if dist<= 370:
        pygame.draw.line(screen, "Blue", (object1_pos), (object2_pos), 3)

    # Отображаем расстояние на экране
    font = pygame.font.Font(None, 36)
    text = font.render(f"Distance: {dist:.2f}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    # Обновление экрана
    pygame.display.flip()

# Завершение работы
pygame.quit()
