Usage
========

```bash
./castle.py <map file>
```

Requirements
========
* Python 3.7

Map File
========
Create a YAML File defining the game map.  The outer keys should be 
**rooms**, **begin**, **goals**

Rooms
-----
Define what rooms are in the castle.  A room can have any name that isn't a space
##### Example
```yaml
rooms:
    atrium: ~
    ballroom: ~
    east-staircase: ~
    outside: ~
```

#### Individual Room
Define what things are in the room. 

##### Description
Put the player in the experience of the game by story telling about each room. 
This text will be displayed everytime the player finishes an action in the room. 
```yaml
rooms:
    atrium:
      description: |  # Optional (defaults to None"")
        You've stepped into a beautifully ornate atrium. It makes you wonder 
        why someone would spend this much money on a room no one ever really 
        stays in.  Make sure to wipe your feet.
```

##### Doors
Usually there are doors leading to connected rooms.

Those door can be one-way or two-way because each room defines which doors are in it. 

You should specify the name of the room you wish the player to enter when stepping
through the door.  It's also possible to specify a key used to lock this door or
an alternate name for the door
```yaml
rooms:
    atrium:
      doors:
        office:
          lock: office-key
          name: Secret
```

#### Items
There may be things laying around in the room the player can pick up. 

__Note__: Currently the engine lets the player use these as keys for locked doors
```yaml
rooms:
    atrium:
      items:
      - office-key
```

Begin
-----
Define the initial state of the game.
##### Example
```yaml
begin:
    room: atrium
    items: []    # Optional (defaults to [])
    intro: |     # Optional (defaults to None)
       Welcome to the Game, This text is only shown once at the beginning.
```

End
---
Define the end state of the game
##### Example
```yaml
end:
    room: outside
    outro: |     # Optional (defaults to None)
       You found your way outside! You rock.
```
