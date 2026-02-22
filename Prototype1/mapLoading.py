import pygame
try:
    import Prototype1.OtherClasses as OtherClasses
except:
    import OtherClasses
import csv

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
    mapData = pygame.sprite.Group()
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
    initialOffset = [(baseScreenDimensions[0]) / 2, (baseScreenDimensions[1] + tileSize) / 2] #(baseScreenDimensions[0] + tileSize / 2, baseScreenDimensions[1] + tileSize / 2) [x, y] -  - tileSize  + tileSize
    initialOffset[1] -= (tileSize - playerHeight)

    for row in segmentedData:
        currentNodePosition[1] = 0
        for column in row:
            if not int(column) == -1 and not int(column) == STARTKEY and not int(column) == ITEMKEY and not int(column) == ENEMYKEY: #if tile not empty
                try:
                    sprite = tileData[column][0]
                    frictionCoef = tileData[column][1]
                except:
                    sprite = tileData[0][0]
                    frictionCoef = tileData[0][1]

                ########REVERT A
                INVALIDKEYS = [STARTKEY, ITEMKEY, ENEMYKEY, -1]

                lWall = row[max(0, currentNodePosition[1] - 1)]
                rWall = row[min(len(row) - 1, currentNodePosition[1] + 1)]
                uWall = segmentedData[max(0, currentNodePosition[0] - 1)][currentNodePosition[1]]
                dWall = segmentedData[min(len(segmentedData) - 1, currentNodePosition[0] + 1)][currentNodePosition[1]]
                lWallPresent = not int(lWall) in INVALIDKEYS#lWall != STARTKEY and lWall != ITEMKEY and int(lWall) != -1
                rWallPresent = not int(rWall) in INVALIDKEYS#rWall != STARTKEY and rWall != ITEMKEY and int(rWall) != -1
                roofPresent = not int(uWall) in INVALIDKEYS
                floorPresent = not int(dWall) in INVALIDKEYS
                sandwichWall = lWallPresent and rWallPresent
                lCorner = floorPresent and lWallPresent and (not rWallPresent) and (not roofPresent)
                rCorner = floorPresent and rWallPresent and not lWallPresent and not roofPresent
                roof = not floorPresent
                #tags = ["floor"]gb
                tags = []
                if roof:
                    tags = ["roof", "wall"]
                elif lCorner:
                    tags = ["lCorner", "wall"]
                elif rCorner:
                    tags = ["rCorner", "wall"]
                elif sandwichWall:
                    tags = ["floor", "wall"]
                else:
                    tags = ["wall"]
                tags.append("floor")
                #####END

                mapData.add(OtherClasses.WallObj(
                    size= pygame.Vector2(tileSize, tileSize),
                    position= pygame.Vector2(
                        x=(currentNodePosition[1] * tileSize) - 2 * tileSize,# - tileSize//2,# + (1 if tileSize%2 > 0 else 0),
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
                    -initialOffset[1] + (currentNodePosition[0] * tileSize),
                    initialOffset[0] + (currentNodePosition[1] * tileSize)
                )
            elif int(column) == ENEMYKEY:
                print("reg")
                enemyStartPositions.append(pygame.Vector2(
                    x=(currentNodePosition[1] * tileSize)  - tileSize,
                    y=(currentNodePosition[0] * tileSize)
                ))
            currentNodePosition[1] += 1
        currentNodePosition[0] += 1

    originOffset = pygame.Vector2(
        x=(startPos[1] * 1),
        y=(startPos[0] * -1)
    )
    for node in mapData:
        node.rect.centerx += originOffset.x
        node.rect.centery += originOffset.y
    for x in enemyStartPositions: ##here
        x.x += originOffset.x
        x.y += originOffset.y

    return (mapData, startPos, originOffset, enemyStartPositions)

#response = loadMapData(
#    mapName="testMapMove",
#    baseScreenDimensions=(1600, 1280),
#    STARTKEY=5,
#    ITEMKEY=6,
#    ENEMYKEY=6,
#    tileSize=76,
#    playerHeight=25
#)
#responseLs = [x for x in response[0]]
#responseLs.sort(key=lambda tile: tile.rect.centery)
#for tile in responseLs:
#    print(tile.tags)