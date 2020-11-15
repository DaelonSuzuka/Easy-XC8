/* [[[cog
import codegen as code
from pathlib import Path

search_pattern = r'(?<=case hash_).*?(?=:)'

strings = utils.search('src/usb/messages.c', search_pattern)
strings = list(dict.fromkeys(strings)) # strip duplicates

prefix = 'hash_'
keys = [
    "jsmn_undefined", 
    "jsmn_object", 
    "jsmn_array", 
    "jsmn_string", 
    "jsmn_primitive", 
]
keys.extend([f'{prefix}{s}' for s in strings])

enum = code.Enum('hash_value_t', values=keys, typedef=True, explicit=True)
struct = code.Struct('hash', ['const char *name', f'{enum.name} value'])

func_contents = [
    f'const struct {struct.name} *result = in_word_set(string, strlen(string));',
    'if (!result) { return -1; }',
    'return result->value;',
]

func = code.Function(
    name = 'hash_string',
    return_type = enum.name,
    contents = func_contents,
    params = 'const char *string',
    extern = True
)

header = code.HeaderFile(
    name = Path(Path(cog.inFile).parent, 'hash_function.h'),
    includes = '<stdint.h>',
    contents = [enum.assemble(), func.declaration(extern=True)]
)

gperf_strings = [f'{k}, {prefix}{k}' for k in strings]
gperf_code = utils.Gperf(gperf_strings, struct.assemble()).run()

source = code.SourceFile(
    name = Path(Path(cog.inFile).parent, 'hash_function.c'),
    includes = ['<stdint.h>','<string.h>',f'"{header.name}"'],
    contents = [gperf_code, func.definition()]
)

header.write()
source.write()

cog.outl(f'#include "{header.name}"')

]]] */
#include "hash_function.h"
/* [[[end]]] */