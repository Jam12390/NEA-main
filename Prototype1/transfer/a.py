from suvat import *
from typing import Union

def nearestNode(absolute, nodeSep):
    yCo = absolute[0]//nodeSep
    return (int(yCo), int(absolute[1]//nodeSep)) #new equation! multiply g by 2 in all equations

def getPointsAcrossCurve(u, g, maxXSpeed, nodeSep, direction, dirEffect):
    numOfPoints = round(10 * (maxXSpeed/20))
    points = []

    g = -abs(g)

    solutions = [solveS(u, g/2, point=0, direction="l"), solveS(u, g/2, point=0, direction="r")]
    if direction == "l":
        solutions[1] = abs(solutions[1])
    else:
        solutions[0] = abs(solutions[0])
    tStep = dirEffect * (solutions[1] - solutions[0])/numOfPoints
    t = 0

    for x in range(numOfPoints + 1):
        points.append(nearestNode(absolute=(s(u, g, t), maxXSpeed * t), nodeSep=nodeSep))
        t += tStep
    
    buffer = []
    for point in points:
        if point not in buffer:
            buffer.append(point)
    
    return buffer

def jumpOffEdge(u, g, maxXSpeed, origin, nodeMap, nodeSep, direction):
    if direction == "l":
        dirEffect = -1
    else:
        dirEffect = 1

    u = dirEffect * abs(u)
    g = -abs(g)

    points = getPointsAcrossCurve(u, g, maxXSpeed, nodeSep, direction, dirEffect)

    topNodes = []

    hitRoof = False
    hitWall = False
    roofNode = (0,0)
    for pointIndex in range(0, len(points)):
        points[pointIndex] = (origin[0] - points[pointIndex][0], points[pointIndex][1] + origin[1])
    for point in points:
        if not hitRoof and not hitWall and point[0] in range(0, len(nodeMap)) and point[1] in range(0, len(nodeMap[0])):
            currentNodeData = nodeMap[point[0]][point[1]]
            if currentNodeData != " " and nodeMap[point[0] + 1][point[1]] == " " and v(u=u, g=g, t=solveS(u=u, g=g, point=point[0], direction=direction)) >= 0:
                hitRoof = True
                roofNode = (point[0] + 1, point[1])
                topNodes.append((point[0] + 1, point[1]))
            elif currentNodeData != " " and (((nodeMap[point[0] + 1][point[1]] == " " and nodeMap[point[0] - 1][point[1]]) == " " and (nodeMap[point[0]][point[1]] != " " or nodeMap[point[0]][point[1]] != " ")) or nodeMap[point[0] + 1][point[1]] != " " or nodeMap[point[0] - 1][point[1]] != " "):
                hitWall = True
            elif not point in topNodes:
                topNodes.append(point)
    
    if hitRoof:
        u *= -1
        index = points.index((roofNode[0] - 1, roofNode[1]))
        buffer = []
        while index >= 0:
            if index == points.index((roofNode[0] - 1, roofNode[1])):
                buffer.append((points[index][0] + 1, points[index][1]))
            else:
                buffer.append(points[index])
            index -= 1
        points = list(tuple(buffer))
        for point in points:
            yDiff = abs(roofNode[0] - point[0])
            xDiff = dirEffect * abs(roofNode[1] - point[1])
            newPoint = (roofNode[0] + yDiff, roofNode[1] + xDiff)
            if not newPoint in topNodes:
                topNodes.append(newPoint)

    return topNodes

def findLowerNodes(topNodes, nodeMap) -> tuple[list[tuple], list[tuple]]:
    foundNodes = []
    floorNodes = []

    while len(topNodes) != 0:
        buffer = []
        for node in topNodes:
            currentNode = [node[0] + 1, node[1]]
            end = currentNode in topNodes or currentNode in foundNodes
            if not end:
                currentNodeData = nodeMap[currentNode[0]][currentNode[1]]
                while currentNodeData == " " and currentNode[0] in range(0, len(nodeMap)) and currentNode[1] in range(0, len(nodeMap[0])):
                    if not currentNode in foundNodes:
                        foundNodes.append((currentNode[0], currentNode[1]))
                        if node[0] - currentNode[0] % 2 == 0:
                            if currentNode[1] - 1 >= 0:
                                if nodeMap[currentNode[0]][currentNode[1] - 1] == " " and not (nodeMap[currentNode[0]][currentNode[1] - 1] in foundNodes or nodeMap[currentNode[0]][currentNode[1] - 1] in topNodes):
                                    buffer.append((currentNode[0], currentNode[1] - 1))
                            if currentNode[1] + 1 <= len(nodeMap[currentNode[0]]):
                                if nodeMap[currentNode[0]][currentNode[1] + 1] == " " and not (nodeMap[currentNode[0]][currentNode[1] + 1] in foundNodes or nodeMap[currentNode[0]][currentNode[1] + 1] in topNodes):
                                    buffer.append((currentNode[0], currentNode[1] + 1))
                    currentNode[0] += 1
                    currentNodeData = nodeMap[currentNode[0]][currentNode[1]]
                currentNode[0] -= 1
            #if not tuple(currentNode) == node:
            floorNodes.append((currentNode[0], currentNode[1], "ground"))
        for node in topNodes:
            if not (node[0], node[1], None) in foundNodes and not (node[0], node[1], "ground") in foundNodes:
                foundNodes.append((node[0], node[1], None))
        topNodes = list(tuple(buffer))

    return (foundNodes, floorNodes)

def traverseFloor(nodeMap, jumpForceInNodes, origin):
    step = 1
    current = list(origin)
    foundNodes = []
    newFloors = []
    corners = []

    waypoints = []
    for x in range(2):
        stop = False
        while current[0] in range(0, len(nodeMap)) and current[1] in range(0, len(nodeMap[0])) and not stop:
            previousCollisionState = [False, False]
            if nodeMap[current[0]][max(0, min(len(nodeMap[current[0]]) - 1, current[1] + step))] != " " or (nodeMap[current[0]][max(0, min(len(nodeMap[current[0]]) - 1, current[1] + step))] != " " and nodeMap[current[0] - 1][max(0, min(len(nodeMap[current[0]]) - 1, current[1] + step))] == " ") or nodeMap[current[0] + 1][max(0, min(len(nodeMap[current[0]]) - 1, current[1] + step))] == " " or not current[1] + step in range(0, len(nodeMap[current[0]])): #what the fuck
                stop = True
                corners.append((current[0], current[1], "l" if step < 0 else "r"))
            foundNodes.append((current[0], current[1], "ground"))
            stepUp = 0
            while nodeMap[max(0, current[0] - stepUp)][current[1]] == " " and current[0] - stepUp in range(0, len(nodeMap)) and stepUp <= jumpForceInNodes:
                if not nodeMap[max(0, current[0] - stepUp)][current[1]] == " " in foundNodes:
                    foundNodes.append((current[0] - stepUp, current[1], None))
                    currentCollisionState = [
                        current[1] - 1 >= 0 and nodeMap[current[0] - stepUp][max(0, current[1] - 1)] != " ", #-stepUp
                        current[1] + 1 < len(nodeMap[current[0] - stepUp]) and nodeMap[current[0] - stepUp][min(len(nodeMap[current[0] - stepUp]) - 1, current[1] + 1)] != " "
                    ]
                    if previousCollisionState[0] and not currentCollisionState[0]:
                        newFloors.append((current[0] - stepUp, current[1] - 1, "ground", "r"))
                        waypoints.append(((current[0], current[1]), "->", (current[0] - stepUp, current[1] - 1)))
                    if previousCollisionState[1] and not currentCollisionState[1]:
                        newFloors.append((current[0] - stepUp, current[1] + 1, "ground", "l"))
                        waypoints.append(((current[0], current[1]), "->", (current[0] - stepUp, current[1] + 1)))
                    
                    previousCollisionState = list(tuple(currentCollisionState))
                    currentCollisionState = [False, False]
                stepUp += 1
            current = list(current)
            current[1] += step
        step *= -1
        current = origin
    
    return (foundNodes, corners, newFloors, waypoints)

def precompileGraph(nodeMap, nodeSep, gravityAccel, enemyData, origin):
    origin = findLowerNodes(topNodes=[origin], nodeMap=nodeMap)[1][0]
    floors = [origin]
    traversedFloors = []
    corners = []

    waypoints = []

    gravityAccel = -abs(gravityAccel)

    maxS = s(u=enemyData["jumpForce"], g=gravityAccel, t=solveV(targetV=0, u=enemyData["jumpForce"], g=gravityAccel))
    jumpHeightInNodes = maxS // nodeSep

    allNodes = []

    while len(floors) != 0:
        buffer = []

        for floor in floors:
            if not floor in traversedFloors:
                traversedFloors.append(floor)
                response = traverseFloor(nodeMap=nodeMap, jumpForceInNodes=jumpHeightInNodes, origin=floor)
                for node in response[0]:
                    if not node in allNodes:
                        allNodes.append(node)
                    if node[2] == "ground" and not node in traversedFloors:
                        traversedFloors.append(node)
                for corner in response[1]:
                    if not corner in corners:
                        corners.append(corner)
                for newFloor in response[2]:
                    if not newFloor in traversedFloors:
                        buffer.append((newFloor[0], newFloor[1], newFloor[2]))
                        corners.append((newFloor[0], newFloor[1], newFloor[3]))
                for waypoint in response[3]:
                    if not waypoint in waypoints:
                        waypoints.append(waypoint)

        for corner in corners:
            topNodes = jumpOffEdge(u=enemyData["jumpForce"], g=gravityAccel, maxXSpeed=enemyData["maxSpeed"][1], origin=corner, nodeMap=nodeMap, nodeSep=nodeSep, direction=corner[2])
            response = findLowerNodes(topNodes=topNodes, nodeMap=nodeMap)
            for node in response[0]:
                if not node in allNodes:
                    allNodes.append(node)
            for newFloor in response[1]:
                newWaypoint = (((corner[0], corner[1]), "->", (newFloor[0], newFloor[1])))
                if not (newFloor in traversedFloors or newFloor in floors):
                    buffer.append(newFloor)
                if not newWaypoint in waypoints:
                    waypoints.append(newWaypoint)
        corners = []
        floors = list(tuple(buffer))
    
    buffer = []
    for waypoint in waypoints:
        if not waypoint[0] == waypoint[2]:
            buffer.append(waypoint)
    waypoints = list(tuple(buffer))
    buffer = []
    for waypoint in waypoints:
        if (waypoint[2], "->", waypoint[0]) in waypoints:
            buffer.append((waypoint[0], "<->", waypoint[2]))
        else:
            if not waypoint in buffer:
                buffer.append(waypoint)
    waypoints = list(tuple(buffer))
    buffer = []
    for waypoint in waypoints:
        if not (waypoint[2], waypoint[1], waypoint[0]) in buffer:
            buffer.append(waypoint)
    
    waypoints = buffer
    
    return (allNodes, waypoints)


def connectAdjacentWaypoints(waypoints: list[tuple], disconnectedWaypoints: list[tuple]):
    waypointGroups = []
    while len(disconnectedWaypoints) != 0:
        newGroup = []
        yCoord = disconnectedWaypoints[0][0] #disconnectedWaypoints => [ (pointY, pointX), ...]
        for point in disconnectedWaypoints:
            if point[0] == yCoord:
                newGroup.append(point)
        for point in newGroup:
            if point in disconnectedWaypoints:
                disconnectedWaypoints.remove(point)
        waypointGroups.append(newGroup)
    newWaypoints = []
    for group in waypointGroups:
        splitAt = [0]
        group = list(group)
        group.sort(key=lambda point: (point[1]))
        for index in range(0, len(group)):
            if index + 1 < len(group):
                if group[index][1] == group[min(len(group) - 1, index + 1)][1] - 1:
                    newWaypoints.append((group[index], "<->", group[index + 1]))
                else:
                    splitAt.append(index)
        splitAt.append(len(group) - 1)
        if len(splitAt) > 2:
            ignoreNext = False
            for splitIndex in range(0, len(splitAt)):
                if not (splitIndex == 0 or splitIndex == len(splitAt) - 1):
                    if not (splitAt[splitIndex - 1], "<->", splitAt[splitIndex]) in newWaypoints and not ignoreNext:
                        newWaypoints.append((group[splitAt[splitIndex - 1]], "<->", group[splitAt[splitIndex]]))
                        ignoreNext = True
                    else:
                        ignoreNext = False
    waypoints.extend(newWaypoints)
    return waypoints


def verifyPathsFormat(paths: list[tuple[Union[tuple[int, int], str], ...]]):
    for path in paths:
        previousItem = ""
        for item in path:
            if (type(previousItem) == str and not type(item) == tuple) or (type(previousItem) == tuple and not type(item) == str):
                raise TypeError(f"WARNING: {path} DOES NOT CONFORM TO TUPLE, STR ALTERNATING RULE")
            previousItem = item
        if (not type(path[0]) == tuple) or (not type(path[len(path) - 1]) == tuple):
            raise TypeError(f"WARNING: {path} DOES NOT BEGIN AND END WITH A TUPLE")

def findPathsFromQueries(paths: list[tuple[Union[tuple[int, int], str], ...]], queries: list[tuple[int, int]]) -> list[tuple[Union[tuple[int, int], str], ...]]:
    #EACH ITEM IN PATHS SHOULD BEGIN AND END WITH A TUPLE AND ALTERNATE BETWEEN TUPLE AND STR
    verifyPathsFormat(paths=paths)
    foundPathIndexes = []
    for pathIndex in range(0, len(paths)):
        validPath = True
        for query in queries:
            if not query in paths[pathIndex]:
                validPath = False
        if validPath:
            foundPathIndexes.append(pathIndex)
    foundPaths = []
    for index in foundPathIndexes:
        foundPaths.append(paths[index])
    return foundPaths

def getTestGraph(graphID: int):
    testGraph = []
    match graphID:
        case 0:
            for x in range(6):
                testGraph.append([" " for x in range(20)])
            a = ["#" for x in range(9)]
            a += [" " for x in range(11)]
            testGraph.append(a)
            for x in range(10):
                testGraph.append([" " for x in range(20)])
            a = [" " for x in range(10)]
            a += ["#" for x in range(10)]
            testGraph.append(a)
            for x in range(2):
                testGraph.append([" " for x in range(20)])
            for x in range(1):
                testGraph.append(["#" for x in range(20)]) #stupid python
        case 1:
            for x in range(9):
                testGraph.append([" " for x in range(20)])
            a = ["#" for x in range(9)]
            a.extend(" " for x in range(3))
            a.extend("#" for x in range(8))
            testGraph.append(a)
            testGraph.append(["#" for x in range(20)])
        case 2:
            for x in range(8):
                testGraph.append([" " for x in range(20)])
            for x in range(2):
                a = [" " for x in range(12)]
                a.extend("#" for x in range(8))
                testGraph.append(a)
            a = ["#" for x in range(9)]
            a.extend(" " for x in range(3))
            a.extend("#" for x in range(8))
            testGraph.append(a)
            testGraph.append(["#" for x in range(20)])
    
    return testGraph

def main(graphID: int):
    testGraph = getTestGraph(graphID=graphID)
    
    origin = (len(testGraph) - 3, 0)

    gravityAccel = 9.81 * 15
    nodeSep = 10

    enemyData = {
        "jumpForce": 100,
        "maxSpeed": (0, 25)
    }

    response = precompileGraph(nodeMap=testGraph, nodeSep=nodeSep, gravityAccel=gravityAccel, enemyData=enemyData, origin=origin)
    allNodes = response[0]

    waypoints = response[1]

    disconnectedWaypoints = []
    for waypoint in waypoints:
        if not waypoint[0] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[0])
        if not waypoint[2] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[2])
    
    waypoints = connectAdjacentWaypoints(waypoints=waypoints, disconnectedWaypoints=disconnectedWaypoints)

    for x in allNodes:
        testGraph[x[0]][x[1]] = "x"
    for w in response[1]:
        testGraph[w[0][0]][w[0][1]] = "W"
        testGraph[w[2][0]][w[2][1]] = "W"
    for line in testGraph:
        print(line)
    print("\n")
    pass

if __name__ == "__main__":
    for x in range(2, 3):
        main(x)