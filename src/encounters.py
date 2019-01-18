import os
import pathlib
from glob import glob
from src.stats_tracker import Tracker

BASE_DIR = 'persistency/encounters'
pathlib.Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

encounters = dict()


def load_encounters():
	files = glob(os.path.join(BASE_DIR, "*.json"))
	for file in files:
		filename = os.path.basename(file)
		name = filename[:(filename.rfind('.'))]
		encounter = Encounter(name)
		encounter.load_from_file(encounter.filename)
		encounters[name] = encounter


class Encounter(Tracker):

	def __init__(self, name):
		self.name = name
		self.filename = os.path.join(BASE_DIR, '{}.json'.format(name))
		Tracker.__init__(self)

	def delete(self):
		os.remove(self.filename)
		del encounters[self.name]


load_encounters()
