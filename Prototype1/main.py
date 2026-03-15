import pygame
import sys
from EntitySubclasses import Player, Enemy
from OtherClasses import WallObj, Item, ItemUIWindow
from dictionaries import *
import UI

import mapLoading
import nMapLoading
from transfer import precompile, pathing

screenWidth = 1000
screenHeight = screenWidth * 0.8  # keep the ratio for w-h at 1:0.8 - could change later

### General pygame setup

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((screenWidth, screenHeight))
clock = pygame.time.Clock()
paused = False

FPS = 60

mapName = "testMapMoveEn"
PLAYERSIZE = pygame.Vector2(50, 50)
TILESIZE = 76

# minimum value for movement to be registered
# too low of a value causes problems with the player coming to a stop
# too high of a value increases the chance of issues with absoluteCoordinate
MOVEMENTTOLERANCE = pygame.Vector2(1, 0.5)

mapResponse = None
loadedMap = None
precompiledGraph = None
walls = None
enemies = None
items = None

# Default player to any existing player
# only used during first boot during the redraw section of mainMenu()
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

# current game state (in terms of UI)
inMainmenu = True

inCharacterSelect = False

inDeathScreen = False

def setup(mapName: str):
    # needs to affect variables outside of it's default scope
    global mapResponse
    global loadedMap
    global precompiledGraph
    global walls
    global enemies
    global items
    global inDeathScreen

    inDeathScreen = False

    mapPath = f"Prototype1/transfer/Maps/{mapName}.csv"

    # Load map data
    mapResponse = nMapLoading.loadMapData(
        mapName=mapName,
        KEYS={
            "STARTKEY": 5,
            "ITEMKEY": 6,
            "ENEMYKEY": 2
        },
        tileSize=TILESIZE,
        baseScreenDimensions=pygame.Vector2(screenWidth, screenHeight)
    ) # => (tiles, items, startingPosition, list[enemyStartingPositions])

    enemyData = {
        "jumpForce": 130,
        "maxSpeed": (50, 50)
    } # some default values for enemyData, can be changed in the future

    invalidKeys = [5, 6, 2, -1] # tile IDs which shouldn't be considered as walls (e.g. Enemies)

    # contains a 2D list of walls and empty spaces (same as nodeMap in precompile.py)
    loadedMap = precompile.loadMap(fileName=mapPath, invalidKeys=invalidKeys)

    #precompiles the graph based on the starting point stored in mapResponse[2] TODO: update origin to be variable based on mapResponse[2]
    precompiledGraph = precompile.precompileGraph(
        nodeMap=loadedMap,
        nodeSep=15,
        gravity=9.81 * 15,
        enemyData=enemyData,
        origin=mapResponse.STARTPOS // TILESIZE, # assuming tiles are square
    )

    walls = mapResponse.MAPDATA#mapResponse[0]
    items = mapResponse.ITEMS#mapResponse[1]

    enemies = pygame.sprite.Group()
    for enemyPos in mapResponse.ENEMYSTARTPOSITIONS: # iterate through where enemies should start
        enemies.add( # and make a new object for each position
            Enemy(
                FPS=FPS,
                jumpForce=enemyData["jumpForce"],
                maxHP=10,
                defense=10,
                speed=1,
                pAttackCooldown=10,
                spritePath="Sprites/DefaultSprite.png", # default
                tags=["enemy"],
                pMass=5,
                startingPosition=pygame.Vector2(enemyPos.x, enemyPos.y),
                pVelocityCap=pygame.Vector2(enemyData["maxSpeed"]),
                startingVelocity=pygame.Vector2(0, 0),
                pSize=pygame.Vector2(50, 50),
                pIgnoreYFriction=True, # helps with simplifying pathing (no need to simulate friction when jumping)
            )
        )

    #######REWORK MAP
    #for x in enemies:
    #    x.absoluteCoordinate.x += TILESIZE
        #x.absoluteCoordinate.y -= mapResponse[3].y
        #x.absoluteCoordinate.x -= screenWidth / 2

def outputEnemyCoords(): # debug procedure
    global enemies
    for enemy in enemies:
        print(enemy.absoluteCoordinate)

def outputPathingData(): # debug procedure for devs - outputs data for all enemies who are pathing
    global enemies

    print(f"Player:")
    print(f"Absolute Coordinate: {player.absoluteCoordinate}")
    print(f"Current Node: {player.currentNode}\n---\n")

    for enemy in enemies:
        if enemy.currentPath != []:
            print(f"Aggro Status: {enemy.aggrod}")
            print(f"Absolute Coordinate: {enemy.absoluteCoordinate}")
            print(f"Current Node: {enemy.currentNode}")
            print(f"Current Path: {enemy.currentPath}")
            print(f"Velocity: {enemy._velocity}")
            print(f"Acceleration: {enemy.getAcceleration()}")
            print(f"X: {enemy._xForces}")
            print(f"Y: {enemy._yForces}")
            print("---\n")

def debugCollide():
    for e in enemies:
        if pygame.Rect.colliderect(player.rect, e.sightRect):
            print(f"Player colliding with enemy at {e.absoluteCoordinate}")

# initialise game state variables
mainLoopRunning = True

inventoryOpen = False

previousBlockedMotion = ()

#debug variables - determines whether data is output when debug keybinds are pressed
debug = True

observePaths = True
observeNodes = True
pauseOnObservation = True

def mainloop():
    # mainloop needs to change variables for all other procedures
    global inventoryOpen
    global paused
    global inDeathScreen
    global inCharacterSelect

    global observePaths
    global observeNodes
    global pauseOnObservation
    # this is why all UI screens are in main.py. Separating them into different files would be too much of an architectural change

    pygame.display.set_caption("Main loop")

    if inMainmenu:
        mainmenu()

    while mainLoopRunning:
        clock.tick(FPS) # next frame

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
                
                if event.key == pygame.K_l and debug:
                    print(f"Player: {player.currentNode}")
                    print("--------")
                    for enemy in enemies:
                        if observePaths:
                            print(f"Enemy: {enemy.currentPath}")
                        if observeNodes:
                            print(f"Enemy: {enemy.currentNode}")
                        print("---")
                    print("----------------------------")
                    if pauseOnObservation:
                        pass # this is where a breakpoint would be placed if pauseOnObservation was true
                        # in any other situation pausing the program would be sufficient for variable watch
                        # however in this case the program would likely pause in PhysicsObject.py or another file, making some variables out of scope
                if event.key == pygame.K_o and debug:
                    pauseOnObservation = not pauseOnObservation # toggle whether the breakpoint should trigger, assuming debug == true

                if event.key == pygame.K_n:
                    observeNodes = not observeNodes # toggle if nodes should be outputted during debug code
                if event.key == pygame.K_m:
                    observePaths = not observePaths # toggle if currentPaths should be outputted during debug code
                    
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
                player.previousGroundedYCoord = tuple([player.absoluteCoordinate.y])[0] # used in realigning the player's absolute y coordinate

            if ( # logic for moving left
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

            if ( # logic for moving right
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

            if keys[pygame.K_s]: # logic for fast falling
                if (
                    not player.containsForce(axis="y", ref="UserInputDown")
                    and not player.isGrounded # if the player is mid-air (can fast fall)
                ):
                    player.fastFalling = True  # start fast falling
                    player.addForce(
                        axis="y", direction="d", ref="UserInputDown", magnitude=2500
                    )
                    # adds a noticeable difference to the speed cap (can be changed later using attributes like player.speed)
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

            screen.fill((0, 0, 0))  # rgb value for black background - could be changed to an image by future devs
            # if so, this would be moved to redraw() and would use pygame.image.smoothscale(pygame.image.load(background), screenSize) instead of an rgb value

            # update the player and get it's displacement
            playerMoved = player.update(collidableObjects=[walls, items, enemies], enemies=enemies)

            # i would use in range() however range() only accepts integers
            if -MOVEMENTTOLERANCE.x <= playerMoved.x and playerMoved.x <= MOVEMENTTOLERANCE.x:
                playerMoved.x = 0
            if -MOVEMENTTOLERANCE.y <= playerMoved.y and playerMoved.y <= MOVEMENTTOLERANCE.y:
                playerMoved.y = 0

            player.absoluteCoordinate += playerMoved

            walls.update() # redundant but here in case any future logic is added regarding walls
            enemies.update(
                collidableObjects=[walls],
                precompiledData=precompiledGraph,
                nodeMap=loadedMap,
                nodeSep=30,
                target=player,
                playerRect=player.rect,
            ) # update enemies after player
            items.update()

            if "u" in player.blockedMotion:
                playerMoved.y = max(0, playerMoved.y)
            if "d" in player.blockedMotion:
                playerMoved.y = min(0, playerMoved.y)
            if "l" in player.blockedMotion:
                playerMoved.x = max(0, playerMoved.x)
            if "r" in player.blockedMotion:
                playerMoved.x = min(0, playerMoved.x)

            # only move objects which aren't the player after all physics logic has finished
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

            # update HUD
            player.healthBar.update()

            # check if the game should swap to deathScreen
            if player.healthBar.isDead():
                inDeathScreen = True
                deathScreen()

            redraw()
            pygame.display.flip()


def redraw():  # it's important to note that redraw() DOES NOT update() any of the objects it's drawing
    player.rect.center = (screenWidth / 2, screenHeight / 2) # recenter player (if it somehow became uncentred)
    player.currentNode = ( # recalculate currentNode for pathing
        int((player.absoluteCoordinate.y) // 75),  # (y, x)
        int((player.absoluteCoordinate.x) // 75),
    )

    # draw sprites here

    screen.blit(player.image, player.rect)

    if player.weapon.currentlyAttacking:
        screen.blit(player.weapon.image, player.weapon.rect)

    for sprite in walls:
        screen.blit(sprite.image, sprite.rect)
        
    walls.draw(screen)
    enemies.draw(screen)

    for item in items:
        screen.blit(item.image, item.rect)
        if item.UIWindow.shown:
            screen.blit(item.UIWindow.surface, item.UIWindow.rect)

    screen.blit(player.healthBar.surface, player.healthBar.rect)

# python doesn't support inline functions, which I would use in inventory
# Therefore nullFunc() exists to be called when func is a required parameter
def nullFunc():
    pass


def inventory():
    # Drawing from back -> front in this order:
    # Screen:
    #   Paused game state
    #   Dim
    #   Background:
    #       Background Colour
    #       Borders
    #       Weapon "Button" (Image)
    #       Item Headers
    #       Description

    # Inventory needs to modify inventoryOpen globally along with paused
    global inventoryOpen
    global paused

    # Colours to change later if needed
    textColour = (255, 255, 255)  # white
    backgroundColour = (125, 125, 125)
    itemHoverColour = (100, 100, 100)

    # Fonts
    titleFont = pygame.font.SysFont("Calibri", 45)
    title = titleFont.render("Inventory", False, textColour)

    itemTitleFont = pygame.font.SysFont("Calibri", 30)
    itemTitle = itemTitleFont.render("Items", False, textColour)

    # Starting position for item headers in the second column
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
                (screenWidth - 100) // 3 * 2 + 15, 25 # Constant position of 3rd column
            ),
            titleFirst=True
        )
        for ID in player.inventory.keys() # Iterating through the player's inventory
    ]

    while inventoryOpen:
        redraw()
        mousePos = pygame.mouse.get_pos()

        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)

        # Dim
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

        # I'm reusing UI.ImageButton instead of making another "Hover" class since both ImageButton
        # and HoverImage would have near identical logic + code
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
            func=nullFunc, # therefore I use nullFunc() here so nothing happens on image click
            absoluteDescriptionPosition=pygame.Vector2(
                (screenWidth - 100) // 3 * 2 + 12, 30
            ),
            titleFirst=True
        )

        weapon.update(mousePos) # update the image like you would a button

        background.blit(weapon.surface, weapon.rect)

        # Check whether to display the Weapon's description
        if weapon.hoveredOver:
            background.blit(weapon.description.background, weapon.description.rect)

        #startingPos = [(screenWidth - 100) // 3 + 100, 150]

        # Iterate through and .update() item titles
        for itemIndex in range(0, len(itemHeaders)):
            # background.blit(itemHeaders[itemIndex], (startingPos[0], startingPos[1]))
            itemHeaders[itemIndex].update(mousePos)
            background.blit(itemHeaders[itemIndex].surface, itemHeaders[itemIndex].rect)
            # Display the description of any hovered over items
            if itemHeaders[itemIndex].hoveredOver:
                background.blit(
                    itemHeaders[itemIndex].description.background,
                    itemHeaders[itemIndex].description.rect,
                )

        screen.blit(background, (50, 50))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # Keybind for toggling inventory
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    inventoryOpen = False
                    paused = False
        
        pygame.display.flip()


def pauseMenu():
    # Draws in back -> front order:
    # Screen:
    #   Paused game state
    #   Dim
    #   pauseText (title)
    #   Buttons

    # paused needs to be modified across main.py
    global paused

    # Fonts
    pauseText = pygame.font.SysFont("Calibri", 90).render(
        "Paused", False, (255, 255, 255)
    )

    # Button setup
    buttonText = ["Resume", "Abandon Run", "Exit to Desktop"]
    renderedText = []
    functions = [unpause, abandonRun, quit]

    # Starting position of the top left corner of the first button
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
        # Align button to the left of the screen (purely a design choice)
        button.rect.left = 25

    while paused:
        # Draw but not update (this is why redraw() was made to not update any of its targets)
        redraw()

        # Dim
        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        screen.blit(pauseText, (25, 25))

        mousePos = pygame.mouse.get_pos()

        # Update and draw buttons
        for button in renderedText:
            button.update(mousePos)
            screen.blit(button.surface, button.rect)

        for event in pygame.event.get():
            # Toggle pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                unpause()
            # Run the button's onClick() function if it's pressed
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
    # Send the player back to the character select screen
    inCharacterSelect = True
    # Make sure the game is unpaused
    paused = False
    # And re-run setup (this is why the game's setup was made into a procedure)
    setup(mapName=mapName)
    

def quit():
    pygame.quit()
    sys.exit()


def mainmenu():
    # Draws in back -> front order:
    # Screen:
    #   Paused game state
    #   Dim
    #   Title
    #   Subtitle
    #   Buttons

    global inMainmenu
    global inCharacterSelect

    # Rendered title + subtitle
    titleText = pygame.font.SysFont("Calibri", 90).render(
        "'Blended'", True, (255, 255, 255)
    )
    subtitleText = pygame.font.SysFont("Calibri", 15).render(
        "AKA the skeleton sidescroller template i worked so hard on", True, (255, 255, 255)
    )

    # Function assignments
    buttonText = ["Play", "Exit To Desktop"]
    functions = [play, quit]

    renderedText = []

    # Starting position of buttons (like in pauseMenu())
    startingPos = pygame.Vector2(25, screenHeight - (75 * len(buttonText)) - 50)

    # Create individual TextButton objects for each text in buttonText
    for index in range(0, len(buttonText)):
        renderedText.append(
            UI.TextButton(
                position=startingPos,
                text=buttonText[index],
                func=functions[index],
                textSize=40
            )
        )
        startingPos.y += 90#renderedText[0].size.y + 25

    while inMainmenu:
        # Redraw paused game
        redraw()

        # Dim
        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        # Title + Subtitle
        screen.blit(titleText, (25, 25))
        screen.blit(subtitleText, (50, 100))

        mousePos = pygame.mouse.get_pos()

        # Update and draw buttons
        for button in renderedText:
            button.update(mousePos)
            screen.blit(button.surface, button.rect)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in renderedText:
                    # Run a button's onClick() function if it's hovered over and clicked on
                    if button.hoveredOver:
                        # Note for future devs:
                        # Try to make the onClick subroutine for each button object a procedure since it reduces
                        # the chance of errors occuring for missing or overload arguments.
                        # If functions are absolutely necessary, use keyword arguments and try: except: statements
                        # to reduce the chance of errors occurring
                        button.onClick()

        pygame.display.flip()


def characterSelect():
    global player

    # Title + Subtitle
    titleText = pygame.font.SysFont("Calibri", 90).render(
        "Character Select", True, (255, 255, 255)
    )
    subtitleText = pygame.font.SysFont("Calibri", 30).render(
        "Please choose a character:", True, (255, 255, 255)
    )

    characters = []

    startingPos = pygame.Vector2(100, 250)

    # Iteration using a for loop helps with future scaling
    for ID in allCharacters.keys():
        characters.append(
            UI.ImageButton(
                position=startingPos,
                imgPath=allCharacters[ID]["imgPath"],
                func=setPlayer,
                # Loading data into the image button
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
        # Draw paused screen
        redraw()

        # Dim
        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        # Title + Subtitle
        screen.blit(titleText, (20, 25))
        screen.blit(subtitleText, (25, 110))

        mousePos = pygame.mouse.get_pos()

        # Update and draw character sprites
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
                    # character.onClick() = setPlayer() so we can always use character.data as a parameter
                    if character.hoveredOver:
                        character.onClick(character.data)
        
        pygame.display.flip()

def deathScreen():
    # Drawing order (back -> front):
    # Screen:
    #   Paused game state
    #   Title + Subtitle
    #   Buttons

    global inDeathScreen
    global inCharacterSelect

    # Rendered title + subtitle
    deathTitle = pygame.font.SysFont("Calibri", 90).render("You Died.", True, (255, 255, 255))
    deathSubtitle = pygame.font.SysFont("Calibri", 30).render("Retry?", True, (255, 255, 255))

    # Button text and functions
    buttonText = ["Retry", "Exit To Desktop"]
    buttonFuncs = [setup, quit]

    # Starting position of buttons (top -> bottom)
    startingPos = pygame.Vector2(125, screenHeight - 100 * len(buttonText))

    # Initialise TextButton objects for each index in buttonText
    buttons = [
        UI.TextButton(
            position=pygame.Vector2(startingPos.x, startingPos.y + 100 * index),
            text=buttonText[index],
            func=buttonFuncs[index],
            textSize=45
        )
        for index in range(0, len(buttonText))
    ]
    # Aligning buttons to the left of the screen
    for button in buttons:
        button.rect.left = 25

    while inDeathScreen:
        # Draw paused screen
        redraw()

        # Dim
        dim = pygame.Surface((screenWidth, screenHeight))
        dim.fill((0, 0, 0))
        dim.set_alpha(200)
        screen.blit(dim, (0, 0))

        mousePos = pygame.mouse.get_pos()

        # Title + Subtitle
        screen.blit(deathTitle, (20, 25))
        screen.blit(deathSubtitle, (25, 110))

        # Update and draw buttons
        for button in buttons:
            button.update(mousePos=mousePos)
            screen.blit(button.surface, button.rect)
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.hoveredOver:
                        # Unfortunately, in this case onClick() might be setup() which takes a map name as a parameter
                        # Due to this, we need a try: except: statement to try and provide mapName as a keyname argument 
                        try:
                            button.onClick(mapName=mapName)
                        except:
                            button.onClick()
        
        pygame.display.flip()
    # The only way to leave the death screen without exiting the game is by going back to the character select screen
    # So we should make sure that by the time deathScreen() ends, inCharacterSelect is set to true
    inCharacterSelect = True


def setPlayer(ID: int):
    # Needs to modify Player object globally alongside inCharacterSelect
    global player
    global inCharacterSelect
    # Set the player variable to a new Player object, disposing of the old one
    player = Player(
        # Load the data from allCharacters[ID] into the object
        FPS=FPS,
        jumpForce=allCharacters[ID]["jumpForce"],
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
        startingPosition=mapResponse.STARTPOS, # In terms of absoluteCoordinate
        startingVelocity=pygame.math.Vector2(0, 0),
        pVelocityCap=pygame.math.Vector2(100, 100),
        startingWeaponID=0,
    )
    
    player.healthBar.resetHP() # Make sure the player always starts with their max HP
    
    # If the player is in character select, make them leave
    inCharacterSelect = False

def play(): # play (from main menu button)
    #Therefore:
    global inMainmenu
    global inCharacterSelect
    # The game should exit the main menu
    inMainmenu = False
    # And enter character select
    inCharacterSelect = True


def exitCharacterSelect():
    global inCharacterSelect
    inCharacterSelect = False

print("--------------------------------")
# Run setup with hardcoded mapName
setup(mapName=mapName)

## DEBUG

if not inCharacterSelect and not inMainmenu:
    setPlayer(1)

player.pickupItem(ID=1, quantity=2)

## END DEBUG

mainloop()