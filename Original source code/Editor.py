import sys

import pygame

from Scripts.DevUtils import load_images, load_images
from Scripts.Tilemap import Tilemap
from PausedGame import PausedGame

RENDER_SCALE = 2.25

class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Game Editor')
        self.screen = pygame.display.set_mode((1080, 612))

        self.display = pygame.Surface((480, 272), pygame.SRCALPHA)
        
        self.clock = pygame.time.Clock()

        self.toMainRun = False
        self.toMenu = False
        self.pauseGame = False

        self.font = pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 18)
        self.font1 = pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 10)
        
        # Load game assets
        self.assets = {
            # Game graphic asset
            'Grass': load_images('Tiles/Grass'),
            'Water': load_images('Tiles/Water'),
            'Stone': load_images('Tiles/Stone'),
            'Stone_Surface': load_images('Tiles/Stone Surface'),
            'Spike': load_images('Tiles/Spike'),
            'Decor_Grasses': load_images('Tiles/Decor/Grasses'),
            'Decor_Rock': load_images('Tiles/Decor/Prop Rock'),
            'Decor_Mossy_Rock': load_images('Tiles/Decor/Prop Mossy Rock'),
            'Decor_Tree': load_images('Tiles/Decor/Tree'),
            'Spawners': load_images('Tiles/Spawners'),
            'Barrier': load_images('Tiles/Barrier')
        }

        # Load editor's sfx
        self.sfx = {
            'Ambience': pygame.mixer.Sound('Data/SFX/Ambience.wav'),
        }

        # Camera's movement
        # With 4 boolean variable to let the game know that which direction the camera is allow to move,
        # following the X or Y axis and following positive or negative direction
        self.movement = [False, False, False, False]

        # Offset camera
        # This create an effect that convince the human's eye to think that when you walk to an object,
        # everything around it will move closer to you
        self.scroll = [0, 0]

        # Tile
        # The tilemap is a .json file contains a huge directory, with a purpose to let the game know where to load a block, 
        # for example if the .json file say at pos (1,1) is a dirt block and with the second variance
        # than the game will which block to load at that specific position,...
        self.tilemap = Tilemap(self, tile_size = 16)
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        # This was created to solve a crash game bug when loading a file if the .json file is not found
        try:
            self.tilemap.load('Data/Maps/Custom/0.json')
        except FileNotFoundError:
            pass
        
        # Checking whether you has click with your mouse or not
        self.left_clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    # This function is used to draw text into your screen
    def draw_text(self, text, font, color, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.display.blit(textobj, textrect)

    # The main function to run this game state (Editor)
    def run(self):
         # Playing game editor's sfx
        self.sfx['Ambience'].play(-1)

        # This is the first loop of the Editor game state, to notify the instruction of this game state first
        # before entering to the main game state's loop
        while True:
            # Draw editor's instruction before you begin to edit a map
            self.draw_text('Instruction!', pygame.font.Font('Data/Font/ARCADECLASSIC.ttf', 20), (255, 250, 250), self.display.get_width() // 2 - 230, self.display.get_height() // 2 - 120)
            self.draw_text('Press  s  to  save  the  current  of  the  map', self.font, (255, 250, 250), self.display.get_width() // 2 - 230, self.display.get_height() // 2 - 80)
            self.draw_text('Hold  Left  Shift  and  scroll  your  mouse  wheel  to', self.font, (255, 250, 250), self.display.get_width() // 2 - 230, self.display.get_height() // 2 - 60)
            self.draw_text('change  to  different  type  of  tile  to  put  on  your  map', self.font, (255, 250, 250), self.display.get_width() // 2 - 230, self.display.get_height() // 2 - 20)
            self.draw_text('Scroll  your  mouse  wheel  to  change  to  different', self.font, (255, 250, 250), self.display.get_width() // 2 - 230, self.display.get_height() // 2 + 20)
            self.draw_text('variant  of  the  tile', self.font, (255, 250, 250), self.display.get_width() // 2 - 230, self.display.get_height() // 2 + 40)
            self.draw_text('Press  SPACE  to  begin  editing  map', self.font, (26, 112, 79), self.display.get_width() // 2 - 157, self.display.get_height() // 2 + 100)

            # Checking game's event
            for event in pygame.event.get():
                # Checking quit event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Checking if player press Space or not
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toMainRun = True
            # Break this game state's loop to return to Menu
            if self.toMainRun:
                break
            
            pygame.display.update()
            self.clock.tick(60)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))


        # Editor's main system
        while True:
            # Rendering black background
            self.display.fill((0, 0, 0))

            # Using mathematics to calculate the right location for the camera to output to the player's screen
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            # Render the tilemap again so when the player input a new block to the map,
            # it will automatically render to the player's screen
            self.tilemap.render(self.display, offset = render_scroll)

            # Render the current block you want to use on the upper left side of your screen
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            # Get your current mouse position on the screen
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))
            
            # Checking whether a block is on grid or not
            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)

            # Input the block you draw to a temporary tilemap
            if self.left_clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            # Delete a block you want from the temporary tilemap
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            # Display the current tile img to your mouse, so you know whether to put it in the position that you want more accurately
            self.display.blit(current_tile_img, (5, 5))

            # Draw text
            self.draw_text('Press  ESC  to  go  back  to  main  menu!', self.font1, (255, 250, 250), self.display.get_width() - 180, 4)

            # Processing editor event
            for event in pygame.event.get():
                # Checking quit event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Checking whether you input a left click or a right click from your mouse or not
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Left click
                    if event.button == 1:
                        self.left_clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    
                    # Right click
                    if event.button == 3:
                        self.right_clicking = True
                    
                    # Checking if you are holding shift and scroll your mouse wheel, then you will change to the other block,
                    # if you are not holding and scroll your mouse wheel, then you will change to the other variance of the current block
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                        if event.button == 5:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                    else:
                        if event.button == 4:   
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])

                # Reset the variable of clicking to default after releasing your mouse
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_clicking = False
                    if event.button == 3:
                        self.right_clicking = False


                if event.type == pygame.KEYDOWN:
                    # Checking if you are pressing left, up,... to move your camera
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True

                    # Checking if you are pressing Left Shift
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                    # Checking if you has pressed G, if you has then it will make the next block
                    # you input to the tilemap will be an none on-grid tile block
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid

                    # Press S to save the tilemap to the .json file
                    if event.key == pygame.K_s:
                            self.tilemap.save('Data/Maps/Custom/0.json')

                    # Press Escape to pause the game state
                    if event.key == pygame.K_ESCAPE:
                        self.pauseGame = True
                
                # Reset the variable of clicking to default after releasing the key in the keyboard
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            # Checking if the game should go to the paused game state or not
            if self.pauseGame:
                PausedGame(self, frame = pygame.surfarray.array3d(self.display)).run()

            # Rendering the frame of the game state
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

            # Back to game menu
            if self.toMenu == True:
                break
            
            # Update the next frame for game to render
            pygame.display.update()
            # Game setting to 60 FPS
            self.clock.tick(60)