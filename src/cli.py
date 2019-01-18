import consolemd
from termcolor import colored
from src.stats_tracker import Tracker, CharacterStats, Monsters, CharacterTypes

tracker = Tracker()
monsters = Monsters()

with open('README.md', 'r') as readme:
	readme_content = readme.read()


def start():

	command_print()
	print("Event loop started!")

	while True:
		command = input("> ")
		command_split = command.split(' ')
		if command_split[0] not in commands:
			print(colored("Invalid command. Usage:", "red"))
			command_help()
		else:
			commands[command_split[0]](*command_split)
		print("")


def command_help(*args):
	consolemd.Renderer().render(readme_content)


def command_save(*args):
	global tracker
	tracker.flush()
	print(colored("saved!", "blue"))


def command_quit(*args):
	global tracker
	tracker.flush()
	print(colored("bye!", "blue"))
	exit()


def command_print(*args):
	global tracker
	print(tracker.table)


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
	command_print()


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
	command_print()


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
	command_print()


def command_damage(*args):
	assert len(args) == 3
	name_or_index = args[1]
	val = int(args[2])
	char = tracker.get_character(name_or_index)
	if not char:
		return
	char.hp_curr -= val
	char.hp_curr = max(0, char.hp_curr)
	command_print()


def command_heal(*args):
	assert len(args) == 3
	name_or_index = args[1]
	val = int(args[2])
	char = tracker.get_character(name_or_index)
	if not char:
		return
	char.hp_curr += val
	char.hp_curr = max(0, char.hp_curr)
	command_print()


def command_remove(*args):
	assert len(args) == 2
	name_or_index = args[1]
	tracker.remove_character(name_or_index)
	command_print()


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
	command_print()


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
	command_print()


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


commands = {
	'h': command_help,
	'help': command_help,
	'q': command_quit,
	'quit': command_quit,
	's': command_save,
	'save': command_save,
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
	'monster': command_monster_details
}
