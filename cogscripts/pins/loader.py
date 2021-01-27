import re
import csv
from dotmap import DotMap

try:
    import pinmap
    pinmap_style = 'new'
except:
    pinmap_style = 'old'


def skip_comments(lines):
    for line in lines:
        line = re.sub(r'\s*#.*$', '', line).strip()
        if line:
            yield line


def load_pins_from_file():
    if pinmap_style == 'old:':
        with open('pins.csv', 'r') as f:
            csv.register_dialect('pincsv', skipinitialspace=True)
            reader = csv.DictReader(skip_comments(f), dialect='pincsv')

            pins = [DotMap(r) for r in reader if r['name']]
            for p in pins:
                p.tags = p.tags.split(" ")
            return pins

    else:
        pins = []
        for pin, data in pinmap.development.items():
            if data:
                p = {'pin':pin, 'name':data[0], 'tags':data[1]}
                pins.append(DotMap(p))

        return pins