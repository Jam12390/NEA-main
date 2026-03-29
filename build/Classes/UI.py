import pygame

try:
    from ..Pathing import pathing
except:
    from Pathing import pathing

import typing

pygame.init()

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, size, position, fontName, maxHP, currentHP):
        super().__init__()

        # Metadata
        self.__maxHP = maxHP
        self.__currentHP = currentHP
        self.__position = position # // Unused, but assigned for future use if needed

        # Surfaces
        self.__remainingBar = pygame.Surface(
            size=size * (self.__currentHP / self.__maxHP)
        )
        self.__remainingBar.fill((0, 255, 0))
        self.__totalBar = pygame.Surface(size=size)
        self.__totalBar.fill((255, 0, 0))

        # Rects
        self.__remainingRect = pygame.Surface.get_rect(self.__remainingBar)
        self.__totalRect = pygame.Surface.get_rect(self.__totalBar)

        # Overlayed text
        self.__textColour = pygame.Color(255, 255, 255)
        self.__font = pygame.font.SysFont(name=fontName, size=20, bold=True)
        self.__text = self.__font.render(
            f"{currentHP}/{maxHP}", False, self.__textColour
        )
        self.__textRect = pygame.Surface.get_rect(self.__text)

        # Shown attributes and rect alignment
        self.surface = pygame.Surface(size=size)
        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.topleft = position

    def changeHP(self, magnitude):
        # Clamping stops health from becoming negative
        self.__currentHP = pathing.clamp(
            inp=(self.__currentHP + magnitude), mini=0, maxi=self.__maxHP
        )

        # Setup the remainingBar surface again
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
    
    def resetHP(self):
        # // We can just add maxHP to currentHP since it gets clamped anyway
        # // The separate function helps to differentiate what's being done in the main program
        self.changeHP(self.__maxHP)

    def getText(self): # // This is more like updating text, however they both mean the same thing
        self.__text = self.__font.render(
            f"{self.__currentHP}/{self.__maxHP}", False, self.__textColour
        )
        self.__textRect = pygame.Surface.get_rect(self.__text)
        self.__textRect.left = 15
        self.__textRect.centery = self.surface.get_height() // 2

    def isDead(self):
        return self.__currentHP == 0

    def update(self):
        # Update text
        self.getText()
        # Redraw self
        self.surface.blit(self.__totalBar, self.__totalRect)
        self.surface.blit(self.__remainingBar, self.__remainingRect)
        self.surface.blit(self.__text, self.__textRect)


class TextButton(pygame.sprite.Sprite):
    def __init__(
        self,
        position: pygame.Vector2,
        text: str,
        func,
        descriptionText: str = "",
        descriptionOffset: pygame.Vector2 = pygame.Vector2(
            0, 0
        ),  # if the position is an offset relative to its parent's position
        absoluteDescriptionPosition: typing.Optional[pygame.Vector2] = None,
        textColour: pygame.Color = pygame.Color(0, 0, 0),
        buttonColour: pygame.Color = pygame.Color(175, 175, 175),
        hoverColour: pygame.Color = pygame.Color(60, 60, 60),
        fontName: str = "Calibri",
        textSize: int = 15,
        hoverOffset: pygame.Vector2 = pygame.Vector2(0, 0),
        titleFirst: bool = False
    ):
        # Initialising font and text
        self.__font = pygame.font.SysFont(fontName, size=textSize)

        self.__text = self.__font.render(text, False, textColour)
        self.__textRect = pygame.Surface.get_rect(self.__text)

        # Background to draw on
        self.surface = pygame.Surface(
            # // Uses textRect.size as a reference point to wrap the button around the text's size itself
            self.__textRect.size + pygame.Vector2(25, 25)
        )
        self.surface.fill(buttonColour)

        # Positioning
        self.__textRect.center = (
            self.surface.get_width() // 2,
            self.surface.get_height() // 2,
        )

        # Drawing
        self.surface.blit(self.__text, self.__textRect)

        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.topleft = (round(position.x), round(position.y))

        # Aesthetics and hover attributes
        self.colour = buttonColour
        self.hoveredOver = False
        self.hoverColour = hoverColour
        self.hoverOffset = hoverOffset
        self.onClick = func

        # Checking what logic to use when positioning description
        if absoluteDescriptionPosition == None and descriptionText != "": # Assuming there is one
            self.description = Description(
                pos=position + descriptionOffset, text=descriptionText, titleFirst=titleFirst, fontSize=textSize - 3
            )
        elif descriptionText != "":
            self.description = Description(
                pos=absoluteDescriptionPosition, text=descriptionText, titleFirst=titleFirst, fontSize=textSize - 3
            )
        else:
            self.description = None

    def checkForHover(self, mousePos):
        # Checks if the mouse's x and y coordinates are in range of the button's rect
        inRangeX = mousePos[0] in range(
            int(self.rect.left + self.hoverOffset.x),
            int(self.rect.right + self.hoverOffset.x),
        )
        inRangeY = mousePos[1] in range(
            int(self.rect.top + self.hoverOffset.y),
            int(self.rect.bottom + self.hoverOffset.y),
        )

        if inRangeX and inRangeY:
            # Sets hoveredOver to true and fill self with hoverColour
            self.hoveredOver = True
            self.surface.fill(self.hoverColour)
        else:
            # Otherwise resets the button's state
            self.hoveredOver = False
            self.surface.fill(self.colour)

    def update(self, mousePos):
        # Update hover logic
        self.checkForHover(mousePos=mousePos)
        # And redraw
        self.surface.blit(self.__text, self.__textRect)


def wrapText(plainText: str, wordsPerLine: int):
    words = plainText.split(" ") # Split into separate words
    currentLength = 0
    lines = []
    currentLine = ""
    while len(words) > 0:
        currentLine += f"{words[0]} " # And append each word to the current line
        currentLength += 1
        words.pop(0)
        if currentLength >= wordsPerLine: # Until the maximum number of words is reached
            lines.append(currentLine) # In which case add the current line to the list of lines
            currentLine = "" # And reset it's data
            currentLength = 0

    if len(currentLine) > 0:
        lines.append(currentLine) # Adds the last line if it's not empty

    return lines


class Description(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: pygame.Vector2,
        text: list[str],
        font="Calibri",
        fontSize=20,
        yOffset: int = 75,
        backgroundColour: pygame.Color = pygame.Color(175, 175, 175),
        titleFirst: bool = False # A parameter which says if the first line in text is meant to be a title
    ):

        # Fonts
        self.__font = pygame.font.SysFont(font, fontSize)
        self.__titleFont = pygame.font.SysFont(font, fontSize + 10) # and is used when checking if titleFont should be used

        if titleFirst:
            # Renders the first line in lines using titleFont
            self.lines = [self.__titleFont.render(text[0], True, (0, 0, 0))]
            text.pop(0) # Then removes it
        else:
            self.lines = [] # Otherwise initialise lines as an empty list
        
        # Render the rest of the lines
        self.lines.extend(self.__font.render(line, False, (0, 0, 0)) for line in text)

        self.lineSize = fontSize + 10

        # Surface
        self.background = pygame.Surface((270, len(self.lines) * self.lineSize + 60))
        self.background.fill(backgroundColour)

        lineNumber = 0
        for line in self.lines:
            # Draws each line equally spaced from one another
            self.background.blit(line, (10, lineNumber * self.lineSize + 15))
            if titleFirst:
                # Doubles the gap between the title and the next line
                lineNumber += 1
                titleFirst = False
            lineNumber += 1

        # Rect and rect positioning
        self.rect = pygame.Surface.get_rect(self.background)
        self.rect.left = round(pos.x)
        self.rect.top = round(pos.y + yOffset)


class ImageButton(pygame.sprite.Sprite):
    def __init__(
        self,
        position: pygame.Vector2,  # the absolute position
        imgPath: str,
        func,
        text: list[str],
        buttonColour: pygame.Color = pygame.Color(175, 175, 175),
        hoverColour: pygame.Color = pygame.Color(60, 60, 60),
        hoverOffset: pygame.Vector2 = pygame.Vector2(0, 0),
        size: pygame.Vector2 = pygame.Vector2(200, 100),
        descriptionOffset: pygame.Vector2 = pygame.Vector2(
            0, 0
        ),  # if the position is an offset relative to its parent's position
        absoluteDescriptionPosition: typing.Optional[pygame.Vector2] = None,
        data = None,
        titleFirst = False
    ) -> None:
        super().__init__()

        self.data = data # Can be None

        # Image surface
        self.image = pygame.transform.smoothscale(pygame.image.load(imgPath), size=size)

        # Background surface
        self.surface = pygame.Surface((size.x, size.y))
        self.surface.fill(buttonColour)
        self.surface.blit(self.image, (0, 0))

        # Rect
        self.rect = pygame.Surface.get_rect(self.surface)
        self.rect.center = (position.x, position.y)

        # Hover attributes
        self.hoveredOver = False
        self.hoverColour = hoverColour
        self.colour = buttonColour
        self.hoverOffset = hoverOffset
        self.onClick = func

        # Logic for positioning the description
        if absoluteDescriptionPosition == None:
            self.description = Description(pos=position + descriptionOffset, text=text, titleFirst=titleFirst)
        else:
            self.description = Description(pos=absoluteDescriptionPosition, text=text, titleFirst=titleFirst)

    def checkForHover(self, mousePos):
        # Same as TextButton
        inRangeX = mousePos[0] in range(
            int(self.rect.left + self.hoverOffset.x),
            int(self.rect.right + self.hoverOffset.x),
        )
        inRangeY = mousePos[1] in range(
            int(self.rect.top + self.hoverOffset.y),
            int(self.rect.bottom + self.hoverOffset.y),
        )

        if inRangeX and inRangeY:
            self.hoveredOver = True
            self.surface.fill(self.hoverColour)
        else:
            self.hoveredOver = False
            self.surface.fill(self.colour)

    def update(self, mousePos):
        # Same as TextButton
        self.checkForHover(mousePos=mousePos)
        self.surface.blit(self.image, (0, 0))