import enum

DIRECTIONS = [
    ("east", "e"),
    ("west", "w"),
    ("north", "n"),
    ("south", "s"),
    ("northeast", "ne"),
    ("northwest", "nw"),
    ("southeast", "se"),
    ("southwest", "sw"),
    ("up", "u"),
    ("down", "d"),
]

Direction = enum.Enum(
    value='Direction',
    names=[(full_name, i) for (i, (full_name, shortcut)) in enumerate(DIRECTIONS)] + \
        [(shortcut, i) for (i, (full_name, shortcut)) in enumerate(DIRECTIONS)]
)

class Location(object):
    """This is a place in the game"""
    def __init__(self, name, description, short_description=None):
        self.name = name
        self.description = description
        self.short_description = short_description or description
        self.exits = {}

    def add_exit(self, direction, destination):
        self.exits[direction] = destination


class Object(object):
    """This is anything that can exist at a location"""
    pass

class Item(Object):
    """This is a non-character object"""
    pass

class Character(Object):
    """This is a character who can move around"""
    pass

locations = {
    "hobbit-hole": Location("hobbit-hole", "a comfortable tunnel like hall"),
    "lonelands": Location("lonelands", "a gloomy empty land with dreary hills ahead", "the Lonelands")
}

connections = {
    "hobbit-hole": {Direction.east: "lonelands"},
    "lonelands": {Direction.west: "hobbit-hole"},
}

def connect_locations():
    for src_name, exits in connections.items():
        src = locations[src_name]
        for direction, destination_name in exits.items():
            destination = locations[destination_name]
            src.add_exit(direction, destination)

connect_locations()

def show_location(location):
    print(f"You are in {location.description}.")
    print("Visible exists are:")
    for exit in location.exits:
        print(exit.name)

if __name__ == '__main__':
    current_location = locations['hobbit-hole']
    while True:
        show_location(current_location)
        command = input("> ")
        if Direction[command]:
            direction = Direction[command]
            if direction in current_location.exits:
                current_location = current_location.exits[direction]
                print(f"You go {direction.name}")
            else:
                print(f"You cannot go {direction.name}")