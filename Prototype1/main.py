import pygame
import sys
from EntitySubclasses import Player, Enemy
import Entity
from OtherClasses import WallObj, Item, ItemUIWindow
import button as Button
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

invalidKeys = [5, 6, 2, -1]

loadedMap = precompile.loadMap(fileName=mapPath, invalidKeys=invalidKeys)

precompiledGraph = precompile.precompileGraph(
    nodeMap=loadedMap,
    nodeSep=15,
    gravity=9.81 * 15,
    enemyData=enemyData,
    origin=(16, 0)
)


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
))

for x in debug:
    x.absoluteCoordinate.y -= mapResponse[3].y
    x.absoluteCoordinate.x -= screenWidth/2

items = mapResponse[1]

mainLoopRunning = True

inventoryOpen = False

previousBlockedMotion = ()

def mainloop():
    global inventoryOpen
    global paused
    pygame.display.set_caption("Main loop")

    if inMainmenu:
        mainmenu()

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
            else: #not holding S
                player.removeForce(axis="y", ref="UserInputDown") #remove downwards force
                if player.fastFalling:
                    player.modifySpeedCap(axis="y", magnitude=-15) #stop fast falling
                    player.fastFalling = False

            screen.fill((0, 0, 0)) #rgb value for black background

            #update all objects (this includes collision detection)
            playerMoved = player.update(collidableObjects=[walls, items])
            if -(player._velocityCap.x / 50) < playerMoved.x and playerMoved.x < player._velocityCap.x / 20:
                playerMoved.x = 0
            if -0.25 < playerMoved.y and playerMoved.y < 0.25:
                playerMoved.y = 0
            player.absoluteCoordinate += playerMoved
            

            walls.update()
            debug.update(
                collidableObjects=[walls],
                precompiledData=precompiledGraph,
                nodeMap=loadedMap,
                nodeSep=30,
                pathingTo=player.currentNode,
                playerRect=player.rect
            )
            
            
            if "u" in player.blockedMotion:
                playerMoved.y = max(0, playerMoved.y)
            if "d" in player.blockedMotion:
                playerMoved.y = min(0, playerMoved.y)
            if "l" in player.blockedMotion:
                playerMoved.x = max(0, playerMoved.x)
            if "r" in player.blockedMotion:
                playerMoved.x = min(0, playerMoved.x)

            for wall in walls:
                wall.rect.centerx -= pathing.clamp(mini=-(player._velocityCap.x / 50), inp=playerMoved.x, maxi=player._velocityCap.x/20, invert=True)
                wall.rect.centery -= pathing.clamp(inp=playerMoved.y, mini=-0.25, maxi=0.25, invert=True)
            for item in items:
                item.rect.centerx -= pathing.clamp(mini=-(player._velocityCap.x / 50), inp=playerMoved.x, maxi=player._velocityCap.x/20, invert=True)
                item.rect.centery -= pathing.clamp(inp=playerMoved.y, mini=-0.25, maxi=0.25, invert=True)
            for enemy in debug:
                enemy.rect.centerx -= playerMoved.x
                enemy.rect.centery -= playerMoved.y
                enemy.sightRect.center = enemy.rect.center


            items.update()
            redraw()
            pygame.display.flip()

def redraw(): #it's important to note that redraw() DOES NOT update() any of the objects it's drawing
    player.rect.center = (screenWidth/2, screenHeight/2)
    player.currentNode = (
        (player.absoluteCoordinate.y) // 75, #(y, x)
        ((player.absoluteCoordinate.x) // 75) + 1
    )
    screen.blit(player.image, player.rect)

    if player.weapon.currentlyAttacking:
        screen.blit(player.weapon.image, player.weapon.rect)

    for sprite in walls:
        screen.blit(sprite.image, sprite.rect)
        #print(sprite.currentNode)
    walls.draw(screen)
    debug.draw(screen)
    
    for x in items:
        screen.blit(x.image, x.rect)
        if x.UIWindow.shown:
            screen.blit(x.UIWindow.surface, x.UIWindow.rect)

def nullFunc():
    pass

def inventory():
    global inventoryOpen
    global paused

    textColour = (255, 255, 255) #white
    backgroundColour = (125, 125, 125)
    itemHoverColour = (100, 100, 100)

    titleFont = pygame.font.SysFont("Calibri", 45)
    title = titleFont.render("Inventory", False, textColour)

    itemTitleFont = pygame.font.SysFont("Calibri", 30)
    itemTitle = itemTitleFont.render("Items", False, textColour)

    itemFont = pygame.font.SysFont("Calibri", 20)
    #itemHeaders = [
    #    [
    #        itemFont.render(f"- {allItems[ID]["name"]}", False, textColour),
    #        itemFont.render(f"Effects: {allItems[ID]["effects"]}", False, textColour)
    #    ]
    #    for ID in player.inventory.keys() #makes separate lists for each item's name and headers in inventory
    #]
    #itemDescriptions = [itemFont.render(f"{item[1]}", False, textColour) for item in player.inventory.values()]

    #itemHeaders = [itemFont.render(f"{player.inventory[ID][2]}x  - {allItems[ID]["name"]}", False, textColour) for ID in player.inventory.keys()]
    startingPos = [(screenWidth - 100) // 3 + 75, 175]

    itemDescriptions = {
        ID: [
            "Description:",
            allItems[ID]["description"],
            f"Replaces: {allItems[ID]["replaces"]}",
            f"Effects: {allItems[ID]["effects"]}"
        ]
        for ID in player.inventory.keys()
    }

    itemHeaders = [
        Button.TextButton(
            position=pygame.Vector2(startingPos[0], startingPos[1]),
            text=f"{player.inventory[ID][2]}x  - {allItems[ID]["name"]}",
            func=nullFunc,
            textColour=pygame.Color(textColour),
            buttonColour=pygame.Color(backgroundColour),
            hoverColour=pygame.Color(itemHoverColour),
            textSize=20,
            hoverOffset=pygame.Vector2(50, 50),
            descriptionText=itemDescriptions[ID],
            absoluteDescriptionPosition=pygame.Vector2(
                (screenWidth - 100) // 6 * 5,
                75
            )
        )
        for ID in player.inventory.keys()
    ]

    fontSize = 20
    lineSize = fontSize + 15

    while inventoryOpen:
        #clock.tick(FPS) #note for future prototypes: ticking the clock twice imitates slow motion (at the cost of FPS ofc)
        redraw()
        mousePos = pygame.mouse.get_pos()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))
        
        background = pygame.Surface((screenWidth-100, screenHeight-100))
        #background.fill((125, 125, 125, 255))

        #Base Background
        pygame.draw.rect(surface=background, color=backgroundColour, rect=pygame.Surface.get_rect(background), border_radius=10)

        #Title
        background.blit(title, (25, 25))

        #Top Divider
        pygame.draw.line(surface=background, color=textColour, start_pos=(0, 90), end_pos=((screenWidth - 100), 90))

        #Weapon - Item Divider
        pygame.draw.line(surface=background, color=textColour, start_pos=((screenWidth - 100) // 3, 90), end_pos=((screenWidth - 100) // 3, screenHeight - 100))

        #Item Title
        background.blit(itemTitle, ((screenWidth - 100) // 3 + 10, 105))
        pygame.draw.line(surface=background, color=textColour, start_pos=((screenWidth - 100) // 3 + 10, 130), end_pos=((screenWidth - 100) // 3 + 80, 130))

        #Item - Description Divider
        pygame.draw.line(surface=background, color=textColour, start_pos=((screenWidth - 100) // 3 * 2, 90), end_pos=((screenWidth - 100) // 3 * 2, screenHeight - 100))

        #Weapon Image
        scaledRect = pygame.transform.smoothscale(pygame.image.load(allWeapons[player.weapon.ID]["imgPath"]), (player.weapon.rect.width * 20, player.weapon.rect.height * 20))
        weaponRect = pygame.Surface.get_rect(scaledRect)
        weaponRect.center = (
            (screenWidth - 100) // 6,
            int(screenHeight - 100) // 2 + 50
        )
        weaponRect.center += allWeapons[player.weapon.ID]["inventoryOffset"]
        #background.blit(scaledRect, weaponRect)

        weapon = Button.ImageButton(
            position=pygame.Vector2(
            (screenWidth - 100) // 6,
            int(screenHeight - 100) // 2
            ),
            #position=pygame.Vector2(0, 115),
            size=pygame.Vector2(player.weapon.rect.width * 7.5, player.weapon.rect.height * 20),
            imgPath=allWeapons[player.weapon.ID]["imgPath"],
            text=Button.wrapText(plainText=allWeapons[player.weapon.ID]["description"], wordsPerLine=5),
            #textColour=pygame.Color(textColour),
            buttonColour=pygame.Color(backgroundColour),
            hoverColour=pygame.Color(itemHoverColour),
            func=nullFunc,
            absoluteDescriptionPosition=pygame.Vector2(
                (screenWidth - 100) // 6 * 5,
                75
            )
        )
        weapon.update(mousePos)
        background.blit(weapon.surface, weapon.rect)
        if weapon.hoveredOver:
            background.blit(weapon.description.background, weapon.description.rect)

        startingPos = [(screenWidth - 100) // 3 + 100, 150]
        for itemIndex in range(0, len(itemHeaders)):
            #background.blit(itemHeaders[itemIndex], (startingPos[0], startingPos[1]))
            itemHeaders[itemIndex].update(mousePos)
            background.blit(itemHeaders[itemIndex].surface, itemHeaders[itemIndex].rect)
            if itemHeaders[itemIndex].hoveredOver:
                background.blit(itemHeaders[itemIndex].description.background, itemHeaders[itemIndex].description.rect)
            #startingPos[1] += 50

        screen.blit(background, (50, 50))

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

    startingPos = pygame.Vector2(125, screenHeight - (75*len(buttonText)) + 25)
    for index in range(0, len(buttonText)):
        renderedText.append(Button.TextButton(
            position=startingPos,
            text=buttonText[index],
            func=functions[index],
            textSize=25,
        ))
        startingPos.y += renderedText[0].rect.height + 25
    
    for button in renderedText:
        button.rect.left = 25
    
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

inMainmenu = False

inCharacterSelect = False

def mainmenu():
    global inMainmenu
    global inCharacterSelect
    titleText = pygame.font.SysFont("Calibri", 90).render("'Blended'", True, (255, 255, 255))

    buttonText = ["Play", "Options", "Quit"]
    functions = [play, openOptions, quit]

    renderedText = []

    startingPos = pygame.Vector2(125, screenHeight - (75*len(buttonText)) + 25)
    for index in range(0, len(buttonText)):
        renderedText.append(Button.TextButton(
            position=startingPos,
            text=buttonText[index],
            func=functions[index],
            textSize=25,
            size=pygame.Vector2(200, 50)
        ))
        startingPos.y += renderedText[0].size.y + 25

    while inMainmenu:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))

        screen.blit(titleText, (25, 25))

        mousePos = pygame.mouse.get_pos()

        for button in renderedText:
            button.update(mousePos)
            screen.blit(button.surface, button.rect)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in renderedText:
                    if button.hoveredOver:
                        button.onClick()

        pygame.display.flip()
    characterSelect()

def characterSelect():
    global player
    titleText = pygame.font.SysFont("Calibri", 90).render("Character Select", True, (255, 255, 255))
    subtitleText = pygame.font.SysFont("Calibri", 30).render("Please choose a character:", True, (255, 255, 255))

    characters = []

    startingPos = pygame.Vector2(100, 250)

    for ID in allCharacters.keys():
        characters.append(
            Button.ImageButton(
                position=startingPos,
                imgPath=allCharacters[ID]["imgPath"],
                func=setPlayer,
                text=[
                    f"Name: {allCharacters[ID]["name"]}",
                    f"HP: {allCharacters[ID]["hp"]}",
                    f"Def: {allCharacters[ID]["defense"]}",
                    f"Speed: {allCharacters[ID]["speed"]}",
                    f"Jumpforce: {allCharacters[ID]["jumpForce"]}",
                    f"Attack Cooldown: {allCharacters[ID]["attackCooldown"]}",
                    f"Size: {allCharacters[ID]["size"]}"
                ],
                size=pygame.Vector2(100, 100),
                descriptionOffset=pygame.Vector2(250, 0)
            )
        )
        startingPos.y += 150

    while inCharacterSelect:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0,0,0))
        dim.set_alpha(200)
        screen.blit(dim, (0,0))

        screen.blit(titleText, (20, 25))
        screen.blit(subtitleText, (25, 110))

        mousePos = pygame.mouse.get_pos()

        for character in characters:
            character.update(mousePos)
            screen.blit(character.surface, character.rect)
            if character.hoveredOver:
                screen.blit(character.description.background, character.description.rect)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for character in characters:
                    if character.hoveredOver:
                        character.onClick(character.ID)
        #print("a")
        pygame.display.flip()

def setPlayer(ID):
    global player
    global inCharacterSelect
    player = Player(
        FPS=FPS,
        jumpForce=allCharacters[ID]["jumpForce"], #pixels/second
        maxHP=allCharacters[ID]["hp"],
        defense=allCharacters[ID]["defense"],
        speed=allCharacters[ID]["speed"],
        pAttackCooldown=allCharacters[ID]["attackCooldown"],
        pSize=allCharacters[ID]["size"],
        spritePath=allCharacters[ID]["imgPath"], #path to the player's sprite goes here
        pTag="player",
        pMass=3,
        startingPosition=mapResponse[2],#pygame.math.Vector2(screenWidth/2, screenHeight/2),
        startingVelocity=pygame.math.Vector2(0, 0),
        pVelocityCap=pygame.math.Vector2(100, 100),
        startingWeaponID=0
    )
    inCharacterSelect = False

if not inCharacterSelect and not inMainmenu:
    setPlayer(1)

def play():
    global inMainmenu
    global inCharacterSelect
    inMainmenu = False
    inCharacterSelect = True

def exitCharacterSelect():
    global inCharacterSelect
    inCharacterSelect = False

#DEBUG
player.pickupItem(ID=0)

mainloop()