import pygame
try:
    from Prototype1.dictionaries import allWeapons, allItems
except:
    from dictionaries import allWeapons, allItems

class Weapon(pygame.sprite.Sprite):
    def __init__(self, FPS: int, pID: int, startingPosition: pygame.Vector2):
        super().__init__()
        self.ID = pID
        self.FPS = FPS
        self.__replaces = "weapon"
        self.image = pygame.transform.smoothscale(pygame.image.load(allWeapons[pID]["imgPath"]), (25, 25))
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(startingPosition.x), round(startingPosition.y))
        self.damage = allWeapons[pID]["damage"]
        self.currentlyAttacking = False
        self.__attackTimer = 0
        self.__anim = {"time": 1.5} #placeholder for anim dictionary
    
    def playAnim(self):
        pass

    def attack(self, parent):
        if parent.simulated and self.__attackTimer <= 0: #the instance of parent will be whichever entity has the weapon (e.g. Player.simulated)
            self.currentlyAttacking = True
            self.__attackTimer = self.__anim["time"] #treating __anim as a map here since it's the easiest to read and understand
            self.playAnim()
    
    def update(self):
        self.__attackTimer -= 1/self.FPS
        if self.__attackTimer <= 0:
            self.currentlyAttacking = False
    
    def killSelf(self):
        self.kill()

class WallObj(pygame.sprite.Sprite):
    def __init__(
            self,
            size: pygame.Vector2,
            position: pygame.Vector2,
            frictionCoef: tuple[int, int] = (0,75, 0,25), #(x, y)
            spritePath: str = "Sprites/DefaultSprite.png",
            #######REVERT A
            pTags: list[str] = ["wall"]
            #END
        ):
        super().__init__()
        self.image = pygame.transform.smoothscale(pygame.image.load(spritePath), (round(size.x), round(size.y)))
        #revert a
        self.tags = pTags
        #end
        self.frictionCoef = frictionCoef
        self.simulated = True
        #revert
        self.absoluteCoordinate = position
        #end
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(position.x), round(position.y))
    
    def killSelf(self):
        self.kill()
    
    def update(self) -> None:
        #offset = pygame.Vector2(
        #    round(offset.x),
        #    round(offset.y)
        #)
        #self.rect.centerx += offset.x
        #self.rect.centery += offset.y
        pass
    
    #def update(self):
    #    pass

class ItemUIWindow(pygame.sprite.Sprite):
    def __init__(self, itemID, replaces, pos, size):
        super().__init__()
        self.itemID = itemID
        itemName = allItems[itemID]["name"]
        itemDesc = allItems[itemID]["description"]
        itemEffects = allItems[itemID]["effects"]
        itemReplaces = replaces
        self.shown = False
        self.size = size

        self.pos = pos

        font = pygame.font.SysFont("Calibri", 16)
        textColour = (0, 0, 0)
        self.title = font.render(f"{self.itemID} - {itemName}", False, textColour)
        self.subtitle = font.render(f"! - Replaces {itemReplaces}   Effects: {itemEffects}", False, textColour)
        self.desc = font.render(itemDesc, False, textColour)

        self.surface = pygame.Surface(self.size)
        self.surface.fill((175, 175, 175))
        self.surface.set_alpha(150)
        self.surface.blit(self.title, (25, 10))
        self.surface.blit(self.subtitle, (25, 46))
        self.surface.blit(self.desc, (25, 100))

        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.center = (pos[0], pos[1])
    
    def update(self):
        self.surface.blit(self.title, (25, 10))
        self.surface.blit(self.subtitle, (25, 46))
        self.surface.blit(self.desc, (25, 100))
    
    def killSelf(self):
        self.kill()

class Item(pygame.sprite.Sprite):
    def __init__(
            self,
            pID: int,
            startingPosition: pygame.Vector2,
            UIWindow: ItemUIWindow
        ):
        super().__init__()
        self.ID = pID
        self.tag = "item"
        self.__replaces = allItems[pID]["replaces"]
        self.surface = pygame.Surface((175, 175))
        self.image = pygame.transform.smoothscale(pygame.image.load(allItems[pID]["imgPath"]), (100, 100))
        self.surface.blit(self.image, (175//2, 175//2))
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (round(startingPosition.x), round(startingPosition.y))
        self.UIWindow = UIWindow
    
    def update(self):
        #self.rect.centerx += playerMoved.x
        #self.rect.centery += playerMoved.y
        self.surface.blit(self.image, (175//2, 175//2))

    def pickup(self, target):
        newData = target.pickupItem(ID=self.ID, replaces=self.__replaces)
        if newData == None:
            self.killSelf()
        else:
            self.swapItem(newID=newData)
            bufferPos = self.UIWindow.pos
            bufferSize = self.UIWindow.size
            self.UIWindow.killSelf()
            self.UIWindow = ItemUIWindow(
                itemID=self.ID,
                replaces=self.__replaces,
                pos=bufferPos,
                size=bufferSize
            )
    
    def swapItem(self, newID: int):
        self.ID = newID
        if self.__replaces == "weapon":
            self.__replaces = "weapon"
            self.image = pygame.transform.smoothscale(pygame.image.load(allWeapons[newID]["imgPath"]), (100, 100))
        else:
            self.__replaces = allItems[newID]["replaces"]
            self.image = pygame.transform.smoothscale(pygame.image.load(allItems[newID]["imgPath"]), (100, 100))
    
    def killSelf(self):
        self.UIWindow.killSelf()
        self.kill()