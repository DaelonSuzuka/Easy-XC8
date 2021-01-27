from .loader import load_pins_from_file
from .functions import *


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

    line("// Tristate set  functions")
    gpio_output_pins = [p for p in gpio_pins if "tristate" in p.tags]
    if not gpio_output_pins:
        line("// none")
    for p in gpio_output_pins:
        line(tristate_set_function_signature(p.name) + " { ")
        line(f"    TRIS{p.pin[0]}bits.TRIS{p.pin} = value;" )
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

        if p.pin != 'E3': # RE3 doesn't have a tris bit
            if "input" in p.tags:
                line(f"    TRIS{p.pin[0]}bits.TRIS{p.pin} = 1;")
            elif "output" in p.tags:
                line(f"    TRIS{p.pin[0]}bits.TRIS{p.pin} = 0;")

        if "analog" in p.tags:
            line(f"    ANSEL{p.pin[0]}bits.ANSEL{p.pin} = 1;")
        if "button" in p.tags:
            line(f"    WPU{p.pin[0]}bits.WPU{p.pin} = 1;")
        if "pullup" in p.tags:
            line(f"    WPU{p.pin[0]}bits.WPU{p.pin} = 1;")

        line("")
    line("}")

    return "\n".join(text)