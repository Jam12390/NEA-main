import pygame
from Entity import Entity
from OtherClasses import Weapon
from dictionaries import allItems
import transfer.pathing as Pathing

hardVCap = pygame.Vector2(200, 200)  # (x, y)
minVCap = pygame.Vector2(75, 50)


class Player(Entity):
    def __init__(
        self,
        FPS: int,
        jumpForce: float,
        maxHP: int,
        defense: int,
        speed: float,
        pAttackCooldown: float,
        pSize: pygame.Vector2,
        spritePath: str,
        pMass: float,
        startingPosition: pygame.Vector2,
        pVelocityCap: pygame.Vector2,
        startingVelocity: pygame.Vector2 = pygame.Vector2(0, 0),
        pTag: str = "None",
        startingWeaponID: int = 0,
    ):
        super().__init__(
            FPS=FPS,
            jumpForce=jumpForce,
            maxHP=maxHP,
            defense=defense,
            speed=speed,
            pAttackCooldown=pAttackCooldown,
            pSize=pSize,
            spritePath=spritePath,
            pMass=pMass,
            startingPosition=startingPosition,
            pVelocityCap=pVelocityCap,
            startingVelocity=startingVelocity,
            pTag=pTag,
        )
        self.inventory = {}
        self.fastFalling = False
        self.crouched = False
        self.weapon = Weapon(
            FPS=FPS,
            pID=startingWeaponID,
            startingPosition=pygame.Vector2(
                round(self.rect.centerx), round(self.rect.centery)
            ),
        )
        self.facing = "r"
        self.ignoreAccelFrames = 0

        self.currentNode = (
            ((self.absoluteCoordinate.x) // 75),
            (self.absoluteCoordinate.y) // 75 + 6,
        )

    def pickupItem(self, ID: int, quantity: int = 1, replaces: str = ""):
        newData = None
        if replaces == "weapon":
            newData = {
                "ID": self.weapon.ID,
                "quantity": quantity
            }
            self.weapon.killSelf()  # destroy the current weapon
            self.weapon = Weapon(
                FPS=self.FPS,
                pID=ID,
                startingPosition=pygame.Vector2(
                    round(self.rect.centerx), round(self.rect.centery)
                ),
            )  # and replace it with a new instance of the picked up weapon
            
        elif (
            ID in self.inventory.keys()
        ):  # if there is nothing to replace and the item is in the inventory
            self.inventory[ID][2] += quantity  # increment the quantity of said item
            
        elif replaces.isdigit():  # if replaces is an ID (defaults to item)
            if (
                int(replaces) in self.inventory.keys()
            ):  # presence check for item to replace
                newData = {
                    "ID": int(replaces),
                    "quantity": quantity
                }
                self.inventory.pop(int(replaces))  # delete it
            self.inventory[ID] = [
                "item",
                allItems[ID]["description"],
                quantity,
            ]  # add the new item to the inventory

        else:  # otherwise
            self.inventory[ID] = [
                "item",
                allItems[ID]["description"],
                1,
            ]  # add the item normally
        self._recalculateAttributes()
        return newData

    def _recalculateAttributes(self):
        self._maxHP = self._originalAttributes["maxHP"]
        self._defense = self._originalAttributes["defense"]
        self._speed = self._originalAttributes["speed"]
        self.attackCooldown = self._originalAttributes["attackCooldown"]

        keys = [item for item in self.inventory.keys()]
        values = [value for value in self.inventory.values()]

        for index in range(
            0, len(keys)
        ):  # value is in format [tag: string, details: string]
            key = keys[index]
            value = values[index]
            if value[0] == "item":
                splitValue = allItems[key]["effects"].split(", ")
                splitEffects = [
                    item.split(" ") for item in splitValue
                ]  # double split to cover items which affect multiple attributes
                for (
                    effect
                ) in (
                    splitEffects
                ):  # effect is now in format [variableAffected: string, operator: string, operand: float]
                    for i in range(value[2]):
                        self.modifyStat(effect[0], effect[1], float(effect[2]))

        effectValues = [value for value in self._effects.values()]

        for index in range(0, len(effectValues)):
            splitValue = effectValues[index].split(
                ", "
            )  # double split to cover effects which affect multiple attributes
            splitEffects = [item.split(" ") for item in splitValue]
            for effect in splitEffects:
                self.modifyStat(effect[0], effect[1], effect[2])

        # increase speed cap by a factor of _speed
        self._velocityCap.x = self._baseVCap[0] * self._speed
        if abs(self._velocityCap.x) > hardVCap.x:
            self._velocityCap.x = hardVCap.x
        elif abs(self._velocityCap.x) < minVCap.x:
            self._velocityCap.x = minVCap.x

        self._velocityCap.y = self._baseVCap[1] * self._speed
        if abs(self._velocityCap.y) > hardVCap.y:
            self._velocityCap.y = hardVCap.y
        elif abs(self._velocityCap.y) < minVCap.y:
            self._velocityCap.y = minVCap.y

        self._baseVCap = self._originalAttributes["baseVCap"]

    def crouch(self):
        self.rect.height //= 2  # make player shorter
        self.rect.centery += self.rect.height
        self.crouched = True  # crouch

    def uncrouch(self):
        self.crouched = False  # uncrouch
        self.rect.centery -= self.rect.height  # move centre up
        self.rect.height *= 2  # make player taller again

    def wallJump(self):
        self.ignoreAccelFrames = 10 * max(1, self._speed / 4)
        # print("the wall")
        if "l" in self.blockedMotion:
            self._velocity.x = 50
            self.rect.centerx += 3
            self.facing = "r"
        elif "r" in self.blockedMotion:
            self._velocity.x = -50
            self.rect.centerx -= 3
            self.facing = "l"

        self._velocity.y = -40

    def update(self, collidableObjects) -> pygame.Vector2:
        for key in self._effects.keys():
            self._effects[key][1] -= (
                1 / self.FPS
            )  # FPS is set off a global variable to enable smooth motion
            if self._effects[key][1] <= 0:
                self.removeEffect(
                    ID=int(key.split("-")[0]), instance=key.split("-")[1], forced=False
                )

        if self.simulated:
            # self._recalculateAttributes()

            if self.crouched:
                self.removeForce(axis="x", ref="UserInputLeft")
                self.removeForce(axis="x", ref="UserInputRight")

            self._resultantForce = self.recalculateResultantForce(
                forceMult=self._speed,
                includedForces=["UserInputLeft", "UserInputRight", "UserInputDown"],
            )
            self._acceleration = self.getAcceleration()
            if self.ignoreAccelFrames > 0:
                match self.facing:
                    case "l":
                        self._acceleration.x = min(self._acceleration.x, 0)
                    case "r":
                        self._acceleration.x = max(0, self._acceleration.x)
                self.ignoreAccelFrames -= 1
            self.getVelocity(turnForce=self._speed)

            displacement = self.displaceObject(
                collidableObjects=collidableObjects, isPlayer=True
            )

            if round(displacement.x) != 0:  # if we are actually registering movement
                if self._velocity.x < 0:  # then allow self.facing to change
                    self.facing = "l"
                else:
                    self.facing = "r"

            match self.facing:
                case "l":
                    self.weapon.rect.right = round(self.rect.left)
                case "r":
                    self.weapon.rect.left = round(self.rect.right)

            self.weapon.rect.centery = round(self.rect.centery)
            self.weapon.update()

            self.rect.clamp_ip(pygame.display.get_surface().get_rect())

            return displacement  # playerMoved


class Enemy(Entity):
    def __init__(
        self,
        FPS,
        jumpForce,
        maxHP,
        defense,
        speed,
        pAttackCooldown,
        pSize,
        spritePath,
        pMass,
        startingPosition,
        pVelocityCap,
        startingVelocity=...,
        pAggroRange=300,
        pFacing="r",
        weaponID=0,
        pTag="Enemy",
        pIgnoreYFriction=False,
    ):
        super().__init__(
            FPS,
            jumpForce,
            maxHP,
            defense,
            speed,
            pAttackCooldown,
            pSize,
            spritePath,
            pMass,
            startingPosition,
            pVelocityCap,
            startingVelocity,
            pTag,
            pIgnoreYFriction,
        )
        self.aggroRange = pAggroRange
        self.aggrod = False
        self.seen = False
        self.weapon = Weapon(
            FPS=FPS,
            pID=weaponID,
            startingPosition=pygame.Vector2(
                round(self.rect.centerx), round(self.rect.centery)
            ),
        )
        self.framesSinceLastPath = 0
        self.framesSinceLastSight = 0

        self.currentNode = (
            int((self.absoluteCoordinate.x) // 75),
            int((self.absoluteCoordinate.y) // 75 + 6),
        )

        self.sightRect = pygame.Rect(
            self.rect.centerx, self.rect.centery, pAggroRange * 2, 10
        )

        self.facing = pFacing

    def update(
        self,
        collidableObjects,
        precompiledData,
        nodeMap,
        nodeSep,
        pathingTo,
        playerRect,
    ):
        self.framesSinceLastPath += 1
        self.simulated = self.currentNode[1] in range(
            int(pathingTo[1] - 10), int(pathingTo[1] + 10)
        )
        if self.simulated:
            self.seen = pygame.Rect.colliderect(self.sightRect, playerRect)

            if not self.seen:
                self.framesSinceLastSight += 1
            else:
                self.aggrod = True
                self.framesSinceLastSight = 0
            if self.framesSinceLastSight > 180:  # 3 secs
                self.aggrod = False

            if self.framesSinceLastPath > 0:  #
                self.path(
                    pathingTo=pathingTo,
                    precompiledData=precompiledData,
                    nodeMap=nodeMap,
                    nodeSep=nodeSep,
                )
                self.framesSinceLastPath = 0

            self.shouldPath = self.aggrod

            self._resultantForce = self.recalculateResultantForce(
                forceMult=self._speed, includedForces=[]
            )
            self._acceleration = self.getAcceleration()
            self.getVelocity()

            displacement = self.displaceObject(collidableObjects=collidableObjects)

            if -2.5 < displacement.x and displacement.x < 2.5:
                displacement.x = 0
            if -0.25 < displacement.y and displacement.y < 0.25:
                displacement.y = 0

            if self.currentNode == self.previousPathCoord:
                self.framesSinceLastNode += 1

            self.rect.center += displacement
            self.absoluteCoordinate += displacement

            self.currentNode = (
                int((self.absoluteCoordinate.y) // 75),  # (y, x)
                int(((self.absoluteCoordinate.x) // 75)),
            )
        else:
            self.framesSinceLastSight += 1
            self.shouldPath = False
            self.currentPath = []
