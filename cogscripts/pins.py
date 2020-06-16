#!/usr/bin/env python3

import os
import sys
import json
import csv
import re
from dotmap import DotMap

# ------------------------------------------------------------------------------

adc_channel = {
    "F7": "47",
    "F6": "46",
    "F5": "45",
    "F4": "44",
    "F3": "43",
    "F2": "42",
    "F1": "41",
    "F0": "40",

    "E2": "34",
    "E1": "33",
    "E0": "32",

    "D7": "31",
    "D6": "30",
    "D5": "29",
    "D4": "28",
    "D3": "27",
    "D2": "26",
    "D1": "25",
    "D0": "24",

    "C7": "23",
    "C6": "22",
    "C5": "21",
    "C4": "20",
    "C3": "19",
    "C2": "18",
    "C1": "17",
    "C0": "16",

    "B7": "15",
    "B6": "14",
    "B5": "13",
    "B4": "12",
    "B3": "11",
    "B2": "10",
    "B1": "9",
    "B0": "8",

    "A7": "7",
    "A6": "6",
    "A5": "5",
    "A4": "4",
    "A3": "3",
    "A2": "2",
    "A1": "1",
    "A0": "0",
}


def GPIO_read_function_signature(pin_name):
    return "bool " + "read_" + pin_name + "(void)"


def GPIO_write_function_signature(pin_name):
    return "void " + "set_" + pin_name + "(bool value)"


# ------------------------------------------------------------------------------

def pin_declarations():
    pins = load_pins_from_file()

    text = [""]
    line = text.append

    gpio_pins = [p for p in pins if "gpio" in p.tags]

    line("// GPIO read functions")
    gpio_input_pins = [p for p in gpio_pins if "input" in p.tags]
    if not gpio_input_pins:
        line("// none")
    for p in gpio_input_pins:
        line(f"extern {GPIO_read_function_signature(p.name)};")
    line("")

    line("// Button stuff")
    button_pins = [p for p in pins if "button" in p.tags]
    if not button_pins:
        line("// none")
    else:
        line(f"#define NUMBER_OF_BUTTONS {len(button_pins)}")
        line("")
        line("// array of pointers to button reading functions")
        line("typedef bool (*button_function_t)(void);")
        line("extern button_function_t buttonFunctions[NUMBER_OF_BUTTONS];")

        line("")
        line("// enum of button names")
        line("enum {")
        for p in button_pins:
            name = p.name.replace("BUTTON_", "").replace("_PIN", "")
            line(f"{name},")
        line("} button_names;")
    line("")

    line("// GPIO write functions")
    gpio_output_pins = [p for p in gpio_pins if "output" in p.tags]
    if not gpio_output_pins:
        line("// none")
    for p in gpio_output_pins:
        line(f"extern {GPIO_write_function_signature(p.name)};")
    line("")

    line("// PPS initialization macros")
    pps_pins = [p for p in pins if "pps" in p.tags]
    if not pps_pins:
        line("// none")
    for p in pps_pins:
        if "input" in p.tags:
            line(f"#define PPS_{p.name} PPS_INPUT({p.pin[0]}, {p.pin[1]})")
        elif "output" in p.tags:
            line(f"#define PPS_{p.name} PPS_OUTPUT({p.pin[0]}, {p.pin[1]})")
    line("")

    line("// ADC Channel Select macros")
    analog_pins = [p for p in pins if "analog" in p.tags]
    if not analog_pins:
        line("// none")
    for p in analog_pins:
        line(f"#define ADC_{p.name} {adc_channel[p.pin]}")
    line("")

    return "\n".join(text)


# ------------------------------------------------------------------------------


def pin_definitions():
    pins = load_pins_from_file()

    text = [""]
    line = text.append

    gpio_pins = [p for p in pins if "gpio" in p.tags]

    line("// GPIO read functions")
    gpio_input_pins = [p for p in gpio_pins if "input" in p.tags]
    if not gpio_input_pins:
        line("// none")
    for p in gpio_input_pins:
        line(GPIO_read_function_signature(p.name) + " { ")
        line(f"    return PORT{p.pin[0]}bits.R{p.pin};")
        line("}")
    line("")

    line("// Button stuff")
    button_pins = [p for p in pins if "button" in p.tags]
    if not button_pins:
        line("// none")
    else:
        line("// array of pointers to button reading functions")
        line("button_function_t buttonFunctions[NUMBER_OF_BUTTONS] = {")
        for p in button_pins:
            line(f"read_{p.name}, //")
        line("};")
    line("")

    line("// GPIO write functions")
    gpio_output_pins = [p for p in gpio_pins if "output" in p.tags]
    if not gpio_output_pins:
        line("// none")
    for p in gpio_output_pins:
        line(GPIO_write_function_signature(p.name) + " { ")
        line(f"    LAT{p.pin[0]}bits.LAT{p.pin} = value;" )
        line("}")
    line("")

    return "\n".join(text)


def pins_init():
    pins = load_pins_from_file()

    text = [""]
    line = text.append

    line("void pins_init(void) {")
    for p in pins:
        line(f"    // {p.name}")

        if "input" in p.tags:
            line(f"    TRIS{p.pin[0]}bits.TRIS{p.pin} = 1;")
        elif "output" in p.tags:
            line(f"    TRIS{p.pin[0]}bits.TRIS{p.pin} = 0;")

        if "analog" in p.tags:
            line(f"    ANSEL{p.pin[0]}bits.ANSEL{p.pin} = 1;")
        if "button" in p.tags:
            line(f"    WPU{p.pin[0]}bits.WPU{p.pin} = 1;")

        line("")
    line("}")

    return "\n".join(text)


# ------------------------------------------------------------------------------


def skip_comments(lines):
    for line in lines:
        line = re.sub(r'\s*#.*$', '', line).strip()
        if line:
            yield line


def load_pins_from_file():
    with open('pins.csv', 'r') as f:
        csv.register_dialect('pincsv', skipinitialspace=True)
        reader = csv.DictReader(skip_comments(f), dialect='pincsv')

        pins = [DotMap(r) for r in reader if r['name']]
        for p in pins:
            p.tags = p.tags.split(" ")
        return pins