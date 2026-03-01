import pygame
import transfer.pathing as pathing

pygame.init()


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, pSize, position, fontName, maxHP, currentHP):
        super().__init__()

        self.__maxHP = maxHP
        self.__currentHP = currentHP
        self.__position = position

        self.__remainingBar = pygame.Surface(
            size=pSize * (self.__currentHP / self.__maxHP)
        )
        self.__remainingBar.fill((0, 255, 0))
        self.__totalBar = pygame.Surface(size=pSize)
        self.__totalBar.fill((255, 0, 0))

        self.__remainingRect = pygame.Surface.get_rect(self.__remainingBar)
        self.__totalRect = pygame.Surface.get_rect(self.__totalBar)

        self.__textColour = pygame.Color(255, 255, 255)
        self.__font = pygame.font.SysFont(name=fontName, size=20, bold=True)
        self.__text = self.__font.render(
            f"{currentHP}/{maxHP}", False, self.__textColour
        )
        self.__textRect = pygame.Surface.get_rect(self.__text)

        self.surface = pygame.Surface(size=pSize)
        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.topleft = position

    def changeHP(self, magnitude):
        self.__currentHP = pathing.clamp(
            inp=(self.__currentHP + magnitude), mini=0, maxi=self.__maxHP
        )
        self.__remainingBar = pygame.Surface(
            size=(
                round(
                    (self.__totalBar.get_width() * (self.__currentHP / self.__maxHP)),
                ),
                50,
            )
        )
        self.__remainingBar.fill((0, 255, 0))
        self.__remainingRect = pygame.Surface.get_rect(self.__remainingBar)
        position = self.__totalRect.topleft
        self.__remainingRect.topleft = position

    def getText(self):
        self.__text = self.__font.render(
            f"{self.__currentHP}/{self.__maxHP}", False, self.__textColour
        )
        self.__textRect = pygame.Surface.get_rect(self.__text)
        self.__textRect.left = 15
        self.__textRect.centery = self.surface.get_height() // 2

    def isDead(self):
        return self.__currentHP == 0

    def update(self):
        self.getText()
        self.surface.blit(self.__totalBar, self.__totalRect)
        self.surface.blit(self.__remainingBar, self.__remainingRect)
        self.surface.blit(self.__text, self.__textRect)
