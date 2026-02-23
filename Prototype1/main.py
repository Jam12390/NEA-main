import pygame
import sys
from EntitySubclasses import Player, Enemy
import Entity
from OtherClasses import WallObj, Item, ItemUIWindow
from button import Button
from dictionaries import *

import mapLoading
from transfer import precompile, pathing

screenWidth = 1000
screenHeight = screenWidth*0.8 #keep the ratio for w-h at 1:0.8 - could change later

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()
paused = False

FPS = 60

#player = pygame.sprite.GroupSingle()

mapName = "testMapMove8"
mapPath = f"Prototype1/transfer/Maps/{mapName}.csv"

TILESIZE = 76
PLAYERSIZE = pygame.Vector2(50, 50)

mapResponse = mapLoading.loadMapData(
    mapName=mapName,
    STARTKEY=5,
    ITEMKEY=6,
    ENEMYKEY=2,
    tileSize=TILESIZE,
    baseScreenDimensions=(screenWidth, screenHeight),
    playerHeight=25
)
pathingOffset = pygame.Vector2(screenWidth/2, screenHeight/2)

enemyData = {
    "jumpForce": 130,
    "maxSpeed": (50, 50)
}

loadedMap = precompile.loadMap(fileName=mapPath)

precompiledGraph = precompile.precompileGraph(
    nodeMap=loadedMap,
    nodeSep=15,
    gravity=9.81 * 15,
    enemyData=enemyData,
    origin=(16, 0)
)

#for x in precompiledGraph["nodes"]:
#    loadedMap[x[0]][x[1]] = "x"
#for row in loadedMap:
#    print(row)

walls = mapResponse[0]

player = Player(
    FPS=FPS,
    jumpForce=150, #pixels/second
    maxHP=100,
    defense=5,
    speed=1,
    pAttackCooldown=0.75,
    pSize=PLAYERSIZE,
    spritePath="Sprites/DefaultSprite.png", #path to the player's sprite goes here
    pTag="player",
    pMass=3,
    startingPosition=mapResponse[2],#pygame.math.Vector2(screenWidth/2, screenHeight/2),
    startingVelocity=pygame.math.Vector2(0, 0),
    pVelocityCap=pygame.math.Vector2(100, 100),
    startingWeaponID=0
)
player.absoluteCoordinate.x -= screenWidth/1.25

#walls = pygame.sprite.Group()
#walls.add(
#    WallObj(
#        size=pygame.Vector2(500, 100),
#        position=pygame.Vector2(screenWidth/2, (screenHeight/2)+200), #position the floor beneath the player
#        spritePath="Sprites/DefaultSprite.png", #placeholder for actual image path in development
#        pTag="floor",
#        frictionCoef=1
#    )
#)

#debug = pygame.sprite.Group()
#debug = Enemy(
#    FPS=FPS,
#    jumpForce=enemyData["jumpForce"],
#    maxHP=10,
#    defense=10,
#    speed=10,
#    pAttackCooldown=10,
#    spritePath="Sprites/DefaultSprite.png",
#    pTag="",
#    pMass=5,
#    startingPosition=pygame.Vector2(mapResponse[3][0]),#(800, 400),
#    pVelocityCap=pygame.Vector2(enemyData["maxSpeed"]),
#    startingVelocity=pygame.Vector2(50, 0),
#    pSize=pygame.Vector2(50, 25),
#    pIgnoreYFriction=True
#)
debug = pygame.sprite.Group()
for enemyPos in mapResponse[4]:
    debug.add(
        Enemy(
        FPS=FPS,
        jumpForce=enemyData["jumpForce"],
        maxHP=10,
        defense=10,
        speed=1,
        pAttackCooldown=10,
        spritePath="Sprites/DefaultSprite.png",
        pTag="",
        pMass=5,
        startingPosition=pygame.Vector2(enemyPos),#(800, 400),
        pVelocityCap=pygame.Vector2(enemyData["maxSpeed"]),
        startingVelocity=pygame.Vector2(50, 0),
        pSize=pygame.Vector2(50, 25),
        pIgnoreYFriction=True
)
    )
#debug = Entity.Entity(
#    FPS=FPS,
#    jumpForce=enemyData["jumpForce"],
#    maxHP=10,
#    defense=10,
#    speed=10,
#    pAttackCooldown=10,
#    spritePath="Sprites/DefaultSprite.png",
#    pTag="",
#    pMass=5,
#    startingPosition=pygame.Vector2(mapResponse[3][0]),#(800, 400),
#    pVelocityCap=pygame.Vector2(enemyData["maxSpeed"]),
#    startingVelocity=pygame.Vector2(50, 0),
#    pSize=pygame.Vector2(50, 25),
#    pIgnoreYFriction=True
#)

for x in debug:
    x.absoluteCoordinate.y -= mapResponse[3].y
    x.absoluteCoordinate.x -= screenWidth/2

items = mapResponse[1]
#for x in items:
#    x.rect.centerx += screenWidth/2
#items.add(
#    Item(
#        pID=0,
#        startingPosition=pygame.Vector2(screenWidth/2 + 150, (screenHeight/2)+175),
#        UIWindow=ItemUIWindow(
#            itemID=0,
#            replaces=allItems[0]["replaces"],
#            pos=(screenWidth/2 + 150, (screenHeight/2) + 50),
#            size=(400, 150)
#        ),
#    )
#)
#items.add(
#    Item(
#        pID=1,
#        startingPosition=pygame.Vector2(screenWidth/2 - 150, (screenHeight/2)+175),
#        UIWindow=ItemUIWindow(
#            itemID=1,
#            replaces=allItems[1]["replaces"],
#            pos=(screenWidth/2 - 150, (screenHeight/2) + 50),
#            size=(400, 150)
#        )
#    )
#)

mainLoopRunning = True

inventoryOpen = False   

previousBlockedMotion = ()

def mainloop():
    global inventoryOpen
    global paused
    pygame.display.set_caption("Main loop")

    while mainLoopRunning:
        clock.tick(FPS)

        events = pygame.event.get()

        for event in events:
            '''
            KEYDOWN is for events which should only happen once if the key is pressed.
            i.e. I is likely to be held for 2-3 frames. If KEYDOWN wasn't used, the inventory screen would open and close rapidly.
            '''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    for item in items:
                        if item.UIWindow.shown: #if the UI is shown, the item is in pickup range
                            item.pickup(target=player)
                if event.key == pygame.K_i:
                    inventoryOpen = True
                    paused = True
                    inventory()
                if event.key == pygame.K_ESCAPE and not inventoryOpen:
                    paused = True
                    pauseMenu()
                if event.key == pygame.K_SPACE and ("l" in player.blockedMotion or "r" in player.blockedMotion) and not player.isGrounded:
                    player.wallJump()
                
                if event.key == pygame.K_p:
                    for x in items:
                        print(x.UIWindow.rect.center)
                if event.key == pygame.K_o:
                    pass
                #if event.key == pygame.K_r:
                #    debug.paused = not debug.paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not player.weapon.currentlyAttacking:
                    player.weapon.attack(parent=player)

            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()

        if not paused:
            #cycle through all potential movement inputs
            if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and player.isGrounded and not "u" in player.blockedMotion:
                player.jump()
                player.previousGroundedYCoord = tuple([player.absoluteCoordinate.y])[0]

            if keys[pygame.K_a] and not player.containsForce(axis="x", ref="UserInputLeft") and not "l" in player.blockedMotion and not player.crouched:
                player.addForce(axis="x", direction="l", ref="UserInputLeft", magnitude=2500)
            elif not keys[pygame.K_a]:
                player.removeForce(axis="x", ref="UserInputLeft")

            if keys[pygame.K_d] and not player.containsForce(axis="x", ref="UserInputRight") and not "r" in player.blockedMotion and not player.crouched:
                player.addForce(axis="x", direction="r", ref="UserInputRight", magnitude=2500)
            elif not keys[pygame.K_d]:
                player.removeForce(axis="x", ref="UserInputRight")

            if keys[pygame.K_s]:
                if not player.containsForce(axis="y", ref="UserInputDown") and not player.isGrounded:
                    player.fastFalling = True #start fast falling
                    player.addForce(axis="y", direction="d", ref="UserInputDown", magnitude=2500)
                    player.modifySpeedCap(axis="y", magnitude=15)
                elif player.isGrounded:
                    if player.fastFalling: #are we fast falling
                        player.fastFalling = False #stop fast falling
                        player.modifySpeedCap(axis="y", magnitude=-15) #change speed cap back
                    player.removeForce(axis="y", ref="UserInputDown")
                    #if not player.crouched: #if we're not crouched
                    #    player.crouch() #crouch
                #elif not player.isGrounded:
                #    if player.crouched: #if we're crouched
                #        player.uncrouch() #uncrouch
            else: #not holding S
                player.removeForce(axis="y", ref="UserInputDown") #remove downwards force
                #if player.crouched:
                #    player.uncrouch()
                if player.fastFalling:
                    player.modifySpeedCap(axis="y", magnitude=-15) #stop fast falling
                    player.fastFalling = False

            if keys[pygame.K_q]: #debug code, resets the player position to center
                print(player.currentNode)
                print(player.absoluteCoordinate)

            screen.fill((0, 0, 0)) #rgb value for black background

            #update all objects (this includes collision detection)
            playerMoved = player.update(collidableObjects=[walls, items])
            if -(player._velocityCap.x / 50) < playerMoved.x and playerMoved.x < player._velocityCap.x / 20:
                playerMoved.x = 0
            if -0.25 < playerMoved.y and playerMoved.y < 0.25:
                playerMoved.y = 0
            player.absoluteCoordinate += playerMoved
            #playerMoved //= 1
            #print(player.absoluteCoordinate)
            #playerMoved = round(playerMoved)

            #print(player._velocity)
            #print(player._xForces) 
            #print(player._yForces)
            #print(player.blockedMotion)
            #print(player.isGrounded)
            #print(                                                                                                                                                                                                                             player._velocity)
            #print(player.rect.center)

            walls.update()
            debug.update(
                collidableObjects=[walls],
                precompiledData=precompiledGraph,
                nodeMap=loadedMap,
                nodeSep=30,
                pathingTo=player.currentNode,
                playerRect=player.rect
            )
            #if "l" in player.blockedMotion and not "l" in previousBlockedMotion:
            #    playerMoved.x = -1
            #elif "r" in player.blockedMotion and not "r" in previousBlockedMotion:
            #    playerMoved.x = 1
            #if "u" in player.blockedMotion and not "u" in previousBlockedMotion:
            #    playerMoved.y = 1
            #elif "d" in player.blockedMotion and not "d" in previousBlockedMotion:
            #    playerMoved.y = -1
            #previousBlockedMotion = tuple(player.blockedMotion)
            #if "l" in player.blockedMotion or "r" in player.blockedMotion:
            #    playerMoved.x = 0
            #if "u" in player.blockedMotion or "d" in player.blockedMotion:
            #    playerMoved.y = 0
            if "u" in player.blockedMotion:
                playerMoved.y = max(0, playerMoved.y)
            if "d" in player.blockedMotion:
                playerMoved.y = min(0, playerMoved.y)
            if "l" in player.blockedMotion:
                playerMoved.x = max(0, playerMoved.x)
            if "r" in player.blockedMotion:
                playerMoved.x = min(0, playerMoved.x)
            
            #print(playerMoved)

            for wall in walls:
                wall.rect.centerx -= playerMoved.x
                wall.rect.centery -= playerMoved.y
            for item in items:
                item.rect.centerx -= playerMoved.x
                item.rect.centery -= playerMoved.y
            for enemy in debug:
                enemy.rect.centerx -= playerMoved.x
                enemy.rect.centery -= playerMoved.y
                enemy.sightRect.center = enemy.rect.center
                #enemy.currentNode = (
                #    int((enemy.absoluteCoordinate.y) // 75), #(y, x)
                #    int(((enemy.absoluteCoordinate.x) // 75))
                #)
            
            #debug.rect.centerx -= playerMoved.x
            #debug.rect.centery -= playerMoved.y
            #debug.sightRect.center = debug.rect.center
            
            
                #path = pathing.main(
                #        start=(16, 31),
                #        end=player.currentNode,
                #        precompiledData=precompiledGraph,
                #        nodeMap=loadedMap,
                #        nodeSep=10,
                #        jumpForce=enemyData["jumpForce"],
                #        maxXSpeed=enemyData["maxSpeed"][1],
                #        gravity=9.81 * 15
                #    )
            items.update()
            redraw()
            pygame.display.flip()

def redraw(): #it's important to note that redraw() DOES NOT update() any of the objects it's drawing
    #screen.blit(player.image, player.rect)
    #offsetRect = player.rect.copy()
    #offsetpos = pygame.math.Vector2()
    #offsetpos.x = offsetRect.centerx + screenWidth//2

    #######REVERT TAG
    player.rect.center = (screenWidth/2, screenHeight/2)
    player.currentNode = (
        (player.absoluteCoordinate.y) // 75, #(y, x)
        ((player.absoluteCoordinate.x) // 75) + 1
    )
    #print(player.currentNode)
    #print(player.absoluteCoordinate)
    screen.blit(player.image, player.rect)

    #for sprite in walls:
    #    #if sprite.absoluteCoordinate.x in range(-1 - TILESIZE, TILESIZE + 1):
    #    screen.blit(sprite.image, sprite.absoluteCoordinate)
    #walls.draw(screen)
    #
    #items.draw(screen)
    ########END


    #### ALEX'S CODE
    #offsetpos = pygame.math.Vector2()
    #offsetpos.x = player.rect.centerx - screenWidth//2
    #offsetpos.y = player.rect.centery - screenHeight//2
#
    #offsetRect = player.rect.copy()
    #offsetRect.center -= offsetpos
    #screen.blit(player.image,offsetRect)
#
    #for wall in walls:
    #    offsetRect = wall.rect.copy()
    #    offsetRect.center -= offsetpos
    #    screen.blit(wall.image,offsetRect)
    #
    #for item in items:
    #    if item.UIWindow.shown:
    #        offsetRect = item.UIWindow.rect.copy()
    #        offsetRect.center -= offsetpos
    #        item.UIWindow.update()
    #        screen.blit(item.UIWindow.surface, offsetRect)
    #    offsetRect = item.rect.copy()
    #    offsetRect.center -= offsetpos
    #    screen.blit(item.image,offsetRect)
    ####//END

    if player.weapon.currentlyAttacking:
        screen.blit(player.weapon.image, player.weapon.rect)

    for sprite in walls:
        screen.blit(sprite.image, sprite.rect)
    
    #screen.blit(debug.image, debug.rect)
    #debug.currentNode = (
    #    int((debug.absoluteCoordinate.y) // 75), #(y, x)
    #    int(((debug.absoluteCoordinate.x) // 75))
    #)
        #print(sprite.currentNode)
    walls.draw(screen)
    debug.draw(screen)
    
    for x in items:
        screen.blit(x.image, x.rect)
        if x.UIWindow.shown:
            screen.blit(x.UIWindow.surface, x.UIWindow.rect)
    #screen.blit(debug.image, debug.rect)
    #pygame.draw.rect(screen, [255, 255, 255], debug.sightRect)
    #print(debug[0].rect.center)

def inventory():
    global inventoryOpen
    global paused
    font = pygame.font.SysFont("Calibri", 20)
    title = font.render("Inventory", False, (255, 255, 255))
    itemHeaders = [
        [
            font.render(f"{allItems[ID]["name"]} - ", False, (255, 255, 255)),
            font.render(f"Effects: {allItems[ID]["effects"]}", False, (255, 255, 255))
        ]
        for ID in player.inventory.keys() #makes separate lists for each item's name and headers in inventory
    ]
    itemDescriptions = [font.render(item[1], False, (255, 255, 255)) for item in player.inventory.values()]
    while inventoryOpen:
        startingPos = [10, 50]
        #clock.tick(FPS) #note for future prototypes: ticking the clock twice imitates slow motion (at the cost of FPS ofc)
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))
        
        background = pygame.Surface((screenWidth-100, screenHeight-100))
        background.fill((0, 0, 125))

        background.blit(title, (10,10))
        for itemIndex in range(0, len(itemHeaders)):
            background.blit(itemHeaders[itemIndex][0], (startingPos[0], startingPos[1])) #itemHeaders[itemIndex] = [itemName, itemEffects]
            background.blit(itemHeaders[itemIndex][1], (startingPos[0] + pygame.Surface.get_rect(itemHeaders[itemIndex][0]).right, startingPos[1]))
            startingPos[1] += 25
            background.blit(itemDescriptions[itemIndex], (startingPos[0], startingPos[1])) #itemDescriptions
            startingPos[1] += 50

        screen.blit(background, (25, 50))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    inventoryOpen = False
                    paused = False
        pygame.display.flip()

def pauseMenu():
    global paused
    pauseText = pygame.font.SysFont("Calibri", 90).render("Paused", False, (255, 255, 255))

    buttonText = ["Resume", "Abandon Run", "Options", "Exit to Desktop"]
    renderedText = []
    functions = [unpause, abandonRun, openOptions, quit]

    startingPos = pygame.Vector2(125, screenHeight - (75*4) + 25)
    for index in range(0, len(buttonText)):
        renderedText.append(Button(
            position=startingPos,
            text=buttonText[index],
            func=functions[index],
            textSize=25,
            size=pygame.Vector2(200, 50)
        ))
        startingPos.y += renderedText[0].size.y + 25
    
    while paused:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))

        screen.blit(pauseText, (25, 25))

        mousePos = pygame.mouse.get_pos()

        for button in renderedText:
            button.update(mousePos)
            screen.blit(button.surface, button.rect)
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                unpause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in renderedText:
                    if button.hoveredOver:
                        button.onClick()
        pygame.display.flip()

def unpause():
    global paused
    paused = False

def abandonRun():
    global paused
    paused = False
    player.rect.center = (round(screenWidth/2), round(screenHeight/2))
    player._velocity = pygame.Vector2(0,0)

def openOptions():
    pass

def quit():
    pygame.quit()
    sys.exit()

mainloop()