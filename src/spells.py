import json
from termcolor import colored


class Spells:

	def __init__(self):
		with open('docs/spells.json') as f:
			spells = json.load(f)
		self.spells = {spell["name"].lower(): spell for spell in spells}

		print(colored("Loaded {} spells".format(len(self.spells)), "blue"))

	def get_details(self, name):
		name = name.lower()
		if name not in self.spells:
			return None
		spell_json = self.spells[name]
		ritual = (spell_json["ritual"] == "yes")
		range = spell_json["range"]
		duration = spell_json["duration"]
		concentration = (spell_json["concentration"] == "yes")
		casting_time = spell_json["casting_time"]
		level = spell_json["level"]
		desc = spell_json["desc"]
		return \
			"{color_magenta}{name}{color_reset} [Level {level}]{ritual}{concentration} ({time}) ({duration}) ({range})" \
			"\n\t{color_green}{desc}{color_reset}" \
			.format(
				color_magenta='\033[95m\033[1m',
				color_green='\033[92m',
				color_yellow='\033[93m',
				color_reset='\033[0m',
				name=spell_json["name"],
				level=level,
				ritual=" (R)" if ritual else "",
				concentration=" (conc)" if concentration else "",
				time=casting_time,
				duration=duration,
				range=range,
				desc="\n\t".join(desc)
			)
