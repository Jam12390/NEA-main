import math

try:
    from suvat import *
    import precompile
except:
    from Pathing.suvat import *
    import Pathing.precompile as precompile

from typing import Optional, Union

# Unlimited length stack
class Stack:
    def __init__(self) -> None:
        self.__data = []

    def push(self, newData):
        self.__data.append(newData)

    def pop(self):
        data = self.__data[len(self.__data) - 1]
        self.__data.pop()
        return data

    def peek(self):
        return self.__data[len(self.__data) - 1]

    def isEmpty(self):
        return len(self.__data) == 0


class TopDownNode:
    def __init__(self, coord, previousNode, end, shortestDistance) -> None:
        self.coord = coord # (y, x)
        self.shortestDistance = shortestDistance
        self.HEURISTIC = getHeuristic(start=coord, end=end)
        self.previousNode = previousNode
        self.nextNodes = []
        self.visited = False


def getHeuristic(start, end, axis: Optional[str] = None) -> float: # In terms of nodes
    if axis == None or not (axis == "x" or axis == "y"):
        # // This should never fail, however rarely start or end is passed as None instead of their (y, x) form
        try:
            return math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)
        except:
            # // Returning 0 as a default makes getHeuristic more consistent anyway (prioritised first in terms of heuristic)
            return 0
    else:
        # Gets the requested axis' difference in nodes
        match axis:
            case "x":
                return abs(end[1] - start[1])
            case "y":
                return abs(end[0] - start[0])
    # This code shouldn't be reachable but just in case return 0 as if an error has occurred in the try: except: statement
    return 0


def getAdjacentNodes(
    graph,
    node,
    directionalGraph: Optional[
        list[tuple[Union[tuple[int, int], str], ...]]
    ],  # nullable [ ( (y1, x1), "<->", (y2, x2) ) ]
):
    # // Null checking directionalGraph is the cleanest way of differentiating between whether
    # // directions should be used or not
    if directionalGraph != None:
        useDirections = True
    else:
        useDirections = False

    adjacentNodes = []
    if useDirections and directionalGraph != None:
        # Logic for directional graphs:

        # // queryWaypoints() works perfectly here as well
        # // I reuse it to reduce the amount of repeated code
        pathsContainingQuery = precompile.queryWaypoints(
            waypoints=directionalGraph, query=node.coord
        )
        for potentialPath in pathsContainingQuery:
            if (
                # Check if A -> B
                # // Could use if "->" in potentialPath[1], but
                # // the more specific expressions improve readability
                potentialPath == (node.coord, "->", potentialPath[2])
                or potentialPath[1] == "<->"
            ):
                # Add the node which isn't the current node to adjacentNodes
                if node.coord == potentialPath[0]:
                    adjacentNodes.append(potentialPath[2])
                else:
                    adjacentNodes.append(potentialPath[0])
            elif not node.coord in potentialPath:
                adjacentNodes.append(potentialPath[0])
    else:
        # // This is a list of tuple[bool, coord] in the form: presence => [left, right, up, down]
        presence = [  # (Exists, coord)
            (
                (node.coord[0], node.coord[1] - 1) in graph,
                (node.coord[0], node.coord[1] - 1),
            ),
            (
                (node.coord[0], node.coord[1] + 1) in graph,
                (node.coord[0], node.coord[1] + 1),
            ),
            (
                (node.coord[0] - 1, node.coord[1]) in graph,
                (node.coord[0] - 1, node.coord[1]),
            ),
            (
                (node.coord[0] + 1, node.coord[1]) in graph,
                (node.coord[0] + 1, node.coord[1]),
            ),
        ]
        for nodeIndex in range(0, len(presence)):
            if presence[nodeIndex][
                0
            ]: # // If the coordinate exists
                adjacentNodes.append(presence[nodeIndex][1])  # // Add it to the adjacentNodes
    return adjacentNodes


def getNextNodeToVisit(nodes: list[TopDownNode]) -> int:
    # Sorts in ascending order based off the sum of shortestDistance and heuristic (like A*)
    nodes.sort(key=lambda node: node.shortestDistance + node.HEURISTIC)
    index = 0
    # Iterate through nodes until we reach an out of range error or until we find one which hasn't been visited
    while nodes[min(len(nodes) - 1, index)].visited and index < len(nodes):
        index += 1

    # Check for which exit condition we triggered
    if index >= len(nodes):
        return -1 # For out of range
    return index # For unvisited node found


# // Gets the index of a TopDownNode object in a list based on a coordinate query
def getNodeFromCoord(nodes: list[TopDownNode], coord):
    for index, node in enumerate(nodes):
        if node.coord == coord:
            return index
    return -1 # Returns -1 if nothing was found


# // Recursive function which updates the shortestDistance of its target's nextNodes,
# // calling itself on each next node
def cascadeUpdate(nodes: list[TopDownNode], startNode: TopDownNode):
    for nextNode in startNode.nextNodes:
        index = getNodeFromCoord(nodes=nodes, coord=nextNode)
        nodes[index].shortestDistance = startNode.shortestDistance + 1
        nodes = cascadeUpdate(nodes=nodes, startNode=nodes[index])
    return nodes # exit condition


def getTopDownPath(
    graph,
    start,
    end,
    directionalGraph: Optional[
        list[tuple[tuple[int, int], str, tuple[int, int]]] # // directionalGraph => [((y, x), "->", (y2, x2))] | None
    ] = None, # // Defaults to None so directionalGraph=None doesn't have to be passed each time getTopDownPath is called
) -> list[tuple[int, int]]: # => [(y1, x1), (y2, x2), ...]

    # // Same reasons as getAdjacentNodes()
    if directionalGraph != None:
        useDirections = True
    else:
        useDirections = False

    nodes = list[TopDownNode](
        [TopDownNode(coord=start, shortestDistance=0, previousNode=None, end=end)]
    )
    currentNode = nodes[0] # Starting node
    path = []
    # A* ends when the end is reached any way
    while end != currentNode.coord and not end in currentNode.nextNodes:
        currentNodeIndex = getNextNodeToVisit(nodes=nodes)
        # If we've ran out of nodes to visit
        if currentNodeIndex == -1:
            # No path
            return []
        currentNode = nodes[currentNodeIndex]
        adjacentNodes = getAdjacentNodes( # // Which can be travelled to
            graph=graph, node=currentNode, directionalGraph=directionalGraph
        )
        for node in adjacentNodes:
            index = getNodeFromCoord(nodes=nodes, coord=node)
            if useDirections:
                # Add the absolute distance from A to B to the current shortestDistance
                newDistance = currentNode.shortestDistance + getHeuristic(
                    start=currentNode.coord, end=node
                )
            else:
                # Otherwise just add 1 (since in a grid each node is 1 unit apart)
                newDistance = float(currentNode.shortestDistance + 1)
            if index == -1: # TopDownNode object doesn't exist in nodes
                nodes.append( # // So create a new one for the node
                    TopDownNode(
                        coord=node,
                        previousNode=currentNode,
                        end=end,
                        shortestDistance=newDistance,
                    )
                ) 
                nodes[currentNodeIndex].nextNodes.append(node) # Add the coordinate to the currentNode's nextNodes
            elif newDistance < nodes[index].shortestDistance:
                    nodes[index].shortestDistance = newDistance
                    overriddenPreviousNodeIndex = getNodeFromCoord( # The node which used to lead to this node
                        nodes=nodes, coord=nodes[index].previousNode.coord
                    )
                    if (
                        nodes[index].coord
                        in nodes[overriddenPreviousNodeIndex].nextNodes
                    ): # Some verification to make sure the previous node still leads to this node
                        nodes[overriddenPreviousNodeIndex].nextNodes.remove( # // Since remove() returns an error if its argument isn't found
                            nodes[index].coord
                        )
                    nodes = cascadeUpdate(nodes=nodes, startNode=nodes[index]) # Cascade update the shortest distance for all previous nodes
        nodes[currentNodeIndex].visited = True # And mark this node as visited

    # Initialising the stack
    stack = Stack()
    stack.push(end)
    path.append(start)

    # Walking backwards from the end -> start
    while currentNode.coord != start:
        stack.push(currentNode.coord)
        currentNode = nodes[
            getNodeFromCoord(nodes=nodes, coord=currentNode.previousNode.coord)
        ]

    # And reversing it
    while not stack.isEmpty():
        path.append(stack.pop())

    return path

# // The time complexity of O(n^2) isn't great and could be a point to improve upon in the future
# // However, since paths tend to be short, the time complexity is closer to being linear rather than
# // a quadratic with a high n
def flattenPath(nodeMap, path):
    flattenedPath = []
    for node in path:
        currentCo = list(node)
        # While the lower node isn't a wall
        while nodeMap[min(len(nodeMap), int(currentCo[0] + 1))][
            int(currentCo[1])
        ] == " " and currentCo[0] < len(nodeMap): # Limit currentCo to nodeMap's length if there are no lower floors
            currentCo[0] += 1 # Increment row
        flattenedPath.append(tuple(currentCo))
    return flattenedPath


def pathfind(
    graph: list[tuple[int, int]],
    nodeMap: list[list[str]],
    nodeSep: int,
    start: tuple[int, int], # (y, x)
    end: tuple[int, int], # (y, x)
    waypoints: list[tuple[tuple, str, tuple]],
    disconnectedWaypoints: list[tuple[int, int]],
    jumpForce: float,
    gravity: float
):
    # // Instead of using a messy if statement to check if the start and end nodes exist in the graph,
    # // I can reuse Point's isValid() method without any impact on the big O space complexity
    rangeCheckSt = precompile.Point(x=start[1], y=start[0], nodeMap=nodeMap)
    rangeCheckEn = precompile.Point(x=end[1], y=end[0], nodeMap=nodeMap)
    if not (rangeCheckSt.isValid() and rangeCheckEn.isValid()):
        return [] # // Returns an empty (invalid) path if either point isn't valid

    try:
        start = precompile.getLowerNodes(
            topNodes=[precompile.Point(x=start[1], y=start[0], nodeMap=nodeMap)],
            nodeMap=nodeMap,
        ).FLOORNODES[0] # Both the start and end nodes should begin on the ground
    except:
        pass

    try:
        end = precompile.getLowerNodes(
            topNodes=[precompile.Point(x=end[1], y=end[0], nodeMap=nodeMap)],
            nodeMap=nodeMap,
        ).FLOORNODES[0]
    except:
        pass

    # Get the most direct path first
    absolutePath = getTopDownPath(
        graph=graph,
        start=start.getCoord(),
        end=end.getCoord(),
        directionalGraph=None,
    )
    if len(absolutePath) != 0:
        # Then flatten it to find the closest waypoint
        flattenedPath = flattenPath(nodeMap, absolutePath)
        nearestStartWaypoint = None
        nearestEndWaypoint = None
        for node in flattenedPath:
            if node in disconnectedWaypoints and nearestStartWaypoint == None:
                # Find the nearest node which is disconnectedWaypoints
                nearestStartWaypoint = node
                break # Exit the loop early to save time
        flattenedPath.reverse()
        flattenedReversePath = flattenedPath
        for node in flattenedReversePath:
            # Iterate backwards
            if node in disconnectedWaypoints and nearestEndWaypoint == None:
                # To find the nearest end waypoint
                nearestEndWaypoint = node
                break

        # Get a path of waypoints // (since it's known they can reach each other)
        waypointPath = getTopDownPath(
            graph=graph, # Unsorted list of valid nodes
            start=nearestStartWaypoint,
            end=nearestEndWaypoint,
            directionalGraph=waypoints,
        )
        finalPath = []
        if len(waypointPath) != 0 and not None in waypointPath: # Logic for if a path of waypoints exists
            # // Since it's known from precompile that waypoints connect to each other,
            # // The final path is the absolute paths of all the waypoints connected to each other

            finalPath = getTopDownPath(
                graph=graph,
                start=start.getCoord(),
                end=nearestStartWaypoint,
                directionalGraph=None,
            ) # Start with the first waypoint

            # Iterating through and connecting waypoints
            for nodeIndex in range(0, len(waypointPath) - 1):
                startWaypoint = waypointPath[nodeIndex]
                startWaypoint = (int(startWaypoint[0]), int(startWaypoint[1]))
                endWaypoint = waypointPath[nodeIndex + 1]
                endWaypoint = (int(endWaypoint[0]), int(endWaypoint[1]))
                    
                absolutePath = getTopDownPath(
                    graph=graph,
                    start=startWaypoint,
                    end=endWaypoint
                )

                # Take the lowest path whenever possible
                flattenedAbsolutePath = flattenPath(nodeMap=nodeMap, path=absolutePath)
                requiresJump = not checkGroundPathValidity(
                    flattenedPath=flattenedAbsolutePath,
                )

                # However extend the path using absolutePath if necessary
                # // This could be removed to improve performance, however its current impact is negligible
                if requiresJump and abs(endWaypoint[1] - startWaypoint[1]) > 2:
                    # // Adding a diagonal node to the path is a simple way to indicate a jump since the enemy only jumps with its max power
                    finalPath.append(startWaypoint)
                    if endWaypoint[1] - startWaypoint[1] > 0 and nodeMap[startWaypoint[0] - 1][startWaypoint[1] + 1] != "#": # Going right and the top right adjacent node is free
                        finalPath.append((startWaypoint[0] - 1, startWaypoint[1] + 1))
                    elif endWaypoint[1] - startWaypoint[1] < 0 and nodeMap[startWaypoint[0] - 1][startWaypoint[1] - 1] != "#": # Going left and the top left adjacent node is free
                        finalPath.append(tuple((startWaypoint[0] - 1, startWaypoint[1] - 1)))
                elif requiresJump:
                    finalPath.extend(absolutePath)
                else:
                    finalPath.extend(flattenedAbsolutePath)
            finalPath.extend(
                flattenPath(
                    nodeMap=nodeMap,
                    path=getTopDownPath(
                        graph=graph,
                        start=nearestEndWaypoint,
                        end=end.getCoord(),
                        directionalGraph=None,
                    ),
                )
            )
        else:
            #reversed = list(tuple(flattenedPath)) # Disconnected copy of the original flattenedPath
            #reversed.reverse() # 
            #return reversed  # if start.getCoord()[1] < end.getCoord()[1] else flattenedPath
            flattenedPath.reverse() # Unreverse the reversed flattenedPath
            return flattenedPath
        return finalPath
    else:
        return []


def canFallTowardsPoint(
    target: precompile.Point,
    gravity: float,
    maxXSpeed: float,
    origin: precompile.Point,
    nodeMap: list[list[str]],
    nodeSep: float,
    dirEffect: int,
):
    fallNodes = list[precompile.Point]( # // Casting for readability and type checking purposes
        precompile.getPointsAcrossCurve( # // Getting a parabola of points starting at the max height
            u=0,
            g=gravity,
            origin=origin,
            nodeMap=nodeMap,
            nodeSep=nodeSep,
            maxXSpeed=maxXSpeed,
            dirEffect=dirEffect,
        )
    )
    for node in fallNodes:
        # If the current node is on the same x coordinate and higher than the target, it can be fallen towards
        if target.x() == node.x() and target.y() >= node.y():
            return True
    return False

# Checks if 
#def checkGroundPathValidity(
#    jumpHeightInNodes: int, flattenedPath: list[tuple[int, int]]
#) -> bool:
#    currentIndex = 0
#    nextIndex = 1
#    for index in range(0, len(flattenedPath) - 1):
#        currentY = flattenedPath[currentIndex][0]
#        nextY = flattenedPath[nextIndex][0]
#        if currentY > nextY and currentY - nextY > jumpHeightInNodes:
#            return False
#        currentIndex += 1
#        nextIndex += 1
#    return True

# Checks if the path is reachable by only moving across the ground
def checkGroundPathValidity(
    flattenedPath: list[tuple[int, int]]
) -> bool:
    currentIndex = 0
    nextIndex = 1
    for index in range(0, len(flattenedPath) - 1):
        currentY = flattenedPath[currentIndex][0]
        nextY = flattenedPath[nextIndex][0]
        if currentY != nextY:
            return False
        currentIndex += 1
        nextIndex += 1
    return True

# Reduces code repetition and cleans messy min max statements
# Clamps a value to only being between 2 floats
def clamp(inp: float, mini: float, maxi: float, invert: bool = False):
    if invert and (inp >= maxi or inp <= mini):
        return inp
    return max(min(maxi, inp), mini)


# Finds the nearest empty node to the player
# // Going in the order: up, left, right, down
# // Returns its input as default
def findFreeNode(nodeMap, start: tuple[int, int]): # (y, x)
    start = [start[0], start[1]]
    if (
        nodeMap[clamp(start[0] - 1, 0, len(nodeMap) - 1)][
            clamp(start[1], 0, len(nodeMap[0]) - 1)
        ]
        != "#"
    ):
        return (start[0] - 1, start[1])
    elif nodeMap[clamp(start[0], 0, len(nodeMap) - 1)][
        clamp(start[1] - 1, 0, len(nodeMap[0]) - 1)
    ] != "#":
        return (start[0], start[1] - 1)
    elif nodeMap[clamp(start[0], 0, len(nodeMap) - 1)][
        clamp(start[1] - 1, 0, len(nodeMap[0]) + 1)
    ] != "#":
        return (start[0], start[1] + 1)
    elif nodeMap[clamp(start[0] + 1, 0, len(nodeMap))][
        start[1], 0, len(nodeMap[0])
    ] != "#":
        return (start[0] + 1, start[1])
    else:
        raise Exception("No free node was found.") # Triggers the try: except: in main() to return []


#def shortenPath(path):
#    index = 0
#    while index + 2 < len(path):
#        xDiff = abs(path[index + 2][1] - path[index][1])
#        yDiff = abs(path[index + 2][0] - path[index][0])
#        if xDiff >= 1 and yDiff >= 1:
#            path.pop(index + 1)
#        index += 1
#    return path

# // Removes most duplicates from the path
# // More to help with reading the debug outputs than with performance
# // Little to no performance impact
def shortenPath(path):
    index = 0
    while index + 1 < len(path): # Iterate using a while loop since we're controlling when to increment index
        if path[index] == path[index + 1]:
            path.pop(index + 1)
        else:
            index += 1 # Only increment index when an index hasn't been removed
    return path


def main(
    start: tuple[int, int], # (y, x)
    end: tuple[int, int], # (y, x)
    precompiledData: precompile.PrecompileResponse, # Class containing metadata about the graph from precompile
    nodeMap: list[list[str]], # 2D list of which coordinates are walls
    nodeSep: int,
    jumpForce: float,
    gravity: float,
):

    # Organising precompiledData
    graph = precompiledData.NODES
    waypoints = precompiledData.WAYPOINTDATA.WAYPOINTS
    disconnectedWaypoints = precompiledData.WAYPOINTDATA.DISCONNECTEDWAYPOINTS

    try:
        # Make sure start and end are free
        if nodeMap[start[0]][start[1]] != " ":
            start = findFreeNode(nodeMap=nodeMap, start=start)
        if nodeMap[end[0]][end[1]] != " ":
            end = findFreeNode(nodeMap=nodeMap, start=end)
        
        end = precompile.getLowerNodes(
            topNodes=[
                precompile.Point(x=end[1], y=end[0], nodeMap=nodeMap),
            ],
            nodeMap=nodeMap,
        ).FLOORNODES[0].getCoord() # and that end has a floor node to travel to
    except:
        return [] # Otherwise return []

    # Then run the main pathfinding algorithm
    path = pathfind(
        graph=graph,
        nodeMap=nodeMap,
        nodeSep=nodeSep,
        start=(int(start[0]), int(start[1])),
        end=(
            int(end[0]),
            int(end[1]),
        ),
        waypoints=waypoints,
        disconnectedWaypoints=list(disconnectedWaypoints),
        jumpForce=jumpForce,
        gravity=gravity,
    )

    path = shortenPath(path=path)

    return path


#testGraph = precompile.loadMap(fileName="Prototype1/transfer/Maps/a.csv", invalidKeys=[5, 6, 2, -1])
#gravityAccel = 9.81 * 15
#nodeSep = 15
#enemyData = {
#   "jumpForce": 125,
#   "maxSpeed": (100, 50)
#}
#response = precompile.precompileGraph(
#   nodeMap=testGraph,
#   nodeSep=nodeSep,
#   gravity=gravityAccel,
#   enemyData=enemyData,
#   origin=(6, 0)
#)
#debug = True
#t = time.time()
#
#if debug:
#    a = main(
#        start=(6, 0),
#        end=(2, 5),
#        precompiledData=response,
#        nodeMap=testGraph,
#        nodeSep=nodeSep,
#        jumpForce=enemyData["jumpForce"],
#        gravity=gravityAccel
#    )
#    for x in a:
#       testGraph[x[0]][x[1]] = "x"
#    for x in testGraph:
#        print(x)
#e = time.time()
#print(e - t)