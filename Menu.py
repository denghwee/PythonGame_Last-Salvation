import os
import sys
import pygame

from Game import Game
from Editor import Editor
from Cutscene import Cutscene
from Scripts.DevUtils import load_image_no_cv, load_image, load_images, Animation

# Game screen's size
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 612
# Game actual display's size
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 272
# Render scale between game screen and display for the right mouse input's position
RENDER_SCALE = 2.25
# Game button's position
BUTTON_POS_X = 370
BUTTON_POS_Y_1 = 100
BUTTON_POS_Y_2 = 150
BUTTON_POS_Y_3 = 200
BUTTON_POS_Y_4 = 50

class MainMenu:
    # Every command in __init__ function of each classes will tell you what purpose of the variable is for
    def __init__(self):
        pygame.init()

        # Game Title
        pygame.display.set_caption('Last Salvation')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        
        self.clock = pygame.time.Clock()

        # Load game font
        self.font = pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 16)
        self.credits_font = pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 12)
        self.custom_map_font = pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 16)

        # Load menu assets
        self.assets = {
            'Menu_Background': Animation(load_images('Menu/Menu Background'), img_dur = 13),
            'Game_Title': load_image_no_cv('Menu/GameTitle.png'),
            'Button': load_image('GUI/Button/Btn1.png'),
            'Button_Pushed': load_image('GUI/Button/Btn2.png')
        }

        # Load menu SFX
        self.sfx = {
            'Click': pygame.mixer.Sound('Data/SFX/Click.wav')
        }

        # Creating game button
        self.button_play = pygame.Rect(BUTTON_POS_X, BUTTON_POS_Y_1, 76, 42)
        self.button_edit = pygame.Rect(BUTTON_POS_X, BUTTON_POS_Y_2, 76, 42)
        self.button_quit = pygame.Rect(BUTTON_POS_X, BUTTON_POS_Y_3, 76, 42)
        self.button_custom = pygame.Rect(BUTTON_POS_X, BUTTON_POS_Y_4, 76, 42)

        # Next game state
        self.game_state = None

        # Checking mouse input
        self.click = False

        # Resize window
        self.fullscreen = False

        # Menu transition
        self.transition = 0

        # Checking custom map button
        self.custom_map = False

    # This function is used to draw text into your screen, for example the word "Play" in Play button
    def draw_text(self, text, font, color, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.display.blit(textobj, textrect)

    # This function is used to load and play theme song
    def load_theme_song(self):
        pygame.mixer.music.load('Data/SFX/Menu Theme Song.Wav')
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    # This function is used to set menu's attribute to default
    def restart_menu_attribute(self):
        self.load_theme_song()
        pygame.mixer.music.play(-1)
        self.click = False
        self.transition = 0

    # This function is used to check whether the button is click or not so the game know which game state is should enter
    def check_button_click(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True

    # This function is used to visible the custom map button for you to play, it will depend on if there is a custom map
    # or not to decide whether to visible it or not
    def visible_custom_map_button(self):
        file_path = 'Data/Maps/Custom/0.json'
        if os.path.exists(file_path):
            self.custom_map = True
            
    # Main function for running the menu
    def run(self):
        # Run game intro
        Cutscene(0).run()

        # Game sfx and music
        self.load_theme_song()

        # Check whether game has a custom map or not
        self.visible_custom_map_button()

        while True:
            if self.game_state == 'Editor':
                self.visible_custom_map_button()

            # Menu background
                # Image Background
            self.display.blit(self.assets['Menu_Background'].img(), (0, 0))
            self.assets['Menu_Background'].update()

            # Credits
            self.draw_text('Created  by  DengHwee', self.credits_font, (255, 250, 250), 10, self.display.get_height() - 20)

            # Game Title
            self.display.blit(self.assets['Game_Title'], (30, 20))
            
            # Getting mouse's current position
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)

            # Drawing button
            self.display.blit(self.assets['Button'], (BUTTON_POS_X, BUTTON_POS_Y_1))
            self.display.blit(self.assets['Button'], (BUTTON_POS_X, BUTTON_POS_Y_2))
            self.display.blit(self.assets['Button'], (BUTTON_POS_X, BUTTON_POS_Y_3))
            self.draw_text('New Game', self.font, (186, 112, 79), BUTTON_POS_X + 6, BUTTON_POS_Y_1 + 10)
            self.draw_text('Edit Map', self.font, (186, 112, 79), BUTTON_POS_X + 6, BUTTON_POS_Y_2 + 10)
            self.draw_text('Quit', self.font, (186, 112, 79), BUTTON_POS_X + 21, BUTTON_POS_Y_3 + 10)
            if self.custom_map == True:
                self.display.blit(self.assets['Button'], (BUTTON_POS_X, BUTTON_POS_Y_4))
                self.draw_text('Custom', self.custom_map_font, (186, 112, 79), BUTTON_POS_X + 11, BUTTON_POS_Y_4 + 4)
                self.draw_text('play', self.custom_map_font, (186, 112, 79), BUTTON_POS_X + 21, BUTTON_POS_Y_4 + 17)

            # Game button collision
                # Checking "Play" button collision
            if self.button_play.collidepoint(mpos):
                self.check_button_click()
                self.draw_text('New Game', self.font, (26, 112, 79), BUTTON_POS_X + 6, BUTTON_POS_Y_1 + 10)
                if self.click:
                    pygame.mixer.music.stop()
                    if self.transition == 0:
                        self.game_state = 'Game'
                        self.sfx['Click'].play()
                    self.display.blit(self.assets['Button_Pushed'], (BUTTON_POS_X, BUTTON_POS_Y_1))
                    
                # Checking "Editing Map" button collision
            if self.button_edit.collidepoint(mpos):
                self.check_button_click()
                self.draw_text('Edit Map', self.font, (26, 112, 79), BUTTON_POS_X + 6, BUTTON_POS_Y_2 + 10)
                if self.click:
                    pygame.mixer.music.stop()
                    if self.transition == 0:
                        self.game_state = 'Editor'
                        self.sfx['Click'].play()
                    self.display.blit(self.assets['Button_Pushed'], (BUTTON_POS_X, BUTTON_POS_Y_2))

                # Checking "Quit" button collision
            if self.button_quit.collidepoint(mpos):
                self.check_button_click()
                self.draw_text('Quit', self.font, (26, 112, 79), BUTTON_POS_X + 21, BUTTON_POS_Y_3 + 10)
                if self.click:
                    if self.transition == 0:
                        self.sfx['Click'].play()
                    pygame.quit()
                    sys.exit()

                # Checking "Custom Map Play" button
            if self.custom_map == True:
                if self.button_custom.collidepoint(mpos):
                    self.check_button_click()
                    self.draw_text('Custom', self.custom_map_font, (26, 112, 79), BUTTON_POS_X + 11, BUTTON_POS_Y_4 + 4)
                    self.draw_text('play', self.custom_map_font, (26, 112, 79), BUTTON_POS_X + 21, BUTTON_POS_Y_4 + 17)
                    if self.click:
                        pygame.mixer.music.stop()
                        if self.transition == 0:
                            self.game_state = 'Custom'
                            self.sfx['Click'].play()
                        self.display.blit(self.assets['Button_Pushed'], (BUTTON_POS_X, BUTTON_POS_Y_4))

            # Checking game's event
            for event in pygame.event.get():
                # Checking quit event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Checking if player press F11 or not
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

            # Create transition between state by creating a black circle to zoom in or zoom out to close the current state
            if self.click:
                self.transition += 1
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            # Choosing next game state
            if self.transition > 30:
                # Game state
                if self.game_state == 'Game':
                    Game(0).run()
                # Editor state
                elif self.game_state == 'Editor':
                    Editor().run()
                # Custom map game state
                elif self.game_state == 'Custom':
                    Game(1).run()

                # Reset menu's attribute everytime return to menu
                self.restart_menu_attribute()

            # Scale game's display size to screen size
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

            # Update next frame for the game to render
            pygame.display.update()
            # Game FPS is set to 60
            self.clock.tick(60)

# Running Menu as the first and the father state, so you can go to different state and return back to it
MainMenu().run()