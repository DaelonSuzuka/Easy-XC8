from .loader import load_pins_from_file
from .functions import *
from .chip_info import adc_channel


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

    line("// Tristate set functions")
    gpio_output_pins = [p for p in gpio_pins if "tristate" in p.tags]
    if not gpio_output_pins:
        line("// none")
    for p in gpio_output_pins:
        line(f"extern {tristate_set_function_signature(p.name)};")
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