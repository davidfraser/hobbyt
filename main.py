#!/usr/bin/env python

import random

from classes import *
import classes

location_list = [
    Location("hobbit-hole", "a comfortable tunnel like hall"),
    Location("lonelands", "a gloomy empty land with dreary hills ahead", "the Lonelands"),
    Location('trolls-path','A hidden path with trolls foot-prints'),
    Location("trolls-clearing",  "the trolls-clearing")
]

locations.update({location.name: location for location in location_list})

barriers.update({
    "round-green-door": Door("round-green-door", "the round green door"),
})

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

characters.update({
    "you": Player("you", locations['hobbit-hole']),
    "Gandalf": Character("Gandalf", locations['hobbit-hole']),
    "Thorin": Character("Thorin", locations['hobbit-hole']),
})

items_list = [
    Item("large-key", "the large key", locations['hobbit-hole']),
]

items.update({item.name: item for item in items_list})

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

if __name__ == '__main__':
    while True:
        player.location.show()
        command = input("> ").lower().strip()
        words = command.split() or ['']
        verb = words[0]
        if verb in Direction.__dict__.keys():
            direction = Direction[command]
            player.go(direction)
        elif verb == 'wait':
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
        else:
            print(f"I do not know how to {command}")
        for other_mover in characters.values():
            if other_mover != player:
                possible_moves = list(other_mover.location.possible_moves(other_mover)) + ['wait']
                move = random.choice(possible_moves)
                if move != 'wait':
                    other_mover.go(move)
