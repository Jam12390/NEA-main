import math
from typing import Optional

class Node():
    def __init__(self, coord, previousNode, data, endNode, incomingYVel, ) -> None:
        self.tag = Optional[str] 
        self.coord = coord #this is what nextNodes points to - sort of like a linked list since Nodes aren't organised during pathing
        self.lowestDistance = 0
        self.heuristic = getHeuristic(coord, endNode)
        #nodes and velocities are in a list since they can have multiple different values
        #this is because there can be multiple paths to 1 node with different velocities
        #the incoming y velocity is important as it determines which paths can be travelled to next
        #higher y velocities are preferred since it makes more paths accessible
        self.previousNode = previousNode
        self.possibleNextNodes = []
        self.data = data
        self.incomingYVel = 0
        self.incomingYOffset = 0 #since we're solving for time on the y axis to go up nodeSep/2 before travelling nodeSep/2 on the x axis, we need to check how far the previous node travelled on the y axis

def s(u, a, t):
    return u*t + 0.5*a*t**2

def solveS(s, u, a):
    if u**2 - 4*a*-s >= 0:
        solutions = [
            (-u + math.sqrt(u**2 - 4*a*-s)) / (2 * a),
            (-u - math.sqrt(u**2 - 4*a*-s)) / (2 * a),
        ]
    else:
        solutions = []
    if len(solutions) != 0:
        for solution in solutions:
            if solution != 0:
                return solution
        return 0
    else:
        return None

def v(u, a, t):
    return u + a*t

def getNodeHeuristic(startNode, endNode):
    yDiff = endNode[0] - startNode[0]
    xDiff = endNode[1] - startNode[1]
    return math.sqrt(xDiff**2 + yDiff**2)

def getAbsoluteHeuristic(absoluteStart, absoluteEnd):
    yDiff = absoluteStart[0] - absoluteEnd[0]
    xDiff = absoluteStart[0] - absoluteEnd[0]
    return math.sqrt(yDiff**2 + xDiff**2)

def getPossibleNextNodes(node: Node, graph, target, nodeSep, maxXSpeed, gravityAccel, yOffset = 0, xOffset = 0, possibleYVelocity = Optional[float]): #possibleYVelocity is used for if the node is grounded (since we can either jump from the node or)
    if node.incomingYVel < 0:
        distanceToTravel = (nodeSep/2) - yOffset
        yDirection = "d"
    else:
        distanceToTravel = (nodeSep/2) + yOffset
        yDirection = "u"
    yTime = solveS(s=(nodeSep/2) - yOffset, u=node.incomingYVel, a=gravityAccel)
    xTime = (nodeSep / 2 - abs(xOffset)) / maxXSpeed
    '''
    since the x offset has - as left and + as right
    taking away a negative offset increases distance right and decreases distance left
    (nodeSep / 2 - xOffset is the distance from left to right)
    hence
    xTimeRight = (nodeSep / 2 - xOffset) / maxXSpeed
    and
    xTimeLeft = (nodeSep - (nodeSep / 2 - xOffset)) / maxXSpeed
    '''
    xTime = {
        "l": (nodeSep / 2 + xOffset) / maxXSpeed,
        "r": (nodeSep / 2 - xOffset) / maxXSpeed
    }

    directionOfTravel = []

    if yTime != None:
        if yTime < xTime["l"]:
            directionOfTravel.append(yDirection)
        else:
            directionOfTravel.append("l")
        if yTime < xTime["r"]:
            directionOfTravel.append(yDirection)
        else:
            directionOfTravel.append("r")
    else:
        directionOfTravel.append("l")
        directionOfTravel.append("r")
    
    '''
    there are 3 options when travelling up:
        1. travel left
        2. travel right
        3. do nothing
        1 -> travel up with left offset or travel right with y offset
        2 -> travel up with right offset or travel right with y offset
        3 -> travel in y direction with no offset
    '''


    for direction in directionOfTravel:
        if direction == "l" or direction == "r":
            outgoingYOffset = yOffset + s(u=node.incomingYVel, a=gravityAccel, t=xTime[direction])
            outgoingYVel = v(u=node.incomingYVel, a=gravityAccel, t=xTime[direction])
            outgoingXOffset = nodeSep/2 * -1 if direction == "r" else 1
        else:
            outgoingYOffset = nodeSep/2 * -1 if direction == "d" else 1
            outgoingYVel = v(u=node.incomingYVel, a=gravityAccel, t=yTime)
    

    #OVERALL
    newPoints = []

    yTimeToTravel = solveS(s=(nodeSep/2) - yOffset, u=node.incomingYVel, a=gravityAccel)
    #LEFT
    left = nodeSep / 2 - (abs(xOffset) + (maxXSpeed * yTimeToTravel))
    #RIGHT
    right = nodeSep / 2 + (abs(xOffset) + (maxXSpeed * yTimeToTravel))
    #NOTHING
    pass

    #CHECK LEFT
    if not left in range(0, nodeSep):
        leftTimeToTravel = (nodeSep / 2 + xOffset) / maxXSpeed
        yDisplacement = s(u=node.incomingYOffset, a=gravityAccel, t=leftTimeToTravel)
        newNode = (node.coord[0], node.coord[1] - 1)
        if (newNode[0], newNode[1]) in graph:
            if graph[newNode[0]][newNode[1]] == " ":
                newPoints.append(
                    Node(
                        coord=newNode,
                        previousNode=node.coord,
                        data=" ",
                        endNode=target
                    )
                )