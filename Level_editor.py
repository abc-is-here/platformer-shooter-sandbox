import pygame
import button
import csv
import subprocess

pygame.init()

clock = pygame.time.Clock()
FPS = 60
screen_width = 800
screen_height = 640
lower_margin = 100
side_margin = 300

screen = pygame.display.set_mode((screen_width + side_margin, screen_height + lower_margin))
pygame.display.set_caption('Level Editor')

rows = 16
max_col = 150
tile_size = screen_height // rows
tile_type = 21
level = 1
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

layer1 = pygame.image.load('img/Background/Layer_0000_9.png').convert_alpha()
layer2 = pygame.image.load('img/Background/Layer_0001_8.png').convert_alpha()
layer3 = pygame.image.load('img/Background/Layer_0002_7.png').convert_alpha()
layer4 = pygame.image.load('img/Background/Layer_0003_6.png').convert_alpha()
layer5 = pygame.image.load('img/Background/Layer_0004_Lights.png').convert_alpha()
layer6 = pygame.image.load('img/Background/Layer_0005_5.png').convert_alpha()
layer7 = pygame.image.load('img/Background/Layer_0006_4.png').convert_alpha()
layer8 = pygame.image.load('img/Background/Layer_0007_Lights.png').convert_alpha()
layer9 = pygame.image.load('img/Background/Layer_0008_3.png').convert_alpha()
layer10 = pygame.image.load('img/Background/Layer_0009_2.png').convert_alpha()
layer11 = pygame.image.load('img/Background/Layer_0010_1.png').convert_alpha()
layer12 = pygame.image.load('img/Background/Layer_0011_0.png').convert_alpha()

img_list = []
for x in range(tile_type):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

save_img = pygame.image.load('img/save_btn.png').convert_alpha()
load_img = pygame.image.load('img/load_btn.png').convert_alpha()
start_img = pygame.image.load('img/start_btn.png').convert_alpha()

BG = (212, 176, 0)
WHITE = (255, 255, 255)
RED = (222, 0, 41)

font = pygame.font.SysFont('Futura', 30)

world_data = []
for row in range(rows):
    r = [-1] * max_col
    world_data.append(r)

for tile in range(0, max_col):
    world_data[rows - 1][tile] = 0

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    width = layer12.get_width()
    for x in range(4):
        screen.blit(layer12, ((x * width) - scroll * 0.05, 0))
        screen.blit(layer11, ((x * width) - scroll * 0.06, screen_height - layer11.get_height()))
        screen.blit(layer10, ((x * width) - scroll * 0.07, screen_height - layer10.get_height()))
        screen.blit(layer9, ((x * width) - scroll * 0.08, screen_height - layer9.get_height()))
        screen.blit(layer8, ((x * width) - scroll * 0.09, screen_height - layer8.get_height()))
        screen.blit(layer7, ((x * width) - scroll * 0.1, screen_height - layer7.get_height()))
        screen.blit(layer6, ((x * width) - scroll * 0.11, screen_height - layer6.get_height()))
        screen.blit(layer5, ((x * width) - scroll * 0.12, screen_height - layer5.get_height()))
        screen.blit(layer4, ((x * width) - scroll * 0.13, screen_height - layer4.get_height()))
        screen.blit(layer3, ((x * width) - scroll * 0.14, screen_height - layer3.get_height()))
        screen.blit(layer2, ((x * width) - scroll * 0.15, screen_height - layer2.get_height()))
        screen.blit(layer1, ((x * width) - scroll * 0.16, screen_height - layer1.get_height()))

def draw_grid():
    for c in range(max_col + 1):
        pygame.draw.line(screen, WHITE, (c * tile_size - scroll, 0), (c * tile_size - scroll, screen_height))
    for c in range(rows + 1):
        pygame.draw.line(screen, WHITE, (0, c * tile_size), (screen_width, c * tile_size))

def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * tile_size - scroll, y * tile_size))


save_button = button.Button(screen_width // 2, screen_height + lower_margin - 50, save_img, 1)
load_button = button.Button(screen_width // 2 + 200, screen_height + lower_margin - 50, load_img, 1)
start_button = button.Button(screen_width // 2 + 400, screen_height + lower_margin - 100, start_img, 1)

button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(screen_width + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0


run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f'Level: {level}', font, WHITE, 10, screen_height + lower_margin - 90)
    draw_text('Press UP or DOWN to change level', font, WHITE, 10, screen_height + lower_margin - 60)

    if save_button.draw(screen):
        with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter = ',')
            for row in world_data:
                writer.writerow(row)
    if load_button.draw(screen):
        scroll = 0
        with open(f'level{level}_data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)
                    
    if start_button.draw(screen):
        subprocess.Popen(['python', 'main.py'])

    pygame.draw.rect(screen, BG, (screen_width, 0, side_margin, screen_height))

    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count
            
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True and scroll < (max_col * tile_size) - screen_width:
        scroll += 5 * scroll_speed

    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // tile_size
    y = pos[1] // tile_size

    if pos[0] < screen_width and pos[1] < screen_height:
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1


    pygame.display.update()

pygame.quit()
