import json
import os.path
from texttable import Texttable, bcolors
from termcolor import colored
from random import randint
from src.colors import colored_table_entry, colored_row


def eval_roll(roll_str):
	"""Expected input: xdy, i.e 20d4"""
	split = roll_str.split('d')
	assert len(split) == 2
	multiplier = int(split[0])
	die = int(split[1])
	total = 0
	for _ in range(0, multiplier):
		total += randint(0, die) + 1
	return total


def extend_aux(list1, list2):
	list1.extend(list2)
	return list1


class Tracker:
	filename = 'persistency/track.json'

	def __init__(self):
		self.characters = {}
		self.load_from_file(self.filename)
		self.current_sort = None

	def load_from_file(self, file_path):
		if not os.path.isfile(file_path):
			return
		with open(file_path) as f:
			rows = json.load(f)
		for row in rows:
			char = CharacterStats.load_json(row)
			self.characters[char.name] = char

	def export_to_file(self, file_path):
		rows = [dict(zip(CharacterStats.columns, char.data_row)) for _, char in self.characters.items()]
		with open(file_path, 'w') as f:
			json.dump(rows, f, indent=4)

	@property
	def table(self):
		self.current_sort = list(self.characters.values())
		self.current_sort.sort(key=lambda char: char.sorting_factor)

		table = Texttable(max_width=250)
		table.set_cols_align(extend_aux(["l"], CharacterStats.columns_align()))
		rows = [colored_row(extend_aux(["index"], CharacterStats.columns), bcolors.PURPLE)]
		for idx, character in enumerate(self.current_sort):
			row = extend_aux([colored_table_entry(idx, bcolors.BLUE)], character.data_row_colored)
			rows.append(row)
		table.add_rows(rows)
		return table.draw()

	def flush(self):
		self.export_to_file(self.filename)

	def add_character(self, char):
		if char.name in self.characters:
			print(colored("Character with name '{}' already exists".format(char.name), "red"))
			return
		self.characters[char.name] = char
		self.current_sort = None

	def remove_character(self, name_or_index):
		char = self.get_character(name_or_index)
		if not char:
			return
		del self.characters[char.name]
		self.current_sort = None

	def get_character(self, name_or_index):
		if name_or_index in self.characters:
			return self.characters[name_or_index]
		try:
			index = int(name_or_index)
			if index >= len(self.current_sort):
				print(colored("Index {} is out of range".format(index), "red"))
				return None
			return self.current_sort[index]
		except ValueError:
			pass
		print(colored("Character with name '{} does not exist".format(name_or_index), "red"))
		return None


class CharacterTypes:
	Player = "player"
	NPC = "npc"
	Monster = "monster"

	@staticmethod
	def sort_factor(type):
		return {
			CharacterTypes.Player: 0,
			CharacterTypes.NPC: 1,
			CharacterTypes.Monster: 2
		}[type]


class CharacterStats:

	columns = ["type", "name", "armor_class", "hp_full", "hp_curr", "initiative"]
	columns_bcolors = {
		'type': bcolors.BOLD,
		'name': bcolors.YELLOW
	}

	def __init__(self):
		self.type = None
		self.name = None
		self.initiative = None

	@classmethod
	def load_monster(cls, monster_json):
		char = CharacterStats()
		char.type = CharacterTypes.Monster
		char.name = monster_json["name"]
		char.armor_class = monster_json["armor_class"]
		char.hp_full = eval_roll(monster_json["hit_dice"])
		char.hp_curr = char.hp_full
		return char

	@classmethod
	def load_json(cls, char_json):
		char = CharacterStats()
		for col in cls.columns:
			if col in char_json and char_json[col]:
				setattr(char, col, char_json[col])
			else:
				setattr(char, col, None)
		return char

	@classmethod
	def columns_align(cls):
		align = ["l", "l", "c", "c", "c", "c"]
		assert len(align) == len(cls.columns)
		return align

	def attr_value_with_color(self, attr):
		value = getattr(self, attr)
		if not value:
			return ""
		if attr in self.columns_bcolors:
			return colored_table_entry(value, self.columns_bcolors[attr])
		if attr == "hp_curr":
			value = int(value)
			if value <= 0:
				return colored_table_entry(value, bcolors.RED)
			if value == getattr(self, 'hp_full'):
				return colored_table_entry(value, bcolors.GREEN)
			else:
				return colored_table_entry(value, bcolors.YELLOW)
		return value

	@property
	def data_row_colored(self):
		return[self.attr_value_with_color(column) for column in self.columns]

	@property
	def data_row(self):
		return[attr if attr else "" for attr in (getattr(self, col) for col in self.columns)]

	@property
	def sorting_factor(self):
		return -1*self.initiative if self.initiative else 0, CharacterTypes.sort_factor(self.type), self.name
