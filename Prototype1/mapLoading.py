import pygame
try:
    import Prototype1.OtherClasses as OtherClasses
except:
    import OtherClasses
import dictionaries
import random
import csv

pygame.init()

def loadMapData(
        mapName: str,
        STARTKEY: int,
        ITEMKEY: int,
        ENEMYKEY: int,
        tileSize: int,
        baseScreenDimensions: tuple[int, int],
        playerHeight: int,
        tileData: dict[int, tuple[str, float]] = {0: ("Sprites/DefaultSprite.png", (0.75, 0.5))}, # ID: (spritePath, frictionCoef => (x, y))
) -> tuple[pygame.sprite.Group, tuple[int, int]]:
    INVALIDKEYS = [STARTKEY, ITEMKEY, ENEMYKEY, -1]

    mapData = pygame.sprite.Group()
    items = pygame.sprite.Group()
    enemyStartPositions = []
    with open(f"Prototype1/transfer/Maps/{mapName}.csv", "r") as map:
        data = csv.reader(map, delimiter=" ", quotechar="|")
        segmentedData = []
        for row in data:
            segmentedData.append([x for x in row[0].split(",")])
        segmentedData.pop(0)
        map.close()
    
    currentNodePosition = [0, 0] #shouldn't be extended but needs to be modifiable => [y, x]
    startPos = (0, 0)
    initialOffset = [(baseScreenDimensions[0]) / 2, (baseScreenDimensions[1]) / 2] #(baseScreenDimensions[0] + tileSize / 2, baseScreenDimensions[1] + tileSize / 2) [x, y] -  - tileSize  + tileSize
    initialOffset[1] -= (tileSize - playerHeight)
    initialOffset = pygame.Vector2((baseScreenDimensions[0]), (baseScreenDimensions[1]))

    for row in segmentedData:
        currentNodePosition[1] = 0
        for column in row:
            if not int(column) in INVALIDKEYS:#int(column) == -1 and not int(column) == STARTKEY and not int(column) == ITEMKEY and not int(column) == ENEMYKEY: #if tile not empty
                try:
                    sprite = tileData[column][0]
                    frictionCoef = tileData[column][1]
                except:
                    sprite = tileData[0][0]
                    frictionCoef = tileData[0][1]

                ########REVERT A

                lWall = row[max(0, currentNodePosition[1] - 1)]
                rWall = row[min(len(row) - 1, currentNodePosition[1] + 1)]
                uWall = segmentedData[max(0, currentNodePosition[0] - 1)][currentNodePosition[1]]
                dWall = segmentedData[min(len(segmentedData) - 1, currentNodePosition[0] + 1)][currentNodePosition[1]]
                lWallPresent = not (int(lWall) in INVALIDKEYS or currentNodePosition[1] - 1 < 0)
                rWallPresent = not (int(rWall) in INVALIDKEYS or currentNodePosition[1] + 1 >= len(row))
                roofPresent = not int(uWall) in INVALIDKEYS
                floorPresent = not int(dWall) in INVALIDKEYS
                sandwichWall = lWallPresent and rWallPresent
                lCorner = floorPresent and rWallPresent and (not lWallPresent) and (not roofPresent)
                rCorner = floorPresent and lWallPresent and not rWallPresent and not roofPresent
                roof = not floorPresent
                tags = []
                if roof:
                    tags = ["roof", "wall", "floor"]
                elif lCorner:
                    tags = ["lCorner", "wall", "floor"]
                elif rCorner:
                    tags = ["rCorner", "wall", "floor"]
                elif sandwichWall:
                    tags = ["floor", "wall"]
                else:
                    tags = ["wall"]
                #####END

                mapData.add(OtherClasses.WallObj(
                    size= pygame.Vector2(tileSize, tileSize),
                    position= pygame.Vector2(
                        x=(currentNodePosition[1] * tileSize),# - 2 * tileSize,# - tileSize//2,# + (1 if tileSize%2 > 0 else 0),
                        y=(currentNodePosition[0] * tileSize)
                    ),
                    frictionCoef=frictionCoef,
                    spritePath=sprite,

                    ########REVERT A
                    pTags=tags
                    #####END
                ))
            elif int(column) == STARTKEY:
                startPos = pygame.Vector2(
                    -initialOffset[1] + (currentNodePosition[1] * tileSize),
                    initialOffset[0] + (currentNodePosition[0] * tileSize)
                )
            elif int(column) == ITEMKEY:
                ID = random.randint(0, len(dictionaries.allItems) - 1)
                itemPos = pygame.Vector2(
                    x=(currentNodePosition[1] * tileSize),# - 2*tileSize,
                    y=(currentNodePosition[0] * tileSize)
                )
                print(ID)
                items.add(OtherClasses.Item(
                    pID=ID,
                    startingPosition=itemPos,
                    UIWindow=OtherClasses.ItemUIWindow(
                        itemID=ID,
                        replaces=dictionaries.allItems[ID]["replaces"],
                        pos=pygame.Vector2(itemPos.x + 200, itemPos.y - 125),
                        size=(400, 150)
                    )
                ))
            elif int(column) == ENEMYKEY:
                print("reg")
                enemyStartPositions.append(pygame.Vector2(
                    x=(currentNodePosition[1] * tileSize),#  - tileSize,
                    y=(currentNodePosition[0] * tileSize)
                ))
            currentNodePosition[1] += 1
        currentNodePosition[0] += 1

    originOffset = pygame.Vector2(
        x=(startPos[1] * 1),
        y=(startPos[0] * -1)
    )
    #for node in mapData:
    #    node.rect.centerx += originOffset.x
    #    node.rect.centery += originOffset.y
    #for x in enemyStartPositions: ##here
    #    x.x += originOffset.x
    #    x.y += originOffset.y
    #for x in items:
    #    x.rect.centerx += originOffset.x
    #    x.rect.centery += originOffset.y
    for node in mapData:
        node.rect.centerx -= initialOffset.x
        node.rect.centery += initialOffset.y
    for x in enemyStartPositions: ##here
        x.x += initialOffset.x
        x.y -= initialOffset.y
    for x in items:
        x.rect.centerx += initialOffset.x
        x.rect.centery -= initialOffset.y

    coords = [x.rect for x in mapData]
    coords.sort(key=lambda x: x.centerx)
    pass

    return (mapData, items, startPos, originOffset, enemyStartPositions)

mapResponse = loadMapData(
    mapName="1",
    STARTKEY=5,
    ITEMKEY=6,
    ENEMYKEY=2,
    tileSize=76,
    baseScreenDimensions=(1000, 800),
    playerHeight=25
)