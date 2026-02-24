try:
    import transfer.suvat as suvat
except:
    import suvat
import csv

class Point():
    def __init__(
            self,
            x: int,
            y: int,
            nodeMap: list[list[str]]
        ) -> None:
        self.__x = x
        self.__y = y
        self.__nodeMap = nodeMap
        if x in range(0, len(nodeMap[0])) and y in range(0, len(nodeMap)):
            self.data = nodeMap[int(y)][int(x)]
        else:
            self.data = "#"
        
    def isEmpty(self) -> bool:
        if self.data == " ":
            return True
        return False
    
    def isValid(self) -> bool:
        if self.__x in range(len(self.__nodeMap[0])) and self.__y in range(0, len(self.__nodeMap)):
            return True
        return False

    def __updateData(self) -> None:
        if self.isValid():
            self.data = self.__nodeMap[int(self.__y)][int(self.__x)]

    def x(self) -> int:
        return self.__x
    
    def setX(self, newX: int) -> None:
        self.__x = newX
        self.__updateData()

    def y(self) -> int:
        return self.__y
    
    def setY(self, newY: int) -> None:
        self.__y = newY
        self.__updateData()
    
    def getCoord(self) -> tuple[int, int]:
        return (self.__y, self.__x)

    def setCoord(self, newX: int, newY: int) -> None:
        self.__y = newY
        self.__x = newX
        self.__updateData()


def nearestNode(
        absolute: tuple[float, float],
        nodeSep: int
) -> tuple[int, int]:
    yCo = absolute[0]//nodeSep
    return (int(yCo), int(absolute[1]//nodeSep)) 

def inList(
        query: Point,
        ls: list
) -> bool:
    if len(ls) > 0:
        for item in ls:
            if item.getCoord() == query.getCoord():
                return True
    return False

def find(
        query: Point,
        ls: list[Point]
) -> int:
    for index in range(0, len(ls)):
        if ls[index].getCoord() == query.getCoord():
            return index
    return -1

def getPointsAcrossCurve(
        u: float,
        g: float,
        maxXSpeed: float,
        origin: Point,
        nodeMap: list[list[str]],
        nodeSep: int,
        dirEffect: int,
        solveForMax: bool = False,
        solvePastMax: bool = False
) -> list[Point]:
    accuracy = round(maxXSpeed) #insert optional formula here
    points = []

    g = -abs(g)

    roots = [
        suvat.solveS(
            u=u,
            g=g,
            point=0,
            direction="l"
        ),
        suvat.solveS(
            u=u,
            g=g,
            point=0,
            direction="r"
        )
    ]
    #roots.remove(0)
    maxima = suvat.solveV(
        targetV=0,
        u=u,
        g=g
    )


    #endPoint = roots[0] * 2
    t = 0
    hitHash = False

    if not solveForMax:
        tStep = dirEffect / accuracy
        while not hitHash:
            coord = nearestNode(
                absolute=(suvat.s(u=u, g=g, t=abs(t)), maxXSpeed * t),
                nodeSep=nodeSep,
            )
            coord = (origin.y() - coord[0], origin.x() + coord[1])
            currentPoint = Point(
                x=coord[1],
                y=coord[0],
                nodeMap=nodeMap
            )
            if currentPoint.isEmpty() and currentPoint.isValid():
                points.append(coord)
            else:
                hitHash = True
            t += tStep
    elif solvePastMax:
        tStep = dirEffect * (maxima / accuracy)
        t = maxima
        coord = Point(
            x=origin.x(),
            y=origin.y(),
            nodeMap=nodeMap
        )
        while not hitHash and coord.isValid():
            coord = nearestNode(
                absolute=(suvat.s(u=u, g=g, t=abs(t)), maxXSpeed * (t - maxima)),
                nodeSep=nodeSep
            )
            coord = (origin.y() - coord[0], origin.x() + coord[1])
            currentPoint = origin.y() - coord[0], origin.x() + coord[1]
            currentPoint = Point(
                x=coord[1],
                y=coord[0],
                nodeMap=nodeMap
            )
            if currentPoint.isEmpty() and currentPoint.isValid():
                points.append(coord)
            else:
                hitHash = True
            t += tStep
    else:
        tStep = dirEffect * (maxima / accuracy)
        tolerancePastMax = 10
        while -abs(maxima) - abs(tStep * tolerancePastMax) <= t and t <= abs(maxima) + abs(tStep * tolerancePastMax) and not hitHash: #t in range(-abs(maxima), abs(maxima)) and not hitHash:
            coord = nearestNode(
                absolute=(suvat.s(u=u, g=g, t=abs(t)), maxXSpeed * t),
                nodeSep=nodeSep,
            )
            coord = (origin.y() - coord[0], origin.x() + coord[1])
            currentPoint = Point(
                x=coord[1],
                y=coord[0],
                nodeMap=nodeMap
            )
            if currentPoint.isEmpty() and currentPoint.isValid():
                points.append(coord)
            else:
                hitHash = True
            t += tStep

    
    uniquePoints = []
    for point in points:
        if not point in uniquePoints: #removing duplicates
            uniquePoints.append(point)
    
    for pointIndex in range(0, len(uniquePoints)):
        uniquePoints[pointIndex] = Point( #converting each unique point to a Point object
            x=uniquePoints[pointIndex][1], # uniquePoints[pointIndex] => [y, x] origin.x() + 
            y=uniquePoints[pointIndex][0], # origin.y() - 
            nodeMap=nodeMap
        )
    
    return uniquePoints

def jumpOffEdge(
        jumpForce: float,
        gravity: float,
        maxXSpeed: float,
        origin: Point,
        nodeMap: list[list[str]],
        nodeSep: int,
        direction: str
) -> list[Point]:
    if direction == "l":
        dirEffect = -1
    else:
        dirEffect = 1
    
    parabolaPoints = list[Point](getPointsAcrossCurve(
        u=jumpForce,
        g=gravity,
        maxXSpeed=maxXSpeed,
        origin=origin,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        dirEffect=dirEffect
    ))
    topNodes = list[Point]([])

    hitRoof = False
    hitWall = False
    hitFloor = False
    roofNode = None

    for currentNode in parabolaPoints:
        if not (hitRoof or hitWall or hitFloor) and currentNode.isValid():
            upperNode = Point(
                x=currentNode.x(),
                y=currentNode.y() - 1,
                nodeMap=nodeMap
            )
            lowerNode = Point(
                x=currentNode.x(),
                y=currentNode.y() + 1,
                nodeMap=nodeMap
            )
            adjacentNode = Point(
                x=currentNode.x() + 1 * dirEffect,
                y=currentNode.y(),
                nodeMap=nodeMap
            )

            yVelocity = suvat.v(
                u=jumpForce,
                g=gravity,
                t=suvat.solveS(
                    u=jumpForce,
                    g=gravity,
                    point=currentNode.y(),
                    direction=direction
                )
            )

            if not currentNode.isEmpty() and lowerNode.isEmpty() and yVelocity >= 0:
                hitRoof = True
                roofNode = Point(
                    x=lowerNode.x(),
                    y=lowerNode.y(),
                    nodeMap=nodeMap
                )
                topNodes.append(lowerNode)
            elif not currentNode.isEmpty() and upperNode.isEmpty():
                hitFloor = True
            elif not currentNode.isEmpty() and adjacentNode.isEmpty():
                hitWall = True
            elif not currentNode in topNodes:
                topNodes.append(currentNode)
    
    if hitRoof:
        reverseAt = find(query=roofNode, ls=parabolaPoints)
        listSegment = [parabolaPoints[index] for index in range(0, reverseAt)]
        listSegment.reverse()

        for reversedPoint in listSegment:
            xDiff = dirEffect * abs(roofNode.x() - reversedPoint.x())
            yDiff = abs(roofNode.y() - reversedPoint.y())
            newPoint = Point(
                x=roofNode.x() + xDiff,
                y=roofNode.y() + yDiff,
                nodeMap=nodeMap
            )
            if not newPoint in topNodes:
                topNodes.append(newPoint)
    
    return topNodes

def getAllCoords(ls: list[Point]):
    coords = []
    for node in ls:
        if not node.getCoord() in coords:
            coords.append(node.getCoord())
    return coords

def fallOffEdge(
        origin: tuple[int, int],
        gravity: float,
        maxXSpeed: float,
        nodeMap: list[list[str]],
        nodeSep: int,
        direction: str
) -> list[Point]:
    if direction == "l":
        dirEffect = -1
    else:
        dirEffect = 1
    origin = (origin[0], origin[1] + dirEffect)

    curve = list[Point](getPointsAcrossCurve(
        u=0,
        g=gravity,
        origin=Point(
            x=origin[1],
            y=origin[0],
            nodeMap=nodeMap
        ),
        maxXSpeed=maxXSpeed,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        dirEffect=dirEffect,
        solveForMax=False,
        solvePastMax=True
    ))
    #allCoords = getAllCoords(ls=curve)

    cleanCurve = []
    for node in curve:
        if not node.getCoord() in cleanCurve:
            cleanCurve.append(node)
    cleanPoints = []
    for coord in cleanCurve:
        cleanPoints.append(Point(
            x=coord.x(),
            y=coord.y(),
            nodeMap=nodeMap
        ))
    
    return cleanPoints

#def fallOffEdge( #rough estimate, could miss key coordinates
#        origin: tuple[int, int],
#        nodeMap: list[list[str]]
#):
    

def getLowerNodes(
        topNodes: list[Point],
        nodeMap: list[list[str]]
) -> dict[str, list[Point]]:
    
    foundNodes = list[Point]([])
    floorNodes = list[Point]([])

    while len(topNodes) != 0:
        newTopNodes = list[Point]([])
        distanceFromTopNode = 0
        for node in topNodes:
            if True: #not inList(query=node, ls=foundNodes):
                foundNodes.append(node)

            currentNode = Point(
                x=node.x(),
                y=node.y() + 1,
                nodeMap=nodeMap
            )
            foundNewTopNode = [False, False]
            xStep = [-1, 1]
            if not (inList(query=currentNode, ls=topNodes) or inList(query=currentNode, ls=foundNodes)):
                while currentNode.isEmpty() and currentNode.isValid():
                    distanceFromTopNode += 1
                    foundNodes.append(Point(
                        x=currentNode.x(),
                        y=currentNode.y(),
                        nodeMap=nodeMap
                    ))
                    if distanceFromTopNode % 2 == 0:
                        for x in range(0, 2):
                            potentialNode = Point(
                                x=currentNode.x() + xStep[x],
                                y=currentNode.y(),
                                nodeMap=nodeMap
                            )
                            if potentialNode.isEmpty() and not foundNewTopNode[max(0, xStep[x])]: #and not inList(query=potentialNode, ls=newTopNodes):
                                newTopNodes.append(Point(
                                    x=potentialNode.x(),
                                    y=potentialNode.y(),
                                    nodeMap=nodeMap
                                ))
                                foundNewTopNode[max(0, xStep[x])] = True
                            elif not potentialNode.isEmpty():
                                foundNewTopNode[max(0, xStep[x])] = False
                            xStep *= 1

                    currentNode.setY(newY=currentNode.y() + 1)
                
                if not currentNode.isEmpty():
                    currentNode.setY(newY=currentNode.y() - 1)
                    floorNodes.append(currentNode)
        topNodes = list(tuple(newTopNodes))
    
    return {
        "nodes": foundNodes,
        "floorNodes": floorNodes
    }

def traverseFloor(
        nodeMap: list[list[str]],
        jumpForceInNodes: int,
        origin: Point
) -> dict[str, list]:
    step = 1
    current = Point(
        x=origin.x(),
        y=origin.y(),
        nodeMap=nodeMap
    )
    next = Point(
        x=origin.x(),
        y=origin.y(),
        nodeMap=nodeMap
    )
    nextFloor = Point(
        x=origin.x(),
        y=origin.y(),
        nodeMap=nodeMap
    )
    foundNodes = list[Point]([])
    newFloors = list[Point]([])
    corners = list[tuple[Point, str]]([])

    waypoints = list[tuple[tuple[int, int], str, tuple[int, int]]]([]) # e.g. ( (1, 0), "->", (1, 4) )
    for x in range(2):
        stop = False
        next.setX(newX=next.x() + step)
        nextFloor.setCoord(
            newX=next.x(),
            newY=next.y() + 1
        )
        while current.isValid() and not stop:
            previousCollisionStates = [False, False]
            if nextFloor.isEmpty() or not next.isEmpty() or not next.isValid():
                stop = True
                if not current in corners:
                    corners.append((
                        Point(
                            x=current.x(),
                            y=current.y(),
                            nodeMap=nodeMap
                        ),
                        "l" if step == -1 else "r"
                    ))
            if current.isEmpty():
                foundNodes.append(
                    Point(
                        x=current.x(),
                        y=current.y(),
                        nodeMap=nodeMap
                    )
                )
                stepUp = 0
                while current.isValid() and current.isEmpty() and stepUp <= jumpForceInNodes:
                    leftNode = Point(
                        x=current.x() - 1,
                        y=current.y(),
                        nodeMap=nodeMap
                    )
                    rightNode = Point(
                        x=current.x() + 1,
                        y=current.y(),
                        nodeMap=nodeMap
                    )
                    if not inList(query=current, ls=foundNodes):
                        foundNodes.append(
                            Point(
                                x=current.x(),
                                y=current.y(),
                                nodeMap=nodeMap
                            )
                        )
                    currentCollisionStates = [
                        leftNode.isValid() and not leftNode.isEmpty(),
                        rightNode.isValid() and not rightNode.isEmpty()
                    ]
                    if previousCollisionStates[0] and not currentCollisionStates[0]:
                        newFloors.append(leftNode)
                        waypoints.append((
                            (current.y() + stepUp, current.x()),
                            "->",
                            (leftNode.y(), leftNode.x())
                        ))
                    if previousCollisionStates[1] and not currentCollisionStates[1]:
                        newFloors.append(rightNode)
                        waypoints.append((
                            (current.y() + stepUp, current.x()),
                            "->",
                            (rightNode.y(), rightNode.x())
                        ))
                    previousCollisionStates = list(tuple(currentCollisionStates))
                    currentCollisionStates = [False, False]
                    stepUp += 1 #keep at end
                    current.setY(newY=current.y() - 1)
            current.setCoord(newX=next.x(), newY=next.y())
            next.setX(newX=next.x() + step)
            nextFloor.setX(newX=next.x())
        step *= -1 #reverse direction
        current = Point(
            x=origin.x(),
            y=origin.y(),
            nodeMap=nodeMap
        )
        next = Point(
            x=origin.x(),
            y=origin.y(),
            nodeMap=nodeMap
        )
    
    return {
        "nodes": list[Point](foundNodes), 
        "corners": list[tuple[Point, str]](corners),
        "newFloors": list[Point](newFloors),
        "waypoints": list[tuple[tuple[int, int], str, tuple[int, int]]](waypoints) # => ( (y1, x1), "->", (y2, x2) )
        }

def removeDuplicateWaypoints(waypoints: list):
    cleanWaypoints = []
    while len(waypoints) != 0:
        waypoint = waypoints[0]
        waypoints.pop(0)
        if (waypoint[2], "->", waypoint[0]) in waypoints:
            waypoints.remove((waypoint[2], "->", waypoint[0]))
            waypoint = (waypoint[0], "<->", waypoint[2])
        if not waypoint[0] == waypoint[2] and not waypoint in cleanWaypoints:
            cleanWaypoints.append(waypoint)
    return cleanWaypoints

def connectAdjacentWaypoints(
        waypoints: list[tuple],
        disconnectedWaypoints: list[tuple[int, int]], # (y, x) coord
        nodeMap: list[list[str]]
) -> list[tuple]: #note: removed newWaypoints list
    waypointGroups = []
    while len(disconnectedWaypoints) != 0:
        newGroup = []
        yQuery = disconnectedWaypoints[0][0] #y coordinate of first index
        preservedWaypoints = list[tuple[int, int]]([])
        for point in disconnectedWaypoints:
            if point[0] == yQuery:
                newGroup.append(point)
            else:
                preservedWaypoints.append(point)

        disconnectedWaypoints = list(tuple(preservedWaypoints))
        
        newGroup.sort(key=lambda point: point[1]) # index 1 == x coord
        waypointGroups.append(newGroup)
    
    for group in waypointGroups:
        ignoreNextConditions = False
        if not group == []:
            cornerIndexes = list[int]([0])
            for index in range(0, len(group) - 1):
                if ignoreNextConditions:
                    cornerIndexes.append(max(1, index))
                    ignoreNextConditions = False
                if group[index][1] == group[index + 1][1] - 1:
                    waypoints.append((group[index], "<->", group[index + 1]))
                #elif group[index][1] == group[max(0, index - 1)][1] + 1 and not (group[index], "<->", (group[max(0, index - 1)][0], group[max(0, index - 1)][1])) in waypoints:
                #    waypoints.append((group[index], "<->", group[index - 1]))
                elif not attemptGroundTraversal(start=group[index], end=group[index + 1], nodeMap=nodeMap):
                    cornerIndexes.append(max(1, index))
                    ignoreNextConditions = True
                else:
                    waypoints.append((group[index], "<->", group[index + 1]))
            cornerIndexes.append(len(group) - 1)

            #cornerIndexes = list(set(cornerIndexes))
            #cornerIndexes.sort()

            for cornerIndex in range(0, len(cornerIndexes) - 1):
                potentialWaypoint = (group[cornerIndexes[cornerIndex]], "<->", group[cornerIndexes[cornerIndex + 1]])
                validConnection = attemptGroundTraversal(
                    start=potentialWaypoint[0],
                    end=potentialWaypoint[2],
                    nodeMap=nodeMap
                )
                if validConnection and not potentialWaypoint in waypoints:
                    waypoints.append(potentialWaypoint)
    
    return removeDuplicateWaypoints(waypoints=waypoints)

def attemptGroundTraversal(
        start: tuple[int, int],
        end: tuple[int, int],
        nodeMap: list[list[str]]
) -> bool:
    if start[1] < end[1]:
        step = 1
    else:
        step = -1

    nextNode = Point(
        x=start[1] + 1,
        y=start[0],
        nodeMap=nodeMap
    )
    nextFloor = Point(
        x=start[1] + 1,
        y=start[0] + 1,
        nodeMap=nodeMap
    )
    while nextNode.x() != end[1]:
        if nextFloor.isEmpty() or not nextNode.isEmpty():
            return False
        nextFloor.setX(newX=nextFloor.x() + step)
        nextNode.setX(newX=nextNode.x() + step)
    return True

def precompileGraph(
        nodeMap: list[list[str]],
        nodeSep: int,
        gravity: float,
        enemyData: dict,
        origin: tuple[int, int]
) -> dict[str, list]:
    origin = getLowerNodes(
        topNodes=[Point(
            x=origin[1],
            y=origin[0],
            nodeMap=nodeMap
        )],
        nodeMap=nodeMap
    )["floorNodes"][0]

    floors = list[Point]([origin])
    traversedFloors = list[tuple[int, int]]([])
    corners = []

    gravity = -abs(gravity)

    maxJumpHeight = suvat.s(
        u=enemyData["jumpForce"],
        g=gravity,
        t=suvat.solveV(
            targetV=0,
            u=enemyData["jumpForce"],
            g=gravity
        )
    )
    jumpHeightInNodes = maxJumpHeight // nodeSep

    allNodes = list[tuple[int, int]]([])
    waypoints = []

    while len(floors) != 0:
        #print(traversedFloors)
        #print([floor.getCoord() for floor in floors])
        newFloors = []
        for floor in floors:
            if not floor.getCoord() in traversedFloors:
                traversedFloors.append(floor.getCoord())
                floorData = traverseFloor(
                    nodeMap=nodeMap,
                    jumpForceInNodes=jumpHeightInNodes,
                    origin=floor
                )
                floorData["nodes"] = list[Point](floorData["nodes"])
                floorY = floor.y()
                for corner in floorData["corners"]:
                    if not corner in corners:
                        corners.append(corner)
                for node in floorData["nodes"]:
                    if node.y() == floorY and not node.getCoord() in traversedFloors:
                        traversedFloors.append(node.getCoord())
                for newFloor in floorData["newFloors"]:
                    if not newFloor.getCoord() in allNodes and not newFloor.getCoord() in traversedFloors: #traversedFloors:
                        newFloors.append(newFloor)
                for waypoint in floorData["waypoints"]:
                    if not waypoint in waypoints:
                        waypoints.append(waypoint)
                for node in floorData["nodes"]: #can be shortened but harms readability too much
                    if not node.getCoord() in allNodes:
                        allNodes.append(node.getCoord())
        
        for corner in corners: # corner => (Point, direction)
            topNodes = jumpOffEdge(
                jumpForce=enemyData["jumpForce"],
                gravity=gravity,
                maxXSpeed=enemyData["maxSpeed"][1],
                origin=corner[0],
                nodeMap=nodeMap,
                nodeSep=nodeSep,
                direction = corner[1]
            )
            fallNodes = fallOffEdge(
                origin=corner[0].getCoord(),
                gravity=gravity,
                maxXSpeed=enemyData["maxSpeed"][1],
                nodeMap=nodeMap,
                nodeSep=nodeSep,
                direction=corner[1]
            )
            columnNodeData = {
                "nodes": [],
                "floorNodes": []
            }
            for x in range(0, 2):
                indexesToRemove = list[int]([])
                if x == 0:
                    observedList = topNodes
                else:
                    observedList = fallNodes
                for node in observedList:
                    if node.data != " ":
                        indexesToRemove.append(observedList.index(node))

                preservedNodes = []
                for index in range(0, len(observedList)):
                    if not index in indexesToRemove:
                        preservedNodes.append(observedList[index])
                observedList = list(tuple(preservedNodes))
                response = getLowerNodes(
                    topNodes=observedList,
                    nodeMap=nodeMap
                )
                columnNodeData["nodes"].extend(response["nodes"])
                columnNodeData["floorNodes"].extend(response["floorNodes"])
            cleanColumnData = {
                "nodes": [],
                "floorNodes": []
            }
            for x in columnNodeData["nodes"]:
                if not x in cleanColumnData["nodes"]:
                    cleanColumnData["nodes"].append(x)
            for x in columnNodeData["floorNodes"]:
                if not x in cleanColumnData["floorNodes"]:
                    cleanColumnData["floorNodes"].append(x)
            columnNodeData = cleanColumnData

            debugData = [x.getCoord() for x in columnNodeData["nodes"]]
            noDuplicates = []
            for x in debugData:
                if not x in noDuplicates:
                    noDuplicates.append(x)
            noDuplicates.sort(key=lambda x: x[1])
            for newFloor in columnNodeData["floorNodes"]:
                if not newFloor.getCoord() in traversedFloors and not (newFloor.getCoord() in allNodes or inList(query=newFloor, ls=floors)): #(newFloor.getCoord() in traversedFloors or newFloor in floors):
                    newFloors.append(newFloor)
                waypoints.append((corner[0].getCoord(), "->", newFloor.getCoord()))
            for node in columnNodeData["nodes"]:
                if not node in allNodes:
                    allNodes.append(node.getCoord())
        corners = []
        floors = list(tuple(newFloors))

    return {
        "nodes": allNodes,
        "waypointData": compileWaypointData(waypoints=waypoints, nodeMap=nodeMap)
    }

def queryWaypoints(
        waypoints: list[tuple],
        query: tuple[int, int] = None,
        doubleQuery: tuple[int, int] = None,
        y: int = None,
        x: int = None,
        ignoreCompressed: bool = False
) -> list[tuple]:
    foundWaypoints = []
    for waypoint in waypoints:
        if waypoint[0][1] == x or waypoint[2][0] == x:
            foundWaypoints.append(waypoint)
        if waypoint[0][0] == y or waypoint[2][0] == y:
            foundWaypoints.append(waypoint)
        if doubleQuery != None:
            if (waypoint[0] == query and waypoint[2] == doubleQuery) or (waypoint[0] == doubleQuery and waypoint[2] == query):
                foundWaypoints.append(waypoint)
        elif waypoint[0] == query or waypoint[2] == query:
            foundWaypoints.append(waypoint)
    
    return foundWaypoints

def queryCompressed(
        waypoints,
        compressedWaypoint
):
    foundWaypoints = []
    start = compressedWaypoint[0][1]
    end = compressedWaypoint[2][1]
    for xCoord in range(start, end + 1):
        response = queryWaypoints(
            waypoints=waypoints,
            query=(compressedWaypoint[0][0], xCoord),
            ignoreCompressed=True
        )
        for x in response:
            if x[0] == (compressedWaypoint[0][0], xCoord) and not x in foundWaypoints and not x[1] == "-":
                foundWaypoints.append(x)
    return foundWaypoints

def checkCompressed(
        query,
        waypoint
):
    return (waypoint[0][0] == query[0] and waypoint[2][0] == query[0] and waypoint[0][1] <= query[1] and query[1] <= waypoint[2][1])
    

def queryDisconnectedWaypoints(
        disconnectedWaypoints: list[tuple[int, int]],
        x: int = 0,
        y: int = 0
) -> list[tuple[int, int]]:
    foundWaypoints = []
    for waypoint in disconnectedWaypoints:
        if waypoint[0] == y or waypoint[1] == x:
            foundWaypoints.append(waypoint)
    return foundWaypoints

def checkForDuplicates(waypoints):
    found = []
    for x in waypoints:
        ls = queryWaypoints(waypoints=waypoints, query=x[0], doubleQuery=x[1])
        if len(ls) > 1:
            found.extend(ls)
    return found

def compressWaypoints(
        waypoints: list,
        disconnectedWaypoints: list[tuple[int, int]],
        nodeMap: list[list[str]]
):
    waypointsByY = []
    for yCoord in range(0, len(nodeMap)):
        waypointsByY.append(queryDisconnectedWaypoints(disconnectedWaypoints=disconnectedWaypoints, y=yCoord))
    for groupIndex in range(0, len(waypointsByY)):
        waypointsByY[groupIndex].sort(key=lambda x: x[1])
        index = 0
        lEdge = None
        rEdge = None
        while index <= len(waypointsByY[groupIndex]) - 1:
            rEdge = waypointsByY[groupIndex][index]
            if lEdge == None:
                lEdge = waypointsByY[groupIndex][index]
            elif not attemptGroundTraversal(
                start=lEdge,
                end=rEdge, #(proposed)
                nodeMap=nodeMap
            ):
                rEdge = waypointsByY[groupIndex][index - 1]
                waypoints.append((lEdge, "-", rEdge))
                lEdge = waypointsByY[groupIndex][index]
            index += 1
        if lEdge != None:
            waypoints.append((lEdge, "-", rEdge))
    return removeDuplicateWaypoints(waypoints=waypoints)
    

def compileWaypointData(
        waypoints: list[tuple[tuple[int, int], str, tuple[int, int]]], # e.g. [ ( (y1, x1) "<->", (y2, x2) ) ]
        nodeMap: list[list[str]]
) -> dict[str, list]:
    waypoints = removeDuplicateWaypoints(waypoints=waypoints)

    disconnectedWaypoints = []
    for waypoint in waypoints:
        if not waypoint[0] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[0])
        if not waypoint[2] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[2])
    
    a = list(tuple(waypoints))
    waypoints = connectAdjacentWaypoints(
        waypoints=waypoints,
        disconnectedWaypoints=disconnectedWaypoints,
        nodeMap=nodeMap
    )
    waypoints.sort(key=lambda waypoint: waypoint[0][0])

    return {
        "waypoints": waypoints,
        "disconnectedWaypoints": disconnectedWaypoints
    }

def findInconsistencies(
        waypoints1,
        waypoints2,
        nodeMap
):
    for rowIndex in range(0, len(nodeMap)):
        for columnIndex in range(0, len(nodeMap[rowIndex])):
            response1 = queryWaypoints(
                waypoints=waypoints1,
                query=(rowIndex, columnIndex)
            )
            response2 = queryWaypoints(
                waypoints=waypoints2,
                query=(rowIndex, columnIndex)
            )
            if len(response1) != len(response2):
                print(f"Coord: ({rowIndex}, {columnIndex})")

def loadMap(fileName: str, invalidKeys) -> list[list[str]]:
    with open(fileName, "r", newline="") as f:
        data = csv.reader(f, delimiter=" ", quotechar="|")
        segmentedData = []
        for row in data:
            segmentedData.append([x for x in row[0].split(",")])
        segmentedData.pop(0)
        testGraph = []
        for row in segmentedData:
            #testGraph.append([" " if x == "-1" or x == "5" or x == "6" else "#" for x in row])
            testGraph.append([" " if int(x) in invalidKeys else "#" for x in row])
        return testGraph

#def main(map: str, origin: tuple[int, int]):
#    testGraph = loadMap(fileName=map) #(7, 6)
#
#    gravityAccel = 9.81 * 15
#    nodeSep = 15
#
#    enemyData = {
#        "jumpForce": 100,
#        "maxSpeed": (100, 37.5)
#    }
#
#    response = precompileGraph(
#        nodeMap=testGraph,
#        nodeSep=nodeSep,
#        gravity=gravityAccel,
#        enemyData=enemyData,
#        origin=origin
#    )
#
#    allNodes = response["nodes"]
#    waypoints = response["waypointData"]["waypoints"]
#
#    for x in allNodes:
#        testGraph[x[0]][x[1]] = "x"
#    for x in waypoints:
#        testGraph[x[0][0]][x[0][1]] = "W"
#        testGraph[x[2][0]][x[2][1]] = "W"
#    
#    pass
#    for line in testGraph:
#        print(line)
#    for waypoint in waypoints:
#        print(waypoint)
#    pass
#
#def outputTestGraph(fileName: str) -> None:
#    data = loadMap(fileName=fileName)
#    for row in data:
#        print(row)
#    pass
#
##t = time.time()
#mapName = "Prototype1/transfer/Maps/testMapMove6.csv"
#origin = (16, 0)
#
#main(map=mapName, origin=origin)
#outputTestGraph(fileName=mapName)
#e = time.time()
#print(e - t)