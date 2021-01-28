

def GPIO_read_function_signature(pin_name):
    return "bool " + "read_" + pin_name + "(void)"


def GPIO_write_function_signature(pin_name):
    return "void " + "set_" + pin_name + "(bool value)"


def gpio_direction_function_signature(pin_name):
    return "void " + "set_tris_" + pin_name + "(bool value)"


def if_dev2(line, p, string, args={}):
    name=p.name
    if 'common' in p.tags:
        port = p.pin[0]
        pin = p.pin[1]
        both = p.pin
        line(string.format(name=name, port=port, pin=pin, both=both, **args))
    else:
        line("#ifdef DEVELOPMENT")
        if 'development' in p.tags:
            port = p.dpin[0]
            pin = p.dpin[1]
            both = p.dpin
            line(string.format(name=name, port=port, pin=pin, both=both, **args))
        line("#else")
        if 'release' in p.tags:
            port = p.rpin[0]
            pin = p.rpin[1]
            both = p.rpin
            line(string.format(name=name, port=port, pin=pin, both=both, **args))
        line("#endif")


def expand(args, pin):
    result = {}
    for k, v in args.items():
        if callable(v):
            result[k] = v(pin)
        else:
            result[k] = v
    return result


def if_dev(line, p, string, args={}, exargs={}):
    if 'common' in p.tags:
        line(string.format(name=p.name, pin=p.pin, port=p.pin[0], num=p.pin[1], **expand(args, p.pin)))
    else:
        line("#ifdef DEVELOPMENT")
        if 'development' in p.tags:
            line(string.format(name=p.name, pin=p.dpin, port=p.dpin[0], num=p.dpin[1], **expand(args, p.dpin)))
        line("#else")
        if 'release' in p.tags:
            line(string.format(name=p.name, pin=p.rpin, port=p.rpin[0], num=p.rpin[1], **expand(args, p.rpin)))
        line("#endif")