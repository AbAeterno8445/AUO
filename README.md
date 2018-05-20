# AUO
Python AUO game project.

# Extra info
Currently used tile flags:
    * wall: blocks movement
    * bv: blocks vision
    * shadow: draws a small shadow around it (use on square wall tiles)
    * xfer: transfer to another level. Usage: xfer/levelname/x/y, levelname is the name of target level, x/y is the position to transfer to in this level.
    * spawn: player spawnpoint in map. Each map should have exactly 1 of this somewhere.
    * indoor: use on tiles inside buildings, default light level for these is 0.
    * light: light source. Usage: light/strength, strength being the light's intensity.