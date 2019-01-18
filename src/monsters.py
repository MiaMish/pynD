import json
import re
from math import floor
from termcolor import colored
from src.stats_tracker import CharacterStats


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
		modifier = floor((int(stat) - 10) / 2)
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

	damage_types = {
		'fire',
		'lightning',
		'poison',
		'acid',
		'bludgeoning',
		'necrotic',
		'piercing',
		'radiant',
		'psychic',
		'force',
		'cold',
		'thunder',
		'slashing'
	}

	@staticmethod
	def _get_damage(action):
		if "desc" not in action:
			return ""
		desc = action["desc"]
		damage = desc[(desc.index('Hit: ')+len('Hit: ')):].split('.')[0]
		if '(' in damage:
			damage = damage.split(' ')
			for idx, item in enumerate(damage):
				if '(' in item:
					del damage[idx-1]
			damage = " ".join(damage)
			damage = damage.replace(')', '').replace('(', '')
		return damage

	@staticmethod
	def _format_actions(monster_json, actions):
		if actions not in monster_json:
			return ""
		actions = monster_json[actions]
		res = []
		for action in actions:
			if "damage_bonus" in action:
				res.append(
					"\t\t* \033[1m\033[30m{}\033[0m: to hit: \033[94m{}\033[0m, damage: \033[91m{}\033[0m"
					.format(
						action["name"],
						action["attack_bonus"],
						Monsters._get_damage(action)
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
