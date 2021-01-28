from .loader import load_pins_from_file
from .functions import *
from .chip_info import adc_channel


# *************************************************************************** #


def button_stuff(line, pins):
    pins = [p for p in pins if "button" in p.tags]

    line("// Button stuff")
    if not pins:
        line("// none")
        return
    
    line(f"#define NUMBER_OF_BUTTONS {len(pins)}")
    line("")
    line("// array of pointers to button reading functions")
    line("typedef bool (*button_function_t)(void);")
    line("extern button_function_t buttonFunctions[NUMBER_OF_BUTTONS];")

    line("")
    line("// enum of button names")
    line("enum {")
    for p in pins:
        name = p.name.replace("BUTTON_", "").replace("_PIN", "")
        line(f"{name},")
    line("} button_names;")


def gpio_read_functions(line, pins):
    pins = [p for p in pins if "gpio" in p.tags and "input" in p.tags]

    line("// GPIO read functions")
    if not pins:
        line("// none")

    for p in pins:
        line(f"extern {GPIO_read_function_signature(p.name)};")


def gpio_write_functions(line, pins):
    pins = [p for p in pins if "gpio" in p.tags and "output" in p.tags]
    
    line("// GPIO write functions")
    if not pins:
        line("// none")

    for p in pins:
        line(f"extern {GPIO_write_function_signature(p.name)};")


def gpio_direction_functions(line, pins):
    pins = [p for p in pins if "gpio" in p.tags and "tristate" in p.tags]

    line("// GPIO direction functions")
    if not pins:
        line("// none")

    for p in pins:
        line(f"extern {gpio_direction_function_signature(p.name)};")


def pps_pin_macros(line, pins):
    pins = [p for p in pins if "pps" in p.tags]

    line("// PPS Pin initialization macros")
    if not pins:
        line("// none")

    for p in pins:
        direction = 'INPUT' if "input" in p.tags else 'OUTPUT'
        if_dev(line, p, '#define PPS_{name} PPS_{direction}({port}, {num})', {'direction':direction})


def adc_channel_macros(line, pins):
    pins = [p for p in pins if "analog" in p.tags]

    line("// ADC Channel Select macros")
    if not pins:
        line("// none")

    for p in pins:
        if_dev(line, p, '#define ADC_{name} {channel}', {'channel': lambda p: adc_channel[p]})


# *************************************************************************** #


def pin_declarations():
    pins = load_pins_from_file()

    text = [""]
    line = text.append

    gpio_read_functions(line, pins)
    line("")
    button_stuff(line, pins)
    line("")
    gpio_write_functions(line, pins)
    line("")
    gpio_direction_functions(line, pins)
    line("")
    pps_pin_macros(line, pins)
    line("")
    adc_channel_macros(line, pins)
    line("")

    return "\n".join(text)