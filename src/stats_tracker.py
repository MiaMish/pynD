import json
import os.path
from texttable import Texttable
from termcolor import colored, COLORS, RESET
from random import randint
from math import floor


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


class Monsters:

	def __init__(self):
		with open('docs/monsters.json') as f:
			monsters = json.load(f)
		self.monsters = {monster["name"].lower(): monster for monster in monsters}

		print(colored("Loaded {} monsters".format(len(self.monsters)), "blue"))

	def get_monster_instance(self, name, nick):
		name = name.lower()
		if name not in self.monsters:
			return None
		monster_json = self.monsters[name]
		monster_json["name"] = nick
		return CharacterStats.load_monster(monster_json)

	@staticmethod
	def _stat_value(monster_json, stat):
		if stat in monster_json:
			return monster_json[stat]
		return 10

	@staticmethod
	def _stat_to_modifier(stat):
		modifier = floor((int(stat)-10)/2)
		if modifier > 0:
			return "+{}".format(modifier)
		else:
			return modifier

	@staticmethod
	def _save_stat(monster_json, stat_name):
		save_stat_name = "{}_save".format(stat_name)
		if save_stat_name in monster_json:
			val = monster_json[save_stat_name]
			if val > 0:
				return "\033[91m+{}\033[0m".format(val)
			else:
				return "\033[91m{}\033[0m".format(val)
		val = Monsters._stat_value(monster_json, stat_name)
		return "\033[91m{}\033[0m".format(Monsters._stat_to_modifier(val))

	@staticmethod
	def _format_actions(monster_json, actions):
		if actions not in monster_json:
			return ""
		actions = monster_json[actions]
		res = []
		for action in actions:
			if "damage_bonus" in action:
				res.append(
					"\t\t* \033[1m\033[30m{}\033[0m: to hit: \033[94m{}\033[0m, damage: \033[91m{} + {}\033[0m"
					.format(
						action["name"],
						action["attack_bonus"],
						action["damage_dice"],
						action["damage_bonus"]
					)
				)
			else:
				res.append("\t\t* \033[1m\033[30m{}\033[0m: {}".format(action["name"], action["desc"]))
		return "\n".join(res)

	def get_details(self, name):
		name = name.lower()
		if name not in self.monsters:
			return None
		monster_json = self.monsters[name]
		str = self._stat_value(monster_json, "strength")
		dex = self._stat_value(monster_json, "dexterity")
		con = self._stat_value(monster_json, "constitution")
		int = self._stat_value(monster_json, "intelligence")
		wis = self._stat_value(monster_json, "wisdom")
		cha = self._stat_value(monster_json, "charisma")
		return \
			"{color_magenta}{name}{color_reset} ({size}, {type}) CR={cr}:" \
			"\n\t{color_green}Stats{color_reset}: STR {str} DEX {dex} CON {con} INT {int} WIS {wis} CHA {cha}" \
			"\n\t{color_green}Saves{color_reset}: STR {str_save} DEX {dex_save} CON {con_save} INT {int_save} WIS {wis_save} CHA {cha_save}" \
			"\n\t{color_green}speed{color_reset} = {speed}, {color_green}AC{color_reset} = {ac}, {color_green}HP{color_reset} = {hp} ({hd})" \
			"\n\t{color_green}Vulnerabilities{color_reset}: {vuln}" \
			"\n\t{color_green}Resistances{color_reset}: {resist}" \
			"\n\t{color_green}Immunities{color_reset}: {imm}" \
			"\n\t{color_yellow}Actions:{color_reset}\n{actions}" \
			"\n\t{color_yellow}Legendary actions:{color_reset}\n{leg_actions}" \
			"\n\t{color_yellow}Special:{color_reset}\n{special_actions}" \
			.format(
				color_magenta='\033[95m\033[1m',
				color_green='\033[92m',
				color_yellow='\033[93m',
				color_reset='\033[0m',
				name=monster_json["name"],
				size=monster_json["size"],
				type=monster_json["type"],
				cr=monster_json["challenge_rating"],
				str="\033[94m{}\033[0m (\033[91m{}\033[0m)".format(str, self._stat_to_modifier(str)),
				dex="\033[94m{}\033[0m (\033[91m{}\033[0m)".format(dex, self._stat_to_modifier(dex)),
				con="\033[94m{}\033[0m (\033[91m{}\033[0m)".format(con, self._stat_to_modifier(con)),
				int="\033[94m{}\033[0m (\033[91m{}\033[0m)".format(int, self._stat_to_modifier(int)),
				wis="\033[94m{}\033[0m (\033[91m{}\033[0m)".format(wis, self._stat_to_modifier(wis)),
				cha="\033[94m{}\033[0m (\033[91m{}\033[0m)".format(cha, self._stat_to_modifier(cha)),
				str_save=self._save_stat(monster_json, "strength"),
				dex_save=self._save_stat(monster_json, "dexterity"),
				con_save=self._save_stat(monster_json, "constitution"),
				int_save=self._save_stat(monster_json, "intelligence"),
				wis_save=self._save_stat(monster_json, "wisdom"),
				cha_save=self._save_stat(monster_json, "charisma"),
				speed=monster_json["speed"],
				ac=monster_json["armor_class"],
				hp=monster_json["hit_points"],
				hd=monster_json["hit_dice"],
				vuln=monster_json["damage_vulnerabilities"],
				resist=monster_json["damage_resistances"],
				imm=monster_json["damage_immunities"],
				actions=self._format_actions(monster_json, "actions"),
				leg_actions=self._format_actions(monster_json, "legendary_actions"),
				special_actions=self._format_actions(monster_json, "special_abilities"),
			)
		return monster_json


class Tracker:
	filename = 'persistency/track.json'

	def __init__(self):
		print("Stats Tracker started!")
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
		rows = [extend_aux(["index"], CharacterStats.columns)]
		for idx, char in enumerate(self.current_sort):
			row = extend_aux([idx], char.data_row)
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


class CharacterStats:

	columns = ["type", "name", "armor_class", "hp_full", "hp_curr", "initiative"]

	def __init__(self):
		self.type = None
		self.name = None
		self.initiative = None

	@classmethod
	def load_monster(cls, monster_json):
		char = CharacterStats()
		char.type = "monster"
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

	@property
	def data_row(self):
		return[attr if attr else "" for attr in (getattr(self, col) for col in self.columns)]

	@property
	def sorting_factor(self):
		return -1*self.initiative if self.initiative else 0, self.type, self.name
