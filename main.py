import enum
import random

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

    def show(self):
        print(f"You are in {self.description}.")
        print("Visible exists are:")
        for exit in self.exits:
            print(exit.name)
        visible = []
        for character in characters.values():
            if character.location == self and not character.is_player:
                visible.append(character)
        if visible:
            print("You see:")
            for item in visible:
                print(item.name)


class Object(object):
    """This is anything that can exist at a location"""
    pass

class Item(Object):
    """This is a non-character object"""
    pass

class Character(Object):
    """This is a character who can move around"""
    is_player = False
    def __init__(self, name, location):
        self.name = name
        self.location = location

    def go(self, direction):
        if direction in self.location.exits:
            came_from = self.location
            self.location = self.location.exits[direction]
            if self.is_player:
                print(f"You go {direction.name}")
            elif came_from == player.location:
                print(f"{self.name} goes {direction.name}")
            elif self.location == player.location:
                print(f"{self.name} enters")
        else:
            print(f"{self.name.title()} cannot go {direction.name}")

class Player(Character):
    is_player = True

locations = {
    "hobbit-hole": Location("hobbit-hole", "a comfortable tunnel like hall"),
    "lonelands": Location("lonelands", "a gloomy empty land with dreary hills ahead", "the Lonelands"),
    "trolls-path": Location('trolls-path','A hidden path with trolls foot-prints'),
}

E, W, N, S = (Direction.east, Direction.west, Direction.north, Direction.south)
NE, NW, SE, SW = (Direction.northeast, Direction.northwest, Direction.southeast, Direction.southwest)
U, D = (Direction.up, Direction.down)

connections = {
    "hobbit-hole": {E: "lonelands"},
    "lonelands": {W: "hobbit-hole", NE: 'trolls-path'},
    # 'trolls-path': {SW: ''}
}

characters = {
    "you": Player("you", locations['hobbit-hole']),
    "Gandalf": Character("Gandalf", locations['hobbit-hole']),
    "Thorin": Character("Thorin", locations['hobbit-hole']),
}

player = characters['you']

def connect_locations():
    for src_name, exits in connections.items():
        src = locations[src_name]
        for direction, destination_name in exits.items():
            destination = locations[destination_name]
            src.add_exit(direction, destination)

connect_locations()

if __name__ == '__main__':
    while True:
        player.location.show()
        command = input("> ")
        if command in Direction.__dict__.keys():
            direction = Direction[command]
            player.go(direction)
        elif command == 'wait':
            print("You wait. Time passes...")
        else:
            print(f"I do not know how to {command}")
        other_mover = random.choice(list(characters.values()))
        if other_mover != player:
            other_mover.go(random.choice(list(other_mover.location.exits.keys())))
