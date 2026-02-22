import pygame
import operator
from PhysicsObject import PhysicsObject
from dictionaries import allEffects
from transfer import precompile

import transfer.pathing as pathing

operators = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv
}

hardVCap = (-75, 75)

class Entity(PhysicsObject):
    def __init__(
            self,
            FPS: int,
            jumpForce: float,
            maxHP: int,
            defense: int,
            speed: float,
            pAttackCooldown: float,
            pSize: pygame.math.Vector2,
            spritePath: str,
            pMass: float,
            startingPosition: pygame.math.Vector2,
            pVelocityCap: pygame.math.Vector2,
            startingVelocity: pygame.math.Vector2 = pygame.math.Vector2(0,0),
            pTag: str = "None",
            pIgnoreYFriction = False
    ):
        super().__init__(
            FPS=FPS,
            pSize=pSize,
            spritePath=spritePath,
            pTag=pTag,
            pMass=pMass,
            startingPosition=startingPosition,
            startingVelocity=startingVelocity,
            pVelocityCap=pVelocityCap,
            pIgnoreYFriction=pIgnoreYFriction
        )
        self.isGrounded = False
        self._jumpForce = jumpForce
        self._originalAttributes = {
            "maxHP": maxHP,
            "defense": defense,
            "speed": speed,
            "attackCooldown": pAttackCooldown,
            "baseVCap": (pVelocityCap.x, pVelocityCap.y)
        }
        self._maxHP = maxHP
        self.remainingHP = maxHP
        self._defense = defense
        self._speed = speed
        self.attackCooldown = pAttackCooldown
        self.cooldownRemaining = 0.0
        self._effects = {}
        #####PROTOTYPE 2
        self.isPathing = False
        self.currentPathEnd = (0, 0) #(x, y)
        #self.currentNode = (0, 0) #(y, x)
        self.currentNode = (
            ((self.absoluteCoordinate.x) // 75),
            (self.absoluteCoordinate.y) // 75 + 6,
        )
        self.debug = 0
        self.currentPath = []

        self.previousPathCoord = (0, 0)
        self.framesSinceLastNode = 0
        self.shouldPath = False
        self.paused = False
    
    def addEffect(self, ID: int):
        freeInstance = False
        currInstance = 0
        while not freeInstance:
            if not str(ID) + "-" + str(currInstance) in self._effects.keys():
                freeInstance = True
            else:
                currInstance += 1
        self._effects[str(ID)+"-"+str(currInstance)] = allEffects[ID] #allEffects is an imported dictionary containing all effects in the game in the format: array[2]
    '''
    default instance to -1 to remove all instances of effect and default ID to -1 to remove all effects
    forced is a local variable which tracks if an effect timed out or was forcefully removed by another function
    '''
    def removeEffect(self, ID: int = -1, instance: str = "-1", forced: bool =False):
        if ID > -1:
            if int(instance) > -1 and str(ID)+"-"+instance in self._effects.keys():
                self._effects.pop(str(ID)+"-"+instance)
            elif int(instance) < 0:
                for key in self._effects.keys():
                    if int(key.split("-")[0]) == ID:
                        self._effects.pop(key)
        else:
            self._effects = {}

        #if the removal was forced, recalculateAttributes() wouldn't have been run, so we need to run it here
        if forced:
            self._recalculateAttributes()
    
    def _recalculateAttributes(self):
        self._maxHP = self._originalAttributes["maxHP"]
        self._defense = self._originalAttributes["defense"]
        self._speed = self._originalAttributes["speed"]
        self.attackCooldown = self._originalAttributes["attackCooldown"]

        effectValues = [value for value in self._effects.values()]

        for index in range(0, len(effectValues)):
            splitValue = effectValues[index].split(", ") #double split to cover effects which affect multiple attributes
            splitEffects = [item.split(" ") for item in splitValue]
            for effect in splitEffects:
                self.modifyStat(effect[0], effect[1], effect[2])

        self._velocityCap.x = max(self._velocityCap.x, self._velocityCap.x*self._speed) #increase speed cap by a factor of _speed
        self._velocityCap.y = max(self._velocityCap.y, self._velocityCap.y*self._speed)
        self._velocityCap.x = max(hardVCap[0], min(self._velocityCap.x, hardVCap[1]))
        self._velocityCap.y = max(hardVCap[0], min(self._velocityCap.y, hardVCap[1]))
    
    def modifyStat(self, stat: str, operator: str, magnitude: float):
        #for all effects, effect is in the form "[attribute], [operator], [magnitude]" since it's easier to display on the UI
        match stat:
            case "jumpForce":
                self._jumpForce = operators[operator](self._jumpForce, magnitude)
            case "maxHP":
                self._maxHP = operators[operator](self._maxHP, magnitude)
            case "defense":
                self._defense = operators[operator](self._defense, magnitude)
            case "speed":
                self._speed = operators[operator](self._speed, magnitude)
            case "cooldown":
                self.attackCooldown = operators[operator](self.attackCooldown, magnitude)
    
    def jump(self):
        self._velocity.y = -self._jumpForce
        self.isGrounded = False
    
    def modifySpeedCap(self, axis: str, magnitude: float):
        if len(axis) > 1:
            axis = axis[0:1]
        if axis == "x":
            self._velocityCap.x += magnitude*self._speed
        else:
            self._velocityCap.y += magnitude*self._speed
    

    #####PROTOTYPE 2
    def path(
            self,
            pathingTo, #(y, x)
            precompiledData,
            nodeMap,
            nodeSep,
            gravity=9.81 * 15,
            rePathTolerance=2
        ):
        pathingTo = (int(pathingTo[0]), int(pathingTo[1]))
        print(self.currentNode)
        print(self.currentPath)
        #print(precompile.getLowerNodes(
        #        topNodes=[precompile.Point(
        #            x=pathingTo[1],
        #            y=pathingTo[0],
        #            nodeMap=nodeMap
        #        )],
        #        nodeMap=nodeMap
        #    )["floorNodes"][0].getCoord())
        #print(self.isPathing)
        if (pathing.getHeuristic(start=self.currentPathEnd, end=pathingTo) > rePathTolerance or not self.isPathing) and self.shouldPath:
            #if precompile.getLowerNodes(
            #    topNodes=[precompile.Point(
            #        x=pathingTo[1],
            #        y=pathingTo[0],
            #        nodeMap=nodeMap
            #    )],
            #    nodeMap=nodeMap
            #)["floorNodes"][0].getCoord() != pathingTo or not self.isPathing: #this is nested to save what little performance i have left
                self.currentPathEnd = pathingTo
                self.currentPath = pathing.main(
                    precompiledData=precompiledData,
                    nodeMap=nodeMap,
                    nodeSep=nodeSep,
                    start=self.currentNode,
                    end=pathingTo,
                    jumpForce=self._jumpForce,
                    maxXSpeed=self._velocityCap.x,
                    gravity=gravity
                )
                print(f"Pathing to {pathingTo}")
                cleanPath = []
                for x in self.currentPath:
                    if not x in cleanPath:
                        cleanPath.append(x)
                self.currentPath = cleanPath
                if len(self.currentPath) == 1:
                    if self.currentPath[0] == self.currentNode:
                        self.isPathing == False
                        self.currentPath = []
                    else:
                        self.isPathing = True
                else:
                    self.isPathing == True
                #self.shouldPath = False
                self.isPathing = True
                pass
        if len(self.currentPath) > 0:
            #print(self.currentNode, self.currentPath[0])
            #print(self.absoluteCoordinate)
            #if self.currentNode == self.currentPath[0]: #(y, x)
            #    print("removed")
            #    self.currentPath.pop(0)

            if self.currentNode in self.currentPath:
                #print(self.currentNode == self.currentPath[0])
                #print(self.currentPath)
                #self._velocity.x = 0
                index = self.currentPath.index(self.currentNode)
                print(self.currentPath)
                for x in range(0, index + 1):
                    print("z")
                    self.framesSinceLastNode = 0
                    self.previousPathCoord = self.currentPath[0]
                    self.removeForce(axis="x", ref="xPathing")
                    self.currentPath.pop(0)
                #while self.currentNode != self.currentPath[0]:
                #    self.currentPath.pop(0)
                #self.currentPath.pop(0)
            elif self.framesSinceLastNode > self.FPS / 2 or (self.currentNode[0] > self.currentPath[0][0] and self.currentNode[1] == self.currentPath[0][1]):
                self.framesSinceLastNode = 0
                self.currentPath.pop(0)
                self.removeForce(axis="x", ref="xPathing")
                try:
                    self.previousPathCoord = self.currentPath[0]
                except:
                    pass

            try:
                xNodeDiff = self.currentPath[0][1] - self.currentNode[1] # + => Move right. - => Move left.
                #print(f"pathing to {self.currentPath[0]}")
                #print(f"x => {xNodeDiff}")
                xDir = "l" if xNodeDiff < 0 else "r"
                yNodeDiff = self.currentNode[0] - self.currentPath[0][0] # + => Move up. - => Move down.
                #print(f"y => {yNodeDiff}")
                yDir = "u" if yNodeDiff > 0 else "d"
                #if (not self.containsForce(axis="x", ref="xPathing")) and xNodeDiff != 0:
                    #print(f"added xPathing")
                self.addForce(axis="x", direction=xDir, ref="xPathing", magnitude=1000)
                if xNodeDiff == 0:
                    self.removeForce(axis="x", ref="xPathing")
                elif self.framesSinceLastNode > 10:
                    self.addForce(axis="x", direction=xDir, ref="xPathing", magnitude=1000)
                if self.isGrounded and yNodeDiff > 0:
                    print("jump")
                    self.jump()
                self.previousPathCoord = self.currentNode
            except:
                pass

        if len(self.currentPath) == 0:
            self.removeForce(axis="x", ref="xPathing")
            self.isPathing = False
            self.shouldPath = False
            self._velocity.x /= 1.5

    '''
    self.FPS is assigned from a global variable denoting the number of game updates per second
    1/self.FPS is the time since last frame
    '''
    def update(
            self,
            collidableObjects,
            precompiledData,
            nodeMap,
            nodeSep,
            pathingTo
        ): #playerMoved=(0, 0)
        for key in self._effects.keys():
            self._effects[key][1] -= 1/self.FPS
            if self._effects[key][1] <= 0:
                self.removeEffect(ID=int(key.split("-")[0]), instance=key.split("-")[1], forced=False)

        if self.simulated:
            #this is in depencency order i.e. all physics functions require updated attributes, therefore self._recalculateAttributes() is run

            self._recalculateAttributes()

            self._resultantForce = self.recalculateResultantForce(forceMult=self._speed, includedForces=[])
            if self.paused:
                self.paused = False

            #print(self._xForces)

            self._acceleration = self.getAcceleration()
            self.getVelocity()

            ####PROTOTYPE 2
            if self.debug > 0 and self.shouldPath:
                self.path(
                    pathingTo=pathingTo,
                    precompiledData=precompiledData,
                    nodeMap=nodeMap,
                    nodeSep=nodeSep
                )
                self.debug = 0
            self.debug += 1

            displacement = self.displaceObject(collidableObjects=collidableObjects)

            if -2.5 < displacement.x and displacement.x < 2.5:
                displacement.x = 0
            if -0.25 < displacement.y and displacement.y < 0.25:
                displacement.y = 0

            if self.currentNode == self.previousPathCoord:
                self.framesSinceLastNode += 1

            self.rect.center += displacement
            self.absoluteCoordinate += displacement

            #self.rect.clamp_ip(pygame.display.get_surface().get_rect())