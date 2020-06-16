from subprocess import Popen, PIPE


def fmt(text):
    if isinstance(text, str):
        pass
    else:
        text = '\n'.join(text)

    p = Popen('clang-format', stdout=PIPE, stdin=PIPE)
    stdout, errs = p.communicate(input=text.encode())
    return stdout.decode()


def hrule(char='*', length=80):
    string = '/* '
    for i in range(length - 6):
        string += char
    string += ' */'
    return string
