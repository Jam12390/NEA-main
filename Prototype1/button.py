import pygame
import typing

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
            hoverOffset: pygame.Vector2 = pygame.Vector2(0, 0)
    ):
        self.font = pygame.font.SysFont(fontName, size=textSize)

        self.text = self.font.render(text, False, textColour)
        self.textRect = pygame.Surface.get_rect(self.text)

        self.surface = pygame.Surface(self.textRect.size + pygame.Vector2(25, 25))#pygame.Surface((round(size.x), round(size.y)))
        self.surface.fill(buttonColour)

        self.textRect.center = (self.surface.get_width() // 2, self.surface.get_height() // 2)

        self.surface.blit(self.text, self.textRect)

        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.center = (round(position.x), round(position.y))

        self.colour = buttonColour
        self.hoveredOver = False
        self.hoverColour = hoverColour
        self.hoverOffset = hoverOffset
        self.onClick = func
    
    def checkForHover(self, mousePos):
        inRangeX = mousePos[0] in range(int(self.rect.left + self.hoverOffset.x), int(self.rect.right + self.hoverOffset.x))
        inRangeY = mousePos[1] in range(int(self.rect.top + self.hoverOffset.y), int(self.rect.bottom + self.hoverOffset.y))

        if inRangeX and inRangeY:
            self.hoveredOver = True
            self.surface.fill(self.hoverColour)
        else:
            self.hoveredOver = False
            self.surface.fill(self.colour)
    
    def update(self, mousePos):
        self.checkForHover(mousePos=mousePos)
        self.surface.blit(self.text, self.textRect)

def wrapText(plainText: str, wordsPerLine: int):
    words = plainText.split(" ")
    currentLength = 0
    lines = []
    currentLine = ""
    while len(words) > 0:
        currentLine += f"{words[0]} "
        currentLength += 1
        words.pop(0)
        if currentLength >= wordsPerLine:
            lines.append(currentLine)
            currentLine = ""
            currentLength = 0
    
    if len(currentLine) > 0:
        lines.append(currentLine)
    
    return lines

class Description(pygame.sprite.Sprite):
    def __init__(
            self,
            pos: pygame.Vector2,
            text: list[str],
            font="Calibri",
            fontSize=25,
            yOffset: int=75
        ):

        self.font = pygame.font.SysFont(font, fontSize)
        self.lines = [self.font.render(line, False, (0, 0, 0)) for line in text]

        self.lineSize = fontSize + 10

        self.background = pygame.Surface((275, len(self.lines) * self.lineSize + 20))
        self.background.fill((200, 200, 200))

        lineNumber = 0
        for line in self.lines:
            self.background.blit(line, (10, lineNumber * self.lineSize + 15))
            lineNumber += 1
        
        self.rect = pygame.Surface.get_rect(self.background)
        self.rect.centerx = round(pos.x)
        self.rect.centery = round(pos.y + yOffset)


class ImageButton(pygame.sprite.Sprite):
    def __init__(
            self,
            position: pygame.Vector2, #the absolute position
            imgPath: str,
            func,
            text: list[str],
            #textColour: pygame.Color = pygame.Color(0, 0, 0),
            buttonColour: pygame.Color = pygame.Color(175, 175, 175),
            hoverColour: pygame.Color = pygame.Color(60, 60, 60),
            #fontName: str = "Calibri",
            #textSize: int = 15,
            hoverOffset: pygame.Vector2 = pygame.Vector2(0, 0),
            size: pygame.Vector2 = pygame.Vector2(100, 100),
            descriptionOffset: pygame.Vector2 = pygame.Vector2(0, 0), #if the position is an offset relative to its parent's position
            absoluteDescriptionPosition: typing.Optional[pygame.Vector2] = None,
            imageRectOffset: pygame.Vector2 = pygame.Vector2(0, 0)
        ) -> None:
        super().__init__()

        self.image = pygame.transform.smoothscale(pygame.image.load(imgPath), size=size)

        self.surface = pygame.Surface((size.x, size.y))
        self.surface.fill(buttonColour)
        self.surface.blit(self.image, (0, 0))

        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.center = (position.x, position.y)

        self.hoveredOver = False
        self.hoverColour = hoverColour
        self.colour = buttonColour

        self.hoverOffset = hoverOffset

        self.onClick = func

        if absoluteDescriptionPosition == None:
            self.description = Description(
                pos=position + descriptionOffset,
                text=text
            )
        else:
            self.description = Description(
                pos=absoluteDescriptionPosition,
                text=text
            )

    def checkForHover(self, mousePos):
        inRangeX = mousePos[0] in range(int(self.rect.left + self.hoverOffset.x), int(self.rect.right + self.hoverOffset.x))
        inRangeY = mousePos[1] in range(int(self.rect.top + self.hoverOffset.y), int(self.rect.bottom + self.hoverOffset.y))

        if inRangeX and inRangeY:
            self.hoveredOver = True
            self.surface.fill(self.hoverColour)
        else:
            self.hoveredOver = False
            self.surface.fill(self.colour)
    
    def update(self, mousePos):
        self.checkForHover(mousePos=mousePos)
        self.surface.blit(self.image, (0, 0))