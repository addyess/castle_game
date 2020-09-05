# /usr/bin/env python3

import abc
import sys
import yaml


class Door:
    def __init__(self, room, door):
        self.room = room
        door = door or {}
        self.name = door.get('name') or room
        self._unlock_with = door.get("lock")
        self.locked = self._unlock_with is not None

    def use(self, item):
        valid = self.locked and self._unlock_with == item
        self.locked ^= valid
        return valid


class Room:
    def __init__(self, name, room=None):
        room = room or {}
        self.name = name
        self.description = room.get("description")
        doors = [
            Door(room, d)
            for room, d in room.get("doors", {}).items()
        ]
        self.doors = {d.name.lower(): d for d in doors}
        self.items = set(room.get("items", []))

    @property
    def described(self):
        describe = self.name
        if self.description:
            describe += f"\n{self.description}"
        if self.doors:
            doors = ', '.join(_.name for _ in self.doors.values())
            describe += f"\n\tAvailable Doors: {doors}"
        if self.items:
            describe += f"\n\tAvailable Items: {', '.join(self.items)}"
        return describe

    def __str__(self):
        return self.described


class Player:
    def __init__(self, first_room, items):
        self.items = set(items)
        self.visited_rooms = [first_room]

    def visit(self, game, args):
        if len(args) != 1:
            return game.respond("% Go where? Please name one door")
        door_name = args[0].lower()
        room = self.current_room
        if door_name not in room.doors:
            return game.respond("% That Door isn't in this room")
        if room.doors[door_name].locked:
            return game.respond("% That Door is locked")
        next_room = game.rooms[room.doors[door_name].room]
        self.visited_rooms.append(next_room)

    def take(self, game, args):
        if len(args) != 1:
            return game.respond("% Take what? Please name the item")
        item = args[0].lower()
        room = self.current_room
        if item not in room.items:
            return game.respond("% That Item isn't in this room")
        room.items.remove(item)
        self.items.update({item})

    def use(self, game, args):
        if len(args) != 2:
            return game.respond("% Use what where? Please name the item and where to use it")
        item, door_name = args
        room = self.current_room
        if door_name.lower() not in room.doors:
            return game.respond("% That Door isn't in this room")
        if item not in self.items:
            return game.respond("% This isn't an item you have")
        used = room.doors[door_name.lower()].use(item)
        if used:
            self.items.remove(item)
            return game.respond(f"Successfully used {item} on {door_name}")
        else:
            return game.respond(f"% That item doesn't work on {door_name}")

    @property
    def current_room(self):
        return self.visited_rooms[-1]


class End:
    def __init__(self, end):
        self.room = Room(end['room'])
        self.outro = end.get('outro') or "Complete!"


class Game(abc.ABC):
    def __init__(self, game_map):
        rooms, begin = game_map['rooms'], game_map['begin']
        self.rooms = {name: Room(name, _) for name, _ in rooms.items()}
        self.end = End(game_map['end'])
        self.player = Player(
            self.rooms[begin['room']],
            begin.get('items') or []
        )
        if 'intro' in begin:
            self.respond(begin['intro'])

    @property
    def reached_end(self):
        return self.player.current_room.name == self.end.room.name

    @abc.abstractmethod
    def prompt(self):
        pass

    @abc.abstractmethod
    def status(self):
        pass

    @abc.abstractmethod
    def respond(self, response):
        pass

    def act(self):
        action = self.prompt()
        v, *args = action.split(' ')
        valid_actions = {
            "use": self.player.use,
            "go": self.player.visit,
            "take": self.player.take
        }
        fn = valid_actions.get(v)
        if not fn:
            return self.respond(
                f"I don't know how to {v}\n"
                f"\tI only can do these things: {', '.join(valid_actions)}."
            )
        return fn(self, args)

    def run(self):
        while not self.reached_end:
            self.act()
        self.status()
        self.respond(self.end.outro)

    @classmethod
    def parse(cls, filepath):
        with open(filepath) as f:
            return cls(yaml.safe_load(f))


class StdInGame(Game):
    def status(self):
        print("--------------------------------------------------------------")
        print(f"You are in {self.player.current_room}")
        if self.player.items:
            print(f"\tYou are holding {', '.join(self.player.items)}")

    def prompt(self):
        self.status()
        return input("Action: ")

    def respond(self, response):
        print(response)


if __name__ == "__main__":
    StdInGame.parse(sys.argv[1]).run()
