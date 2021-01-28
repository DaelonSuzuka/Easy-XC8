

def GPIO_read_function_signature(pin_name):
    return "bool " + "read_" + pin_name + "(void)"


def GPIO_write_function_signature(pin_name):
    return "void " + "set_" + pin_name + "(bool value)"


def gpio_direction_function_signature(pin_name):
    return "void " + "set_tris_" + pin_name + "(bool value)"


def expand(args, pin):
    result = {}
    for k, v in args.items():
        if callable(v):
            result[k] = v(pin)
        else:
            result[k] = v
    return result


def if_dev(line, p, string, args={}):
    if 'common' in p.tags:
        line(string.format(name=p.name, pin=p.pin, port=p.pin[0], num=p.pin[1], **expand(args, p.pin)))
    else:
        dev = string.format(name=p.name, pin=p.dpin, port=p.dpin[0], num=p.dpin[1], **expand(args, p.dpin))
        rel = string.format(name=p.name, pin=p.rpin, port=p.rpin[0], num=p.rpin[1], **expand(args, p.rpin))

        if 'development' in p.tags:
            line("#ifdef DEVELOPMENT")
            line(dev)
            if 'release' in p.tags:
                line("#else")
                line(rel)
            line("#endif")

        else:
            line("#ifndef DEVELOPMENT")
            line(rel)
            line("#endif")