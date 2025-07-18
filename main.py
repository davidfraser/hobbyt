#!/usr/bin/env python

import random

from classes import *
import classes

location_list = [
    Location("hobbit-hole", "a comfortable tunnel like hall"),
    Location("lonelands", "a gloomy empty land with dreary hills ahead", "the Lonelands"),
    Location('trolls-path','A hidden path with trolls foot-prints'),
    Location("trolls-clearing",  "the trolls-clearing"),
    Location('trolls-cave', "the trolls cave"),
]

locations.update({location.name: location for location in location_list})

barriers.update({
    "round-green-door": Door("round-green-door", "the round green door"),
    "heavy-rock-door": LockableDoor("heavy-rock-door", "the heavy rock door", "large-key"),
})

E, W, N, S = (Direction.east, Direction.west, Direction.north, Direction.south)
NE, NW, SE, SW = (Direction.northeast, Direction.northwest, Direction.southeast, Direction.southwest)
U, D = (Direction.up, Direction.down)

connections = {
    "hobbit-hole": {E: ("round-green-door", "lonelands")},
    "lonelands": {W: ("round-green-door", "hobbit-hole"), NE: 'trolls-path', E: 'trolls-path',
                  N: "trolls-clearing"},
    'trolls-path': {S: 'trolls-clearing', N: ("heavy-rock-door", "trolls-cave")},
    'trolls-cave': {S: ('heavy-rock-door', 'trolls-path')},
    "trolls-clearing": {N: "trolls-path", SW: "lonelands"},
}

characters_list = [
    Player("you", "you", locations['hobbit-hole']),
    Character("gandalf", "Gandalf", locations['hobbit-hole']),
    Character("thorin", "Thorin", locations['hobbit-hole']),
    Troll("hideous-troll", "the hideous troll", locations['trolls-clearing'],
          "Blimey, looks at this. Can yer cook em?", True),
    Troll("vicious-troll", "the vicious troll", locations['trolls-clearing'],
          "Yer can try, but he wouldn't make above a mouthful.", False),
]

characters.update({character.name: character for character in characters_list})

items_list = [
    Item("large-key", "the large key", characters['hideous-troll']),
#  Item("  
]

items.update({item.name: item for item in items_list})
for item in items_list:
    if isinstance(item.location, Character):
        item.location.items.append(item)

player = classes.player = characters['you']

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

def play_game():
    reset_time()
    while player.is_alive:
        player.location.show()
        for character in player.location.present_characters():
            character.on_sight(player)
        if not player.is_alive:
            break
        command = input("> ").lower().strip()
        words = command.split() or ['']
        verb = words[0]
        if verb in Direction.__dict__.keys():
            direction = Direction[command]
            player.go(direction)
        elif verb == 'wait' or not verb:
            print("You wait. Time passes...")
        elif verb in ('open', 'close', 'lock', 'unlock'):
            subject = words[1:]
            if 'door' in subject:
                if len(player.location.barriers) == 1:
                    direction, (barrier, destination) = list(player.location.barriers.items())[0]
                    barrier.take_action(player, verb)
        elif verb in ('get', 'take'):
            subject = words[1:]
            subject = ' '.join(subject)
            for item in items.values():
                if item.description == subject:
                    if item.location == player.location:
                        player.take_item(item)
        elif verb == 'drop':
            subject = words[1:]
            subject = ' '.join(subject)
            for item in items.values():
                if item.description == subject:
                    if item.location == player.location:
                        player.drop_item(item)
        elif verb == 'inventory':
            print(f"{player.subject_name} are carrying:")
            if not player.items:
                print("  nothing")
            for item in player.items:
                print(f"  {item.description}")
        elif verb == 'quit':
            break
        else:
            print(f"I do not know how to {command}")
            continue
        current_time = tick()
        for other_mover in characters.values():
            if other_mover.time_sensitive:
                other_mover.handle_tick(current_time)
            if other_mover != player:
                possible_moves = list(other_mover.location.possible_moves(other_mover)) + ['wait']
                move = random.choice(possible_moves)
                if move != 'wait':
                    other_mover.go(move)

if __name__ == '__main__':
    play_game()