import random
import math

import pygame

from Scripts.Particle import Particle
from Scripts.Spark import Spark

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # Physics for animation
        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.set_action('Idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement = (0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # Character moving
            # Moving in X axis
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.execute_rects(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    if not self.game.dead:
                        self.game.screenshake = max(16, self.game.screenshake)
                    for i in range(10):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 0.5 + 0.5
                        pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                        self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))
                    self.game.dead += 1
                if frame_movement[0] < 0:
                    if not self.game.dead:
                        self.game.screenshake = max(16, self.game.screenshake)
                    for i in range(10):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 0.5 + 0.5
                        pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                        self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))
                    self.game.dead += 1
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
                
            # Moving in Y axis
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.execute_rects(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    if not self.game.dead:
                        self.game.screenshake = max(16, self.game.screenshake)
                    for i in range(10):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 0.5 + 0.5
                        pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                        self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))
                    self.game.dead += 1
                if frame_movement[1] < 0:
                    if not self.game.dead:
                        self.game.screenshake = max(16, self.game.screenshake)
                    for i in range(10):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 0.5 + 0.5
                        pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                        self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))
                    self.game.dead += 1
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        # Changing player direction base on movement
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        # Gravity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        # Updating player animation
        self.animation.update()

    def render(self, surf, offset = (0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

# Player class
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'Player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement = (0, 0)):
        super().update(tilemap, movement = movement)

        # Changing player animation
        self.air_time += 1

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        # Record player's last movement
        self.last_movement = movement

        # Player's function
            # Wall slide
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['left']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('Wall_Slide')
            # Changing action
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('Jump')
            elif movement[0] != 0:
                self.set_action('Run')
            else:
                self.set_action('Idle')
            # Dashing
        if abs(self.dashing) in {60, 50}:
            for i in range(10):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))
        if abs(self.dashing) in {60, 50}:
            for i in range(10):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
    
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(1, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(1, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] -= 3
            self.jumps -= 1
            self.air_time = 5
            return True

    def dash(self):
        if not self.dashing:
            self.game.sfx['Dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60

    def attack(self):
        pass

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'Enemy', pos, size)
        
        self.walking = 0
    
    def update(self, tilemap, movement = (0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.75 if self.flip else 0.75, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['Shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.sfx['Shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement = movement)
        
        if movement[0] != 0:
            self.set_action('Run')
        else:
            self.set_action('Idle')
            
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'Particle', self.rect().center, velocity = [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame = random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True
            
    def render(self, surf, offset = (0, 0)):
        super().render(surf, offset = offset)
        
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['Gun'], True, False), (self.rect().centerx - 4 - self.game.assets['Gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['Gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))