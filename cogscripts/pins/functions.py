

def GPIO_read_function_signature(pin_name):
    return "bool " + "read_" + pin_name + "(void)"


def GPIO_write_function_signature(pin_name):
    return "void " + "set_" + pin_name + "(bool value)"


def tristate_set_function_signature(pin_name):
    return "void " + "set_tris_" + pin_name + "(bool value)"