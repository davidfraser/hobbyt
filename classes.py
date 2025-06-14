"""Contains the classes used by the main program"""

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
        for obj in list(characters.values()) + list(items.values()):
            if obj.location == self and not (isinstance(obj, Character) and obj.is_player):
                if obj.visible:
                    visible.append(obj)
        if visible:
            print("You see:")
            for obj in visible:
                if isinstance(obj, Character) and obj.items:
                    print(f"  {obj}. {obj.subject_name} is carrying")
                    for item in obj.items:
                        print(f"    {item}")
                else:
                    print(f"  {obj}")

    def possible_moves(self, character):
        for direction in self.exits:
            yield direction
        for direction, (barrier, destination) in self.barriers.items():
            if barrier.can_pass():
                yield direction

    def present_characters(self):
        """Yields all characters that are present and living"""
        for character in characters.values():
            if character.location is self and character.is_alive:
                yield character

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

    def take_action(self, character, action, report_unknown_actions=True):
        """The given character takes the given action on this door. Returns whether an action was understood"""
        if action == 'open':
            if self.is_open:
                print(f"{self.description} is open.")
            else:
                character.report_action(action, self.description)
                self.is_open = True
            return True
        elif action == 'close':
            if self.is_open:
                character.report_action(action, self.description)
                self.is_open = False
            else:
                print(f"{self.description} is closed.")
            return True
        elif report_unknown_actions:
            print(f"{character.subject_name} cannot {action} {self.description}")
        return False

class LockableDoor(Door):
    def __init__(self, name, description, key_name, starts_open=False, starts_locked=True):
        Door.__init__(self, name, description, starts_open)
        self.key_name = key_name
        self.is_locked = starts_locked

    def take_action(self, character, action, report_unknown_action=True):
        """The given character takes the given action on this door. Returns whether an action was understood"""
        if not self.is_locked:
            if Door.take_action(self, character, action, report_unknown_actions=False):
                return True
        if action == 'unlock':
            if self.is_locked:
                if character.has_item(self.key_name):
                    key = items[self.key_name]
                    character.report_action(action, f"{self.description} with {key}")
                    self.is_locked = False
                    return True
        elif action == 'lock':
            if not self.is_locked:
                if character.has_item(self.key_name):
                    key = items[self.key_name]
                    character.report_action(action, f"{self.description} with {key}")
                    self.is_locked = True
                    return True
        if report_unknown_action:
           print(f"{character.subject_name} cannot {action} {self.description}")
        return False

class Object(object):
    """This is anything that can exist at a location"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.visible = True

    def __str__(self):
        return self.description

class Item(Object):
    """This is a non-character object"""
    def __init__(self, name, description, location):
        Object.__init__(self, name, description)
        self.location = location

class Character(Object):
    """This is a character who can move around"""
    is_player = False
    time_sensitive = False
    def __init__(self, name, description, location):
        Object.__init__(self, name, description)
        self.location = location
        self.is_alive = True
        self.items = []

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
            if self.is_player or (player and came_from == player.location):
                self.report_action('go', direction.name)
            elif self.location == (player.location if player else None):
                self.report_action('enter')
        else:
            print(f"{self.subject_name} cannot go {direction.name}")
        if not self.is_player:
            for character in self.location.present_characters():
               character.on_sight(self)

    def report_action(self, action, additional=''):
        print(f"{self.subject_name} {self.verb_suffix(action)}{' ' if additional else ''}{additional}.")

    @property
    def subject_name(self):
        return self.description.title()

    def verb_suffix(self, verb):
        if self.name == "you":
            return verb
        else:
            if verb[-1:] in "aeiou":
                return verb + "es"
            return verb + "s"

    def has_item(self, item_name):
        for item in self.items:
            if item_name == item.name:
                return True
        return False

    def take_item(self, item):
        if item not in self.items:
            self.items.append(item)
            item.location = self
            self.report_action("take", item.description)

    def drop_item(self, item_or_name):
        item = item_or_name if isinstance(Item) else items[item_or_name]
        if item in self.items:
            self.items.remove(item)
            item.location = self.location
            self.report_action("drop", item.description)

    def kill(self):
        self.is_alive = False
        for item in self.items[:]:
            self.items.remove(item)
            item.location = self.location

    def on_sight(self, character):
        pass

    def handle_tick(self, current_time):
        pass

class Player(Character):
    is_player = True

    def kill(self):
        Character.kill(self)
        print(f"{self.subject_name} are dead.")

class Troll(Character):
    time_sensitive = True
    def __init__(self, name, description, location, saying, gluttonous=False):
        Character.__init__(self, name, description, location)
        self.saying = saying
        self.gluttonous = gluttonous
        self.seen_player = False

    def on_sight(self, character):
        if character == player:
            if self.seen_player:
                if self.gluttonous:
                    print(f"{self.subject_name} eats {character}.")
                    print(f"His foul gluttony has killed {self.description}.")
                    self.kill()
                    character.kill()
            else:
                print(f'{self.subject_name} says "{self.saying}"')
            self.seen_player = get_tick()

    def go(self, direction):
        """These trolls are immovable and ignore such plans"""
        pass

    def handle_tick(self, current_time):
        if (self.seen_player is not False) and current_time >= (self.seen_player + 3):
            if not global_state['daylight']:
                print(f"Day dawns")
                global_state['daylight'] = True
                self.location.description = "a clearing with two stone trolls"
            self.kill()

    def kill(self):
        Character.kill(self)
        self.visible = False

# global variables used by the rest of the program

locations = {}
characters = {}
barriers = {}
items = {}
player = None
global_state = {
    'time': 0,
    'daylight': False,
}

def reset_time():
    global_state['time'] = 0

def get_tick():
    return global_state['time']

def tick():
    global_state['time'] += 1
    return global_state['time']
