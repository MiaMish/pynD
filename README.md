## USAGE:

### General
- **h/help**: help text
- **q/quit/exit**: exit
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

### Encounters
- **ee/edit-encounter** \<name>: enter encounter edit mode for this new or existing encounter by name
- **ees/stop-edit-encounter** \<name>: exit encounter edit mode
- **le/load-encounter**: load a pre-existing encounter to current stats
- **ge/get-encounters**: list all encounters
- **pe/print-encounters**: print all encounters
- **de/delete-encounter**: \<name>: delete an encounter by name
