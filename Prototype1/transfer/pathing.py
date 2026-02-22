import math
try:
    from transfer.suvat import *
except:
    from suvat import *
import time
try:
    import transfer.precompile as precompile
except:
    import precompile
from typing import Optional, Union

class Stack():
    def __init__(self) -> None:
        self.__data = []
    def push(self, newData):
        self.__data.append(newData)
    def pop(self):
        data = self.__data[len(self.__data)-1]
        self.__data.pop()
        return data
    def peek(self):
        return self.__data[len(self.__data)-1]
    def isEmpty(self):
        return len(self.__data) == 0

class TopDownNode():
    def __init__(self, coord, previousNode, end, shortestDistance, tolerance: float = 0) -> None:
        self.coord = coord
        self.shortestDistance = shortestDistance
        self.heuristic = getHeuristic(start=coord, end=end)
        self.previousNode = previousNode
        self.nextNodes = []
        self.visited = False

def getHeuristic(start, end, axis: Optional[str] = None) -> float:
    if axis == None or not (axis == "x" or axis=="y"):
        try:
            return math.sqrt( (start[0]-end[0])**2 + (start[1]-end[1])**2)
        except:
            return 0
    else:
        match axis:
            case "x":
                return abs(end[1] - start[1])
            case "y":
                return abs(end[0] - start[0])
    return 0


def getAdjacentNodes(graph, node, directionalGraph: Optional[list[tuple[Union[tuple[int, int], str], ...]]], debug = None):
    if directionalGraph != None:
        useDirections = True
    else:
        useDirections = False
    adjacentNodes = []
    if useDirections and directionalGraph != None:
        #pathsContainingQuery = findPathsFromQueries(paths=directionalGraph, queries=[node.coord])
        pathsContainingQuery = precompile.queryWaypoints(waypoints=directionalGraph, query=node.coord)
        for potentialPath in pathsContainingQuery:
            #if potentialPath[1] == "-":
            #    #DEBUGRESPONSE = precompile.queryWaypoints(waypoints=directionalGraph, query=potentialPath)
            #    DEBUGRESPONSE = precompile.queryCompressed(waypoints=directionalGraph, compressedWaypoint=potentialPath)
            #    for x in DEBUGRESPONSE:
            #        if not x[0] in adjacentNodes:
            #            adjacentNodes.append(x[0])
            #    #adjacentNodes.append((potentialPath[0][0], node.coord[1])) #error w. connections containing -
            if potentialPath == (node.coord, "->", potentialPath[2]) or potentialPath[1] == "<->":
                if node.coord == potentialPath[0]:
                    adjacentNodes.append(potentialPath[2])
                else:
                    adjacentNodes.append(potentialPath[0])
            elif not node.coord in potentialPath:
                adjacentNodes.append(potentialPath[0])
    else:
        presence = [ #(Exists, coord)
            ((node.coord[0], node.coord[1] - 1) in graph, (node.coord[0], node.coord[1] - 1)),
            ((node.coord[0], node.coord[1] + 1) in graph, (node.coord[0], node.coord[1] + 1)),
            ((node.coord[0] - 1, node.coord[1]) in graph, (node.coord[0] - 1, node.coord[1])),
            ((node.coord[0] + 1, node.coord[1]) in graph, (node.coord[0] + 1, node.coord[1]))
        ]
        for nodeIndex in range(0, len(presence)):
            if presence[nodeIndex][0]: #if coord exists in the graph and is reachable by an optional directionalGraph
                adjacentNodes.append(presence[nodeIndex][1]) #add coord to valid
    return adjacentNodes

def getNextNodeToVisit(nodes: list[TopDownNode], start: Optional[TopDownNode] = None, preferDirection: Optional[str] = None) -> int:
    nodes.sort(key=lambda node: node.shortestDistance + node.heuristic)
    index = 0
    discouragedNodes = [] #if a direction is preferred, we need to store *possible* nodes which aren't in the direction we want in case there aren't any nodes in the preferred direction
    preferredNodeFound = False
    while (nodes[min(len(nodes) - 1, index)].visited or (preferDirection != None and not preferredNodeFound)) and index < len(nodes):
        if not nodes[min(len(nodes) - 1, index)].visited:
            discouragedNodes.append(index)
        index += 1
        #if preferredNodeFound:
        #    preferredNodeFound = False #make sure a preferred node state doesn't carry over to the next check
        #if index < len(nodes) and preferDirection in ["l", "r", "u", "d"]:
        #    if preferDirection in ["l", "r"]:
        #        offset = getHeuristic(start=start.coord, end=nodes[index].coord, axis="x")
        #    elif preferDirection in ["u", "d"]:
        #        offset = getHeuristic(start=start.coord, end=nodes[index].coord, axis="y")
        #    match preferDirection:
        #        case "l":
        #            preferredNodeFound = offset < 0
        #        case "r":
        #            preferredNodeFound = offset > 0
        #        case "u":
        #            preferredNodeFound = offset < 0
        #        case "d":
        #            preferredNodeFound = offset > 0
    
    #if not preferredNodeFound and preferDirection != None:
    #    index = discouragedNodes[0]
            
    if index >= len(nodes):
        return -1
    return index

def getNodeFromCoord(nodes: list[TopDownNode], coord):
    for index, node in enumerate(nodes):
        if node.coord == coord:
            return index
        else:
            index -= 1
    return -1

def cascadeUpdate(nodes: list[TopDownNode], startNode: TopDownNode):
    for nextNode in startNode.nextNodes:
        index = getNodeFromCoord(nodes=nodes, coord=nextNode)
        nodes[index].shortestDistance = startNode.shortestDistance + 1
        nodes = cascadeUpdate(nodes=nodes, startNode=nodes[index])
    return nodes


def getTopDownPath(graph, start, end, tolerance: int, directionalGraph: Optional[list[tuple[tuple[int, int], str, tuple[int, int]]]] = None, preferDirection: Optional[str] = None, debug = None) -> list[tuple[int, int]]: #directionalGraph => [((y, x), "->", (y2, x2))] | None
    if directionalGraph != None:
        useDirections = True
    else:
        useDirections = False

    nodes = list[TopDownNode]([
        TopDownNode(
            coord=start,
            shortestDistance=0,
            previousNode=None,
            end=end
        )
    ])
    currentNode = nodes[0]
    path = []
    while end != currentNode.coord and not end in currentNode.nextNodes:
        if preferDirection == None:
            currentNodeIndex = getNextNodeToVisit(nodes=nodes)
        else:
            currentNodeIndex = getNextNodeToVisit(nodes=nodes, start=nodes[0], preferDirection=preferDirection)
        if currentNodeIndex == -1:
            nodes.sort(key=lambda x: x.heuristic) #list(set()) is causing invalid path alongside extra elif, idfk why figure it out
            return []
        currentNode = nodes[currentNodeIndex]
        adjacentNodes = getAdjacentNodes(graph=graph, node=currentNode, directionalGraph=directionalGraph, debug=debug)
        for node in adjacentNodes:
            index = getNodeFromCoord(nodes=nodes, coord=node)
            if useDirections:
                newDistance = currentNode.shortestDistance + getHeuristic(start=currentNode.coord, end=node)
            else:
                newDistance = float(currentNode.shortestDistance + 1)
            if index == -1:
                nodes.append(TopDownNode(
                    coord=node,
                    previousNode=currentNode,
                    end=end,
                    shortestDistance=newDistance
                )) #continue here with cascade updating
                nodes[currentNodeIndex].nextNodes.append(node)
            else:
                if newDistance < nodes[index].shortestDistance and abs(newDistance - nodes[index].shortestDistance) > tolerance:
                    nodes[index].shortestDistance = newDistance
                    overriddenPreviousNodeIndex = getNodeFromCoord(nodes=nodes, coord=nodes[index].previousNode.coord)
                    if nodes[index].coord in nodes[overriddenPreviousNodeIndex].nextNodes:
                        nodes[overriddenPreviousNodeIndex].nextNodes.remove(nodes[index].coord)
                    nodes = cascadeUpdate(nodes=nodes, startNode=nodes[index])
        nodes[currentNodeIndex].visited = True
    

    stack = Stack()
    stack.push(end)
    path.append(start)
    while currentNode.coord != start:
        stack.push(currentNode.coord)
        currentNode = nodes[getNodeFromCoord(nodes=nodes, coord=currentNode.previousNode.coord)] #I KNOW THIS IS AN ERROR, IT WONT LET ME SPECIFY THE TYPE TO REMOVE THE ERROR DDD:
    while not stack.isEmpty():
        path.append(stack.pop())
    
    return path

def flattenPath(nodeMap, path):
    flattenedPath = []
    for node in path:
        currentCo = list(node)
        while nodeMap[int(currentCo[0] + 1)][int(currentCo[1])] == " ":
            currentCo[0] += 1
        flattenedPath.append(tuple(currentCo))
    return flattenedPath

def pathfind(
        graph: list[tuple[int, int]],
        nodeMap: list[list[str]],
        nodeSep: int,
        start: tuple[int, int],
        end: tuple[int, int],
        tolerance: int,
        waypoints: list[tuple[tuple, str, tuple]],
        disconnectedWaypoints: list[tuple[int, int]],
        jumpForce: float,
        maxXSpeed: float,
        gravity: float,
        debug = None
    ):
    rangeCheckSt = precompile.Point(
        x=start[1],
        y=start[0],
        nodeMap=nodeMap
    )
    rangeCheckEn = precompile.Point(
        x=end[1],
        y=end[0],
        nodeMap=nodeMap
    )
    if not (rangeCheckSt.isValid() and rangeCheckEn.isValid()):
        return []

    start = precompile.getLowerNodes(
        topNodes=[precompile.Point(
            x=start[1],
            y=start[0],
            nodeMap=nodeMap
        )],
        nodeMap=nodeMap
    )["floorNodes"][0]

    end = precompile.getLowerNodes(
        topNodes=[precompile.Point(
            x=end[1],
            y=end[0],
            nodeMap=nodeMap
        )],
        nodeMap=nodeMap
    )["floorNodes"][0]
    #end = end[len(end) - 1]

    #start = (start[0], start[1])
    #end = (end[0], end[1])

    absolutePath = getTopDownPath( #for some reason
        graph=graph,
        start=start.getCoord(),
        end=end.getCoord(),
        tolerance=tolerance,
        directionalGraph=None
    )
    if len(absolutePath) != 0:
        flattenedPath = flattenPath(nodeMap, absolutePath)
        nearestStartWaypoint = None
        nearestEndWaypoint = None
        for node in flattenedPath:
            if node in disconnectedWaypoints and nearestStartWaypoint == None:
                nearestStartWaypoint = node
                break
        flattenedPath.reverse()
        flattenedReversePath = flattenedPath
        for node in flattenedReversePath:
            if node in disconnectedWaypoints and nearestEndWaypoint == None:
                nearestEndWaypoint = node
                break
            
        waypointPath = getTopDownPath(graph=graph, start=nearestStartWaypoint, end=nearestEndWaypoint, tolerance=tolerance, directionalGraph=waypoints)#preferDirection="d")
        finalPath = []
        if len(waypointPath) != 0 and not None in waypointPath:
            finalPath = getTopDownPath(graph=graph, start=start.getCoord(), end=nearestStartWaypoint, tolerance=tolerance, directionalGraph=None)
            jumpHeight = abs(s(
                    u=jumpForce,
                    g=gravity,
                    t=solveV(
                        targetV=0,
                        u=jumpForce,
                        g=gravity
                    )
                ))
            jumpHeightInNodes = jumpHeight // nodeSep
            for nodeIndex in range(0, len(waypointPath) - 1):
                if len(finalPath) != 0:
                    finalPath.pop(len(finalPath) - 1)
                absolutePath = getTopDownPath(
                    graph=graph,
                    start=waypointPath[nodeIndex],
                    end=waypointPath[nodeIndex + 1],
                    tolerance=0
                )
                flattenedAbsolutePath = flattenPath(
                    nodeMap=nodeMap,
                    path=absolutePath
                )
                requiresJump = not checkGroundPathValidity(
                    jumpHeightInNodes=jumpHeightInNodes,
                    flattenedPath=flattenedAbsolutePath
                )

                #if requiresJump:
                #    downNode = None
                #    upNode = None
#
                #    for nodeIndex in range(0, len(flattenedAbsolutePath) - 1):
                #        if nodeIndex > 0:
                #            if 

                if requiresJump:
                    finalPath.extend(absolutePath)
                    #count = 0
                    #intermediatePoint = None
                    #temp, intermediatePoint = waypointJump(
                    #    start=waypointPath[nodeIndex],
                    #    end=waypointPath[nodeIndex + 1],
                    #    nodeMap=nodeMap,
                    #    jumpForce=jumpForce,
                    #    maxXSpeed=maxXSpeed,
                    #    gravity=gravity,
                    #    nodeSep=nodeSep,
                    #    graph=graph,
                    #    jumpHeightInNodes=jumpHeightInNodes
                    #)
                    #count -= 1
                    #intermediatePath = getTopDownPath(
                    #    graph=graph,
                    #    start=waypointPath[nodeIndex],
                    #    end=intermediatePoint.getCoord(),
                    #    tolerance=0
                    #)
                    #pathFromIntermediatePoint = getTopDownPath(
                    #    graph=graph,
                    #    start=intermediatePoint.getCoord(),
                    #    end=waypointPath[nodeIndex + 1],
                    #    tolerance=0
                    #)
                    #finalPath.extend(intermediatePath)
                    #finalPath.extend(pathFromIntermediatePoint)
                else:
                    finalPath.extend(flattenedAbsolutePath)



                #if requiresJump:
                #    if waypointPath[nodeIndex][1] < waypointPath[nodeIndex + 1][1]:
                #        preferredDirection = "r"
                #    elif waypointPath[nodeIndex][1] > waypointPath[nodeIndex + 1][1]:
                #        preferredDirection = "l"
                #    else:
                #        preferredDirection = None
                #    jumpHeight = abs(s(
                #        u=jumpForce,
                #        g=gravity,
                #        t=solveV(
                #            targetV=0,
                #            u=jumpForce,
                #            g=gravity
                #        )
                #    ))
                #    #jumpHeightInNodes = jumpHeight // nodeSep
                #    #jumpPath = getTopDownPath(graph=graph, start=waypointPath[nodeIndex], end=intermediatePoint.getCoord(), tolerance=tolerance, directionalGraph=None)
                #    #jumpPath.extend(getTopDownPath(graph=graph, start=intermediatePoint.getCoord(), end=waypointPath[nodeIndex + 1], tolerance=tolerance, directionalGraph=None, preferDirection=preferredDirection))
                #    #flattenedJumpPath = flattenPath(nodeMap=nodeMap, path=jumpPath)
                #    #finalPath.extend(comparePaths(flattenedPath=flattenedJumpPath, jumpPath=jumpPath, jumpHeightInNodes=jumpHeightInNodes))
                #    finalPath.extend(getTopDownPath(graph=graph, start=waypointPath[nodeIndex], end=intermediatePoint.getCoord(), tolerance=0, directionalGraph=None))
                #    finalPath.extend(getTopDownPath(graph=graph, start=intermediatePoint.getCoord(), end=waypointPath[nodeIndex + 1], tolerance=0, directionalGraph=None))#, preferDirection=preferredDirection))
                #else:
                #    finalPath.extend(getTopDownPath(graph=graph, start=waypointPath[nodeIndex], end=waypointPath[nodeIndex + 1], tolerance=tolerance, directionalGraph=None))
            finalPath.extend(getTopDownPath(graph=graph, start=nearestEndWaypoint, end=end.getCoord(), tolerance=tolerance, directionalGraph=None))
        else:
            reversed = list(tuple(flattenedPath))
            reversed.reverse()
            return reversed# if start.getCoord()[1] < end.getCoord()[1] else flattenedPath
        return finalPath
    else:
        return []

def comparePaths(
        flattenedPath,
        jumpPath,
        jumpHeightInNodes
):
    currentIndex = 0
    nextIndex = 1

    cleanFlatPath = []
    for x in flattenedPath:
        if not x in cleanFlatPath:
            cleanFlatPath.append(x)
    flattenedPath = cleanFlatPath

    for x in range(len(flattenedPath) - 1):
        if abs(flattenedPath[currentIndex][0] - flattenedPath[nextIndex][1]) > jumpHeightInNodes:
            return jumpPath
    
    if len(flattenedPath) <= len(jumpPath):
        return flattenedPath
    else:
        return jumpPath

def waypointJump( #(21, 27), (18, 25)
        start: tuple[int, int],
        end: tuple[int, int],
        nodeMap: list[list[str]],
        jumpForce: float,
        maxXSpeed: float,
        gravity: float,
        nodeSep: int,
        graph,
        jumpHeightInNodes
):
    start = precompile.Point(
        x=start[1],
        y=start[0],
        nodeMap=nodeMap
    )
    end = precompile.Point(
        x=end[1],
        y=end[0],
        nodeMap=nodeMap
    )

    if not (start.isValid() and end.isValid()):
        return False, None
    #traversableByGround = precompile.attemptGroundTraversal(
    #    start=start.getCoord(),
    #    end=end.getCoord(),
    #    nodeMap=nodeMap
    #)
    traversableByGround = False
    if traversableByGround:
        return False, None
    if abs(start.x() - end.x()) < 1:
        return False, None
    
    gradient = -abs(end.y() - start.y()) / abs(end.x() - start.x())
    if gradient <= -abs(gravity / maxXSpeed):
        return False, None
    
    if start.x() < end.x():
        dirEffect = 1
    else:
        dirEffect = -1
    #tempStart = precompile.Point(
    #    x=start.x() + dirEffect,
    #    y=start.y(),
    #    nodeMap=nodeMap
    #)
    #if not tempStart.isEmpty():
    #    tempStart = start
    tempStart = start
    topNodes = precompile.getPointsAcrossCurve(
        u=jumpForce,
        g=gravity,
        maxXSpeed=maxXSpeed,
        origin=tempStart,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        dirEffect=dirEffect,
        solveForMax=False,#True
    )
    topNodes[0].setY(topNodes[0].y() + dirEffect)
    currentNode = 0
    exceededRange = currentNode > len(topNodes) - 1
    foundIntermediatePoint = False
    while not (exceededRange or foundIntermediatePoint):
        foundIntermediatePoint = canFallTowardsPoint(
            target=end,
            gravity=gravity,
            maxXSpeed=maxXSpeed,
            origin=topNodes[currentNode],
            nodeMap=nodeMap,
            nodeSep=nodeSep,
            dirEffect=dirEffect,
            graph=graph,
            jumpHeightInNodes=jumpHeightInNodes
        )
        currentNode += 1
        exceededRange = currentNode > len(topNodes) - 1
    if exceededRange and not foundIntermediatePoint:
        return False, None
    return True, topNodes[currentNode - 1]
    
def canFallTowardsPoint(
        target: precompile.Point,
        gravity: float,
        maxXSpeed: float,
        origin: precompile.Point,
        nodeMap: list[list[str]],
        nodeSep: float,
        dirEffect: int,
        graph,
        jumpHeightInNodes
):
    fallNodes = list[precompile.Point](precompile.getPointsAcrossCurve(
        u=0,
        g=gravity,
        origin=origin,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        maxXSpeed=maxXSpeed,
        dirEffect=dirEffect
    ))
    for node in fallNodes:
        if target.x() == node.x() and target.y() >= node.y():
            return True
    return False

def checkGroundPathValidity(
        jumpHeightInNodes: int,
        flattenedPath: list[tuple[int, int]]
) -> bool:
    currentIndex = 0
    nextIndex = 1
    for index in range(0, len(flattenedPath) - 1):
        currentY = flattenedPath[currentIndex][0]
        nextY = flattenedPath[nextIndex][0]
        if (currentY > nextY and currentY - nextY > jumpHeightInNodes):
            return False
        currentIndex += 1
        nextIndex += 1
    return True
    

'''
New idea:
Instead of frankensteining w path of waypoints
what if i instead used the flattened path in combination with my initial idea of tracking the upward and downward movement of the path, only using waypoint paths when the path goes down then up
where it can't directly jump up
i could then move backwards x number of times, tracking where the path goes up as an increment of x and checking for a waypoint path from the corner where the path goes up
this should increase efficiency (since the initial path doesn't go wasted)
and solve my problem of jumping when not required

TODO:
1. Get flattened path
2. Iterate through the list, tracking where the path goes down then up
3. For each pair where the path goes down then up, find a waypoint path between the 2 and use the already in place waypointJump function to bridge the gap
4. Remove the previous intermediate path and insert the fresh one
'''

def clamp(
        inp: float,
        mini: float,
        maxi: float
):
    return max(mini, min(inp, maxi))

def findFreeNode(
        nodeMap,
        start: tuple[int, int] #(y, x)
):
    start = [start[0], start[1]]
    if nodeMap[clamp(start[0] - 1, 0, len(nodeMap)-1)][clamp(start[1], 0, len(nodeMap[0])-1)] != "#":
        return (start[0] - 1, start[1])
    if nodeMap[clamp(start[0], 0, len(nodeMap)-1)][clamp(start[1] - 1, 0, len(nodeMap[0])-1)]:
        return (start[0], start[1] - 1)
    if nodeMap[clamp(start[0], 0, len(nodeMap)-1)][clamp(start[1] - 1, 0, len(nodeMap[0])+1)]:
        return (start[0], start[1] + 1)
    #while start[0] > 0 and nodeMap[clamp(start[0], 0, len(nodeMap)-1)][clamp(start[1], 0, len(nodeMap[0])-1)] == "#":
    #    start[0] -= 1
    return tuple(start)

def shortenPath(path, nodeMap):
    index = 0
    while index + 2 < len(path):
        xDiff = abs(path[index + 2][1] - path[index][1])
        yDiff = abs(path[index + 2][0] - path[index][0])
        if xDiff == 1 and yDiff == 1 and nodeMap[path[index][0] - 1][path[index][1]] != "#":# and nodeMap[path[index][0]][path[index][1] + 1] != "#" and nodeMap[path[index][0]][path[index][1] - 1] != "#":
            path.pop(index + 1)
        index += 1
    return path

def main(
        start: tuple[int, int],
        end: tuple[int, int],
        precompiledData: dict[str, list],
        nodeMap: list[list[str]],
        nodeSep: int,
        jumpForce: float,
        maxXSpeed: float,
        gravity: float
):    

    #start = (29, 80)
    #end = (18, 38)

    graph = precompiledData["nodes"]

    waypoints = precompiledData["waypointData"]["waypoints"]
    #awaypoints = precompiledData["waypointData"]["debug"]
    disconnectedWaypoints = precompiledData["waypointData"]["disconnectedWaypoints"]

    start = findFreeNode(
        nodeMap=nodeMap,
        start=start
    )

    end = findFreeNode(
        nodeMap=nodeMap,
        start=end
    )
    print(f"end - {end}")
    end = precompile.getLowerNodes(
        topNodes=[
            precompile.Point(
                x=end[1],
                y=end[0],
                nodeMap=nodeMap
            ),
        ],
        nodeMap=nodeMap
    )["floorNodes"][0].getCoord()

    #print(f"{start} -> {end}")
    path = pathfind(
        graph=graph,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        start=(int(start[0]), int(start[1])),
        end=(int(end[0]), int(end[1])), #check for if path wraps around vertically using obj.previousNode and compare if the current previous node is on the same or lower y axis and that "d" is preferred as a direction
        tolerance=0,
        waypoints=waypoints,
        disconnectedWaypoints=list(disconnectedWaypoints),
        jumpForce=jumpForce,
        maxXSpeed=maxXSpeed,
        gravity=gravity
    )

    path = shortenPath(
        path=path,
        nodeMap=testGraph
    )

    #return path

    for x in path:
        testGraph[x[0]][x[1]] = "x"
    for line in testGraph:
        print(line)
    if path == []:
        print("Invalid Path")
    print("\n")

    return path

#startTestSet = [
#    (29, 80),
#    (14, 0),
#    (18, 38),
#    (18, 38)
#]
#endTestSet = [
#    (18, 38),
#    (29, 0),
#    (18, 41),
#    (20, 5)
#]
#

testGraph = precompile.loadMap(fileName="Prototype1/transfer/Maps/testMapMove6.csv")

gravityAccel = 9.81 * 15
nodeSep = 15

enemyData = {
    "jumpForce": 100,
    "maxSpeed": (100, 50)
}

response = precompile.precompileGraph(
    nodeMap=testGraph,
    nodeSep=nodeSep,
    gravity=gravityAccel,
    enemyData=enemyData,
    origin=(16, 0)
)

debug = True
t = time.time()

if debug:
    main(
        start=(16, 6),
        end=(12, 18),
        precompiledData=response,
        nodeMap=testGraph,
        nodeSep=nodeSep,
        jumpForce=enemyData["jumpForce"],
        maxXSpeed=enemyData["maxSpeed"][1],
        gravity=gravityAccel
    )
e = time.time()
print(e - t)