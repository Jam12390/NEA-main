'''
This is a placeholder file for the actual effects in the game.
It's used to stop errors in files like Entity.py which require variables like allEffects
'''
import pygame

allEffects = {}

allItems = {
    0: {
        "imgPath": "Sprites/ItemSprite0.png",
        "name": "TestItem",
        "replaces": "1",
        "description": "A test item... Should make you move really fast",
        "effects": "speed * 5",
    },
    1: {
        "imgPath": "Sprites/ItemSprite1.png",
        "name": "TheOtherTestItem",
        "replaces": "0",
        "description": "A test item... Should replace ID 0",
        "effects": "speed * 0.5",
    }
}

allWeapons = {
    0: {
        "imgPath": "Sprites/GlassShard.png", #https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fwww.pixilart.com%2Fart%2Fglass-shard-632f6eebfe9be52&ved=0CBYQjRxqFwoTCJjijaqQ8pIDFQAAAAAdAAAAABAI&opi=89978449
        "damage": 10,
        "initialRotation": -90,
        "inventoryOffset": pygame.Vector2(-35, 25)
    }
}

allCharacters = {
    0: {
        "name": "OJ",
        "imgPath": "Sprites/ItemSprite0.png",
        "hp": 100,
        "defense": 5,
        "speed": 1,
        "jumpForce": 100,
        "attackCooldown": 0.75,
        "size": pygame.Vector2(50, 50)
    },
    1: {
        "name": "man",
        "imgPath": "Sprites/ItemSprite1.png",
        "hp": 100,
        "defense": 5,
        "speed": 1,
        "jumpForce": 150,
        "attackCooldown": 0.75,
        "size": pygame.Vector2(50, 50)
    }
}