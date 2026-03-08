import pygame

try:
    import Prototype1.OtherClasses as OtherClasses
except:
    import OtherClasses
import dictionaries
import random
import csv
import transfer.pathing as pathing

pygame.init()


def loadMapData(
    mapName: str,
    STARTKEY: int,
    ITEMKEY: int,
    ENEMYKEY: int,
    tileSize: int,
    baseScreenDimensions: tuple[int, int],
    tileData: dict[int, tuple[str, float]] = {
        0: ("Sprites/DefaultSprite.png", (0.75, 0.5))
    },  # ID: (spritePath, frictionCoef => (x, y))
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

    currentNodePosition = [
        0,
        0,
    ]  # shouldn't be extended but needs to be modifiable => [y, x]

    initialOffset = pygame.Vector2(
        tileSize // 2,
        tileSize // 2
    )

    for row in segmentedData:
        currentNodePosition[1] = 0
        for column in row:
            column = int(column)
            if not column in INVALIDKEYS:
                try:
                    sprite = tileData[column][0]
                    frictionCoef = tileData[column][1]
                except:
                    sprite = tileData[0][0]
                    frictionCoef = tileData[0][1]
                
                lWall = int(row[max(0, currentNodePosition[1] - 1)])
                rWall = int(row[min(len(row) - 1, currentNodePosition[1] + 1)])

                roof = int(segmentedData[max(0, currentNodePosition[0] - 1)][currentNodePosition[1]])
                floor = int(segmentedData[min(len(segmentedData) - 1, currentNodePosition[0] + 1)][currentNodePosition[1]])

                lWallPresent = (not lWall in INVALIDKEYS) or currentNodePosition[1] - 1 < 0
                rWallPresent = (not rWall in INVALIDKEYS) or currentNodePosition[1] + 1 >= len(row)

                roofPresent = (not roof in INVALIDKEYS) or currentNodePosition[0] - 1 < 0
                floorPresent = (not floor in INVALIDKEYS) or currentNodePosition[0] + 1 >= len(segmentedData)

                lCorner = (not lWallPresent) and rWallPresent and (not roofPresent)
                rCorner = (not rWallPresent) and lWallPresent and (not roofPresent)
                roof = not floorPresent

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
                        size=pygame.Vector2(tileSize, tileSize),
                        position=pygame.Vector2(
                            (currentNodePosition[1] * tileSize),
                            (currentNodePosition[0] * tileSize)
                        ) + initialOffset,
                        frictionCoef=frictionCoef,
                        spritePath=sprite,
                        pTags=tags
                    )
                )
            elif column == STARTKEY:
                startPos = pygame.Vector2(
                    (currentNodePosition[1] * tileSize),
                    (currentNodePosition[0] * tileSize)
                ) + initialOffset
            elif column == ITEMKEY:
                ID = random.randint(0, len(dictionaries.allItems.keys()) - 1)
                itemPos = pygame.Vector2(
                    (currentNodePosition[1] * tileSize),
                    (currentNodePosition[0] * tileSize)
                ) + initialOffset
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
            elif column == ENEMYKEY:
                enemyPos = pygame.Vector2(
                    (currentNodePosition[1] * tileSize),
                    (currentNodePosition[0] * tileSize)
                ) + initialOffset
                enemyStartPositions.append(enemyPos)

            currentNodePosition[1] += 1
        currentNodePosition[0] += 1
    
    playerDistFromCentre = pygame.Vector2(
        (baseScreenDimensions.x // 2 - startPos.x),
        (baseScreenDimensions.y // 2 - startPos.y)
    )
    for node in mapData:
        node.rect.center += playerDistFromCentre
    for item in items:
        item.rect.center += playerDistFromCentre
    for enemyStart in enemyStartPositions:
        enemyStart += playerDistFromCentre
    
    return (mapData, items, startPos, enemyStartPositions)

loadMapData(
    mapName="testMapMove8",
    STARTKEY=5,
    ITEMKEY=6,
    ENEMYKEY=2,
    tileSize=76,
    baseScreenDimensions=pygame.Vector2(1000, 800)
)