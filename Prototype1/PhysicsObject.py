import pygame
import typing

class PhysicsObject(pygame.sprite.Sprite):
    def __init__(
            self,
            FPS: int,
            pSize: pygame.Vector2,
            spritePath: str,
            pMass: float,
            startingPosition: pygame.Vector2,
            pVelocityCap: pygame.Vector2,
            startingVelocity: pygame.Vector2 = pygame.Vector2(0, 0),
            pTag: str = "none",
            pIgnoreYFriction = False,
    ):
        super().__init__()
        self.FPS = FPS
        self.size = pSize
        self.image = pygame.transform.smoothscale(pygame.image.load(spritePath), (pSize.x, pSize.y))
        self.absoluteCoordinate = startingPosition
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(startingPosition.x), round(startingPosition.y))
        self.simulated = True
        self.tag = pTag
        self._mass = pMass
        self._xForces = {}
        self._yForces = {"gravity": pMass*9.81*15} #gravity ignores mass
        self._resultantForce = pygame.Vector2(0,0)
        self._velocity = startingVelocity
        self._velocityCap = pVelocityCap
        self._baseVCap = pVelocityCap
        self._acceleration = pygame.Vector2(0,0)
        self.blockedMotion = []
        self.isGrounded = False
        self.previousGroundedYCoord = self.absoluteCoordinate.y
        self.isPostGroundedFrame = 0
        self.shouldReturnDisplacement = False
        self.ignoreYFriction = pIgnoreYFriction
    
    def recalculateResultantForce(self, forceMult: float = 1, includedForces: list = []):
        resXForce = 0
        resYForce = 0

        xForces, xForceKeys = [force for force in self._xForces.values()], [key for key in self._xForces.keys()]
        yForces, yForceKeys = [force for force in self._yForces.values()], [key for key in self._yForces.keys()]

        for index in range(0, len(xForces)): #sum of horizontal forces
            resXForce += xForces[index] if xForceKeys[index] not in includedForces else xForces[index] * forceMult
        for index in range(0, len(yForces)): #sum of vertical forces
            resYForce += yForces[index] if yForceKeys[index] not in includedForces else yForces[index] * forceMult
        return pygame.Vector2(resXForce, resYForce) #store as vector2 (easier for later operations)
    
    def getAcceleration(self):
        return (self._resultantForce / self._mass) #a = F/m
    
    def getVelocity(self):
        initialVelocity = self._velocity

        overflowReductionRate = 2

        if initialVelocity.x > self._velocityCap.x:
            xVelocity = initialVelocity.x - overflowReductionRate
            xVelocity += min(self._acceleration.y*(1/self.FPS), 0)
        elif initialVelocity.x < self._velocityCap.x*-1:
            xVelocity = initialVelocity.x + overflowReductionRate
            xVelocity += max(self._acceleration.y*(1/self.FPS), 0)
        else:
            xVelocity = self._velocity.x + self._acceleration.x*(1/self.FPS)
            xVelocity = max(self._velocityCap.x * -1, min(xVelocity, self._velocityCap.x)) #clamping xVelocity to _velocityCap.x
        
        if initialVelocity.y > self._velocityCap.y:
            yVelocity = initialVelocity.y - overflowReductionRate
            yVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y <= 0 else 0
        elif initialVelocity.y < self._velocityCap.y*-1:
            yVelocity = initialVelocity.y + overflowReductionRate
            yVelocity += self._acceleration.y*(1/self.FPS) if self._acceleration.y >= 0 else 0
        else:
            yVelocity = self._velocity.y + self._acceleration.y*(1/self.FPS)
            yVelocity = max(self._velocityCap.y * -1, min(yVelocity, self._velocityCap.y)) #same with yVelocity
        
        self._velocity = pygame.Vector2(xVelocity, yVelocity)

    def getVelocityValue(self):
        return self._velocity
    
    def getMass(self):
        return self._mass
    
    def displaceObject(
            self,
            collidableObjects,
            isPlayer=False
    ) -> typing.Optional[pygame.Vector2]:
        
        xDisplacement = self._velocity.x*5*(1/self.FPS)
        yDisplacement = self._velocity.y*5*(1/self.FPS) #conversion of 1m -> 5pix - no

        #if self.isPostGroundedFrame > 0:
        #    #self.isPostGroundedFrame = False
        #    self.isPostGroundedFrame -= 1
        #    ignoreDiff = 0 #multiplier
        #else:
        #    ignoreDiff = 1

        diff = self.renderCollisions(collidableObjects=collidableObjects, displacement=pygame.Vector2(xDisplacement, yDisplacement), isPlayer=isPlayer) #update position - playerMoved
        #self.rect.center = (self.rect.centerx + xDisplacement, self.rect.centery + yDisplacement)
        #response = self.camRenderCollisions(
        #    collidableObjects=collidableObjects,
        #    pixelTolerance=0, #i cant think anymore - ive reached that point of exhaustion
        #    isPlayer=isPlayer
        #)
        #if response.x != 0:
        #    self.blockedMotion.append("l" if xDisplacement < 0 else "r")
        #if response.y != 0:
        #    self.blockedMotion.append("u" if yDisplacement < 0 else "d")
        #self.blockedMotion = []
        #finalDisplacement = self.undercookedCollision(
        #    collidableObjects=collidableObjects,
        #    moved=pygame.Vector2(xDisplacement, yDisplacement)
        #)
        
        '''
        collision note:
        what if i attached the collidable to blockedMotion and just set xDisplacement to the distance between the 2?
        sure whatever ill do that after my break
        what to do what to do...
        '''

        #if "l" in self.blockedMotion:
        #    self._velocity.x = 0 #assume velocity is in the same direction and therefore set it to 0
        #    response.x = 0
        #
        #if "r" in self.blockedMotion:
        #    self._velocity.x = 0
        #    response.x = 0
        #
        #if "d" in self.blockedMotion:
        #    self._velocity.y = 0
        #    response.y = 0
        #
        #if "u" in self.blockedMotion:
        #    self._velocity.y = 0
        #    response.y = 0
        #
        ##camCollision
        #finalDisplacement = pygame.Vector2(
        #    x=xDisplacement - response.x,
        #    y=yDisplacement - response.y
        #)

        #if not isPlayer:
        #    self.rect.centerx += finalDisplacement.x
        #    self.rect.centery += finalDisplacement.y
        return pygame.math.Vector2(xDisplacement - diff[0], yDisplacement - diff[1]) #finalDisplacement
    
    def undercookedCollision(
            self,
            collidableObjects,
            moved
    ):
        finalDisplacement = pygame.Vector2(moved.x, moved.y)

        self.rect.centerx += moved.x
        self.rect.centery += moved.y

        borders = {
            "ul": self.rect.topleft,
            "ur": self.rect.topright,
            "dl": self.rect.bottomleft,
            "dr": self.rect.bottomright
        }

        self.rect.centerx -= moved.x
        self.rect.centery -= moved.y

        foundCollisions = self.cycleCollidables(
            collidableObjects=collidableObjects,
            borders=borders
        )
        frictionCoefs = {}

        for direction in foundCollisions.keys():
            if foundCollisions[direction][0] != None:
                match direction:
                    case "u":
                        finalDisplacement.y = foundCollisions[direction][0].bottom - self.rect.top
                        self.blockedMotion.append("u")
                        frictionCoefs["u"] = foundCollisions[direction][1]
                    case "d":
                        finalDisplacement.y = foundCollisions[direction][0].top - self.rect.bottom
                        self.blockedMotion.append("d")
                        frictionCoefs["d"] = foundCollisions[direction][1]
                    case "r":
                        finalDisplacement.x = foundCollisions[direction][0].left - self.rect.right
                        self.blockedMotion.append("r")
                        frictionCoefs["r"] = foundCollisions[direction][1]
                    case "l":
                        finalDisplacement.x = foundCollisions[direction][0].right - self.rect.left
                        self.blockedMotion.append("l")
                        frictionCoefs["l"] = foundCollisions[direction][1]
        
        self.__updateFriction(coef=frictionCoefs)
        return finalDisplacement
        

    def renderCollisions(self, collidableObjects, displacement: pygame.math.Vector2, isPlayer: bool=False, tileSize=76) -> typing.Optional[pygame.Vector2]:
        self.blockedMotion = []
        collidingDirections = []

        frictionCoefs = {}

        #totalDiff = [displacement.x, displacement.y]
        totalDiff = [0, 0]

        collidingObjects = {
            "l": None,
            "r": None,
            "u": None,
            "d": None
        }

        #if not isPlayer:
            #print("Modified by render")
            #self.absoluteCoordinate = pygame.Vector2(self.absoluteCoordinate.x + displacement.x, self.absoluteCoordinate.y + displacement.y) #reverse this on the player object at the end..?
            #self.rect.center = (self.rect.centerx + displacement.x, self.rect.centery + displacement.y) #reverse this on the player object at the end..?
        #originalDisplacement = tuple([displacement.x, displacement.y])
        #originalDisplacement = pygame.Vector2(x=originalDisplacement[0], y=originalDisplacement[1])



        for group in collidableObjects:
            for collidable in group:
                #print(collidable.rect.center)
                if "item" in collidable.tags and self.tag == "player":
                    if pygame.Rect.colliderect(self.rect, collidable.rect): #collidable is an item in the scene
                        collidable.UIWindow.shown = True
                    else:
                        collidable.UIWindow.shown = False

                if ("wall" in collidable.tags or "floor" in collidable.tags)and collidable.simulated: #thinking ahead for when objects are de-rendered to improve performance - source: https://www.digitalocean.com/community/tutorials/how-to-compare-two-lists-in-python len(set(collidable.tags) & set(["wall", "floor"])) > 0
                    renderedDifference = [0, 0]
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomleft):
                            xDiff = abs(self.rect.left - collidable.rect.right)
                            yDiff = abs(self.rect.bottom - collidable.rect.top)

                            if xDiff < yDiff and self._velocity.x < 0 and "wall" in collidable.tags:
                                renderedDifference[0] += 1
                                if not isPlayer:
                                    self.rect.left = collidable.rect.right
                                else:
                                    totalDiff[0] -= xDiff
                                collidingDirections.append("l")
                                frictionCoefs["l"] = collidable.frictionCoef
                                collidingObjects["l"] = collidable
                            elif xDiff > yDiff and self._velocity.y > 0 and len(set(collidable.tags) & set({"floor", "lCorner", "rCorner"})) > 0:
                                renderedDifference[1] += 1
                                if not isPlayer:
                                    self.rect.bottom = collidable.rect.top
                                else:
                                    totalDiff[1] += yDiff
                                collidingDirections.append("d")
                                frictionCoefs["d"] = collidable.frictionCoef
                                collidingObjects["d"] = collidable

                        #top left corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.topleft): #do tag checks here
                        xDiff = abs(self.rect.left - collidable.rect.right)
                        yDiff = abs(self.rect.top - collidable.rect.bottom)
                        if xDiff < yDiff and self._velocity.x < 0 and "wall" in collidable.tags:
                            renderedDifference[0] += 1
                            if not isPlayer:
                                self.rect.left = collidable.rect.right
                            else:
                                totalDiff[0] -= xDiff
                            collidingDirections.append("l")
                            collidingObjects["l"] = collidable
                            frictionCoefs["l"] = collidable.frictionCoef
                        elif xDiff > yDiff and self._velocity.y < 0 and "roof" in collidable.tags:
                            renderedDifference[1] += 1
                            if not isPlayer:
                                self.rect.top = collidable.rect.bottom
                            else:
                                totalDiff[1] -= yDiff
                            collidingDirections.append("u")
                            frictionCoefs["u"] = collidable.frictionCoef
                            collidingObjects["u"] = collidable
                    #top right corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.topright):
                        xDiff = abs(self.rect.right - collidable.rect.left)
                        yDiff = abs(self.rect.top - collidable.rect.bottom)
                        if xDiff < yDiff and self._velocity.x > 0 and "wall" in collidable.tags:
                            renderedDifference[0] += 1
                            if not isPlayer:
                                self.rect.right = collidable.rect.left
                            else:
                                totalDiff[0] += xDiff
                            collidingDirections.append("r")
                            frictionCoefs["r"] = collidable.frictionCoef
                            collidingObjects["r"] = collidable
                        elif xDiff > yDiff and self._velocity.y < 0 and "roof" in collidable.tags:
                            renderedDifference[1] += 1
                            if not isPlayer:
                                self.rect.top = collidable.rect.bottom
                            else:
                                totalDiff[1] -= yDiff
                            collidingDirections.append("u")
                            frictionCoefs["u"] = collidable.frictionCoef
                            collidingObjects["u"] = collidable
                    #bottom right corner
                    if pygame.Rect.collidepoint(collidable.rect, self.rect.bottomright):
                        xDiff = abs(self.rect.right - collidable.rect.left)
                        yDiff = abs(self.rect.bottom - collidable.rect.top)
                        if xDiff < yDiff and self._velocity.x > 0 and "wall" in collidable.tags:
                            renderedDifference[0] += 1
                            if not isPlayer:
                                self.rect.right = collidable.rect.left
                            else:
                                totalDiff[0] += xDiff
                            collidingDirections.append("r")
                            frictionCoefs["r"] = collidable.frictionCoef
                            collidingObjects["r"] = collidable
                        elif xDiff > yDiff and self._velocity.y > 0 and len(set(collidable.tags) & set({"floor", "lCorner", "rCorner"})) > 0:
                            renderedDifference[1] += 1
                            if not isPlayer:
                                self.rect.bottom = collidable.rect.top
                            else:
                                totalDiff[1] += yDiff
                            collidingDirections.append("d")
                            frictionCoefs["d"] = collidable.frictionCoef
                            collidingObjects["d"] = collidable

                    #if isPlayer and renderedDifference[0] > 1:
                    #    totalDiff[0] /= 2
                    #if isPlayer and renderedDifference[1] > 1:
                    if renderedDifference[0] > 1 and isPlayer:
                        totalDiff[0] /= 2
                    if renderedDifference[1] > 1 and isPlayer:
                        totalDiff[1] /= 2
                    #totalDiff[0] *= 2
                    #totalDiff[1] *= 2
                    
                    collisionTolerance = 5
                    '''
                    pygame.Rect.collidepoint doesn't return true if points are bordering on a rect
                    due to this, for frame 1 after floor collision, although the object is technically grounded, renderCollision doesn't return true since the points are "bordering"
                    this causes inaccuracies when calculating friction since friction = resForce.axis in the opposite direction and if the player isn't grounded, UserInputDown can be applied.
                    to solve this, we add a tolerance to the bottom of the rect to check if the object is close enough to be grounded without editing its actual position
                    '''

                    #print("run")
                    #if "d" in collidingDirections:
                    #    self.isGrounded = True
                    #    self.removeForce(axis="y", ref="UserInputDown")
                    #else:
                    #    self.isGrounded = False
        if "d" in collidingDirections:
            #print(self.rect.centery)
            #print(collidingObjects["d"].rect.centery)
            #totalDiff[1] = 0
            #totalDiff[1] = abs(self.rect.bottom - collidingObjects["d"].rect.top)
            #if not self.isGrounded and self.previousGroundedYCoord - 25 < self.absoluteCoordinate.y and self.absoluteCoordinate.y < self.previousGroundedYCoord + 25:
            #    #self.isPostGroundedFrame += 2
            #    totalDiff[1] = displacement.y
            #    self.absoluteCoordinate.y = collidingObjects["d"].absoluteCoordinate.y - self.size.y // 2 - collidingObjects["d"].rect.height // 2#tuple([self.previousGroundedYCoord])[0]
            self.isGrounded = True
            self.removeForce(axis="y", ref="UserInputDown")
            #if self.rect.bottom > collidingObjects["d"].rect.top:
            #    totalDiff[0] -= 3
            self.absoluteCoordinate.y = collidingObjects["d"].absoluteCoordinate.y - self.size.y // 2 - collidingObjects["d"].rect.height // 2#tuple([self.previousGroundedYCoord])[0]
        else:
            self.isGrounded = False
        for direction in collidingDirections:
            if not direction in self.blockedMotion:
                self.blockedMotion.append(direction)
        self.__updateFriction(coef=frictionCoefs)

        #for x in collidingObjects.keys():
        #    if collidingObjects[x] != None:
        #        print(f"{x} - {collidingObjects[x].tags}")
        #print("-------------------")

        if "u" in self.blockedMotion:
            if "roof" in collidingObjects["u"].tags or "wall" in collidingObjects["u"].tags:
                self._velocity.y = max(0, self._velocity.y)
        elif "d" in self.blockedMotion:
            self._velocity.y = min(0, self._velocity.y)
        if "l" in self.blockedMotion:
            #if len({"rCorner", "sandwich"} & set(collidingObjects["l"].tags)) == 0 and not "d" in self.blockedMotion:
            if not("rCorner" in collidingObjects["l"].tags or "sandwich" in collidingObjects["l"].tags):
                self._velocity.x = max(0, self._velocity.x)
            #if collidingObjects["l"] != None:
            #    self.absoluteCoordinate.x = collidingObjects["l"].absoluteCoordinate.x + self.size.x // 2 + collidingObjects["l"].rect.width // 2
        elif "r" in self.blockedMotion:
            #if len({"lCorner", "sandwich"} & set(collidingObjects["r"].tags)) == 0 and not "d" in self.blockedMotion:
            if not("lCorner" in collidingObjects["r"].tags or "sandwich" in collidingObjects["r"].tags):
                self._velocity.x = min(0, self._velocity.x)
            if collidingObjects["r"] != None:
                self.absoluteCoordinate.x = collidingObjects["r"].absoluteCoordinate.x + self.size.x // 2 + collidingObjects["r"].rect.width // 2
            
        return totalDiff

        #if isPlayer:
        #    self.rect.center = (self.rect.centerx - originalDisplacement.x, self.rect.centery - originalDisplacement.y)
        #    return pygame.Vector2(totalDiff[0], totalDiff[1])
        #else:
        #    return None
    
    def camRenderCollisions(
            self,
            collidableObjects: list[pygame.sprite.Group],
            pixelTolerance: int,
            isPlayer: bool=False
    ):
        self.blockedMotion = []

        if isPlayer:
            borders = {
                "tl": (self.rect.left - pixelTolerance, self.rect.top - pixelTolerance),
                "tr": (self.rect.right + pixelTolerance, self.rect.top - pixelTolerance),
                "bl": (self.rect.left - pixelTolerance, self.rect.bottom + pixelTolerance),
                "br": (self.rect.right + pixelTolerance, self.rect.bottom + pixelTolerance)
            }
            response = self.cycleCollidables(
                collidableObjects=collidableObjects,
                borders=borders
            )
            diff = response["diff"]
            frictionCoefs = response["frictionCoefs"]
        else:
            borders = {
                "tl": self.rect.topleft,
                "tr": self.rect.topright,
                "bl": self.rect.bottomleft,
                "br": self.rect.bottomright
            }
            response = self.cycleCollidables(
                collidableObjects=collidableObjects,
                borders=borders
            )
            diff = response["diff"]
            frictionCoefs = response["frictionCoefs"]
        
        #xDiff = [x[0] for x in diff.values() if x[0] != 0]
        #if len(xDiff) != 0 and self._velocity.x < 0:
        #    xDiff = max(xDiff)
        #elif len(xDiff) != 0:
        #    xDiff = min(xDiff)
        #else:
        #    xDiff = 0
        #yDiff = [y[1] for y in diff.values() if y[0] != 0]
        #if len(yDiff) != 0 and self._velocity.y < 0:
        #    yDiff = min(yDiff)
        #elif len(yDiff) != 0:
        #    yDiff = max(yDiff)
        #else:
        #    yDiff = 0


        
        self.__updateFriction(coef=frictionCoefs)
        return pygame.Vector2(diff[0], diff[1]) #(xDiff, yDiff)

    
    def cycleCollidables(
            self,
            collidableObjects: list[pygame.sprite.Group],
            borders: dict[str, int]
    ) -> dict[str, tuple[int, int]]:
        #foundCollisions = {
        #    "u": (None, 0),
        #    "d": (None, 0),
        #    "l": (None, 0),
        #    "r": (None, 0)
        #}

        fCoef = {}
        diff = [0, 0]

        for collidableList in collidableObjects:
            for collidable in collidableList:
                for corner in borders.keys():
                    if pygame.Rect.collidepoint(collidable.rect, borders[corner]):
                        if corner[1:] == "r":
                            xKey = "r"
                            xSide = collidable.rect.left
                            fCoef["r"] = collidable.frictionCoef
                        else:
                            xKey = "l"
                            xSide = collidable.rect.right
                            fCoef["l"] = collidable.frictionCoef
                        if corner[:1] == "u":
                            yKey = "u"
                            ySide = collidable.rect.bottom
                            fCoef["u"] = collidable.frictionCoef
                        else:
                            yKey = "d"
                            ySide = collidable.rect.top
                            fCoef["d"] = collidable.frictionCoef
                        xDiff = xSide - borders[corner][0]
                        yDiff = ySide - borders[corner][1]
                        if abs(xDiff) < abs(yDiff):
                            diff[0] = xDiff
                            #foundCollisions[xKey] = (collidable.rect, collidable.frictionCoef)
                        else:
                            diff[1] = -yDiff
                            #foundCollisions[yKey] = (collidable.rect, collidable.frictionCoef)
        
        #return foundCollisions
        return {
            "diff": diff,
            "frictionCoefs": fCoef
        }

    def addForce(
            self,
            axis: str, #python doesn't have a char datatype, so we need data validation to ensure len(axis) = 1
            direction: str,
            ref: str,
            magnitude: float

    ):
        if self.ignoreYFriction and "friction" in ref.lower() and axis == "y":
            return None
        if len(axis) > 0:
            axis = axis[0:1] #data validation to ensure axis is 1 character
        if direction == "l" or direction == "u": #dirEffect is used to ensure magnitude follows PYGAME's convention (-) = left or up, (+) = down or right
            dirEffect = -1
        else:
            dirEffect = 1
        
        if axis == "x":
            if ref in self._xForces.values(): #presence check for force reference
                self._xForces[ref] = dirEffect*magnitude #if the force exists, add magnitude to it
            else:
                self._xForces[ref] = dirEffect*magnitude #otherwise add it to the dictionary
        else:
            if ref in self._yForces.values():
                self._yForces[ref] = dirEffect*magnitude
            else:
                self._yForces[ref] = dirEffect*magnitude

    def removeForce(
            self,
            axis: str,
            ref: str
    ):
        if len(axis) > 0:
            axis = axis[0:1] #data validation to ensure axis is 1 character
        if axis == "x":
            if ref in self._xForces.keys():
                self._xForces.pop(ref)
        elif ref in self._yForces.keys():
            self._yForces.pop(ref)
    
    def containsForce(self, axis: str, ref: str):
        if len(axis) > 1:
            axis = axis[0:1] #truncate axis to only be 1 character
        if axis == "x":
            return ref in self._xForces.keys()
        else:
            return ref in self._yForces.keys()
    
    def __updateFriction(self, coef: dict):
        self.removeForce(axis="x", ref="xFriction")
        self.removeForce(axis="y", ref="yFriction")
        self.removeForce(axis="x", ref="xAirResistance")
        self.removeForce(axis="y", ref="yAirResistance")

        xAirResistance = 0
        yAirResistance = 0
        xFriction = 0
        yFriction = 0

        airResistanceCoef = 0.01

        strippedResForce = self.recalculateResultantForce()

        if not(-2.75 < self._velocity.x and self._velocity.x < 2.75):
            if not ("l" in coef.keys() or "r" in coef.keys()):
                xAirResistance = abs(airResistanceCoef * self._velocity.x * self.FPS)
            
            xFriction = coef["d"][0]*strippedResForce.y if "d" in coef.keys() else coef["u"][0]*strippedResForce.y if "u" in coef.keys() else 0
            if strippedResForce.x != 0:
                xFriction = min(abs(strippedResForce.x), abs(xFriction))
            xDirection = "r" if self._velocity.x < 0 else "l"
        else:
            xFriction = 0

        if not(-2.75 < self._velocity.y and self._velocity.y < 2.75):
            if not ("d" in coef.keys() or "u" in coef.keys()):
                yAirResistance = abs(airResistanceCoef * self._velocity.y * self.FPS)

            yFriction = coef["l"][1]*strippedResForce.y if "l" in coef.keys() else coef["r"][1]*strippedResForce.y if "r" in coef.keys() else 0
            if strippedResForce.y != 0:
                yFriction = min(abs(strippedResForce.y), abs(yFriction))
            yDirection = "u" if self._velocity.y > 0 else "d"
        else:
            yFriction = 0

        if xFriction != 0:
            self.addForce(axis="x", direction=xDirection, ref="xFriction", magnitude=xFriction) #direction will always be bound if friction != 0, so ignore #type: ignore
        if yFriction != 0:
            self.addForce(axis="y", direction=yDirection, ref="yFriction", magnitude=yFriction) #type: ignore
        if xAirResistance != 0 and ((xFriction != strippedResForce.x and xFriction != 0) or not self.isGrounded):
            self.addForce(axis="x", direction="l" if self._velocity.x > 0 else "r", ref="xAirResistance", magnitude=xAirResistance)
        if yAirResistance != 0 and yFriction != strippedResForce.y:
            self.addForce(axis="y", direction="u" if self._velocity.y < 0 else "d", ref="yAirResistance", magnitude=yAirResistance)


    def killSelf(self):
        self.kill()

    def update(self, collidableObjects, playerMoved=(0, 0)):
        if self.simulated:
            self._resultantForce = self.recalculateResultantForce() #methods are called in dependency order i.e. ResForce is required for getAcceleration() which is required for getVelocity(), etc.
            self._acceleration = self.getAcceleration()
            self.getVelocity()
            self.displaceObject(collidableObjects=collidableObjects, playerMoved=playerMoved)

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())