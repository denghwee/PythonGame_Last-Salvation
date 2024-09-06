import sys

import pygame

from Scripts.DevUtils import load_transparency_image, load_image, load_images, Animation

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 612
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 272

class Cutscene:
    def __init__(self, scene):
        pygame.init()
        self.clock = pygame.time.Clock()
        
        self.screen = self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # Current scene to render as cutscene
        self.scene = scene
        # Delay before entering back to the game
        self.delay = 0
        # Allow player to skip the cutscene
        self.skip = False

        # Loading game font
        self.font = pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 28)
        
        # Loading cutscene's assets
        self.assets = {
            'Background_Sky': load_image('Background/Background.png'),
            'Intro': Animation(load_images('Intro'), img_dur = 26, loop = False),
        }

        # Loading intro cutscene sound
        self.sfx = {
            'Click': pygame.mixer.Sound('Data/SFX/Click.wav'),
            'Mouse_Click': pygame.mixer.Sound('Data/SFX/Mouse Click.wav'),
        }

        # Game state
        self.continueGame = False
    
    # This function is used to draw text into your screen, for example the word "Play" in Play button
    def draw_text(self, text, font, color, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.display.blit(textobj, textrect)
    
    # Main function for running the cutscene
    def run(self):
        # Loading intro cutscene's music and sfx
        if self.scene == 0:
            pygame.mixer.music.load('Data/SFX/Birds.Wav')
            pygame.mixer.music.set_volume(1)
            pygame.mixer.music.play(-1)

        while True:
            # Load the captured frame and blit it to the screen
            self.display.fill((255, 250, 250))

            # If the scene need to render is the intro
            if self.scene == 0:
                self.display.blit(self.assets['Background_Sky'], (0, 0))
                self.draw_text('DengHwee  Entertainment', self.font, (20, 52, 164), self.display.get_width() // 2 - 145, self.display.get_height() // 2 + 60)
                self.display.blit(self.assets['Intro'].img(), (self.display.get_width() // 2 - 75, self.display.get_height() // 2 - 100))
                self.assets['Intro'].update()
                if self.assets['Intro'].done == True:
                    self.delay += 1
                if self.delay == 1:
                    self.sfx['Mouse_Click'].play()
                if self.delay == 50:
                    break
            # The only cutscene we have now is the intro cutscene
            elif self.scene == 1:
                pass
            
            # Checking game's event
            for event in pygame.event.get():
                # Checking quit event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Checking whether you input a left click from your mouse or not
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.click = False
                
                # Checking whether you has pressed the Escape key or not
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.skip = True
            
            # Checking whether the game should skip the game state or not, following the Escape key event above
            if self.skip:
                break
            
            # Rendering the frame of the game
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

            # Update the next frame for game to render
            pygame.display.update()
            # Game setting to 60 FPS
            self.clock.tick(60)