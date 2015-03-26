import pygame, time, math
import eztext # Credit to pywiz32: found online at http://www.pygame.org/project-EzText-920-.html, used for dynamic text input of name
from pygame.locals import*
global screen
pygame.init()


TOTALTIME = 150
STARTSPRITE = 1
NEW_LIVES = 3

Tile_Length = 40
View_Height = 600
View_Width = 800
Half_View_Height = (View_Height)/2
Half_View_Width = (View_Width)/2
View_Screen = (View_Width, View_Height)
screen = pygame.display.set_mode(View_Screen)
pygame.display.set_caption("ColorMania")
class Image(pygame.sprite.Sprite):

    def __init__(self, color, filename, location, size):
 
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(filename).convert_alpha()

        self.image.set_colorkey(color) 
        
        self.image = pygame.transform.scale(self.image, (size[0],size[1]))
        self.rect = self.image.get_rect()

        self.rect.x = location[0]
        self.rect.y = location[1]


class Window(object):
    def __init__(self, functionCall, width, height):
        self.functionCall = functionCall
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.functionCall(self.state, target.rect)

    def custupdate(self, target):
        self.state = self.functionCall(self.state, target)

def complex_camera(camera, target_rect):
    j, k, _, _ = target_rect
    _, _, x, y = camera
    j, k, _, _ = -j+Half_View_Width, -k+Half_View_Height, x, y

    j = min(0, j)                          
    j = max(-(camera.width-View_Width), j)  
    k = max(-(camera.height-View_Height), k)
    k = min(0, k)                          
    return Rect(j, k, x, y)

def loading(name):
    image = pygame.image.load(name)
    return image

class Character(pygame.sprite.Sprite):
    def __init__(self, imagesright, imagesleft, size, imagesrightOne, imagesleftOne, startSprite):
        super(Character, self).__init__()
        self.imagesright = imagesright
        # assuming both images are 64x64 pixels
        self.imagesleft = imagesleft

        self.tempimagesright = imagesrightOne
        self.tempimagesleft = imagesleftOne
           
        self.name = ""

        self.currrentSprite = startSprite

        self.changeSprites(self.currrentSprite, size)
        self.index = 0
        self.image = self.imagesright[self.index]

        self.sound = True

        self.rect = self.image.get_rect()
        self.rect = self.rect.inflate(-10, 0)
        self.x = 320
        self.y = 30
        self.xvel = 0 
        self.yvel = 0
        self.onGround = False
        self.gemsCollected = []
        self.lives = 3
        self.time = 0
        self.complete = False
        self.gems = 0
        self.lives_start = self.lives
        
    def changeSprites(self, spritIndex, size):
        loadImages(spritIndex)
        for x in range(len(self.imagesright)):
            self.imagesright[x] = pygame.transform.scale(self.imagesright[x], (size[0],size[1]))
            self.tempimagesright[x] = pygame.transform.scale(self.tempimagesright[x], (size[0],size[1]))
        for x in range(len(self.imagesleft)): 
            self.imagesleft[x] = pygame.transform.scale(self.imagesleft[x], (size[0],size[1]))
            self.tempimagesleft[x] = pygame.transform.scale(self.tempimagesleft[x], (size[0],size[1]))
        self.index = 0
        self.image = self.imagesright[self.index]

    def resetStats(self):
        self.gemsCollected = []
        self.lives = NEW_LIVES
        self.gems = 0
        self.time = 0
        self.complete = False

    def update(self, up, down, left, right, platforms, gemActivate, gems, base_platforms, goals, firstGem, secondGem, thirdGem):

        isInvisibility = False
        gemInt = -1; 
        if up: 
            if self.onGround: self.yvel -= 11
            #if gemActivate: 
            #    if (self.gemsCollected[0].typeOfGem == "Jumping"): 
            #        self.gemsCollected[0].time -= 1; 
            #        if self.onGround: 
            #            self.gemsCollected[0].Jumping(self)
        if down: 
            pass 
        if right:
            if (self.onGround): 
                self.index += 1
            self.xvel = 8
            if self.index >= len(self.imagesright):
                self.index = 0
            self.image = self.imagesright[self.index]
        if left:
            if (self.onGround): 
                self.index += 1
            self.xvel = -8
            if self.index >= len(self.imagesleft):
                self.index = 0
            self.image = self.imagesleft[self.index]
        #if gemActivate: 
        #    self.gemsCollected[0].time -= 1
        #    if (self.gemsCollected[0].typeOfGem == "Invisibility"):  
        #        isInvisibility = True; 
        if firstGem: 
            gemInt = 0
        if secondGem: 
            gemInt = 1
        if thirdGem: 
            gemInt = 2
        self.gems = gemInt + 1
        if (firstGem or secondGem or thirdGem): 
            self.gemsCollected[gemInt].time -= 1
            if (self.gemsCollected[gemInt].typeOfGem == "Invisibility"): 
                isInvisibility = True; 
            if (self.gemsCollected[gemInt].typeOfGem == "Jumping") and up: 
                if self.onGround: 
                    self.gemsCollected[gemInt].Jumping(self)
            if (self.gemsCollected[gemInt].typeOfGem == "Shrinking"):
                self.resize(30)
            if (self.gemsCollected[gemInt].typeOfGem == "Traction"):
                self.xvel /= 5 
            if (self.gemsCollected[gemInt].typeOfGem == "Sprinting"):
                self.xvel *= 2
            if (self.gemsCollected[gemInt].typeOfGem == "Flying"):
                self.fly(up, down)
        if not self.onGround: 
            self.yvel += 0.3
            if self.yvel > 100: self.yvel= 100
        if not(left or right): 
            self.xvel = 0
        
        self.rect.right += self.xvel 
        self.collide(self.xvel, 0, platforms, gems, isInvisibility, base_platforms, goals)
        
        self.rect.top += self.yvel
        self.onGround = False
        self.collide(0, self.yvel, platforms, gems, isInvisibility, base_platforms, goals)

    def updateTime(self, val):
        self.time += val
        
    def loseLife(self):
        self.lives -=1
    def setTime(self, val):
        self.time =  val
        
    def getTime(self):
        return self.time          
    def getNumGems(self):
        return self.gems
    def collide (self, xvel, yvel, platforms, gems, isInvisibility, base_platforms, goals):
        if (isInvisibility): 
            for p in base_platforms: 
                if pygame.sprite.collide_rect(self, p):
                    if xvel > 0:
                        self.rect.right = p.rect.left
                    if xvel < 0:
                        self.rect.left = p.rect.right
                    if yvel >= 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 1
        else: 
            for p in platforms:
                if pygame.sprite.collide_rect(self, p):
                    if xvel > 0:
                        self.rect.right = p.rect.left
                    if xvel < 0:
                        self.rect.left = p.rect.right
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 1
        
                for g in gems: 
                    if pygame.sprite.collide_rect(self,g):
                        if len(self.gemsCollected) < 3: 
                            g.Collided()
                            self.gemsCollected.append(g)  
                        
    def victory(self, goals):
        for b in goals: 
            if pygame.sprite.collide_rect(self,b):
                self.complete = True
                return True
            
        
    def is_dead(self, level_height, spawn):
        if (self.rect.top >= level_height + 2): 
            return True
        if ((TOTALTIME - self.getTime()) <= 0 ): 
            return True
        return False
    
    def reset(self, loc, level_state, originial_level_state):
        self.x =  loc[0]
        self.y = loc[1]
        self.rect.x = loc[0]
        self.rect.y = loc[1]
        del self.gemsCollected[:]
        self.gemsCollected = []
        if (level_state != originial_level_state): 
            self.lives_start = self.lives 
        self.hidefResize()


    def fly(self, up, down):
        self.onGround = False
        self.yvel -= 0.3
        if up:
            self.yvel = -3
        if down:
            self.yvel = 11
    def resize(self, value):    
        tempx = self.rect.x
        tempy = self.rect.y
        self.image = pygame.transform.scale(self.image, (value,value))
        for x in range(len(self.imagesright)): 
            self.imagesright[x] = pygame.transform.scale(self.imagesright[x], (value,value))
        for x in range(len(self.imagesleft)): 
            self.imagesleft[x] = pygame.transform.scale(self.imagesleft[x], (value,value))
        self.rect = self.image.get_rect()
        self.rect.x = tempx
        self.rect.y = tempy

    def hidefResize(self): 
        tempx = self.rect.x
        tempy = self.rect.y
        self.imagesright = self.tempimagesright
        self.imagesleft = self.tempimagesleft
        self.rect = self.imagesright[0].get_rect()
        self.rect.x = tempx
        self.rect.y = tempy

def display_box(screen, message, x, y, lives):
    font = pygame.font.SysFont("Courier New", 20)
    if(lives == 0):
        font = pygame.font.SysFont("Courier New", 36)
        prompt = font.render(message, 1, [0, 0, 255])
    elif(lives == 4):
        prompt = font.render(message, 1, [0, 0, 255])
    else:
        prompt = font.render(message % lives, 1, [0, 0, 255])
    screen.blit(prompt, (x, y))  
        
class Gem(pygame.sprite.Sprite):
    def __init__(self, color, filename, location, typeOfGem, size):
        # call parent class constructor
        pygame.sprite.Sprite.__init__(self)
        
        # load the image, converting the pixel format for optimization
        self.image = pygame.image.load(filename).convert_alpha()
        # make 'color' transparent on the image
        self.image.set_colorkey(color) 
        # set the rectangle defined for this image for collision detection
        self.image = pygame.transform.scale(self.image, (size[0],size[1]))
      
        # position the image
        
        self.rect = self.image.get_rect()
        self.rect.x = location[0]
        self.rect.y = location[1]
        
        self.typeOfGem = typeOfGem
        self.exist = True
        
        if (self.typeOfGem == "Invisibility"): 
            self.type = "Invisibility"
            self.checkCollision = False
            self.time = 7 * 60

        if (self.typeOfGem == "Jumping"): 
            self.type = "Jumping"
            self.yvel = 4
            self.time = 15 * 60 
        if (self.typeOfGem == "Traction"):
            self.type = "Traction"
            self.xvel = 1
            self.time = 20 * 60 
        if (self.typeOfGem == "Flying"):
            self.type = "Flying"
            self.time = 20 * 60 
        if (self.typeOfGem == "Shrinking"):
            self.type = "Shrinking"
            self.time = 4 * 60
        if (self.typeOfGem == "Sprinting"):
            self.type = "Sprinting"
            self.time = 15 * 60
    def Jumping(self, Character): 
        Character.yvel -= 4
    def Collided (self):
        self.exist = False
        self.rect = (0, 0, 0 , 0)
        self.kill()
        
class Menu(pygame.sprite.Sprite):
    def __init__(self,color, filename, location, types):
        # call parent class constructor
        pygame.sprite.Sprite.__init__(self)
        
        # load the image, converting the pixel format for optimization
        self.image = pygame.image.load(filename).convert_alpha()
        # make 'color' transparent on the image
        self.image.set_colorkey(color) 
        # set the rectangle defined for this image for collision detection
      
        # position the image
        self.rect = self.image.get_rect()
        self.rect.x = location[0]
        self.rect.y = location[1]
        
        self.type = types

class HeadsUpDisplay(pygame.sprite.Sprite): 
    def __init__(self, filename, color, filenameOne, filenameTwo, filenameThree, filenameFour, filenameFive, filenameSix): 
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image.set_colorkey(color)

        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        self.imageOne = pygame.image.load(filenameOne).convert_alpha()
        self.imageTwo = pygame.image.load(filenameTwo).convert_alpha()
        self.imageThree = pygame.image.load(filenameThree).convert_alpha()
        self.imageOneUsing = pygame.image.load(filenameFour).convert_alpha()
        self.imageTwoUsing = pygame.image.load(filenameFive).convert_alpha()
        self.imageThreeUsing = pygame.image.load(filenameSix).convert_alpha()

    def displayToScreen(self, time, lives, screen, Character, usingGemOne, usingGemTwo, usingGemThree): 
        screen.blit(self.image, (0,0))

        if (len(Character.gemsCollected) == 1 and not(usingGemOne)):
            screen.blit(self.imageOne, (0,0))
            screen.blit(Character.gemsCollected[0].image, (18, 50))
        if (len(Character.gemsCollected) == 2 and not (usingGemTwo)): 
            screen.blit(self.imageTwo, (0,0))
            screen.blit(Character.gemsCollected[0].image, (18, 50))
            screen.blit(Character.gemsCollected[1].image, (85, 50))
        if (len(Character.gemsCollected) == 3 and not(usingGemThree)): 
            screen.blit(self.imageThree, (0,0))
            screen.blit(Character.gemsCollected[0].image, (18, 50))
            screen.blit(Character.gemsCollected[1].image, (85, 50))
            screen.blit(Character.gemsCollected[2].image, (150, 50))
        start_coord = 18 
        if (usingGemOne): 
            screen.blit(self.imageOneUsing, (0,0))
            for x in range(len(Character.gemsCollected)): 
                if (x > 0): 
                    screen.blit(Character.gemsCollected[x].image, (start_coord, 50))
                start_coord += 60
        if (usingGemTwo): 
            screen.blit(self.imageTwoUsing, (0,0))
            for x in range(len(Character.gemsCollected)): 
                if (x != 1 and x != 3): 
                    screen.blit(Character.gemsCollected[x].image, (start_coord, 50))
                start_coord += 60
        if (usingGemThree): 
            screen.blit(self.imageThreeUsing, (0,0)) 
            for x in range(len(Character.gemsCollected)): 
                if (x != 3 and x != 2): 
                    screen.blit(Character.gemsCollected[x].image, (start_coord, 50))
                start_coord += 60
        font = pygame.font.SysFont("Courier New", 16)
        promptTime = font.render("%d Seconds"  % time , 1, [0, 0, 0])
        screen.blit(promptTime, (78, 25))
        promptLives = font.render("%d" %lives, 1, [0,0,0])
        screen.blit(promptLives, (78, 7))
        white_box = pygame.draw.rect(screen, (255, 255, 255), (0, 0, 10, 10))

class LevelMap(pygame.sprite.Sprite):
    def __init__(self, level, levelTileset, gemsVector, hintsVector): 
        self.platforms, self.gems, self.allSprites, self.base_platforms, self.goal, self.allSprites_scroll, self.level_scroll, self.scaleFactor, self.EasyHints, self.HardHints = Level_Vector_Creations(level,levelTileset,gemsVector,hintsVector)
        self.level = level
        self.levelTileset = levelTileset
        self.gemsVector = gemsVector
        self.hintsVector = hintsVector

    def getValues(self):
        return self.platforms, self.gems, self.allSprites, self.base_platforms, self.level, self.goal, self.EasyHints, self.HardHints

    def getScroll(self):
        return self.level_scroll, self.allSprites_scroll, self.level, self.scaleFactor

    def getRestart(self):
        return self.level, self.levelTileset, self.gemsVector, self.hintsVector

def CheckOutofBounds(Character, level_height, level_width):
    if (Character.rect.left <= 0): 
        Character.rect.left = 0
    if (Character.rect.right >= level_width): 
        Character.rect.right = level_width
    if (Character.rect.top <= 0): 
        Character.rect.top = 0
        Character.yvel = 1

def Music_Play(music_file, repetitions, sound):
    if sound:
        pygame.mixer.init()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(repetitions)
    
def Tutorial(Character):
    if (Character.rect.x > 0 and Character.rect.x < 1000): #if the player is within the starting section, display these words
        display_box(screen, "Welcome! To move, use the up or side arrow keys.", View_Width/6, View_Height/3, 4)
        display_box(screen, "Walk right to continue.",View_Width/3,View_Height/2.5,4)
    if(Character.getNumGems() == 0):
        if (Character.rect.x > 1100 and Character.rect.x < 2000):
            display_box(screen, "Walk over the ghost gem to collect it.",View_Width/4,View_Height/3,4)
            display_box(screen, "Press the Number 1 Key to activate gem.",View_Width/3.8,View_Height/2.5,4)
        elif (Character.rect.x > 2500 and Character.rect.x < 3500): 
            display_box(screen, "Walk over the Jumping gem to collect it.",View_Width/4,View_Height/3,4)
            display_box(screen, "Press the Number 1 Key to activate gem.",View_Width/3.8,View_Height/2.5,4)
    else:
        if(Character.gemsCollected[0].type == "Invisibility" and Character.gemsCollected[0].time > 0):
            display_box(screen, "You can walk through everything for 7 seconds.",View_Width/5.3,View_Height/3,4)
            display_box(screen, "Walk through the wall on the right to continue.",View_Width/6,View_Height/2.5,4)

        elif(Character.gemsCollected[0].type == "Jumping" and Character.gemsCollected[0].time > 0):
            display_box(screen, "Jump over the wall using your elevated jumping abilities",View_Width/3 - 190,View_Height/3,4)
            display_box(screen, "Hit the exit sign to reach the menu again",View_Width/6,View_Height/2.5,4)
    
        #pygame.display.update()
    if(Character.rect.x > 3600):
        display_box(screen, "LEVEL COMPLETED!",View_Width/3 - 190,View_Height/3,4)
        Character.time = 150

def Diagnostics(score, screen):
    if(score < 200):
        display_box(screen, "The player should continue to play to practice making quick decisions.",View_Width/8,View_Height/2, 4)
    elif(score < 400):
        display_box(screen, "The player may want to work on making decisions faster.",View_Width/7,View_Height/2, 4)
    elif(score < 600):
        display_box(screen, "The player did well but could improve speed of decisions.",View_Width/7,View_Height/2, 4)
    else:
        display_box(screen, "The player did a great job!",View_Width/3,View_Height/2, 4)
    display_box(screen, "Press the Escape Key to go back",View_Width/3 - 35 , 2*View_Height/3, 4)

def View_Map(platforms, allSprites, level, scale):
    first_level_height = View_Height
    first_level_length = len(level[0]) * Tile_Length * scale
    cameraScrolling = Window(complex_camera, first_level_length, first_level_height)

    invis_objects = pygame.draw.rect(screen, (255, 255, 255), (first_level_length, first_level_height, 10, 10))
    invis_objects.x = first_level_length - View_Width/2
    invis_objects.y = 0

    active = True
    xvel = 0.1
    font = pygame.font.SysFont("Courier New", 40)
    prompt = font.render("Level Begins", 1, [0, 0, 255])
    

    while active:
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit
                active = False
                return 

        cameraScrolling.custupdate(invis_objects)
        for k in range(15):
            screen.blit(sky, [400, k * Tile_Length])
        for k in range(15):
            screen.blit(sky, [0, k * Tile_Length])
        for k in range(15):
            screen.blit(sky, [200, k * Tile_Length])
        for k in range(15):
            screen.blit(sky, [600, k * Tile_Length])
        for sprite in allSprites: 
            screen.blit(sprite.image, cameraScrolling.apply(sprite))

        if (invis_objects.x > first_level_length/2.0):
            xvel += 0.05
        else: 
            xvel -= 0.03

        if(invis_objects.x < 50): 
            screen.blit(prompt, (View_Height/2, View_Width/5)) 
            pygame.display.update()
            time.sleep(1)
            return;

        invis_objects.x -= xvel; 

        pygame.display.update()


def Level_Screens(platforms, gems, allSprites, base_platforms, player, level, background, player_sprite_vec, goals, EasyHints, HardHints, levelState):
    first_level_height = len(level) * Tile_Length
    first_level_length = len(level[0]) * Tile_Length
    camera = Window(complex_camera, first_level_length, first_level_height)

    pause = False #Controls when paused
    esclifted = True #Tracks if the key is down for escape
    totalPauseTime = 0 #Tracks the total paused time
    pauseStartTime = 0 #Tracks when a paused is started
    pauseEndTime = 0 #Tracks when a paused is ended
    
    timer = pygame.time.Clock()
    gemActivate = False
    active = True
    up = down = left = right = False
    firstGem = secondGem = thirdGem = False
    spawn = time.clock()
    precedence = 0; 
    while active:  
        timer.tick(60)
        start = time.clock() - spawn #Takes the time minus the time spent on the menu
        player.setTime(start - totalPauseTime) #Sets the time minus the total time paused
        #pygame.mixer.music.play()
        #if (gemActivate): 
        #    if (player.gemsCollected[0].time <= 0): 
        #        gemActivate = False
        #        del player.gemsCollected[:]
        #        #player.gemsCollected.remove(Gem)
        if (pause):
            screen.fill([208,244,247]) 
            for men in pause_men:
                screen.blit(men.image, men)

            for event in pygame.event.get():
                if event.type == QUIT:
                    raise SystemExit
                    active = False
                    return 
                if (event.type == pygame.MOUSEBUTTONDOWN):
                    pos = pygame.mouse.get_pos()
                    menSelect = 0
                    for men in pause_men:
                        if men.rect.collidepoint(pos):
                            menSelect = men.type
                            if menSelect == 0:
                                pause  = not(pause)
                                pauseEndTime = time.clock()
                                totalPauseTime += pauseEndTime - pauseStartTime #Adds total time paused for that pausing time
                            elif menSelect == 1:
                                player.resetStats()
                                return (1, level_state)
                            elif menSelect == 2:
                                pause = not(pause)
                                player.resetStats()
                                player.reset([0,0], 0, 0)
                                return (0, level_state)
                            elif menSelect == -1:
                                return (-1, level_state)
                if event.type == KEYDOWN and event.key == K_ESCAPE and esclifted:
                    esclifted = False
                    pause  = not(pause)
                    pauseEndTime = time.clock()
                    totalPauseTime += pauseEndTime - pauseStartTime #Adds total time paused for that pausing time
                if event.type == KEYUP and event.key == K_ESCAPE and not(esclifted):
                    esclifted = True
        else:

            for event in pygame.event.get():
                if event.type == QUIT:
                    raise SystemExit
                    active = False
                    return 
                if event.type == KEYDOWN and event.key == K_UP:
                    up = True
                    Music_Play("Char Jump.wav", 0, player.sound)
                if event.type == KEYDOWN and event.key == K_LEFT:
                    left = True
                if event.type == KEYDOWN and event.key == K_RIGHT:
                    right = True
                #if event.type == KEYDOWN and event.key == K_SPACE:
                #    if (len(player.gemsCollected) > 0):  
                #        gemActivate = True
                #        if (player.gemsCollected[0].typeOfGem == "Invisibility"): 
                #            Music_Play("Gem1 GhostInvis.wav", 0)   
                if event.type == KEYUP and event.key == K_UP:
                    up = False
                if event.type == KEYUP and event.key == K_RIGHT:
                    right = False
                if event.type == KEYUP and event.key == K_LEFT:
                    left = False
                if event.type == KEYDOWN and event.key == K_ESCAPE and esclifted:
                    esclifted = False
                    pause  = not(pause)
                    pauseStartTime = time.clock()
                if event.type == KEYUP and event.key == K_ESCAPE and not(esclifted):
                    esclifted = True
                if event.type == KEYDOWN and event.key == K_1: 
                    if (len(player.gemsCollected) > 0): 
                        firstGem = True
                    if not(secondGem or thirdGem): 
                        precedence = 1
                if event.type == KEYDOWN and event.key == K_2: 
                    if (len(player.gemsCollected) > 1): 
                        secondGem = True
                    if not(thirdGem or firstGem): 
                        precedence = 2 
                if event.type == KEYDOWN and event.key == K_3:
                    if (len(player.gemsCollected) > 2): 
                        thirdGem = True
                    if not(secondGem or firstGem): 
                        precedence = 3

            if (firstGem and precedence == 1): 
                if (secondGem):
                    player.gemsCollected[0].time = 0
                    precedence = 1
                if (thirdGem):
                    player.gemsCollected[0].time = 0
                    precedence = 2
                if (player.gemsCollected[0].time <= 0):
                    if(player.gemsCollected[0].typeOfGem == "Shrinking"):
                        player.hidefResize()
                    if not(secondGem): 
                        firstGem = False
                    secondGem = False
                    if (thirdGem):
                        secondGem = True
                        thirdGem = False
                    del player.gemsCollected[0]
            if (secondGem and precedence == 2): 
                if (firstGem): 
                    player.gemsCollected[1].time = 0
                    precedence = 1
                if (thirdGem): 
                    player.gemsCollected[1].time = 0
                    precedence = 2
                if (player.gemsCollected[1].time <= 0):
                    if(player.gemsCollected[1].typeOfGem == "Shrinking"):
                        player.hidefResize()
                    if not(thirdGem): 
                        secondGem = False
                    thirdGem = False
                    del player.gemsCollected[1]
            if (thirdGem and precedence == 3): 
                if (firstGem): 
                    player.gemsCollected[2].time = 0
                    precedence = 1
                    firstGem = True
                if (secondGem): 
                    player.gemsCollected[2].time = 0
                    precedence = 2
                    secondGem = True
                if (player.gemsCollected[2].time <= 0):
                    if(player.gemsCollected[2].typeOfGem == "Shrinking"):
                        player.hidefResize()
                    thirdGem = False
                    del player.gemsCollected[2]

            for k in range(15):
                screen.blit(sky, [400, k * Tile_Length])
            for k in range(15):
                screen.blit(sky, [0, k * Tile_Length])
            for k in range(15):
                screen.blit(sky, [200, k * Tile_Length])
            for k in range(15):
                screen.blit(sky, [600, k * Tile_Length])


                
            camera.update(player)
            CheckOutofBounds(player, first_level_height, first_level_length)

            if(player.is_dead(first_level_height, spawn)):
                player.loseLife()
                return (0, level_state); 
            
            if (player.victory(goals)):
                return (0, level_state + 1); 
            
            player.update(up, down, left, right, platforms, gemActivate, gems, base_platforms, goals, firstGem, secondGem, thirdGem)
            for sprite in allSprites: 
                screen.blit(sprite.image, camera.apply(sprite))
            if (player.lives_start - player.lives == 2): 
                for x in EasyHints: 
                    screen.blit(x.image, camera.apply(x))
            if (player.lives_start - player.lives == 1): 
                for x in HardHints: 
                    screen.blit(x.image, camera.apply(x))
            for p in player_sprite_vec: 
                screen.blit(p.image, camera.apply(p))

            #if(player.lives > 0): 
            #    if (not(gamestate == 4)):
            #        display_box(screen, "Lives: %d", 20, 10, player.lives)
            #    display_box(screen, "Time: %d seconds", 20, 40, TOTALTIME - player.getTime()) #now just takes total time minus player time
            #TimeLeft = TOTALTIME - player.getTime()
            #HUD.displayToScreen(TimeLeft , player.lives, screen)

                
            if (gamestate == 4):
                Tutorial(player)

            TimeLeft = TOTALTIME - player.getTime()
            HUD.displayToScreen(TimeLeft , player.lives, screen, player, firstGem, secondGem, thirdGem)
            
        pygame.display.update()
        
def Level_Vector_Creations(level,levelTileset,gemsVector,hintsVector):
    
    level_scroll = []
    allSprites_scroll = pygame.sprite.Group()

    totalHeight = Tile_Length * len(level)
    totalWidth = Tile_Length * len(level[0])
    scaleFactor = (View_Height + 0.0)/(0.0 + totalHeight)
    scaleTile = Tile_Length * scaleFactor

    platforms = []
    gems = []
    allSprites = pygame.sprite.Group()
    base_platforms = []
    goal = []
    x = 0
    y = 0
    x_scaleTile = 0
    y_scaleTile = 0

    SemiHints = pygame.sprite.Group()
    AllHints = pygame.sprite.Group()
    
    for row in level: 
        for col in row:
            if col == "M": #Mid
                Mid_Platform = Image((255,255,255),levelTileset[0], (x,y), (Tile_Length, Tile_Length))
                platforms.append(Mid_Platform)
                allSprites.add(Mid_Platform)
                Mid_Platform_Scroll = Image((255, 255, 255), levelTileset[0], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(Mid_Platform_Scroll)
                allSprites_scroll.add(Mid_Platform_Scroll)
                if (y == (len(level) - 1)*Tile_Length): 
                    base_platforms.append(Mid_Platform)
            if col == "L": #Left or Long
                Start_Platform = Image((255,255,255),levelTileset[1], (x,y), (Tile_Length, Tile_Length))
                platforms.append(Start_Platform)
                allSprites.add(Start_Platform)
                Start_Platform_Scroll = Image((255, 255, 255), levelTileset[1], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(Start_Platform_Scroll)
                allSprites_scroll.add(Start_Platform_Scroll)
                if (y == (len(level) - 1)*Tile_Length): 
                    base_platforms.append(Start_Platform)
            if col == "R": #Right
                End_Platform = Image((255,255,255),levelTileset[2], (x,y), (Tile_Length, Tile_Length))
                platforms.append(End_Platform)
                allSprites.add(End_Platform)
                End_Platform_Scroll = Image((255, 255, 255), levelTileset[2], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(End_Platform_Scroll)
                allSprites_scroll.add(End_Platform_Scroll)
                if (y == (len(level) - 1)*Tile_Length): 
                    base_platforms.append(End_Platform)
            if col == "C": #Cliff Left
                Start_Ledge = Image((255,255,255),levelTileset[3], (x,y), (Tile_Length,Tile_Length))
                platforms.append(Start_Ledge)
                allSprites.add(Start_Ledge)
                Start_Ledge_Scroll = Image((255, 255, 255), levelTileset[3], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(Start_Ledge_Scroll)
                allSprites_scroll.add(Start_Ledge_Scroll)
            if col == "D": #Cliff Right
                End_Ledge = Image((255,255,255),levelTileset[4], (x,y), (Tile_Length,Tile_Length))
                platforms.append(End_Ledge)
                allSprites.add(End_Ledge)
                End_Ledge_Scroll = Image((255, 255, 255), levelTileset[4], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(End_Ledge_Scroll)
                allSprites_scroll.add(End_Ledge_Scroll)
            if col == "B": #Box
                Box = Image((255,255,255),levelTileset[5], (x,y), (Tile_Length, Tile_Length))
                platforms.append(Box)
                allSprites.add(Box)
                Box_Scroll = Image((255, 255, 255), levelTileset[5], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(Box_Scroll)
                allSprites_scroll.add(Box_Scroll)
            if col == "F": #signExit/Finish
                Sign = Image((255,255,255),levelTileset[6], (x,y), (Tile_Length, Tile_Length))
                goal.append(Sign)
                allSprites.add(Sign)
                Sign_Scroll = Image((255, 255, 255), levelTileset[6], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(Sign_Scroll)
                allSprites_scroll.add(Sign_Scroll)
            if col == "H": #Hill
                Hill = Image((255,255,255),levelTileset[7], (x,y - 36), (Tile_Length, Tile_Length*2))
                allSprites.add(Hill)
                Hill_Scroll = Image((255, 255, 255), levelTileset[7], (x_scaleTile,y_scaleTile - math.floor(36*scaleFactor)), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length*2))))
                level_scroll.append(Hill_Scroll)
                allSprites_scroll.add(Hill_Scroll)
            if col == "G": #Ghost Gem
                InvisGem = Gem((255,255,255), gemsVector[0], (x,y), "Invisibility", (Tile_Length - 10, Tile_Length))
                gems.append(InvisGem)
                allSprites.add(InvisGem)
                InvisGem_Scroll = Image((255, 255, 255), gemsVector[0], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*Tile_Length)), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(InvisGem_Scroll)
                allSprites_scroll.add(InvisGem_Scroll)
            if col == "J": #Spring/Jump Gem
                JumpGem = Gem((255,255,255),gemsVector[1], (x,y), "Jumping", ((Tile_Length - 10, Tile_Length)))     
                gems.append(JumpGem)
                allSprites.add(JumpGem)    
                JumpGem_Scroll = Image((255, 255, 255), gemsVector[1], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*(Tile_Length - 10))), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(JumpGem_Scroll)
                allSprites_scroll.add(JumpGem_Scroll)
            if col == "S": #Shrinking Gem
                ShrinkGem = Gem((255,255,255),gemsVector[2], (x,y), "Shrinking", ((Tile_Length - 10, Tile_Length)))     
                gems.append(ShrinkGem)
                allSprites.add(ShrinkGem)    
                ShrinkGem_Scroll = Image((255, 255, 255), gemsVector[2], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*(Tile_Length - 10))), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(ShrinkGem_Scroll)
                allSprites_scroll.add(ShrinkGem_Scroll)
            if col == "P": #Sprinting Gem
                SprintGem = Gem((255,255,255),gemsVector[3], (x,y), "Sprinting", ((Tile_Length - 10, Tile_Length)))     
                gems.append(SprintGem)
                allSprites.add(SprintGem)    
                SprintGem_Scroll = Image((255, 255, 255), gemsVector[3], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*(Tile_Length - 10))), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(SprintGem_Scroll)
                allSprites_scroll.add(SprintGem_Scroll)
            if col == "Y": #Flying Gem
                FlyGem = Gem((255,255,255),gemsVector[4], (x,y), "Flying", ((Tile_Length - 10, Tile_Length)))     
                gems.append(FlyGem)
                allSprites.add(FlyGem)    
                FlyGem_Scroll = Image((255, 255, 255), gemsVector[4], (x_scaleTile,y_scaleTile), (int(math.ceil(scaleFactor*(Tile_Length - 10))), int(math.floor(scaleFactor*Tile_Length))))
                level_scroll.append(FlyGem_Scroll)
                allSprites_scroll.add(FlyGem_Scroll)
            if col == "1": #Right easy hint arrow
                EasyHints = Image((255,255,255), hintsVector[0], (x,y), (Tile_Length, Tile_Length))
                SemiHints.add(EasyHints)
            if col == "2" or col == "1": #Right hard hint arrow
                HardHints = Image((255,255,255), hintsVector[0], (x,y), (Tile_Length, Tile_Length))
                AllHints.add(HardHints)
            x += Tile_Length; 
            x_scaleTile += scaleTile
        y += Tile_Length;
        y_scaleTile += scaleTile
        x = 0
        x_scaleTile = 0
    return (platforms, gems, allSprites, base_platforms, goal, allSprites_scroll, level_scroll, scaleFactor, SemiHints, AllHints)

def isTyped(event):
    if event.type == KEYDOWN and event.key == K_UP:
        up = True
        Music_Play("Char Jump.wav", 0, False)

def loadImages(index):
    #player vector animation initializations
    sindex = str(index)
    del imagesright[:]
    del imagesleft[:]
    del imagesrightResize[:]
    del imagesleftResize[:]

    imagesright.append(loading('p' + sindex + '_walk02.png'))
    imagesright.append(loading('p' + sindex + '_walk03.png'))
    imagesright.append(loading('p' + sindex + '_walk04.png'))
    imagesright.append(loading('p' + sindex + '_walk05.png'))
    imagesright.append(loading('p' + sindex + '_walk06.png'))
    imagesright.append(loading('p' + sindex + '_walk07.png'))
    imagesright.append(loading('p' + sindex + '_walk08.png'))
    imagesright.append(loading('p' + sindex + '_walk09.png'))
    imagesright.append(loading('p' + sindex + '_walk10.png'))

    
    imagesleft.append(loading('p' + sindex + '_walk12.png'))
    imagesleft.append(loading('p' + sindex + '_walk13.png'))
    imagesleft.append(loading('p' + sindex + '_walk14.png'))
    imagesleft.append(loading('p' + sindex + '_walk15.png'))
    imagesleft.append(loading('p' + sindex + '_walk16.png'))
    imagesleft.append(loading('p' + sindex + '_walk19.png'))
    imagesleft.append(loading('p' + sindex + '_walk17.png'))
    imagesleft.append(loading('p' + sindex + '_walk17.png'))
    imagesleft.append(loading('p' + sindex + '_walk18.png'))

    
    imagesrightResize.append(loading('p' + sindex + '_walk02.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk03.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk04.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk05.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk06.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk07.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk08.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk09.png'))
    imagesrightResize.append(loading('p' + sindex + '_walk10.png'))

    
    imagesleftResize.append(loading('p' + sindex + '_walk12.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk13.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk14.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk15.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk16.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk19.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk17.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk17.png'))
    imagesleftResize.append(loading('p' + sindex + '_walk18.png'))

def levelRestart(levels, index, level, levelTileset1, gemsVector, hintsVector):
    newLevel = LevelMap(level, levelTileset1, gemsVector, hintsVector)
    levels[index] = newLevel
    return levels


level_tutorial= [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "X                            B                                                           X",
        "X                            B                                                           X",
        "X                            B            CMMMMMD B                                      X",
        "X                            B                    B                                      X",
        "X                            B         CMD        B                                      X",
        "X                            B                    B                                      X",
        "X                            B                    B                                      X",
        "X                   CMMMD    B              CMMMMDB                          B           X",
        "X                            B    CMMMMD          B                          B           X",
        "X                            B                    B                          B           X",
        "X        CMMMMMMMMD          B                    B                          B           X",
        "X                            B           CMMMD    B               J          B           X",
        "X                            B                    B              CMMMMMD     B           X",
        "X                    CMMD    B                    B                          B           X",
        "X            CMMMD           B     CMMMMD    BB   B       CMMD               B           X",  
        "X                                            BB   B                          B           X", 
        "X                                 G          BB   B                          B         F X",
        "LMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMR",
        ]

#platforms_tutorial, gems_tutorial, allSprites_tutorial, base_platforms_tutorial, goals_tutorial = Level_Vector_Creations(level_tutorial)

level_one= [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "X                                                                                                                                       X",
        "X                                                                          CMMMMMD                                                      X",
        "X     CMMMMMD                                CMMMMMD                                    CMD                                             X",
        "X                                                                                                  CMD                                  X",
        "X                      CMMMD          CMD                                                                                               X",
        "X                                                                           CMD            CMD                                          X",
        "X                                                      H                                          1  J   H                     B        X",
        "X               H                CMMMMD               CMMMMD                                        CMMMMD               2     B        X",
        "X            CMMMMMMMMMMD                                             2         B       H                                      B        X",
        "X                                                                          CMD  B      CMMMMMD                                 B        X",
        "X                                                                               B                                              B        X",
        "X  CMMMMD                               CMMMD              B        CMD         B                 CMMD                    CMD  B        X",
        "X                B                             2           B                    B            H                                 B        X",
        "X       G        B   CMMD     1                   CMMMMD   B              CMD   B          CMMMD                               B        X",
        "X      CMMMD     B                CMMMMD                   B                    B                                      CMD     B        X",  
        "X                B           B                H            B         CMMD       B    CMD                          BB           B        X", 
        "BBBBB                                                                                                                                    ",
        "X           F    B   H  H    B               CMMMMD        B    H               B             H        H         BBB           B      F X",
        "LMMMMMMR   LMMMMMMMMMMMMMMMMMMMMMR                   LMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMR",
        ]

#Ghost, Jumping, and Shrink
level_two= [
        "XXXXXXBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXBBBXXXXXXXXXXXXXXXXXX",
        "X     B                                       B                                                                     BBB                  ",
        "MR    BG                                      B                                                                     BBB                  ",
        "X     BMD                                     B                                                                                          ",
        "X    LB          CMMD                         B                                        BBBMMD                       BBBMMD               ",
        "X     B                                       B            CMMD                        BBB                          BBB                  ",
        "MR    B                                       B                                     CMMBBB                     CMMMDBBB               CMM",
        "X     BMD        BBBBMMD                      B                                        BBB                          BBB                  ",
        "X    LB          BBBB                         B                      CMMD              BBB          CMMD            BBB                  ",
        "X     B          BBBB                         B                                        BBB                          BBBMMMMMMMMD         ",
        "X              CMBBBB                         B      CMMMD                             BBB                          BBB                  ",
        "X                BBBB                         B                                        BBBMMMMMMMMMMMMMMMMMMMMMD    BBB                  ",
        "X                BBBB                     CMMMB                                        BBB                          BBB     CMMMMMMMMMMMM",
        "MR    BMD        BBBB                         B                              CMMD      BBB                          BBB                  ",
        "X     B          BBBB                         B                                        BBB   CMMMMMMMMMMMMMMMMMMMMMMBBB                  ",
        "X    LB    GJSPY BBBB           CMMMD                                                  BBB                            CMMMD              ",
        "X     B        CMBBBBMD                                                                BBB                                               ",
        "X     B                                                                               JBBB                                              F",
        "LMMMMMMMMMMMMMMMMMMMMMMMMMMR            M     M      LMR      LMR         LMMMMMMMMMMMMMMMMMMMMR       LMMR    LR    MMMMMMMMMMMMMMMMMMMR",
        ]

#For Flying
level_three= [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXBXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "X                                                                           B                                        1                   ",
        "X                                                                           B                                                            ",
        "X                                                                          JB                  1                   BMMMD                 ",
        "X                                                                        CMMB        BB                            B                     ",
        "X                                                                                    BB                            B                     ",
        "X                                                              CMD                   BB       BMMD                 B           CMMMMMMMMM",
        "X                                                                                    BB       B                  BMB                     ",
        "X                                                                                    BB       B                  B                       ",
        "X               CMMD         CMD         CMMMMD       CMD                CMMD        BBB      B                  B                       ",
        "X                                                                                    BB       B         BBMMMMMMMMMMMMMMD                ",
        "X                                                                                    BB       BD        BB                               ",
        "X                                                                                    BB       B         BB                               ",
        "X                                                                                    BB       B         BB                       CMMMMMMM",
        "X                                                                                    BB      BB        CBB       CD                      ",
        "X                                     1                                                       B         BB                               ",
        "X                                                                                             B         BB                               ",
        "XY                                                                                          2 BG                                        F",
        "LMMMMMMMMMM         M      M     M      M     M      LMR      LMR         LMMMMMMMMMMMMMMMMMMMMR       LMMR    LR    MMMM      MMMMMMMMMR",
        ]

#For Traction with Ice Tile Set (Must use levelTileset2)
level_four= [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXBBXXXXXXXXXXXXXXXXXXXXX",
        "X                                                                                                                 BB                     ",
        "X                     J                                                                                    2                             ",
        "X                    RR                                                                                                                  ",
        "X                                                                                                                 BB                     ",
        "X                                                                                                                BBB                     ",
        "X                    RR                                                                                                                  ",
        "X                                                                                                                 HH                     ",
        "X                                          RR                                                         BB         BRR                     ",
        "X             R      1                     HH                 LH                                      BB                                 ",
        "X                                                                               LH                    BB          HH                     ",
        "X                                LLLLLLR       LLLLLLLLH                                  RRRR        BBB         RR                     ",
        "X                                                             HH       LH                     RRRR 2 GBB                                 ",
        "X      BB           LLLL                                      RR                      R           RRRRRR          HH           RR        ",
        "X      BB                                                     HH                                                 RRR                     ",
        "X      BB                                                                                                                                ",
        "X     BBB                                                                                                         HH       R         H  F",
        "RRRRRRRRRLLLLLLLL          RRRRRRRHHHHRRRRRRRRRHRHRHRHRHRHRHRHHRHHRRHHHRHHHRHHHRRRRRHHHHRRRRHHHHRRRRRRRRRRRRRRRRRRRRRRRRRRRRLLLLHRRRRRRRR",
        "MMMMMMMMMMMMMMMMM          MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
        ]

level_five= [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "X                                                                                                          B  B                                B                                                                        ",
        "X            2  J                                                                                                                                                               B                                       ",
        "X              CMR                                                                           B         BB      B       CD                CD   1     M                           B             2                        F",
        "X              B MD                           LR                             B                         BBBBBBBBB                                                                B                              B      CM",
        "X              B            M                                B                                         BB                       CD                  BBBBBBBBBBBB                B                              BB       ",
        "X              B                                                                             CMMMMMMMMMMD                                            B      B                   B   B         CMD           CMMB        ",
        "X    BBMD      B                                                                             BBBBBBBBBBBB                                            B                              B                          B      CM",
        "X    BB        B        CD            1 P                                          CMD       BBBBBBBBBBBB                                            B             BBBB             B                          BB       ",
        "BB   BB      CMB                     BMMR            CMD            CMD                      BBBBBB    BB                                           BB                B             B                          B        ",
        "X    BB        B                     B               B               B                       BBBBBB B  BB              BB                            BB               B        CMMD        B                   B      CM",
        "X   BBBD       BMD                  BB               B               B         B      2             B  BB         B                        M         B              BBB                    B                   BB       ",
        "X    BB                              B               B               B                     CMMMMMMMMM   B                                            B                B                    B                 CMB        ",
        "BB   BB                              B               B   Y           B                                  B             CMD         M                 MBB               BMD                  B                   B      CM",
        "X    BB MMMMMMMMMMMMMMMMMMMMMMD      B           MMMMMMMMMMMMMMM  MMMMMMMMM    B                        B                                                            BB              B     B      B            B        ",
        "X   BBB B      B        B    B      BBB          B       B     B  B           BB                              CMD                                                     B                    B                   B        ",
        "X    BBBBB                           B                                         B                                       M                                              B                                  1             B",
        "XS        1 Y       B                B                B     B         B        B                                                                                     BB                                               BB",
        "MMMMMMMMMMMMM      LR      MMMMMM    MMMMMMMM    MMM  MMMMMMMMMM  MMMMMMMMMMM  M                     LMM       M                  M              M             M      M        LMMR       MMM       MMMM     MMMMMMMMMMM",
        ]

HUD = HeadsUpDisplay("HUDsmaller.png", (255, 255, 255), "HUDgemOne.png", "HUDgemTwo.png", "HUDgemThree.png", "HUDusingOne.png", "HUDusingTwo.png", "HUDusingThree.png")

#Loading tile set for the first level and tutorial. There are 8 elements in this vector
#Grass Tile set
levelTileset1 = []
levelTileset1.append("grassMid.png")
levelTileset1.append("grassLeft.png")
levelTileset1.append("grassRight.png")
levelTileset1.append("grassCliffLeft.png")
levelTileset1.append("grassCliffRight.png")
levelTileset1.append("box.png")
levelTileset1.append("signExit.png")
levelTileset1.append("hill_small.png")

#Ice Tile set
levelTileset2 = []
levelTileset2.append("IceBrick.png")
levelTileset2.append("IceLongBlock.png")
levelTileset2.append("IceSnowBlock.png")
levelTileset2.append("IceLeftIceBerg.png")
levelTileset2.append("IceRightIceBerg.png")
levelTileset2.append("box.png")
levelTileset2.append("signExit.png")
levelTileset2.append("IceSpike.png")

#Loading tile set for all gems. gems will be called from this vector depending on the level.
#1 = ghost, 2 = jump, 3 = , 4 = .
gemsVector = []
gemsVector.append("ghost.png")
gemsVector.append("springboardUp.png")
gemsVector.append("shrinkinggem.png")
gemsVector.append("sprintinggem.png")
gemsVector.append("FlyingGem.png")

#vector for hint images
hintsVector = []
hintsVector.append("arrow.png")

#player vector animation initializations
imagesright = []
imagesleft = []
imagesrightResize = []
imagesleftResize = []

loadImages(STARTSPRITE)

gamestate = 1
nameToGame = False

title = Menu( (255,255,255), "TITLE.png", (30, 50), 0)
menus = []
menus.append(Menu( (255,255,255),"PLAY.png", (150,200), 0))
menus.append(Menu( (255,255,255),"Setting.png", (450,200), 2))
menus.append(Menu( (255,255,255),"Customize.png", (150,350), 3))
menus.append(Menu( (255,255,255),"Instructions.png", (450,350), 4))

pause_men = []
pause_men.append(Menu( (255,255,255),"PLAY.png", (150,150), 0)) 
pause_men.append(Menu( (255,255,255), "Restart.png", (450, 150), 2))
pause_men.append(Menu( (255,255,255),"MainMenu.png", (150,360), 1)) 
pause_men.append(Menu( (255,255,255),"QUIT.png", (450,360), -1)) 

end_men = []
end_men.append((Menu( (255,255,255),"MainMenu.png", (150,350), 1)) )
end_men.append((Menu( (255,255,255),"QUIT.png", (450,460), -1)) )
end_men.append(Menu( (255,255,255), "Restart.png", (450, 350), 2))
end_men.append(Menu( (255,255,255), "Diagnostics.png", (150, 460), 6))

name_men = []
name_men.append((Menu( (255,255,255),"Back.png", (150,360), 2)) )
name_men.append((Menu( (255,255,255),"PLAY.png", (150,360), 0)) )
name_men.append((Menu( (255,255,255),"MainMenu.png", (450,360), 1)) )

set_men = []
set_men.append((Menu( (255,255,255),"ArrowLeft.png", (480,425), -1)) )
set_men.append((Menu( (255,255,255),"ArrowRight.png", (680,425), 1)) )
set_men.append((Menu( (255,255,255),"Back.png", (30,400), 0)) )
set_men.append((Menu( (255,255,255),"Change.png", (275,100), 7)) )

charaterSelectImages = []
charaterSelectImages.append(loading('GreenBiclops.png'))
charaterSelectImages.append(loading('BlueTriclops.png'))
charaterSelectImages.append(loading('PinkCyclops.png'))

soundStatus = []
soundStatus.append(Menu( (255,255,255),"Off.png", (275,250), 1))
soundStatus.append(Menu( (255,255,255),"On.png", (275,250), 0))

sky = pygame.image.load('bg.png').convert()
player_tutorial_sprite_vec = pygame.sprite.Group()
player_tutorial = Character( imagesright, imagesleft, (60, 60), imagesrightResize, imagesleftResize, STARTSPRITE)
player_tutorial_sprite_vec.add(player_tutorial)
pygame.mixer.init()

player_sprite_vec = pygame.sprite.Group()
player = Character( imagesright, imagesleft, (60, 60), imagesrightResize, imagesleftResize, STARTSPRITE)
player_sprite_vec.add(player)

pygame.mixer.init()
level_state = 0
originial_level_state = -1
done = False

main_men = pygame.display.set_mode([800, 600])

levels = []
levels.append(LevelMap(level_one,levelTileset1,gemsVector,hintsVector))
levels.append(LevelMap(level_two,levelTileset1,gemsVector,hintsVector))
levels.append(LevelMap(level_three,levelTileset1,gemsVector,hintsVector))
levels.append(LevelMap(level_four,levelTileset1,gemsVector,hintsVector))

while (not done):
    quit_game = False

    if (gamestate == -1):
        done = True
    elif (gamestate == 0):
        if (player.name == ""):
            gamestate = 7
            nameToGame = True

        if gamestate != 0:
            continue
        while(gamestate == 0): 
            
            while (player.lives > 0 and gamestate == 0):
                if (originial_level_state != level_state):
                    platforms, allSprites, level, scale = levels[level_state].getScroll()
                    View_Map(platforms, allSprites, level, scale)
                    originial_level_state = level_state;

                platforms, gems, allSprites, base_platforms, level, goals, EasyHints, HardHints = levels[level_state].getValues()
                gamestate, level_state = Level_Screens(platforms, gems, allSprites, base_platforms, player, level, sky, player_sprite_vec, goals, EasyHints, HardHints, level_state)
                
                if (level_state > len(levels) - 1):
                    gamestate = 5
                    break

                level, levelTileset, gemsVector, hintsVector = levels[level_state].getRestart()

                if (originial_level_state != level_state):
                    levels = levelRestart(levels, level_state-1, level, levelTileset, gemsVector, hintsVector)
                else:
                    levels = levelRestart(levels, level_state, level, levelTileset, gemsVector, hintsVector)

                player.reset([0,0], level_state, originial_level_state)
                 
            if (player.lives == 0): 
                gamestate = 5
        #Reset level state 
        level_state = 1
    elif (gamestate == 1):
        main_men.fill([208,244,247]) 
        main_men.blit(title.image, title)

        for menu_item in menus:
            main_men.blit(menu_item.image, menu_item)

        ev = pygame.event.get()

        for event in ev:
            if (event.type == pygame.MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()
                for menu_item in menus:
                    if menu_item.rect.collidepoint(pos):
                        gamestate = menu_item.type
                        if gamestate == 0:
                            player.resetStats()
            elif (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gamestate = -1
        pygame.display.update()

    elif (gamestate == 2):
        set_screen = pygame.display.set_mode([800,600])
        set_screen.fill([208,244,247])

        if player.name == "":
            dispName = "CLICK CHANGE"
        else:
            dispName = player.name

        font = pygame.font.SysFont("Courier New", 30)
        prompt = font.render("Current Name:", 1, [0, 0, 255])
        currName = font.render(dispName, 1, [0, 0, 255])

        soundFont = pygame.font.SysFont("Courier New", 50)
        soundName = soundFont.render("Sound: ", 1, [0,0,255])


        set_screen.blit(prompt, [20, 100]) 
        set_screen.blit (currName,[22,150])
        set_screen.blit(soundName, [30, 275])

        set_screen.blit(soundStatus[player.sound].image, soundStatus[player.sound])

        for men in set_men:
            set_screen.blit(men.image, men)

        set_screen.blit(charaterSelectImages[player.currrentSprite - 1], [518, 125])

        ev = pygame.event.get()
        for event in ev:
            if (event.type == pygame.MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()
                for men in set_men:
                    if men.rect.collidepoint(pos):
                        action = men.type
                        pastChar = player.currrentSprite
                        if action == -1:
                            player.currrentSprite += action
                            if player.currrentSprite <= 0:
                                player.currrentSprite = len(charaterSelectImages)
                        elif action == 1:
                            player.currrentSprite += action
                            if player.currrentSprite > len(charaterSelectImages):
                                player.currrentSprite = 1
                        elif action == 0:
                            gamestate = 1
                            player.changeSprites(player.currrentSprite, [60,60])
                            player_tutorial.changeSprites(player.currrentSprite,[60,60])
                        elif action == 7:
                            gamestate = 7
                            nameToGame = False
                if soundStatus[player.sound].rect.collidepoint(pos):
                    player.sound = soundStatus[player.sound].type
                            
            elif (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gamestate = -1

        pygame.display.update()
    elif(gamestate == 3):
        #Change this to Level Selector page
        print("Level Selector Pressed!")
        gamestate = 1
    elif (gamestate == 4):
        #Change this to Instructions page
        platforms_tutorial, gems_tutorial, allSprites_tutorial, base_platforms_tutorial, goals_tutorial, allSprites_scroll_tu, level_scroll_tu, scaleFactor, EasyHints_tutorial, HardHints_tutorial = Level_Vector_Creations(level_tutorial,levelTileset1,gemsVector,hintsVector)
        gamestate, x = Level_Screens(platforms_tutorial, gems_tutorial, allSprites_tutorial, base_platforms_tutorial, player_tutorial, level_tutorial, sky, player_tutorial_sprite_vec, goals_tutorial, EasyHints_tutorial, HardHints_tutorial, 0)
        gamestate = 1
    elif (gamestate == 5):
        #End of game score, etc
        end_screen = pygame.display.set_mode([800, 600])
        
        score = player.getTime() * 10
        
        end_screen.fill([208,244,247])
        
        if (player.complete): 
            display_box(end_screen, "Great Job! Level Completed!", 150, 210, 0)
            display_box(end_screen, "Score: %d", 325, 270, score)
            #Diagnostics(score)
        else: 
            display_box(end_screen, "Better Luck Next Time!", 150, 250, 0)
            
        
        for men in end_men:
            end_screen.blit(men.image, men)
               
        pygame.display.update()

        ev = pygame.event.get()
        for event in ev:
            if (event.type == pygame.MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()
                for men in end_men:
                    if men.rect.collidepoint(pos):
                        gamestate = men.type
                        if (gamestate == 2):
                            gamestate = 0
                            player.resetStats()
                            player.reset([0,0], 0, 0)
                        elif (gamestate == 1):
                            player.resetStats()
            elif (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gamestate = -1
    elif (gamestate == 6):
        diag_screen = pygame.display.set_mode([800, 600])
        diag_screen.fill([208,244,247])
        Diagnostics(score, diag_screen)
        pygame.display.update()
        ev = pygame.event.get()
        for event in ev:
            if (event.type == QUIT):
                gamestate = -1
            elif (event.type == KEYDOWN and event.key == K_ESCAPE):
                gamestate = 5
    elif (gamestate == 7):
        name_screen = pygame.display.set_mode([800, 600])
        userName = eztext.Input(maxlength= 13, color=(0,0,255), prompt='')
        userName.value = player.name

        while (gamestate == 7):
            name_screen.fill([208,244,247])

            font = pygame.font.SysFont("Courier New", 40)

            prompt = font.render("Enter Your Name:", 1, [0, 0, 255])
            screen.blit(prompt, (View_Height/3, View_Width/5)) 

            userName.set_pos(View_Height/3 , View_Width/5 + 41)
            userName.set_font(font)
            userName.update(ev)
            userName.draw(name_screen)

            name_screen.blit(name_men[nameToGame].image, name_men[nameToGame])
            name_screen.blit(name_men[2].image, name_men[2])

            ev = pygame.event.get()
            for event in ev:
                if (event.type == pygame.MOUSEBUTTONDOWN):
                    pos = pygame.mouse.get_pos()
                    if name_men[nameToGame].rect.collidepoint(pos):
                        gamestate = name_men[nameToGame].type
                        player.name = userName.value
                        if (player.name == "" and nameToGame):
                            gamestate = 7
                    elif name_men[2].rect.collidepoint(pos):
                        gamestate = name_men[2].type
                        if not(nameToGame):
                                player.name = userName.value
                if (event.type == KEYDOWN and event.key == K_RETURN):
                    player.name = userName.value
                    if nameToGame:
                        gamestate = 0
                    else:
                        gamestate = 2
                elif (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    gamestate = -1

            pygame.display.update()