import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()


screen_width = 800
screen_height = int(screen_width * 0.8)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Shooter')
clock = pygame.time.Clock()
FPS = 60

gravity = 0.75
thresh = 200
rows = 16
col = 150
tile_size = screen_height // rows
tile_type = 21
max_level = 1
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

pygame.mixer.music.load('audio/music.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.mp3')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shoot.mp3')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.mp3')
grenade_fx.set_volume(0.5)

start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

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
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (tile_size, tile_size))
	img_list.append(img)
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
	'Health'	: health_box_img,
	'Ammo'		: ammo_box_img,
	'Grenade'	: grenade_box_img
}

BG = (212, 176, 0)
RED = (222, 0, 41)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (222, 0, 122)

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def draw_bg():
	screen.fill(BG)
	width = layer12.get_width()
	for x in range(10):
		screen.blit(layer12, ((x * width) - bg_scroll * 0.05, 0))
		screen.blit(layer11, ((x * width) - bg_scroll * 0.06, screen_height - layer11.get_height()))
		screen.blit(layer10, ((x * width) - bg_scroll * 0.07, screen_height - layer10.get_height()))
		screen.blit(layer9, ((x * width) - bg_scroll * 0.08, screen_height - layer9.get_height()))
		screen.blit(layer8, ((x * width) - bg_scroll * 0.09, screen_height - layer8.get_height()))
		screen.blit(layer7, ((x * width) - bg_scroll * 0.1, screen_height - layer7.get_height()))
		screen.blit(layer6, ((x * width) - bg_scroll * 0.11, screen_height - layer6.get_height()))
		screen.blit(layer5, ((x * width) - bg_scroll * 0.12, screen_height - layer5.get_height()))
		screen.blit(layer4, ((x * width) - bg_scroll * 0.13, screen_height - layer4.get_height()))
		screen.blit(layer3, ((x * width) - bg_scroll * 0.14, screen_height - layer3.get_height()))
		screen.blit(layer2, ((x * width) - bg_scroll * 0.15, screen_height - layer2.get_height()))
		screen.blit(layer1, ((x * width) - bg_scroll * 0.16, screen_height - layer1.get_height()))


def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	data = []
	for _ in range(rows):
		r = [-1] * col
		data.append(r)

	return data

class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.is_alive = True
		self.char_type = char_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = 0

		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			temp_list = []
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update(self):
		self.update_animation()
		self.check_alive()
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1


	def move(self, moving_left, moving_right):
		screen_scroll = 0
		dx = 0
		dy = 0

		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True

		self.vel_y += gravity
		if self.vel_y > 10:
			self.vel_y = 10
		dy += self.vel_y

		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		if self.rect.bottom > screen_height:
			self.health = 0

		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
				dx = 0

		self.rect.x += dx
		self.rect.y += dy

		if self.char_type == 'player':
			if (self.rect.right > screen_width - thresh and bg_scroll < (world.level_length * tile_size) - screen_width)\
				or (self.rect.left < thresh and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete



	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			self.ammo -= 1
			shot_fx.play()


	def ai(self):
		if self.is_alive and player.is_alive:
			if self.idling == False and random.randint(1, 200) == 1:
				self.update_action(0)
				self.idling = True
				self.idling_counter = 50
			
			if self.vision.colliderect(player.rect):
				self.update_action(0)
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1)
					self.move_counter += 1
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

					if self.move_counter > tile_size:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		self.rect.x += screen_scroll


	def update_animation(self):
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.action][self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0

	def update_action(self, new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.is_alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * tile_size
					img_rect.y = y * tile_size
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * tile_size, y * tile_size)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * tile_size, y * tile_size)
						decoration_group.add(decoration)
					elif tile == 15:
						player = Soldier('player', x * tile_size, y * tile_size, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:
						enemy = Soldier('enemy', x * tile_size, y * tile_size, 1.65, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 17:
						item_box = ItemBox('Ammo', x * tile_size, y * tile_size)
						item_box_group.add(item_box)
					elif tile == 18:
						item_box = ItemBox('Grenade', x * tile_size, y * tile_size)
						item_box_group.add(item_box)
					elif tile == 19:
						item_box = ItemBox('Health', x * tile_size, y * tile_size)
						item_box_group.add(item_box)
					elif tile == 20:
						exit = Exit(img, x * tile_size, y * tile_size)
						exit_group.add(exit)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))


	def update(self):
		self.rect.x += screen_scroll
		if pygame.sprite.collide_rect(self, player):
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
			self.kill()


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		self.health = health
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150 * (1), 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		self.rect.x += (self.direction * self.speed) + screen_scroll
		if self.rect.right < 0 or self.rect.left > screen_width:
			self.kill()
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.is_alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.is_alive:
					enemy.health -= 25
					self.kill()



class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += gravity
		dx = self.direction * self.speed
		dy = self.vel_y

		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	

		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			if abs(self.rect.centerx - player.rect.centerx) < tile_size * 2 and \
				abs(self.rect.centery - player.rect.centery) < tile_size * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < tile_size * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < tile_size * 2:
					enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		self.rect.x += screen_scroll

		EXPLOSION_SPEED = 4
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]


class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, screen_width // 2, screen_height))
			pygame.draw.rect(screen, self.colour, (screen_width // 2 + self.fade_counter, 0, screen_width, screen_height))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, screen_width, screen_height // 2))
			pygame.draw.rect(screen, self.colour, (0, screen_height // 2 +self.fade_counter, screen_width, screen_height))
		if self.direction == 2:
			pygame.draw.rect(screen, self.colour, (0, 0, screen_width, 0 + self.fade_counter))
		if self.fade_counter >= screen_width:
			fade_complete = True

		return fade_complete

intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)

start_button = button.Button(screen_width // 2 - 130, screen_height // 2 - 150, start_img, 1)
exit_button = button.Button(screen_width // 2 - 110, screen_height // 2 + 50, exit_img, 1)
restart_button = button.Button(screen_width // 2 - 100, screen_height // 2 - 50, restart_img, 2)

enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

world_data = []
for row in range(rows):
	r = [-1] * col
	world_data.append(r)
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)



is_running = True
while is_running:

	clock.tick(FPS)

	if start_game == False:
		screen.fill(BG)
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if exit_button.draw(screen):
			is_running = False
	else:
		draw_bg()
		world.draw()
		health_bar.draw(player.health)
		draw_text('AMMO: ', font, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img, (90 + (x * 10), 40))
		draw_text('GRENADES: ', font, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img, (135 + (x * 15), 60))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)

		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0

		if player.is_alive:
			if shoot:
				player.shoot()
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
				 			player.rect.top, player.direction)
				grenade_group.add(grenade)
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)
			elif moving_left or moving_right:
				player.update_action(1)
			else:
				player.update_action(0)
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= max_level:
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)	
		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			is_running = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_w and player.is_alive:
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				is_running = False

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False


	pygame.display.update()

pygame.quit()