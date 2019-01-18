## USAGE:

### General
- **h/help**: help text
- **q/quit**: exit
- **s/save**: saves all stats
- **p/print**: print current stats

### Players
- **au/add-user** \<name> \<ac> \<hp>
- **an/add-npc** \<name> \<ac> \<hp>
- **am/add-monster** "\<official name>" \<nick name>

### Runtime
- **u/update** \<name/index> \<attr> \<val>: update an attribute of a character: hp/hpmax/init/ac
- **d/damage** \<name/index> \<val>: modify the hp of a character (positive for damage, negative for heal)
- **hl/heal** \<name/index> \<val>: modify the hp of a character (negative for damage, positive for heal)
- **rm/remove** \<name/index>: removes the character with this name (cannot be undone!)
- **rs/reset** \<attr>: resets attribute to everyone: init/hp

### Monsters
- **m/monster** "\<official name>": prints monster details
