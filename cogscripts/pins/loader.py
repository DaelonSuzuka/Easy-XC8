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
    if pinmap_style == 'old':
        with open('pins.csv', 'r') as f:
            csv.register_dialect('pincsv', skipinitialspace=True)
            reader = csv.DictReader(skip_comments(f), dialect='pincsv')

            pins = [DotMap(r) for r in reader if r['name']]
            for p in pins:
                p.tags = p.tags.split(" ")
                p.tags.append('common')
            return pins

    else:
        pins = []
        for pin, data in pinmap.common.items():
            if data:
                pins.append(DotMap({'pin':pin, 'name':data[0], 'tags':[*data[1], 'common']}))

        dev_pins = {}
        for pin, data in pinmap.development.items():
            if data:
                dev_pins[data[0]] = DotMap({'pin':pin, 'name':data[0], 'tags':data[1]})

        rel_pins = {}
        for pin, data in pinmap.release.items():
            if data:
                rel_pins[data[0]] = DotMap({'pin':pin, 'name':data[0], 'tags':data[1]})

        for pin in dev_pins:
            if pin in rel_pins:
                p = DotMap({**dev_pins[pin], 'pin':'NA', 'dpin':dev_pins[pin].pin, 'rpin':rel_pins[pin].pin})
                p.tags.append('development')
                p.tags.append('release')
                pins.append(p)
            else:
                p = DotMap({**dev_pins[pin], 'pin':'NA', 'dpin':dev_pins[pin].pin, 'rpin':'NA'})
                p.tags.append('development')
                pins.append(p)

        for pin in rel_pins:
            if pin not in dev_pins:
                p = DotMap({**rel_pins[pin], 'pin':'NA', 'dpin':'NA', 'rpin':rel_pins[pin].pin})
                p.tags.append('release')
                pins.append(p)

        return pins