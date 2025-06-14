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
        self.barriers = {}

    def add_exit(self, direction, destination):
        self.exits[direction] = destination

    def add_barrier(self, direction, barrier, destination):
        self.barriers[direction] = (barrier, destination)

    def show(self):
        print(f"You are in {self.description}.")
        for direction, (barrier, destination) in self.barriers.items():
            print(f"To the {direction.name} there is the {barrier.description}.")
        if self.exits:
            print("Visible exits are:")
            for direction in self.exits:
                print(f"  {direction.name}")
        visible = []
        for character in characters.values():
            if character.location == self and not character.is_player:
                visible.append(character)
        if visible:
            print("You see:")
            for item in visible:
                print(item.name)

    def possible_moves(self, character):
        for direction in self.exits:
            yield direction
        for direction, (barrier, destination) in self.barriers.items():
            if barrier.can_pass():
                yield direction

class Barrier(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def can_pass(self):
        return False

class Door(Barrier):
    def __init__(self, name, description, starts_open=False):
        Barrier.__init__(self, name, description)
        self.is_open = starts_open

    def can_pass(self):
        return self.is_open

    def take_action(self, character, action):
        if action == 'open':
            if self.is_open:
                print(f"{self.description} is open.")
            else:
                character.report_action(action, self.description)
                self.is_open = True
        elif action == 'close':
            if self.is_open:
                character.report_action(action, self.description)
                self.is_open = False
            else:
                print(f"{self.description} is closed.")
        else:
            print(f"{character.subject_name} cannot {action} {self.description}")

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
        came_from = self.location
        move = None
        if direction in self.location.exits:
            move = direction
            self.location = self.location.exits[direction]
        elif direction in self.location.barriers:
            barrier, destination = self.location.barriers[direction]
            if barrier.can_pass():
                move = direction
                self.location = destination
        if move:
            if self == player or came_from == player.location:
                self.report_action('go', direction.name)
            elif self.location == player.location:
                self.report_action('enter')
        else:
            print(f"{self.subject_name} cannot go {direction.name}")

    def report_action(self, action, additional=''):
        print(f"{self.subject_name} {self.verb_suffix(action)}{' ' if additional else ''}{additional}.")

    @property
    def subject_name(self):
        return self.name.title()

    def verb_suffix(self, verb):
        if self.name == "you":
            return verb
        else:
            if verb[-1:] in "aeiou":
                return verb + "es"
            return verb + "s"

class Player(Character):
    is_player = True

location_list = [
    Location("hobbit-hole", "a comfortable tunnel like hall"),
    Location("lonelands", "a gloomy empty land with dreary hills ahead", "the Lonelands"),
    Location('trolls-path','A hidden path with trolls foot-prints'),
    Location("trolls-clearing",  "the trolls-clearing")
]

locations = {location.name: location for location in location_list}

barriers = {
    "round-green-door": Door("round-green-door", "the round green door"),
}

E, W, N, S = (Direction.east, Direction.west, Direction.north, Direction.south)
NE, NW, SE, SW = (Direction.northeast, Direction.northwest, Direction.southeast, Direction.southwest)
U, D = (Direction.up, Direction.down)

connections = {
    "hobbit-hole": {E: ("round-green-door", "lonelands")},
    "lonelands": {W: ("round-green-door", "hobbit-hole"), NE: 'trolls-path', E: 'trolls-path',
                  N: "trolls-clearing"},
    'trolls-path': {S: 'trolls-clearing'},
    "trolls-clearing": {N: "trolls-path", SW: "lonelands"},
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
        for direction, target in exits.items():
            if isinstance(target, str):
                destination = locations[target]
                src.add_exit(direction, destination)
            elif isinstance(target, tuple):
                barrier_name, destination_name = target
                barrier = barriers[barrier_name]
                destination = locations[destination_name]
                src.add_barrier(direction, barrier, destination)

connect_locations()

if __name__ == '__main__':
    while True:
        player.location.show()
        command = input("> ").lower().strip()
        words = command.split()
        verb = words[0]
        if verb in Direction.__dict__.keys():
            direction = Direction[command]
            player.go(direction)
        elif verb == 'wait':
            print("You wait. Time passes...")
        elif verb in ('open', 'close'):
            subject = words[1:]
            if 'door' in subject:
                if len(player.location.barriers) == 1:
                    direction, (barrier, destination) = list(player.location.barriers.items())[0]
                    barrier.take_action(player, verb)
        else:
            print(f"I do not know how to {command}")
        for other_mover in characters.values():
            if other_mover != player:
                possible_moves = list(other_mover.location.possible_moves(other_mover)) + ['wait']
                move = random.choice(possible_moves)
                if move != 'wait':
                    other_mover.go(move)
