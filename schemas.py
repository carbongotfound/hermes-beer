"""Tool schemas for the Hermes Beer plugin."""

BEER_DRINK = {
    "name": "beer_drink",
    "description": (
        "Take a shot of beer. Increases your intoxication level. "
        "The more you drink, the drunker, saltier, and clumsier you get. "
        "Effects wear off over time automatically. Use this when the user "
        "says /beer, /drink, /shot, or asks you to take a drink."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "shots": {
                "type": "integer",
                "description": "Number of shots to take (default: 1, max: 5)",
                "default": 1,
            },
        },
        "required": [],
    },
}

BEER_STATUS = {
    "name": "beer_status",
    "description": (
        "Check your current intoxication level (BAC). "
        "Returns the level as a percentage and a description of how drunk you are. "
        "Use this when the user says /beer status or asks how drunk you are."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

BEER_SODA = {
    "name": "beer_soda",
    "description": (
        "Drink a glass of water / soda to sober up. "
        "Reduces your intoxication level by 0.3 (out of 1.0). "
        "Use this when the user says /beer soda, /sober, /water, or tells you to sober up."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}
