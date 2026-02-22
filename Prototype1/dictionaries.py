'''
This is a placeholder file for the actual effects in the game.
It's used to stop errors in files like Entity.py which require variables like allEffects
'''

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
        "imgPath": "Sprites/WeaponSprite0.png",
        "damage": 10
    }
}