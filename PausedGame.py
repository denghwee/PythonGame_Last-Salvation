import sys

import pygame

from Scripts.DevUtils import load_transparency_image, load_image, load_images, Animation

# Game screen's size
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 612
# Game actual display's size
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 272
# Game button's position
BUTTON_POS_X = 446
BUTTON_POS_Y = 8
BUTTON_POS_X_SOUND = 410
BUTTON_POS_Y_SOUND = 8
# Render scale between game screen and display for the right mouse input's position
RENDER_SCALE = 2.25

class PausedGame:
    def __init__(self, game, frame):
        pygame.init()
        self.clock = pygame.time.Clock()
        
        self.screen = self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # Current game state (Game, Editor,...) when paused game
        self.game = game
        # Current frame when you paused the game
        self.frame = frame

        # Loading game font
        self.font = pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 28)
        
        # Loading game assets
        self.assets = {
            # Background
            'Pause_Background': load_transparency_image('Background/Pause_Background.png'),
            # GUI
            'Exit_Button': load_image('GUI/Button/BtnExit.png'),
            'Sound_Button_Off': load_image('GUI/Button/BtnSoundOff.png'),
            'Sound_Button_On': load_image('GUI/Button/BtnSoundOn.png')
        }

        # Loading game sound
        self.sfx = {
            'Click': pygame.mixer.Sound('Data/SFX/Click.wav')
        }

        # Checking mouse's input
        self.click = False

        # Game state
        self.continueGame = False

        # Paused game's button
        self.button_exit = pygame.Rect(BUTTON_POS_X, BUTTON_POS_Y, 17, 20)
        self.button_sound = pygame.Rect(BUTTON_POS_X_SOUND, BUTTON_POS_Y_SOUND, 24, 20)
        self.Sound_Btn_State = 'Sound_Button_On'
        self.sound_setting_delay = 10
    
    # This function is used to draw text into your screen
    def draw_text(self, text, font, color, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.display.blit(textobj, textrect)
    
    # The main function to run this game state (Paused Game)
    def run(self):
        while True:

            # Load the captured frame and render it with couple of other things to the screen as the background
            self.display.blit(pygame.surfarray.make_surface(self.frame), (0, 0))
            self.display.blit(self.assets['Pause_Background'], (0, 0))
            self.draw_text('PAUSED', self.font, (255, 250, 250), self.game.display.get_width() // 2 - 44, self.game.display.get_height() // 2 - 36)
            self.draw_text('Press Space to continue!', pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 16), (255, 250, 250), self.game.display.get_width() // 2 - 92, self.game.display.get_height() // 2 - 8)
            self.display.blit(self.assets['Exit_Button'], (BUTTON_POS_X, BUTTON_POS_Y))
            self.display.blit(self.assets[self.Sound_Btn_State], (BUTTON_POS_X_SOUND, BUTTON_POS_Y_SOUND))

            # Delaying the input of your mouse when setting, to prevent the game could create the same output more than a time 
            if self.sound_setting_delay != 10:
                self.sound_setting_delay += 1

            # Get your mouse's position in the screen
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            
            # Checking game's event
            for event in pygame.event.get():
                # Checking quit event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Checking if player press left click or not
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.click = False
                
                # Checking if player press Space or not
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game.pauseGame = False
                        self.continueGame = True
            
            # Game button collision
                # Checking "Exit" button collision
            if self.button_exit.collidepoint(mpos):
                if self.click == True:
                    self.game.pauseGame = False
                    self.game.toMenu = True
                    break
                # Checking "Sound" button collision
            if self.button_sound.collidepoint(mpos):
                if self.click == True and self.sound_setting_delay == 10:
                    if self.Sound_Btn_State == 'Sound_Button_On':
                        self.Sound_Btn_State = 'Sound_Button_Off'
                        pygame.mixer.music.pause()
                        self.game.sfx['Ambience'].stop()
                        self.sound_setting_delay = 0
                    elif self.Sound_Btn_State == 'Sound_Button_Off':
                        self.Sound_Btn_State = 'Sound_Button_On'
                        pygame.mixer.music.unpause()
                        self.game.sfx['Ambience'].play(-1)
                        self.sound_setting_delay = 0
            
            # Continuing Game
            if self.continueGame:
                break

            # Rendering the frame of the game state
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

            # Update the next frame for game to render
            pygame.display.update()
            # Game setting to 60 FPS
            self.clock.tick(60)