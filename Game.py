import os
import sys
import random
import math

import pygame

from Scripts.DevUtils import load_transparency_image, load_image, load_images, Animation
from Scripts.Entities import Player, Enemy
from Scripts.Tilemap import Tilemap
from Scripts.BackgroundEntities import Clouds
from Scripts.Particle import Particle
from Scripts.Spark import Spark
from PausedGame import PausedGame

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 612
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 272
BUTTON_POS_X = 446
BUTTON_POS_Y = 8
BUTTON_POS_X_SOUND = 410
BUTTON_POS_Y_SOUND = 8
RENDER_SCALE = 2.25

class Game:
    def __init__(self, mode):
        pygame.init()

        pygame.display.set_caption('Last Salvation')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        
        self.clock = pygame.time.Clock()

        # Game mode
        self.mode = mode

        # Back to menu or pause game
        self.pauseGame = False
        self.toMenu = False
        self.button_exit = pygame.Rect(BUTTON_POS_X, BUTTON_POS_Y, 17, 20)
        self.button_sound = pygame.Rect(BUTTON_POS_X_SOUND, BUTTON_POS_Y_SOUND, 24, 20)
        
        # Game assets
        self.assets = {
            # Game graphic asset
            'Barrier': load_images('Tiles/Barrier'),
            'Grass': load_images('Tiles/Grass'),
            'Water': load_images('Tiles/Water'),
            'Stone': load_images('Tiles/Stone'),
            'Stone_Surface': load_images('Tiles/Stone Surface'),
            'Spike': load_images('Tiles/Spike'),
            'Clouds': load_images('Tiles/Decor/Clouds'),
            'Background': load_image('Background/Background.png'),
            'Forest_Background': load_image('Background/Background_1.png'),
            'Cave_Background': load_image('Background/Cave_Background.png'),
            'Decor_Grasses': load_images('Tiles/Decor/Grasses'),
            'Decor_Rock': load_images('Tiles/Decor/Prop Rock'),
            'Decor_Mossy_Rock': load_images('Tiles/Decor/Prop Mossy Rock'),
            'Decor_Tree': load_images('Tiles/Decor/Tree'),
            # Player's asset
            'Player/Idle': Animation(load_images('Entities/Player/Idle'), img_dur = 10),
            'Player/Run': Animation(load_images('Entities/Player/Run'), img_dur = 5),
            'Player/Jump': Animation(load_images('Entities/Player/Jump')),
            'Player/Wall_Slide': Animation(load_images('Entities/Player/Wall Slide')),
            # Enemies's asset
            'Enemy/Idle': Animation(load_images('Entities/Enemy/Idle'), img_dur = 6),
            'Enemy/Run': Animation(load_images('Entities/Enemy/Run'), img_dur = 4),
            'Gun': load_image('gun.png'),
            'Projectile': load_image('projectile.png'),
            # Particles
            'Particle/Leaf': Animation(load_images('Particles/Leaf'), img_dur = 20, loop = False),
            'Particle/Particle': Animation(load_images('Particles/Particle'), img_dur = 6, loop = False),
            # Tutorial
            'Tutorial/Moving': Animation(load_images('Tutorial/Moving'), img_dur = 20),
            'Tutorial/Double_Jump': Animation(load_images('Tutorial/Double Jump'), img_dur = 20),
            'Tutorial/Jumping':Animation(load_images('Tutorial/Jumping'), img_dur = 20),
            'Tutorial/Dash': Animation(load_images('Tutorial/Slide'), img_dur = 20),
            'Tutorial/Wall_Slide': Animation(load_images('Tutorial/Wall Slide'), img_dur = 30),
            'Tutorial/Notification_1': load_image('Tutorial/Notification/00.png'),
            'Tutorial/Notification_2': load_image('Tutorial/Notification/01.png'),
            'Tutorial/Notification_3': load_image('Tutorial/Notification/02.png'),
        }

        # Game sound
        self.sfx = {
            'Jump': pygame.mixer.Sound('Data/SFX/Jump.wav'),
            'Dash': pygame.mixer.Sound('Data/SFX/Dash.wav'),
            'Hit': pygame.mixer.Sound('Data/SFX/Hit.wav'),
            'Shoot': pygame.mixer.Sound('Data/SFX/Shoot.wav'),
            'Ambience': pygame.mixer.Sound('Data/SFX/Ambience.wav'),
        }

        # Player
        self.player = Player(self, (50, 50), (14, 16))

        # Player's movement
        self.movement = [False, False]

        # Offset camera
        self.scroll = [0, 0]

        # Cloud in the background
        self.clouds = Clouds(self.assets['Clouds'], count = 12)

        # Screen shaking effect
        self.screenshake = 0

        # Tile
        self.tilemap = Tilemap(self, tile_size = 16)
        self.tilemap.load('Data/Maps/0.json')

        # Game level
        self.level = 0
        if mode == 0:
            self.load_level(0)
        else:
            self.load_level(99)

        # Forest background position
        self.forest_pos = 0
        self.forest_dist_travel = 0
        
        # Turn off tutorial message
        self.tutorial_message = True
        self.tutorial_message_0 = True

    def draw_text(self, text, font, color, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.display.blit(textobj, textrect)

    def load_level(self, map_id):
        if map_id == 99:
            map_id = 0
            self.tilemap.load('Data/Maps/Custom/0.json')
        else:
            self.tilemap.load('Data/Maps/' + str(map_id) + '.json')
        
        # Spawner
            # Leaf falling
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('Decor_Tree', 0), ('Decor_Tree', 1)], keep = True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0] + 40, 4 + tree['pos'][1] + 15, 35, 160))
            # Enemies
        self.enemies = []
        for spawner in self.tilemap.extract([('Spawners', 0), ('Spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            
        self.projectiles = []
        self.particles = []
        self.sparks = []
        
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
    
    def load_tutorial(self, tilemap, pos):
        if self.tutorial_message_0 == True:
            if self.tutorial_message == True:
                if self.player.pos[0] >= 0 and self.player.pos[0] < 16 * 16:
                    self.display.blit(self.assets['Tutorial/Moving'].img(), (20, 20))
                    self.assets['Tutorial/Moving'].update()
                elif self.player.pos[0] >= 16 * 16 and self.player.pos[0] <= 28 * 16:
                    self.display.blit(self.assets['Tutorial/Jumping'].img(), (20, 20))
                    self.assets['Tutorial/Jumping'].update()
                elif self.player.pos[0] >= 32 * 16 and self.player.pos[0] <= 38 * 16:
                    self.display.blit(self.assets['Tutorial/Wall_Slide'].img(), (20, 20))
                    self.assets['Tutorial/Wall_Slide'].update()
                    self.display.blit(self.assets['Tutorial/Double_Jump'].img(), (20, 80))
                    self.assets['Tutorial/Double_Jump'].update()
                elif self.player.pos[0] >= 47 * 16 and self.player.pos[0] < 70 * 16:
                    self.display.blit(self.assets['Tutorial/Dash'].img(), (20, 20))
                    self.assets['Tutorial/Dash'].update()
                elif self.player.pos[0] >= 70 * 16 and self.player.pos[0] < 83 * 16:
                    self.display.blit(self.assets['Tutorial/Notification_1'], (20, 20))
            else:
                if self.player.pos[0] >= 0 and self.player.pos[0] < 16 * 16:
                    self.display.blit(self.assets['Tutorial/Notification_2'], (20, 20))
            if self.player.pos[0] >= 83 * 16 and self.player.pos[0] <= 87 * 16:
                self.display.blit(self.assets['Tutorial/Notification_3'], (20, 20))
        


    # Main function for running the game
    def run(self):
        # Game sfx and music
        pygame.mixer.music.load('Data/SFX/Music.Wav')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        self.sfx['Ambience'].play(-1)
        self.sfx['Dash'].set_volume(0.5)

        # Game loop
        while True:
            # Render the correct background for each level
            if self.level == 0:
                # Rendering background
                self.display.blit(self.assets['Background'], (0, 0))
                
                # Forest background position
                self.forest_pos = -self.scroll[0] * 0.4
                self.display.blit(self.assets['Forest_Background'], (self.forest_pos, 40))
                self.display.blit(self.assets['Forest_Background'], (self.forest_pos + 640, 40))
                self.display.blit(self.assets['Forest_Background'], (self.forest_pos + 640 * 2, 40))
                self.display.blit(self.assets['Forest_Background'], (self.forest_pos + 640 * 3, 40))
                self.display.blit(self.assets['Forest_Background'], (self.forest_pos - 640, 40))
            if self.level == 1:
                # Rendering background
                self.display.blit(self.assets['Cave_Background'], (0, 0))

            # Screenshaking effect when kill or whatever...
            self.screenshake = max(0, self.screenshake - 1)

            # End level if player is dead
            if self.dead == 1:
                kill = self.sparks
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.tutorial_message = False
                    self.load_level(self.level)

            # Move to next level if all enemy are eliminated
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    if self.mode == 0:
                        self.level = min(self.level + 1, len(os.listdir('Data/Maps')) - 1)
                        self.load_level(self.level)
                    else:
                        break
            if self.transition < 0:
                self.transition += 1

            # Using mathematics to calculate the right location for the camera to output to the player's screen
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Rendering leaf from trees, by using 
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'Leaf', pos, velocity = [-0.1, 0.3], frame = random.randint(0, 20)))

            # Rendering decor:
                # Clouds:
            if self.level == 0:
                self.clouds.update()
                self.clouds.render(self.display, offset = render_scroll)

            # Rendering map
            self.tilemap.render(self.display, offset = render_scroll)

            # Rendering player
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset = render_scroll)
            
            # Enemy Manager
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset = render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['Projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.tutorial_message_0 = False
                        self.sfx['Hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 10
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'Particle', self.player.rect().center, velocity = [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame = random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset = render_scroll)
                if kill:
                    self.sparks.remove(spark)

            # Rendering particle
                # Leaf falling
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if particle.type == 'Leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # Handling game event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.sfx['Jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_z:
                        self.player.attack()
                    if event.key == pygame.K_ESCAPE:
                        self.pauseGame = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            # Tutorial message
            if self.mode == 0:
                self.load_tutorial(self.tilemap, self.player.pos)

            # End level animation
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            # Camera shaking's offset
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)

            # Paused game
            if self.pauseGame:
                PausedGame(self, frame = pygame.surfarray.array3d(self.display)).run()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)

            # Back to game menu
            if self.toMenu:
                break

            pygame.display.update()
            self.clock.tick(60)