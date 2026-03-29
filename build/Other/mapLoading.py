import pygame

try:
    from ..Classes import OtherClasses
    import dictionaries
except:
    import Classes.OtherClasses as OtherClasses
    import Other.dictionaries as dictionaries

import random
import csv

pygame.init()

# // Would be an enum, but these attributes aren't constant until the end of loadMapData
class MapResponse():
    def __init__(
            self,
            mapData,
            items,
            startPos,
            enemyStartPositions,
            playerDistFromCentre
        ):
        # // These variables are constant after being initialised and so are capitalised
        self.MAPDATA = mapData
        self.ITEMS = items
        self.STARTPOS = startPos
        self.ENEMYSTARTPOSITIONS = enemyStartPositions
        self.PLAYERDISTFROMCENTRE = playerDistFromCentre

def loadMapData(
    mapName: str,
    # IDs of specific tile types
    # // Passed as a dictionary to ease scaling tile types in the future
    KEYS: dict[str, int],
    TILESIZE: pygame.Vector2,
    baseScreenDimensions: pygame.Vector2,
    tileData: dict[int, tuple[str, float]] = {
        #0: ("Sprites/DefaultSprite.png", (0.75, 0.5))
        0: ("Sprites/TileSprite.png", (0.75, 0.5))
    },  # ID: (spritePath, frictionCoef => (x, y))
) -> MapResponse:
    additionalRows = 3

    INVALIDKEYS = list(KEYS.values())
    INVALIDKEYS.append(-1) # Constant from now on

    # // Tiles and items use pygame.sprite.Groups since they are lists of objects which inherit from pygame.sprite.Sprite
    # // enemyStartPositions uses a list since it stores pygame.Vector2 objects instead of pygame.sprite.Sprite objects
    # // In the future when enemy types might get implemented, enemyStartPositions should probably be a dict[int, list[pygame.Vector2]]
    # // to link IDs (int) to a list of spawn points
    mapData = pygame.sprite.Group()
    items = pygame.sprite.Group()
    enemyStartPositions = []
    with open(f"Maps/{mapName}.csv", "r") as map:
        data = csv.reader(map, delimiter=" ", quotechar="|")
        segmentedData = []
        for row in data:
            segmentedData.append([int(x) for x in row[0].split(",")])
        map.close()

    currentNodePosition = [
        0,
        0,
    ]  # Shouldn't be extended but needs to be modifiable => [y, x]
    # // Tiles are squares in this scenario, however if they aren't in the future, this logic is already implemented to cover that
    initialOffset = pygame.Vector2(
        TILESIZE.x // 2,
        TILESIZE.y // 2
    )

    longestRow = 0
    for row in segmentedData:
        if len(row) > longestRow:
            longestRow = len(row)
    
    for x in range(additionalRows):
        segmentedData.insert(0, [-1 for i in range(0, longestRow)])

    for row in segmentedData:
        # Reset column index
        currentNodePosition[1] = 0
        for column in row:
            # General check to see if the ID is considered a wall or not
            if not column in INVALIDKEYS:
                # Try assign sprite and friction data from the tile's metadata
                try:
                    sprite = tileData[column][0]
                    frictionCoef = tileData[column][1]
                except:
                    # Default data values
                    sprite = tileData[0][0]
                    frictionCoef = tileData[0][1]
                
                # Gets the IDs of adjacent nodes
                # // Inline clamping is messy but creating a separate function would be just as messy and therefore redundant
                lWall = int(row[max(0, currentNodePosition[1] - 1)])
                rWall = int(row[min(len(row) - 1, currentNodePosition[1] + 1)])

                roof = int(segmentedData[max(0, currentNodePosition[0] - 1)][currentNodePosition[1]])
                floor = int(segmentedData[min(len(segmentedData) - 1, currentNodePosition[0] + 1)][currentNodePosition[1]])

                # The IDs are stored in separate variables to simplify the expressions in lWallPresent, rWallPresent, etc.
                lWallPresent = (not lWall in INVALIDKEYS) or currentNodePosition[1] - 1 < 0
                rWallPresent = (not rWall in INVALIDKEYS) or currentNodePosition[1] + 1 >= len(row)

                roofPresent = (not roof in INVALIDKEYS) or currentNodePosition[0] - 1 < 0
                floorPresent = (not floor in INVALIDKEYS) or currentNodePosition[0] + 1 >= len(segmentedData)

                lCorner = (not lWallPresent) and rWallPresent and (not roofPresent)
                rCorner = (not rWallPresent) and lWallPresent and (not roofPresent)
                roof = not floorPresent

                # Assign tags
                # All tiles are considered walls and so start with the "wall" tag
                tags = ["wall"]
                if roof:
                    tags.append("roof")
                if lCorner:
                    tags.extend(["floor", "lCorner"])
                if rCorner:
                    tags.extend(["floor", "rCorner"])
                if lWallPresent and rWallPresent:
                    tags.append("floor")
                
                mapData.add(
                    OtherClasses.WallObj(
                        size=pygame.Vector2(TILESIZE.x, TILESIZE.y),
                        # currentNodePosition translated into absoluteCoordinates =
                        # currentNodePosition * TILESIZE + distance to tile centre
                        position=pygame.Vector2(
                            (currentNodePosition[1] * TILESIZE.x),
                            (currentNodePosition[0] * TILESIZE.y)
                        ) + initialOffset,
                        frictionCoef=frictionCoef,
                        spritePath=sprite,
                        pTags=tags
                    )
                )
            elif column == KEYS["STARTKEY"]:
                # Set start position
                startPos = pygame.Vector2(
                    (currentNodePosition[1] * TILESIZE.x),
                    (currentNodePosition[0] * TILESIZE.y)
                ) + initialOffset
                startPos.y += initialOffset.y
            elif column == KEYS["ITEMKEY"]:
                # Get a random item
                ID = random.randint(0, len(dictionaries.allItems.keys()) - 1)
                itemPos = pygame.Vector2(
                    (currentNodePosition[1] * TILESIZE.x),
                    (currentNodePosition[0] * TILESIZE.y)
                ) + initialOffset

                # And add it to (rendered) items
                items.add(
                    OtherClasses.Item(
                        pID=ID,
                        startingPosition=itemPos,
                        UIWindow=OtherClasses.ItemUIWindow(
                            itemID=ID,
                            replaces=dictionaries.allItems[ID]["replaces"],
                            pos=pygame.Vector2(itemPos.x + 200, itemPos.y - 125),
                            size=(400, 150),
                        ),
                    )
                )
            elif column == KEYS["ENEMYKEY"]:
                enemyPos = pygame.Vector2(
                    (currentNodePosition[1] * TILESIZE.x),
                    (currentNodePosition[0] * TILESIZE.y)
                ) #+ initialOffset
                enemyStartPositions.append(enemyPos)

                # // Future code could look like this for attaching IDs to enemy spawn points:
                #if column in enemyDict.keys():
                #    enemyDict[column].append(enemyPos)
                #else:
                #    enemyDict[column] = [enemyPos]

            # Move along 1 column
            currentNodePosition[1] += 1
        # Move down a row
        currentNodePosition[0] += 1

    # // Centre is considered to be the centre of the screen as absolute coordinates
    # // Ususally it would be (0, 0), however in this case that would cause everything to be offset by the screenDimensions / 2
    # // when the player is redrawn at the centre of the screen
    playerDistFromCentre = pygame.Vector2(
        (baseScreenDimensions.x // 2 - startPos.x),
        (baseScreenDimensions.y // 2 - startPos.y)
    )

    # Offset everything other than the player by this distance so that the startPos tile in the tiled software aligns with the player
    # on screen
    for node in mapData:
        node.rect.center += playerDistFromCentre
    for item in items:
        item.rect.center += playerDistFromCentre
    for enemyStart in enemyStartPositions:
        enemyStart += playerDistFromCentre
    
    return MapResponse(
        mapData=mapData,
        items=items,
        startPos=startPos,
        enemyStartPositions=enemyStartPositions,
        playerDistFromCentre=playerDistFromCentre
    )

debug = False
if debug:
    a = loadMapData(
        mapName="testMapMove3",
        KEYS={
            "STARTKEY": 5,
            "ITEMKEY": 6,
            "ENEMYKEY": 2
        },
        TILESIZE=pygame.Vector2(76, 76),
        baseScreenDimensions=pygame.Vector2(1000, 800)
    )
    pass