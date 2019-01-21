import consolemd
from functools import wraps
from termcolor import colored
from src.stats_tracker import Tracker, CharacterStats, CharacterTypes
from src.monsters import Monsters
from src.encounters import encounters, Encounter

tracker = Tracker()
monsters = Monsters()

with open('README.md', 'r') as readme:
	readme_content = readme.read()


def post_save(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		global tracker
		resp = func(self, *args, **kwargs)
		tracker.flush()
		return resp
	return wrapper


def post_print(func):
	@wraps(func)
	def wrapper(self, *args, **kwargs):
		resp = func(self, *args, **kwargs)
		command_print()
		return resp
	return wrapper


def start():

	command_print()
	print("Event loop started!")

	while True:
		try:
			command = input("> ")
			command_split = command.split(' ')
			if command_split[0] not in commands:
				print(colored("Invalid command. Usage:", "red"))
				command_help()
			else:
				commands[command_split[0]](*command_split)
			print("")
		except Exception as ex:
			print(colored(ex, "red"))


def command_help(*args):
	consolemd.Renderer().render(readme_content)


def command_quit(*args):
	global tracker
	tracker.flush()
	print(colored("bye!", "blue"))
	exit()


def command_print(*args):
	global tracker
	print(tracker.table)


@post_save
@post_print
def command_add_user(*args):
	if not len(args) == 4:
		print(colored("Invalid input, aborting command", "red"))
		return
	char = CharacterStats()
	char.type = CharacterTypes.Player
	char.name = args[1]
	char.armor_class = int(args[2])
	char.hp_full = int(args[3])
	char.hp_curr = char.hp_full
	tracker.add_character(char)


@post_save
@post_print
def command_add_npc(*args):
	if not len(args) == 4:
		print(colored("Invalid input, aborting command", "red"))
		return
	char = CharacterStats()
	char.type = CharacterTypes.NPC
	char.name = args[1]
	char.armor_class = int(args[2])
	char.hp_full = int(args[3])
	char.hp_curr = char.hp_full
	tracker.add_character(char)


@post_save
@post_print
def command_update(*args):
	assert len(args) == 4
	name_or_index = args[1]
	attr = args[2]
	val = args[3]
	char = tracker.get_character(name_or_index)
	if not char:
		return
	if attr == 'hp':
		char.hp_curr = int(val)
	elif attr == 'hpmax':
		char.hp_full = int(val)
	elif attr == 'init':
		char.initiative = float(val)
	elif attr == 'ac':
		char.armor_class = int(val)
	else:
		print(colored("Invalid attribute: '{}'".format(attr), "red"))
		return


@post_save
@post_print
def command_damage(*args):
	assert len(args) == 3
	name_or_index = args[1]
	val = int(args[2])
	char = tracker.get_character(name_or_index)
	if not char:
		return
	char.hp_curr -= val
	char.hp_curr = max(0, char.hp_curr)


@post_save
@post_print
def command_heal(*args):
	assert len(args) == 3
	name_or_index = args[1]
	val = int(args[2])
	char = tracker.get_character(name_or_index)
	if not char:
		return
	char.hp_curr += val
	char.hp_curr = max(0, char.hp_curr)


@post_save
@post_print
def command_remove(*args):
	assert len(args) == 2
	name_or_index = args[1]
	tracker.remove_character(name_or_index)


@post_save
@post_print
def command_add_monster(*args):
	if len(args) < 3:
		print(colored("Invalid input, aborting command", "red"))
		return
	if args[1].startswith('"'):
		idx = 1
		while not args[idx].endswith('"'):
			idx += 1
		name = " ".join(args[1:idx+1])
		name = name[1:-1]
		nick = args[idx+2]
	else:
		name = args[1]
		nick = args[2]
	monster = monsters.get_monster_instance(name, nick)
	if not monster:
		print(colored("No monster with name '{}'".format(name), "red"))
		return
	tracker.add_character(monster)


@post_save
@post_print
def command_reset(*args):
	assert len(args) == 2
	attr = args[1]
	for _, char in tracker.characters.items():
		if attr == 'hp':
			char.hp_curr = char.hp_full
		elif attr == 'init':
			char.initiative = None
		else:
			print(colored("Invalid attribute: '{}'".format(attr), "red"))
			return


def command_monster_details(*args):
	if len(args) < 2:
		print(colored("Invalid input, aborting command", "red"))
		return
	if args[1].startswith('"'):
		idx = 1
		while not args[idx].endswith('"'):
			idx += 1
		name = " ".join(args[1:idx+1])
		name = name[1:-1]
	else:
		name = args[1]
	details = monsters.get_details(name)
	if not details:
		print(colored("No monster with name '{}'".format(name), "red"))
		return
	print(details)


@post_print
def command_edit_encounter(*args):
	global tracker
	if len(args) < 2:
		print(colored("Invalid input - please supply encounter name, aborting command", "red"))
		return
	name = args[1]
	if name not in encounters:
		encounters[name] = Encounter(name)
	tracker = encounters[name]


@post_print
def command_stop_edit_encounter(*args):
	global tracker
	if not isinstance(tracker, Encounter):
		print("No encounter is currently edited")
		return
	print(colored("Stopping to edit encounter {}".format(tracker.name)))
	tracker.flush()
	tracker = Tracker()


@post_save
@post_print
def command_load_encounter(*args):
	global tracker
	if isinstance(tracker, Encounter):
		print(colored("You are in the context of an encounter edit, cannot load", "red"))
		return
	if len(args) < 2:
		print(colored("Invalid input - please supply encounter name, aborting command", "red"))
		return
	name = args[1]
	if name not in encounters:
		print(colored("Encounter '{}' does not exist, aborting command".format(name), "red"))
		return
	encounter = encounters[name]
	for character in encounter.characters.values():
		tracker.add_character(character)


def command_get_encounters(*args):
	if not encounters:
		print(colored("No encounters found", "red"))
		return
	for name in encounters.keys():
		print(colored(name, "yellow"))


def command_print_encounters(*args):
	if not encounters:
		print(colored("No encounters found", "red"))
		return
	for name, encounter in encounters.items():
		print("-- Encounter {} --".format(colored(name, "yellow")))
		print(encounter.table)
		print()


def command_delete_encounter(*args):
	if len(args) < 2:
		print(colored("Invalid input - please supply encounter name, aborting command", "red"))
		return
	name = args[1]
	if name not in encounters:
		print(colored("Encounter '{}' does not exist, aborting command".format(name), "red"))
		return
	encounters[name].delete()


commands = {
	'h': command_help,
	'help': command_help,
	'q': command_quit,
	'quit': command_quit,
	'exit': command_quit,
	'p': command_print,
	'print': command_print,
	'au': command_add_user,
	'add-user': command_add_user,
	'an': command_add_npc,
	'add-npc': command_add_npc,
	'u': command_update,
	'update': command_update,
	'd': command_damage,
	'damage': command_damage,
	'hl': command_heal,
	'heal': command_heal,
	'rm': command_remove,
	'remove': command_remove,
	'am': command_add_monster,
	'add-monster': command_add_monster,
	'rs': command_reset,
	'reset': command_reset,
	'm': command_monster_details,
	'monster': command_monster_details,
	'edit-encounter': command_edit_encounter,
	'ee': command_edit_encounter,
	'stop-edit-encounter': command_stop_edit_encounter,
	'ees': command_stop_edit_encounter,
	'load-encounter': command_load_encounter,
	'le': command_load_encounter,
	'get-encounters': command_get_encounters,
	'ge': command_get_encounters,
	'print-encounters': command_print_encounters,
	'pe': command_print_encounters,
	'delete-encounter': command_delete_encounter,
	'de': command_delete_encounter
}
