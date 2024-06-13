# coding: shift-jis

import sys, os, csv
from collections import OrderedDict

## global
SRC_DIR = (os.path.dirname(os.path.realpath(__file__)))

CONFIG_FILE = 'config.csv'

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

PROJECT_DIR = os.path.join(SRC_DIR, '..')

class ConfigReader():
    def __init__(self):
        # set system defaults (these parameters were used, if there is no configuration file on local and server)
        self._SetSystemDefaults()

        # read config.csv
        self._ReadCSV(os.path.join(PROJECT_DIR, CONFIG_FILE))

    def _SetSystemDefaults(self):
        self._values = OrderedDict()
        self._values['Number_Of_Backups'] = 10
        self._values['Bead_Thickness'] = 5
        self._values['Bead_Elem_Size'] = 3
        self._values['Average_Elem_Size'] = 10
        self._values['Aspect_Ratio'] = 10
        self._values['Max_Angle_Per_Elem'] = 45
        self._values['Fillet_Tokekomi'] = 5
        self._values['Fillet_Gap_Limit'] = 3
        self._values['Intermittent_Bead_Length'] = 30
        self._values['Intermittent_Number_Of_Beads'] = 5
        self._values['Intermittent_Pitch_Length'] = 75
        self._values['Yomori_height'] = 10
        self._values['Yomori_Loop_Radius'] = 10
        
        self._values['Connect_Connected_Edge_Bead_Radius'] = 8
        self._values['Connect_Connected_Edge_Bead_Elem_Size'] = 8
        

    def _ReadCSV(self, path):
        with open(path, 'r', encoding="utf_8") as f:
            reader = csv.reader(f)
            _ = next(reader)
            for line in reader:
                if len(line) != 2:
                    continue
                self._values[line[0]] = line[1]

    def Get(self, key):
        if not key in self._values.keys():
            return ''
        return self._values[key]
