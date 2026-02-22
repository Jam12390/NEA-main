import pygame

class Button(pygame.sprite.Sprite):
    def __init__(
            self,
            position: pygame.Vector2,
            text: str,
            func,
            textColour: pygame.Color = pygame.Color(0, 0, 0),
            buttonColour: pygame.Color = pygame.Color(175, 175, 175),
            hoverColour: pygame.Color = pygame.Color(60, 60, 60),
            fontName: str = "Calibri",
            textSize: int = 15,
            size: pygame.Vector2 = pygame.Vector2(150, 50)
    ):
        self.size = size
        self.font = pygame.font.SysFont(fontName, size=textSize)

        self.text = self.font.render(text, False, textColour)
        self.textRect = pygame.Surface.get_rect(self.text)
        self.textRect.center = (round(size.x/2), round(size.y/2))

        self.surface = pygame.Surface((round(size.x), round(size.y)))
        self.surface.fill(buttonColour)
        self.surface.blit(self.text, self.textRect)

        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.center = (round(position.x), round(position.y))

        self.colour = buttonColour
        self.hoveredOver = False
        self.hoverColour = hoverColour
        self.onClick = func
    
    def checkForHover(self, mousePos):
        inRangeX = mousePos[0] in range(self.rect.left, self.rect.right)
        inRangeY = mousePos[1] in range(self.rect.top, self.rect.bottom)

        if inRangeX and inRangeY:
            self.hoveredOver = True
            self.surface.fill(self.hoverColour)
        else:
            self.hoveredOver = False
            self.surface.fill(self.colour)
    
    def update(self, mousePos):
        self.checkForHover(mousePos=mousePos)
        self.surface.blit(self.text, self.textRect)