from .loader import load_pins_from_file
from .functions import *


# *************************************************************************** #


def button_stuff(line, pins):
    pins = [p for p in pins if "button" in p.tags]

    line("// Button stuff")
    if not pins:
        line("// none")
        return
    
    line("// array of pointers to button reading functions")
    line("button_function_t buttonFunctions[NUMBER_OF_BUTTONS] = {")
    for p in pins:
        line(f"read_{p.name}, //")
    line("};")


def gpio_read_functions(line, pins):
    pins = [p for p in pins if "gpio" in p.tags and "input" in p.tags]

    line("// GPIO read functions")
    if not pins:
        line("// none")

    for p in pins:
        line(GPIO_read_function_signature(p.name) + " { ")
        if_dev(line, p, 'return PORT{port}bits.R{pin};')
        line("}")


def gpio_write_functions(line, pins):
    pins = [p for p in pins if "gpio" in p.tags and "output" in p.tags]
    
    line("// GPIO write functions")
    if not pins:
        line("// none")
    
    for p in pins:
        line(GPIO_write_function_signature(p.name) + " { ")
        if_dev(line, p, 'LAT{port}bits.LAT{pin} = value;')
        line("}")


def gpio_direction_functions(line, pins):
    pins = [p for p in pins if "tristate" in p.tags]

    line("// GPIO direction functions")
    if not pins:
        line("// none")

    for p in pins:
        line(gpio_direction_function_signature(p.name) + " { ")
        if_dev(line, p, 'TRIS{port}bits.TRIS{pin} = value;')
        line("}")


# *************************************************************************** #


def pin_definitions():
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

    return "\n".join(text)


def pins_init():
    pins = load_pins_from_file()

    text = [""]
    line = text.append

    line("void pins_init(void) {")
    for p in pins:
        line(f"// {p.name}")

        if p.pin != 'E3': # RE3 doesn't have a tris bit
            if "input" in p.tags:
                if_dev(line, p, 'TRIS{port}bits.TRIS{pin} = 1;')
            elif "output" in p.tags:
                if_dev(line, p, 'TRIS{port}bits.TRIS{pin} = 0;')

        if "analog" in p.tags:
            if_dev(line, p, 'ANSEL{port}bits.ANSEL{pin} = 1;')
        if "button" in p.tags:
            if_dev(line, p, 'WPU{port}bits.WPU{pin} = 1;')
        if "pullup" in p.tags:
            if_dev(line, p, 'WPU{port}bits.WPU{pin} = 1;')

        line("")
    line("}")

    return "\n".join(text)