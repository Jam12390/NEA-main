try:
    import transfer.suvat as suvat
except:
    import suvat
import csv
import time


class Point:
    def __init__(self, x: int, y: int, nodeMap: list[list[str]]) -> None:
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

    # Checks if the coordinate is within the bounds of the graph
    def isValid(self) -> bool:
        if self.__x in range(len(self.__nodeMap[0])) and self.__y in range(
            0, len(self.__nodeMap)
        ):
            return True
        return False

    # Setter - data
    def __updateData(self) -> None:
        if self.isValid():
            self.data = self.__nodeMap[int(self.__y)][int(self.__x)]

    # Getter - x
    def x(self) -> int:
        return self.__x

    # Setter - x
    def setX(self, newX: int) -> None:
        self.__x = newX
        self.__updateData()

    # Getter - y
    def y(self) -> int:
        return self.__y

    # Setter - y
    def setY(self, newY: int) -> None:
        self.__y = newY
        self.__updateData()

    # Getter - Coord
    def getCoord(self) -> tuple[int, int]:
        return (self.__y, self.__x)

    # Setter - Coord
    def setCoord(self, newX: int, newY: int) -> None:
        self.__y = newY
        self.__x = newX
        self.__updateData()


# // Classes of constant values made to organise the responses of functions like traverseFloor() and getLowerNodes()
class FloorResponse():
    def __init__(self, nodes: list[Point], corners: list[Point], newFloors: list[Point], waypoints: list[tuple[tuple[int, int], str, tuple[int, int]]]):
        self.NODES = nodes
        self.CORNERS = corners
        self.NEWFLOORS = newFloors
        self.WAYPOINTS = waypoints

class LowerNodesResponse():
    def __init__(self, nodes: list[Point], floorNodes: list[Point]):
        self.NODES = nodes
        self.FLOORNODES = floorNodes

class CompiledWaypointResponse():
    def __init__(self, waypoints: list[tuple[tuple[int, int], str, tuple[int, int]]], disconnectedWaypoints: tuple[int, int]):
        self.WAYPOINTS = waypoints
        self.DISCONNECTEDWAYPOINTS = disconnectedWaypoints

class PrecompileResponse():
    def __init__(self, nodes: tuple[int, int], waypointData: CompiledWaypointResponse):
        self.NODES = nodes
        self.WAYPOINTDATA = waypointData

# Conversion to node terms
def nearestNode(absolute: tuple[float, float], nodeSep: int) -> tuple[int, int]:
    yCo = absolute[0] // nodeSep
    return (int(yCo), int(absolute[1] // nodeSep))

# Checks if a Point is in a list of Point objects
def inList(query: Point, ls: list[Point]) -> bool:
    if len(ls) > 0:
        for item in ls:
            if item.getCoord() == query.getCoord():
                return True
    return False

# Gets the index of a Point object in a list of Point objects
def find(query: Point, ls: list[Point]) -> int:
    for index in range(0, len(ls)):
        if ls[index].getCoord() == query.getCoord():
            return index
    return -1


# Gets a list of points along a parabola
def getPointsAcrossCurve(
    u: float,
    g: float,
    maxXSpeed: float,
    origin: Point,
    nodeMap: list[list[str]],
    nodeSep: int,
    dirEffect: int,
    solveForMax: bool = False,
    solvePastMax: bool = False,
) -> list[Point]:
    # // Accuracy is the number of points gotten across the curve
    # // Any formula used by future developers (based on speed) would be put within the round statement
    accuracy = round(maxXSpeed)
    points = []

    g = -abs(g) # Forces g to be negative

    roots = [
        suvat.solveS(u=u, g=g, point=0, direction="l"),
        suvat.solveS(u=u, g=g, point=0, direction="r"),
    ]
    # roots.remove(0)
    maxima = suvat.solveV(targetV=0, u=u, g=g) # Max height

    # endPoint = roots[0] * 2
    t = 0
    hitHash = False # => hitWall

    if not solveForMax: # Default logic
        tStep = dirEffect / accuracy
        while not hitHash: # The function stops when it hits a wall
            coord = nearestNode(
                absolute=(suvat.s(u=u, g=g, t=abs(t)), maxXSpeed * t), # s = ut + 0.5at^2, a = g
                nodeSep=nodeSep,
            ) # Convert a point across the curve into being in terms of nodes
            # Offset it by the opposite of its origin so it aligns with the curve on the graph
            coord = (origin.y() - coord[0], origin.x() + coord[1])
            currentPoint = Point(x=coord[1], y=coord[0], nodeMap=nodeMap) # And convert it into a Point object
            if currentPoint.isEmpty() and currentPoint.isValid(): # So we can use the inbuild isEmpty and isValid methods
                points.append(coord) # If the point is empty and in the graph
            else:
                hitHash = True # Otherwise stop
            t += tStep # Increment t by (1 / accuracy)
    elif solvePastMax: # From maxima onwards - // Used for fallTowardsPoint() in pathing.py
        tStep = dirEffect * (maxima / accuracy)
        t = maxima
        coord = Point(x=origin.x(), y=origin.y(), nodeMap=nodeMap)
        while not hitHash and coord.isValid():
            # // The same logic is used here as before
            coord = nearestNode(
                absolute=(suvat.s(u=u, g=g, t=abs(t)), maxXSpeed * (t - maxima)),
                nodeSep=nodeSep,
            )
            coord = (origin.y() - coord[0], origin.x() + coord[1])
            currentPoint = origin.y() - coord[0], origin.x() + coord[1]
            currentPoint = Point(x=coord[1], y=coord[0], nodeMap=nodeMap)
            if currentPoint.isEmpty() and currentPoint.isValid():
                points.append(coord)
            else:
                hitHash = True
            t += tStep
    else: # Solve for max
        tStep = dirEffect * (maxima / accuracy)
        while (
            t <= abs(maxima) and not hitHash
        ):  # t in range(-abs(maxima), abs(maxima)) and not hitHash:
            # Same logic here, but with an extra exit condition when t > max
            coord = nearestNode(
                absolute=(suvat.s(u=u, g=g, t=abs(t)), maxXSpeed * t),
                nodeSep=nodeSep,
            )
            coord = (origin.y() - coord[0], origin.x() + coord[1])
            currentPoint = Point(x=coord[1], y=coord[0], nodeMap=nodeMap)
            if currentPoint.isEmpty() and currentPoint.isValid():
                points.append(coord)
            else:
                hitHash = True
            t += tStep

    uniquePoints = []
    for point in points:
        if not point in uniquePoints:  # Removing duplicates
            uniquePoints.append(point)

    for pointIndex in range(0, len(uniquePoints)):
        uniquePoints[pointIndex] = (
            Point(  # Converting each unique point to a Point object
                x=uniquePoints[pointIndex][
                    1
                ],  # uniquePoints[pointIndex] => [y, x] origin.x() +
                y=uniquePoints[pointIndex][0],  # origin.y() -
                nodeMap=nodeMap,
            )
        )

    return uniquePoints


def jumpOffEdge(
    jumpForce: float,
    gravity: float,
    maxXSpeed: float,
    origin: Point,
    nodeMap: list[list[str]],
    nodeSep: int,
    direction: str,
) -> list[Point]:
    if direction == "l":
        dirEffect = -1 # Effect on X travel
    else:
        dirEffect = 1

    parabolaPoints = list[Point](
        getPointsAcrossCurve(
            u=jumpForce,
            g=gravity,
            maxXSpeed=maxXSpeed,
            origin=origin,
            nodeMap=nodeMap,
            nodeSep=nodeSep,
            dirEffect=dirEffect,
        )
    )
    topNodes = list[Point]([])

    hitRoof = False
    hitWall = False
    hitFloor = False
    roofNode = None

    for currentNode in parabolaPoints:
        # Until something happens
        if not (hitRoof or hitWall or hitFloor) and currentNode.isValid():
            # Get the upper, lower and adjacent nodes
            upperNode = Point(x=currentNode.x(), y=currentNode.y() - 1, nodeMap=nodeMap)
            lowerNode = Point(x=currentNode.x(), y=currentNode.y() + 1, nodeMap=nodeMap)
            adjacentNode = Point(
                x=currentNode.x() + 1 * dirEffect, y=currentNode.y(), nodeMap=nodeMap
            )

            # And the velocity
            yVelocity = suvat.v(
                u=jumpForce,
                g=gravity,
                t=suvat.solveS(
                    u=jumpForce, g=gravity, point=currentNode.y(), direction=direction
                ), # solveS -> t
            )

            # // If we're travelling up, the currentNode is a wall and the lower node is free
            if not currentNode.isEmpty() and lowerNode.isEmpty() and yVelocity >= 0:
                hitRoof = True # // Then we've hit a roof
                roofNode = Point(x=lowerNode.x(), y=lowerNode.y(), nodeMap=nodeMap) # Mark the lowerNode as the reversal point for the parabola
                topNodes.append(lowerNode)
            elif not currentNode.isEmpty() and upperNode.isEmpty():
                hitFloor = True
            elif not currentNode.isEmpty() and adjacentNode.isEmpty():
                hitWall = True
            elif not currentNode in topNodes:
                topNodes.append(currentNode)

    if hitRoof:
        # // Parabolas are symmetrical, therefore we can just reverse the points up to the roofNode and append them
        reverseAt = find(query=roofNode, ls=parabolaPoints)
        listSegment = [parabolaPoints[index] for index in range(0, reverseAt)]
        listSegment.reverse()

        for reversedPoint in listSegment:
            # Get the x and y difference between the current point and the roof node
            # // Note: abs() is used on the x axis since x's direction is ambiguous whereas y's
            # // direction can only be down after a roof node
            xDiff = dirEffect * abs(roofNode.x() - reversedPoint.x())
            yDiff = abs(roofNode.y() - reversedPoint.y())
            newPoint = Point( # Add the new point as if it continued from the roofNode
                x=roofNode.x() + xDiff, y=roofNode.y() + yDiff, nodeMap=nodeMap
            )
            if not newPoint in topNodes: # Provided it isn't already present
                topNodes.append(newPoint)

    return topNodes


# Debug function: Gets all unique coordinates from a list of points
def getAllCoords(ls: list[Point]):
    coords = []
    for node in ls:
        if not node.getCoord() in coords:
            coords.append(node.getCoord())
    return coords


# // Similar to jumpOffEdge, however initial velocity = 0 instead of jumpForce
def fallOffEdge(
    origin: tuple[int, int],
    gravity: float,
    maxXSpeed: float,
    nodeMap: list[list[str]],
    nodeSep: int,
    direction: str,
) -> list[Point]:
    if direction == "l": # Match direction to its effect
        dirEffect = -1
    else:
        dirEffect = 1
    origin = (origin[0], origin[1] + dirEffect)

    curve = list[Point](
        getPointsAcrossCurve(
            u=0,
            g=gravity,
            origin=Point(x=origin[1], y=origin[0], nodeMap=nodeMap),
            maxXSpeed=maxXSpeed,
            nodeMap=nodeMap,
            nodeSep=nodeSep,
            dirEffect=dirEffect,
            solveForMax=False,
            solvePastMax=True,
        )
    )

    # Remove duplicates from the curve
    cleanCurve = []
    for node in curve:
        if not node.getCoord() in cleanCurve:
            cleanCurve.append(node)
    cleanPoints = []

    # And convert them into Point objects
    for coord in cleanCurve:
        cleanPoints.append(Point(x=coord.x(), y=coord.y(), nodeMap=nodeMap))

    return cleanPoints


# // Takes a list of unique Point objects, compiling all nodes below it
# // into a list and marking the floor node from each top node
def getLowerNodes(
    topNodes: list[Point], nodeMap: list[list[str]]
) -> LowerNodesResponse:

    # Initialising variables
    foundNodes = list[Point]([])
    floorNodes = list[Point]([])

    # // Whenever a while loop is used, it's likely that we're changing the subject
    # // within the loop
    while len(topNodes) != 0:
        newTopNodes = list[Point]([])
        distanceFromTopNode = 0 # To the current node
        for node in topNodes:
            foundNodes.append(node)

            currentNode = Point(x=node.x(), y=node.y() + 1, nodeMap=nodeMap)
            # // foundNewTopNode's purpose is to stop 2 topNodes from being marked which can reach each other
            # // This reduces time spent going over nodes which have already been found
            foundNewTopNode = [False, False] # [Left, Right]
            xStep = [-1, 1] # [Left, Right]
            if not (
                inList(query=currentNode, ls=topNodes) # // Making sure not to start overlapping points
                or inList(query=currentNode, ls=foundNodes) # // and marking new topNodes which are already there
            ):
                while currentNode.isEmpty() and currentNode.isValid():
                    distanceFromTopNode += 1
                    foundNodes.append(
                        Point(x=currentNode.x(), y=currentNode.y(), nodeMap=nodeMap)
                    )
                    # // Since getPointsAcrossCurve only works to a certain degree of accuracy,
                    # // after that point, the program will only move across 1 node every n
                    # // nodes (in this case 2)
                    if distanceFromTopNode % 2 == 0: # if distanceFromTopNode % n == 0
                        for x in range(0, 2): # Do this for both left and right
                            potentialNode = Point(
                                x=currentNode.x() + xStep[x],
                                y=currentNode.y(),
                                nodeMap=nodeMap,
                            )
                            if (
                                potentialNode.isEmpty() # If the node across is empty
                                and not foundNewTopNode[max(0, xStep[x])] # And we haven't marked a new topNode for this column yet
                            ): 
                                newTopNodes.append(
                                    Point(
                                        x=potentialNode.x(),
                                        y=potentialNode.y(),
                                        nodeMap=nodeMap,
                                    )
                                ) # Mark a new top node
                                foundNewTopNode[max(0, xStep[x])] = True
                            elif not potentialNode.isEmpty(): # If the node across is a wall
                                foundNewTopNode[max(0, xStep[x])] = False # Reset foundNewTopNode for this direction
                            xStep *= 1

                    # Lower the current node
                    currentNode.setY(newY=currentNode.y() + 1)

                if not currentNode.isEmpty(): # If at any point the lower node is a wall
                    currentNode.setY(newY=currentNode.y() - 1)
                    floorNodes.append(currentNode) # Mark the upper node as a floorNode
        topNodes = list(tuple(newTopNodes))

    #return {"nodes": foundNodes, "floorNodes": floorNodes}
    return LowerNodesResponse(
        nodes=foundNodes,
        floorNodes=floorNodes
    )


# // Walks along the passed floor until the next floor node is either invalid or missing
def traverseFloor(
    nodeMap: list[list[str]], jumpForceInNodes: int, origin: Point
) -> dict[str, list]:
    # Nodes observed
    step = 1
    current = Point(x=origin.x(), y=origin.y(), nodeMap=nodeMap)
    next = Point(x=origin.x(), y=origin.y(), nodeMap=nodeMap)
    nextFloor = Point(x=origin.x(), y=origin.y(), nodeMap=nodeMap)
    foundNodes = list[Point]([])
    newFloors = list[Point]([])
    corners = list[tuple[Point, str]]([])

    waypoints = list[tuple[tuple[int, int], str, tuple[int, int]]](
        []
    )  # e.g. ( (1, 0), "->", (1, 4) )
    for x in range(2):
        stop = False
        # Step to next node
        next.setX(newX=next.x() + step)
        nextFloor.setCoord(newX=next.x(), newY=next.y() + 1)

        while current.isValid() and not stop: # Until the current node is invalid or we've stopped
            previousCollisionStates = [False, False] # // [Left, Right]
            # The next node is a wall, the next floor is missing or we've left the graph's bounds
            if nextFloor.isEmpty() or not next.isEmpty() or not next.isValid():
                # Stop
                stop = True
                if not current in corners:
                    # // And mark the current node as a corner
                    corners.append(
                        (
                            Point(x=current.x(), y=current.y(), nodeMap=nodeMap),
                            "l" if step == -1 else "r",
                        ) # // Tuple(Point object, Edge direction i.e. lCorner, rCorner)
                    )
            
            if current.isEmpty():
                foundNodes.append(Point(x=current.x(), y=current.y(), nodeMap=nodeMap))
                stepUp = 0 # Distance from the floor to the current node
                while ( # While the current node is within the graph's bounds, is empty and is within the entity's jump range
                    current.isValid()
                    and current.isEmpty()
                    and stepUp <= jumpForceInNodes
                ):
                    # Mark the left and right adjacent nodes
                    leftNode = Point(x=current.x() - 1, y=current.y(), nodeMap=nodeMap)
                    rightNode = Point(x=current.x() + 1, y=current.y(), nodeMap=nodeMap)
                    if not inList(query=current, ls=foundNodes): # Presence check // To avoid duplicates
                        foundNodes.append(
                            Point(x=current.x(), y=current.y(), nodeMap=nodeMap)
                        )
                    currentCollisionStates = [
                        leftNode.isValid() and not leftNode.isEmpty(), # => if [direction] node is within the graph's bounds and isn't a wall
                        rightNode.isValid() and not rightNode.isEmpty(),
                    ]
                    if previousCollisionStates[0] and not currentCollisionStates[0]: # Checks if collision has changed from true to false on the left side
                        newFloors.append(leftNode) # In which case a new floor has been found
                        waypoints.append(
                            ( # // Here we see the standard for waypoints which I've used
                                (current.y() + stepUp, current.x()), # // Being (y1, x1) "->" (y2, x2)
                                "->",
                                (leftNode.y(), leftNode.x()),
                            )
                        )
                    if previousCollisionStates[1] and not currentCollisionStates[1]: # Does the same for the right
                        newFloors.append(rightNode)
                        waypoints.append(
                            (
                                (current.y() + stepUp, current.x()),
                                "->",
                                (rightNode.y(), rightNode.x()),
                            )
                        )
                    
                     # // Note: python kept passing currentCollisionState by reference, hence the seemingly useless list(tuple()) cast to
                     # // create a disconnected copy
                    previousCollisionStates = list(tuple(currentCollisionStates)) # Move currentCollisionState to previousCollisionState
                    currentCollisionStates = [False, False] # And reset currentCollisionState

                    stepUp += 1  # Keep at end (goes to next row)
                    current.setY(newY=current.y() - 1)

            current.setCoord(newX=next.x(), newY=next.y())
            next.setX(newX=next.x() + step)
            nextFloor.setX(newX=next.x())

        step *= -1  # Reverse direction here
        current = Point(x=origin.x(), y=origin.y(), nodeMap=nodeMap) # And reset to origin
        next = Point(x=origin.x(), y=origin.y(), nodeMap=nodeMap)

    #return {
    #    "nodes": list[Point](foundNodes),
    #    "corners": list[tuple[Point, str]](corners),
    #    "newFloors": list[Point](newFloors),
    #    "waypoints": list[tuple[tuple[int, int], str, tuple[int, int]]](
    #        waypoints
    #    ),  # => ( (y1, x1), "->", (y2, x2) )
    #}
    return FloorResponse(
        nodes=foundNodes,
        corners=corners,
        newFloors=newFloors,
        waypoints=waypoints
    )

# // Cleans waypoints of duplicates
# // list(set()) can't be used to remove duplicate waypoints since we need additional logic to compress waypoints like
# // (y1, x1) -> (y2, x2) and (y2, x2) -> (y1, x1) into (y1, x1) <-> (y2, x2)
def removeDuplicateWaypoints(waypoints: list):
    cleanWaypoints = []
    while len(waypoints) != 0:
        waypoint = waypoints[0] # Store the first waypoint
        waypoints.pop(0) # And remove it
        if (waypoint[2], "->", waypoint[0]) in waypoints: # // Check if another waypoint stores (y2, x2) "->" (y1, x1)
            waypoints.remove((waypoint[2], "->", waypoint[0]))
            waypoint = (waypoint[0], "<->", waypoint[2]) # // Since we can compress it into (y1, x1) "<->" (y2, x2) if so
        if not waypoint[0] == waypoint[2] and not waypoint in cleanWaypoints: # Presence check to ensure we don't add a duplicate to our clean list
            cleanWaypoints.append(waypoint)
    return cleanWaypoints


# // Connects waypoints on the same floor
def connectAdjacentWaypoints(
    waypoints: list[tuple],
    disconnectedWaypoints: list[tuple[int, int]],  # (y, x) coords
    nodeMap: list[list[str]],
) -> list[tuple]:  # note: removed newWaypoints list
    waypointGroups = [] # 2D list of coordinates on the same y level which appear in waypoints
    while len(disconnectedWaypoints) != 0: # // Condition controlled loop since we change disconnectedWaypoints within the loop
        newGroup = []
        yQuery = disconnectedWaypoints[0][0]  # y coordinate of first index
        preservedWaypoints = list[tuple[int, int]]([])
        for point in disconnectedWaypoints:
            if point[0] == yQuery:
                newGroup.append(point) # // Removes the point from disconnectedWaypoints
            else:
                preservedWaypoints.append(point) # // since disconnectedWaypoints becomes preservedWaypoints after this loop

        disconnectedWaypoints = list(tuple(preservedWaypoints))

        newGroup.sort(key=lambda point: point[1])  # Sort newGroup by ascending x
        waypointGroups.append(newGroup)

    for group in waypointGroups:
        ignoreNextConditions = False # Guarantees that the next node is a corner if true
        if not group == []:
            cornerIndexes = list[int]([0]) # The first index will always be a corner // since it's sorted by ascending x
            for index in range(0, len(group) - 1):
                if ignoreNextConditions:
                    cornerIndexes.append(max(1, index))
                    ignoreNextConditions = False # ignoreNextConditions should only be true for 1 node at a time
                if group[index][1] == group[index + 1][1] - 1: # If the current waypoint is adjacent to the next waypoint
                    waypoints.append((group[index], "<->", group[index + 1]))
                elif not attemptGroundTraversal(
                    start=group[index], end=group[index + 1], nodeMap=nodeMap # Checks if coordinate A can't reach B without jumping
                ):
                    cornerIndexes.append(max(1, index)) # If so, mark it as a corner
                    ignoreNextConditions = True # // After a corner, the next node will always be a corner
                else:
                    waypoints.append((group[index], "<->", group[index + 1])) # // If A can reach B, mark it as a bidirectional waypoint
            cornerIndexes.append(len(group) - 1)


            for cornerIndex in range(0, len(cornerIndexes) - 1):
                potentialWaypoint = (
                    group[cornerIndexes[cornerIndex]],
                    "<->",
                    group[cornerIndexes[cornerIndex + 1]],
                ) # Each corner on a floor can reach each other
                validConnection = attemptGroundTraversal(
                    start=potentialWaypoint[0],
                    end=potentialWaypoint[2],
                    nodeMap=nodeMap,
                ) # // But verify using attemptGroundTraversal() just in case
                if validConnection and not potentialWaypoint in waypoints:
                    waypoints.append(potentialWaypoint)

    return removeDuplicateWaypoints(waypoints=waypoints)


def attemptGroundTraversal(
    start: tuple[int, int], end: tuple[int, int], nodeMap: list[list[str]]
) -> bool:
    if start[1] < end[1]:
        step = 1 # Same as dirEffect
    else:
        step = -1

    # Travels along the floor in the direction indicated by step
    nextNode = Point(x=start[1] + 1, y=start[0], nodeMap=nodeMap)
    nextFloor = Point(x=start[1] + 1, y=start[0] + 1, nodeMap=nodeMap)
    while nextNode.x() != end[1]:
        if nextFloor.isEmpty() or not nextNode.isEmpty():
            return False # Until either a floor is empty (can't travel via the ground)
        nextFloor.setX(newX=nextFloor.x() + step)
        nextNode.setX(newX=nextNode.x() + step)
    return True # Or the target is reached (can travel via the ground)


def precompileGraph(
    nodeMap: list[list[str]], # 2D list of which nodes are walls
    nodeSep: int,
    gravity: float,
    enemyData: dict,
    origin: tuple[int, int], # (y, x)
) -> PrecompileResponse:
    origin = getLowerNodes(
        topNodes=[Point(x=origin[1], y=origin[0], nodeMap=nodeMap)], nodeMap=nodeMap
    ).FLOORNODES[0] # Always start on the ground

    floors = list[Point]([origin])
    traversedFloors = list[tuple[int, int]]([])
    corners = []

    gravity = -abs(gravity) # Force gravity to be negative

    maxJumpHeight = suvat.s(
        u=enemyData["jumpForce"],
        g=gravity,
        t=suvat.solveV(targetV=0, u=enemyData["jumpForce"], g=gravity),
    ) # s = ut + 0.5at^2
    jumpHeightInNodes = maxJumpHeight // nodeSep

    allNodes = list[tuple[int, int]]([]) # Unsorted list of valid nodes
    waypoints = []

    while len(floors) != 0: # Loops until no new floors are found through the loop
        newFloors = []
        for floor in floors:
            if not floor.getCoord() in traversedFloors: # Verifies that the floor hasn't been traversed yet
                traversedFloors.append(floor.getCoord())
                floorData = traverseFloor(
                    nodeMap=nodeMap, jumpForceInNodes=jumpHeightInNodes, origin=floor
                )
                
                floorY = floor.y()
                # Transferring data from floorData to other lists to iterate through
                for corner in floorData.CORNERS:
                    if not corner in corners:
                        corners.append(corner)
                for node in floorData.NODES:
                    if node.y() == floorY and not node.getCoord() in traversedFloors:
                        traversedFloors.append(node.getCoord())
                for newFloor in floorData.NEWFLOORS:
                    if (
                        not newFloor.getCoord() in allNodes
                        and not newFloor.getCoord() in traversedFloors
                    ):
                        newFloors.append(newFloor) # Will become floors at the end of the while loop
                for waypoint in floorData.WAYPOINTS:
                    if not waypoint in waypoints: # No duplicate waypoints
                        waypoints.append(waypoint)
                for node in floorData.NODES: # Can be shortened but it harms readability too much
                    if not node.getCoord() in allNodes:
                        allNodes.append(node.getCoord())

        # 
        for corner in corners:  # corner => (Point, direction)
            topNodes = jumpOffEdge(
                jumpForce=enemyData["jumpForce"],
                gravity=gravity,
                maxXSpeed=enemyData["maxSpeed"][1],
                origin=corner[0],
                nodeMap=nodeMap,
                nodeSep=nodeSep,
                direction=corner[1],
            )
            # // Falling off an edge is unnecessary in most cases since it's only valid in 1 case where there's a wall close by the corner
            # // However, since it slightly improves accuracy and doesn't harm performance as precompile is only run once, it is kept in
            fallNodes = fallOffEdge(
                origin=corner[0].getCoord(),
                gravity=gravity,
                maxXSpeed=enemyData["maxSpeed"][1],
                nodeMap=nodeMap,
                nodeSep=nodeSep,
                direction=corner[1],
            )

            columnNodeData = {"nodes": list[Point]([]), "floorNodes": list[Point]([])}
            for x in range(0, 2): # // The logic used for topNodes and fallNodes is identical and so is simplified using a for loop
                indexesToRemove = list[int]([])
                if x == 0: # and an extra variable "observedList" to track which list is in use
                    observedList = topNodes
                else:
                    observedList = fallNodes
                
                # Make sure all nodes being tracked are free
                for node in observedList:
                    if node.data != " ": 
                        indexesToRemove.append(observedList.index(node)) # By removing wall nodes
                preservedNodes = []
                for index in range(0, len(observedList)):
                    if not index in indexesToRemove:
                        preservedNodes.append(observedList[index])

                observedList = list(tuple(preservedNodes)) # list(tuple()) is used for the same reason as in traverseFloor()
                response = getLowerNodes(topNodes=observedList, nodeMap=nodeMap)
                columnNodeData["nodes"].extend(response.NODES)
                columnNodeData["floorNodes"].extend(response.FLOORNODES)

            # Removing duplicates
            cleanColumnData = {"nodes": [], "floorNodes": []}
            for x in columnNodeData["nodes"]:
                if not x in cleanColumnData["nodes"]:
                    cleanColumnData["nodes"].append(x)
            for x in columnNodeData["floorNodes"]:
                if not x in cleanColumnData["floorNodes"]:
                    cleanColumnData["floorNodes"].append(x)
            columnNodeData = cleanColumnData
            
            # Cycle through newFloors to traverse
            for newFloor in columnNodeData["floorNodes"]:
                if not newFloor.getCoord() in traversedFloors and not (
                    newFloor.getCoord() in allNodes or inList(query=newFloor, ls=floors) # Prevents duplicates in floors
                ):
                    newFloors.append(newFloor)
                waypoints.append((corner[0].getCoord(), "->", newFloor.getCoord())) # Add a waypoint between the origin corner and the new floor
            for node in columnNodeData["nodes"]:
                if not node in allNodes: # Prevents duplicates in allNodes
                    allNodes.append(node.getCoord())
        corners = []
        floors = list(tuple(newFloors)) # floors now becomes newFloors

    #return {
    #    "nodes": allNodes,
    #    "waypointData": compileWaypointData(waypoints=waypoints, nodeMap=nodeMap),
    #}
    return PrecompileResponse(
        nodes=allNodes,
        waypointData=compileWaypointData(waypoints=waypoints, nodeMap=nodeMap)
    )


# // Used for debugging and in pathing when getting adjacent nodes
def queryWaypoints(
    waypoints: list[tuple],
    query: tuple[int, int] = None,
    doubleQuery: tuple[int, int] = None, # Used for more specific queries
    y: int = None,
    x: int = None
) -> list[tuple]:
    foundWaypoints = []
    for waypoint in waypoints:
        # x and y searching
        if waypoint[0][1] == x or waypoint[2][0] == x:
            foundWaypoints.append(waypoint)
        if waypoint[0][0] == y or waypoint[2][0] == y:
            foundWaypoints.append(waypoint)
        # Searching for a specific waypoint
        if doubleQuery != None:
            if (waypoint[0] == query and waypoint[2] == doubleQuery) or (
                waypoint[0] == doubleQuery and waypoint[2] == query
            ):
                foundWaypoints.append(waypoint)
        # Searching for a coordinate
        elif waypoint[0] == query or waypoint[2] == query:
            foundWaypoints.append(waypoint)

    return foundWaypoints


#def queryCompressed(waypoints, compressedWaypoint):
#    foundWaypoints = []
#    start = compressedWaypoint[0][1]
#    end = compressedWaypoint[2][1]
#    for xCoord in range(start, end + 1):
#        response = queryWaypoints(
#            waypoints=waypoints,
#            query=(compressedWaypoint[0][0], xCoord),
#            ignoreCompressed=True,
#        )
#        for x in response:
#            if (
#                x[0] == (compressedWaypoint[0][0], xCoord)
#                and not x in foundWaypoints
#                and not x[1] == "-"
#            ):
#                foundWaypoints.append(x)
#    return foundWaypoints
#
#
#def checkCompressed(query, waypoint):
#    return (
#        waypoint[0][0] == query[0]
#        and waypoint[2][0] == query[0]
#        and waypoint[0][1] <= query[1]
#        and query[1] <= waypoint[2][1]
#    )


# // Queries an x or y coordinate in disconnectedWaypoints
def queryDisconnectedWaypoints(
    disconnectedWaypoints: list[tuple[int, int]], x: int = 0, y: int = 0
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
    return found # Duplicate waypoints


#def compressWaypoints(
#    waypoints: list,
#    disconnectedWaypoints: list[tuple[int, int]],
#    nodeMap: list[list[str]],
#):
#    waypointsByY = [] # Groups of waypoints organised by their y coordinate
#    for yCoord in range(0, len(nodeMap)):
#        waypointsByY.append(
#            queryDisconnectedWaypoints( # Groups waypoints by their y coordinate
#                disconnectedWaypoints=disconnectedWaypoints, y=yCoord
#            )
#        )
#    for groupIndex in range(0, len(waypointsByY)):
#        waypointsByY[groupIndex].sort(key=lambda x: x[1])
#        index = 0
#        lEdge = None
#        rEdge = None
#        while index <= len(waypointsByY[groupIndex]) - 1:
#            rEdge = waypointsByY[groupIndex][index]
#            if lEdge == None:
#                lEdge = waypointsByY[groupIndex][index]
#            elif not attemptGroundTraversal(
#                start=lEdge, end=rEdge, nodeMap=nodeMap  # (proposed)
#            ):
#                rEdge = waypointsByY[groupIndex][index - 1]
#                waypoints.append((lEdge, "-", rEdge))
#                lEdge = waypointsByY[groupIndex][index]
#            index += 1
#        if lEdge != None:
#            waypoints.append((lEdge, "-", rEdge))
#    return removeDuplicateWaypoints(waypoints=waypoints)


def compileWaypointData(
    waypoints: list[
        tuple[tuple[int, int], str, tuple[int, int]]
    ],  # e.g. [ ( (y1, x1) "<->", (y2, x2) ) ]
    nodeMap: list[list[str]],
) -> CompiledWaypointResponse:
    waypoints = removeDuplicateWaypoints(waypoints=waypoints) # Remove duplicates

    # Compile disconnectedWaypoints
    disconnectedWaypoints = []
    for waypoint in waypoints:
        if not waypoint[0] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[0])
        if not waypoint[2] in disconnectedWaypoints:
            disconnectedWaypoints.append(waypoint[2])

    # Connect adjacent waypoints
    waypoints = connectAdjacentWaypoints(
        waypoints=waypoints,
        disconnectedWaypoints=disconnectedWaypoints,
        nodeMap=nodeMap,
    )
    waypoints.sort(key=lambda waypoint: waypoint[0][0])

    #return {"waypoints": waypoints, "disconnectedWaypoints": disconnectedWaypoints}
    return CompiledWaypointResponse(
        waypoints=waypoints,
        disconnectedWaypoints=disconnectedWaypoints
    )


# // Made to check if waypoints was being passed by reference, left in since theres no point in removing functioning debug code
# // Goes through every node in the nodeMap and queries both waypoint lists with that node
# // Outputs nodes which aren't in both lists
# // Used purely for debugging
def findInconsistencies(waypoints1, waypoints2, nodeMap):
    for rowIndex in range(0, len(nodeMap)):
        for columnIndex in range(0, len(nodeMap[rowIndex])):
            response1 = queryWaypoints(
                waypoints=waypoints1, query=(rowIndex, columnIndex)
            )
            response2 = queryWaypoints(
                waypoints=waypoints2, query=(rowIndex, columnIndex)
            )
            if len(response1) != len(response2):
                print(f"Coord: ({rowIndex}, {columnIndex})")


# Converts the contents of a .csv file into a 2D list of walls and empty nodes
def loadMap(fileName: str, invalidKeys: list[int]) -> list[list[str]]:
    with open(fileName, "r", newline="") as f:
        data = csv.reader(f, delimiter=" ", quotechar="|")
        segmentedData = []
        for row in data:
            segmentedData.append([x for x in row[0].split(",")])
        segmentedData.pop(0)
        testGraph = []
        for row in segmentedData:
            # try: except: used as "e" was exported as an ID during terminal testing with maps
            try:
                testGraph.append([" " if int(x) in invalidKeys else "#" for x in row])
            except:
                pass
        f.close()
    return testGraph


# Debugging
def main(map: str, origin: tuple[int, int]):
    testGraph = loadMap(fileName=map, invalidKeys=[5, 6, 2, -1])  # (7, 6)

    gravityAccel = 9.81 * 15
    nodeSep = 15

    enemyData = {"jumpForce": 125, "maxSpeed": (100, 37.5)}

    response = precompileGraph(
        nodeMap=testGraph,
        nodeSep=nodeSep,
        gravity=gravityAccel,
        enemyData=enemyData,
        origin=origin,
    )

    allNodes = response.NODES
    waypoints = response.WAYPOINTDATA.WAYPOINTS

    for x in allNodes:
        testGraph[x[0]][x[1]] = "x"
    for x in waypoints:
        testGraph[x[0][0]][x[0][1]] = "W"
        testGraph[x[2][0]][x[2][1]] = "W"

    pass
    for line in testGraph:
        print(line)
    for waypoint in waypoints:
        print(waypoint)
    pass


def outputTestGraph(fileName: str) -> None:
    data = loadMap(fileName=fileName, invalidKeys=[5, 6, 2, -1])
    for row in data:
        print(row)
    pass


# t = time.time()
#mapName = "Prototype1/transfer/Maps/a.csv"
#origin = (6, 0)
#main(map=mapName, origin=origin)
#outputTestGraph(fileName=mapName)
# e = time.time()
# print(e - t)
