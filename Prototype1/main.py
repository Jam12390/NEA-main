import pygame
import sys
from EntitySubclasses import Player, Enemy
from OtherClasses import WallObj, Item, ItemUIWindow
from dictionaries import *
import UI

import mapLoading
from transfer import precompile, pathing

screenWidth = 1000
screenHeight = screenWidth * 0.8  # keep the ratio for w-h at 1:0.8 - could change later

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()
paused = False

FPS = 60

mapName = "testMapMove8"
PLAYERSIZE = pygame.Vector2(50, 50)
TILESIZE = 76

MOVEMENTTOLERANCE = pygame.Vector2(1, 0.5)

mapResponse = None
loadedMap = None
precompiledGraph = None
walls = None
enemies = None
items = None

player = Player(
       FPS=FPS,
       jumpForce=allCharacters[0]["jumpForce"],  # pixels/second
       maxHP=allCharacters[0]["hp"],
       defense=allCharacters[0]["defense"],
       speed=allCharacters[0]["speed"],
       pAttackCooldown=allCharacters[0]["attackCooldown"],
       pSize=allCharacters[0]["size"],
       spritePath=allCharacters[0][
           "imgPath"
       ],  # path to the player's sprite goes here
       tags=["player"],
       pMass=3,
       startingPosition=pygame.Vector2(0, 0),  # pygame.math.Vector2(screenWidth/2, screenHeight/2),
       startingVelocity=pygame.math.Vector2(0, 0),
       pVelocityCap=pygame.math.Vector2(100, 100),
       startingWeaponID=0,
   )

inMainmenu = False

inCharacterSelect = False

inDeathScreen = False

def setup(mapName: str):
    global mapResponse
    global loadedMap
    global precompiledGraph
    global walls
    global enemies
    global items
    global inDeathScreen

    inDeathScreen = False

    mapPath = f"Prototype1/transfer/Maps/{mapName}.csv"

    mapResponse = mapLoading.loadMapData(
        mapName=mapName,
        STARTKEY=5,
        ITEMKEY=6,
        ENEMYKEY=2,
        tileSize=TILESIZE,
        baseScreenDimensions=(screenWidth, screenHeight),
        playerHeight=25,
    )

    enemyData = {"jumpForce": 130, "maxSpeed": (50, 50)}

    invalidKeys = [5, 6, 2, -1]

    loadedMap = precompile.loadMap(fileName=mapPath, invalidKeys=invalidKeys)

    precompiledGraph = precompile.precompileGraph(
        nodeMap=loadedMap,
        nodeSep=15,
        gravity=9.81 * 15,
        enemyData=enemyData,
        origin=(16, 0),
    )

    walls = mapResponse[0]
    items = mapResponse[1]

    enemies = pygame.sprite.Group()
    for enemyPos in mapResponse[3]:
        enemies.add(
            Enemy(
                FPS=FPS,
                jumpForce=enemyData["jumpForce"],
                maxHP=10,
                defense=10,
                speed=1,
                pAttackCooldown=10,
                spritePath="Sprites/DefaultSprite.png",
                tags=["enemy"],
                pMass=5,
                startingPosition=pygame.Vector2(enemyPos.x, enemyPos.y),  # (800, 400),
                pVelocityCap=pygame.Vector2(enemyData["maxSpeed"]),
                startingVelocity=pygame.Vector2(0, 0),
                pSize=pygame.Vector2(50, 50),
                pIgnoreYFriction=True,
            )
        )

    for x in enemies:
        x.absoluteCoordinate.x += TILESIZE
        #x.absoluteCoordinate.y -= mapResponse[3].y
        #x.absoluteCoordinate.x -= screenWidth / 2

mainLoopRunning = True

inventoryOpen = False

previousBlockedMotion = ()


def mainloop():
    global inventoryOpen
    global paused
    global inDeathScreen
    global inCharacterSelect
    pygame.display.set_caption("Main loop")

    if inMainmenu:
        mainmenu()

    while mainLoopRunning:
        clock.tick(FPS)

        if inCharacterSelect:
            characterSelect()

        events = pygame.event.get()

        for event in events:
            """
            KEYDOWN is for events which should only happen once if the key is pressed.
            i.e. I is likely to be held for 2-3 frames. If KEYDOWN wasn't used, the inventory screen would open and close rapidly.
            """
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    for item in items:
                        if (
                            item.UIWindow.shown
                        ):  # if the UI is shown, the item is in pickup range
                            item.pickup(target=player)
                if event.key == pygame.K_i:
                    inventoryOpen = True
                    paused = True
                    inventory()
                if event.key == pygame.K_ESCAPE and not inventoryOpen:
                    paused = True
                    pauseMenu()
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not player.weapon.currentlyAttacking:
                    player.weapon.attack(parent=player)

            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()

        if not paused:
            # cycle through all potential movement inputs
            if (
                (keys[pygame.K_w] or keys[pygame.K_SPACE])
                and player.isGrounded
                and not "u" in player.blockedMotion
            ):
                player.jump()
                player.previousGroundedYCoord = tuple([player.absoluteCoordinate.y])[0]

            if (
                keys[pygame.K_a]
                and not player.containsForce(axis="x", ref="UserInputLeft")
                and not "l" in player.blockedMotion
                and not player.crouched
            ):
                player.addForce(
                    axis="x", direction="l", ref="UserInputLeft", magnitude=2500
                )
            elif not keys[pygame.K_a]:
                player.removeForce(axis="x", ref="UserInputLeft")

            if (
                keys[pygame.K_d]
                and not player.containsForce(axis="x", ref="UserInputRight")
                and not "r" in player.blockedMotion
                and not player.crouched
            ):
                player.addForce(
                    axis="x", direction="r", ref="UserInputRight", magnitude=2500
                )
            elif not keys[pygame.K_d]:
                player.removeForce(axis="x", ref="UserInputRight")

            if keys[pygame.K_s]:
                if (
                    not player.containsForce(axis="y", ref="UserInputDown")
                    and not player.isGrounded
                ):
                    player.fastFalling = True  # start fast falling
                    player.addForce(
                        axis="y", direction="d", ref="UserInputDown", magnitude=2500
                    )
                    player.modifySpeedCap(axis="y", magnitude=15)
                elif player.isGrounded:
                    if player.fastFalling:  # are we fast falling
                        player.fastFalling = False  # stop fast falling
                        player.modifySpeedCap(
                            axis="y", magnitude=-15
                        )  # change speed cap back
                    player.removeForce(axis="y", ref="UserInputDown")
            else:  # not holding S
                player.removeForce(
                    axis="y", ref="UserInputDown"
                )  # remove downwards force
                if player.fastFalling:
                    player.modifySpeedCap(axis="y", magnitude=-15)  # stop fast falling
                    player.fastFalling = False

            screen.fill((0, 0, 0))  # rgb value for black background

            # update all objects (this includes collision detection)
            playerMoved = player.update(collidableObjects=[walls, items, enemies], enemies=enemies)

            if -MOVEMENTTOLERANCE.x <= playerMoved.x and playerMoved.x <= MOVEMENTTOLERANCE.x:
                playerMoved.x = 0
            if -MOVEMENTTOLERANCE.y <= playerMoved.y and playerMoved.y <= MOVEMENTTOLERANCE.y:
                playerMoved.y = 0

            player.absoluteCoordinate += playerMoved

            walls.update()
            enemies.update(
                collidableObjects=[walls],
                precompiledData=precompiledGraph,
                nodeMap=loadedMap,
                nodeSep=30,
                target=player,
                playerRect=player.rect,
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
                wall.rect.centerx -= playerMoved.x
                wall.rect.centery -= playerMoved.y
            for item in items:
                item.rect.centerx -= playerMoved.x
                item.rect.centery -= playerMoved.y
            for enemy in enemies:
                enemy.rect.centerx -= playerMoved.x
                enemy.rect.centery -= playerMoved.y
                enemy.sightRect.center = enemy.rect.center

            player.healthBar.update()

            if player.healthBar.isDead():
                inDeathScreen = True
                deathScreen()
                player.healthBar.changeHP(1)

            items.update()
            redraw()
            pygame.display.flip()


def redraw():  # it's important to note that redraw() DOES NOT update() any of the objects it's drawing
    player.rect.center = (screenWidth / 2, screenHeight / 2)
    player.currentNode = (
        int((player.absoluteCoordinate.y) // 75),  # (y, x)
        int((player.absoluteCoordinate.x) // 75),
    )
    screen.blit(player.image, player.rect)

    if player.weapon.currentlyAttacking:
        screen.blit(player.weapon.image, player.weapon.rect)

    for sprite in walls:
        screen.blit(sprite.image, sprite.rect)
        
    walls.draw(screen)
    enemies.draw(screen)

    for x in items:
        screen.blit(x.image, x.rect)
        if x.UIWindow.shown:
            screen.blit(x.UIWindow.surface, x.UIWindow.rect)

    screen.blit(player.healthBar.surface, player.healthBar.rect)


def nullFunc():
    pass


def inventory():
    global inventoryOpen
    global paused

    textColour = (255, 255, 255)  # white
    backgroundColour = (125, 125, 125)
    itemHoverColour = (100, 100, 100)

    titleFont = pygame.font.SysFont("Calibri", 45)
    title = titleFont.render("Inventory", False, textColour)

    itemTitleFont = pygame.font.SysFont("Calibri", 30)
    itemTitle = itemTitleFont.render("Items", False, textColour)

    itemFont = pygame.font.SysFont("Calibri", 20)
    startingPos = [(screenWidth - 100) // 3 + 15, 150]

    itemDescriptions = {}
    for ID in player.inventory.keys():
        desc = [f"{allItems[ID]["name"]}:"]
        desc.extend(UI.wrapText(plainText=allItems[ID]["description"], wordsPerLine=5))
        desc.extend([f"Replaces: {allItems[ID]["replaces"]}", f"Effects: {allItems[ID]["effects"]}"])
        itemDescriptions[ID] = desc

    itemHeaders = [
        UI.TextButton(
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
                (screenWidth - 100) // 3 * 2 + 15, 25
            ),
            titleFirst=True
        )
        for ID in player.inventory.keys()
    ]

    while inventoryOpen:
        # clock.tick(FPS) #note for future prototypes: ticking the clock twice imitates slow motion (at the cost of FPS ofc)
        redraw()
        mousePos = pygame.mouse.get_pos()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        background = pygame.Surface((screenWidth - 100, screenHeight - 100))
        # background.fill((125, 125, 125, 255))

        # Base Background
        pygame.draw.rect(
            surface=background,
            color=backgroundColour,
            rect=pygame.Surface.get_rect(background),
            border_radius=10,
        )

        # Title
        background.blit(title, (25, 25))

        # Top Divider
        pygame.draw.line(
            surface=background,
            color=textColour,
            start_pos=(0, 90),
            end_pos=((screenWidth - 100), 90),
        )

        # Weapon - Item Divider
        pygame.draw.line(
            surface=background,
            color=textColour,
            start_pos=((screenWidth - 100) // 3, 90),
            end_pos=((screenWidth - 100) // 3, screenHeight - 100),
        )

        # Item Title
        background.blit(itemTitle, ((screenWidth - 100) // 3 + 10, 105))
        pygame.draw.line(
            surface=background,
            color=textColour,
            start_pos=((screenWidth - 100) // 3 + 10, 130),
            end_pos=((screenWidth - 100) // 3 + 80, 130),
        )

        # Item - Description Divider
        pygame.draw.line(
            surface=background,
            color=textColour,
            start_pos=((screenWidth - 100) // 3 * 2, 90),
            end_pos=((screenWidth - 100) // 3 * 2, screenHeight - 100),
        )

        # Weapon Image
        scaledRect = pygame.transform.smoothscale(
            pygame.image.load(allWeapons[player.weapon.ID]["imgPath"]),
            (player.weapon.rect.width * 20, player.weapon.rect.height * 20),
        )
        weaponRect = pygame.Surface.get_rect(scaledRect)
        weaponRect.center = (
            (screenWidth - 100) // 6,
            int(screenHeight - 100) // 2 + 50,
        )
        weaponRect.center += allWeapons[player.weapon.ID]["inventoryOffset"]

        weaponText = [f"{allWeapons[player.weapon.ID]["name"]}:"]
        weaponText.extend(UI.wrapText(
            plainText=allWeapons[player.weapon.ID]["description"], wordsPerLine=5
        ))

        weapon = UI.ImageButton(
            position=pygame.Vector2(
                (screenWidth - 100) // 6, int(screenHeight - 100) // 2
            ),
            
            size=pygame.Vector2(
                player.weapon.rect.width * 3.75, player.weapon.rect.height * 20
            ),
            imgPath=allWeapons[player.weapon.ID]["imgPath"],
            text=weaponText,
            
            buttonColour=pygame.Color(backgroundColour),
            hoverColour=pygame.Color(itemHoverColour),
            func=nullFunc,
            absoluteDescriptionPosition=pygame.Vector2(
                (screenWidth - 100) // 3 * 2 + 12, 30
            ),
            titleFirst=True
        )
        weapon.update(mousePos)
        background.blit(weapon.surface, weapon.rect)
        if weapon.hoveredOver:
            background.blit(weapon.description.background, weapon.description.rect)

        startingPos = [(screenWidth - 100) // 3 + 100, 150]
        for itemIndex in range(0, len(itemHeaders)):
            # background.blit(itemHeaders[itemIndex], (startingPos[0], startingPos[1]))
            itemHeaders[itemIndex].update(mousePos)
            background.blit(itemHeaders[itemIndex].surface, itemHeaders[itemIndex].rect)
            if itemHeaders[itemIndex].hoveredOver:
                background.blit(
                    itemHeaders[itemIndex].description.background,
                    itemHeaders[itemIndex].description.rect,
                )

        screen.blit(background, (50, 50))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    inventoryOpen = False
                    paused = False
        pygame.display.flip()


def pauseMenu():
    global paused
    pauseText = pygame.font.SysFont("Calibri", 90).render(
        "Paused", False, (255, 255, 255)
    )

    buttonText = ["Resume", "Abandon Run", "Exit to Desktop"]
    renderedText = []
    functions = [unpause, abandonRun, quit]

    startingPos = pygame.Vector2(25, screenHeight - (75 * len(buttonText)) - 25)
    for index in range(0, len(buttonText)):
        renderedText.append(
            UI.TextButton(
                position=startingPos,
                text=buttonText[index],
                func=functions[index],
                textSize=35,
            )
        )
        startingPos.y += renderedText[0].rect.height + 20

    for button in renderedText:
        button.rect.left = 25

    while paused:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

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
    global inCharacterSelect
    inCharacterSelect = True
    paused = False
    setup(mapName=mapName)


def openOptions():
    pass


def quit():
    pygame.quit()
    sys.exit()


def mainmenu():
    global inMainmenu
    global inCharacterSelect
    titleText = pygame.font.SysFont("Calibri", 90).render(
        "'Blended'", True, (255, 255, 255)
    )
    subtitleText = pygame.font.SysFont("Calibri", 15).render(
        "AKA the skeleton sidescroller template i worked so hard on", True, (255, 255, 255)
    )

    buttonText = ["Play", "Exit To Desktop"]
    functions = [play, quit]

    renderedText = []

    startingPos = pygame.Vector2(25, screenHeight - (75 * len(buttonText)) - 50)
    for index in range(0, len(buttonText)):
        renderedText.append(
            UI.TextButton(
                position=startingPos,
                text=buttonText[index],
                func=functions[index],
                textSize=40,
                #size=pygame.Vector2(200, 50),
            )
        )
        startingPos.y += 90#renderedText[0].size.y + 25

    while inMainmenu:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        screen.blit(titleText, (25, 25))
        screen.blit(subtitleText, (50, 100))

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


def characterSelect():
    global player
    titleText = pygame.font.SysFont("Calibri", 90).render(
        "Character Select", True, (255, 255, 255)
    )
    subtitleText = pygame.font.SysFont("Calibri", 30).render(
        "Please choose a character:", True, (255, 255, 255)
    )

    characters = []

    startingPos = pygame.Vector2(100, 250)

    for ID in allCharacters.keys():
        characters.append(
            UI.ImageButton(
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
                    f"Size: {allCharacters[ID]["size"]}",
                ],
                size=pygame.Vector2(100, 100),
                descriptionOffset=pygame.Vector2(75, -125),
                data=ID
            )
        )
        startingPos.y += 150

    while inCharacterSelect:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        screen.blit(titleText, (20, 25))
        screen.blit(subtitleText, (25, 110))

        mousePos = pygame.mouse.get_pos()

        for character in characters:
            character.update(mousePos)
            screen.blit(character.surface, character.rect)
            if character.hoveredOver:
                screen.blit(
                    character.description.background, character.description.rect
                )

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for character in characters:
                    if character.hoveredOver:
                        character.onClick(character.data)
        
        pygame.display.flip()

def deathScreen():
    global inDeathScreen
    global inCharacterSelect

    deathTitle = pygame.font.SysFont("Calibri", 90).render("You Died.", True, (255, 255, 255))
    deathSubtitle = pygame.font.SysFont("Calibri", 30).render("Retry?", True, (255, 255, 255))

    buttonText = ["Retry", "Exit To Desktop"]
    buttonFuncs = [setup, quit]

    startingPos = pygame.Vector2(125, screenHeight - 100 * len(buttonText))

    buttons = [
        UI.TextButton(
            position=pygame.Vector2(startingPos.x, startingPos.y + 100 * index),
            text=buttonText[index],
            func=buttonFuncs[index],
            textSize=45
        )
        for index in range(0, len(buttonText))
    ]
    for button in buttons:
        button.rect.left = 25

    while inDeathScreen:
        redraw()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        mousePos = pygame.mouse.get_pos()

        screen.blit(deathTitle, (20, 25))
        screen.blit(deathSubtitle, (25, 110))

        for button in buttons:
            button.update(mousePos=mousePos)
            screen.blit(button.surface, button.rect)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.hoveredOver:
                        try:
                            button.onClick(mapName=mapName)
                        except:
                            button.onClick()
        
        pygame.display.flip()
    inCharacterSelect = True


def setPlayer(ID):
    global player
    global inCharacterSelect
    player = Player(
        FPS=FPS,
        jumpForce=allCharacters[ID]["jumpForce"],  # pixels/second
        maxHP=allCharacters[ID]["hp"],
        defense=allCharacters[ID]["defense"],
        speed=allCharacters[ID]["speed"],
        pAttackCooldown=allCharacters[ID]["attackCooldown"],
        pSize=allCharacters[ID]["size"],
        spritePath=allCharacters[ID][
            "imgPath"
        ],  # path to the player's sprite goes here
        tags=["player"],
        pMass=3,
        startingPosition=mapResponse[
            2
        ],  # pygame.math.Vector2(screenWidth/2, screenHeight/2),
        startingVelocity=pygame.math.Vector2(0, 0),
        pVelocityCap=pygame.math.Vector2(100, 100),
        startingWeaponID=0,
    )
    player.absoluteCoordinate -= pygame.Vector2(screenWidth + 76, -screenHeight / 2)
    player.healthBar.resetHP()
    #player.absoluteCoordinate.x -= TILESIZE//2
    inCharacterSelect = False

def play():
    global inMainmenu
    global inCharacterSelect
    inMainmenu = False
    inCharacterSelect = True


def exitCharacterSelect():
    global inCharacterSelect
    inCharacterSelect = False

print("--------------------------------")
setup(mapName="testMapMove8")

if not inCharacterSelect and not inMainmenu:
    setPlayer(1)

player.pickupItem(ID=1, quantity=2)

mainloop()
